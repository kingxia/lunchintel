import requests, re
from requests.auth import HTTPBasicAuth

def process_doc(url):
    pass

def process_html(url):
    pass

def process_pdf(url):
    pass

content_handlers = {
    'doc' : process_doc,
    'html' : process_html,
    'pdf' : process_pdf
}
eval_site = 'https://www.law.harvard.edu/students/dean/resources/secure/current.html'
name_regex = '<p><strong>.*<\/strong><\/p>'
class_regex = '.*<br \/>'

# LOL I'm not putting these anywhere near github.
credentials = '../../credentials.txt'

class Marker():
    def __init__(self, regex, offset=0):
        self.regex = regex
        self.offset = offset

eval_markers = [Marker(name_regex), Marker(class_regex, 1)]

class Professor():
    def __init__(self, name, courses):
        self.name = name
        self.courses = courses

class Course():
    def __init__(self, name, evals):
        self.name = name
        self.evals = evals

# Placeholder
class Evaluation():
    def __init__(self, score):
        self.score = score

def get_credentials(location):
    f = open(credentials, 'r')
    lines = [line.strip() for line in f.readlines()]
    f.close()
    return HTTPBasicAuth(lines[0], lines[1])

def get_html(url, auth):
    lines = requests.get(url, auth=auth)
    return [line for line in lines.iter_lines()]

def segment_html(lines):
    segments = []
    current_segment = []
    for i in range(len(lines)):
        if re.match(name_regex, lines[i]):
            segments.append(current_segment)
            current_segment = []
        current_segment.append(lines[i])
    segments.append(current_segment)
    return segments

def get_content_type(url):
    return requests.get(url).headers['Content-Type']
    #return url.split('.')[-1]

class Segment():
    def __init__(self, identifier):
        self.identifier = identifier
        self.segments = None

    def __str__(self):
        return '%s, with %d subsegments' % (self.identifier, 0 if not self.segments else len(self.segments))

def recursive_segment(text, markers):
    if not text or len(text) == 0:
        return None
    if not markers or len(markers) == 0:
        return [Segment(line) for line in text]
    
    start_index = None
    segments = []
    for i in range(len(text)):
        if i <= start_index:
            continue
        if re.match(markers[0].regex, text[i]):
            if start_index:
                segments.append(Segment(text[start_index]))
                segments[-1].segments = recursive_segment(text[start_index+1:i+markers[0].offset], markers[1:])
            start_index = i+markers[0].offset
    if not start_index:
        start_index = 0
    
    segments.append(Segment(text[start_index]))
    segments[-1].segments = recursive_segment(text[start_index+1:i+markers[0].offset], markers[1:])
    return segments

def main():
    auth = get_credentials(credentials)
    lines = get_html(eval_site, auth)
    segments = recursive_segment(lines, eval_markers)
    return segments
    #profs = []
    #for line in segments:
    #    profs.append(Professor(line[0], line[1:]))
    #return profs

if __name__ == '__main__':
    main()
