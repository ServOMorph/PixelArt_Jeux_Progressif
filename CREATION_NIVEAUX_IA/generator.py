# -*- coding: utf-8 -*-
"""
Générateur de Niveaux — Création procédurale de labyrinthes avec biomes et mobs.
Gère les séries de niveaux (ex: 10 niveaux avec progression de difficulté).
"""
import random
from src.tiles import TileType

class Biome:
    """Définit le style visuel d'un niveau."""
    def __init__(self, nom, mur, bordure, chemin, arbre=None, sortie=None):
        self.nom = nom
        self.colors = {
            "wall": mur,
            "wall_border": bordure,
            "path": chemin,
        }
        if arbre: self.colors["tree"] = arbre
        if sortie: self.colors["exit"] = sortie

# Définition des biomes disponibles
BIOMES = [
    Biome("Néon Violet", (138, 43, 226), (255, 100, 255), (25, 25, 112)),
    Biome("Forêt Mystique", (34, 139, 34), (0, 100, 0), (20, 40, 20), arbre=(34, 139, 34)),
    Biome("Enfer Rouge", (100, 0, 0), (200, 0, 0), (30, 0, 0), sortie=(255, 20, 147)),
    Biome("Abysses Bleues", (0, 0, 80), (0, 150, 255), (0, 0, 20)),
    Biome("Désert d'Or", (150, 100, 0), (255, 215, 0), (50, 30, 0)),
]

class LevelGenerator:
    """Génère des niveaux de labyrinthe de manière procédurale."""

    def __init__(self):
        pass

    def generer_serie(self, nombre=10, id_debut=200):
        """Génère une série de niveaux avec difficulté progressive."""
        serie = []
        for i in range(nombre):
            difficulte = (i + 1) / nombre
            est_boss = (i == nombre - 1)
            niveau = self.generer_niveau(
                id_niveau=id_debut + i,
                difficulte=difficulte,
                est_boss=est_boss
            )
            serie.append(niveau)
        return serie

    def generer_niveau(self, id_niveau, difficulte=0.5, est_boss=False):
        """Génère un seul niveau complet."""
        # Dimensions progressives
        largeur = 15 + int(difficulte * 10)
        hauteur = 11 + int(difficulte * 8)
        
        if est_boss:
            largeur += 4
            hauteur += 4

        # 1. Générer le labyrinthe (DFS)
        maze = self._generer_maze_dfs(largeur, hauteur)
        
        # 2. Choisir un biome
        biome = random.choice(BIOMES)
        
        # 3. Placer mobs
        mobs = self._placer_mobs(maze, difficulte, est_boss)
        
        # 4. Ajouter des arbres destructibles (selon biome ou aléatoire)
        if random.random() < 0.4 or biome.nom == "Forêt Mystique":
            self._ajouter_arbres(maze, difficulte)

        # 5. Déterminer start et exit
        start_pos = [1, 1]
        exit_pos = [largeur - 2, hauteur - 2]
        
        # S'assurer que exit est accessible (chemin)
        maze[exit_pos[1]][exit_pos[0]] = TileType.PATH

        return {
            "id": id_niveau,
            "name": f"{'BOSS: ' if est_boss else ''}{biome.nom} {id_niveau}",
            "maze": maze,
            "start_pos": start_pos,
            "exit_pos": exit_pos,
            "colors": biome.colors,
            "mobs": mobs
        }

    def _generer_maze_dfs(self, largeur, hauteur):
        """Algorithme de génération par Deep First Search (DFS)."""
        # Grille remplie de murs
        maze = [[TileType.WALL for _ in range(largeur)] for _ in range(hauteur)]
        
        # On travaille sur des coordonnées impaires pour laisser des murs entre les cellules
        # Largeur et hauteur effectives des "cellules"
        w, h = (largeur - 1) // 2, (hauteur - 1) // 2
        visite = [[False for _ in range(w)] for _ in range(h)]
        
        def creuser(cx, cy):
            visite[cy][cx] = True
            maze[cy*2 + 1][cx*2 + 1] = TileType.PATH
            
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and not visite[ny][nx]:
                    # Creuser le mur entre
                    maze[cy*2 + 1 + dy][cx*2 + 1 + dx] = TileType.PATH
                    creuser(nx, ny)

        creuser(0, 0)
        
        # Ajouter quelques ouvertures pour rendre le maze moins strict (plus de chemins)
        for _ in range(int(largeur * hauteur * 0.05)):
            rx = random.randint(1, largeur - 2)
            ry = random.randint(1, hauteur - 2)
            maze[ry][rx] = TileType.PATH
            
        return maze

    def _placer_mobs(self, maze, difficulte, est_boss):
        """Place des mobs intelligemment selon la difficulté."""
        mobs = []
        hauteur = len(maze)
        largeur = len(maze[0])
        
        # Nombre de mobs
        nb_mobs = int(3 + difficulte * 8)
        if est_boss: nb_mobs += 5
        
        # Types disponibles selon difficulté
        types = ["horizontal", "vertical"]
        if difficulte > 0.3: types.append("chaser")
        if difficulte > 0.6: types.append("shooter")
        
        for _ in range(nb_mobs):
            # Trouver une zone de chemin vide
            for _ in range(20): # Tentatives
                rx = random.randint(1, largeur - 2)
                ry = random.randint(1, hauteur - 2)
                
                if maze[ry][rx] == TileType.PATH and (rx > 3 or ry > 3): # Pas trop près du spawn
                    m_type = random.choice(types)
                    mob = {
                        "type": "Mob1",
                        "start_pos": [rx, ry],
                        "pattern": m_type,
                        "speed": 0.05 + (difficulte * 0.08)
                    }
                    
                    if m_type in ["horizontal", "vertical"]:
                        mob["distance"] = random.randint(2, 6)
                    elif m_type == "shooter":
                        mob["distance"] = random.randint(60, 150) # Délai de tir
                        
                    mobs.append(mob)
                    break
                    
        return mobs

    def _ajouter_arbres(self, maze, difficulte):
        """Ajoute des obstacles destructibles."""
        hauteur = len(maze)
        largeur = len(maze[0])
        densite = 0.05 + (difficulte * 0.1)
        
        for _ in range(int(largeur * hauteur * densite)):
            rx = random.randint(1, largeur - 2)
            ry = random.randint(1, hauteur - 2)
            if maze[ry][rx] == TileType.PATH:
                maze[ry][rx] = TileType.TREE
