from flask import Flask, Response, request
import cgi, datetime, food_scraper, logging, os, sys

day_cache = {}
event_cache = {}

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

@app.route('/', methods=["GET","POST"])
def get_lunches():
    def generate(date_offset=0):
        global day_cache, event_cache
        today = datetime.datetime.today()
        today = today + datetime.timedelta(days = date_offset)
        date_events = food_scraper.get_events(today.date(), day_cache)
        food = {'dinner':[], 'lunch':[], 'nofood':[]}

        page = ''
        page += '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
        page += "<html>\n<title>There is such a thing</title>\n"
        page += '<head>'
        page += '''<!-- Global Site Tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-75643216-2"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments)};
  gtag('js', new Date());

  gtag('config', 'UA-75643216-2');
</script>'''
        page += '<link rel="shortcut icon" type="image/x-icon" href="favicon.ico" />'
        page += '<meta id="meta" name="viewport" content="width=device-width; initial-scale=1.0" />'
        page += '</head>\n'
        page += '<body style="margin-left: 12px; margin-top: 12px">\n'
        
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
    day_offset = request.args.get("date")
    if day_offset:
        try:
            day_offset = int(day_offset.encode('utf8'))
        except ValueError:
            print 'Got a bad day offset: %s' % day_offset
            day_offset = 0
    else:
        day_offset = 0
    return Response(generate(day_offset), mimetype='text/html')
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico', mimetype='image/png')
    
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
