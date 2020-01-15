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
    # Now we split data into 100kb chunks
    chunks = list(split_into_chunks(data, 1024*300))
    n_chunks = len(chunks)

    chunk_urls = []
    pastebin = PasteBin()
    for (i, chunk) in enumerate(chunks):
        chunk = compress(chunk)
        chunk, nonce, authTag, key = encrypt(chunk)

        print('Uploading chunk {} out of {}...'.format(i, n_chunks))
        url = pastebin.upload(chunk)
        chunk_urls.append({
            'url': url,

            'nonce':   b85encode(nonce).decode(),
            'authTag': b85encode(authTag).decode(),
            'key':     b85encode(key).decode(),
        })

    with open(name + '.json', 'w') as f:
        json.dump({
            'chunks': chunk_urls,
            'name': name,
        }, f)


def download(fileinfo: dict):
    data = b''
    for (i, chunk) in enumerate(fileinfo['chunks']):
        print('Downloading chunk {} of {}'.format(i, len(fileinfo['chunks'])))
        data_chunk = requests.get(chunk['url']).content

        data_chunk = decrypt(data_chunk,
                             key     = b85decode(chunk['key']),
                             nonce   = b85decode(chunk['nonce']),
                             authTag = b85decode(chunk['authTag']))

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


