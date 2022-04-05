from urllib.parse import quote_plus as urlenc
from time import sleep
import requests
import sys
import re


class RequestSender:
    s = requests.Session()
    timeout = 12.0
    retry = 3
    err_wait = 1
    url = ''
    method = ''
    header = ''
    init_payload = ''
    left = ''
    right = ''

    @staticmethod
    def gen_header(source):
        lines = source.split('\n')

        method, path, _ = lines[0].split(' ')
        host, *port = lines[1].split(' ', 1)[1].split(':')
        port = port or [80]
        url = f"http://{host}:{port[0]}{path}"

        header = {}
        for line in lines[2:]:
            splitted = line.split(':', 1)
            splitted[1] = splitted[1].split(' ', 1)[1]
            if splitted[0] != 'Connection':
                header[splitted[0]] = splitted[1]

        return url, method, header

    def gen_payload(self, source):
        result = source.split(r'%5EPAYLOAD%5E')
        result[0] += self.left
        result[1] = self.right + result[1]

        return result

    def send_request(self, payload):
        from requests import Request
        req = Request()
        if self.method == 'POST':
            pl = self.init_payload[0] + payload + self.init_payload[1]
            req = Request(self.method, self.url, headers=self.header, data=pl)
        # if self.method == 'GET':
        #     req = Request(self.method, self.url, timeout=self.timeout,
        #                   headers=self.header, params=payload)
        else:
            print("error: now only support POST", file=sys.stderr)
            exit(1)

        prep = self.s.prepare_request(req)

        for _ in range(self.retry):
            try:
                return self.s.send(prep, timeout=self.timeout)
            except KeyboardInterrupt:
                exit(1)
            except:
                sleep(self.err_wait)
        else:
            raise Exception

    def __init__(self, args):
        input = open(args.p.request, mode='r').read().strip()
        raw_header, raw_payload = input.split('\n\n', 1)

        self.left = args.left
        self.right = args.right

        self.url, self.method, self.header = self.gen_header(raw_header)
        self.init_payload = self.gen_payload(raw_payload)

        if args.p.proxy:
            self.s.proxies.update(
                {'http': args.p.proxy, 'https': args.p.proxy})

    def __del__(self):
        self.s.close()
