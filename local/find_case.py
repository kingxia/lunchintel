import os, sys

year = "1L"
term = "Fall Term"
classmap = {
    "civpro":"Civil Procedure",
    "crim":"Criminal Law",
    "lrw":"Legal Reading and Writing",
    "legreg":"Legislation and Regulation",
    "torts":"Torts"
}

def main():
    search = raw_input("Case: ") if len(sys.argv) < 2 \
             else sys.argv[1]
    search = search.lower()
    classname = get_class_name() if len(sys.argv) < 3 \
                else classmap[sys.argv[2].lower()]

    target = "../../%s/%s/%s/Briefs" % (year, term, classname)
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), target)
    files = [f for f in os.listdir(target_path) if search in f.lower() and os.path.isfile(os.path.join(target_path, f))]
    if len(files) == 0:
        print "File not found."

    index = 0
    if len(files) > 1:
        print "Select file:"
        for i in range(len(files)):
            print "\t[%d] %s" % (i, files[i])
        index = int(raw_input("File: "))
    
    os.startfile(os.path.join(target_path, files[index]))

if __name__ == "__main__":
    main()
