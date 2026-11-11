"""Modèle : un joueur et ses associations steam / brawlhalla."""
from random import randint

from . import api

#: Liste statique des légends du jeu, actualisée par l'API BrawlHalla
#: au démarrage si une clé est disponible.
LEGENDS: list = [
    "Bödvar",
    "Cassidy",
    "Orion",
    "Lord_Vraxx",
    "Gnash",
    "Queen Nai",
    "Hattori",
    "Sir_Roland",
    "Scarlet",
    "Thatch",
    "Ada",
    "Sentinel",
    "Lucien",
    "Teros",
    "Brynn",
    "Asuri",
    "Barraza",
    "Ember",
    "Azoth",
    "Koji",
    "Ulgrim",
    "Diana",
    "Jhala",
    "Kor",
    "Wu_Shang",
    "Val",
    "Ragnir",
    "Cross",
    "Mirage",
    "Nix",
    "Mordex",
    "Yumiko",
    "Artemis",
    "Caspian",
    "Isaiah",
    "Jiro",
    "Lin_Fei",
    "Zariel",
    "Rayman",
    "Dusk",
    "Fait",
    "Thor",
    "Petra",
    "Vector",
    "Volkov",
    "Onyx",
    "Jaeyun",
    "Mako",
    "Magyar",
    "Reno",
    "Munin",
]

_WEAPONS = ["principale", "secondaire", "aucune", "objets", "tous"]


class Player:
    """Un joueur identifié par son id Discord, lié à un compte steam/brawlhalla.

    Les instances sont référencées dans le dictionnaire de classe :pyattr:`players`
    (clé = id discord) afin de pouvoir retrouver un joueur déjà créé.
    """

    #: Joueur créés (clé = id discord, valeur = objet :class:`Player`).
    players: dict = {}
    #: Légends du jeu (statiques par défaut, actualisées par l'API).
    legends: list = LEGENDS.copy()

    def __init__(self, id_discord: str):
        self.legends: list = []
        if id_discord not in Player.players:
            Player.players[id_discord] = self
        self.name = id_discord
        self.steam_id = None
        self.brawlhalla_id = None

    def set_steam_id(self, steam_id: str) -> None:
        """Lie un id steam au joueur et résout le brawlhalla id associé."""
        self.steam_id = steam_id
        self.brawlhalla_id = api.get_brawlhalla_id_from_steam_id(steam_id)

    def is_connected(self) -> bool:
        """Renvoie ``True`` si le brawlhalla id est renseigné."""
        return self.brawlhalla_id is not None

    def furnish(self) -> None:
        """Remplit la liste de legend du joueur (statique ou via l'API)."""
        if not self.is_connected():
            self.legends = Player.legends.copy()
        else:
            self.legends = api.get_legends_of_player(self.brawlhalla_id)

    def random(self) -> str:
        """Tire aléatoirement une legend de la liste du joueur (sans répéter)."""
        if len(self.legends) == 0:
            self.furnish()
        i = randint(0, len(self.legends) - 1)
        return self.legends.pop(i)

    def rest(self) -> str:
        """Renvoie les legends restantes formatées en 2 colonnes."""
        names = "\n"
        self.legends.sort()
        for i in range(1, len(self.legends) - 1, 2):
            names += f' - {self.legends[i - 1]}    {" - " + self.legends[i]}\n'
        if len(self.legends) % 2 != 0:
            names += f' - {self.legends[-1]}\n'
        return names.replace("_", " ")

    def to_json(self) -> dict:
        """Représentation sérialisable du joueur."""
        return {
            "name": self.name,
            "steam": self.steam_id,
            "brawlhalla": self.brawlhalla_id,
            "legends": self.legends,
        }

    def __str__(self) -> str:
        return (
            f"({self.name})->[steam:{self.steam_id},"
            f" brawlhalla:{self.brawlhalla_id}]"
        )

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_json(json: dict) -> "Player":
        """Restaure un :class:`Player` à partir de son dictionnaire."""
        player = Player(json["name"])
        player.brawlhalla_id = json["brawlhalla"]
        player.steam_id = json["steam"]
        player.legends = json["legends"]
        return player

    @staticmethod
    def load_from_save(path: str = "./save.json") -> None:
        """Charge les joueurs depuis le fichier de sauvegarde."""
        from . import storage

        data = storage.load_save(path)
        if data is None:
            return
        for p in data:
            Player.from_json(p)

    @staticmethod
    def get(name: str):
        """Retrouve un joueur à partir de son id discord, ou ``None``."""
        return Player.players.get(name, None)

    @staticmethod
    def weapon() -> str:
        """Tire aléatoirement un challenge d'armes."""
        return _WEAPONS[randint(0, len(_WEAPONS) - 1)]


def statistics_formatter(stats: dict, type_: str = "stat") -> dict:
    """Formate les statistiques brutes de l'API en structure lisible.

    :param stats: dictionnaire brut retourné par l'API (``stat`` ou ``ranked``).
    :param type_: ``"stat"`` ou ``"ranked"``.
    :return: dictionnaire formatté (``player`` + ``legends``).
    """
    formatted_stats: dict = {"player": {}, "legends": []}

    if type_ == "stat":
        formatted_stats["player"] = {
            "name": stats["name"],
            "level": stats["level"],
            "games": {
                "total": stats["games"],
                "wins": stats["wins"],
            },
        }
        for legend in stats["legends"]:
            formatted_stats["legends"].append(
                {
                    "name": legend["legend_name_key"],
                    "kos": legend["kos"],
                    "games": {
                        "total": legend["games"],
                        "wins": legend["wins"],
                    },
                }
            )
        formatted_stats["legends"].sort(key=lambda x: x["name"])

    elif type_ == "ranked":
        formatted_stats["player"] = {
            "name": stats["name"],
            "rating": {
                "current": stats["rating"],
                "peak": stats["peak_rating"],
                "tier": stats["tier"],
            },
            "games": {
                "total": stats["games"],
                "wins": stats["wins"],
            },
        }
        for legend in stats["legends"]:
            formatted_stats["legends"].append(
                {
                    "name": legend["legend_name_key"],
                    "rating": {
                        "current": legend["rating"],
                        "peak": legend["peak_rating"],
                        "tier": legend["tier"],
                    },
                    "games": {
                        "total": legend["games"],
                        "wins": legend["wins"],
                    },
                }
            )
        formatted_stats["legends"].sort(
            key=lambda x: x["rating"]["peak"], reverse=True
        )

    return formatted_stats
