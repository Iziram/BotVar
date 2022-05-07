"""! @brief Librairie personnelle qui a pour but de faciliter la gestion des joueurs et l'utilisation de l'api brawlhalla
 @file player.py
 @section libs Librairies/Modules
  - Requests
  - Random

 @section authors Auteur(s)
  - Créé par Matthias HARTMANN le 31/03/2022 .
"""
from random import randint, shuffle
from json import load
import os
import requests
class Player:
    #Dictionnaire qui contiendra les joueurs connectés (clé = id discord, valeur = objet Player)
    players = {}
    #Liste statique des légends du jeu, cette liste est actualisée par l'api brawlhalla
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

    def __init__(self, id_discord:str):
        """!
        @brief Constructeur de l'objet Joueur

        Paramètres : 
            @param self => variable représentant l'objet
            @param id_discord : str => l'id discord qui sera associé à l'objet

        """
        #On initialise la liste de legend du joueur avec une liste vide, cela forcement 
        #la réatribution d'une nouvelle liste avec l'api(si connecté) avec la liste statique sinon
        self.legends : list = []

        #On ajoute l'objet dans la liste statique de la class
        if(id_discord not in Player.players):
            Player.players[id_discord] = self

        """
        On créé des variables d'instance :
        name représente l'id discord du joueur
        steam_id représent l'id steam du joueur, initialisé à None par défaut
        brawlhalla_id représent l'id brawlhalla du joueur, initialisé à None par défaut
        """
        self.name = id_discord;
        self.steam_id = None
        self.brawlhalla_id = None
    
    def setSteamID(self, steamId:str):
        """!
        @brief Cette fonction permet de lié un id steam à l'objet joueur. On essaye aussi de recuppérer et lier le brawlhalla_id

        Paramètres : 
            @param self => variable représentant l'objet
            @param steamId : str => l'id steam donné par le joueur au bot

        """
        self.steam_id = steamId;
        #On appelle l'api brawlhalla pour tenter d'obtenir le brawlhalla_id
        self.brawlhalla_id = brawlhallaAPI.getBrawlHallaIDFromSteamID(steamId)
    
    def isConnected(self) -> bool:
        """!
        @brief Cette fonction permet de savoir si la liaison avec le brawlhalla est correcte

        Paramètres : 
            @param self => variable représentant l'objet
        Retour de la fonction : 
            @return bool => Renvoie vrai si le brawlhalla_id est correct Faux sinon

        """
        return self.brawlhalla_id != None
        
    def fournish(self):
        """!
        @brief Cette fonction à pour but de remplir la liste de legend du joueur

        Paramètres : 
            @param self => variable représentant l'objet

        """
        #Si le joueur n'est pas connecté on utilise la liste statique, sinon on utilise l'api pour obtenir la liste de legend du joueur
        if(not self.isConnected()):
            self.legends : list = Player.legends.copy()
        else:
            self.legends : list = brawlhallaAPI.getLegendOfPlayer(self.brawlhalla_id)

    def random(self) -> str:
        """!
        @brief Cette fonction permet de tirer aléatoirement une legend dans la liste de legend du joueur

        Paramètres : 
            @param self => variable représentant l'objet
        Retour de la fonction : 
            @return str => le nom d'une legend

        """
        #On vérifie si la liste est vide, si c'est le cas on la remplie à nouveau.
        #Cela permet de ne pas tirer plusieurs fois d'affilé la même legend
        if(len(self.legends) == 0): self.fournish()
        i : int = randint(0, len(self.legends)-1)
        return self.legends.pop(i)
    
    def rest(self) -> str:
        """!
        @brief Cette fonction renvoie la liste de legend sous forme de 2 colonnes.
        TODO:
            Changer l'affichage 

        Paramètres : 
            @param self => variable représentant l'objet
        Retour de la fonction : 
            @return str => La liste sous forme de 2 colonne (une seule chaine de caractère)

        """
        names = "\n"
        #On trie la liste de legend de façon à l'avoir par ordre alphabétique
        self.legends.sort()

        #On recuppère les legends deux à deux et on les mets en forme
        for i in range(1, len(self.legends)-1, 2):
            names += f' - {self.legends[i-1]}    {" - " + self.legends[i]}\n'
        #Dans le cas ou la liste est impaire
        if(len(self.legends) % 2 != 0):
            names += f' - {self.legends[-1]}\n'

        return names.replace("_"," ")

    def toJson(self)-> dict:
        return {
            "name" : self.name,
            "steam" : self.steam_id,
            "brawlhalla" : self.brawlhalla_id,
            "legends" : self.legends
        }
    

    def __str__(self) -> str:
        """!
        @brief Gestion de l'affichage de l'objet dans un print DEBUG ONLY

        Paramètres : 
            @param self => variable représentant l'objet
        Retour de la fonction : 
            @return str => la représentation de l'objet

        """
        return f"({self.name})->[steam:{self.steam_id}, brawlhalla:{self.brawlhalla_id}]"
    def __repr__(self) -> str:
        """!
        @brief Gestion de l'affichage de l'objet dans un print DEBUG ONLY

        Paramètres : 
            @param self => variable représentant l'objet
        Retour de la fonction : 
            @return str => la représentation de l'objet

        """
        return self.__str__()
    
    @staticmethod
    def fromJson(json : dict)->object:
        player = Player(json["name"])
        player.brawlhalla_id = json["brawlhalla"]
        player.steam_id = json["steam"]
        player.legends = json["legends"]
    
    @staticmethod
    def loadFromSave():
        if(os.path.exists('./save.json')):
            with open('./save.json') as f:
                json = load(f)
                for p in json:
                    player = Player(p["name"])
                    player.brawlhalla_id = p["brawlhalla"]
                    player.steam_id = p["steam"]
                    player.legends = p["legends"]
    
    @staticmethod
    def statisticsFormatter(stats : dict, type_ : str = "stat") -> dict:
        formatted_stats : dict = {
            "player":{},
            "legends":[]
        }
        if(type_ == "stat"):
            formatted_stats["player"] = {
                "name" : stats["name"],
                "level" : stats["level"],
                "games" : {
                    "total" : stats["games"],
                    "wins" : stats["wins"]
                },
                # "clan" : {
                #     "name" : stats["clan"]["clan_name"],
                #     "xp" : {
                #         "total" : stats["clan"]["clan_xp"],
                #         "personnal" : stats["clan"]["personnal_xp"],
                #     }
                # }
            }

            for legend in stats["legends"]:
                legend_json = {
                    "name" : legend["legend_name_key"],
                    "kos" : legend["kos"],
                    "games" : {
                        "total" : legend["games"],
                        "wins" : legend["wins"],
                    }
                }
                formatted_stats["legends"].append(legend_json)
            formatted_stats["legends"].sort(key=lambda x: x["name"])

        elif(type_ == "ranked"):
            formatted_stats["player"] = {
                "name" : stats["name"],
                "rating" : {
                    "current" : stats["rating"],
                    "peak" : stats["peak_rating"],
                    "tier" : stats["tier"]
                },
                "games" : {
                        "total" : stats["games"],
                        "wins" : stats["wins"],
                }
               
            }
            for legend in stats["legends"]:
                legend_json = {
                    "name" : legend["legend_name_key"],
                    "rating" : {
                        "current" : legend["rating"],
                        "peak" : legend["peak_rating"],
                        "tier" : legend["tier"]
                    },
                    "games" : {
                        "total" : legend["games"],
                        "wins" : legend["wins"],
                    }
                }
                formatted_stats["legends"].append(legend_json)
            formatted_stats["legends"].sort(key= lambda x: x["rating"]["peak"], reverse=True)

        return formatted_stats


    @staticmethod
    def get(name: str) -> object or None:
        """!
        @brief Cette fonction statique permet de récuppérer un joueur à partir de son id discord

        Paramètres : 
            @param name : str => chaine de caractère représentant l'id_discord
        Retour de la fonction : 
            @return Player or None => l'objet joueur associé ou None

        """
        return Player.players.get(name, None)

    @staticmethod
    def weapon() -> str:
        """!
        @brief Cette fonction permet de tirer aléatoirement un challenge (ne pouvoir utiliser que certaines armes)

        Retour de la fonction : 
            @return str => le type d'arme que le joueur pourra utiliser

        """
        weapons = ["principale", "secondaire", "aucune", "objets", "tous"]
        return weapons[randint(0, len(weapons)-1)]

