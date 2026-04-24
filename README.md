# Pixel Art Maze Game

> [!NOTE]
> **AI Context**: This is a Python/Pygame project structured with a Centralized Controller (`src/game.py`). Entry points are `run.py` (game) and `run_editeur.py` (editor). It uses JSON for persistence (`stats.json`, `levels/custom_levels.json`). Graphics are rendered via `src/ui.py`.

Un jeu de labyrinthe progressif en Pixel Art développé en Python avec Pygame.

## 🚀 Fonctionnalités

- **Aventure Progressive** : Traversez des niveaux de plus en plus complexes.
- **Éditeur de Niveaux Complet** : Créez vos propres labyrinthes avec ennemis et points d'intérêt.
- **Support de la Souris** : Naviguez dans les menus et dessinez vos niveaux à la souris.
- **Système de Stats** : Suivi de votre progression, nombre de morts et meilleurs niveaux.
- **Ennemis Dynamiques** : Mobs patrouilleurs, traqueurs (chaser) et tireurs de missiles (shooter).
- **Tuiles Destructibles** : Système d'arbres pouvant être détruits par les missiles (HP).
- **Grille de Sélection** : Naviguez parmi des dizaines de niveaux via une interface claire.
- **Thèmes Visuels** : Basculez entre le mode **Défaut** (géométrique) et le mode **Chiadé** (Pixel Art Premium).

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
- **SOURIS** : Clic sur les boutons de menu, options et édition.
- **ECHAP** : Retour au menu principal (ou retour à l'éditeur depuis le mode test).
- **Options** : Menu dédié pour configurer le mode de rendu graphique.

## 🏗️ Éditeur de Niveaux

### Raccourcis de l'Éditeur (1-9)
1. `WALL` : Mur classique.
2. `PATH` : Vide / Chemin.
3. `START` : Point de départ.
4. `EXIT` : Arrivée.
5. `TREE` : Arbre destructible (3 HP).
6. `MOB_H` : Patrouille Horizontale.
7. `MOB_V` : Patrouille Verticale.
8. `TRACKER` : Mob qui suit le joueur.
9. `MISSILE` : Mob qui tire sur le joueur.
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
