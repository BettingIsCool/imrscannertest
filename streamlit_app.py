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

  
  # Fetch processed bets for each user
  processed_eventids = db_imr.get_processed_bets(username=username)
  data = db_imr.get_log(sports=selected_sports, leagues=selected_leagues, min_diff=float(min_diff) / 100, min_limit=min_limit)

  for event in data:
    event.update({'processed': False})
    if event['event_id'] in processed_eventids:
      event.update({'processed': True})

  
  if data:

    
    # Convert dictionary to pandas dataframe
    dataframe = pd.DataFrame(data)

    
    # Replace negative stakes with zeros and use integers
    dataframe['stake_home'][dataframe['stake_home'] < 0] = 0
    dataframe['stake_away'][dataframe['stake_away'] < 0] = 0
    dataframe['stake_home'] = dataframe['stake_home'].astype(int)
    dataframe['stake_away'] = dataframe['stake_away'].astype(int)

    
    # Rename and reorder columns
    dataframe = dataframe.rename(columns={'processed': 'PROCESSED', 'event_id': 'EVENTID', 'starts': 'STARTS', 'sport_name': 'SPORT', 'league_name': 'LEAGUE', 'runner_home': 'HOME TEAM', 'runner_away': 'AWAY TEAM', 'line': 'HOME LINE', 'spread_home': 'ODDS HOME', 'spread_away': 'ODDS AWAY', 'spread_home_max': 'LIMIT', 'diff_home': 'DIFF HOME', 'diff_away': 'DIFF AWAY', 'stake_home': 'STAKE HOME', 'stake_away': 'STAKE AWAY', 'timestamp': 'ODDS UPDATED', 'ratings_updated': 'RATINGS UPDATED'})
    dataframe = dataframe[['PROCESSED', 'STARTS', 'SPORT', 'LEAGUE', 'HOME TEAM', 'AWAY TEAM', 'HOME LINE', 'ODDS HOME', 'ODDS AWAY', 'LIMIT', 'DIFF HOME', 'DIFF AWAY', 'STAKE HOME', 'STAKE AWAY', 'ODDS UPDATED', 'RATINGS UPDATED', 'EVENTID']]

    
    # Apply font & background colors to cells, apply number formatting
    styled_df = dataframe.style.applymap(tools.highlight_cell, subset=['DIFF HOME', 'DIFF AWAY']).applymap(tools.highlight_outdated_odds, subset=['ODDS UPDATED']).applymap(tools.highlight_outdated_ratings, subset=['RATINGS UPDATED']).format({'HOME LINE': '{:+g}'.format, 'ODDS HOME': '{:,.3f}'.format, 'ODDS AWAY': '{:,.3f}'.format, 'LIMIT': '{0:g}'.format, 'DIFF HOME': '{:+.0%}'.format, 'DIFF AWAY': '{:+.0%}'.format, 'STAKE HOME': '{}'.format, 'STAKE AWAY': '{}'.format})

    
    # Convert dataframe to data_editor object to make specific columns editable for users
    edited_dataframe = st.data_editor(styled_df, column_config={"PROCESSED": st.column_config.CheckboxColumn("PROCESSED", help="Select if you have processed this game!", default=False)}, disabled=['EVENTID', 'STARTS', 'SPORT', 'LEAGUE', 'HOME TEAM', 'AWAY TEAM', 'HOME LINE', 'ODDS HOME', 'ODDS AWAY', 'LIMIT', 'DIFF HOME', 'DIFF AWAY', 'STAKE HOME', 'STAKE AWAY', 'ODDS UPDATED', 'RATINGS UPDATED'], hide_index=True)
    st.cache_data.clear()
    
    processed_eventids_new = edited_dataframe.loc[(edited_dataframe['PROCESSED'] == True), 'EVENTID'].tolist()
  
    # Delete event_id in db if event is not in selected events
    processed_eventids_old = db_imr.get_processed_bets(username=username)
    for event_id in processed_eventids_old:
      if event_id not in processed_eventids_new:
        db_imr.delete_processed_bet(username=username, event_id=event_id)

    # Append event_id if missing in db
    processed_eventids_old = db_imr.get_processed_bets(username=username)
    for event_id in processed_eventids_new:
      if event_id not in processed_eventids_old:
        db_imr.append_processed_bet(username=username, event_id=event_id)
   
    tools.print_advise()
  
