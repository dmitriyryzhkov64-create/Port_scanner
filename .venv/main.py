import socket
from concurrent.futures import ThreadPoolExecutor
import requests

def check_http(ip, port, schema):
    try:
        response = requests.get(f"{schema}://{ip}:{port}", timeout=2, verify=False)
        print(f'Анализ {schema.upper()} на порту {port}')
        print(f'[*] Статус ответа: {response.status_code}')
        print(f'[*] Сервер: {response.headers.get("Server", "Неизвестно")}')
        security_headers = ['Content-Security-Policy', 'X-Frame-Options', 'X-Content-Type-Options']

        for header in security_headers:
            if header not in response.headers:
                print(f"[!] Внимание: Отсутствует заголовок {header}")

    except requests.exceptions.RequestException as e:
        print(f"[X] Не удалось подключиться к HTTP на порту {port}")


def check(ip, port, family):
    with socket.socket(family, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        if s.connect_ex((ip, port)) == 0:
            print(f'[+] Найден открытый порт: {port}')
            return port
    return None

flag = False
result = []

while not flag:
    host = input('Введите ip или домен сайта: ')
    try:
        info = socket.getaddrinfo(host, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
        first_result = info[0]
        family = first_result[0]
        sockaddr = first_result[4]
        ip_address = sockaddr[0]
        flag = True

    except socket.gaierror:
        print(f'Сайт ({host}) не найден. Проверьте правильность написания сайта')

with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(check, ip_address, port, family) for port in range(1, 1025)]
    print('\n')
    for f in futures:
        res = f.result()
        if res:
            result.append(res)

print(f'\nОткрыте порты для хоста {host}: {sorted(result)}')

print("\nЗапуск глубокого анализа HTTP:\n")
for port in result:
    if port == 80:
        check_http(ip_address, port, schema="http")
    elif port == 443:
        check_http(ip_address, port, schema="https")

