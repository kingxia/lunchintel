import codecs, PyPDF2, sys

def get_pdf(filename):
    return open(filename, 'rb')

def get_reader(pdf):
    return PyPDF2.PdfFileReader(pdf)

def find_text(reader, string):
    for page in range(reader.numPages):
        pageObject = reader.getPage(page)
        text = pageObject.extractText()
        plaintext = text.encode('ascii', 'ignore').strip(codecs.BOM_UTF8).replace('\n', '')
        if string in plaintext:
            return plaintext
    return None

def find_first_text(reader, strings, reverse=True):
    pages = {}
    for page in range(reader.numPages - 1 if reverse else 0, \
                      -1 if reverse else reader.numPages, \
                      -1 if reverse else 1):
        pageObject = reader.getPage(page)
        text = pageObject.extractText()
        plaintext = text.encode('ascii', 'ignore').strip(codecs.BOM_UTF8).replace('\n', '')
        found = filter(lambda x: x not in pages and x in plaintext, strings)
        for string in found:
            pages[string] = page
        if len(pages) == len(strings):
            break
    return pages

def find_all_text(reader, strings):
    pages = {}
    for string in strings:
        pages[string] = []
    for page in range(reader.numPages):
            pageObject = reader.getPage(page)
            text = pageObject.extractText()
            plaintext = text.encode('ascii', 'ignore').strip(codecs.BOM_UTF8).replace('\n', '')
            #if any(s in plaintext for s in strings):
            found = filter(lambda x: x in plaintext, strings)
            for string in found:
                pages[string].append(page) #plaintext
    return pages

def get_strings():
    strings = []
    last_input = 'default'
    while last_input != '':
        strings.append(last_input)
        last_input = raw_input('Search term: ')
    return strings[1:]

def main():
    path = "../../1L/Fall Term/Criminal Law/%s"
    filename = "Criminal Law Packet 1.pdf"
    starting_page = 1
    pdf = get_pdf(path % filename)
    reader = get_reader(pdf)
    strings = get_strings() if len(sys.argv) < 2 else sys.argv[1:]
    pages = find_first_text(reader, sys.argv[1:])
    pdf.close()

    for page in pages:
        print '%s: %s' % (page, pages[page])

if __name__ == '__main__':
    main()
