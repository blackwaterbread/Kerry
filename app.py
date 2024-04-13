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

print('[App] Loading recently posts ...')
storage: list = load_posts()

@client.event
async def on_ready():
    print(f'[Discord] Logged in as {client.user}')
    task.start()

@tasks.loop(seconds=5)
async def task():
    new_posts = get_posts()
    last_post = new_posts[-1]

    if not storage:
        storage.extend(new_posts)
        save_posts(storage)

    else:
        if last_post['id'] > storage[-1]['id']:
            channel = await client.fetch_channel(CHANNEL_ID)
            p = new_posts.index(storage[-1]) + 1
            # it will be problem when it bigger
            newer = new_posts[p:]
            storage.extend(newer)
            save_posts(storage)
            print(f'[App] New post detected: {len(newer)}')

            for post in newer:
                if (type(channel) == discord.channel.TextChannel):
                    image_attached = '[글]' if post['type'] == 'icon_txt' else '[이미지]'
                    embed = discord.Embed(
                        title = post['subject'],
                        description = f"{image_attached} {post['username']}",
                        url = f"${post_url}&no={post['id']}",
                        color = discord.Color.blue()
                    )
                    await channel.send(embed = embed)
                else:
                    # todo: Exception
                    return

            else:
                print('[App] No new post')

    next_interval = random.randint(300, 600)
    print(f'[App] Next refresh: {next_interval} s')
    task.change_interval(seconds=next_interval)

client.run(TOKEN)