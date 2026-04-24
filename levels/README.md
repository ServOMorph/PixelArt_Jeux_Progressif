# Niveaux (levels/)

Ce dossier contient les données de structure des labyrinthes.

## 📄 Fichiers

- **`levels_config.py`** : Contient les niveaux "hardcodés" par défaut fournis avec le jeu.
- **`custom_levels.json`** : (Généré automatiquement) Contient les niveaux créés par l'utilisateur via l'éditeur.
- **`__init__.py`** : Package Python pour l'importation des configurations de niveaux.

## 🛠️ Structure d'un niveau
Un niveau est défini par :
- `id` : Identifiant unique.
- `maze` : Une matrice 2D d'entiers (1 pour mur, 0 pour chemin).
- `start_pos` : Coordonnées `[x, y]` de départ.
- `exit_pos` : Coordonnées `[x, y]` de la sortie.
- `mobs` : Liste des ennemis avec leurs patterns.
