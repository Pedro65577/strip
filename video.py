import os
import time
import subprocess
import requests
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from requests.exceptions import ConnectionError



def download(url, file_name):
    """
    downloads video with ffmpeg
    """                                                                                                                                                  
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', url , '-c', 'copy', 'cache/' + file_name]
    process = subprocess.Popen(args)
    comm = process.communicate()[0]
    rc = process.returncode

    return rc

def gen_thumb(file_name):
    thumb = file_name +  '.jpeg'
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', 'cache/' + file_name, '-ss', '00:00:59', '-frames:v', '1','thumbs/' + thumb] #i know it looks weird
    if os.path.isfile('thumbs/' + thumb):
        return thumb
    else:
        return 'null'

def remove(file_name):
    """
    deletes video 
    """
    os.remove(file_name) #i will later add a double check to see if the file was actually uploaded

def slipt(file_name):
    """
    slipts file to avoid telegram upload limit
    """
    pass


 


