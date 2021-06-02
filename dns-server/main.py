import pickle
from socket import socket, AF_INET, SOCK_DGRAM, timeout

from dnslib import DNSRecord
from dnslib import QTYPE, RR, A, AAAA, NS, PTR
from scapy.all import *

qtype_to_init = {
    1: (QTYPE.A, A),
    2: (QTYPE.NS, NS),
    12: (QTYPE.PTR, PTR),
    28: (QTYPE.AAAA, AAAA),
}
ROOT_SERVER_IPS = ["198.41.0.4", "198.97.190.53", "192.33.4.12", "199.7.91.13", "192.5.5.241", "192.203.230.10"]
CACHE_FILE_NAME = "cache"


class Cache:
    TIME_CACHE_CLEANED = time.time()

    def __init__(self):
        self.cache = {}
        self.create()

    def create(self):
        for record_type in qtype_to_init.keys():
            self.cache[record_type] = {}

    def get_if_exist(self, parsed_packet):
        rname = str(parsed_packet.q.qname)
        q_type = parsed_packet.q.qtype
        if q_type not in self.cache or rname not in self.cache[q_type]:
            return
        replyed = parsed_packet.reply()
        replyed.add_answer(self.get_pr_record(q_type, rname))
        return replyed.pack()

    def get_pr_record(self, q_type, body):
        return RR(body, qtype_to_init[q_type][0], rdata=qtype_to_init[q_type][1](self.cache[q_type][body][0]), ttl=60)

    def add_records(self, records):
        for record in records:
            self.cache[record.rtype][str(record.rname)] = (str(record.rdata), time.time(), record.ttl)

    def remove_expired_records(self):
        for q_type in self.cache:
            for q_name in self.cache[q_type]:
                time_record_created = self.cache[q_type][q_name][1]
                ttl = self.cache[q_type][q_name][2]
                if time.time() - time_record_created > ttl:
                    del self.cache[q_type][q_name]
        self.TIME_CACHE_CLEANED = time.time()

    def save_cache(self, cache_file_name):
        with open(cache_file_name, 'wb+') as dump:
            pickle.dump(self, dump)

    @staticmethod
    def load_cache(cache_file_name):
        try:
            with open(cache_file_name, 'rb') as dump:
                cache = pickle.load(dump)
            print('Cache loaded')
            return cache
        except FileNotFoundError:
            print('Cache does not exist')
            return Cache()


def get_ip_for_request():
    return ROOT_SERVER_IPS[random.randint(0, len(ROOT_SERVER_IPS) - 1)]


CACHE = Cache.load_cache(CACHE_FILE_NAME)


class Server:
    def __init__(self, cache, host_ip="localhost", port=53):
        self.server = socket.socket(AF_INET, SOCK_DGRAM)
        self.server.settimeout(2)
        self.server.bind((host_ip, port))
        self.cache = cache

    def start(self):
        while True:
            data, address = self.get_packet()
            response = self.handle_packet(data)
            self.clear_cache_if_need(time.time())
            self.server.sendto(response, address)

    def clear_cache_if_need(self, time_now):
        if time_now - self.cache.TIME_CACHE_CLEANED > 30:
            self.cache.remove_expired_records()

    def get_packet(self):
        try:
            return self.server.recvfrom(256)
        except timeout:
            return self.get_packet()
        except Exception as e:
            self.server.close()
            print(e)
            exit()

    def handle_packet(self, packet: bytes) -> bytes:
        ip = get_ip_for_request()
        byte_response = None
        response = None
        while response is None or len(response.rr) == 0:
            parsed_packet = DNSRecord.parse(packet)
            cache_record = self.cache.get_if_exist(parsed_packet)
            if cache_record:
                return cache_record
            try:
                byte_response = parsed_packet.send(ip, timeout=4)
            except socket.timeout:
                ip = get_ip_for_request()
                continue
            response = DNSRecord.parse(byte_response)
            if response.header.rcode == 3:
                return byte_response
            self.cache.add_records(response.ar)
            ip = next((str(x.rdata) for x in response.ar if x.rtype == 1), -1)
            if ip == -1 and len(response.rr) == 0:
                resp = self.handle_packet(DNSRecord.question(str(response.auth[0].rdata)).pack())
                ip = str(DNSRecord.parse(resp).rr[0].rdata)
        self.cache.add_records(response.rr)
        return byte_response


def main():
    try:
        server = Server(CACHE)
        server.start()
    except (KeyboardInterrupt, SystemExit):
        print('Exit. Cache save..')
        CACHE.save_cache(CACHE_FILE_NAME)


if __name__ == '__main__':
    main()
