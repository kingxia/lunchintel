# HLS
A collection of scripts I use to make law school a bit easier.

new_case.py - creates templated case briefs.  
food_scraper.py - scrape HLS event calendar for free food.  
food_server.py - serve food_scraper.py to localhost.  
flask_food_server.py - serve food_scraper.py to localhost with Flask.

Local servers can be exposed by something like ngrok, or just hosted on your own webserver.

Prefer to develop on qa-prod and then merge many changes into master. This is both safer development practices, allows for a qa environment to land changes into, and means that master will not dump its cache as often if auto-synced to.
