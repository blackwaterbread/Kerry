import os
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

load_dotenv()
GALLERY_ID = os.environ.get('GALLERY_ID')

gallery_url = f'https://gall.dcinside.com/mgallery/board/lists/?id={GALLERY_ID}'
header = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' }
encoding = 'utf-8'

def get_posts(page: int = 1):
    posts = []
    r = requests.get(f'{gallery_url}&page={page}', headers=header)
    r.encoding = encoding
    soup = bs(r.text, 'lxml')

    for post in soup.select('tr.us-post'):
        user = post.select_one('td.ub-writer')
        username, user_ip, user_uid = user['data-nick'], user['data-ip'], user['data-uid']

        post = {
            'id': int(post['data-no']),
            'type': post['data-type'],
            'username': f'{username} ({user_uid})' if user_ip == "" else f'{username} ({user_ip})',
            'subject': post.select_one('a[href]').get_text().strip()
        }

        posts.append(post)

    return sorted(posts, key = lambda x: x['id'])