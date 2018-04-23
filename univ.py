#!/usr/bin/env python3

import discord
import asyncio
import bs4 as BeautifulSoup
from random import choice
from time import mktime
from dateutil import tz
from datetime import datetime
from datetime import timedelta
from icalendar import Calendar
from collections import OrderedDict
from urllib.request import urlopen

from_zone = tz.gettz("UTC")
to_zone = tz.gettz("Europe/Paris")

def getLessons():
    try:
        request = urlopen("https://adewebcons.unistra.fr/jsp/custom/modules/plannings/anonymous_cal.jsp?resources=22647,22645,556&projectId=1&calType=ical&nbWeeks=14")
    except urllib.error.HTTPError:
        getLessons()
    else:
        gcal = Calendar.from_ical(request.read())
        return gcal.walk("VEVENT")

def getNextDay(lessons):
    nextDay = None
    for lesson in lessons:
        date = lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).date()
        if nextDay == None or date < nextDay:
            nextDay = date
    return nextDay

def getNextLesson(lessons):
    nextLesson = None
    for lesson in lessons:
        diff = lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone) - datetime.utcnow().replace(tzinfo=from_zone).astimezone(to_zone) + timedelta(minutes=60)
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

def getDayLessons(lessons, nextDay):
    dayLessons = dict()
    for lesson in lessons:
        if nextDay == lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).date():
            dayLesson = list()
            dayLesson.append(lesson.get("summary"))
            dayLesson.append(lesson.get("location"))
            dayLesson.append(lesson.get("description").split("\n")[3])
            dayLesson.append(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M"))
            dayLesson.append(lesson.get("dtend").dt.replace(tzinfo=from_zone).astimezone(to_zone).strftime("%H:%M"))
            dayLessons[mktime(lesson.get("dtstart").dt.replace(tzinfo=from_zone).astimezone(to_zone).timetuple())] = dayLesson
    return OrderedDict(sorted(dayLessons.items())).items()

async def helpCommand(client, message):
    commands = OrderedDict()
    commands["help"] = [".help [command]", "Si un argument est passé, on affiche l'aide de la commmande, sinon affiche la liste des commandes"]
    commands["test"] = [".test", "Affiche « Hello world! »"]
    commands["next"] = [".next", "Affiche le prochain cours"]
    commands["day"] = [".day [DD/MM/YYYY]", "Affiche les cours de la journée passé en arguments ou la prochaine journée de cours"]
    commands["menu"] = [".menu [i]", "Affiche le menu"]
    commands["wtf"] = [".wtf", "Affiche la super grimace de Mélenchon"]
    commands["fuck"] = [".fuck", "Affiche une image « fuck » parmis une sélection"]
    commands["hendek"] = [".hendek", "Affiche l'image « Appelez les hendeks !! »"]
    commands["cheh"] = [".cheh", "Affiche l'image « Cheh !! »"]
    commands["gogole"] = [".gogole", "Affiche l'image « Alerte au gogole !! »"]
    
    args = message.content.split(" ")
    if len(args) >= 2:
        embed = discord.Embed(colour=discord.Colour.dark_red())
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        if args[1] in commands:
            embed.description = "**{}**\n".format(commands[args[1]][0])
            embed.description += "\t\t{}\n\n".format(commands[args[1]][1])
        else:
            embed.description = "Cette commande n'existe pas"
    else:
        embed = discord.Embed(title="Liste des commandes", colour=discord.Colour.dark_red())
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
        embed.description = ""
        for command, infos in commands.items():
            embed.description += "**{}**\n".format(infos[0])
            embed.description += "\t\t{}\n\n".format(infos[1])
    await client.send_message(message.channel, embed=embed)

async def testCommand(client, message):
    embed = discord.Embed(title="Test", description="Hello world !", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    await client.send_message(message.channel, embed=embed)

async def nextCommand(client, message):
    embed = discord.Embed(title="Prochain cours", description="Chargement en cours...", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    msg = await client.send_message(message.channel, embed=embed)

    lessons = getLessons()
    nextLesson = getNextLesson(lessons)
    embed.description = "{}\n".format(nextLesson[1])
    embed.description += "Le {} de {} à {}\n".format(nextLesson[4], nextLesson[5], nextLesson[6])
    embed.description += "Professeur: {}\n".format(nextLesson[3])
    embed.description += "Salle: {}\n".format(nextLesson[2])
    await client.edit_message(msg, embed=embed)

async def dayCommand(client, message):
    embed = discord.Embed(title="", description="Chargement en cours...", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    msg = await client.send_message(message.channel, embed=embed)

    args = message.content.split(" ")
    if len(args) >= 2:
        try:
            nextDay = datetime.strptime(args[1], "%d/%m/%Y").date()
        except ValueError:
            embed.description = "Veuillez entrer une date au format JJ/MM/YYYY"
        else:
            lessons = getLessons()
            dayLessons = getDayLessons(lessons, nextDay)

            if len(dayLessons) >= 1:
                embed.title = "Cours du " + nextDay.strftime("%d/%m/%Y")
                embed.description = "**Matin**\n"
                for day, dayLesson in dayLessons:
                    if dayLesson[3] == "13:30":
                        embed.description += "\n**Après-midi**\n"
                    embed.description += "{}\n".format(dayLesson[0])
                    embed.description += "Début: {}\n".format(dayLesson[3])
                    embed.description += "Fin: {}\n".format(dayLesson[4])
                    embed.description += "Professeur: {}\n".format(dayLesson[2])
                    embed.description += "Salle: {}\n".format(dayLesson[1])
            else:
                embed.description = "Aucun cours"
    else:
        lessons = getLessons()
        nextDay = getNextDay(lessons)
        dayLessons = getDayLessons(lessons, nextDay)

        embed.title = "Cours du " + nextDay.strftime("%d/%m/%Y")
        embed.description = "**Matin**\n"
        for day, dayLesson in dayLessons:
            if dayLesson[3] == "13:30":
                embed.description += "\n**Après-midi**\n"
            embed.description += "{}\n".format(dayLesson[0])
            embed.description += "Début: {}\n".format(dayLesson[3])
            embed.description += "Fin: {}\n".format(dayLesson[4])
            embed.description += "Professeur: {}\n".format(dayLesson[2])
            embed.description += "Salle: {}\n".format(dayLesson[1])
    await client.edit_message(msg, embed=embed)

async def menuCommand(client, message):
    embed = discord.Embed(title="Menu de la semaine", description="Chargement en cours...", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    msg = await client.send_message(message.channel, embed=embed)

    themes = list(["Entrées chaudes et froides", "Dessert", "Pâtes/Pizza", "Plat du jour", "Rôtisserie/Grillade", "Plat du monde"])

    html = urlopen("http://www.crous-strasbourg.fr/restaurant/resto-u-illkirch/").read()
    soup = BeautifulSoup.BeautifulSoup(html, "html.parser")

    week = soup.find("div", attrs={"id": u"menu-repas"}).ul
    days = week.find_all("li", recursive=False)

    args = message.content.split(" ")
    if len(args) >= 2:
        try:
            day = int(args[1]) - 1
            assert day > -1
            assert day < len(days)
        except (ValueError, Exception, AssertionError):
            embed.description = ""
            for i in range(len(days)):
                embed.description += "{}. {}\n".format(i+1, days[i].h3.text)
        else:
            repas = days[day].div.find_all("div", recursive=False)[1].div.div
            plats = repas.find_all("ul")

            embed.description = ""
            for i in range(0, 6):
                embed.description += "**" + themes[i] + "**\n"
                for plat in plats[i].find_all("li"):
                    if plat.string != None:
                        embed.description += plat.string[0].upper() + plat.string[1:].lower() + "\n"
                embed.description += "\n"
            embed.title = days[day].h3.text
    else:
        embed.description = ""
        for i in range(len(days)):
            embed.description += "{}. {}\n".format(i+1, days[i].h3.text)
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
    embed = discord.Embed(title="Appelez les hendeks !!", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/358718175636094976/393357739805376524/209cml.jpg")
    await client.send_message(message.channel, embed=embed)

async def chehCommand(client, message):
    embed = discord.Embed(title="Cheh !!", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_image(url="http://m.memegen.com/9whbay.jpg")
    await client.send_message(message.channel, embed=embed)

async def gogoleCommand(client, message):
    embed = discord.Embed(title="Alerte au gogole !!", colour=discord.Colour.dark_red())
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_image(url="https://cdn.discordapp.com/attachments/395330641283252224/402802078210195456/hqdefault.png")
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
        if message.content.startswith(".help"):
            await helpCommand(client, message)
        elif message.content.startswith(".test"):
            await testCommand(client, message)
        elif message.content.startswith(".next"):
            await nextCommand(client, message)
        elif message.content.startswith(".day"):
            await dayCommand(client, message)
        elif message.content.startswith(".menu"):
            await menuCommand(client, message)
        elif message.content.startswith(".wtf"):
            await wtfCommand(client, message)
        elif message.content.startswith(".fuck"):
            await fuckCommand(client, message)
        elif message.content.startswith(".hendek"):
            await hendekCommand(client, message)
        elif message.content.startswith(".cheh"):
            await chehCommand(client, message)
        elif message.content.startswith(".gogole"):
            await gogoleCommand(client, message)

    with open("/root/Bot/token.txt") as file:
        client.run(file.read())