## HLS food scraper
## See what's on the menu today

import datetime, json, re, requests, sys
from HTMLParser import HTMLParser

debug = False

food_terms = ["lunch", "dinner", "snack", "food", "served", "provided",
              "burger", "pizza", "shake", "drinks", "ice cream", "reception",
              "cocktail"]
no_food_terms = ["not be served", "no lunch", "no dinner", "not be provided", "walk-in"]

day_url = "http://hls.harvard.edu/calendar/%s"
event_api = "http://hls.harvard.edu/wp-json/tribe/events/v1/events?start_date=%s"
event_marker = 'class="url"'
description_marker = 'type="application/ld+json"'
script_start = '<script type="application/ld+json">'
script_end = '</script>'

time_format = "%Y-%m-%dT%H:%M:%S+00:00"
time_format_2 = "%Y-%m-%dT%H:%M:%S+0000"
json_parse_error = "Error parsing json from %s"
time_display = "%I:%M %p"
date_display = "%A, %b. %d"

class Event:
    def __init__(self, name, start, end, location, description, group, url, error=None):
        self.name = name
        self.start = start
        self.end = end
        self.location = location
        self.food = self.get_food_sentences(description)
        self.group = group
        self.url = url
        self.error = error

    def has_food(self):
        return not self.error and self.food

    def get_food_sentences(self, text):
        if not text:
            return None
        food = ''
        sentences = re.split('[!.?]', text)
        for sentence in sentences:
            score = 0
            for word in food_terms:
                score += sentence.count(word)
            for phrase in no_food_terms:
                if sentence.find(phrase) != -1:
                    score = 0
                    break
            if score > 0:
                food += " %s." % sentence.strip()
        return food if len(food) > 0 else None

    def is_lunch(self):
        if not self.end:
            return False
        return self.end.time() <= datetime.time(15)

    def is_dinner(self):
        if not self.start:
            return False
        return self.start.time() >= datetime.time(15)

    def short_str(self):
        if self.error:
            return self.error
        return "%s: (%s, %s - %s)." % \
               (self.name, self.location, str(self.start.time()), str(self.end.time()))

    def time(self):
        return "%s - %s" % (self.start.strftime(time_display),
                            self.end.strftime(time_display))

    def __str__(self):
        if self.error:
            return self.error
        return "%s: (%s, %s - %s).\n\t%s" % \
               (self.name, self.location, str(self.start.time()), str(self.end.time()), self.food)

def extract_url(line):
    href = line.split(" ")[2]
    return href.split("\"")[1]

def get_filtered_lines(url, marker):
    lines = requests.get(url)
    return [line for line in lines.iter_lines() if marker in line]

def get_rest_api_json(url):
    site = requests.get(url)
    if not site.ok:
        debug('Site is not okay: %s' % site)
        return {}
    return json.loads(site.text)

# Date should be a datetime object.
def get_events(date, day_cache={}):
    debug('get_events(%s)' % date)
    if date in day_cache:
        return day_cache[date]
    url_lines = get_filtered_lines(day_url % str(date), event_marker)
    urls = [extract_url(line) for line in url_lines]
    day_cache[date] = urls
    return urls

def get_datetime(json):
    if json is None:
        return None
    return datetime.datetime(int(json['year']), int(json['month']), int(json['day']),
                             int(json['hour']), int(json['minutes']), int(json['seconds']))

def get_venue(json):
    if json is None:
        return None
    return json['venue']

def get_organizer(json):
    if json is None or len(json) == 0:
        return None
    return json[0].get('organizer')

