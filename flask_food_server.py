from flask import Flask, Response, request, render_template, send_from_directory, url_for
import cgi, datetime, food_scraper, logging, os, sys
import jinja2

day_cache = {}
event_cache = {}

app = Flask(__name__)
app.config.from_object(__name__)
#app.config['SERVER_NAME'] = 'lunchintel-qa.herokuapp.com'
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

def error_page():
    page = ''
    page += '<h2>Something broke :(</h2>\n'
    page += 'Please ping me if this continues for more than a few minutes.\n'
    page += '</body>\n</html>'
    return page

class Card():
    def __init__(self, title, text, link):
        self.title = title
        self.text = text
        self.link = link

@app.route('/', methods=["GET","POST"])
def get_lunches():
    global day_cache, event_cache
    def try_generate(date_offset=0, should_log=True):
        try:
            for item in generate_lunch_cards(date_offset, should_log):
                yield item
        except:
            with app.app_context():
                yield render_template('error.html', log=should_log)

    def generate_lunch_cards(date_offset=0, should_log=True):
        global day_cache, event_cache, app
        cards = []
        today = datetime.datetime.today()
        today = today + datetime.timedelta(days = date_offset)
        yield '<!-- getting all events... -->\n'
        date_events = food_scraper.get_events(today.date(), day_cache)
        food = {'dinner':[], 'lunch':[], 'nofood':[]}
        yield '<!-- getting individual events... -->\n'
        for event in date_events:
            yield '<!-- getting event... -->\n'
            new_event = food_scraper.get_event(event, event_cache)
            marker = 'nofood' if not new_event.has_food() else \
                     'lunch' if new_event.is_lunch() else 'dinner'
            food[marker].append(new_event)
        for item in food['lunch']:
            cards.append(Card(item.name, item.food, item.url))
        with app.app_context():
            yield render_template('main.html', date=today.date(), cards=cards, log=should_log)
            
    def generate(date_offset=0, no_log=False):
        global day_cache, event_cache
        today = datetime.datetime.today()
        today = today + datetime.timedelta(days = date_offset)
        date_events = food_scraper.get_events(today.date(), day_cache)
        food = {'dinner':[], 'lunch':[], 'nofood':[]}

        ## Common header ##
        page = ''
        page += '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        page += "<html>\n<title>There is such a thing</title>\n"
        page += '<head>'
        ## Add MaterialLite
        page += '<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">'
        page += '<link rel="stylesheet" href="material.min.css">'
        page += '<script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script>'
        
        ## Add GA
        if not no_log:
            page += '''<!-- Global Site Tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-75643216-2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments)};
  gtag('js', new Date());

  gtag('config', 'UA-75643216-2');
</script>'''
        
        page += '</head>\n'
        page += '<body style="margin-left: 12px; margin-top: 12px">\n'
        ## Common header ##
        
        yield page

        for event in date_events:
            yield '<!-- working... -->'
            new_event = food_scraper.get_event(event, event_cache)
            marker = 'nofood' if not new_event.has_food() else \
                     'lunch' if new_event.is_lunch() else 'dinner'
            food[marker].append(new_event)

        page = ''
        page += "<h2>Events for %s</h2>\n" % today.date()
        page += "<hr>\n<h3>Lunch:</h3>\n"
        page += "<ul>\n"
        for event in food['lunch']:
            page += '<li>%s <a href="%s">Link.</a>' % (event.short_str(), event.url)
            page += '<ul><li>%s</li></ul>' % event.food
            page += "</li>\n"
        page += "</ul>\n<hr>\n<h3>Dinner:</h3>\n"
        page += "<ul>\n"
        for event in food['dinner']:
            page += '<li>%s <a href="%s">Link.</a>' % (event.short_str(), event.url)
            page += '<ul><li>%s</li></ul>' % event.food
            page += "</li>\n"
        page += "</ul>\n<hr>\n<h3>Other events:</h3>\n"
        page += "<ul>\n"
        for event in food['nofood']:
            page += "<li>%s</li>" % event.short_str()
        page += "</ul>\n<hr>\n"
        page += '<form action=".">'
        page += '<input type="submit" value="Today" />'
        page += '<input type="hidden" name="date" value="0">'
        page += '</form>'
        page += '<form action=".">'
        page += '<input type="submit" value="Tomorrow" />'
        page += '<input type="hidden" name="date" value="1">'
        page += '</form>'
        page += '<form action=".">'
        page += '<input type="submit" value="2 days from now" />'
        page += '<input type="hidden" name="date" value="2">'
        page += '</form>\n'
        page += "</body>\n</html>\n"
        yield page
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

##    cards = []
##
##    today = datetime.datetime.today()
##    today = today + datetime.timedelta(days = date_offset)
##    date_events = food_scraper.get_events(today.date(), day_cache)
##    food = {'dinner':[], 'lunch':[], 'nofood':[]}
##    for event in date_events:
##        new_event = food_scraper.get_event(event, event_cache)
##        marker = 'nofood' if not new_event.has_food() else \
##                 'lunch' if new_event.is_lunch() else 'dinner'
##        food[marker].append(new_event)
##    for item in food['lunch']:
##        cards.append(Card(item.name, item.food, item.url))
    return Response(try_generate(date_offset, not no_log), mimetype='text/html')
    #return render_template('main.html', date="10-27-2017", cards=cards, no_log=not no_log)
    #return Response(stream_template('main.html', date="10-27-2017", cards=cards, log=not no_log))
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico', mimetype='image/png')
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
