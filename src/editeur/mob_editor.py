# -*- coding: utf-8 -*-
import pygame
from config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT

class MobEditorModal:
    """Gère l'interface de modification des paramètres d'un Mob spécifique."""
    
    def __init__(self, editor):
        self.editor = editor
        self.rect = pygame.Rect(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 200, 500, 400)
        self.visible = False
        self.target_mob = None # Référence au dict du mob dans editor.mobs
        
        # Définition des zones cliquables
        self.close_rect = pygame.Rect(self.rect.right - 40, self.rect.y + 10, 30, 30)
        self.pattern_btn_rect = pygame.Rect(self.rect.x + 50, self.rect.y + 100, 400, 50)
        self.speed_minus_rect = pygame.Rect(self.rect.x + 50, self.rect.y + 200, 50, 50)
        self.speed_plus_rect = pygame.Rect(self.rect.right - 100, self.rect.y + 200, 50, 50)
        self.dist_minus_rect = pygame.Rect(self.rect.x + 50, self.rect.y + 300, 50, 50)
        self.dist_plus_rect = pygame.Rect(self.rect.right - 100, self.rect.y + 300, 50, 50)

    def open(self, mob_data):
        self.target_mob = mob_data
        self.visible = True

    def close(self):
        self.visible = False
        self.target_mob = None

    def handle_events(self, event):
        if not self.visible or not self.target_mob:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            if self.close_rect.collidepoint(mx, my):
                self.close()
                return True
                
            # Changement de Pattern
            if self.pattern_btn_rect.collidepoint(mx, my):
                patterns = ["horizontal", "vertical", "chaser", "shooter"]
                curr_idx = patterns.index(self.target_mob["pattern"])
                self.target_mob["pattern"] = patterns[(curr_idx + 1) % len(patterns)]
                # Reset defaults
                if self.target_mob["pattern"] == "chaser":
                    self.target_mob["speed"] = 0.04
                elif self.target_mob["pattern"] == "shooter":
                    self.target_mob["speed"] = 0.08
                    self.target_mob["distance"] = 120 # On utilise distance pour le délai de tir
                else:
                    self.target_mob["speed"] = 0.08
                    self.target_mob["distance"] = 4
                return True

            # Vitesse
            if self.speed_minus_rect.collidepoint(mx, my):
                self.target_mob["speed"] = max(0.01, round(self.target_mob["speed"] - 0.01, 2))
                return True
            if self.speed_plus_rect.collidepoint(mx, my):
                self.target_mob["speed"] = min(0.3, round(self.target_mob["speed"] + 0.01, 2))
                return True

            # Distance (seulement si patrol)
            if self.target_mob["pattern"] != "chaser":
                if self.dist_minus_rect.collidepoint(mx, my):
                    self.target_mob["distance"] = max(1, self.target_mob.get("distance", 3) - 1)
                    return True
                if self.dist_plus_rect.collidepoint(mx, my):
                    self.target_mob["distance"] = min(15, self.target_mob.get("distance", 3) + 1)
                    return True

        return False

    def draw(self, screen, fonts):
        if not self.visible or not self.target_mob:
            return

        # Overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Fenêtre
        pygame.draw.rect(screen, (30, 30, 50), self.rect, border_radius=10)
        pygame.draw.rect(screen, COLORS["player"], self.rect, 2, border_radius=10)

        # Titre
        title = fonts.get('medium').render("RÉGLAGES MOB", True, COLORS["white"])
        screen.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 20))
        
        # Bouton fermer
        pygame.draw.rect(screen, (150, 0, 0), self.close_rect, border_radius=5)
        pygame.draw.line(screen, COLORS["white"], (self.close_rect.x+5, self.close_rect.y+5), (self.close_rect.right-5, self.close_rect.bottom-5), 2)
        pygame.draw.line(screen, COLORS["white"], (self.close_rect.right-5, self.close_rect.y+5), (self.close_rect.x+5, self.close_rect.bottom-5), 2)

        # 1. Pattern
        pygame.draw.rect(screen, (60, 60, 90), self.pattern_btn_rect, border_radius=5)
        p_text = fonts.get('small').render(f"Type: {self.target_mob['pattern'].upper()}", True, COLORS["white"])
        screen.blit(p_text, (self.pattern_btn_rect.centerx - p_text.get_width() // 2, self.pattern_btn_rect.centery - p_text.get_height() // 2))

        # 2. Vitesse
        v_label = fonts.get('small').render(f"Vitesse: {self.target_mob['speed']}", True, COLORS["white"])
        screen.blit(v_label, (self.rect.centerx - v_label.get_width() // 2, self.rect.y + 160))
        
        for r, t in [(self.speed_minus_rect, "-"), (self.speed_plus_rect, "+")]:
            pygame.draw.rect(screen, (80, 80, 100), r, border_radius=5)
            txt = fonts.get('medium').render(t, True, COLORS["white"])
            screen.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

        # 3. Distance / Délai
        if self.target_mob["pattern"] != "chaser":
            label = "Délai (frames):" if self.target_mob["pattern"] == "shooter" else "Distance:"
            d_label = fonts.get('small').render(f"{label} {self.target_mob.get('distance', 3)}", True, COLORS["white"])
            screen.blit(d_label, (self.rect.centerx - d_label.get_width() // 2, self.rect.y + 260))
            
            for r, t in [(self.dist_minus_rect, "-"), (self.dist_plus_rect, "+")]:
                pygame.draw.rect(screen, (80, 80, 100), r, border_radius=5)
                txt = fonts.get('medium').render(t, True, COLORS["white"])
                screen.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))
        else:
            msg = fonts.get('controls').render("(Poursuit le joueur en continu)", True, (150, 150, 150))
            screen.blit(msg, (self.rect.centerx - msg.get_width() // 2, self.rect.y + 300))
