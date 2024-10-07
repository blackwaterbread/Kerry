import os
import discord
import random
from discord.ext import tasks
from git import Repo
from log import printLog
from dotenv import load_dotenv
from crawler import get_posts, get_arma_news
from storage import load_posts, save_posts, load_news, save_news

load_dotenv()

TOKEN = os.environ.get('TOKEN')
GUILD_ID = int(os.environ.get('GUILD_ID'))
GALLERY_ID = os.environ.get('GALLERY_ID')
POST_CHANNEL_ID = int(os.environ.get('POST_CHANNEL_ID'))
NEWS_CHANNEL_ID = int(os.environ.get('NEWS_CHANNEL_ID'))

post_url = f'https://gall.dcinside.com/mgallery/board/view/?id={GALLERY_ID}'

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.dm_messages = True
intents.message_content = True

client = discord.Client(intents=intents)

post_type = {
    'icon_notice': '[공지]',
    'icon_txt': '[글]',
    'icon_pic': '[이미지]',
    'icon_movie': '[동영상]',
    'icon_recomtxt': '[념글]',
    'icon_recomimg': '[념글_이미지]',
    'icon_recomovie': '[념글_동영상]'
}

printLog('[App] Loading recently posts ...')
post_storage = None
news_storage = None

@client.event
async def on_ready():
    printLog(f'[App] Logged in as {client.user}')
    repo = Repo('./')
    commit = repo.head.commit
    presence = discord.Game(f'kerry/{commit.hexsha[0:7]}')
    await client.change_presence(status = discord.Status.online, activity = presence)
    ref_post_task.start()
    ref_news_task.start()

@tasks.loop(seconds=5)
async def ref_news_task():
    global news_storage
    news = get_arma_news()

    if not news_storage:
        news_storage = load_news()

    new_news_arma3 = None
    if (len(news_storage['arma3']) > 0):
        new_news_arma3 = list(filter(lambda x: x['id'] > news_storage['arma3'][-1]['id'], news['arma3']))
    else:
        new_news_arma3 = news['arma3']

    new_news_armareforger = None
    if (len(news_storage['arma_reforger']) > 0):
        new_news_armareforger = list(filter(lambda x: x['id'] > news_storage['arma_reforger'][-1]['id'], news['arma_reforger']))
    else:
        new_news_armareforger = news['arma_reforger']

    if new_news_arma3:
        channel = await client.fetch_channel(NEWS_CHANNEL_ID)
        news_storage['arma3'].extend(new_news_arma3)
        save_news(news_storage)
        printLog(f'[App] Arma3 news detected: {len(new_news_arma3)}')

        for news in new_news_arma3:
            if (type(channel) == discord.channel.TextChannel):
                embed = discord.Embed(
                    title = news['news_title'],
                    url = news['news_link'],
                    description = news['news_content'],
                    color = discord.Color.blue()
                )

                embed.set_footer(text = news['news_date'])
                embed.set_thumbnail(url = news['news_image_src'])

                msg = await channel.send(embed = embed)
                printLog(f'[App] New arma3 news embed: {msg.id}')
            else:
                # todo: Exception
                return

    else:
        printLog('[App] No arma3 news')
        
    if new_news_armareforger:
        channel = await client.fetch_channel(NEWS_CHANNEL_ID)
        news_storage['arma_reforger'].extend(new_news_armareforger)
        save_news(news_storage)
        printLog(f'[App] Arma Reforger news detected: {len(new_news_armareforger)}')
        
        for news in new_news_armareforger:
            if (type(channel) == discord.channel.TextChannel):
                embed = discord.Embed(
                    title = news['news_title'],
                    url = news['news_link'],
                    description = news['news_category'],
                    color = discord.Color.blue()
                )

                embed.set_footer(text = news['news_date'])
                embed.set_image(url = news['news_image_src'])

                msg = await channel.send(embed = embed)
                printLog(f'[App] New reforger news embed: {msg.id}')
            else:
                # todo: Exception
                return

    else:
        printLog('[App] No reforger news')

    next_interval = 3600
    printLog(f'[App] Next news refresh: {next_interval} s')
    ref_post_task.change_interval(seconds=next_interval)

@tasks.loop(seconds=5)
async def ref_post_task():
    global post_storage
    posts = get_posts()
    # last_post = req_posts[-1]

    if not post_storage:
        post_storage = load_posts()

    new_posts = None
    if (len(post_storage) > 0):
        new_posts = list(filter(lambda x: x['id'] > post_storage[-1]['id'], posts))
    else:
        new_posts = posts

    if new_posts:
        channel = await client.fetch_channel(POST_CHANNEL_ID)
        post_storage.extend(new_posts)
        save_posts(post_storage)
        printLog(f'[App] New post detected: {len(new_posts)}')

        for post in new_posts:
            if (type(channel) == discord.channel.TextChannel):
                image_attached = '[알수없음]'
                try:
                    image_attached = post_type[post['type']]
                except:
                    printLog('[App] Something unknown post type')

                embed = discord.Embed(
                    title = post['subject'],
                    description = f"{image_attached} {post['username']}",
                    url = f"{post_url}&no={post['id']}",
                    color = discord.Color.blue(),
                )
                msg = await channel.send(embed = embed)
                printLog(f'[App] New post embed: {msg.id}')
            else:
                # todo: Exception
                return

    else:
        printLog('[App] No new post')

    next_interval = random.randint(300, 600)
    printLog(f'[App] Next post refresh: {next_interval} s')
    ref_post_task.change_interval(seconds=next_interval)

client.run(TOKEN)