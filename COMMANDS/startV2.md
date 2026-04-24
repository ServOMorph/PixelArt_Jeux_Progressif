# Commande /start - Analyse et suivi de la Roadmap

Analyse le projet pour démarrer une session de travail efficace.

## Instructions

Tu dois effectuer les actions suivantes dans l'ordre :

### 1. Lecture des documents clés
- Read `docs/ROADMAP.md` (if it exists) to understand phases, tasks and status.
- Read `docs/MAP.md` to get an instant overview of the project architecture.
- Read `README.md` (if it exists) to understand the global context.

### 2. Analyse de l'état actuel
- Identifier les tâches marquées "En cours" ou "À démarrer"
- Repérer les prochaines actions immédiates listées
- Noter les métriques de succès définies

### 3. Charger les apprentissages pertinents 📚

**Systeme centralise** : `C:\Users\raph6\Documents\ServOMorph\Agents_IA_V2\.claude\learnings\`

1. Detecter le contexte du projet (technologies, type, fichiers recents)
2. Rechercher les apprentissages pertinents :
   ```bash
   python C:\Users\raph6\Documents\ServOMorph\Agents_IA_V2\.claude\learnings\learning_manager.py search "[contexte]"
   ```
3. Afficher les apprentissages charges (si disponibles)

### 4. Synthèse à présenter

Présente un rapport structuré contenant :

```
## État du Projet

**Phase actuelle** : [numéro et nom de la phase]
**Statut global** : [À démarrer / En cours / Bloqué]

## Tâches Prioritaires

1. [Tâche prioritaire 1]
2. [Tâche prioritaire 2]
3. [Tâche prioritaire 3]

## Contexte Technique

- Stack : [technologies identifiées]
- Structure : [architecture du projet]

## Prêt à travailler sur

[Liste des actions réalisables immédiatement]
```

### 5. Question de démarrage

Termine en demandant :
> "Sur quelle tâche souhaites-tu travailler ?"
