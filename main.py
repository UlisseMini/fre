#!/usr/bin/env python
import os, json, requests, zlib, math
from backends import TermBin

from base64 import b85encode, b85decode

def compress(data: bytes):
    return zlib.compress(data, 9)

def decompress(data: bytes):
    return zlib.decompress(data)

def split_into_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def upload(name: str, data: bytes):
    chunks = list(split_into_chunks(data, 1024*500))
    n_chunks = len(chunks)

    chunk_urls = []
    pastebin = TermBin()
    for (i, chunk) in enumerate(chunks):
        chunk = compress(chunk)

        url = pastebin.upload(chunk)
        print('Uploaded chunk {} ({}) out of {}...'.format(i, url, n_chunks))
        chunk_urls.append(url)

    with open(name + '.json', 'w') as f:
        json.dump({
            'chunks': chunk_urls,
            'name': name,
        }, f)


def download(fileinfo: dict):
    data = b''
    for (i, url) in enumerate(fileinfo['chunks']):
        print('Downloading chunk {} of {}'.format(i, len(fileinfo['chunks'])))
        data_chunk = requests.get(url).content
        data_chunk = decompress(data_chunk)

        data += data_chunk

    # We got the file!
    print('Downloaded {}'.format(fileinfo['name']))

    with open(fileinfo['name'], 'wb') as f:
        f.write(data)

# TODO: Use argparse
if __name__ == '__main__':
    from sys import argv
    if len(argv) < 3:
        print('''Usage: {} [cmd] file
    Examples
        {} put file.txt
        {} get fileinfo.json
        '''.format(argv[0], argv[0], argv[0]))
        exit()


    # Read the file
    if argv[1] == 'put':
        with open(argv[2], 'rb') as f:
            data = f.read()
        upload(argv[2], data)
    elif argv[1] == 'get':
        with open(argv[2], 'r') as f:
            finfo = json.load(f)
        download(finfo)


