# -*- coding: utf-8 -*-
"""
Journal de session — Enregistre les événements importants pendant le jeu de l'IA.
Utilisé ensuite pour l'analyse par Ollama.
"""
import time
import json
import os
from datetime import datetime


class SessionLogger:
    """Enregistre les événements d'une session de jeu IA."""

    def __init__(self, niveau_id, niveau_nom):
        self.niveau_id = niveau_id
        self.niveau_nom = niveau_nom
        self.tentative = 0
        self.evenements = []
        self.morts = []
        self.chemin = []  # Liste de (x, y) — positions visitées
        self.carte_chaleur = {}  # (x,y) -> nombre de passages
        self.temps_debut = None
        self.temps_total = 0.0
        self.frames_total = 0
        self.victoire = False
        self.distance_totale = 0.0
        self.distance_tentative = 0.0

    def demarrer_tentative(self):
        """Démarre une nouvelle tentative."""
        self.tentative += 1
        self.temps_debut = time.time()
        self.chemin = []
        self.distance_tentative = 0.0
        self.ajouter_evenement(f"🔄 Tentative #{self.tentative} démarrée")

    def enregistrer_position(self, x, y):
        """Enregistre une position du joueur IA."""
        pos = (round(x, 1), round(y, 1))
        
        # Calcul de la distance parcourue
        if self.chemin:
            dernier_x, dernier_y = self.chemin[-1]
            dx = pos[0] - dernier_x
            dy = pos[1] - dernier_y
            dist = (dx**2 + dy**2)**0.5
            self.distance_tentative += dist
            self.distance_totale += dist

        self.chemin.append(pos)
        
        # Carte de chaleur (arrondi à la tuile)
        tuile = (int(x), int(y))
        self.carte_chaleur[tuile] = self.carte_chaleur.get(tuile, 0) + 1
        self.frames_total += 1

    def enregistrer_mort(self, cause, x, y):
        """Enregistre une mort avec sa cause."""
        duree = round(time.time() - self.temps_debut, 2) if self.temps_debut else 0
        self.temps_total += duree
        self.morts.append({
            "tentative": self.tentative,
            "cause": cause,
            "position": (round(x, 1), round(y, 1)),
            "frame": self.frames_total,
            "temps": duree
        })
        self.ajouter_evenement(f"💀 Mort #{len(self.morts)} — {cause} en ({int(x)},{int(y)})")

    def enregistrer_victoire(self):
        """Enregistre une victoire."""
        self.victoire = True
        duree = round(time.time() - self.temps_debut, 2) if self.temps_debut else 0
        self.temps_total += duree
        self.ajouter_evenement(f"🏆 Victoire ! Tentative #{self.tentative} en {duree}s")

    def ajouter_evenement(self, texte):
        """Ajoute un événement textuel au journal."""
        self.evenements.append({
            "frame": self.frames_total,
            "texte": texte
        })

    def obtenir_resume(self):
        """Retourne un résumé structuré de la session pour Ollama."""
        # Zones dangereuses = positions fréquentes de mort (Converties en string pour JSON)
        zones_danger = {}
        for mort in self.morts:
            tuile_str = f"{int(mort['position'][0])},{int(mort['position'][1])}"
            zones_danger[tuile_str] = zones_danger.get(tuile_str, 0) + 1

        # Zones les plus visitées (top 10) (Converties en string pour JSON)
        zones_populaires = []
        for tuile, nb in sorted(self.carte_chaleur.items(), key=lambda x: x[1], reverse=True)[:10]:
            zones_populaires.append({
                "pos": f"{tuile[0]},{tuile[1]}",
                "passages": nb
            })

        return {
            "niveau_id": self.niveau_id,
            "niveau_nom": self.niveau_nom,
            "tentatives": self.tentative,
            "morts_total": len(self.morts),
            "victoire": self.victoire,
            "distance_parcourue": round(self.distance_totale, 1),
            "temps_total_secondes": round(self.temps_total, 2),
            "causes_de_mort": self._compter_causes(),
            "zones_danger": zones_danger,
            "zones_populaires": zones_populaires,
        }

    def _compter_causes(self):
        """Compte les causes de mort."""
        compteur = {}
        for mort in self.morts:
            cause = mort["cause"]
            compteur[cause] = compteur.get(cause, 0) + 1
        return compteur

    def obtenir_logs_recents(self, n=15):
        """Retourne les N derniers événements pour l'affichage dashboard."""
        return [e["texte"] for e in self.evenements[-n:]]

    def sauvegarder_archive(self, evaluation_ia=None):
        """Sauvegarde la session et l'évaluation dans un fichier JSON."""
        # Créer le dossier logs s'il n'existe pas
        log_dir = "CREATION_NIVEAUX_IA/logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{log_dir}/test_{self.niveau_id}_{timestamp}.json"
        
        data = {
            "session": self.obtenir_resume(),
            "evaluation_ia": evaluation_ia,
            "date": datetime.now().isoformat(),
            "morts_detail": self.morts,
            "evenements": self.evenements
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return filename
