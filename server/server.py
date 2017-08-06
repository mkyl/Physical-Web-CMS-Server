import sync

import os
import http
import socketserver
import _thread
import time

MODULE_FOLDER = os.path.dirname(__file__)
MODULE_PARENT = os.path.dirname(MODULE_FOLDER)
CONTENT_FOLDER = os.path.join(MODULE_PARENT, "data") 
PORT = 8080
CHECK_INTERVAL = 300 # seconds

def start_server():
    os.chdir(CONTENT_FOLDER)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print(" [🛈] serving at port", PORT)

    try:
        httpd.serve_forever(); 
    except KeyboardInterrupt:
        pass
    httpd.server_close()

def check_on_content():
    while True:
        time.sleep(CHECK_INTERVAL)
        sync.initialSync(CONTENT_FOLDER)

def main():
    sync.initialSync(CONTENT_FOLDER)
    _thread.start_new_thread(check_on_content, ())
    start_server()

if __name__ == "__main__":
    main()
