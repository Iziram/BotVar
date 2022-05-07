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
from threading import Thread
from time import sleep
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

def embedGenerator(title:str, 
    message:str,
    auteur:dis.user = None, 
    color:int = 0xde64d4) -> dis.embeds:
    """!
    @brief Cette fonction génère des embed discord

    Paramètres : 
        @param title : str => Titre du embed
        @param message : str => Message du embed
        @param auteur : dis.user = None => l'auteur
        @param color : int = 0xde64d4 => la couleur
    Retour de la fonction : 
        @return dis.embeds => l'embed

    """

    embed : dis.embeds = dis.Embed(
        title = title,
        description = message,
        color = color
    )
    if(auteur != None):
        embed.set_author(
            name=auteur.name,
            icon_url=auteur.avatar_url
        )
    return embed

def playerSaver(_):
    while True:
        sleep(60)
        if(os.path.exists('./save.json')):
            os.remove('./save.json')
        with open("./save.json", 'w') as f:
            dump([p.toJson() for p in Player.players.values()], f)

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
    if(full_command[0] != "!b" or len(full_command) < 2 or isinstance(message.channel, dis.DMChannel)):
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
                
                await message.author.send(f"Utilise : {legend}")

            #Si c'est list alors on affiche la liste des legends qu'il reste
            elif full_command[2] == "list":
                legend = []
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                legend = player.rest()
                
                await message.author.send(embed=embedGenerator(
                        "Succès",
                        f"Tu n'as pas encore utilisé les legendes suivantes: {legend}({len(player.legends)})",
                        auteur=author,
                        color=0x54c759
                ))
            
            #Si c'est weapon alors on affiche un challenge aléatoire
            elif full_command[2] == "weapon":
                await message.author.send(embed=embedGenerator(
                        "Succès",
                        f"Arme(s) à utiliser : {Player.weapon()}",
                        auteur=author,
                        color=0x54c759
                ))

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
                
                if(player.isConnected()):
                    await message.author.send(embed=embedGenerator(
                        "Succès",
                        "Votre compte steam a bien été relié.",
                        auteur=author,
                        color=0x54c759
                    ))
                else:
                    await message.author.send(embed=embedGenerator(
                        "Erreur",
                        "Votre compte steam n'a pas pu être relié.",
                        auteur=author,
                        color=0xf04646
                    ))

                await message.delete()

        elif len(full_command) > 2:

            #Dans le cas des statistiques basiques du joueur
            if(full_command[2] == "stats"):
                player : Player or None = None
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                if(player != None and player.isConnected()):
                    with open('./stats.json', 'w') as f:
                        dump(Player.statisticsFormatter(brawlhallaAPI.getPlayerStats(player.brawlhalla_id)), f)
                    await message.author.send(embed=embedGenerator(
                        "Succès",
                        "Voici vos statistiques (ouvrez le fichier avec votre navigateur internet pour avoir une version lisible)",
                        auteur=author,
                        color=0x54c759
                    ), file=dis.File(r'./stats.json'))
                    os.remove("./stats.json")
                else:
                    await message.author.send(embed=embedGenerator(
                        "Erreur",
                        "Votre compte steam n'a pas été relié, vous ne pouvez pas accédez à vos données brawlhalla",
                        auteur=author,
                        color=0xf04646
                    ))

            #Dans le cas des statistiques de Ranked du joueur
            elif(full_command[2] == "ranked"):
                player : Player or None = None
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                if(player != None and player.isConnected()):
                    with open('./ranked.json', 'w') as f:
                        dump(Player.statisticsFormatter(brawlhallaAPI.getPlayerRanked(player.brawlhalla_id), "ranked"), f)
                    await message.author.send(embed=embedGenerator(
                        "Succès",
                        "Voici vos statistiques de ranked (ouvrez le fichier avec votre navigateur internet pour avoir une version lisible)",
                        auteur=author,
                        color=0x54c759
                    ), file=dis.File(r'./ranked.json'))
                    os.remove("./ranked.json")
                else:
                    await message.author.send(embed=embedGenerator(
                        "Erreur",
                        "Votre compte steam n'a pas été relié, vous ne pouvez pas accédez à vos données brawlhalla",
                        auteur=author,
                        color=0xf04646
                    ))
            
            elif (full_command[2] == "clan"):
                if author.id in Player.players:
                    player = Player.get(author.id)
                else:
                    player = Player(author.id)
                if(player != None and player.isConnected()):
                    stats = brawlhallaAPI.getPlayerStats(player.brawlhalla_id)
                    if("clan" in stats.keys()):
                        with open('./clan.json', 'w') as f:
                            dump(brawlhallaAPI.getClan(stats["clan"]["clan_id"]), f)
                        await message.author.send(embed=embedGenerator(
                            "Succès",
                            "Voici les statistiques de votre clan (ouvrez le fichier avec votre navigateur internet pour avoir une version lisible)",
                            auteur=author,
                            color=0x54c759
                        ), file=dis.File(r'./clan.json'))
                        os.remove("./clan.json")
                    else:
                        await message.author.send(embed=embedGenerator(
                            "Erreur",
                            "Vous n'avez pas de clan.",
                            auteur=author,
                            color=0xf04646
                        ))
                    
                else:
                    await message.author.send(embed=embedGenerator(
                        "Erreur",
                        "Votre compte steam n'a pas été relié, vous ne pouvez pas accédez à vos données brawlhalla",
                        auteur=author,
                        color=0xf04646
                    ))
            await message.delete()

    #Si la commande concerne les teams
    elif command == "teams":
        if "jirobot" not in [a.name.lower() for a in author.roles]:
            await message.author.send(embed=embedGenerator(
                "Erreur",
                "Vous n'avez pas la permission d'utiliser cette commande.",
                auteur=author,
                color=0xf04646
            ))
            return
        if len(full_command) > 2:
            #Pour créer une nouvelle partie
            channel = message.channel
            if full_command[2] == "new":
                code : str = ""
                if(len(full_command) > 3):
                    code = "RoomCode : " + full_command[3]
                answer = await channel.send(embed=embedGenerator(
                    "Une nouvelle partie a été lancée",
                    f"Veuillez cliquer sur la réaction pour rejoindre la partie. {code}",
                    author
                ))
                await answer.add_reaction("🕹")
                Team.teamReaction = answer.id


            #Pour lister les participants en attente de la partie
            elif full_command[2] == "list":
                p = Team.participants()
                names = await userIdToNames(p)
                await channel.send(embed=embedGenerator(
                    "Les participants",
                    f"{names}",
                    author
                ))
            #Pour selectionner les équipes aléatoires
            elif full_command[2] == "select":
                Team.selection()
                Rednames = await userIdToNames(Team.teamRed.players)
                BlueNames = await userIdToNames(Team.teamBlue.players)

                await channel.send(embed=embedGenerator(
                    "Les Rouges sont : ",
                    f"{Rednames}",
                    author
                ))
                await channel.send(embed=embedGenerator(
                    "Les Bleus sont : ",
                    f"{BlueNames}",
                    author
                ))

            #Pour remettre à 0 la partie
            elif full_command[2] == "reset":
                Team.init()
                await channel.send(embed=embedGenerator(
                    "La partie a été réinitialisée",
                    "",
                    author
                ))
            await message.delete()
    #Pour afficher la liste de commande et comment les utiliser
    elif command == "help":
        if (len(full_command) < 3):
            commandes = """
            !b help ➡ affiche la liste des commandes
            !b legend ➡ commandes relatives aux legendes
            !b player ➡ commandes relatives aux joueurs 
            !b teams ➡ commandes relatives aux parties

            Pour plus d'informations sur une commande :
            !b help <commande>
            """
            await message.author.send(embed=embedGenerator(
                "Liste des commandes",
                commandes,
                auteur=author,
                color=0x54c759
            ))
        elif (len(full_command) < 4):
            if(full_command[2] == "legend"):
                commandes = """
                !b legend list ➡ Affiche la liste des legendes que vous n'avez pas encore utilisé
                !b legend rdm ➡ Tire aléatoirement une legende
                !b legend weapon ➡ Tire aléatoirement un challenge d'armes (restriction des armes à utiliser)
                """

                await message.author.send(embed=embedGenerator(
                    "Liste des commandes liées aux Legendes",
                    commandes,
                    auteur=author,
                    color=0x54c759
                ))
            elif(full_command[2] == "player"):
                commandes = """
                !b player steam <steam_id> ➡ Lie votre compte discord à votre compte steam
                !b player stats ➡ Affiche vos statistiques brawhalla
                !b player ranked ➡ Affiche vos statistiques ranked brawlhalla
                !b player clan ➡ Affiche des informations sur votre clan brawlhalla
                """

                await message.author.send(embed=embedGenerator(
                    "Liste des commandes liées aux Joueurs",
                    commandes,
                    auteur=author,
                    color=0x54c759
                ))

            elif(full_command[2] == "teams"):
                commandes = """
                *Seuls les membres ayant le role JiroBot pourront utiliser ces commandes*

                !b teams new [Roomcode] ➡ génère une nouvelle partie brawlhalla le roomcode n'est pas obligatoire
                !b teams list ➡ Affiche la liste des participants à la partie
                !b teams select ➡ Selectionne les équipes aléatoirement
                !b teams reset ➡ Réinitialise la partie
                """

                await message.author.send(embed=embedGenerator(
                    "Liste des commandes liées aux Parties",
                    commandes,
                    auteur=author,
                    color=0x54c759
                ))


        await message.delete()
    else:
        await message.author.send(embed=embedGenerator(
            "Erreur",
            f"La commande '{command}' n'existe pas. Faites !b help pour avoir la liste des commandes",
            auteur=author,
            color=0xf04646
        ))
        await message.delete()

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

@client.event
async def on_raw_reaction_remove(payload : dis.raw_models.RawReactionActionEvent):
    """!
    @brief Cette fonction permet au bot de retirer un joueur de la partie lors que celui-ci retire sa réaction

    Paramètres : 
        @param payload : dis.raw_models.RawReactionActionEvent => l'event généré par l'utilisateur

    """
    if payload.message_id == Team.teamReaction:
        Team.teamWaiter.remove(payload.user_id)


thread = Thread(target=playerSaver, args=(1,))
thread.start()
#Au lancement du bot on met à jour la liste statiques des legends
Player.loadFromSave()
Player.legends = brawlhallaAPI.getAllLegends()

#On lance le bot
client.run(token)