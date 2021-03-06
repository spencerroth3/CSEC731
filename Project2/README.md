This repository contains a basic web server written from scratch in python. The main web server file is `server.py`. The usage is as follows:

```
usage: server.py [-h] --ip IP --port PORT [--cert CERT] [--key KEY]
server.py: error: the following arguments are required: --ip, --port

Process args

optional arguments:
  -h, --help   show this help message and exit
  --ip IP      IP address for the server to listen on
  --port PORT  Port for the server to listen on
  --cert CERT  Path to the HTTPS Certificate File
  --key KEY    Path to the HTTPS Private Key
```
Note: if a self-signed cert is used for the server, certificate verification will need to be turned off by the client. For example, if using `curl` you will need to add the `-k` flag. 

All valid requests will be logged in `server.log`

When a resource ending in `.php` is requested, the request data will be passed to php-cgi and the output will be returned in the request. PHP-cgi needs to be installed on the host which the server is running on. On Ubuntu, it can be installed as follows: `apt install php-cgi`
