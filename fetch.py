#!/usr/bin/env python3

import os
import getopt
import hashlib
import sys
import time
import urllib3
import validators
import yaml

from logging2 import Logger
from os.path import exists


logger = Logger('app')
http   = urllib3.PoolManager()

def download(req: dict, file_path='', attempts=2):
    """Downloads a URL content into a file (with large file support by streaming)

    :param req: request dictionary
    :param file_path: Local file name to contain the data downloaded
    :param attempts: Number of attempts
    :return: New file path. Empty string if the download failed
    """
    url = req['url']
    validation_type = req['validation']['type']

    if not validators.url(url):
        logger.warning(f'Skipping Invalid URL: {url}')
        return ''
    
    if 'auth' in req:
        logger.warning(f'Request: {url} requires auth.')
        return ''
    
    if validation_type == "sha256":
        if not file_path:
            file_path = os.path.realpath(os.path.basename(url))

        logger.debug(f'Downloading {url} content to {file_path}')

        for attempt in range(1, attempts+1):
            try:
                if attempt > 1:
                    time.sleep(10)  # 10 seconds wait time between downloads
                with http.request('GET', url, preload_content=False) as response:
                    with open(file_path, 'wb') as out_file:
                        while True:
                          data = response.read(8192)
                          if not data:
                              break
                          out_file.write(data)
                    response.release_conn()
                    logger.debug('Download finished successfully')
                    verify_checksum(req, file_path)
                    return file_path
            except Exception as ex:
                logger.error(f'Attempt #{attempt} failed with error: {ex}')

    return ''


def verify_checksum(req, filename):
    """Verify sha256 checksum vs calculated checksum

    :type req: dict
    :param req: requirement dictionary
    :type filename: str
    :param filename: original filename

    Returns:
    bool: True if checksum matches or False if not sha256 request
    """

    checksum = req['validation']['value']

    logger.debug(f"Validating {filename} matches {checksum}")

    with open(filename, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        calculated_checksum = hashlib.sha256(bytes).hexdigest()

    logger.debug("calculated checksum {0} for {1}".format(calculated_checksum,
                                                          filename))
    if calculated_checksum != checksum:
        logger.error(
            f"checksum verification failed for {filename}, expected {checksum} got {calculated_checksum}")
        return False
    
    return True


def main(argv):
    # Process command-line arguments
    hm_path  = ""
    manifest = ""

    usage = []
    usage.append("fetch.py <args>")
    usage.append("Argument              Description")
    usage.append("  --hm-path        Path to the hardening_manifest.yaml")

    try:
        opts, args = getopt.getopt(argv, "h", ["hm-path="])
    except getopt.GetoptError:
        for i in usage:
            print(i)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("--hm-path"):
            hm_path = arg

    if not hm_path:
        hm_path = os.getcwd() + "/hardening_manifest.yaml"
    
    dir_path = os.path.dirname(hm_path)

    logger.info("Executing downloads to: " + dir_path)

    # Read hardening manifest
    try:
        with open(hm_path, 'r') as stream:
            manifest = yaml.safe_load(stream)
        
    except yaml.YAMLError as exc:
        logger.error(
            f"Unable to load yaml manifest: {exc}")
    
    # Process resources
    if any(manifest['resources']):
        for req in manifest['resources']:
            if 'filename' in req:
                logger.debug(f"Processing: {req['filename']}")

                req_path = f"{dir_path}/{req['filename']}"
                
                if exists(req_path):
                    if not verify_checksum(req, req_path):
                        download(req, req_path)
                else:
                    download(req, req_path)
            else:
                logger.warning(f"Skipping: {req['url']}")
    else:
        logger.error(f"No resources to fetch.")
        exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
