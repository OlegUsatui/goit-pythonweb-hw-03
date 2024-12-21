from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
import os

STORAGE_DIR = 'storage'
DATA_FILE = os.path.join(STORAGE_DIR, 'data.json')

os.makedirs(STORAGE_DIR, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/':
                self.path = '/index.html'
            elif self.path == '/message':
                self.path = '/message.html'
            elif self.path == '/read':
                self._handle_read()
                return

            file_path = '.' + self.path

            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            else:
                content_type = 'text/html'

            with open(file_path, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-Type', f'{content_type}; charset=utf-8')
                self.end_headers()
                self.wfile.write(file.read())

        except FileNotFoundError:
            self._handle_404()

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_data = dict(x.split('=') for x in post_data.split('&'))

            username = post_data.get('username')
            message = post_data.get('message')

            if username and message:
                with open(DATA_FILE, 'r+') as f:
                    data = json.load(f)
                    timestamp = datetime.now().isoformat()
                    data[timestamp] = {"username": username, "message": message}
                    f.seek(0)
                    json.dump(data, f, indent=4)

            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

    def _handle_read(self):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)

            messages_html = ''.join(
                f"<div><strong>{msg['username']}</strong> ({timestamp}):<br>{msg['message']}</div><hr>"
                for timestamp, msg in data.items()
            )

            response_content = f"""
            <html>
                <head><title>Messages</title></head>
                <body>
                    <h1>Messages</h1>
                    {messages_html}
                    <a href="/">Back to Home</a>
                </body>
            </html>
            """

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response_content.encode('utf-8'))

        except FileNotFoundError:
            self._handle_404()

    def _handle_404(self):
        try:
            with open('error.html', 'rb') as file:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'<h1>Sorry, page not found...</h1>')


def start_web_server():
    server_address = ('localhost', 3000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Serving on port 3000...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print('Shutdown server')

if __name__ == '__main__':
    start_web_server()
