"""! @brief [description du fichier]
 @file player.py
 @section libs Librairies/Modules
  - Requests

 @section authors Auteur(s)
  - Créé par Matthias HARTMANN le 31/03/2022 .
"""
from random import randint, shuffle
import readline
import requests
class Player:
    players = {}
    legends : list = [
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
    def __init__(self, name:str):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla
            @param name : str => [description]

        """
        self.legends : list = []
        Player.players[name] = self
        self.name = name;
        self.steam_id = None
        self.brawlhalla_id = None
    def setSteamID(self, steamId:str):
        self.steam_id = steamId;
        self.brawlhalla_id = brawlhallaAPI.getBrawlHallaIDFromSteamID(steamId)
    
    def isConnected(self) -> bool:
        return self.brawlhalla_id != None
    def fournish(self):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla

        """
        if(self.brawlhalla_id == None):
            self.legends : list = Player.legends.copy()
        else:
            self.legends : list = brawlhallaAPI.getLegendOfPlayer(self.brawlhalla_id)

    def random(self):
        if(len(self.legends) == 0): self.fournish()
        i : int = randint(0, len(self.legends)-1)
        return self.legends.pop(i)
    
    def reste(self):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla

        """
        names = "\n"
        for i in range(1, len(self.legends)-1, 2):
            names += f' - {self.legends[i-1]}    {" - " + self.legends[i]}\n'
        if(len(self.legends) % 2 != 0):
            names += f' - {self.legends[-1]}\n'

        return names.replace("_"," ")

    def __str__(self) -> str:
        return f"({self.name})->[steam:{self.steam_id}, brawlhalla:{self.brawlhalla_id}]"
    def __repr__(self) -> str:
        return f"({self.name})->[steam:{self.steam_id}, brawlhalla:{self.brawlhalla_id}]"

    @staticmethod
    def get(name):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param name => [description]

        """
        return Player.players.get(name, None)

    @staticmethod
    def weapon():
        """!
        @brief [Description de la fonction]


        """
        weapons = ["principale", "secondaire", "aucune", "objets", "tous"]
        return weapons[randint(0, len(weapons)-1)]

class Team:
    def __init__(self, color):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla
            @param color => [description]

        """
        self.color = color
        self.players = []
    def add(self, player):
        self.players.append(player)
    def remove(self, player):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla
            @param player => [description]

        """
        if(player in self.players):
            self.players.remove(player)
    def melange(self):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla

        """
        shuffle(self.players)
    def __len__(self):
        """!
        @brief [Description de la fonction]

        Paramètres : 
            @param self => Blabla

        """
        return len(self.players)

    teamReaction = ""
    teamRed = None
    teamBlue = None
    teamWaiter = None

    @staticmethod
    def participants():
        """!
        @brief [Description de la fonction]


        """
        if(len(Team.teamWaiter)>0):
            return Team.teamWaiter.players
        return []
    
    @staticmethod
    def init():
        """!
        @brief [Description de la fonction]


        """
        Team.teamRed = Team("red")
        Team.teamBlue = Team("blue")
        Team.teamWaiter = Team("waiter")
    @staticmethod
    def selection():
        """!
        @brief [Description de la fonction]


        """
        Team.teamWaiter.melange()
        players = Team.teamWaiter.players
        mid = len(players)//2
        red = players[:mid]
        blue = players[mid:]

        Team.teamBlue.players = blue
        Team.teamRed.players = red


class brawlhallaAPI:
    apikey = "";
    @staticmethod
    def useAPIKEY():
        with open('./apikey.txt', 'r') as f:
            brawlhallaAPI.apikey = f.readline();
    @staticmethod
    def getBrawlHallaIDFromSteamID(steamID : str ) -> None or int:
        reponse = requests.get(f"https://api.brawlhalla.com/search?steamid={steamID}&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json()["brawlhalla_id"]
        return None
    @staticmethod
    def getPlayerStats(brawlhalla_id : int) -> dict() or None:
        reponse = requests.get(f"https://api.brawlhalla.com/player/{brawlhalla_id}/stats?&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json()
        return None
    @staticmethod
    def getPlayerRanked(brawlhalla_id : int) -> dict or None:
        reponse = requests.get(f"https://api.brawlhalla.com/player/{brawlhalla_id}/ranked?&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json()
        return None
    @staticmethod
    def getAllLegends() -> list:
        reponse = requests.get(f"https://api.brawlhalla.com/legend/all/&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            json = reponse.json();
            liste = []
            for legend in json:
                liste.append(legend["legend_name_key"])
            return liste
        return None
    @staticmethod
    def getLegendOfPlayer(brawlhalla_id) -> None or list:
        stats = brawlhallaAPI.getPlayerStats(brawlhalla_id)
        if(stats == None):
            return None
        legends = stats["legends"]
        liste = []
        for l in legends:
            liste.append(l["legend_name_key"])
        return liste
    #Faire requetes clan