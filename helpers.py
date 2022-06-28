import requests
import mimetypes
import os
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

class helpers:

    def get_ext(self, url):
        response = requests.head(url, timeout=10)
        try:
            content_type = response.headers['content-type']
            extension = mimetypes.guess_extension(content_type)
        except KeyError:
            extension = None
        if extension == '.m3u' or extension == '.m3u8':
            extension = '.mp4'

        return extension

    def get_duration(self, file_name):
        duration = 0
        metadata = extractMetadata(createParser('cache/' + file_name))
        if metadata is not None:
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds

        return duration

    def b_valid_url(self, url):
        try:
            request = requests.get(url)
            if request.status_code != 200:
                return False
            else:
                return True
        except Exception:
            return False

    def add_to_whitelist(self, id):
        with open('whitelist', 'a') as the_file:
            the_file.write(str(id) + '\n')
    
    def remove_whitelist(self, id):
        with open('whitelist', "r") as f:
            lines = f.readlines()
        with open('whitelist', "w") as f:
            for line in lines:
                if line.strip("\n") != str(id):
                    f.write(line)

    def b_whitelisted(self, id):
        with open('whitelist') as f:
            content = f.readlines()
            content = [x.strip() for x in content]
        if str(id) in content:
            return True
        else:
            return False


