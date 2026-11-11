# BotVar

Un bot Discord et une CLI pour retrouver les statistiques des joueurs Brawlhalla,
organiser des parties et bien plus encore.

## Installation

```bash
# Avec uv (recommandé)
uv venv .venv
uv pip install -e ".[dev]" --python .venv/bin/python

# Ou avec pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Utilisation

### CLI

```bash
# Lancer le REPL interactif (sans discord)
botvar repl

# Lancer le bot discord (nécessite DISCORD_TOKEN)
botvar bot

# Commandes directes
botvar legend rdm          # tirer une legend aléatoire
botvar legend weapon       # tirer un challenge d'armes
botvar legend list         # lister les legends restantes
botvar player steam <id>   # lier son compte steam
botvar player stats        # afficher les statistiques
botvar player ranked       # afficher les statistiques ranked
botvar player clan         # afficher les infos clan
botvar teams new 1234      # lancer une partie
botvar teams list          # lister les participants
botvar teams select        # tirer les équipes
botvar teams reset         # réinitialiser
botvar save                # sauvegarder les joueurs
```

### REPL

```
botvar> help
botvar> legend rdm
Utilise : Jiro
botvar> player stats
...
botvar> quit
```

### Bot Discord

Le bot répond aux commandes `!b <commande> <option>` sur le serveur Discord.
Exemples : `!b legend rdm`, `!b player stats`, `!b teams new 1234`.

## Configuration

- **Bot Discord** : le token est lu depuis la variable d'environnement `DISCORD_TOKEN`
  ou le fichier `apikey.txt` (`<brawlhalla_api_key> <discord_token>`).
- **API Brawlhalla** : la clé est lue depuis `BRAWLHALLA_API_KEY` ou le même fichier.

## Tests

```bash
python -m unittest discover -s tests -v
```

## TODO
- Changer l'affichage des legends
