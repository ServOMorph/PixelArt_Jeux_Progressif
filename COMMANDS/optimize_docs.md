# Commande /optimize-docs - Standardisation de la Documentation

Cette commande permet de restructurer toute la documentation du projet pour une compréhension optimale par les IA (LLMs) tout en gardant une interface claire pour les humains.

## 🤖 Instructions pour l'IA

Tu dois parcourir l'intégralité du projet et appliquer les transformations suivantes :

### 1. Documentation Interne (Code Python)
Pour chaque fichier `.py`, assure-toi que :
- **Docstrings de Fichier** : Chaque fichier commence par un résumé clair de son rôle dans l'architecture globale.
- **Format Standard** : Utilise le format Google/Sphinx pour les docstrings (Arguments, Returns, Raises).
- **Typage Explicite** : Si le typage Python n'est pas présent, mentionne explicitement les types attendus dans les docstrings.
- **Commentaires de Logique** : Ajoute des commentaires sur les sections de code complexes pour expliquer le "pourquoi" et pas seulement le "comment".

### 2. Documentation Externe (READMEs)
Pour chaque `README.md` :
- **Structure Humaine** : Utilise des titres clairs, des listes à puces et des emojis pour la lisibilité.
- **Section "Context for AI"** : Ajoute une section cachée ou explicite au début ou à la fin contenant :
  - Un résumé technique ultra-dense.
  - La liste des dépendances critiques.
  - Les points d'entrée (entry points).
  - Les pièges connus (gotchas).

### 3. Arborescence
- Génère ou mets à jour un fichier `docs/MAP.md` qui représente l'arborescence complète avec une description d'une ligne pour chaque fichier.

## 🛠️ Exécution

1. **Scan** : Liste tous les fichiers sources.
2. **Analyse** : Compare la doc actuelle aux standards définis ci-dessus.
3. **Édition** : Applique les modifications fichier par fichier.
4. **Rapport** : Résume les changements effectués.

## 🎯 Objectif
Réduire le temps d'analyse de l'IA lors des prochaines sessions et éviter les erreurs d'interprétation sur la logique métier.
