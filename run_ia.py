# -*- coding: utf-8 -*-
"""
Point d'entrée — Système IA de Création & Évaluation de Niveaux.
Lance une fenêtre Pygame splittée : jeu à gauche, tableau de commande à droite.

Usage: python run_ia.py
"""
import sys
import os
import time

import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, COLORS, FPS
from src.level import Level, LevelManager
from src.entities import Player
from src.ui import FontManager, GameRenderer
from src.data_manager import DataManager
from mobs import create_mob

from CREATION_NIVEAUX_IA.ai_agent import AgentIA
from CREATION_NIVEAUX_IA.dashboard import Dashboard, COULEURS_DASH
from CREATION_NIVEAUX_IA.session_logger import SessionLogger
from CREATION_NIVEAUX_IA.ollama_client import ClientOllama
from CREATION_NIVEAUX_IA.generator import LevelGenerator

# --- CONSTANTE GLOBALE DE VITESSE ---
# Tout le jeu (mobs, projectiles, IA) est calé sur ce multiplicateur.
# Modifiable dynamiquement via le slider du dashboard.
VITESSE_JEU = 1.0


class ControleurIA:
    """Contrôleur principal du système IA.
    
    Gère :
    - L'affichage splitté (jeu + dashboard)
    - L'agent IA qui joue en direct
    - La communication avec Ollama
    - Le cycle de test/évaluation
    """

    def __init__(self):
        pygame.init()
        
        # Fenêtre plein écran
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🧠 IA — Création & Évaluation de Niveaux")
        self.clock = pygame.time.Clock()

        # Layout splitté : Plus de place pour le jeu, dashboard réduit
        self.largeur_jeu = 1400  # Largeur confortable pour voir tout le jeu
        self.largeur_dashboard = WINDOW_WIDTH - self.largeur_jeu  # ~520px

        # Composants
        self.data_manager = DataManager()
        self.font_manager = FontManager()
        self.level_manager = LevelManager(self.data_manager.load_custom_levels())
        self.generator = LevelGenerator()
        self.dashboard = Dashboard(self.largeur_jeu, self.largeur_dashboard, WINDOW_HEIGHT)
        self.ollama = ClientOllama()

        # État du jeu
        self.accumulateur_vitesse = 0.0
        self.niveau = None
        self.joueur = None
        self.mobs = []
        self.projectiles = []
        self.game_renderer = None
        self.agent = None
        self.logger = None

        # État du système
        self.en_cours = False
        self.en_pause = False
        self.niveau_actuel_id = 1
        self.donnees_niveau_actuel = None
        self.temps_debut_tentative = 0

        # Générer une première série de 10 niveaux IA (IDs à partir de 200)
        self._generer_nouvelle_serie()
        
        # Charger le premier niveau de la série
        self._charger_niveau(200)
        
        # Envoyer la liste des niveaux au dashboard
        self.dashboard.definir_niveaux(self.level_manager.get_all_levels_ids())
        
        # Vérifier Ollama au démarrage
        if self.ollama.est_disponible():
            self.dashboard.ajouter_log("✅ Ollama connecté")
        else:
            self.dashboard.ajouter_log("⚠️ Ollama non détecté (localhost:11434)")

    def _charger_niveau(self, niveau_id):
        """Charge un niveau et prépare l'agent IA."""
        if not self.level_manager.set_current_level(niveau_id):
            # Essayer le premier niveau disponible
            ids = self.level_manager.get_all_levels_ids()
            if not ids:
                self.dashboard.ajouter_log("❌ Aucun niveau trouvé !")
                return False
            niveau_id = ids[0]
            self.level_manager.set_current_level(niveau_id)

        self.niveau = self.level_manager.get_current_level()
        if not self.niveau or not self.niveau.maze:
            self.dashboard.ajouter_log(f"❌ Niveau {niveau_id} invalide")
            return False

        self.niveau_actuel_id = niveau_id
        
        # Sauvegarder les données brutes pour Ollama
        self.donnees_niveau_actuel = self._extraire_donnees_niveau()
        
        # Créer le joueur
        self.joueur = Player(self.niveau, start_x=self.niveau.start_x, start_y=self.niveau.start_y)
        
        # Créer les mobs
        self.mobs = []
        for m_data in self.niveau.mobs_data:
            mob = create_mob(m_data, self.niveau)
            self.mobs.append(mob)
        self.projectiles = []

        # Créer le renderer (adapté à la moitié gauche)
        self.game_renderer = GameRendererIA(
            self.screen, self.font_manager, self.niveau, self.largeur_jeu
        )

        # Créer l'agent IA
        self.agent = AgentIA(self.niveau, self.joueur)
        self.agent.initialiser()

        # Créer le logger
        self.logger = SessionLogger(self.niveau.id, self.niveau.name)

        # Mise à jour du dashboard
        self.dashboard.mettre_a_jour_stats(
            niveau_id=self.niveau.id,
            niveau_nom=self.niveau.name,
            tentative=0,
            morts=0,
            temps=0.0,
            distance=0.0,
            victoire=False
        )
        self.dashboard.ajouter_log(f"📦 Niveau {niveau_id} — {self.niveau.name} chargé")
        
        return True

    def _generer_nouvelle_serie(self, nombre=None):
        """Génère une nouvelle série de niveaux et les injecte dans le manager."""
        if nombre is None:
            nombre = self.dashboard.taille_serie if hasattr(self, 'dashboard') else 10
            
        self.dashboard.ajouter_log(f"🛠️ Génération d'une nouvelle série de {nombre} niveaux...")
        serie = self.generator.generer_serie(nombre=nombre, id_debut=200)
        
        # On rafraîchit le manager avec ces nouveaux niveaux
        # Note: On garde les niveaux originaux et on ajoute les nouveaux
        all_levels_data = self.data_manager.load_custom_levels()
        all_levels_data.extend(serie)
        self.level_manager.refresh_levels(all_levels_data)
        
        self.dashboard.definir_niveaux(self.level_manager.get_all_levels_ids())
        self.dashboard.ajouter_log("✅ Série de 10 niveaux générée (IDs 200-209)")

    def _extraire_donnees_niveau(self):
        """Extrait les données brutes du niveau pour Ollama."""
        return {
            "id": self.niveau.id,
            "name": self.niveau.name,
            "maze": [list(row) for row in self.niveau.maze],
            "start_pos": [self.niveau.start_x, self.niveau.start_y],
            "exit_pos": [self.niveau.exit_x, self.niveau.exit_y],
            "mobs": self.niveau.mobs_data,
        }

    def _reinitialiser_tentative(self):
        """Recharge le niveau pour une nouvelle tentative (sans tout recréer)."""
        # Recharger le niveau (pour reset les arbres destructibles)
        self.level_manager.set_current_level(self.niveau_actuel_id)
        self.niveau = self.level_manager.get_current_level()
        
        # Reset joueur
        self.joueur = Player(self.niveau, start_x=self.niveau.start_x, start_y=self.niveau.start_y)
        
        # Reset mobs
        self.mobs = []
        for m_data in self.niveau.mobs_data:
            mob = create_mob(m_data, self.niveau)
            self.mobs.append(mob)
        self.projectiles = []

        # Reset agent (mais garder les zones_danger apprises !)
        zones_apprises = self.agent.zones_danger if self.agent else {}
        self.agent = AgentIA(self.niveau, self.joueur)
        self.agent.zones_danger = zones_apprises
        self.agent.initialiser()

        # Mettre à jour le renderer
        self.game_renderer = GameRendererIA(
            self.screen, self.font_manager, self.niveau, self.largeur_jeu
        )

        # Logger
        self.logger.demarrer_tentative()
        self.temps_debut_tentative = time.time()

        self.dashboard.mettre_a_jour_stats(
            tentative=self.logger.tentative if self.logger else 1,
            victoire=False
        )

    def _demarrer(self):
        """Démarre ou redémarre l'agent IA."""
        self.en_cours = True
        self.en_pause = False
        
        # Recharger le niveau proprement
        niveaux_all = self.data_manager.load_custom_levels()
        self.level_manager.refresh_levels(niveaux_all)
        self._charger_niveau(self.niveau_actuel_id)
        
        self._reinitialiser_tentative()
        self.dashboard.ajouter_log("▶ IA démarrée !")

    def _gerer_mort(self, cause):
        """Gère la mort du joueur."""
        if self.logger:
            self.logger.enregistrer_mort(cause, self.joueur.x, self.joueur.y)
        
        # L'agent apprend de sa mort pour la prochaine tentative
        if self.agent:
            self.agent.apprendre_mort(self.joueur.x, self.joueur.y, cause)
        
        # Mise à jour immédiate des morts sur le dashboard
        self.dashboard.mettre_a_jour_stats(morts=len(self.logger.morts) if self.logger else 0)
        
        # Relancer la tentative (cela incrémentera le compteur)
        self._reinitialiser_tentative()
        
        self.dashboard.definir_logs(self.logger.obtenir_logs_recents() if self.logger else [])

    def _gerer_victoire(self):
        """Gère la victoire de l'IA."""
        if self.logger:
            self.logger.enregistrer_victoire()
        
        self.en_cours = False
        self.dashboard.mettre_a_jour_stats(victoire=True)
        self.dashboard.definir_logs(self.logger.obtenir_logs_recents() if self.logger else [])
        self.dashboard.ajouter_log("🏆 L'IA a terminé le niveau !")

    def _evaluer_avec_ollama(self):
        """Lance l'évaluation du niveau via Ollama."""
        if not self.logger or not self.donnees_niveau_actuel:
            self.dashboard.ajouter_log("⚠️ Pas de données à évaluer")
            return

        resume = self.logger.obtenir_resume()
        self.dashboard.statut_ollama = "⏳ Évaluation en cours..."
        self.dashboard.ajouter_log("🧠 Envoi à Ollama (Format Court)...")

        def callback(reponse):
            self.dashboard.reponse_ollama = reponse
            self.dashboard.statut_ollama = self.ollama.obtenir_statut()
            self.dashboard.scroll_ollama = 0
            self.dashboard.popup_scroll = 0  # Remet en haut
            self.dashboard.popup_active = True  # OUVRE LA FENÊTRE CENTRALE
            self.dashboard.ajouter_log("✅ Réponse reçue et archivée !")
            
            # Archivage automatique
            if self.logger:
                filepath = self.logger.sauvegarder_archive(reponse)
                print(f"Archive sauvegardée : {filepath}")

        self.ollama.evaluer_niveau(
            self.donnees_niveau_actuel, 
            resume, 
            callback, 
            log_callback=self.dashboard.ajouter_log
        )

    def _tester_com_ollama(self):
        """Lance un simple test de ping-pong avec Ollama."""
        self.dashboard.statut_ollama = "⏳ Test en cours..."
        self.dashboard.ajouter_log("🧪 Envoi du test de communication...")
        self.dashboard.reponse_ollama = ""

        def callback(reponse):
            self.dashboard.reponse_ollama = reponse
            self.dashboard.statut_ollama = self.ollama.obtenir_statut()
            self.dashboard.scroll_ollama = 0
            self.dashboard.popup_active = True  # Affiche le résultat du test
            self.dashboard.ajouter_log("✅ Réponse du test reçue !")

        # Utilisation du flag TEST reconnu par ollama_client
        self.ollama.evaluer_niveau(
            {"name": "TEST"}, 
            {}, 
            callback, 
            log_callback=self.dashboard.ajouter_log
        )

    def _niveau_suivant(self):
        """Passe au niveau suivant."""
        ids = self.level_manager.get_all_levels_ids()
        try:
            idx = ids.index(self.niveau_actuel_id)
            if idx < len(ids) - 1:
                self.niveau_actuel_id = ids[idx + 1]
            else:
                self.dashboard.ajouter_log("🎉 Dernier niveau atteint !")
                return
        except ValueError:
            self.niveau_actuel_id = ids[0] if ids else 1

        self.en_cours = False
        self._charger_niveau(self.niveau_actuel_id)
        self.dashboard.reponse_ollama = ""
        self.dashboard.ajouter_log(f"⏭ Passage au niveau {self.niveau_actuel_id}")

    def gerer_evenements(self):
        """Gère tous les événements Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

            # Événements du dashboard
            action = self.dashboard.gerer_evenement(event)
            if action == "lancer":
                self._demarrer()
            elif action == "pause":
                self.en_pause = self.dashboard.en_pause
            elif action == "evaluer":
                self._evaluer_avec_ollama()
            elif action == "test_com":
                self._tester_com_ollama()
            elif action == "suivant":
                self._niveau_suivant()
            elif action == "reinitialiser":
                self.en_cours = False
                self._charger_niveau(self.niveau_actuel_id)
                self.dashboard.ajouter_log("🔄 Niveau réinitialisé")
            elif action and action.startswith("LOAD_LEVEL_"):
                lvl_id = int(action.split("_")[-1])
                self.en_cours = False
                self._charger_niveau(lvl_id)
                self.dashboard.ajouter_log(f"📂 Chargement direct du niveau {lvl_id}")
            elif action == "nouvelle_serie":
                self.en_cours = False
                self._generer_nouvelle_serie()
                self._charger_niveau(200)
                self.dashboard.ajouter_log("✨ Nouvelle série prête !")

        return True

    def mettre_a_jour_logique(self):
        """Met à jour la logique de jeu selon la vitesse réglée."""
        if not self.en_cours or self.en_pause or not self.agent or not self.joueur:
            return

        # Récupérer la vitesse du dashboard
        vitesse = self.dashboard.obtenir_vitesse_jeu()
        
        # Accumuler le temps écoulé (proportionnel à la vitesse)
        self.accumulateur_vitesse += vitesse
        
        # Exécuter autant de steps de logique que nécessaire
        # Si vitesse < 1, on ne fera pas un step à chaque frame.
        # Si vitesse > 1, on fera plusieurs steps par frame.
        while self.accumulateur_vitesse >= 1.0:
            self._step_logique()
            self.accumulateur_vitesse -= 1.0

    def _step_logique(self):
        """Un seul step de logique de jeu."""
        if not self.en_cours or not self.joueur:
            return

        # 1. L'agent IA décide de la direction
        dx, dy = self.agent.mettre_a_jour(self.mobs, self.projectiles)
        
        # 2. Déplacer le joueur (comme un humain)
        if dx != 0 or dy != 0:
            self.joueur.move(dx, dy)

        # 3. Mettre à jour les mobs (avec vitesse globale)
        for mob in self.mobs:
            spawn = mob.update(player_pos=(self.joueur.x, self.joueur.y))
            if spawn:
                self.projectiles.append(spawn)
            
            # Collision mob direct
            if mob.collides_with(self.joueur):
                self._gerer_mort("Collision avec mob")
                return

        # 4. Mettre à jour les projectiles
        for p in self.projectiles[:]:
            p.update()
            if not p.alive:
                self.projectiles.remove(p)
            elif p.collides_with(self.joueur):
                self.projectiles.remove(p)
                self._handle_player_death_logic("Touché par un projectile")
                return

        # 5. Vérifier victoire
        if self.joueur.is_at(self.niveau.exit_x, self.niveau.exit_y):
            self._gerer_victoire()
            return

        # 6. Enregistrer la position
        if self.logger:
            self.logger.enregistrer_position(self.joueur.x, self.joueur.y)

        # 7. Mettre à jour les stats du dashboard
        temps_ecoule = time.time() - self.temps_debut_tentative if self.temps_debut_tentative else 0
        self.dashboard.mettre_a_jour_stats(
            tentative=self.logger.tentative if self.logger else 1,
            temps=temps_ecoule,
            distance=self.logger.distance_tentative if self.logger else 0
        )

    def _handle_player_death_logic(self, cause):
        """Gère la mort du joueur dans la boucle de logique."""
        self._gerer_mort(cause)

    def dessiner(self):
        """Dessine tout l'écran."""
        self.screen.fill(COULEURS_DASH["fond"])

        # Zone jeu (gauche)
        if self.game_renderer and self.joueur:
            self.game_renderer.dessiner_jeu_ia(
                self.joueur, self.mobs, self.projectiles,
                self.agent.obtenir_chemin_actuel() if self.agent else []
            )

        # Dashboard (droite)
        self.dashboard.dessiner(self.screen)

        pygame.display.flip()

    def boucle_principale(self):
        """Boucle principale du système."""
        en_cours = True
        while en_cours:
            en_cours = self.gerer_evenements()
            self.mettre_a_jour_logique()
            self.dessiner()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


