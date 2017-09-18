from flask import Flask
import datetime, food_scraper, os

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
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)