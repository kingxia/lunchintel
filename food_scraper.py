## HLS food scraper
## See what's on the menu today

import datetime, json, re, sys, urllib

food_terms = ["lunch", "dinner", "snack", "food", "served", "provided",
              "burger", "pizza", "shake"]
no_food_terms = ["not be served", "no lunch", "no dinner", "not be provided"]

day_url = "http://hls.harvard.edu/calendar/%s"
event_marker = 'class="url"'
description_marker = 'type="application/ld+json"'

time_format = "%Y-%m-%dT%H:%M:%S+00:00"
json_parse_error = "Error parsing json from %s"

class Event:
    def __init__(self, name, start, end, description, error=None):
        self.name = name
        self.start = start
        self.end = end
        self.food = self.get_food_sentences(description)
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

    def __str__(self):
        if self.error:
            return self.error
        return "%s: (%s - %s).\n\t%s" % \
               (self.name, str(self.start.time()), str(self.end.time()), self.food)

def extract_url(line):
    href = line.split(" ")[2]
    return href.split("\"")[1]

def get_filtered_lines(url, marker):
    lines = urllib.urlopen(url)
    return [line for line in lines if marker in line]

# Date should be a datetime object.
def get_events(date):
    debug('get_events(%s)' % date)
    url_lines = get_filtered_lines(day_url % str(date), event_marker)
    urls = [extract_url(line) for line in url_lines]
    return urls

def get_event(url):
    debug('get_event(%s)' % url)
    event_data = get_filtered_lines(url, description_marker)[0]
    try:
        details = json.loads(event_data.split("[")[1].split("]")[0])
        start = datetime.datetime.strptime(details['startDate'], time_format)
        end = datetime.datetime.strptime(details['endDate'], time_format)
        event = Event(details['name'].encode('utf8'), start, end, details['description'].encode('utf8'))
    except ValueError:
        event = Event(None, None, None, None, json_parse_error % url)
    return event

def get_food_listings(date, day_cache, event_cache):
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
    if __name__ == "__main__":
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
