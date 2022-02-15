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
from operator import itemgetter

logger = Logger('app')
http   = urllib3.PoolManager()

def download(url: str, file_path='', attempts=2):
    """Downloads a URL content into a file (with large file support by streaming)

    :param url: URL to download
    :param file_path: Local file name to contain the data downloaded
    :param attempts: Number of attempts
    :return: New file path. Empty string if the download failed
    """
    if not validators.url(url):
        logger.error(f'Invalid URL: {url}')
        return ''

    if not file_path:
        file_path = os.path.realpath(os.path.basename(url))

    logger.info(f'Downloading {url} content to {file_path}')

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
                logger.info('Download finished successfully')
                return file_path
        except Exception as ex:
            logger.error(f'Attempt #{attempt} failed with error: {ex}')
    return ''


def verify_checksum(checksum, filename):
    """
        Verify sha256 checksum vs calculated checksum

        :type checksum: str
        :param checksum: expected checksum of data
        :type filename: str
        :param checksum: original filename
        """
    logger.info(f"Validating {filename} matches {checksum}")

    with open(filename, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        calculated_checksum = hashlib.sha256(bytes).hexdigest()

    logger.debug("calculated checksum {0} for {1}".format(calculated_checksum,
                                                          filename))
    if calculated_checksum != checksum:
        logger.error(
            f"checksum verification failed, expected {checksum} got {calculated_checksum}")
        exit(1)

def main(argv):
    # Process command-line arguments
    hm_path  = ""
    manifest = ""

    usage = []
    usage.append("getemall.py <args>")
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

    if hm_path:
        dir_path = os.path.dirname(hm_path)
    else:
      logger.info(f"Directory path could not be found: {hm_path}")
      exit(1)

    logger.info("Executing downloads to: " + dir_path)

    # Read hardening manifest
    try:
        with open(hm_path, 'r') as stream:
            manifest = yaml.safe_load(stream)
        
    except yaml.YAMLError as exc:
        logger.info(
            f"Unable to load yaml manifest: {exc}")
    
    # Get resources
    if any(manifest['resources']):
        # Process resources
        for req in manifest['resources']:
            logger.info(f"Processing: {req['filename']}")
            download(req['url'], f"{dir_path}/{req['filename']}")

            if req['validation']['type'] == "sha256":
                verify_checksum(req['validation']['value'],
                                f"{dir_path}/{req['filename']}")
    else:
        logger.info(f"No resources to fetch.")
        exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
