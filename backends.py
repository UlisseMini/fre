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

backends = [TermBin(), PasteRs()]
