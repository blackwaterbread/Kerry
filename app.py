import os
import discord
import random
from discord.ext import tasks
from dotenv import load_dotenv
from crawler import get_posts
from storage import load_posts, save_posts

load_dotenv()

TOKEN = os.environ.get('TOKEN')
GUILD_ID = int(os.environ.get('GUILD_ID'))
CHANNEL_ID = int(os.environ.get('CHANNEL_ID'))
GALLERY_ID = os.environ.get('GALLERY_ID')

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

print('[App] Loading recently posts ...')
storage: list = load_posts()

@client.event
async def on_ready():
    print(f'[Discord] Logged in as {client.user}')
    task.start()

@tasks.loop(seconds=5)
async def task():
    posts = get_posts()
    # last_post = req_posts[-1]

    if not storage:
        storage.extend(posts)
        save_posts(storage)

    else:
        new_posts = list(filter(lambda x: x['id'] > storage[-1]['id'], posts))
        if new_posts:
            channel = await client.fetch_channel(CHANNEL_ID)
            storage.extend(new_posts)
            save_posts(storage)
            print(f'[App] New post detected: {len(new_posts)}')

            for post in new_posts:
                if (type(channel) == discord.channel.TextChannel):
                    image_attached = '[알수없음]'
                    try:
                        image_attached = post_type[post['type']]
                    except:
                        print('[App] Something unknown post type')

                    embed = discord.Embed(
                        title = post['subject'],
                        description = f"{image_attached} {post['username']}",
                        url = f"{post_url}&no={post['id']}",
                        color = discord.Color.blue()
                    )
                    msg = await channel.send(embed = embed)
                    print(f'[Discord] New post embed: {msg.id}')
                else:
                    # todo: Exception
                    return

        else:
            print('[App] No new post')

    next_interval = random.randint(300, 600)
    print(f'[App] Next refresh: {next_interval} s')
    task.change_interval(seconds=next_interval)

client.run(TOKEN)