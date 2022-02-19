"""
CSEC 731: Project B
Author: Spencer Roth
Date: 2/4/2022

parser.py   This program functions as a parser for the HTTP protocol
"""

import sys
from urllib import request

class RequestHTTP:
    def __init__(self, method, path, version):
        self.method = method
        self.path = path
        self.version = version
        self.headers = {}
        self.data = None

def parse_request(req):
    """
    """
    request_line = req[0].split(" ")
    req = req[1:]
    r = RequestHTTP(request_line[0], request_line[1], request_line[2]) #.split("/")[1])

    req_iter = req #create an iterator so we can perform destructive action on req
    for line in req_iter:
        if line != "":
            h = line.split(": ")
            r.headers[h[0]] = h[1]
        else:
            r.data += line + "\n"

        req = req[1:]

    return r



def get_request(path):
    """
    Takes a file path as an argument and returns a python list of the lines of data within the file 
    """
    with open(path) as f:
        return f.readlines()

def main():
    request_path = sys.argv[1]
    req = get_request(request_path)
    r = parse_request(req)

    print(r.headers)
    print("-------")
    print(r.data)




main()