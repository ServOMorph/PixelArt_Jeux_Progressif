# -*- coding: utf-8 -*-
"""
Agent IA — Joue visuellement au jeu en utilisant A* et l'esquive de dangers.
Contrôle le Player existant exactement comme un humain le ferait.
"""
import heapq
import math


class AgentIA:
    """Agent intelligent qui joue au jeu en temps réel.
    
    Compréhension du jeu comme un humain :
    - Voit le labyrinthe complet (comme un humain voit l'écran)
    - Connaît la position des mobs et des projectiles
    - Planifie un chemin vers la sortie (A*)
    - Détecte les dangers proches et recalcule son chemin
    - Apprend des morts précédentes (zones à éviter)
    """

    def __init__(self, niveau, joueur):
        self.niveau = niveau
        self.joueur = joueur
        self.chemin = []  # Liste de (x, y) — tuiles à suivre
        self.index_chemin = 0
        self.zones_danger = {}  # (x,y) -> score de danger (augmenté par les morts)
        self.derniere_position = None
        self.frames_immobile = 0
        self.seuil_recalcul = 30  # Recalculer si immobile trop longtemps
        self.marge_esquive = 2.5  # Distance pour détecter un danger
        self.en_esquive = False
        self.objectif_esquive = None

    def initialiser(self):
        """Calcule le premier chemin vers la sortie."""
        self.chemin = self._trouver_chemin(
            (int(self.joueur.x), int(self.joueur.y)),
            (self.niveau.exit_x, self.niveau.exit_y)
        )
        self.index_chemin = 0
        self.frames_immobile = 0
        self.en_esquive = False

    def mettre_a_jour(self, mobs, projectiles):
        """Décide de la prochaine action. Retourne (dx, dy) normalisé.
        
        Logique de décision (comme un humain) :
        1. Y a-t-il un danger immédiat ? → Esquiver
        2. Suis-je bloqué ? → Recalculer le chemin
        3. Sinon → Suivre le chemin planifié
        """
        pos_joueur = (self.joueur.x, self.joueur.y)
        
        # 1. Détection de danger immédiat (projectiles proches)
        danger = self._detecter_danger(mobs, projectiles)
        if danger:
            return self._esquiver(danger, mobs, projectiles)

        # 2. Détection si on est bloqué
        if self.derniere_position:
            dx = abs(pos_joueur[0] - self.derniere_position[0])
            dy = abs(pos_joueur[1] - self.derniere_position[1])
            if dx < 0.01 and dy < 0.01:
                self.frames_immobile += 1
            else:
                self.frames_immobile = 0

        self.derniere_position = pos_joueur

        if self.frames_immobile > self.seuil_recalcul:
            self.chemin = self._trouver_chemin(
                (int(self.joueur.x), int(self.joueur.y)),
                (self.niveau.exit_x, self.niveau.exit_y)
            )
            self.index_chemin = 0
            self.frames_immobile = 0

        # 3. Suivre le chemin
        if not self.chemin or self.index_chemin >= len(self.chemin):
            # Plus de chemin — recalculer
            self.chemin = self._trouver_chemin(
                (int(self.joueur.x), int(self.joueur.y)),
                (self.niveau.exit_x, self.niveau.exit_y)
            )
            self.index_chemin = 0
            if not self.chemin:
                return (0, 0)  # Aucun chemin trouvé

        # Obtenir la prochaine tuile cible
        cible_x, cible_y = self.chemin[self.index_chemin]
        
        # Calculer la direction vers la cible
        dx = cible_x - self.joueur.x
        dy = cible_y - self.joueur.y
        dist = math.sqrt(dx**2 + dy**2)

        # Si on est assez proche de la tuile cible, passer à la suivante
        if dist < 0.3:
            self.index_chemin += 1
            if self.index_chemin >= len(self.chemin):
                return (0, 0)
            cible_x, cible_y = self.chemin[self.index_chemin]
            dx = cible_x - self.joueur.x
            dy = cible_y - self.joueur.y
            dist = math.sqrt(dx**2 + dy**2)

        if dist > 0:
            # Normaliser pour donner une direction (le Player gère la vitesse)
            return (dx / dist, dy / dist)
        
        return (0, 0)

    def apprendre_mort(self, x, y, cause):
        """Mémorise une zone dangereuse après une mort."""
        tuile = (int(x), int(y))
        # Marquer la zone autour comme dangereuse
        for ox in range(-1, 2):
            for oy in range(-1, 2):
                pos = (tuile[0] + ox, tuile[1] + oy)
                self.zones_danger[pos] = self.zones_danger.get(pos, 0) + 5

    def _detecter_danger(self, mobs, projectiles):
        """Détecte le danger le plus proche. Retourne sa position ou None."""
        px, py = self.joueur.x, self.joueur.y
        danger_proche = None
        dist_min = self.marge_esquive

        # Vérifier les projectiles (danger prioritaire)
        for proj in projectiles:
            dist = math.sqrt((proj.x - px)**2 + (proj.y - py)**2)
            if dist < dist_min:
                dist_min = dist
                danger_proche = (proj.x, proj.y, "projectile", proj.vx, proj.vy)

        # Vérifier les mobs
        for mob in mobs:
            dist = math.sqrt((mob.x - px)**2 + (mob.y - py)**2)
            if dist < dist_min * 0.8:  # Les mobs sont un peu moins prioritaires
                dist_min = dist
                danger_proche = (mob.x, mob.y, "mob", 0, 0)

        return danger_proche

    def _esquiver(self, danger, mobs, projectiles):
        """Calcule un mouvement d'esquive perpendiculaire au danger."""
        dx, dy = danger[0], danger[1]
        px, py = self.joueur.x, self.joueur.y
        
        # Direction du danger vers nous
        vers_nous_x = px - dx
        vers_nous_y = py - dy
        dist = math.sqrt(vers_nous_x**2 + vers_nous_y**2)
        
        if dist < 0.01:
            return (1, 0)  # Fuir dans une direction par défaut

        # Normaliser
        vers_nous_x /= dist
        vers_nous_y /= dist

        # Direction perpendiculaire (choisir le côté le plus sûr)
        perp1 = (-vers_nous_y, vers_nous_x)
        perp2 = (vers_nous_y, -vers_nous_x)

        # Tester quel côté est walkable
        test1_x = int(px + perp1[0] * 1.5)
        test1_y = int(py + perp1[1] * 1.5)
        test2_x = int(px + perp2[0] * 1.5)
        test2_y = int(py + perp2[1] * 1.5)

        score1 = 0 if self.niveau.is_walkable(test1_x, test1_y) else -100
        score2 = 0 if self.niveau.is_walkable(test2_x, test2_y) else -100

        # Bonus pour se rapprocher de la sortie
        dist_sortie_1 = math.sqrt((test1_x - self.niveau.exit_x)**2 + (test1_y - self.niveau.exit_y)**2)
        dist_sortie_2 = math.sqrt((test2_x - self.niveau.exit_x)**2 + (test2_y - self.niveau.exit_y)**2)
        score1 -= dist_sortie_1
        score2 -= dist_sortie_2

        # Aussi s'éloigner du danger (composante de fuite)
        fuite_x = vers_nous_x * 0.5
        fuite_y = vers_nous_y * 0.5

        if score1 >= score2:
            return (perp1[0] + fuite_x, perp1[1] + fuite_y)
        else:
            return (perp2[0] + fuite_x, perp2[1] + fuite_y)

    def _trouver_chemin(self, depart, arrivee):
        """Algorithme A* pour trouver le chemin optimal.
        
        Prend en compte les zones_danger apprises des morts précédentes.
        """
        if depart == arrivee:
            return [arrivee]

        ouvert = []
        heapq.heappush(ouvert, (0, depart))
        parents = {depart: None}
        cout_g = {depart: 0}

        while ouvert:
            _, courant = heapq.heappop(ouvert)

            if courant == arrivee:
                # Reconstruire le chemin
                chemin = []
                while courant is not None:
                    chemin.append(courant)
                    courant = parents[courant]
                chemin.reverse()
                return chemin

            for voisin in self._obtenir_voisins(courant):
                # Coût de base = 1 + pénalité de danger
                penalite = self.zones_danger.get(voisin, 0)
                nouveau_cout = cout_g[courant] + 1 + penalite

                if voisin not in cout_g or nouveau_cout < cout_g[voisin]:
                    cout_g[voisin] = nouveau_cout
                    # Heuristique : distance Manhattan
                    h = abs(voisin[0] - arrivee[0]) + abs(voisin[1] - arrivee[1])
                    f = nouveau_cout + h
                    heapq.heappush(ouvert, (f, voisin))
                    parents[voisin] = courant

        return []  # Pas de chemin trouvé

    def _obtenir_voisins(self, pos):
        """Retourne les tuiles voisines accessibles (4 directions)."""
        x, y = pos
        voisins = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if self.niveau.is_walkable(nx, ny):
                voisins.append((nx, ny))
        return voisins

    def obtenir_chemin_actuel(self):
        """Retourne le chemin restant pour le rendu visuel."""
        if self.chemin and self.index_chemin < len(self.chemin):
            return self.chemin[self.index_chemin:]
        return []
