from flask import Flask, Response, request, render_template, send_from_directory, url_for
import cgi, datetime, food_scraper, json, logging, os, requests, sys

event_cache = {}

app = Flask(__name__)
app.config.from_object(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/', methods=["GET","POST"])
def get_lunches():
    def try_generate(date_offset=0, should_log=True):
        try:
            for item in generate_lunch_cards(date_offset, should_log):
                yield item
        except:
            with app.app_context():
                yield render_template('error.html', log=should_log)

    def generate_lunch_cards(date_offset=0, should_log=True):
        global event_cache, app
        today = datetime.datetime.today()
        today = today + datetime.timedelta(days = date_offset)
        yield '<!-- getting all events... -->\n'
        date_events = food_scraper.get_rest_api_events(today.date(), event_cache)
        food = {'dinner':[], 'lunch':[], 'nofood':[]}
        yield '<!-- getting individual events... -->\n'
        for event in date_events:
            #yield '<!-- getting event... -->\n'
            marker = 'nofood' if not event.has_food() else \
                     'lunch' if event.is_lunch() else 'dinner'
            food[marker].append(event)
        with app.app_context():
            yield render_template('main.html',
                                  date=today.date().strftime(food_scraper.date_display),
                                  cards=food, log=should_log)
            
    date_offset = request.args.get("date")
    no_log = request.args.get("ghost")
    
    if date_offset:
        try:
            date_offset = int(date_offset.encode('utf8'))
        except ValueError:
            print 'Got a bad day offset: %s' % date_offset
            date_offset = 0
    else:
        date_offset = 0

    return Response(try_generate(date_offset, not no_log), mimetype='text/html')
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico', mimetype='image/png')
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
