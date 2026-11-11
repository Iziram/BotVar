"""! @brief Gestion des joueurs (lien discord/steam/brawlhalla, tirage de legends)
 @file player.py
 @section libs Librairies/Modules
   - random
   - botvar.api
   - botvar.legends
   - botvar.save

 @section authors Auteur(s)
   - Créé par Matthias HARTMANN le 31/03/2022 .
"""
from random import randint

from .api import BrawlhallaAPI
from .legends import LEGENDS
from .save import load, save


class Player:
    # Dictionnaire des joueurs connus (clé = id discord, valeur = objet Player)
    players: dict = {}
    # Liste statique des légends du jeu, actualisée par l'api Brawlhalla
    legends: list = LEGENDS.copy()

    def __init__(self, id_discord: str):
        """!
        @brief Constructeur de l'objet Joueur.

        @param id_discord : str => l'id discord qui sera associé à l'objet
        """
        # Liste de legends du joueur, vide au départ (remplie par ``fournish``)
        self.legends: list = []
        # L'objet rejoint la liste statique de la classe
        if id_discord not in Player.players:
            Player.players[id_discord] = self
        self.name = id_discord
        self.steam_id = None
        self.brawlhalla_id = None

    def set_steam_id(self, steam_id: str) -> None:
        """!
        @brief Ligne un id steam à l'objet joueur et tente de récupérer le brawlhalla_id.

        @param steam_id : str => l'id steam donné par le joueur
        """
        self.steam_id = steam_id
        self.brawlhalla_id = BrawlhallaAPI.get_brawlhalla_id_from_steam_id(steam_id)

    # Compatibilité avec l'ancienne API
    setSteamID = set_steam_id

    def is_connected(self) -> bool:
        """!
        @brief Vrai si le brawlhalla_id est renseigné.

        @return bool => True si le compte brawlhalla est relié
        """
        return self.brawlhalla_id is not None

    # Compatibilité avec l'ancienne API
    isConnected = is_connected

    def fournish(self) -> None:
        """!
        @brief Remplit la liste de legend du joueur
        (liste statique si déconnecté, api sinon).
        """
        if not self.is_connected():
            self.legends = Player.legends.copy()
        else:
            self.legends = BrawlhallaAPI.get_legend_of_player(self.brawlhalla_id)

    def random(self) -> str:
        """!
        @brief Tire aléatoirement une legend dans la liste du joueur (sans
        la rejouer tant que la liste n'est pas vide).

        @return str => le nom d'une legend
        """
        if len(self.legends) == 0:
            self.fournish()
        i = randint(0, len(self.legends) - 1)
        return self.legends.pop(i)

    def rest(self) -> str:
        """!
        @brief Renvoie la liste de legend restant, mise en forme en 2 colonnes.

        @return str => la liste sous forme de 2 colonnes
        """
        names = "\n"
        self.legends.sort()
        for i in range(1, len(self.legends) - 1, 2):
            names += f' - {self.legends[i - 1]}    {" - " + self.legends[i]}\n'
        if len(self.legends) % 2 != 0:
            names += f' - {self.legends[-1]}\n'
        return names.replace("_", " ")

    def to_json(self) -> dict:
        """!
        @brief Représentation sérialisable du joueur (utilisée pour la sauvegarde).

        @return dict => le json du joueur
        """
        return {
            "name": self.name,
            "steam": self.steam_id,
            "brawlhalla": self.brawlhalla_id,
            "legends": self.legends,
        }

    # Compatibilité avec l'ancienne API
    toJson = to_json

    def __str__(self) -> str:
        """Représentation lisible de l'objet (DEBUG ONLY)."""
        return f"({self.name})->[steam:{self.steam_id}, brawlhalla:{self.brawlhalla_id}]"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_json(data: dict) -> "Player":
        """!
        @brief Reconstruit un objet Player depuis son json.

        @param data : dict => json du joueur
        @return Player => l'objet joueur reconstruit
        """
        player = Player(data["name"])
        player.brawlhalla_id = data["brawlhalla"]
        player.steam_id = data["steam"]
        player.legends = data["legends"]
        return player

    # Compatibilité avec l'ancienne API
    fromJson = from_json

    @classmethod
    def load_from_save(cls, path: str = "save.json") -> None:
        """!
        @brief Charge les joueurs sauvegardés dans ``players``.

        @param path : str => chemin du fichier de sauvegarde
        """
        for data in load(path):
            cls.from_json(data)

    # Compatibilité avec l'ancienne API
    loadFromSave = load_from_save

    @staticmethod
    def get(name: str) -> "Player | None":
        """!
        @brief Récupère un joueur à partir de son id discord.

        @param name : str => id_discord
        @return Player or None => l'objet joueur associé ou None
        """
        return Player.players.get(name, None)

    @staticmethod
    def weapon() -> str:
        """!
        @brief Tire aléatoirement un challenge d'armes.

        @return str => le type d'arme autorisée
        """
        weapons = ["principale", "secondaire", "aucune", "objets", "tous"]
        return weapons[randint(0, len(weapons) - 1)]

    @staticmethod
    def reset() -> None:
        """Vide la liste statique des joueurs (utile entre les sessions)."""
        Player.players = {}
        Player.legends = LEGENDS.copy()

    # Sauvegarde / chargement du dictionnaire courant
    @staticmethod
    def save_all(path: str = "save.json") -> None:
        save(Player.players, path)