class Team:
    def __init__(self, color: str):
        """!
        @brief Constructeur de l'objet team

        Paramètres : 
            @param self => variable représentant l'objet
            @param color : str => la couleur de l'équipe (bleu, rouge ou Waiter(team d'attente))

        """
        self.color = color
        self.players = []
        
    def add(self, player : Player):
        """!
        @brief Cette fonction permet d'ajouter un joueur dans l'équipe

        Paramètres : 
            @param self => variable représentant l'objet
            @param player : Player => un objet Joueur

        """
        self.players.append(player)
    def remove(self, player : Player):
        """!
        @brief Cette fonction permet de supprimer un joueur de l'équipe

        Paramètres : 
            @param self => variable représentant l'objet
            @param player : Player => un objet joueur

        """
        if(player in self.players):
            self.players.remove(player)
    def melange(self):
        """!
        @brief Cette fonction permet de mélanger les joueurs à l'intérieur d'une équipe (par la team Waiter)

        Paramètres : 
            @param self => variable représentant l'objet

        """
        shuffle(self.players)
    def __len__(self) -> int:
        """!
        @brief Cette fonction permet de facilement avoir la taille de l'équipe (= taille de la liste de joueurs)

        Paramètres : 
            @param self => variable représentant l'objet
        Retour de la fonction : 
            @return int => la taille de l'équipe

        """
        return len(self.players)

    #La réaction utilisé par le bot pour ajouter une personne dans la team waiter
    teamReaction = ""
    #Initialisation des teams (variables statiques)
    teamRed = None
    teamBlue = None
    teamWaiter = None

    @staticmethod
    def participants()-> list:
        """!
        @brief Cette fonction permet de connaitres les joueurs en attente

        Retour de la fonction : 
            @return list => liste des joueurs en attente

        """
        if(len(Team.teamWaiter)>0):
            return Team.teamWaiter.players
        return []
    
    @staticmethod
    def init():
        """!
        @brief Cette fonction génère les 3 teams (rouge, bleu, waiter)


        """
        Team.teamRed = Team("red")
        Team.teamBlue = Team("blue")
        Team.teamWaiter = Team("waiter")
    @staticmethod
    def selection():
        """!
        @brief Cette fonction permet mettre les joueurs en attente dans les teams red et blue aléatoirement
        
        """
        Team.teamWaiter.melange()
        players = Team.teamWaiter.players
        mid = len(players)//2
        red = players[:mid]
        blue = players[mid:]

        Team.teamBlue.players = blue
        Team.teamRed.players = red


