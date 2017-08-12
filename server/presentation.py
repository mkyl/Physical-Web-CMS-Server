import os
import json
import urllib.request
import mimetypes
from pathlib import Path
from distutils.dir_util import copy_tree


HTML_PAGE_HEADER = "<!DOCTYPE html> \n <html> \n <body>"
HTML_PAGE_FOOTER = "</body> \n </html>"

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

def _decorate_content(content):
    url = urllib.request.pathname2url(content)
    mimetype = mimetypes.guess_type(url)[0].lower()
    if mimetype.startswith("image/"):
        return _decorate_image_content(content)
    elif mimetype.startswith("audio/"):
        return _decorate_sound_content(content)
    elif mimetype.startswith("video/"):
        return _decorate_video_content(content)
    else:
        raise ValueError("Couldn't determine filetype: " + content)

def _decorate_image_content(image):
    return '<img src="{image_url}"/>\n'.format(image_url=image)

def _decorate_sound_content(sound):
    return '<audio controls src="{sound_url}"></audio>\n'.format(sound_url=sound)

def _decorate_video_content(video):
    return '<video controls src="{video_url}"></video>\n'.format(video_url=video)


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
    page.append(HTML_PAGE_HEADER)
    page.append(_decorate_h1(title))
    page.append(_decorate_subtitle(subtitle))
    page.append(_decorate_unordered_list(beacons))
    page.append(HTML_PAGE_FOOTER)
    page = ''.join(page)

    with open(index_file, 'w') as f:
        f.write(page)

def _build_content_page(beacon, public_folder):
    content_filename = "index.html"
    content_file = os.path.join(public_folder, content_filename)
    Path(content_file).touch(exist_ok=True)

    title = beacon["address"]
    contents_html = []
    for content in beacon["contents"]:
        contents_html.append(_decorate_content(content))
    contents_html = ''.join(contents_html)

    page = []
    page.append(HTML_PAGE_HEADER)
    page.append(_decorate_h1(title))
    page.append(contents_html)
    page.append(HTML_PAGE_FOOTER)
    page = ''.join(page)

    with open(content_file, 'w') as f:
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
    copy_tree(active_exhibit_folder, public_folder)
    exhibit_metadata = _fetch_metadata(active_exhibit_folder)
    _build_index_page(exhibit_metadata, public_folder)
    for beacon in exhibit_metadata["beacons"]:
        beacon_folder = os.path.join(public_folder, beacon["address"])
        _build_content_page(beacon, beacon_folder)