# Date should be datetime.date not datetime.datetime
def get_rest_api_events(date, event_cache={}):
    debug('get_rest_api_events(%s)' % date)
    if date in event_cache:
        return event_cache[date]
    event_json = get_rest_api_json(event_api % str(date))
    events = []

    if event_json.get('events') is not None:
        for event in event_json['events']:
            debug('\ngetting event')
            if event is None:
                continue
            try:
                debug('getting name')
                name = try_decode(event.get('title'))
                debug('getting url')
                url = event.get('url')
                debug('getting description')
                description = try_decode(event.get('description'))
                debug('getting start')
                start = get_datetime(event.get('start_date_details'))
                debug('getting end')
                end = get_datetime(event.get('end_date_details'))
                debug('getting venue')
                location = try_decode(get_venue(event.get('venue')))
                debug('getting organizer')
                group = get_organizer(event.get('organizer'))
                debug('checking dates')

                if start.date() != date:
                    debug('passing by')
                    continue
                
                debug('append event')
                events.append(Event(name, start, end, location, description, group, url))
            except:
                debug('got an error parsing: %s' % str(event))
                url = event.get('url') if event.get('url') is not None else ''
                events.append(Event(event.get('title'), None, None, None,
                                    None, None, url, json_parse_error % url))

    event_cache[date] = events
    return events

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, data):
        self.fed.append(data)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()

def try_get(json, key):
    """Safe json getter when json could be None."""
    return json.get(key) if json else json

def try_decode(string):
    """Safe string decoding when string could be None."""
    return string.encode('ascii', 'ignore').decode('utf-8', 'ignore') \
           if string else string

def try_format(time, fmt):
    """Safe time formatting when time could be None."""
    return datetime.datetime.strptime(time, fmt) if time else time

def try_offset(time, offset=4, dst=True):
    """Safe time offsetting when time could be None.
    Default to 5-hour offset; the difference between GMT and EST, plus DST."""
    return time - datetime.timedelta(hours=(offset + (1 if dst else 0))) \
           if time else time

def get_event(url, event_cache={}):
    debug('get_event(%s)' % url)
    if url in event_cache:
        return event_cache[url]
    url_lines = requests.get(url)
    page_data = [line for line in url_lines.iter_lines()]
    event_data = [line for line in page_data if description_marker in line][0]
    index = [i for i, s in enumerate(page_data) if "Event content" in s][0]
    index_2 = [i for i, s in enumerate(page_data) if ".tribe-events-single-event-description" in s][0]

    try:
        json_str = event_data.split(script_start)[1].split(script_end)[0]
        details = json.loads(json_str[1:len(json_str)-1])
        name = try_decode(details.get('name'))
        start = try_offset(try_format(details.get('startDate'), time_format))
        end = try_offset(try_format(details.get('endDate'), time_format))
        location = try_decode(try_get(details.get('location'), 'name'))
        group = ''
        description = ''
        for i in range(index+2, index_2):
            description += strip_tags(page_data[i].strip())
        encoded = description.decode('utf-8', 'ignore')
        error = None
        #description = [3:len(details-4)]
        event = Event(name, start, end, location, encoded, group, url)
    except ValueError:
        event = Event(None, None, None, None, None, None, url, json_parse_error % url)
    event_cache[url] = event
    return event

def get_food_listings(date, day_cache={}, event_cache={}, e_cache={}):
    debug('get_food_listings(%s)' % date)

    events = e_cache[date] if date in e_cache else get_rest_api_events(date, event_cache=e_cache)
        
    
##    date_events = day_cache[date] if date in day_cache else get_events(date)
##    if date not in day_cache:
##        day_cache[date] = date_events
##    events = []
##    for event in date_events:
##        events.append(event_cache[event] if event in event_cache else get_event(event))
##        event_cache[event] = events[-1]
    output = {'food':[], 'nofood':[]}
    for event in events:
        output['food' if event.has_food() else 'nofood'].append(event)
    return output

def debug(message):
    if not debug or __name__ == "__main__":
        return
    print message

def main():
    date_offset = 0 if len(sys.argv) < 2 else int(sys.argv[1])
    today = datetime.datetime.today()
    offset = today + datetime.timedelta(days = date_offset)
    events = [get_event(event) for event in get_events(offset.date())]
    print "Events for %s" % offset.date()
    for event in events:
        if not event.has_food():
            continue
        print "%s\n" % event
