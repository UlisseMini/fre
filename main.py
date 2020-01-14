#!/usr/bin/env python
import os, json, requests, zlib
from backends import backends

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

def upload(name: str, data: bytes):
    data = compress(data)
    data, nonce, authTag, key = encrypt(data)

    urls = []
    for backend in backends:
        url = backend.upload(data)
        urls.append(url)

    print(json.dumps({
        'urls': urls,
        'name': name,

        'nonce':   b85encode(nonce).decode(),
        'authTag': b85encode(authTag).decode(),
        'key':     b85encode(key).decode(),
    }))


def download(fileinfo: dict):
    for url in fileinfo['urls']:
        try:
            data = requests.get(url).content

            data = decrypt(data,
                           key     = b85decode(fileinfo['key']),
                           nonce   = b85decode(fileinfo['nonce']),
                           authTag = b85decode(fileinfo['authTag']))

            data = decompress(data)

            # We got the file!
            print('Downloaded {} from {}'.format(fileinfo['name'], url))
            break
        except Exception as e:
            # we'll getem next time (in the next loop iteration)
            print('Failed to get file from {}, {}'.format(url, e))

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