class GameRendererIA(GameRenderer):
    """Renderer adapté à la vue splittée (moitié gauche de l'écran).
    
    Ajoute le rendu du chemin planifié par l'IA et une couleur spéciale pour le joueur.
    """

    def __init__(self, screen, font_manager, level, largeur_max):
        self.screen = screen
        self.fonts = font_manager
        self.level = level
        self.largeur_max = largeur_max
        self._calculate_offsets_ia()

    def _calculate_offsets_ia(self):
        """Calcule les offsets pour centrer le labyrinthe dans la moitié gauche."""
        maze_width, maze_height = self.level.get_pixel_dimensions()
        self.offset_x = (self.largeur_max - maze_width) // 2
        self.offset_y = (self.screen.get_height() - maze_height) // 2
        # S'assurer que c'est dans la zone gauche
        self.offset_x = max(10, min(self.offset_x, self.largeur_max - maze_width - 10))

    def dessiner_chemin_ia(self, chemin):
        """Dessine le chemin planifié par l'IA (semi-transparent)."""
        if not chemin:
            return
        for i, (cx, cy) in enumerate(chemin):
            rect = pygame.Rect(
                self.offset_x + cx * TILE_SIZE + TILE_SIZE // 4,
                self.offset_y + cy * TILE_SIZE + TILE_SIZE // 4,
                TILE_SIZE // 2,
                TILE_SIZE // 2
            )
            # Dégradé : début = cyan vif, fin = cyan sombre
            alpha = max(30, 150 - i * 5)
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            surface.fill((0, 255, 255, alpha))
            self.screen.blit(surface, rect)

    def dessiner_joueur_ia(self, player):
        """Dessine le joueur IA avec une couleur distinctive (cyan pulsant)."""
        pos_x, pos_y = player.get_pixel_position(self.offset_x, self.offset_y)
        player_rect = pygame.Rect(pos_x + 5, pos_y + 5, TILE_SIZE - 10, TILE_SIZE - 10)
        
        # Couleur pulsante
        pulse = abs(int(pygame.time.get_ticks() / 5) % 200 - 100)
        couleur = (0, 155 + pulse, 255)
        
        pygame.draw.rect(self.screen, couleur, player_rect, border_radius=8)
        
        # Indicateur "IA"
        font = pygame.font.Font(None, 18)
        txt = font.render("IA", True, (0, 0, 0))
        txt_rect = txt.get_rect(center=player_rect.center)
        self.screen.blit(txt, txt_rect)

    def dessiner_jeu_ia(self, player, mobs, projectiles, chemin_ia):
        """Rendu complet d'une frame avec le chemin de l'IA."""
        # Fond de la zone jeu seulement
        zone_jeu = pygame.Rect(0, 0, self.largeur_max, self.screen.get_height())
        pygame.draw.rect(self.screen, COLORS["bg"], zone_jeu)

        self.draw_maze()
        self.draw_exit()
        self.dessiner_chemin_ia(chemin_ia)
        self.draw_mobs(mobs)
        self.draw_projectiles(projectiles)
        self.dessiner_joueur_ia(player)

        # Info en haut
        font = pygame.font.Font(None, 24)
        info = font.render(
            f"Niveau {self.level.id} — {self.level.name}",
            True, COULEURS_DASH["titre"]
        )
        self.screen.blit(info, (15, 15))


# === Point d'entrée ===
if __name__ == "__main__":
    controleur = ControleurIA()
    controleur.boucle_principale()
