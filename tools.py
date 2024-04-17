import streamlit as st
from datetime import datetime

# Highlight value bet
def highlight_cell(val):

 # Forest Trees https://www.color-hex.com/color-palette/
 if val >= 0.25:
  color = '#3e6c60'
 elif val >= 0.15:
  color = '#569358'
 elif val >= 0.08:
  color = '#77c063'
 elif val >= 0.05:
  color = '#ffe406'
  
 else:
  color = ''
 return f'background-color: {color}'


# Highlight outdated odds
def highlight_outdated_odds(val):

 if (datetime.now() - val).total_seconds() > 180:
  color = 'red' 
 else:
  color = 'green'
 return f'color: {color}'


# Highlight outdated ratings
def highlight_outdated_ratings(val):

 if (datetime.now() - val).total_seconds() > 86400:
  color = 'red' 
 else:
  color = 'green'
 return f'color: {color}'

def print_advise():
 
 st.markdown("""👉 Sort rows by clicking on the column header.""")
 st.markdown("""👉 Enter 'wide-mode' in the settings (top right) for a more convenient view.""")
 st.markdown("""👉 I strongly advise to shop for better prices whenever possible. This could easily be the difference between winning and losing!""")
 st.markdown("""👉 Have realistic expectations. We are up against the sharpest books of the world and I'm not claiming any ridiculous profits. Your long-term ROI will be +3% at best!""")
 st.markdown("""👉 Betting is a marathon, not a sprint. So take a long-term view and evaluate your bets after a year. Judging your bets too early and you will be fooled by randomness.""")
 st.markdown("""👉 DIFF HOME/AWAY is the difference in implied probabilities between the current odds and my model's odds (it is NOT the expected ROI). Recommended setting: Min Diff Percentage = 8%""")
 st.markdown("""👉 Performance will vary on when you place the bets. Generally the earlier the better as opening/early prices are softest. However this will mean you need to deal with smaller limits and prices not widely available. It's up to you to strike the balance between volume and ROI.""")
 
