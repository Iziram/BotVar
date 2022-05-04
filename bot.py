"""! @brief Bot discord pour un serveur communautaire BrawlHalla
 @file bot.py
 @section libs Librairies/Modules
  - discord
  - json
  - os

 @section authors Auteur(s)
  - Créé par Matthias HARTMANN le 31/03/2022 .
"""
import discord as dis
from player import Player, Team, brawlhallaAPI
from json import dump
import os


"""
Gestion de token dans un fichier "apikey.txt"
en premier on trouve la clé de l'api brawlhalla puis un espace et le token du bot discord
"""
token : str = ""
with open('./apikey.txt', 'r') as f:
    tokens : list = f.readline().split(" ")
    print(tokens)
    brawlhallaAPI.api_key = tokens[0];
    token = tokens[1]


#On initialise le client (bot) afin de lui assigner des events
client = dis.Client()

#On initialise la gestion des Teams (afin de pouvoir l'utiliser avec le bot)
Team.init()

async def userIdToNames(users : list) -> list:
    """!
    @brief Cette fonction permet d'obtenir une liste de nom d'utilisateur discord à partir d'une liste d'id

    Paramètres : 
        @param users : list => liste d'id discord
    Retour de la fonction : 
        @return list => liste de nom discord

    """
    names = ""
    for u in users:
        user = await client.fetch_user(u)
        names += "- "+user.name + "\n"
    return names

@client.event
async def on_message(message : dis.Message):
    """!
    @brief Cette fonction permet au bot de lire les messages discord sur un channel et d'y répondre en fonction de leur contenu

    Paramètres : 
        @param message : dis.Message => l'objet message associé au message qui a provoqué l'event

    """

    #On récupère le contenu du message qu'on transforme en liste de str (lowercase) pour pouvoir traiter si le message est une commande ou non
    full_command = [i.lower() for i in message.content.split(" ")]

    #On vérifie si le message commence par "!b"  et qu'il possède au moins deux mots sinon on ne traite pas le message.
    if(full_command[0] != "!b" or len(full_command) < 2):
        return
    
    #On récuppère l'auteur du message
    author = message.author

    #On détermine la command c'est à dire le premier mot après "!b"
    command = full_command[1]

    #On prépare une variable player qui sera utilisé dans la fonction
    player : Player or None = None

    #Le cas ou la commande concerne les legends du joueurs (obtenir une legend aléatoire, obtenir un challenge, connaitre la liste des legends restantes)
    if command == "legend":
        if len(full_command) > 2:
            #On regarde le paramètre de la commande legend

            #Si c'est rdm alors on tire aléatoirement une legend dans la liste du joueur
            if full_command[2] == "rdm":
                legend = "Bödvar"
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                legend = player.random()
                
                await message.channel.send(f"Utilise : {legend}")

            #Si c'est list alors on affiche la liste des legends qu'il reste
            elif full_command[2] == "list":
                legend = []
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                legend = player.rest()
                
                await message.channel.send(f"Tu n'as pas encore utilisé les legendes suivantes: {legend}({len(player.legends)})")
            
            #Si c'est weapon alors on affiche un challenge aléatoire
            elif full_command[2] == "weapon":
                author = message.author
                await message.channel.send(f"Arme(s) à utiliser : {Player.weapon()}")

            await message.delete()
    #Le cas où la commande concerne le joueur et ses statistiques 
    elif command == "player":
        if len(full_command) > 3:
            #Si le paramètre est steam alors on essaye de lier l'id steam entré en paramètre avec l'objet joueur
            if(full_command[2] == "steam"):
                author = message.author
                if author.id in Player.players:
                    player : Player = Player.get(author.id)
                else:
                    player = Player(author.id)
                player.setSteamID(full_command[3])
                
                if(player.brawlhalla_id != None):
                    await message.channel.send(f"Votre compte steam a bien été lié.")
                else:
                    await message.channel.send(f"Votre compte steam n'a pas pu être lié.")

                await message.delete()

        elif len(full_command) > 2:

            """
            TODO:
                Afficher les statistiques d'une autre façon
                Envoyer les statistiques en message privé
            """

            #Dans le cas des statistiques basiques du joueur
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

            #Dans le cas des statistiques de Ranked du joueur
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
        

    #Si la commande concerne les teams
    elif command == "teams":
        if len(full_command) > 2:
            #Pour créer une nouvelle partie
            if full_command[2] == "new":
                channel = message.channel
                answer = await channel.send(f'Veuillez cliquer sur la reaction pour participer.')
                await answer.add_reaction("🕹")
                Team.teamReaction = answer.id
            #Pour lister les participants en attente de la partie
            elif full_command[2] == "list":
                p = Team.participants()
                names = await userIdToNames(p)
                await message.channel.send(f"Les participants sont: \n{names}")
            #Pour selectionner les équipes aléatoires
            elif full_command[2] == "select":
                Team.selection()
                Rednames = await userIdToNames(Team.teamRed.players)
                await message.channel.send(f"Les Rouges sont: \n{Rednames}")

                BlueNames = await userIdToNames(Team.teamBlue.players)
                await message.channel.send(f"Les Bleus sont: \n{BlueNames}")
            #Pour remettre à 0 la partie
            elif full_command[2] == "reset":
                Team.init()
                await message.channel.send(f"La préparation des teams a été réinitialisée.")
            await message.delete()
    #Pour afficher la liste de commande et comment les utiliser
    elif command == "help":
        """
        TODO:
            Afficher la liste des commandes
            Afficher l'utilisation des commandes
        """
        pass

@client.event
async def on_reaction_add(reaction: dis.reaction, user:dis.user):
    """!
    @brief Cette fonction permet au bot d'ajouter un joueur à la partie en cours 

    Paramètres : 
        @param reaction : dis.reaction => La réaction ajouté par l'utilisateur discord
        @param user : dis.user => l'utilisateur discord

    """
    if not user.bot and reaction.message.id == Team.teamReaction:
        Team.teamWaiter.add(user.id)
        await reaction.message.channel.send(f'{user.name} a rejoint la partie.')

@client.event
async def on_raw_reaction_remove(payload : dis.raw_models.RawReactionActionEvent):
    """!
    @brief Cette fonction permet au bot de retirer un joueur de la partie lors que celui-ci retire sa réaction

    Paramètres : 
        @param payload : dis.raw_models.RawReactionActionEvent => l'event généré par l'utilisateur

    """
    if payload.message_id == Team.teamReaction:
        Team.teamWaiter.remove(payload.user_id)
        user = await client.fetch_user(payload.user_id)
        await client.get_channel(payload.channel_id).send(f'{user.name} a quitté la partie.')

#Au lancement du bot on met à jour la liste statiques des legends
Player.legends = brawlhallaAPI.getAllLegends()

#On lance le bot
client.run(token)