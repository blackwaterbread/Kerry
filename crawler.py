import os
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from dateutil.parser import parse

load_dotenv()
GALLERY_ID = os.environ.get('GALLERY_ID')
header = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36' }
encoding = 'utf-8'

gallery_url = f'https://gall.dcinside.com/mgallery/board/lists/?id={GALLERY_ID}'
news_arma3_url = 'https://arma3.com/news'
news_armareforger_url = 'https://reforger.armaplatform.com/news'

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

def get_arma_news():
    news_arma3 = []
    news_armareforger = []
    r_arma3 = requests.get(news_arma3_url, headers=header)
    r_armareforger = requests.get(news_armareforger_url, headers=header)
    r_arma3.encoding = encoding
    r_armareforger.encoding = encoding
    soup_arma3 = bs(r_arma3.text, 'lxml')
    soup_armareforger = bs(r_armareforger.text, 'lxml')
    
    # arma 3
    for news in soup_arma3.select_one('section#main-section > section#main-content > div.row').select('article'):
        body = news.select_one('div.panel-body > header > h1 > a')
        news_image_src = news.select_one('div.post-thumb-wrapper > a > img.img-thumbnail').attrs['src']
        news_link = body.attrs['href']
        news_title = body.attrs['title']
        news_content = news.select_one('div.post-excerpt > p').text
        news_date = news.select_one('footer > time').text
        news = {
            'id': parse(news_date).timestamp(),
            'news_title': news_title,
            'news_link': news_link,
            'news_content': news_content,
            'news_image_src': news_image_src,
            'news_date': news_date
        }
        news_arma3.append(news)
        
    # arma reforger
    for news in soup_armareforger.select_one('main > section.pb-16 > div.container > div').select('a.group'):
        news_link = news.attrs['href']
        article = news.select_one('article > div')
        labels = news.select_one('div > div')
        labels2 = labels.select('span')
        news_image_src = article.select_one('figure > span').find('noscript').find('img').attrs['src']
        news_title = labels.select_one('h2').text
        news_date = labels2[0].text
        news_category = labels2[1].text
        news = {
            'id': parse(news_date).timestamp(),
            'news_title': news_title,
            'news_link': f'https://reforger.armaplatform.com{news_link}',
            'news_category': news_category,
            'news_image_src': news_image_src.replace(' ', '%20'),
            'news_date': news_date,
        }
        news_armareforger.append(news)
        
    return { 'arma3': news_arma3, 'arma_reforger': news_armareforger }