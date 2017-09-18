from flask import Flask
import datetime, food_scraper

day_cache = {}
event_cache = {}

app = Flask(__name__)

@app.route('/')
def get_lunches():
	global day_cache, event_cache
	today = datetime.datetime.today()
	today = today + datetime.timedelta(days = 0)
	food = food_scaper.get_food_listings(today.date, day_cache, event_cache)
	return "hi"
    
if __name__ == "__main__":
    app.run()