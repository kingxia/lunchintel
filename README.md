# lunchintel
lunchin.tel is a site for finding lunch talks at HLS, emphasis on lunch. Check it out!

new_case.py - creates templated case briefs.  
food_scraper.py - scrape HLS event calendar for food events.  
flask_food_server.py - serve food_scraper.py to localhost with Flask.

Prefer to develop on qa-prod and then merge many changes into master. This is both safer development practice, allows for a qa environment to land changes into, and means that master will not dump its cache as often if auto-synced to.