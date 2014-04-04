import urllib, os.path
import requests
from bs4 import BeautifulSoup
from urlparse import urlparse

def retrieve(url, file_prefix='', target_dir=''):
    """
    Get a favicon given a URL. Retrurn None if unable to find the file.
    If the file is found, retrun it.
    
    We first check the icon meta tags in the markup. If it's not there,
    we check URL/facicon.ico.
    """

    # Help the user out if they didn't give us a protocol
    if not url.startswith('http'):
        url = 'http://' + url
    
    # Get the markup
    response = requests.get(url)
    
    if response.status_code == requests.codes.ok:
        soup = BeautifulSoup(response.content)
    else:
        pass
        # throw some exception here
        
    # Do we have a link element with the icon?
    icon_link = soup.find('link', rel='icon')
    if icon_link and icon_link.has_attr('href'):
        
        favicon_url = icon_link['href']
        
        # Sometimes we get a protocol-relative path
        if favicon_url.startswith('//'):
            parsed_uri = urlparse(url)
            favicon_url = parsed_uri.scheme + ':' + favicon_url
        
        response = requests.get(favicon_url)
        if response.status_code == requests.codes.ok:
            # we want to get the the filename from the url without any params
            parsed_uri = urlparse(favicon_url)
            favicon_filepath = parsed_uri.path
            favicon_path, favicon_filename  = os.path.split(favicon_filepath)
            
            local_filename = os.path.join(target_dir, file_prefix + favicon_filename)
            return _save_file(local_filename, response)
    else:
        # The favicon doesn't appear to be in the makrup
        # Let's look at the common locaiton, url/favicon.ico
        parsed_uri = urlparse(url)
        favicon_location = '{uri.scheme}://{uri.netloc}/favicon.ico'.format(\
            uri=parsed_uri)
                            
        response = requests.get(favicon_location)
        if response.status_code == requests.codes.ok:
            local_filename = os.path.join(local_filename_prefix, file_prefix + 
                'favicon.ico')
            return _save_file(local_filename, response)

    
    
def _save_file(local_filename, response):
    """
    A simple helper to save the favicon to disk
    """
    
    sanitized_filename = "".join([x if x.isalnum() else "" for x in local_filename]) 
    with open(sanitized_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
                    
    return local_filename