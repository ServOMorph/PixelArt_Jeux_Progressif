# Project Map - Pixel Art Maze Game

Ce document sert d'index technique pour une navigation rapide par l'IA.

## 📂 Racine
- **`run.py`** : Point d'entrée principal (Jeu complet).
- **`run_editeur.py`** : Point d'entrée de l'éditeur de niveaux standalone.
- **`config.py`** : Constantes globales (Résolution, FPS, Couleurs, Mode Dev).
- **`stats.json`** : Stockage persistant des statistiques joueurs (JSON).

## 📂 src/ (Cœur de Logique)
- **`constants.py`** : Énumérations des états du jeu (`GameState`).
- **`data_manager.py`** : Service de persistance (Stats & Niveaux Custom).
- **`entities.py`** : Modèles du Joueur et des Ennemis (IA de base, mouvement).
- **`input_handler.py`** : Pont entre les événements Pygame et la logique métier.
- **`level.py`** : Gestionnaire de chargement et de validation des labyrinthes.
- **`ui.py`** : Moteur de rendu graphique (Basé sur Pygame surfaces).
- **`editor.py`** : Interface de création interactive de niveaux.

## 📂 levels/ (Données)
- **`levels_config.py`** : Définition des niveaux d'aventure par défaut.
- **`custom_levels.json`** : Base de données des niveaux créés par l'utilisateur.

## 📂 COMMANDS/ (Workflows)
- **`startV2.md`** : Protocole d'initialisation de session.
- **`closeV2.md`** : Protocole de clôture.
- **`optimize_docs.md`** : Protocole de standardisation documentaire.
