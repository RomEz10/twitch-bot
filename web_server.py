from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from requests import post
import creds
import os.path


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html')
        if self.path == '/':
            filename = root + '\\index.html'
        else:
            filename = root + self.path

        self.send_response(200)
        if self.path[1:2] == '?':
            url = self.path
            url_vars = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            print(url_vars)
            try:
                code = url_vars.get('code')[0]
                print(code)
                token = self.get_token(code)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(('token: ' + token[0] + ' is valid for ' + str(token[2]) + ' seconds should use: ' +
                                  token[1] + ' to refresh the token').encode('utf-8'))
            except:
                self.send_response(404)
        else:
            if filename[-4:] == '.css':
                self.send_header('Content-type', 'text/css')
            elif filename[-5:] == '.json':
                self.send_header('Content-type', 'application/javascript')
            elif filename[-3:] == '.js':
                self.send_header('Content-type', 'application/javascript')
            elif filename[-4:] == '.ico':
                self.send_header('Content-type', 'image/x-icon')
            else:
                self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(filename, 'rb') as fh:
                html = fh.read()
                self.wfile.write(html)

    @staticmethod
    def get_token(code):
        response = post('https://id.twitch.tv/oauth2/token?client_id=' + creds.client_id +
                                 '&client_secret=' + creds.client_secret +
                                 '&code=' + code +
                                 '&grant_type=authorization_code&redirect_uri=http://localhost:8000')
        print(response.json())
        token = response.json().get('access_token', 'non')
        refresh_token = response.json().get('refresh_token', 'non')
        timeout = response.json().get('expires_in', 0)
        return token, refresh_token, timeout


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()