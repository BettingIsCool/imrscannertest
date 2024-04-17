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
