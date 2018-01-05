#!/usr/bin/env python3

import discord
import asyncio
import collections
from random import choice
from time import mktime
from dateutil import tz
from datetime import datetime
from datetime import timedelta
from icalendar import Calendar
from urllib.request import urlopen

from_zone = tz.gettz("UTC")
to_zone = tz.gettz("Europe/Paris")

def getLessons():
    request = urlopen("https://adewebcons.unistra.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=22647,22645,556&projectId=1&calType=ical&nbWeeks=14")
    gcal = Calendar.from_ical(request.read())
    return gcal.walk("VEVENT")

def getNextLesson():
    nextLesson = None
    for lesson in getLessons():
        diff = lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone) - datetime.utcnow().replace(tzinfo=from_zone).astimezone(to_zone) - timedelta(minutes=60)
        if nextLesson == None or diff < nextLesson[0] and diff.total_seconds() > 0:
            nextLesson = list()
            nextLesson.append(diff)
            nextLesson.append(lesson.get("summary"))
            nextLesson.append(lesson.get("location"))
            nextLesson.append(lesson.get("description").split("\n")[3])
            nextLesson.append(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%d/%m/%Y"))
            nextLesson.append(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M"))
            nextLesson.append(lesson.get("dtend").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M"))
    return nextLesson

def getDayLessons(nextDay=None):
    lessons = getLessons()
    if nextDay is None:
        for lesson in lessons:
            date = lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).date()
            if nextDay == None or date < nextDay:
                nextDay = date

    dayLessons = dict()
    for lesson in lessons:
        if nextDay == lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).date():
            dayLesson = list()
            dayLesson.append(lesson.get("summary"))
            dayLesson.append(lesson.get("location"))
            dayLesson.append(lesson.get("description").split("\n")[3])
            dayLesson.append(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%d/%m/%Y"))
            dayLesson.append(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M"))
            dayLesson.append(lesson.get("dtend").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M"))
            dayLessons[mktime(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).timetuple())] = dayLesson
    return collections.OrderedDict(sorted(dayLessons.items())).items()

async def nextCommand(client, message):
    embed = discord.Embed(title="Prochain cours", description="Chargement en cours...", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    msg = await client.send_message(message.channel, embed=embed)

    nextLesson = getNextLesson()
    embed.description = "{}\n".format(nextLesson[1])
    embed.description += "Le {} de {} à {}\n".format(nextLesson[4], nextLesson[5], nextLesson[6])
    embed.description += "Professeur: {}\n".format(nextLesson[3])
    embed.description += "Salle: {}\n".format(nextLesson[2])
    await client.edit_message(msg, embed=embed)

async def dayCommand(client, message):
    embed = discord.Embed(title="Prochain journée de cours", description="Chargement en cours...", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    msg = await client.send_message(message.channel, embed=embed)

    args = message.content.split(" ")
    if len(args) >= 2:
        try:
            nextDay = datetime.strptime(args[1], "%d/%m/%Y").date()
        except ValueError:
            embed.description = "Veuillez entrer une date au format JJ/MM/YYYY"
        else:
            dayLessons = getDayLessons(nextDay)
            if len(dayLessons) >= 1:
                embed.description = "**Matin:**\n"
                for day, dayLesson in dayLessons:
                    if dayLesson[4] == "13:30":
                        embed.description += "\n**Après-midi:**\n"
                    embed.description += "{}\n".format(dayLesson[0])
                    embed.description += "Le {} de {} à {}\n".format(dayLesson[3], dayLesson[4], dayLesson[5])
                    embed.description += "Professeur: {}\n".format(dayLesson[2])
                    embed.description += "Salle: {}\n".format(dayLesson[1])
            else:
                embed.description = "Aucun cours"
    else:
        dayLessons = getDayLessons()
        embed.description = "**Matin:**\n"
        for day, dayLesson in dayLessons:
            if dayLesson[4] == "13:30":
                embed.description += "\n**Après-midi:**\n"
            embed.description += "{}\n".format(dayLesson[0])
            embed.description += "Le {} de {} à {}\n".format(dayLesson[3], dayLesson[4], dayLesson[5])
            embed.description += "Professeur: {}\n".format(dayLesson[2])
            embed.description += "Salle: {}\n".format(dayLesson[1])
    await client.edit_message(msg, embed=embed)

async def wtfCommand(client, message):
    embed = discord.Embed(title="What the Fuck ???", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_image(url="http://ljdchost.com/BUBgLiw.gif")
    await client.send_message(message.channel, embed=embed)

async def fuckCommand(client, message):
    fuck = ("https://ljdchost.com/CtDqj.gif", "http://ljdchost.com/Fmov8QZ.gif", "http://ljdchost.com/HLNRJHb.gif")
    embed = discord.Embed(title="Fuck !!!!", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_image(url=choice(fuck))
    await client.send_message(message.channel, embed=embed)

async def hendekCommand(client, message):
    embed = discord.Embed(title="Appellez les hendeks !!!", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/358718175636094976/393357739805376524/209cml.jpg")
    await client.send_message(message.channel, embed=embed)

async def testCommand(client, message):
    embed = discord.Embed(title="Test", description="Hello world !", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    await client.send_message(message.channel, embed=embed)

if __name__ == '__main__':
    client = discord.Client()

    @client.event
    async def on_ready():
        print("------- Bot Discord --------")
        print("Développé par Norman FELTZ")
        print("Connecté: ", client.user.name + "#" + client.user.discriminator)
        print("----------------------------")

    @client.event
    async def on_message(message):
        if message.content.startswith(".next"):
            await nextCommand(client, message)
        elif message.content.startswith(".day"):
            await dayCommand(client, message)
        elif message.content.startswith(".wtf"):
            await wtfCommand(client, message)
        elif message.content.startswith(".fuck"):
            await fuckCommand(client, message)
        elif message.content.startswith(".hendek"):
            await hendekCommand(client, message)
        elif message.content.startswith(".test"):
            await testCommand(client, message)

    with open("token.txt") as file:
        client.run(file.read())