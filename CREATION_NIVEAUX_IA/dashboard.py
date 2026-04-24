# -*- coding: utf-8 -*-
"""
Dashboard — Tableau de commande Pygame pour suivre l'IA en temps réel.
Panneau à droite de l'écran avec stats, logs, boutons et zone Ollama.
"""
import pygame


# Couleurs du dashboard
COULEURS_DASH = {
    "fond":         (15, 15, 25),
    "panneau":      (25, 25, 40),
    "bordure":      (60, 60, 100),
    "titre":        (0, 255, 255),
    "texte":        (200, 200, 220),
    "texte_dim":    (120, 120, 150),
    "succes":       (0, 255, 100),
    "erreur":       (255, 80, 80),
    "warning":      (255, 200, 0),
    "bouton":       (40, 40, 70),
    "bouton_hover": (60, 60, 100),
    "bouton_actif": (0, 200, 200),
    "chemin_ia":    (0, 255, 255, 80),
    "joueur_ia":    (0, 255, 255),
    "slider_fond":  (40, 40, 60),
    "slider_fill":  (0, 180, 200),
    "slider_knob":  (255, 255, 255),
}


class Bouton:
    """Bouton cliquable pour le dashboard."""

    def __init__(self, x, y, largeur, hauteur, texte, action):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.action = action
        self.survol = False
        self.actif = False

    def dessiner(self, surface, police):
        """Dessine le bouton."""
        if self.actif:
            couleur = COULEURS_DASH["bouton_actif"]
        elif self.survol:
            couleur = COULEURS_DASH["bouton_hover"]
        else:
            couleur = COULEURS_DASH["bouton"]

        pygame.draw.rect(surface, couleur, self.rect, border_radius=6)
        pygame.draw.rect(surface, COULEURS_DASH["bordure"], self.rect, 1, border_radius=6)

        txt = police.render(self.texte, True, COULEURS_DASH["texte"])
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)

    def verifier_survol(self, pos_souris):
        """Met à jour l'état de survol."""
        self.survol = self.rect.collidepoint(pos_souris)
        return self.survol

    def verifier_clic(self, pos_souris):
        """Vérifie si le bouton est cliqué."""
        return self.rect.collidepoint(pos_souris)


class SliderVitesse:
    """Slider pour contrôler la vitesse de jeu."""

    def __init__(self, x, y, largeur, hauteur):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.valeur = 1.0  # Multiplicateur de vitesse (0.5 à 10.0)
        self.min_val = 0.5
        self.max_val = 10.0
        self.en_train_de_glisser = False
        self.etapes = [0.5, 1.0, 2.0, 4.0, 6.0, 10.0]  # Paliers prédéfinis
        self.index_etape = 1  # Commence à x1

    def dessiner(self, surface, police):
        """Dessine le slider."""
        # Fond
        pygame.draw.rect(surface, COULEURS_DASH["slider_fond"], self.rect, border_radius=4)
        
        # Barre de remplissage
        ratio = (self.valeur - self.min_val) / (self.max_val - self.min_val)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, int(self.rect.width * ratio), self.rect.height)
        pygame.draw.rect(surface, COULEURS_DASH["slider_fill"], fill_rect, border_radius=4)
        
        # Curseur
        knob_x = self.rect.x + int(self.rect.width * ratio)
        pygame.draw.circle(surface, COULEURS_DASH["slider_knob"], (knob_x, self.rect.centery), 8)
        
        # Texte
        txt = police.render(f"Vitesse: x{self.valeur:.1f}", True, COULEURS_DASH["titre"])
        surface.blit(txt, (self.rect.x, self.rect.y - 20))

    def gerer_clic(self, pos):
        """Gère un clic sur le slider."""
        if self.rect.collidepoint(pos):
            self._mettre_a_jour_depuis_position(pos[0])
            self.en_train_de_glisser = True
            return True
        return False

    def gerer_glissement(self, pos):
        """Gère le glissement continu."""
        if self.en_train_de_glisser:
            self._mettre_a_jour_depuis_position(pos[0])

    def arreter_glissement(self):
        """Arrête le glissement."""
        self.en_train_de_glisser = False

    def _mettre_a_jour_depuis_position(self, x):
        """Met à jour la valeur depuis la position x de la souris."""
        ratio = max(0, min(1, (x - self.rect.x) / self.rect.width))
        self.valeur = round(self.min_val + ratio * (self.max_val - self.min_val), 1)
        # Snapper sur le palier le plus proche
        plus_proche = min(self.etapes, key=lambda v: abs(v - self.valeur))
        if abs(self.valeur - plus_proche) < 0.5:
            self.valeur = plus_proche


