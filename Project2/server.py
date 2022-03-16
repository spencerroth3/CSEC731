"""
CSEC 731: Project B
Author: Spencer Roth
Date: 2/4/2022

server.py   This program expands upon the parser.py to create a server which parses and hadles HTTP requests
"""

import argparse
import subprocess
import os 
import socket
import ssl
import shutil

SUPPORTED_METHODS = {"GET", "POST", "PUT", "DELETE", "CONNECT", "HEAD"}
SUPPORTED_VERSIONS = {"HTTP/1.0", "HTTP/1.1", "HTTP/2.0"}
LOG_FILE = 'server.log'

STATUS_CODES = {
    200: 'OK',
    201: 'Created',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    411: 'Length Required',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    505: 'HTTP Version Not Supported'
}

# Request object
class RequestHTTP:
    def __init__(self, method, path, version):
        self.method = method
        self.path = path
        self.params = ""
        self.version = version
        self.headers = {}
        self.body = ""

def parse_request(req):
    """
    This function is used to parse an HTTP request into 3 parts: request line, list of headers, and body

    @param req: raw HTTP request string
    @return r: parsed HTTP request as a python object
    """
    req = req.split("\r\n")
    request_line = req[0].split(" ")
    req = req[1:]
    r = RequestHTTP(request_line[0], request_line[1], request_line[2].strip("\r\n")) #.split("/")[1])
    if "?" in r.path:
        tmp = r.path.split("?")
        r.path = tmp[0]
        r.params = tmp[1]

    req_iter = req #create an iterator so we can perform destructive action on req
    for line in req_iter:
        req = req[1:]
        line = line.strip("\r\n")
        if line != "":
            h = line.split(": ")
            r.headers[h[0]] = h[1]
        else:
            break
        
    for line in req:
        #print(line)
        r.body += line
    return r

