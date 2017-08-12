import sync
import presentation

import os
import http
import socketserver
import _thread
import time

MODULE_FOLDER = os.path.abspath(os.path.dirname(__file__))
MODULE_PARENT = os.path.dirname(MODULE_FOLDER)
CONTENT_FOLDER = os.path.join(MODULE_PARENT, "data") 
PUBLIC_FOLDER = os.path.join(MODULE_PARENT, "export")

PORT = 8080
CHECK_INTERVAL = 120 # seconds

def start_server():
    os.chdir(PUBLIC_FOLDER)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print(" [🛈] serving at port", PORT)

    try:
        httpd.serve_forever();
    except KeyboardInterrupt:
        pass
    httpd.server_close()

def check_on_content():
    try:
        while True:
            for i in range(CHECK_INTERVAL):
                time.sleep(1) # 1 second
            prepare_content()
    except KeyboardInterrupt:
        pass

def prepare_content():
    sync.initialSync(CONTENT_FOLDER)
    presentation.build_website(CONTENT_FOLDER, PUBLIC_FOLDER)

def main():
    prepare_content()
    _thread.start_new_thread(check_on_content, ())
    # must be run last because it occupies thread
    start_server()

if __name__ == "__main__":
    main()
