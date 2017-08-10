import json
import os
from pathlib import Path

HOME_PAGE_HEADER = "<!DOCTYPE html> \n <html> \n <body>"
HOME_PAGE_FOOTER = "</body> \n </html>"

def _decorate_h1(text):
    return "<h1>" + text + "</h1>"

def _decorate_subtitle(text):
    return "<h2>" + text + "</h2>"

def _decorate_p(text):
    return "<p>" + text + "</p>"

def _decorate_unordered_list(items):
    result = []
    result.append("Beacons:")
    result.append("<ul>")
    for item in items:
        result.append("<li> <a href={beacon}>{beacon}</a></li>"
            .format(beacon=item))
    result.append("</ul>")
    result = "".join(result)
    return result

def _decorate_sound_content(sound):
    return None

def _decorate_image_content(image):
    return None

def _decorate_video_content(video):
    return None

def _build_index_page(website_metadata, public_folder):
    index_filename = "index.html"
    index_file = os.path.join(public_folder, index_filename)
    Path(index_file).touch(exist_ok=True)

    title = website_metadata["name"]
    subtitle = website_metadata["description"]
    beacons = []
    for beacon in website_metadata["beacons"]:
        beacons.append(beacon["address"])

    page = []
    page.append(HOME_PAGE_HEADER)
    page.append(_decorate_h1(title))
    page.append(_decorate_subtitle(subtitle))
    page.append(_decorate_unordered_list(beacons))
    page.append(HOME_PAGE_FOOTER)
    page = ''.join(page)

    with open(index_file, 'w') as f:
        f.write(page)

def _find_active_exhibit(exhibits_folder):
    metadata_file = os.path.join(exhibits_folder, 'metadata.json')
    with open(metadata_file) as data_file:    
        id = json.load(data_file)["active-exhibit"]
    active_exhibit_folder = os.path.join(exhibits_folder, str(id))
    return active_exhibit_folder

def _fetch_metadata(content_folder):
    metadata_file = os.path.join(content_folder, 'metadata.json')
    with open(metadata_file) as data_file:    
        return json.load(data_file)

def build_website(exhibits_folder, public_folder):
    os.makedirs(public_folder, exist_ok=True)
    active_exhibit_folder = _find_active_exhibit(exhibits_folder) 
    website_metadata = _fetch_metadata(active_exhibit_folder)
    _build_index_page(website_metadata, public_folder)
    #for beacon in website_metadata["beacons"]:
        #build_content_page(beacon)
