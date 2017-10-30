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
# LOL I'm not putting these anywhere near github.
credentials = '../../credentials.txt'

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
    return url.split('.')[-1]

def main():
    auth = get_credentials(credentials)
    lines = get_html(eval_site, auth)
    segments = segment_html(lines)
    print len(segments)

if __name__ == '__main__':
    main()