def handle_php(r):
    """
    Takes in a request object that requests a .php resource and passes data to CGI script. Returns output of PHP script in the response body.
    @param r: request object
    @return php-cgi script output
    """
    env_vars = os.environ.copy()
    env_vars['REQUEST_METHOD'] = r.method
    env_vars['REDIRECT_STATUS'] = '0'
    env_vars['GATEWAY_INTERFACE'] = 'CGI/1.1'
    
    full_path = os.path.abspath(r.path[1:])
    env_vars['SCRIPT_NAME'] = r.path[1:] 
    env_vars['SCRIPT_FILENAME'] = full_path

    if not os.path.exists(full_path):
        raise FileNotFoundError

    if r.method == 'GET':
        env_vars['QUERY_STRING'] = r.params
    elif r.method == 'POST':
        env_vars['CONTENT_TYPE'] = r.headers['Content-Type']
        env_vars['CONTENT_LENGTH'] = r.headers['Content-Length']

    php_cgi = shutil.which('php-cgi')

    if not php_cgi:
        raise Exception
    proc = subprocess.Popen(php_cgi, env=env_vars, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if r.method == 'POST':
        stdout, stderr = proc.communicate(input=r.body.encode('utf-8'), timeout=None)
    else:
        stdout, stderr = proc.communicate(None)
    
    return stdout.decode('utf-8')
    


def handle_get(r):
    """
    Handler for a GET request
    @param r: request object
    @return http_response: response string to send back to the client
    """
    try:
        resource = open(r.path[1:], "r")
        data = resource.read()
        resource.close()

        # If php resource is requested, pass data to CGI script
        if '.php' in r.path:
            data = handle_php(r)

        http_response =  "HTTP/1.1 " + '200 ' + STATUS_CODES[200] + "\r\n" 

        # Write to log file
        log = open(LOG_FILE, "a+")
        log.write(http_response)
        log.close()

        http_response += "Content-Type: text/html\r\n"
        http_response += "Content-Length: " + str(len(data)) + "\r\n"
        http_response += "Connection: Closed\r\n\r\n"
        http_response += data

        return http_response

    except PermissionError:
        return "HTTP/1.1 " + '403 ' + STATUS_CODES[403] + "\r\n" + "Connection: Closed\r\n\r\n"
    except FileNotFoundError:
        return "HTTP/1.1 " + '404 ' + STATUS_CODES[404] + "\r\n" + "Connection: Closed\r\n\r\n"
    except:
        return "HTTP/1.1 " + '500 ' + STATUS_CODES[500] + "\r\n" + "Connection: Closed\r\n\r\n"


def handle_post(r):
    """
    Handler for a POST request
    @param r: request object
    @return http_response: response string to send back to the client
    """
    try:
        #Check for proper Content-Length Header
        if int(r.headers['Content-Length']) != len(r.body):
            raise Exception

        if '.php' in r.path:
            data = handle_php(r)
        http_response =  "HTTP/1.1 " + '200 ' + STATUS_CODES[200] + "\r\n" 

        # Write to log file
        log = open(LOG_FILE, "a+")
        log.write(http_response)
        log.close()
        
        http_response += "Connection: Closed\r\n\r\n"
        http_response += data
        return http_response

    except PermissionError:
        return "HTTP/1.1 " + '403 ' + STATUS_CODES[403] + "\r\n" + "Connection: Closed\r\n\r\n"
    except FileNotFoundError:
        return "HTTP/1.1 " + '404 ' + STATUS_CODES[404] + "\r\n" + "Connection: Closed\r\n\r\n"
    except:
        return "HTTP/1.1 " + '500 ' + STATUS_CODES[500] + "\r\n" + "Connection: Closed\r\n\r\n"

def handle_put(r):
    """
    Handler for a PUT request
    @param r: request object
    @return http_response: response string to send back to the client
    """
    try:
        #Check for proper Content-Length Header
        if int(r.headers['Content-Length']) != len(r.body):
            raise Exception

        resource = open(r.path[1:], "w+")
        resource.write(r.body)
        resource.close()

        http_response =  "HTTP/1.1 " + '201 ' + STATUS_CODES[201] + "\r\n" 

        # Write to log file
        log = open(LOG_FILE, "a+")
        log.write(http_response)
        log.close()

        http_response += "Location: " + r.path +"\r\n"
        http_response += "Connection: Closed\r\n\r\n"
        http_response += r.body

        return http_response

    except PermissionError:
        return "HTTP/1.1 " + '403 ' + STATUS_CODES[403] + "\r\n" + "Connection: Closed\r\n\r\n"
    except FileNotFoundError:
        return "HTTP/1.1 " + '404 ' + STATUS_CODES[404] + "\r\n" + "Connection: Closed\r\n\r\n"
    except:
        return "HTTP/1.1 " + '500 ' + STATUS_CODES[500] + "\r\n" + "Connection: Closed\r\n\r\n"

def handle_delete(r):
    """
    Handler for a DELETE request
    @param r: request object
    @return http_response: response string to send back to the client
    """
    try:
        os.remove(r.path[1:])
        http_response =  "HTTP/1.1 " + '200 ' + STATUS_CODES[200] + "\r\n" 

        # Write to log file
        log = open(LOG_FILE, "a+")
        log.write(http_response)
        log.close()

        http_response += "Connection: Closed\r\n\r\n"

        return http_response

    except PermissionError:
        return "HTTP/1.1 " + '403 ' + STATUS_CODES[403] + "\r\n" + "Connection: Closed\r\n\r\n"
    except FileNotFoundError:
        return "HTTP/1.1 " + '404 ' + STATUS_CODES[404] + "\r\n" + "Connection: Closed\r\n\r\n"
    except:
        return "HTTP/1.1 " + '500 ' + STATUS_CODES[500] + "\r\n" + "Connection: Closed\r\n\r\n"

def handle(req, client_conn):
    """
    Handles Client request
    @param req: Raw HTTP request string
    @param client_conn: Client socket stream
    """
    http_response = ""

    try:
        r = parse_request(req)
    except:
        http_response = "HTTP/1.1 " + '400 ' + STATUS_CODES[400] + "\r\n" + "Connection: Closed\r\n\r\n"
    
    if http_response == "":
        if r.method not in SUPPORTED_METHODS:
            http_response = "HTTP/1.1 " + '501 ' + STATUS_CODES[501] + "\r\n" + "Connection: Closed\r\n\r\n"
        elif r.version not in SUPPORTED_VERSIONS:
            http_response = "HTTP/1.1 " + '505 ' + STATUS_CODES[505] + "\r\n" + "Connection: Closed\r\n\r\n"
        elif r.method == "POST" and 'Content-Length' not in r.headers:
            http_response = "HTTP/1.1 " + '411 ' + STATUS_CODES[411] + "\r\n" + "Connection: Closed\r\n\r\n"
        
        try:
            if r.method == "GET":
                http_response = handle_get(r)
            elif r.method == "POST":
                http_response = handle_post(r)
            elif r.method == "PUT":
                http_response = handle_put(r)
            elif r.method == "DELETE":
                http_response = handle_delete(r)
        except: 
            http_response = "HTTP/1.1 " + '500 ' + STATUS_CODES[500] + "\r\n" + "Connection: Closed\r\n\r\n" 

    client_conn.sendall(http_response.encode('utf-8')) 
    client_conn.close()


def main():
    parser = argparse.ArgumentParser(description='Process args')
    parser.add_argument('--ip', required=True,  help='IP address for the server to listen on')
    parser.add_argument('--port', required=True, help='Port for the server to listen on')
    parser.add_argument('--cert', required=False, help='Path to the HTTPS Certificate File')
    parser.add_argument('--key', required=False, help='Path to the HTTPS Private Key')

    args = parser.parse_args()

    if args.cert and not args.key:
        print('[!] Missing Key File!')
        exit(1)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((args.ip, int(args.port)))

    if args.cert and args.key:
        l_socket = ssl.wrap_socket(server_socket, server_side=True, cert_reqs=ssl.CERT_NONE, certfile=args.cert, keyfile=args.key, ssl_version=ssl.PROTOCOL_TLSv1_2)
    else:
        l_socket = server_socket
    
    l_socket.listen(1)
    
    print('[*] Listening for connections...')
   
    while True:
        try:
            client_conn, client_addr = l_socket.accept()
            print("[+] Connection received from ", client_addr)
            request_data = client_conn.recv(1024)
            req = request_data.decode('utf-8')
            handle(req, client_conn)
        except KeyboardInterrupt:
            print('[*] Shutting down server...')
            exit(1)
        except:
            pass
main()
