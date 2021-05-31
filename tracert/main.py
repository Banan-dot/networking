import re
import subprocess
from json import loads
from urllib import request

from prettytable import PrettyTable

ip_regex = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
error_text = 'Произошла ошибка'
not_resolve = 'Не удается разрешить системное имя узла'
tracing = 'Трассировка маршрута'
jumps = 'прыжков'


class Row:
    def __init__(self, json):
        org = json.get('org') or '*'
        self.ip = json.get('ip') or '*'
        self.as_block = org.split()[0] or '*'
        self.provider = ' '.join(org.split()[1:]) or '*'
        self.city = json.get('city') or '*'
        self.country = json.get('country') or '*'


def get_info_about_ip(ip):
    try:
        return Row(loads(request.urlopen(f'https://ipinfo.io/{ip}/json').read()))
    except:
        return Exception()


def get_traceroute(hostname):
    return subprocess.Popen(["tracert", hostname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readline


def format_table(rows: list[Row]):
    table = PrettyTable()
    table.field_names = ['#', 'IP', 'AS', 'COUNTRY || CITY', 'PROVIDER']
    for i in range(len(rows)):
        table.add_row([
            i + 1,
            rows[i].ip,
            rows[i].as_block,
            f"{rows[i].country} {rows[i].city}",
            rows[i].provider
        ])
    return table


def get_route(address):
    get_as = False
    rows = []
    curr_ip = ""
    for line in iter(get_traceroute(address), ""):
        line = line.decode(encoding='cp866')
        if not_resolve in line:
            print(line)
            break
        elif tracing in line:
            print(line)
            curr_ip = ip_regex.findall(line)[0]
        elif jumps in line:
            get_as = True
        matches = ip_regex.findall(line)
        if not matches:
            continue
        ip = matches[0]
        if get_as:
            if ip == curr_ip:
                break
            try:
                rows.append(get_info_about_ip(ip))
            except:
                print(error_text)
                return
    return format_table(rows)


print(get_route("8.8.8.8"))
