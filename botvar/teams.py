"""! @brief Gestion des équipes (rouge, bleue, attente) pour le tirage au sort
 @file teams.py
 @section libs Librairies/Modules
   - random
"""
from random import shuffle


class Team:
    # L'id de la réaction discord utilisée pour rejoindre la liste d'attente
    team_reaction: str = ""

    # Équipes statiques (initialisées par ``init``)
    team_red: "Team | None" = None
    team_blue: "Team | None" = None
    team_waiter: "Team | None" = None

    def __init__(self, color: str):
        """!
        @brief Constructeur de l'équipe.

        @param color : str => couleur de l'équipe (red, blue ou waiter)
        """
        self.color = color
        self.players: list = []

    def add(self, player) -> None:
        """!
        @brief Ajoute un joueur dans l'équipe.

        @param player => un objet joueur (id discord)
        """
        self.players.append(player)

    def remove(self, player) -> None:
        """!
        @brief Retire un joueur de l'équipe.

        @param player => un objet joueur
        """
        if player in self.players:
            self.players.remove(player)

    def shuffle(self) -> None:
        """!
        @brief Mélange les joueurs dans l'équipe (utilisé avant la sélection).
        """
        shuffle(self.players)

    def __len__(self) -> int:
        """!
        @brief Taille de l'équipe.

        @return int => le nombre de joueurs
        """
        return len(self.players)

    @staticmethod
    def participants() -> list:
        """!
        @brief Renvoie les joueurs en attente de rejoindre une partie.

        @return list => liste des joueurs en attente
        """
        if len(Team.team_waiter) > 0:
            return Team.team_waiter.players
        return []

    @staticmethod
    def init() -> None:
        """!
        @brief (Ré)initialise les 3 équipes (rouge, bleue, attente).
        """
        Team.team_red = Team("red")
        Team.team_blue = Team("blue")
        Team.team_waiter = Team("waiter")
        Team.team_reaction = ""

    @staticmethod
    def select() -> tuple:
        """!
        @brief Répartit aléatoirement les joueurs en attente entre les équipes rouge et bleue.

        @return tuple => (joueurs rouges, joueurs bleus)
        """
        Team.team_waiter.shuffle()
        players = Team.team_waiter.players
        mid = len(players) // 2
        red = players[:mid]
        blue = players[mid:]
        Team.team_blue.players = blue
        Team.team_red.players = red
        return red, blue

    # Compatibilité avec l'ancienne API
    selection = select
