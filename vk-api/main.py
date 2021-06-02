import json
import socket
import ssl
from datetime import datetime

token = "b61145d694ec154d927af0c0c38cac9b6b82ecbfcaba4bdfed2c7b59e9eb27abae26b436f24582ab34b14"
user_id = "208550102"
host = "api.vk.com"


def qet_wall(token: str, host: str, user_id: str):
    return f"""GET /method/wall.get?access_token={token}&owner_id={user_id}&v=5.124 HTTP/1.1\nHost: {host}\nAccept: */*\n\n"""


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as api:
    api.connect((host, 443))
    api = ssl.wrap_socket(api)
    api.send((qet_wall(token, host, user_id) + '\n').encode())
    data = bytearray()
    try:
        while True:
            fragment = api.recv(65535)
            if not fragment:
                break
            data.extend(fragment)
    except:
        pass
    body = json.loads(data.decode().split('\n')[-1])['response']
    posts = body['items']
    for post in posts:
        post_id = post['id']
        owner_id = post['from_id']
        date = datetime.utcfromtimestamp(int(post['date'])).strftime('%Y-%m-%d %H:%M:%S')
        text = post['text']
        print(f'Post #{post_id}\nAuthorId: {owner_id}\nDate: {date}\nText: {text}\n\n')
    if len(posts) == 0:
        print('Было загружено 0 постов')
