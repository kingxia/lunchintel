## HLS food scraper
## See what's on the menu today

import datetime, json, re, requests, sys
from HTMLParser import HTMLParser

debug = False

food_terms = ["lunch", "dinner", "snack", "food", "served", "provided",
              "burger", "pizza", "shake", "drinks", "ice cream", "reception",
              "cocktail"]
no_food_terms = ["not be served", "no lunch", "no dinner", "not be provided"]

day_url = "http://hls.harvard.edu/calendar/%s"
event_marker = 'class="url"'
description_marker = 'type="application/ld+json"'

time_format = "%Y-%m-%dT%H:%M:%S+00:00"
time_format_2 = "%Y-%m-%dT%H:%M:%S+0000"
json_parse_error = "Error parsing json from %s"

class Event:
    def __init__(self, name, start, end, location, description, url, error=None):
        self.name = name
        self.start = start
        self.end = end
        self.location = location
        self.food = self.get_food_sentences(description)
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

# Date should be a datetime object.
def get_events(date, day_cache={}):
    debug('get_events(%s)' % date)
    if date in day_cache:
        return day_cache[date]
    url_lines = get_filtered_lines(day_url % str(date), event_marker)
    urls = [extract_url(line) for line in url_lines]
    day_cache[date] = urls
    return urls

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
        details = json.loads(event_data.split("[")[1].split("]")[0])
        name = details['name'].decode('utf-8', 'ignore')
        start = datetime.datetime.strptime(details['startDate'], time_format)
        start -= datetime.timedelta(hours=4)
        end = datetime.datetime.strptime(details['endDate'], time_format)
        end -= datetime.timedelta(hours=4)
        location = details['location']['name'].decode('utf-8', 'ignore')
        description = ''
        for i in range(index+2, index_2):
            description += strip_tags(page_data[i].strip())
        encoded = description.decode('utf-8', 'ignore')
        error = None
        #description = [3:len(details-4)]
        event = Event(name, start, end, location, encoded, url)
    except ValueError:
        event = Event(None, None, None, None, None, url, json_parse_error % url)
    event_cache[url] = event
    return event

def get_food_listings(date, day_cache={}, event_cache={}):
    debug('get_food_listings(%s)' % date)
    date_events = day_cache[date] if date in day_cache else get_events(date)
    if date not in day_cache:
        day_cache[date] = date_events
    events = []
    for event in date_events:
        events.append(event_cache[event] if event in event_cache else get_event(event))
        event_cache[event] = events[-1]
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

if __name__ == "__main__":
    main()
