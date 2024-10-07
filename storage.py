import json

posts_path = './storage/posts.json'
news_path = './storage/news.json'

def load_posts():
    posts = []
    with open(posts_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    return posts

def save_posts(data: dict):
    with open(posts_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
def load_news():
    posts = []
    with open(news_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    return posts

def save_news(data: dict):
    with open(news_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)