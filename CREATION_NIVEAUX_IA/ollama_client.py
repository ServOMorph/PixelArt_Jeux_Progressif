# -*- coding: utf-8 -*-
"""
Client Ollama — Communication avec le modèle IA local pour évaluation de niveaux.
Utilise l'API REST de Ollama sur localhost:11434.
"""
import json
import urllib.request
import urllib.error
import threading


# Modèle Ollama sélectionné (Plus rapide : llama3.2, Plus puissant : qwen3.5)
MODELE_OLLAMA = "llama3.2:latest"
# Utilisation de 127.0.0.1 au lieu de localhost pour plus de stabilité sur Windows
URL_OLLAMA = "http://127.0.0.1:11434/api/generate"


class ClientOllama:
    """Client pour communiquer avec Ollama en local."""

    def __init__(self, modele=MODELE_OLLAMA):
        self.modele = modele
        self.derniere_reponse = None
        self.en_cours = False
        self.erreur = None
        self.statut = "💤 En attente"

    def est_disponible(self):
        """Vérifie si Ollama est en cours d'exécution."""
        try:
            req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def evaluer_niveau(self, donnees_niveau, resume_session, callback, log_callback=None):
        """Lance l'évaluation d'un niveau en arrière-plan."""
        # On ne bloque plus si c'est un test de com
        if self.en_cours and donnees_niveau.get("name") != "TEST":
            if log_callback: log_callback("⚠️ Une évaluation est déjà en cours...")
            return

        def worker():
            try:
                self.en_cours = True
                self.erreur = None
                
                if log_callback: log_callback("📡 Préparation des données...")
                prompt = self._construire_prompt_evaluation(donnees_niveau, resume_session)
                
                if log_callback: log_callback(f"🧠 Ollama ({self.modele}) réfléchit...")
                self.statut = "🤔 Réflexion..."
                
                reponse = self._appeler_ollama(prompt)
                
                if log_callback: log_callback("📥 Réponse reçue, traitement...")
                self.derniere_reponse = reponse
                self.statut = "✅ Terminé"
                
                if log_callback: log_callback("✨ Évaluation terminée avec succès !")
                if callback:
                    callback(reponse)
                
            except Exception as e:
                self.erreur = str(e)
                self.statut = "❌ Erreur"
                if log_callback: log_callback(f"❌ Erreur Ollama : {str(e)[:50]}...")
                if callback:
                    callback(f"Erreur lors de l'évaluation : {e}")
            finally:
                self.en_cours = False

        threading.Thread(target=worker, daemon=True).start()

    def _construire_prompt_evaluation(self, donnees_niveau, resume):
        """Construit le prompt structuré pour l'évaluation."""
        # MODE TEST SIMPLIFIÉ
        if donnees_niveau.get("name") == "TEST":
            return "Bonjour Ollama, ceci est un test de communication. Réponds simplement 'OK, je suis prêt !' si tu reçois ce message."

        # Convertir le maze en représentation lisible
        maze_texte = self._maze_vers_texte(donnees_niveau.get("maze", []))
        
        # Infos mobs
        mobs_texte = ""
        for m in donnees_niveau.get("mobs", []):
            pos = m.get("start_pos", [0, 0])
            pattern = m.get("pattern", "?")
            mobs_texte += f"  - {pattern} en ({pos[0]},{pos[1]})\n"

        prompt = f"""Expert Game Design. Analyse ce niveau Pixel Art :
ID:{donnees_niveau.get('id')} Name:{donnees_niveau.get('name')}
Start:{donnees_niveau.get('start_pos')} Exit:{donnees_niveau.get('exit_pos')}
Grid (0:path, 1:wall, 2:tree):
{maze_texte}
Mobs: {mobs_texte if mobs_texte else 'None'}
Stats: {resume.get('tentatives')} tries, {resume.get('morts_total')} deaths, Win:{resume.get('victoire')}
Deaths types: {json.dumps(resume.get('causes_de_mort', {}), ensure_ascii=False)}
Hotspots: {json.dumps(resume.get('zones_danger', {}), ensure_ascii=False)}

Réponds en FR, format :
**Scores**: Fun X/10, Diff X/10, Bal X/10
**Points +/-**: ...
**Actions**: 1. 2. 3.
"""
        return prompt

    def _maze_vers_texte(self, maze):
        """Version compacte de la grille."""
        return "\n".join(" ".join(str(c) for c in row) for row in maze)

    def _appeler_ollama(self, prompt):
        """Appel synchrone à l'API Ollama."""
        donnees = json.dumps({
            "model": self.modele,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_ctx": 8192,
                "num_predict": 768,
                "top_k": 40,
                "top_p": 0.9
            }
        }).encode("utf-8")

        req = urllib.request.Request(
            URL_OLLAMA,
            data=donnees,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                corps_reponse = resp.read().decode("utf-8")
                resultat = json.loads(corps_reponse)
                return resultat.get("response", "Pas de réponse")
        except urllib.error.URLError as e:
            raise ConnectionError(f"Ollama indisponible : {e}")
        except Exception as e:
            raise RuntimeError(f"Erreur Ollama : {e}")

    def obtenir_statut(self):
        """Retourne le statut actuel pour l'affichage dashboard."""
        return self.statut
