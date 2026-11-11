"""Bot Discord : l'interface Discord de BotVar.

La logique des commandes vit dans :mod:`botvar.actions` ; ici on ne fait que
brancher chaque commande Discord sur l'action correspondante et afficher le
résultat sous forme d'embed.
"""
import os
from json import dump
from threading import Thread
from time import sleep

import discord
from discord.ext import commands

from . import actions, config, render
from .player import Player
from .team import Team

COLOR_OK = 0x54C759
COLOR_ERR = 0xF04646
COLOR_DEFAULT = 0xDE64D4


def embed_generator(
    title: str,
    message: str,
    auteur=None,
    color: int = COLOR_DEFAULT,
) -> discord.Embed:
    """Génère un embed Discord."""
    embed = discord.Embed(title=title, description=message, color=color)
    if auteur is not None:
        embed.set_author(name=auteur.name, icon_url=auteur.avatar_url)
    return embed


class BotVar(commands.Bot):
    """Le bot Discord (hérite de :class:`discord.ext.commands.Bot`)."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="!b ",
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        self.add_view(ReactionTeamsView())

    async def on_ready(self) -> None:
        Team.init()
        Player.load_from_save()
        legends = config.load_api_key()
        config.init_api(legends)


class ReactionTeamsView(discord.ui.View):
    """Gère les réactions 🕹 pour rejoindre / quitter la file d'attente."""

    @discord.ui.button(label="🕹", custom_id="botvar_join")
    async def join(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not interaction.user.bot:
            Team.teamWaiter.add(interaction.user.id)


class BotVarBot(BotVar):
    """Sous-classe qui enregistre les commandes au démarrage."""

    async def setup_hook(self) -> None:
        await super().setup_hook()
        self.tree.add_command(*self.get_all_commands())


def _send_result(message, result: dict) -> None:
    """Envvoie le résultat d'une action en embed au destinataire."""
    title = "Succès" if result.get("status") == "success" else "Erreur"
    color = COLOR_OK if result.get("status") == "success" else COLOR_ERR
    text = render.render(result)
    embed = embed_generator(title, text, auteur=message.author, color=color)

    # Les résultats avec données (stats / ranked / clan) sont aussi livrés en JSON.
    if "data" in result:
        filename = result.get("filename", "output.json")
        with open(filename, "w") as f:
            dump(result["data"], f)
        message.author.send(
            embed=embed, file=discord.File(filename)
        )
        os.remove(filename)
        return

    message.author.send(embed=embed)


def build_cogs(bot: BotVarBot) -> None:
    """Déclare les commandes Discord sur ``bot``."""

    @bot.command(name="legend")
    async def legend(ctx: commands.Context, sub: str):
        if sub == "rdm":
            result = actions.legend_rdm(ctx.author.id)
        elif sub == "list":
            result = actions.legend_list(ctx.author.id)
        elif sub == "weapon":
            result = actions.legend_weapon()
        else:
            result = {"status": "error", "message": "Utilisez !b help legend."}
        _send_result(ctx.message, result)
        await ctx.message.delete()

    @bot.command(name="player")
    async def player_cmd(ctx: commands.Context, sub: str, value: str = None):
        if sub == "steam" and value is not None:
            result = actions.player_steam(ctx.author.id, value)
        elif sub == "stats":
            result = actions.player_stats(ctx.author.id)
        elif sub == "ranked":
            result = actions.player_ranked(ctx.author.id)
        elif sub == "clan":
            result = actions.player_clan(ctx.author.id)
        else:
            result = {"status": "error", "message": "Utilisez !b help player."}
        _send_result(ctx.message, result)
        await ctx.message.delete()

    @bot.command(name="teams")
    async def teams(ctx: commands.Context, sub: str, room_code: str = None):
        has_role = "jirobot" in [r.name.lower() for r in ctx.author.roles]
        if not has_role:
            _send_result(
                ctx.message,
                {
                    "status": "error",
                    "message": "Vous n'avez pas la permission d'utiliser cette commande.",
                },
            )
            return
        if sub == "new":
            result = actions.teams_new(room_code)
            await ctx.channel.send(
                embed=embed_generator(
                    "Une nouvelle partie a été lancée",
                    "Veuillez cliquer sur la réaction pour rejoindre la partie."
                    + (f" {result['text'].split('. ', 1)[1]}" if room_code else ""),
                    ctx.author,
                )
            )
        elif sub == "list":
            result = actions.teams_list()
            await ctx.channel.send(
                embed=embed_generator("Les participants", render.render(result), ctx.author)
            )
        elif sub == "select":
            result = actions.teams_select()
            await ctx.channel.send(
                embed=embed_generator(
                    "Les Rouges sont : ",
                    ", ".join(str(p) for p in result["red"]) or "-",
                    ctx.author,
                )
            )
            await ctx.channel.send(
                embed=embed_generator(
                    "Les Bleus sont : ",
                    ", ".join(str(p) for p in result["blue"]) or "-",
                    ctx.author,
                )
            )
        elif sub == "reset":
            result = actions.teams_reset()
            await ctx.channel.send(
                embed=embed_generator(
                    "La partie a été réinitialisée", "", ctx.author
                )
            )
        else:
            _send_result(ctx.message, {"status": "error", "message": "Utilisez !b help teams."})
        await ctx.message.delete()

    @bot.command(name="help")
    async def help_cmd(ctx: commands.Context, topic: str = None):
        result = actions.help(topic)
        title = (
            "Liste des commandes"
            if result.get("status") == "success"
            else "Erreur"
        )
        color = (
            COLOR_OK if result.get("status") == "success" else COLOR_ERR
        )
        text = result.get("text") or result.get("message")
        await ctx.author.send(
            embed=embed_generator(title, text, auteur=ctx.author, color=color)
        )
        await ctx.message.delete()


def _player_saver() -> None:
    """Sauvegarde périodique des joueurs (toutes les 30 s)."""
    from . import storage

    while True:
        sleep(30)
        storage.save_players(Player.players.values())


def run() -> None:
    """Point d'entrée du bot Discord."""
    token = config.load_discord_token()
    if not token:
        raise SystemExit(
            "Token Discord introuvable. Décrivez-le via DISCORD_TOKEN ou apikey.txt."
        )
    bot = BotVarBot()
    build_cogs(bot)
    thread = Thread(target=_player_saver, args=(1,))
    thread.start()
    bot.run(token)