class Dashboard:
    """Tableau de commande principal — panneau droit de l'écran."""

    def __init__(self, x_debut, largeur, hauteur):
        """
        Args:
            x_debut: Position X où commence le panneau (fin de la zone jeu)
            largeur: Largeur du panneau
            hauteur: Hauteur totale de l'écran
        """
        self.x = x_debut
        self.largeur = largeur
        self.hauteur = hauteur
        self.marge = 15
        
        # Polices
        self.police_titre = pygame.font.Font(None, 32)
        self.police_texte = pygame.font.Font(None, 22)
        self.police_petit = pygame.font.Font(None, 18)
        self.police_bouton = pygame.font.Font(None, 24)

        # Boutons
        bx = self.x + self.marge
        bw = (self.largeur - self.marge * 3) // 2
        self.boutons = {
            "lancer": Bouton(bx, 80, bw, 35, "▶ Lancer", "lancer"),
            "pause": Bouton(bx + bw + self.marge, 80, bw, 35, "⏸ Pause", "pause"),
            "evaluer": Bouton(bx, 125, bw, 35, "🧠 Évaluer", "evaluer"),
            "test_com": Bouton(bx + bw + self.marge, 125, bw, 35, "📡 Test Com", "test_com"),
            "suivant": Bouton(bx, 170, bw, 35, "⏭ Suivant", "suivant"),
            "reinitialiser": Bouton(bx + bw + self.marge, 170, bw, 35, "🔄 Reset", "reinitialiser"),
            "nouvelle_serie": Bouton(bx, 215, self.largeur - self.marge * 2, 35, "🛠️ Générer nouvelle série", "nouvelle_serie"),
        }

        # Slider de vitesse
        self.slider = SliderVitesse(bx, 295, self.largeur - self.marge * 2, 16)

        # État
        self.logs = []
        self.statut_ollama = "💤 En attente"
        self.reponse_ollama = ""
        self.scroll_ollama = 0
        self.en_pause = False
        self.niveaux_disponibles = []
        self.rects_niveaux = {}  # {id: Rect}
        self.taille_serie = 10   # Valeur dynamique par défaut

        # Fenêtre Pop-up
        self.popup_active = False
        self.popup_rect = pygame.Rect(200, 100, 1000, 800)
        self.popup_bouton_fermer = pygame.Rect(650, 820, 100, 40)
        self.popup_scroll = 0

        # Stats
        self.stats = {
            "tentative": 0,
            "morts": 0,
            "temps": 0.0,
            "distance": 0.0,
            "niveau_id": 0,
            "niveau_nom": "",
            "victoire": False,
        }

    def mettre_a_jour_stats(self, **kwargs):
        """Met à jour les statistiques affichées."""
        for cle, val in kwargs.items():
            if cle in self.stats:
                self.stats[cle] = val

    def ajouter_log(self, texte):
        """Ajoute une ligne de log."""
        self.logs.append(texte)
        # Garder les 50 derniers
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]

    def definir_logs(self, liste_logs):
        """Remplace les logs par une nouvelle liste."""
        self.logs = list(liste_logs)

    def definir_niveaux(self, liste_ids):
        """Définit la liste des niveaux affichés dans le sélecteur."""
        self.niveaux_disponibles = liste_ids

    def gerer_evenement(self, event):
        """Gère les événements du dashboard. Retourne l'action ou None."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Clic sur les boutons de taille de série
            if hasattr(self, 'rect_plus') and self.rect_plus.collidepoint(pos):
                self.taille_serie = min(50, self.taille_serie + 5)
                return None
            if hasattr(self, 'rect_moins') and self.rect_moins.collidepoint(pos):
                self.taille_serie = max(5, self.taille_serie - 5)
                return None

            # Clic sur bouton fermer popup
            if self.popup_active and self.popup_bouton_fermer.collidepoint(pos):
                self.popup_active = False
                return None
                
            # Si popup active, on bloque le reste des clics du dashboard
            if self.popup_active:
                return None

            # Slider
            if self.slider.gerer_clic(pos):
                return None
            
            # Clic sur un niveau
            for lvl_id, rect in self.rects_niveaux.items():
                if rect.collidepoint(pos):
                    return f"LOAD_LEVEL_{lvl_id}"
            
            # Boutons
            for nom, bouton in self.boutons.items():
                if bouton.verifier_clic(pos):
                    if nom == "pause":
                        self.en_pause = not self.en_pause
                        bouton.actif = self.en_pause
                        bouton.texte = "▶ Reprendre" if self.en_pause else "⏸ Pause"
                    return bouton.action

        elif event.type == pygame.MOUSEBUTTONUP:
            self.slider.arreter_glissement()

        elif event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.slider.gerer_glissement(pos)
            for bouton in self.boutons.values():
                bouton.verifier_survol(pos)

        elif event.type == pygame.MOUSEWHEEL:
            # Scroll de la zone Ollama ou de la popup
            if event.y:
                if self.popup_active:
                    self.popup_scroll = max(0, self.popup_scroll - event.y * 25)
                else:
                    self.scroll_ollama = max(0, self.scroll_ollama - event.y * 20)

        return None

    def dessiner(self, surface):
        """Dessine le panneau complet."""
        # Fond du panneau
        panneau_rect = pygame.Rect(self.x, 0, self.largeur, self.hauteur)
        pygame.draw.rect(surface, COULEURS_DASH["panneau"], panneau_rect)
        pygame.draw.line(surface, COULEURS_DASH["bordure"], (self.x, 0), (self.x, self.hauteur), 2)

        # Titre
        titre = self.police_titre.render("🎮 Tableau de Commande IA", True, COULEURS_DASH["titre"])
        surface.blit(titre, (self.x + self.marge, 15))

        # Séparateur
        self._ligne_separateur(surface, 55)

        # Boutons
        for bouton in self.boutons.values():
            bouton.dessiner(surface, self.police_bouton)

        # Slider
        self.slider.dessiner(surface, self.police_petit)

        # Taille de la série
        self._dessiner_reglage_serie(surface, 258)

        # Section Sélecteur de Niveaux
        self._ligne_separateur(surface, 325)
        self._dessiner_selecteur_niveaux(surface, 340)

        # Section Stats
        self._ligne_separateur(surface, 480)
        self._dessiner_stats(surface, 495)

        # Section Logs
        self._ligne_separateur(surface, 640)
        self._dessiner_logs(surface, 655)

        # Section Ollama
        self._ligne_separateur(surface, 840)
        self._dessiner_ollama(surface, 855)

        # Fenêtre Pop-up (si active)
        if self.popup_active:
            self._dessiner_popup(surface)

    def _dessiner_popup(self, surface):
        """Dessine la fenêtre centrale d'analyse complète avec scroll."""
        # Overlay sombre
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Fenêtre
        pygame.draw.rect(surface, (30, 30, 50), self.popup_rect, border_radius=12)
        pygame.draw.rect(surface, COULEURS_DASH["bordure"], self.popup_rect, 2, border_radius=12)

        # Titre
        titre = self.police_titre.render("🔍 Analyse Complète de l'IA", True, COULEURS_DASH["titre"])
        surface.blit(titre, (self.popup_rect.x + 30, self.popup_rect.y + 25))

        # Découpage du texte avec retour à la ligne
        marge_interne = 40
        largeur_max = self.popup_rect.width - (marge_interne * 2) - 20
        y_base = self.popup_rect.y + 80
        
        # Préparer toutes les lignes (Word Wrap)
        lignes_finales = []
        paragraphes = self.reponse_ollama.split("\n")
        for p in paragraphes:
            if not p.strip():
                lignes_finales.append("")
                continue
            
            mots = p.split(' ')
            ligne_actuelle = ""
            for mot in mots:
                test_ligne = ligne_actuelle + (" " if ligne_actuelle else "") + mot
                if self.police_texte.size(test_ligne)[0] < largeur_max:
                    ligne_actuelle = test_ligne
                else:
                    lignes_finales.append(ligne_actuelle)
                    ligne_actuelle = mot
            lignes_finales.append(ligne_actuelle)

        # Affichage avec Scroll
        hauteur_ligne = 22
        max_visibles = (self.popup_rect.height - 150) // hauteur_ligne
        index_debut = self.popup_scroll // hauteur_ligne
        
        # Limiter le scroll
        max_scroll = max(0, (len(lignes_finales) - max_visibles) * hauteur_ligne)
        self.popup_scroll = min(self.popup_scroll, max_scroll)

        for i, ligne in enumerate(lignes_finales[index_debut : index_debut + max_visibles]):
            txt = self.police_texte.render(ligne, True, COULEURS_DASH["texte"])
            surface.blit(txt, (self.popup_rect.x + marge_interne, y_base + i * hauteur_ligne))

        # Dessiner un indicateur d'ascenseur (barre à droite) - PLUS VISIBLE
        if len(lignes_finales) > max_visibles:
            barre_x = self.popup_rect.right - 20
            barre_y_debut = y_base
            barre_hauteur = self.popup_rect.height - 180
            # Fond de la barre
            pygame.draw.rect(surface, (40, 40, 60), (barre_x, barre_y_debut, 10, barre_hauteur), border_radius=5)
            
            # Curseur (Cyan pour être bien vu)
            ratio_vis = max_visibles / len(lignes_finales)
            curseur_h = max(40, barre_hauteur * ratio_vis)
            ratio_scroll = self.popup_scroll / (max_scroll if max_scroll > 0 else 1)
            curseur_y = barre_y_debut + (barre_hauteur - curseur_h) * ratio_scroll
            pygame.draw.rect(surface, COULEURS_DASH["titre"], (barre_x, curseur_y, 10, curseur_h), border_radius=5)
            pygame.draw.rect(surface, (255, 255, 255), (barre_x, curseur_y, 10, curseur_h), 1, border_radius=5)

        # Bouton Fermer
        self.popup_bouton_fermer.centerx = self.popup_rect.centerx
        self.popup_bouton_fermer.bottom = self.popup_rect.bottom - 20
        pygame.draw.rect(surface, COULEURS_DASH["bouton"], self.popup_bouton_fermer, border_radius=6)
        pygame.draw.rect(surface, COULEURS_DASH["bordure"], self.popup_bouton_fermer, 1, border_radius=6)
        txt_fermer = self.police_bouton.render("Fermer", True, COULEURS_DASH["texte"])
        surface.blit(txt_fermer, txt_fermer.get_rect(center=self.popup_bouton_fermer.center))

    def _dessiner_reglage_serie(self, surface, y):
        """Dessine le petit sélecteur pour la taille de la série."""
        txt = self.police_petit.render(f"Taille série : {self.taille_serie}", True, COULEURS_DASH["texte"])
        surface.blit(txt, (self.x + self.marge, y))
        
        # Boutons + et -
        bw, bh = 25, 20
        self.rect_moins = pygame.Rect(self.x + self.marge + 120, y - 2, bw, bh)
        self.rect_plus = pygame.Rect(self.x + self.marge + 150, y - 2, bw, bh)
        
        for r, t in [(self.rect_moins, "-"), (self.rect_plus, "+")]:
            pygame.draw.rect(surface, COULEURS_DASH["bouton"], r, border_radius=3)
            pygame.draw.rect(surface, COULEURS_DASH["bordure"], r, 1, border_radius=3)
            char = self.police_petit.render(t, True, COULEURS_DASH["texte"])
            surface.blit(char, char.get_rect(center=r.center))

    def _ligne_separateur(self, surface, y):
        """Dessine une ligne de séparation."""
        pygame.draw.line(
            surface, COULEURS_DASH["bordure"],
            (self.x + self.marge, y), (self.x + self.largeur - self.marge, y), 1
        )

    def _dessiner_selecteur_niveaux(self, surface, y_debut):
        """Dessine une grille de badges pour sélectionner les niveaux."""
        titre = self.police_texte.render("📂 Niveaux Disponibles", True, COULEURS_DASH["titre"])
        surface.blit(titre, (self.x + self.marge, y_debut))

        y = y_debut + 35
        x_base = self.x + self.marge + 5
        taille_badge = 35
        espacement = 8
        colonnes = 10
        
        self.rects_niveaux = {}

        for i, lvl_id in enumerate(self.niveaux_disponibles):
            col = i % colonnes
            row = i // colonnes
            
            bx = x_base + col * (taille_badge + espacement)
            by = y + row * (taille_badge + espacement)
            
            rect = pygame.Rect(bx, by, taille_badge, taille_badge)
            self.rects_niveaux[lvl_id] = rect
            
            # Couleur badge : actif si c'est le niveau actuel
            est_actuel = (lvl_id == self.stats["niveau_id"])
            couleur = COULEURS_DASH["bouton_actif"] if est_actuel else COULEURS_DASH["bouton"]
            
            pygame.draw.rect(surface, couleur, rect, border_radius=4)
            if not est_actuel:
                pygame.draw.rect(surface, COULEURS_DASH["bordure"], rect, 1, border_radius=4)
            
            # Texte du badge (ID)
            txt = self.police_petit.render(str(lvl_id), True, COULEURS_DASH["texte"])
            txt_rect = txt.get_rect(center=rect.center)
            surface.blit(txt, txt_rect)

    def _dessiner_stats(self, surface, y_debut):
        """Dessine la section statistiques."""
        titre = self.police_texte.render("📊 Statistiques en direct", True, COULEURS_DASH["titre"])
        surface.blit(titre, (self.x + self.marge, y_debut))

        y = y_debut + 30
        espacement = 22

        infos = [
            f"Niveau : {self.stats['niveau_id']} — {self.stats['niveau_nom']}",
            f"Tentative : #{self.stats['tentative']}",
            f"Morts : {self.stats['morts']}",
            f"Temps : {self.stats['temps']:.1f}s",
            f"Distance : {self.stats['distance']:.1f} tuiles",
            f"Statut : {'🏆 Victoire !' if self.stats['victoire'] else '🎮 En cours...'}",
        ]

        for info in infos:
            couleur = COULEURS_DASH["succes"] if "Victoire" in info else COULEURS_DASH["texte"]
            txt = self.police_petit.render(info, True, couleur)
            surface.blit(txt, (self.x + self.marge + 10, y))
            y += espacement

    def _dessiner_logs(self, surface, y_debut):
        """Dessine la section des logs déroulants."""
        titre = self.police_texte.render("📋 Journal de l'IA", True, COULEURS_DASH["titre"])
        surface.blit(titre, (self.x + self.marge, y_debut))

        y = y_debut + 28
        # Afficher les 10 derniers logs
        logs_visibles = self.logs[-10:]
        for log in logs_visibles:
            # Troncature si trop long
            texte = log[:50] + "..." if len(log) > 50 else log
            couleur = COULEURS_DASH["texte_dim"]
            if "💀" in log:
                couleur = COULEURS_DASH["erreur"]
            elif "🏆" in log:
                couleur = COULEURS_DASH["succes"]
            elif "🔄" in log:
                couleur = COULEURS_DASH["warning"]
            
            txt = self.police_petit.render(texte, True, couleur)
            surface.blit(txt, (self.x + self.marge + 5, y))
            y += 18

    def _dessiner_ollama(self, surface, y_debut):
        """Dessine un aperçu rapide de l'évaluation dans le dashboard."""
        titre = self.police_texte.render("🧠 Évaluation Ollama", True, COULEURS_DASH["titre"])
        surface.blit(titre, (self.x + self.marge, y_debut))

        # Statut
        statut = self.police_petit.render(self.statut_ollama, True, COULEURS_DASH["warning"])
        surface.blit(statut, (self.x + self.marge + 10, y_debut + 28))

        # Aperçu très court (si pas de popup active)
        if self.reponse_ollama and not self.popup_active:
            y = y_debut + 52
            lignes = self.reponse_ollama.split("\n")
            # Juste les 3 premières lignes pour ne pas déborder
            for i, ligne in enumerate(lignes[:3]):
                texte = ligne[:45] + "..." if len(ligne) > 45 else ligne
                txt = self.police_petit.render(texte, True, COULEURS_DASH["texte_dim"])
                surface.blit(txt, (self.x + self.marge + 5, y + i * 18))
            
            # Note pour ouvrir
            note = self.police_petit.render("(Analyse complète disponible)", True, COULEURS_DASH["titre"])
            surface.blit(note, (self.x + self.marge + 5, y + 60))

    def obtenir_vitesse_jeu(self):
        """Retourne le multiplicateur de vitesse actuel."""
        return self.slider.valeur
