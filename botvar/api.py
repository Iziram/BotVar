"""! @brief Client de l'api publique Brawlhalla
 @file api.py
 @section libs Librairies/Modules
   - requests

 @section authors Auteur(s)
   - Créé par Matthias HARTMANN le 31/03/2022 .
"""
import requests

API_URL = "https://api.brawlhalla.com"


class BrawlhallaAPI:
    """Client statique de l'api Brawlhalla.

    La clé d'api se configure via la variable de classe ``api_key`` (ou la
    variable d'environnement ``BRAWLHALLA_API_KEY`` au premier appel).
    """

    api_key: str = ""

    @classmethod
    def _key(cls) -> str:
        import os

        return cls.api_key or os.environ.get("BRAWLHALLA_API_KEY", "")

    @classmethod
    def _get(cls, path: str, params: dict) -> dict | None:
        response = requests.get(f"{API_URL}{path}", params={"api_key": cls._key(), **params})
        if response.status_code == 200:
            return response.json()
        return None

    @classmethod
    def get_brawlhalla_id_from_steam_id(cls, steam_id: str) -> int | None:
        """!
        @brief Obtient le brawlhalla id d'un joueur à partir de son steam id.

        @param steam_id : str => identifiant steam (paramètres du compte steam)
        @return int or None => le brawlhalla id, None si la requête échoue
        """
        data = cls._get("/search", {"steamid": steam_id})
        if data is None:
            return None
        return data.get("brawlhalla_id")

    @classmethod
    def get_player_stats(cls, brawlhalla_id: int) -> dict | None:
        """!
        @brief Statistiques globales d'un joueur à partir de son brawlhalla id.

        @return dict or None => les statistiques du joueur
        """
        return cls._get(f"/player/{brawlhalla_id}/stats", {})

    @classmethod
    def get_player_ranked(cls, brawlhalla_id: int) -> dict | None:
        """!
        @brief Statistiques ranked d'un joueur à partir de son brawlhalla id.

        @return dict or None => les statistiques ranked du joueur
        """
        return cls._get(f"/player/{brawlhalla_id}/ranked", {})

    @classmethod
    def get_all_legends(cls) -> list | None:
        """!
        @brief Liste de toutes les legends du jeu.

        @return list or None => la liste des noms des légends
        """
        data = cls._get("/legend/all", {})
        if data is None:
            return None
        return [legend["legend_name_key"] for legend in data]

    @classmethod
    def get_legend_of_player(cls, brawlhalla_id: str) -> list | None:
        """!
        @brief Liste des legends qu'un joueur possède.

        @param brawlhalla_id : str => le brawlhalla id d'un joueur
        @return list or None => la liste des legends possédées
        """
        stats = cls.get_player_stats(brawlhalla_id)
        if stats is None:
            return None
        return [legend["legend_name_key"] for legend in stats["legends"]]

    @classmethod
    def get_clan(cls, clan_id: str) -> dict | None:
        """!
        @brief Récupère les informations d'un clan à partir de son id.

        @return dict or None => le json du clan
        """
        return cls._get(f"/clan/{clan_id}", {})


# Compatibilité avec l'ancienne API (``brawlhallaAPI`` du module player.py)
brawlhallaAPI = BrawlhallaAPI
