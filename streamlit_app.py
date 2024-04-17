import time
import tools
import db_imr
import pandas as pd
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth

from config import TEXT_LANDING_PAGE

# Switch to wide-mode for better view
st.set_page_config(layout="wide")


# Fetch all active users from database
users = db_imr.get_users()


# Create credential lists for authentication
names = [item['name'] for item in users]
usernames = [item['username'] for item in users]
passwords = [item['password'] for item in users]


# Create hashed passwords for secure login
hashed_passwords = stauth.Hasher(passwords).generate()
authenticator = stauth.Authenticate(names, usernames, hashed_passwords, 'app_home', 'auth', cookie_expiry_days=1)
name, authentication_status, username = authenticator.login("Login", "sidebar")


# Place welcome text on landing page
placeholder1 = st.empty()
placeholder2 = st.empty()
placeholder1.title('Implied Market Ratings')
placeholder2.markdown(TEXT_LANDING_PAGE)


# Display text if authentication fails
if authentication_status is False:
  st.error("Username/password incorrect or subscription expired.")


# Continue if authentication suceeds
if authentication_status:

  placeholder1.empty()
  placeholder2.empty()

  
  # Monkey patch for failed logout
  try:
    authenticator.logout("Logout", "sidebar") 
  except KeyError:
    pass  # ignore it
  except Exception as err:
    st.error(f'Unexpected exception {err}')
    raise Exception(err)  # but not this, let's crash the app

  
  # Display name & widgets in side bar
  st.sidebar.title(f"Welcome {name}")
  
  min_diff = st.sidebar.slider(label='Min Diff Percentage', min_value=5, max_value=100, value=8, step=1)
  min_limit = st.sidebar.slider(label='Min Limit', min_value=0, max_value=10000, value=0, step=100)
  
  unique_sports = db_imr.get_sports()
  selected_sports = st.sidebar.multiselect(label='Sports', options=sorted(unique_sports), default=unique_sports)
  selected_sports = [f"'{s}'" for s in selected_sports]
  selected_sports = f"({','.join(selected_sports)})"
  
  unique_leagues = db_imr.get_leagues()
  selected_leagues = st.sidebar.multiselect(label='Leagues', options=sorted(unique_leagues), default=unique_leagues)
  selected_leagues = [f"'{s}'" for s in selected_leagues]
  selected_leagues = f"({','.join(selected_leagues)})"

  
  # Place a refresh button on top of the table to clear the cache
  if st.button('Refresh data', type="primary"):
    st.cache_data.clear()

  processed_bets = db_imr.get_processed_bets(username=username)
  data = db_imr.get_log(sports=selected_sports, leagues=selected_leagues, min_diff=float(min_diff) / 100, min_limit=min_limit)

  for d in data:
    d.update({'processed': True}) if d['event_id'] in processed_bets else d.update({'processed': False})

  st.write(processed_bets)
  st.write(data)

  if data:
    
    dataframe = pd.DataFrame(data)

    dataframe['stake_home'] = dataframe['stake_home']
    dataframe['stake_away'] = dataframe['stake_away']
    dataframe['stake_home'][dataframe['stake_home'] < 0] = 0
    dataframe['stake_away'][dataframe['stake_away'] < 0] = 0
    dataframe['stake_home'] = dataframe['stake_home'].astype(int)
    dataframe['stake_away'] = dataframe['stake_away'].astype(int)
    
    dataframe = dataframe.rename(columns={'event_id': 'EVENTID', 'starts': 'STARTS', 'sport_name': 'SPORT', 'league_name': 'LEAGUE', 'runner_home': 'HOME TEAM', 'runner_away': 'AWAY TEAM', 'line': 'HOME LINE', 'spread_home': 'ODDS HOME', 'spread_away': 'ODDS AWAY', 'spread_home_max': 'LIMIT', 'diff_home': 'DIFF HOME', 'diff_away': 'DIFF AWAY', 'stake_home': 'STAKE HOME', 'stake_away': 'STAKE AWAY', 'timestamp': 'ODDS UPDATED', 'ratings_updated': 'RATINGS UPDATED'})

    dataframe.insert(0, "PROCESSED", [False] * len(dataframe.index), True)
    styled_df = dataframe.style.applymap(tools.highlight_cell, subset=['DIFF HOME', 'DIFF AWAY']).applymap(tools.highlight_outdated_odds, subset=['ODDS UPDATED']).applymap(tools.highlight_outdated_ratings, subset=['RATINGS UPDATED']).format({'HOME LINE': '{:+g}'.format, 'ODDS HOME': '{:,.3f}'.format, 'ODDS AWAY': '{:,.3f}'.format, 'LIMIT': '{0:g}'.format, 'DIFF HOME': '{:+.0%}'.format, 'DIFF AWAY': '{:+.0%}'.format, 'STAKE HOME': '{}'.format, 'STAKE AWAY': '{}'.format})

    edited_dataframe = st.data_editor(styled_df, column_config={"PROCESSED": st.column_config.CheckboxColumn("PROCESSED", help="Select if you have processed this game!", default=False,)}, disabled=['EVENTID', 'STARTS', 'SPORT', 'LEAGUE', 'HOME TEAM', 'AWAY TEAM', 'HOME LINE', 'ODDS HOME', 'ODDS AWAY', 'LIMIT', 'DIFF HOME', 'DIFF AWAY', 'STAKE HOME', 'STAKE AWAY', 'ODDS UPDATED', 'RATINGS UPDATED'], hide_index=True)
    st.write(edited_dataframe.loc[(edited_dataframe['PROCESSED'] == True), 'EVENTID'])
   
    st.markdown("""👉 Sort rows by clicking on the column header.""")
    st.markdown("""👉 Enter 'wide-mode' in the settings (top right) for a more convenient view.""")
    st.markdown("""👉 I strongly advise to shop for better prices whenever possible. This could easily be the difference between winning and losing!""")
    st.markdown("""👉 Have realistic expectations. We are up against the sharpest books of the world and I'm not claiming any ridiculous profits. Your long-term ROI will be +3% at best!""")
    st.markdown("""👉 Betting is a marathon, not a sprint. So take a long-term view and evaluate your bets after a year. Judging your bets too early and you will be fooled by randomness.""")
    st.markdown("""👉 DIFF HOME/AWAY is the difference in implied probabilities between the current odds and my model's odds (it is NOT the expected ROI). Recommended setting: Min Diff Percentage = 8%""")
    st.markdown("""👉 Performance will vary on when you place the bets. Generally the earlier the better as opening/early prices are softest. However this will mean you need to deal with smaller limits and prices not widely available. It's up to you to strike the balance between volume and ROI.""")
    
  
