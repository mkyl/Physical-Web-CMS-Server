# Physical Web CMS Server
Server-side application to process content produced by [Physical Web Beacon Manager app](https://github.com/mkyl/Physical-Web-CMS-Android).

## Installation
1. `client_secret.json` must be downloaded from Drive API console and placed into working directory
2. `pip -r install requirements.txt`
3. Run `python server/server.py` and follow on-screen instructions to log in to Google Drive account
4. HTML content for exhibit will be generated in `.\export\`
5. Host `.\export\` content on an HTTPS server. Github Pages is a good choice.
6. Configure companion Android app to point to server, by setting "Server URI" in the app settings menu.