class brawlhallaAPI:
    api_key = "";
    
    @staticmethod
    def getBrawlHallaIDFromSteamID(steamID : str ) -> None or int:
        """!
        @brief Cette fonction permet d'obtenir le brawlhalla id d'un joueur à partir de son steam id

        Paramètres : 
            @param steamID : str => identifiant steam (disponible dans les paramètres du compte steam)
        Retour de la fonction : 
            @return None or int => Le brawlhalla id ou None si la requête échoue

        """
        reponse = requests.get(f"https://api.brawlhalla.com/search?steamid={steamID}&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json().get("brawlhalla_id", None)
        return None
        
    @staticmethod
    def getPlayerStats(brawlhalla_id : int) -> dict or None:
        """!
        @brief Cette fonction permet de récuppérer les statistiques d'un joueur à partir de son brawlhalla id

        Paramètres : 
            @param brawlhalla_id : int => le brawlhalla id d'un joueur
        Retour de la fonction : 
            @return dict or None => un json représentant les statistiques du joueur

        """
        reponse = requests.get(f"https://api.brawlhalla.com/player/{brawlhalla_id}/stats?&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json()
        return None

    @staticmethod
    def getPlayerRanked(brawlhalla_id : int) -> dict or None:
        """!
        @brief Cette fonction permet de récuppérer les statistiques de Ranked d'un joueur à partir de son brawlhalla id

        Paramètres : 
            @param brawlhalla_id : int => le brawlhalla id d'un joueur
        Retour de la fonction : 
            @return dict or None => un json représentant les statistiques ranked du joueur

        """
        reponse = requests.get(f"https://api.brawlhalla.com/player/{brawlhalla_id}/ranked?&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json()
        return None

    @staticmethod
    def getAllLegends() -> list:
        """!
        @brief Cette fonction permet d'obtenir la liste de toutes les legends du jeu

        Retour de la fonction : 
            @return list => la liste des noms des légends

        """
        reponse = requests.get(f"https://api.brawlhalla.com/legend/all/&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            json = reponse.json();
            liste = []
            for legend in json:
                liste.append(legend["legend_name_key"])
            return liste
        return None

    @staticmethod
    def getLegendOfPlayer(brawlhalla_id : str) -> None or list:
        """!
        @brief Cette fonction permet d'obtenir la liste des legends qu'un joueur possède

        Paramètres : 
            @param brawlhalla_id : str => le brawlhalla id d'un joueur
        Retour de la fonction : 
            @return None or list => la liste des legends qu'il possède

        """
        stats = brawlhallaAPI.getPlayerStats(brawlhalla_id)
        if(stats == None):
            return None
        legends = stats["legends"]
        liste = []
        for l in legends:
            liste.append(l["legend_name_key"])
        return liste
    
    @staticmethod
    def getClan(clan_id : str)-> None or dict:
        reponse = requests.get(f"https://api.brawlhalla.com/clan/{clan_id}/?&api_key={brawlhallaAPI.api_key}")
        if(reponse.status_code == 200):
            return reponse.json()
        return None
    