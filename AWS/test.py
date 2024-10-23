#!/usr/bin/env python3
import sys
import json
import time
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <name>")
        sys.exit(1)
    
    # Get the name argument from sys.argv
    json_in = sys.argv[1]

    test = json.loads(json_in)
    time.sleep(10)
    print(type(test))
    print(test['message'])
    

if __name__ == "__main__":
    main()
