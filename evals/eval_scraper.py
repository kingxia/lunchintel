import requests, re

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
#name_marker = '<p><strong>'
name_regex = '<p><strong>.*<\/strong><\/p>'

def get_html(url):
    lines = requests.get(url)
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
    lines = get_html(eval_site)
    segments = segment_html(lines)

#if __name__ == '__main__':
#    main()
