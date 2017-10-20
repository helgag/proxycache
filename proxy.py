import os
import logging
import re
import BaseHTTPServer
import hashlib
import requests
import getpass
from bs4 import BeautifulSoup
import werkzeug


BASE_DOMAIN = 'https://our.kacasey.sb.facebook.com'
PROXY_DOMAIN = 'http://localhost:8000'
CACHE = True
session = requests.Session()
session.cookies = requests.cookies.cookielib.LWPCookieJar('cookies.txt')
if not os.path.exists('cookies.txt'):
    session.cookies.save()
session.cookies.load()

COPY_HEADERS = [
    "vary",
    "content-type",
]

def transform_resp(data):
    data = data.replace(BASE_DOMAIN, '')
    data = data.replace(BASE_DOMAIN.replace('/', '\\/'), '')
    data = re.sub(r'(https?:\\/\\/[0-9a-z-.]+\.[a-z]{2,3})', r'http://localhost:8000/__dom/\1', data)
    data = re.sub(r'(https?://[0-9a-z-.]+\.[a-z]{2,3})', r'http://localhost:8000/__dom/\1', data)
    return data

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def _do_GET(self):
        domain = re.findall(r'^/__dom/(https?://[0-9a-z-.]+\.[a-z]{2,3})', self.path)
        if domain:
            domain = domain[0]
            path = self.path[7:]
        else:
            domain = BASE_DOMAIN
            path = '{}{}'.format(BASE_DOMAIN, self.path)

        hashfile = os.path.join('cache', hashlib.sha1(path).hexdigest() + '.cache')
        hashfile_header = os.path.join('header_cache', hashlib.sha1(path).hexdigest() + '.cache')
        HEADER_KEY_VALUE_SEPARATOR = '::::::'
        if CACHE and os.path.exists(hashfile) and os.path.exists(hashfile_header):
            with open(hashfile) as f:
                data = f.read()
            self.send_response(200)
            with open(hashfile_header) as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    k, v = line.split(HEADER_KEY_VALUE_SEPARATOR)
                    self.send_header(k, v)
            self.end_headers()
        elif CACHE:
            return
        else:
            if CACHE:
                import pdb; pdb.set_trace()
            r = session.get("{}".format(path))

            data = transform_resp(r.content)
            with open(hashfile, 'w') as f:
                f.write(data)
            self.send_response(r.status_code)

            with open(hashfile_header, 'w') as f:
                for k, v in r.headers.items():
                    if k.lower() in COPY_HEADERS:
                        f.write(k + HEADER_KEY_VALUE_SEPARATOR + v + '\n')
                        self.send_header(k, v)

            self.end_headers()

        self.wfile.writelines(data)

    def do_GET(self):
        try:
            self._do_GET()
            session.cookies.save()
        except Exception as e:
            print("GET failed: %s\n%s" % (self.path, e))
            logging.debug("GET failed: %s\n%s" % (self.path, e))

    def _do_POST(self):
        # TODO: cache this at all?
        domain = re.findall(r'__dom/(https?://[0-9a-z-.]+\.[a-z]{2,3})', self.path)
        if domain:
            domain = domain[0]
            path = self.path[7:]
        else:
            domain = BASE_DOMAIN
            path = '{}{}'.format(BASE_DOMAIN, self.path)

        length = int(self.headers.getheader('content-length'))
        field_data = self.rfile.read(length)
        fields = werkzeug.url_decode(field_data)

        CRITICAL_KEYS = ['q']
        data_for_path = ''
        for crit in CRITICAL_KEYS:
            if crit in fields:
                data_for_path += fields[crit]

        path_with_data = path + data_for_path
        hashfile = os.path.join('post_cache', hashlib.sha1(path_with_data).hexdigest() + '.cache')

        if CACHE and os.path.exists(hashfile):
            with open(hashfile) as f:
                data = f.read()
            self.send_response(200)
        elif CACHE:
            return
        else:
            r = session.post("{}".format(path), data=dict(**fields))

            data = transform_resp(r.content)

            with open(hashfile, 'w') as f:
                f.write(data)

            self.send_response(r.status_code)
        self.end_headers()
        self.wfile.writelines(data)

    def do_POST(self):
        try:
            self._do_POST()
            session.cookies.save()
        except Exception as e:
            print("POST failed: %s\n%s" % (self.path, e))
            logging.debug("POST failed: %s\n%s" % (self.path, e))

def run():
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    server_address = ('', 8000)
    httpd = BaseHTTPServer.HTTPServer(server_address, Handler)
    httpd.serve_forever()


if __name__ == '__main__':
    run()
