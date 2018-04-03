#!/usr/bin/env python3

import os
import html
import discord
import feedparser
from sys import argv
from time import mktime
from datetime import datetime
from bs4 import BeautifulSoup

feed = feedparser.parse("http://dites.bonjourmadame.fr/rss")

def isInFile(title):
    with open(argv[0].replace("py", "txt"), "r") as file:
        for line in file:
            if title in line:
                return True
        return False

def addToFile(title):
    with open(argv[0].replace("py", "txt"), "a") as file:
        file.write(title + "\n")


if __name__ == '__main__':
    client = discord.Client()

    @client.event
    async def on_ready():
        news = list()
        for item in feed["entries"]:
            if not isInFile(item["title"]):
                soup = BeautifulSoup(item["summary_detail"]["value"], "html.parser")
                news.append([item["title"], item["link"], soup.p.get_text(), soup.img.get("src"), datetime.fromtimestamp(mktime(item["published_parsed"]))])

        if len(news) >= 1:
            for item in news:
                if item[4].weekday() != 5 and item[4].weekday() != 6:
                    embed = discord.Embed(title=item[0], description=item[2], colour=discord.Colour.dark_blue(), url=item[1])
                    embed.set_author(name=feed["feed"]["title"], icon_url="https://78.media.tumblr.com/avatar_1bbaa5b5cc2e_128.pnj")
                    embed.set_image(url=item[3])
                    await client.send_message(discord.Object(id="358718838289989642"), embed=embed)

                addToFile(item[0])

        client.close()
        os._exit(0)

    with open("/root/Bot/token.txt") as file:
        client.run(file.read())