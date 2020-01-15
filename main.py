#!/usr/bin/env python
import os, json, requests, zlib, math
from backends import PasteBin

from Crypto.Cipher import AES
from base64 import b85encode, b85decode

# TODO: Use
# https://cryptography.io/en/latest/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM
def encrypt(data: bytes):
    key = os.urandom(32)
    aesCipher = AES.new(key, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(data)

    return ciphertext, aesCipher.nonce, authTag, key

def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, authTag: bytes):
    aesCipher = AES.new(key, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext

def compress(data: bytes):
    return zlib.compress(data, 9)

def decompress(data: bytes):
    return zlib.decompress(data)

def split_into_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def upload(name: str, data: bytes):
    data = compress(data)
    data, nonce, authTag, key = encrypt(data)

    # Now we split data into 100kb chunks
    chunks = list(split_into_chunks(data, 1024*300))
    n_chunks = len(chunks)

    chunk_urls = []
    pastebin = PasteBin()
    for (i, chunk) in enumerate(chunks):
        print('Uploading chunk {} out of {}...'.format(i, n_chunks))
        url = pastebin.upload(chunk)
        chunk_urls.append(url)

    with open(name + '.json', 'w') as f:
        json.dump({
            'chunks': chunk_urls,
            'name': name,

            'nonce':   b85encode(nonce).decode(),
            'authTag': b85encode(authTag).decode(),
            'key':     b85encode(key).decode(),
        }, f)


def download(fileinfo: dict):
    data = b''
    for (i, url) in enumerate(fileinfo['chunks']):
        print('Downloading chunk {} of {}'.format(i, len(fileinfo['chunks'])))
        chunk = requests.get(url).content
        data += chunk

    data = decrypt(data,
                   key     = b85decode(fileinfo['key']),
                   nonce   = b85decode(fileinfo['nonce']),
                   authTag = b85decode(fileinfo['authTag']))

    data = decompress(data)

    # We got the file!
    print('Downloaded {} from {}'.format(fileinfo['name'], url))

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


