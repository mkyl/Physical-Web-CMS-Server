import sync
import presentation

import os
import http
import socketserver
import _thread
import time
import tempfile

MODULE_FOLDER = os.path.abspath(os.path.dirname(__file__))
MODULE_PARENT = os.path.dirname(MODULE_FOLDER)
TEMP_FOLDER = tempfile.gettempdir()
CONTENT_FOLDER = os.path.join(TEMP_FOLDER, "physical-web-server") 
PUBLIC_FOLDER = os.path.join(MODULE_PARENT, "export")

PORT = 8080
CHECK_INTERVAL = 300 # seconds

def start_server():
    os.chdir(PUBLIC_FOLDER)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print(" [i] serving at port", PORT)

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
    # cannot use this server because Physical Web URL must be https
    # start_server()

if __name__ == "__main__":
    main()
