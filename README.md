# LMSQuery
    
**Fork of Query library for Logitech Media Server**
original created by roberteninhaus
https://github.com/roberteinhaus/lmsquery

This library provides easy to use functions to send queries to a Logitech Media Server (https://github.com/Logitech/slimserver)

### Installation
    pip install lmsquery-fork

### Usage Example
    import lmsquery
    lms = lmsquery.LMSQuery('127.0.0.1', '9000') # use ip and port of lms server
    players = lms.get_players()
    for player in players:
      print player['name']
