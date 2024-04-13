# 마지막 요소의 id가 새로 받아온 id보다 높으면 메세지 보내기
import json
from collections import OrderedDict

path = './storage/posts.json'

def load_posts():
    posts = []

    with open(path, 'r') as f:
        posts = json.load(f)

    return posts

def save_posts(data: dict):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)