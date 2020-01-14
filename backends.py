class TermBin:
    def upload(self, data: bytes) -> str:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('termbin.com', 9999))

            # SHUT_WR is needed else termbin might expect more data.
            s.sendall(data)
            s.shutdown(socket.SHUT_WR)

            url = s.recv(128)
            return url.decode('UTF-8').rstrip(' \t\r\n\0')


class PasteRs:
    def upload(self, data: bytes) -> str:
        import requests
        resp = requests.post('https://paste.rs/', data = data)
        return resp.text.rstrip(' \t\r\n\0')


# Ripped off https://github.com/acidvegas/pastebin thanks acidvegas <3
class PasteBin:
    def __init__(self, api_dev_key, timeout = 10):
        self.api_dev_key = api_dev_key
        self.timeout = timeout

    def api_call(self, method, params):
        import urllib.parse
        import urllib.request

        response = urllib.request.urlopen('https://pastebin.com/api/' + method,
                                          urllib.parse.urlencode(params).encode('utf-8'),
                                          timeout=self.timeout)
        return response.read().decode()

    def upload(self, data):
        params = {
            'api_dev_key': self.api_dev_key,
            'api_option': 'paste',
            'api_paste_code': data,
            'api_paste_expire_date': 'N'
        }

        url = self.api_call('api_post.php', params)

        # Could hardcode as 20, but risky
        n = url.rfind('/')

        return url[:n] + '/raw' + url[n:]


backends = [PasteRs(), PasteBin('42d8c13038f701723cf3d145fd6cc08b'), TermBin()]
