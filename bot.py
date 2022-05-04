"""! @brief [description du fichier]
 @file bot.py
 @section libs Librairies/Modules
  - [Nom du module] (lien)

 @section authors Auteur(s)
  - Créé par Matthias HARTMANN le 31/03/2022 .
"""
import discord as dis
from player import Player, Team, brawlhallaAPI
from json import dump
import os

token : str = ""
with open('./apikey.txt', 'r') as f:
    tokens : list = f.readline().split(" ")
    brawlhallaAPI.apikey = tokens[0];
    token = tokens[1]



client = dis.Client()
Team.init()
async def userIdToNames(users):
    names = ""
    for u in users:
        user = await client.fetch_user(u)
        names += "- "+user.name + "\n"
    return names

@client.event
async def on_message(message):
    full_command = [i.lower() for i in message.content.split(" ")]
    if(len(full_command) < 2 or full_command[0] != "!b"):
        return
    author = message.author
    command = full_command[1]
    if command == "legend":
        if len(full_command) > 2:
            if full_command[2] == "rdm":
                legend = "Bödvar"
                if author.id in Player.players:
                    player = Player.get(author.id)
                    legend = player.random()
                else:
                    player = Player(author.id)
                    legend = player.random()
                
                await message.channel.send(f"Utilise : {legend}")
            elif full_command[2] == "list":
                legend = []
                if author.id in Player.players:
                    player = Player.get(author.id)
                    legend = player.reste()
                else:
                    player = Player(author.id)
                    legend = player.reste()
                
                await message.channel.send(f"Tu n'as pas encore utilisé les legendes suivantes: {legend}({len(player.legends)})")
            elif full_command[2] == "weapon":
                author = message.author
                await message.channel.send(f"Arme(s) à utiliser : {Player.weapon()}")
    elif command == "player":
        if len(full_command) > 3:
            if(full_command[2] == "steam"):
                author = message.author
                if author.id in Player.players:
                    player : Player = Player.get(author.id)
                    player.setSteamID(full_command[3])
                else:
                    player = Player(author.id)
                    player.setSteamID(full_command[3])
                
                if(player.brawlhalla_id != None):
                    await message.channel.send(f"Votre compte steam a bien été lié.")
                else:
                    await message.channel.send(f"Votre compte steam n'a pas pu être lié.")

                await message.delete()

        elif len(full_command) > 2:

            #Afficher les stats en plus joli et envoyer en MP 
            if(full_command[2] == "stats"):
                player : Player or None = None
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                if(player != None and player.isConnected()):
                    with open('./stats.json', 'w') as f:
                        dump(brawlhallaAPI.getPlayerStats(player.brawlhalla_id), f)
                    await message.channel.send("Voici vos statistiques", file=dis.File(r'./stats.json'))
                    os.remove("./stats.json")
                else:
                    await message.channel.send("Votre compte steam n'a pas été relié. Vous ne pouvez donc pas obtenir vos statistiques")

            if(full_command[2] == "ranked"):
                player : Player or None = None
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                if(player != None and player.isConnected()):
                    with open('./ranked.json', 'w') as f:
                        dump(brawlhallaAPI.getPlayerRanked(player.brawlhalla_id), f)
                    await message.channel.send("Voici vos statistiques", file=dis.File(r'./ranked.json'))
                    os.remove("./ranked.json")
                else:
                    await message.channel.send("Votre compte steam n'a pas été relié. Vous ne pouvez donc pas obtenir vos statistiques")
        


    elif command == "teams":
        if len(full_command) > 2:
            if full_command[2] == "new":
                channel = message.channel
                answer = await channel.send(f'Veuillez cliquer sur la reaction pour participer.')
                await answer.add_reaction("🕹")
                Team.teamReaction = answer.id
            elif full_command[2] == "list":
                p = Team.participants()
                names = await userIdToNames(p)
                await message.channel.send(f"Les participants sont: \n{names}")
            elif full_command[2] == "select":
                Team.selection()
                Rednames = await userIdToNames(Team.teamRed.players)
                await message.channel.send(f"Les Rouges sont: \n{Rednames}")

                BlueNames = await userIdToNames(Team.teamBlue.players)
                await message.channel.send(f"Les Bleus sont: \n{BlueNames}")
            elif full_command[2] == "reset":
                Team.init()
                await message.channel.send(f"La préparation des teams a été réinitialisée.")
            await message.delete()

    #Faire Affichage statistiques de clan (total + nom/xp/rank par personne)
    elif command == "help":
        #Envoyer message avec toutes les commandes
        pass

@client.event
async def on_reaction_add(reaction, user):
    if not user.bot and reaction.message.id == Team.teamReaction:
        Team.teamWaiter.add(user.id)
        await reaction.message.channel.send(f'{user.name} a rejoint la partie.')

@client.event
async def on_raw_reaction_remove(payload):
    if payload.message_id == Team.teamReaction:
        Team.teamWaiter.remove(payload.user_id)
        user = await client.fetch_user(payload.user_id)
        await client.get_channel(payload.channel_id).send(f'{user.name} a quitté la partie.')

Player.legends = brawlhallaAPI.getAllLegends()
client.run(token)