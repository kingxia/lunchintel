from flask import Flask, Response
import cgi, datetime, food_scraper, logging, os, sys

day_cache = {}
event_cache = {}

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/')
def get_lunches():
    def generate():
        global day_cache, event_cache
        today = datetime.datetime.today()
        #print request.args
        #date_offset = cgi.escape(request.args['date'] if 'date' in request.args else '')
        today = today + datetime.timedelta(days = 0)
        date_events = food_scraper.get_events(today.date(), day_cache)
        food = {'food':[], 'nofood':[]}
        #food = food_scraper.get_food_listings(today.date(), day_cache, event_cache)
        page = ''
        page += '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        page += "<html>\n<title>There is such a thing</title>\n"
        page += '<head><link rel="shortcut icon" type="image/x-icon" href="favicon.ico" /></head>\n'
        yield page

        for event in date_events:
            yield '<!-- working... -->'
            new_event = food_scraper.get_event(event, event_cache)
            food['food' if new_event.has_food() else 'nofood'].append(new_event)

        page = ''
        page += "<body>\n<h2>Events for %s</h2>\n" % today.date()
        page += "<hr>\n<h3>With food:</h3>\n"
        page += "<ul>\n"
        for event in food['food']:
            page += "<li>%s" % event.short_str()
            page += '<ul><li>%s. <a href="%s">Link.</a></li></ul>' % (event.food, event.url)
            page += "</li>"
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
    return Response(generate(), mimetype='text/html')
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico', mimetype='image/png')
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
