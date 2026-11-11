"""! @brief Bot discord pour un serveur communautaire BrawlHalla
 @file discord_bot.py
 @section libs Librairies/Modules
   - discord
   - json
   - os
   - threading

 @section authors Auteur(s)
   - Créé par Matthias HARTMANN le 31/03/2022 .

 Le token discord et la clé d'api brawlhalla sont lus depuis le fichier
 ``apikey.txt`` (2 valeurs séparées par un espace) ou depuis les variables
 d'environnement ``BRAWLHALLA_API_KEY`` et ``DISCORD_TOKEN``.
"""
import os
from json import dump
from threading import Thread
from time import sleep

import discord as dis

from .api import BrawlhallaAPI
from .player import Player
from .stats import format as format_stats
from .teams import Team


def load_tokens(apikey_file: str = "apikey.txt") -> tuple:
    """!
    @brief Charge la clé d'api brawlhalla et le token discord.

    L'ordre de priorité :
      1. variables d'environnement ``BRAWLHALLA_API_KEY`` / ``DISCORD_TOKEN``
      2. fichier ``apikey.txt`` : ``<api_key> <discord_token>``

    @return tuple => (api_key, discord_token)
    """
    api_key = os.environ.get("BRAWLHALLA_API_KEY", "")
    token = os.environ.get("DISCORD_TOKEN", "")
    if not (api_key and token) and os.path.exists(apikey_file):
        with open(apikey_file, "r", encoding="utf-8") as f:
            values = f.readline().split(" ")
            if len(values) >= 2:
                api_key = api_key or values[0].strip()
                token = token or values[1].strip()
    return api_key, token


def player_saver(interval: float = 30.0, path: str = "save.json") -> None:
    """Sauvegarde périodique des joueurs (lancée en thread par ``run``)."""
    from .save import save as _save

    while True:
        sleep(interval)
        try:
            _save(Player.players, path)
        except Exception:
            pass


def embed_generator(
    title: str,
    message: str,
    auteur: dis.User | None = None,
    color: int = 0xDE64D4,
) -> dis.Embed:
    """!
    @brief Génère un embed discord.

    @param title : str => titre de l'embed
    @param message : str => message de l'embed
    @param auteur : dis.user or None => l'auteur
    @param color : int => la couleur
    @return dis.Embed => l'embed
    """
    embed = dis.Embed(title=title, description=message, color=color)
    if auteur is not None:
        embed.set_author(name=auteur.name, icon_url=auteur.avatar_url)
    return embed


async def user_id_to_names(client: dis.Client, users: list) -> str:
    """!
    @brief Convertit une liste d'id discord en liste de noms.

    @param client : dis.Client => le client discord
    @param users : list => liste d'id discord
    @return str => liste de noms discord
    """
    names = ""
    for u in users:
        user = await client.fetch_user(u)
        names += f"- {user.name}\n"
    return names


def make_bot() -> dis.Client:
    """!
    @brief Crée le client discord et lui affecte les handlers d'événements.

    @return dis.Client => le client discord prêt à être lancé
    """
    intents = dis.Intents.default()
    intents.message_content = True
    intents.reactions = True
    client = dis.Client(intents=intents)

    @client.event
    async def on_message(message: dis.Message):
        """Lit les messages discord et y répond en fonction de leur contenu."""
        full_command = [i.lower() for i in message.content.split(" ")]

        # Le message doit commencer par "!b" et avoir au moins 2 mots, hors DM
        if (
            full_command[0] != "!b"
            or len(full_command) < 2
            or isinstance(message.channel, dis.DMChannel)
        ):
            return

        author = message.author
        command = full_command[1]

        if command == "legend":
            await _cmd_legend(client, message, author, full_command)
        elif command == "player":
            await _cmd_player(client, message, author, full_command)
        elif command == "teams":
            await _cmd_teams(client, message, author, full_command)
        elif command == "help":
            await _cmd_help(client, message, author, full_command)
        else:
            await message.author.send(
                embed=embed_generator(
                    "Erreur",
                    f"La commande '{command}' n'existe pas. Faites !b help pour avoir la liste des commandes",
                    auteur=author,
                    color=0xF04646,
                )
            )
            await message.delete()

    @client.event
    async def on_reaction_add(reaction: dis.Reaction, user: dis.User):
        """Ajoute un joueur à la partie en cours quand il réagit."""
        if not user.bot and reaction.message.id == Team.team_reaction:
            Team.team_waiter.add(user.id)

    @client.event
    async def on_raw_reaction_remove(payload: dis.RawReactionActionEvent):
        """Retire un joueur de la partie quand il enlève sa réaction."""
        if payload.message_id == Team.team_reaction:
            Team.team_waiter.remove(payload.user_id)

    return client


