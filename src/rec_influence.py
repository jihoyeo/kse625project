import sys, getopt
import re

def main(argv):
    user_id = ''
    location = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["user_id=","location="])
        
    except getopt.GetoptError:
        print 'rec_influence.py -u <user_id> -l <location>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'rec_influence.py -i <inputfile> -l <location>'
            sys.exit()
        elif opt in ("-u", "--user_id"):
            user_id = arg
        elif opt in ("-l", "--location"):
            location = arg
            
    print 'user_id: "', user_id
    print 'location: (%.3f,%.3f)', re.findall(r'\d+.\d+')

if __name__ == '__main__':
    main(sys.argv[1:])