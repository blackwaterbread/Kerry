import json

path = './storage/posts.json'

def load_posts():
    posts = []
    with open(path, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    return posts

def save_posts(data: dict):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)