async def _get_or_create_player(author) -> Player:
    if author.id in Player.players:
        return Player.get(author.id)
    return Player(author.id)


async def _cmd_legend(client, message, author, full_command):
    if len(full_command) > 2:
        if full_command[2] == "rdm":
            player = await _get_or_create_player(author)
            legend = player.random()
            await message.author.send(f"Utilise : {legend}")
        elif full_command[2] == "list":
            player = await _get_or_create_player(author)
            legend = player.rest()
            await message.author.send(
                embed=embed_generator(
                    "Succès",
                    f"Tu n'as pas encore utilisé les legendes suivantes: {legend}({len(player.legends)})",
                    auteur=author,
                    color=0x54C759,
                )
            )
        elif full_command[2] == "weapon":
            await message.author.send(
                embed=embed_generator(
                    "Succès",
                    f"Arme(s) à utiliser : {Player.weapon()}",
                    auteur=author,
                    color=0x54C759,
                )
            )
        await message.delete()


async def _send_stats_file(client, message, author, data, filename, message_text):
    with open(filename, "w", encoding="utf-8") as f:
        dump(data, f)
    await message.author.send(
        embed=embed_generator("Succès", message_text, auteur=author, color=0x54C759),
        file=dis.File(filename),
    )
    os.remove(filename)


async def _cmd_player(client, message, author, full_command):
    if len(full_command) > 3 and full_command[2] == "steam":
        player = await _get_or_create_player(author)
        player.set_steam_id(full_command[3])
        if player.is_connected():
            await message.author.send(
                embed=embed_generator(
                    "Succès",
                    "Votre compte steam a bien été relié.",
                    auteur=author,
                    color=0x54C759,
                )
            )
        else:
            await message.author.send(
                embed=embed_generator(
                    "Erreur",
                    "Votre compte steam n'a pas pu être relié.",
                    auteur=author,
                    color=0xF04646,
                )
            )
        await message.delete()
        return

    if len(full_command) > 2:
        player = await _get_or_create_player(author)
        if full_command[2] == "stats":
            if player.is_connected():
                data = format_stats(BrawlhallaAPI.get_player_stats(player.brawlhalla_id))
                await _send_stats_file(
                    client,
                    message,
                    author,
                    data,
                    "./stats.json",
                    "Voici vos statistiques (ouvrez le fichier avec votre navigateur "
                    "internet pour avoir une version lisible)",
                )
            else:
                await _no_brawlhalla_error(author)
        elif full_command[2] == "ranked":
            if player.is_connected():
                data = format_stats(
                    BrawlhallaAPI.get_player_ranked(player.brawlhalla_id), "ranked"
                )
                await _send_stats_file(
                    client,
                    message,
                    author,
                    data,
                    "./ranked.json",
                    "Voici vos statistiques de ranked (ouvrez le fichier avec votre "
                    "navigateur internet pour avoir une version lisible)",
                )
            else:
                await _no_brawlhalla_error(author)
        elif full_command[2] == "clan":
            if player.is_connected():
                stats = BrawlhallaAPI.get_player_stats(player.brawlhalla_id)
                if stats is not None and "clan" in stats:
                    data = BrawlhallaAPI.get_clan(stats["clan"]["clan_id"])
                    await _send_stats_file(
                        client,
                        message,
                        author,
                        data,
                        "./clan.json",
                        "Voici les statistiques de votre clan (ouvrez le fichier avec "
                        "votre navigateur internet pour avoir une version lisible)",
                    )
                else:
                    await message.author.send(
                        embed=embed_generator(
                            "Erreur", "Vous n'avez pas de clan.", auteur=author, color=0xF04646
                        )
                    )
            else:
                await _no_brawlhalla_error(author)
        await message.delete()


async def _no_brawlhalla_error(author):
    await author.send(
        embed=embed_generator(
            "Erreur",
            "Votre compte steam n'a pas été relié, vous ne pouvez pas accédez à vos données brawlhalla",
            auteur=author,
            color=0xF04646,
        )
    )


