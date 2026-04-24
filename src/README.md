# Source Code (src/)

Ce dossier contient le cœur de la logique du jeu.

## 📄 Fichiers

- **`constants.py`** : Définit les états du jeu (`GameState`).
- **`data_manager.py`** : Gère la lecture et l'écriture des fichiers JSON (`stats.json`, `custom_levels.json`).
- **`entities.py`** : Logique des entités (`Player` et `Mob`), incluant les mouvements et collisions.
- **`input_handler.py`** : Capture les événements clavier et souris et les traduit en actions de jeu.
- **`level.py`** : Classes `Level` et `LevelManager` pour charger et manipuler les labyrinthes.
- **`ui.py`** : Moteur de rendu (`UIRenderer`, `GameRenderer`) et gestion des polices.
- **`editor.py`** : Logique complète de l'éditeur de niveaux interactif.
- **`__init__.py`** : Marque le dossier comme un package Python.
