import httplib2
import os
import argparse
import tzlocal

from pathlib import Path
from dateutil.parser import parse
from datetime import datetime 

from apiclient import discovery
from apiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/drive.appdata'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Physical Web CMS Server'

TZ = tzlocal.get_localzone()


def _get_credentials():
    """
    Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
        'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, 
            SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = argparse.ArgumentParser(parents=[tools.argparser]
            ).parse_args()
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            credentials = tools.run(flow, store)
        print('Storing credentials to: ' + credential_path)

    return credentials

def _get_exhibit_folder(service):
    query = "mimeType = 'application/vnd.google-apps.folder' \
        and 'appDataFolder' in parents"
    results = service.files().list(
        spaces='appDataFolder',
        q = query,
        pageSize=10,
        fields="nextPageToken, files(id, name)").execute()

    items = results.get('files', [])
    if not items:
        print(' [⛔] No exhibit folder found, please run the companion app at least once before proceeding.')
        raise SystemExit("Program terminated: Google Drive content error")
    elif len(items) != 1:
        print(' [⚠] More than one root exhibit folder found. Drive database is corrupted. Will attempt to proceed.')

    return items[0]

def _download_drive_file(drive_file, local_folder, drive_service):
    file_id = drive_file['id']
    local_file_name = os.path.join(local_folder, drive_file["name"])

    if Path(local_file_name).exists():
        drive_file_modified = drive_service.files().get(fileId=file_id, fields="modifiedTime").execute()['modifiedTime']
        modified_remote = parse(drive_file_modified)

        modified_local = datetime.fromtimestamp(os.path.getmtime(local_file_name))
        modified_local = TZ.localize(modified_local)
        if modified_local > modified_remote:
            print(" [🛈] File cached, not downloading: " + drive_file["name"])
            return
    else:
        Path(local_file_name).touch(exist_ok=True)

    with open(local_file_name, 'wb') as local_file:
        request = drive_service.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(local_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(" [🛈] Downloading " + drive_file["name"] + ": " + str(status.progress() * 100) + "%")

def _download_drive_folder(drive_folder, local_folder, drive_service):
    if drive_folder is None:
        return

    os.makedirs(local_folder, exist_ok=True)
    files_only_query = "mimeType != 'application/vnd.google-apps.folder'"
    folders_only_query = "mimeType = 'application/vnd.google-apps.folder'"
    children_query = "'" + drive_folder["id"] + "' in parents"

    # download file children first
    results = drive_service.files().list(
        spaces='appDataFolder',
        q = children_query + " and " + files_only_query,
        pageSize=10,
        fields="nextPageToken, files(id, name)").execute()

    items = results.get('files', [])
    for drive_file in items:
        _download_drive_file(drive_file, local_folder, drive_service)

    # download subfolders now
    results = drive_service.files().list(
        spaces='appDataFolder',
        q = folders_only_query + " and " + children_query,
        pageSize=10,
        fields="nextPageToken, files(id, name)").execute()

    items = results.get('files', [])
    for remote_folder in items:
        _download_drive_folder(remote_folder, os.path.join(local_folder, remote_folder["name"]), drive_service)

def initialSync(local_folder):
    print(' [🛈] Begining initial synchronization')
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    exhibit_folder = _get_exhibit_folder(service)
    _download_drive_folder(exhibit_folder, local_folder, service)
    print(' [✓] Initial synchronization complete')