async def _cmd_teams(client, message, author, full_command):
    if "jirobot" not in [a.name.lower() for a in author.roles]:
        await message.author.send(
            embed=embed_generator(
                "Erreur",
                "Vous n'avez pas la permission d'utiliser cette commande.",
                auteur=author,
                color=0xF04646,
            )
        )
        return
    if len(full_command) > 2:
        channel = message.channel
        if full_command[2] == "new":
            code = ""
            if len(full_command) > 3:
                code = "RoomCode : " + full_command[3]
            answer = await channel.send(
                embed=embed_generator(
                    "Une nouvelle partie a été lancée",
                    f"Veuillez cliquer sur la réaction pour rejoindre la partie. {code}",
                    author,
                )
            )
            await answer.add_reaction("🕹")
            Team.team_reaction = answer.id
        elif full_command[2] == "list":
            names = await user_id_to_names(client, Team.participants())
            await channel.send(
                embed=embed_generator("Les participants", names, author)
            )
        elif full_command[2] == "select":
            Team.select()
            red_names = await user_id_to_names(client, Team.team_red.players)
            blue_names = await user_id_to_names(client, Team.team_blue.players)
            await channel.send(
                embed=embed_generator("Les Rouges sont : ", red_names, author)
            )
            await channel.send(
                embed=embed_generator("Les Bleus sont : ", blue_names, author)
            )
        elif full_command[2] == "reset":
            Team.init()
            await channel.send(
                embed=embed_generator("La partie a été réinitialisée", "", author)
            )
        await message.delete()


async def _cmd_help(client, message, author, full_command):
    if len(full_command) < 3:
        commandes = """
        !b help ➡ affiche la liste des commandes
        !b legend ➡ commandes relatives aux legendes
        !b player ➡ commandes relatives aux joueurs
        !b teams ➡ commandes relatives aux parties

        Pour plus d'informations sur une commande :
        !b help <commande>
        """
        title = "Liste des commandes"
    elif len(full_command) < 4 and full_command[2] == "legend":
        commandes = """
        !b legend list ➡ Affiche la liste des legendes que vous n'avez pas encore utilisé
        !b legend rdm ➡ Tire aléatoirement une legende
        !b legend weapon ➡ Tire aléatoirement un challenge d'armes (restriction des armes à utiliser)
        """
        title = "Liste des commandes liées aux Legendes"
    elif len(full_command) < 4 and full_command[2] == "player":
        commandes = """
        !b player steam <steam_id> ➡ Lie votre compte discord à votre compte steam
        !b player stats ➡ Affiche vos statistiques brawhalla
        !b player ranked ➡ Affiche vos statistiques ranked brawlhalla
        !b player clan ➡ Affiche des informations sur votre clan brawlhalla
        """
        title = "Liste des commandes liées aux Joueurs"
    elif len(full_command) < 4 and full_command[2] == "teams":
        commandes = """
        *Seuls les membres ayant le role JiroBot pourront utiliser ces commandes*

        !b teams new [Roomcode] ➡ génère une nouvelle partie brawlhalla le roomcode n'est pas obligatoire
        !b teams list ➡ Affiche la liste des participants à la partie
        !b teams select ➡ Selectionne les équipes aléatoirement
        !b teams reset ➡ Réinitialise la partie
        """
        title = "Liste des commandes liées aux Parties"
    else:
        return
    await message.author.send(
        embed=embed_generator(title, commandes, auteur=author, color=0x54C759)
    )
    await message.delete()


def run(apikey_file: str = "apikey.txt", save_path: str = "save.json") -> None:
    """!
    @brief Lance le bot discord (charge les tokens, la sauvegarde, la liste
    des legends et démarre le client).
    """
    api_key, token = load_tokens(apikey_file)
    BrawlhallaAPI.api_key = api_key
    if not token:
        raise RuntimeError(
            "Token discord manquant : définissez DISCORD_TOKEN ou le fichier apikey.txt"
        )

    Team.init()
    client = make_bot()

    thread = Thread(target=player_saver, args=(30, save_path))
    thread.daemon = True
    thread.start()

    # Au lancement on met à jour la liste statique des legends
    Player.load_from_save(save_path)
    legends = BrawlhallaAPI.get_all_legends()
    if legends:
        Player.legends = legends

    client.run(token)
