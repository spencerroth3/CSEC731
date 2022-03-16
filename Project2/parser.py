"""
CSEC 731: Project B
Author: Spencer Roth
Date: 2/4/2022

parser.py   This program functions as a parser for the HTTP protocol
"""

import sys

SUPPORTED_METHODS = {"GET", "POST", "PUT", "DELETE", "CONNECT", "HEAD"}
SUPPORTED_VERSIONS = {"HTTP/1.0", "HTTP/1.1", "HTTP/2.0"}

class RequestHTTP:
    def __init__(self, method, path, version):
        self.method = method
        self.path = path
        self.version = version
        self.headers = {}
        self.body = ""

def parse_request(req):
    """
    """
    request_line = req[0].split(" ")
    req = req[1:]
    r = RequestHTTP(request_line[0], request_line[1], request_line[2].strip("\n")) #.split("/")[1])

    req_iter = req #create an iterator so we can perform destructive action on req
    for line in req_iter:
        req = req[1:]
        line = line.strip("\n")
        if line != "":
            h = line.split(": ")
            r.headers[h[0]] = h[1]
        else:
            break
        
    for line in req:
        #print(line)
        r.body += line
    return r



def get_request(path):
    """
    Takes a file path as an argument and returns a python list of the lines of data within the file 
    """
    with open(path) as f:
        return f.readlines()

def main():
    if len(sys.argv) < 2:
        print("usage: parser.py <path to HTTP request>")
        exit(1)
    
    try:
        try:
            request_path = sys.argv[1]
            req = get_request(request_path)
            r = parse_request(req)

            if r.method not in SUPPORTED_METHODS or r.version not in SUPPORTED_VERSIONS:
                raise Exception
            else:
                print("200 OK")
        except:
            print("400 BAD REQUEST")

    except:
        print("500 INTERNAL SERVER ERROR")


main()
