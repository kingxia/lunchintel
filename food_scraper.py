## HLS food scraper
## See what's on the menu today

import datetime, json, sys, urllib

food_terms = ["lunch", "dinner", "snack", "food", "served"]
non_food_terms = ["no"]

day_url = "http://hls.harvard.edu/calendar/%s"
event_marker = 'class="url"'
description_marker = 'type="application/ld+json"'

class Event:
    def __init__(self, name, start, end, food):
        self.name = name
        self.start = start
        self.end = end
        self.food = food

    def __str__(self):
        return "%s: (%s - %s), %s" % \
               (self.name, str(self.start), str(self.end), self.food)

def extract_url(line):
    href = line.split(" ")[2]
    return href.split("\"")[1]

def get_filtered_lines(url, marker):
    lines = urllib.urlopen(url)
    return [line for line in lines if marker in line]

# Date should be a datetime object.
def get_events(date):
    url_lines = get_filtered_lines(day_url % str(date), event_marker)
    urls = [extract_url(line) for line in url_lines]
    return urls

def get_event(url):
    event = get_filtered_lines(url, description_marker)[0]
    details = json.loads(event.split("[")[1].split("]")[0])
    return details

def main():
    for line in get_events(datetime.datetime.today().date()):
        print get_event(line)['description'].encode('utf8')

if __name__ == "__main__":
    main()
