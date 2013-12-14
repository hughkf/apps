#!/usr/bin/env python

"""Simple implementation of a file fetcher"""

import sys
import os
import urllib
import tarfile

def get_bathy(url, destination=os.getcwd(), force=False):
    r"""Get bathymetry file located at `url`

    Will check downloaded file's suffix to see if the file needs to be extracted
    """

    file_name = os.path.basename(url)
    output_path = os.path.join(destination, file_name)
    if not os.path.exists(output_path) or force:
        print "Downloading %s to %s..." % (url, output_path)
        urllib.urlretrieve(url, output_path)
        print "Finished downloading."
    else:
        print "Skipping %s, file already exists." % file_name

    # Extract file is applicable
    try:
        tarfile.open(output_path)
        tarfile.extractall()
        tarfile.close()
    except tarfile.ReadError:
        print "Could not untar file, may not be a tarfile or download failed."


if __name__ == "__main__":
    # Default URLs
    base_url = "http://users.ices.utexas.edu/~kyle/bathy/"

    # Override base_url
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    urls = [os.path.join(base_url, 'gulf_caribbean.tt3'),
            os.path.join(base_url, 'NOAA_Galveston_Houston.tt3'),
            os.path.join(base_url, 'galveston_tx.asc')]

    for url in urls:
        get_bathy(url)