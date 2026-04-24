# Commande /close - Cloture de session

Analyse la conversation, met à jour la documentation et crée un commit.

## Instructions

Tu dois effectuer les actions suivantes dans l'ordre :

### 1. Analyse de la session

Parcourir toute la conversation pour identifier :
- Les tâches accomplies
- Les fichiers créés ou modifiés
- Les décisions prises
- Les problèmes résolus
- Les points en suspens

### 2. Mise à jour de la ROADMAP

Modifier `docs/ROADMAP.md` (s'il existe) pour :
- Cocher les tâches terminées (ajouter le marqueur approprié)
- Mettre à jour les statuts des phases
- Ajouter les nouvelles tâches identifiées
- Noter la date de dernière mise à jour

### 3. Mise à jour du README et de la MAP

Modifier `README.md` (s'il existe) pour :
- Refléter l'état actuel du projet
- Ajouter les nouvelles fonctionnalités implémentées
- Mettre à jour les instructions d'installation si nécessaire
- Créer le fichier s'il n'existe pas avec une structure de base
 
Modifier `docs/MAP.md` pour :
- Ajouter tout nouveau fichier créé.
- Mettre à jour la description des fichiers si leur rôle a changé.
- S'assurer que l'arborescence technique est fidèle à la réalité.

**Optionnel** : Si des changements structurels majeurs ont eu lieu, exécuter la commande `COMMANDS/optimize_docs.md` pour re-standardiser l'ensemble. *À utiliser avec parcimonie pour économiser les tokens.*

### 4. Extraire et stocker les apprentissages 📚

**Systeme centralise** : `C:\Users\raph6\Documents\ServOMorph\Agents_IA_V2\.claude\learnings\`

Analyser la conversation pour detecter :
- Fichiers modifies plusieurs fois (iterations)
- Erreurs explicites suivies de corrections
- Patterns "essai → echec → succes"

Stocker les apprentissages :
```bash
# Sauvegarder conversation dans fichier temporaire
# Appeler le gestionnaire
python C:\Users\raph6\Documents\ServOMorph\Agents_IA_V2\.claude\learnings\learning_manager.py analyze "[fichier_conversation]" "[NomProjet]"
```

Afficher le nombre d'apprentissages enregistres.

### 5. Création du commit

Exécuter les commandes git :
```bash
git add .
git status
```

Puis créer un commit avec un message descriptif au format :
```
[type]: description courte

- Détail des changements 1
- Détail des changements 2

🤖 Generated with Claude Code
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types de commit :
- `feat` : nouvelle fonctionnalité
- `fix` : correction de bug
- `docs` : documentation uniquement
- `refactor` : refactorisation
- `test` : ajout de tests
- `chore` : maintenance

### 6. Rapport de clôture

Présenter un résumé :

```
## Session terminée

**Durée estimée** : [basé sur les échanges]
**Fichiers modifiés** : [nombre]

### Accompli
- [liste des réalisations]

### En suspens
- [liste des tâches restantes]

### Prochain démarrage
- [suggestions pour la prochaine session]
```
