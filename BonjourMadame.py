#!/usr/bin/env python3

import os
import discord
import bs4 as BeautifulSoup
from urllib.request import urlopen

if __name__ == '__main__':
    client = discord.Client()

    @client.event
    async def on_ready():
        html = urlopen("http://dites.bonjourmadame.fr/").read()
        soup = BeautifulSoup.BeautifulSoup(html, "html.parser")

        img = soup.find("div", attrs={"class": u"photo post"}).a.img

        embed = discord.Embed(title=img['alt'], colour=discord.Colour.dark_blue())
        embed.set_author(name="Filles nues, sexy et magnifiques - Bonjour Madame", icon_url="https://78.media.tumblr.com/avatar_1bbaa5b5cc2e_128.pnj")
        embed.set_image(url=img['src'])
        await client.send_message(discord.Object(id="358718838289989642"), embed=embed)

        client.close()
        os._exit(0)

    with open("/root/Bot/token.txt") as file:
        client.run(file.read())