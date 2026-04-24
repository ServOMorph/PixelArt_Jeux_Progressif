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
- **`entities.py`** : Modèles du Joueur.
- **`tiles.py`** : Système de tuiles extensible (Propriétés, HP).
- **`input_handler.py`** : Pont entre les événements Pygame et la logique métier.
- **`level.py`** : Gestionnaire de chargement (Dynamique) et de validation des labyrinthes.
- **`ui.py`** : Moteur de rendu graphique (Gestion des arbres, grille de sélection).

## 📂 mobs/ (IA Modulaire)
- **`base.py`** : Classe abstraite pour tous les ennemis.
- **`patrol.py`** : Logique de patrouille (H/V).
- **`chaser.py`** : Logique de traque du joueur.
- **`shooter.py`** : Logique de tir et gestion des projectiles.
- **`factory.py`** : Créateur dynamique de mobs selon la config.

## 📂 levels/ (Données)
- **`levels_config.py`** : Définition des niveaux d'aventure par défaut.
- **`custom_levels.json`** : Base de données des niveaux créés par l'utilisateur.

## 📂 COMMANDS/ (Workflows)
- **`startV2.md`** : Protocole d'initialisation de session.
- **`closeV2.md`** : Protocole de clôture.
- **`optimize_docs.md`** : Protocole de standardisation documentaire.
