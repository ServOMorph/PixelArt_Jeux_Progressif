# Pixel Art Maze Game

> [!NOTE]
> **AI Context**: This is a Python/Pygame project structured with a Centralized Controller (`src/game.py`). Entry points are `run.py` (game) and `run_editeur.py` (editor). It uses JSON for persistence (`stats.json`, `levels/custom_levels.json`). Graphics are rendered via `src/ui.py`.

Un jeu de labyrinthe progressif en Pixel Art développé en Python avec Pygame.

## 🚀 Fonctionnalités

- **Aventure Progressive** : Traversez des niveaux de plus en plus complexes.
- **Éditeur de Niveaux Complet** : Créez vos propres labyrinthes avec ennemis et points d'intérêt.
- **Support de la Souris** : Naviguez dans les menus et dessinez vos niveaux à la souris.
- **Système de Stats** : Suivi de votre progression, nombre de morts et meilleurs niveaux.
- **Ennemis Dynamiques** : Mobs avec patterns de mouvement horizontaux et verticaux.
- **Mode Développeur** : Option de login automatique pour les tests rapides.

## 🛠️ Installation

Assurez-vous d'avoir Python 3.x installé sur votre système.

1. Clonez ou téléchargez le dépôt.
2. Installez la dépendance Pygame :
   ```bash
   pip install pygame
   ```

## 🎮 Comment Jouer

### Lancer le Jeu
Exécutez le script principal :
```bash
python run.py
```

### Contrôles en Jeu
- **Z / Q / S / D** : Déplacement du personnage.
- **SOURIS** : Clic sur les boutons de menu et options.
- **ECHAP** : Retour au menu principal.
- **ESPACE** : Passer au niveau suivant (après une victoire).

## 🏗️ Éditeur de Niveaux

Vous pouvez lancer l'éditeur depuis le menu principal du jeu ou via le script dédié :
```bash
python run_editeur.py
```

### Fonctionnalités de l'Éditeur
- **Peinture à la souris** : Maintenez le clic gauche pour dessiner des murs.
- **Outils (Touches 1-6)** :
  1. `WALL` : Murs infranchissables.
  2. `PATH` : Chemin libre.
  3. `START` : Point de départ du joueur.
  4. `EXIT` : Point d'arrivée (victoire).
  5. `MOB_H` : Ennemi à mouvement horizontal.
  6. `MOB_V` : Ennemi à mouvement vertical.
- **ID de Niveau** : Cliquez sur la boîte ID en haut pour changer le numéro du niveau (les niveaux personnalisés commencent à 100).
- **SAVE** : Enregistre le niveau dans `levels/custom_levels.json`.
- **CLEAR** : Réinitialise la grille.

## 📁 Structure du Projet

- `run.py` : Point d'entrée principal du jeu.
- `run_editeur.py` : Lanceur autonome de l'éditeur.
- `config.py` : Paramètres globaux (résolution, FPS, mode dev, couleurs).
- `src/` : Code source logique (entités, rendu, entrées, etc.).
- `levels/` : Données des niveaux par défaut et personnalisés.
- `stats.json` : Fichier de sauvegarde des statistiques joueurs.

---
Développé avec ❤️ pour ServOMorph.
