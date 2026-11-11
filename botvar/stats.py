"""! @brief Formatage des statistiques Brawlhalla
 @file stats.py

 Transforme le json brut de l'api en une structure lisible (utilisée pour
 l'affichage CLI et pour les exports du bot discord).
"""


def format_stats(stats: dict) -> dict:
    """!
    @brief Formate les statistiques globales d'un joueur.

    @param stats : dict => json brut de l'api (endpoint /player/<id>/stats)
    @return dict => structure simplifiée
    """
    formatted: dict = {"player": {}, "legends": []}
    formatted["player"] = {
        "name": stats["name"],
        "level": stats["level"],
        "games": {
            "total": stats["games"],
            "wins": stats["wins"],
        },
    }
    for legend in stats["legends"]:
        formatted["legends"].append(
            {
                "name": legend["legend_name_key"],
                "kos": legend["kos"],
                "games": {
                    "total": legend["games"],
                    "wins": legend["wins"],
                },
            }
        )
    formatted["legends"].sort(key=lambda x: x["name"])
    return formatted


def format_ranked(stats: dict) -> dict:
    """!
    @brief Formate les statistiques ranked d'un joueur.

    @param stats : dict => json brut de l'api (endpoint /player/<id>/ranked)
    @return dict => structure simplifiée
    """
    formatted: dict = {"player": {}, "legends": []}
    formatted["player"] = {
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
        formatted["legends"].append(
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
    formatted["legends"].sort(key=lambda x: x["rating"]["peak"], reverse=True)
    return formatted


def format(stats: dict, type_: str = "stat") -> dict:
    """Formatte selon le type de statistiques demandées (``stat`` ou ``ranked``)."""
    if type_ == "ranked":
        return format_ranked(stats)
    return format_stats(stats)
