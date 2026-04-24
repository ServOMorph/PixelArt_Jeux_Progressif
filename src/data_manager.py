import json
import os

class DataManager:
    """Gere la persistance des donnees des joueurs."""
    
    FILE_PATH = "stats.json"

    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        """Charge les donnees depuis le fichier JSON."""
        if os.path.exists(self.FILE_PATH):
            try:
                with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur chargement stats: {e}")
                return {}
        return {}

    def _save_data(self):
        """Sauvegarde les donnees dans le fichier JSON."""
        try:
            with open(self.FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde stats: {e}")

    def get_player_stats(self, pseudo):
        """Retourne les stats d'un joueur ou en cree de nouvelles."""
        if pseudo not in self.data:
            self.data[pseudo] = {
                "levels_completed": 0,
                "deaths": 0,
                "time_played": 0,
                "best_level": 0
            }
            self._save_data()
        return self.data[pseudo]

    def update_stats(self, pseudo, deaths=0, level_won=None):
        """Met a jour les stats d'un joueur."""
        stats = self.get_player_stats(pseudo)
        stats["deaths"] += deaths
        if level_won:
            stats["levels_completed"] = max(stats["levels_completed"], level_won)
            stats["best_level"] = max(stats["best_level"], level_won)
        self._save_data()

    def load_custom_levels(self):
        """Charge les niveaux personnalisés."""
        path = os.path.join("levels", "custom_levels.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur chargement niveaux perso: {e}")
                return []
        return []

    def save_custom_levels(self, levels):
        """Sauvegarde les niveaux personnalisés."""
        path = os.path.join("levels", "custom_levels.json")
        if not os.path.exists("levels"):
            os.makedirs("levels")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(levels, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde niveaux perso: {e}")
