import socket
from datetime import datetime
import dnslib
from interface import LineDrawer, Colors
from cache_management import CacheManagementUnit, Packet


class CachingDNSServer:
    forwarder = '8.8.8.8'
    colors = Colors()
    line = f'{colors.BOLD}{LineDrawer().draw_horisontal_line()}{colors.ENDC}'

    def __init__(self):
        print(f'{self.line}\n{self.colors.BOLD}Перенаправляющий сервер: {self.forwarder}{self.colors.ENDC}')
        self.cmu = CacheManagementUnit()
        self.database = self.cmu.database
        self.set_socket()

    def set_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 53))

    def send_response(self, response, address):
        self.sock.connect(address)
        self.sock.sendall(response)
        self.sock.close()

    def get_cache_response(self, dns_record):
        print(f"{self.line}\n{self.colors.OKBLUE}Просматриваем кэш{self.colors.ENDC}")
        key = (str(dns_record.q.qname).lower(), dns_record.q.qtype)
        if key in self.database and self.database[key]:
            response = dns_record.reply()
            response.rr = [p.resource_record for p in self.database[key]]
            print(f"{self.line}\n{self.colors.OKGREEN}Ответ получен из кэша\n{response}{self.colors.ENDC}\n{self.line}")
            return response
        print(f"{self.line}\n{self.colors.WARNING}В кэше такого нет{self.colors.ENDC}\n{self.line}")

    def single_record(self, resource_record, date_time):
        key = (str(resource_record.rname).lower(), resource_record.rtype)
        if key in self.database:
            self.database[key].add(Packet(resource_record, date_time))
        else:
            self.database[key] = {Packet(resource_record, date_time)}
        print(f'{self.colors.HEADER}Добавлена новая запись:'
              f'\n{resource_record}{self.colors.ENDC}\n{self.line}')

    def several_records(self, dns_record):
        for resource in dns_record.rr + dns_record.auth + dns_record.ar:
            date_time = datetime.now()
            self.single_record(resource, date_time)

    def run_server(self):
        print(f'{self.colors.OKGREEN}{self.colors.BOLD}Сервер запущен{self.colors.ENDC}{self.colors.ENDC}\n{self.line}')
        try:
            try:
                while True:
                    data, addr = self.sock.recvfrom(2048)
                    if self.database:
                        self.cmu.delete_old_records()
                    try:
                        dns_record = dnslib.DNSRecord.parse(data)
                        self.several_records(dns_record)
                    except dnslib.DNSError as dnse:
                        print(f'{self.colors.FAIL}Возникла ошибка при разборе пакета: {dnse}{self.colors.ENDC}')
                        continue
                    if not dns_record.header.qr:
                        response = self.get_cache_response(dns_record)
                        try:
                            if response:
                                self.send_response(response.pack(), addr)
                                if self.database:
                                    self.cmu.save_cache(self.database)
                            else:
                                resp = dns_record.send(self.forwarder)
                                self.several_records(dnslib.DNSRecord.parse(resp))
                                self.send_response(resp, addr)
                            self.set_socket()
                        except Exception as e:
                            print(f'{self.line}\n{self.colors.WARNING}Сервер не отвечает: {e}{self.colors.ENDC}\n{self.line}')
            except Exception as e:
                print(f'{self.line}\n{self.colors.FAIL}Ошибка сервера! {e}{self.colors.ENDC}\n{self.line}')
        except KeyboardInterrupt:
            exit(0)
        finally:
            if self.database:
                self.cmu.save_cache(self.database)
            print(f'{self.line}\n{self.colors.FAIL}Сервер отключен:({self.colors.ENDC}\n{self.line}')


if __name__ == '__main__':
    server = CachingDNSServer()
    server.run_server()
