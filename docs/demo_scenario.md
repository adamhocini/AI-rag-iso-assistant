# Scénario de démonstration — Assistant IA RAG ISO
## Objectif de la démonstration
Cette démonstration présente un assistant IA RAG local permettant d’interroger une documentation qualité ISO fictive.
Le PoC montre comment un assistant IA peut :
- rechercher des informations dans un corpus documentaire ;
- générer une réponse sourcée ;
- afficher les extraits utilisés ;
- calculer un score de confiance ;
- signaler les limites de la réponse ;
- détecter des alertes documentaires ;
- journaliser les interactions ;
- faciliter la préparation d’éléments d’audit.
L’assistant ne remplace pas un auditeur, un responsable qualité ou une validation humaine. Il sert d’aide à l’analyse documentaire.
---
## Architecture démontrée
```txt
Utilisateur
↓
Interface Streamlit
↓
Question
↓
Détection d’intention
↓
Recherche vectorielle ChromaDB
↓
Sélection des chunks pertinents
↓
Détection d’alertes documentaires
↓
Génération locale avec Ollama
↓
Contrôles de cohérence Python
↓
Réponse sourcée + score + alertes
↓
Journalisation CSV

⸻

## Question 1 — Retrouver une procédure métier

Question à poser

Quelle est la procédure de gestion des non-conformités ?

Objectif de la question

Montrer que l’assistant peut retrouver une procédure métier dans le corpus documentaire.

Comportement attendu

L’assistant doit identifier principalement :

PROC-NC-001 — Procédure de gestion des non-conformités

Il doit expliquer les grandes étapes :

* détection ;
* enregistrement ;
* analyse des causes ;
* traitement ;
* vérification d’efficacité ;
* clôture.

Ce que cette question démontre

Cette question montre la capacité de base du RAG :

Question métier
↓
Recherche documentaire
↓
Réponse sourcée

⸻

## Question 2 — Identifier des preuves d’audit

Question à poser

Quels documents prouvent qu’un audit interne a été réalisé ?

Objectif de la question

Montrer que l’assistant sait distinguer une procédure théorique d’une preuve documentaire.

Comportement attendu

L’assistant doit utiliser principalement :

CR-AUD-2025-001 — Compte rendu fictif d’audit interne achats
PROC-AUD-001 — Procédure d’audit interne

Le compte rendu est la preuve que l’audit a été réalisé.

La procédure explique ce qu’un compte rendu d’audit doit contenir.

Ce que cette question démontre

Cette question montre :

* la recherche de preuves ;
* la sélection métier des sources ;
* la distinction entre document de référence et enregistrement d’audit ;
* l’affichage des sources.

⸻

## Question 3 — Générer une checklist d’audit

Question à poser

Prépare une checklist d’audit pour le processus achats.

Objectif de la question

Montrer que l’assistant peut produire un livrable structuré à partir des documents.

Comportement attendu

L’assistant doit s’appuyer sur :

FP-ACH-001 — Fiche processus achats
PROC-AUD-001 — Procédure d’audit interne
PROC-NC-001 — Procédure de gestion des non-conformités
REG-AC-001 — Registre des actions correctives

La réponse attendue doit contenir des points de contrôle comme :

* existence d’une demande d’achat validée ;
* existence d’une commande ;
* preuve de réception ;
* évaluation fournisseur ;
* traitement des non-conformités fournisseurs ;
* suivi des actions correctives ;
* indicateurs achats.

Ce que cette question démontre

Cette question montre la capacité de génération contrôlée :

Sources documentaires
↓
Synthèse structurée
↓
Checklist exploitable

⸻

## Question 4 — Vérifier la validité documentaire

Question à poser

Cette procédure de gestion des risques est-elle encore valide ?

Objectif de la question

Montrer que l’assistant prend en compte les métadonnées documentaires.

Comportement attendu

L’assistant doit détecter que :

PROC-RISK-001 — Procédure de gestion des risques
Statut : En révision
Version : 0.9

Il doit répondre prudemment :

Le document est en révision ; il ne doit pas être utilisé comme seule référence applicable sans validation humaine.

Ce que cette question démontre

Cette question montre :

* l’utilisation des métadonnées ;
* l’alerte sur un document en révision ;
* la baisse du score de confiance ;
* la nécessité de validation humaine.

⸻

## Question 5 — Détecter une incohérence documentaire

Question à poser

Y a-t-il des incohérences entre le compte rendu d’audit et la fiche processus achats ?

Objectif de la question

Montrer que l’assistant peut détecter une incohérence simple entre documents.

Comportement attendu

Le système doit détecter :

CR-AUD-2025-001 mentionne FP-ACH-001 version 1.0
FP-ACH-001 est actuellement indexé en version 1.1

L’alerte attendue est :

Incohérence de version détectée : l’extrait issu de CR-AUD-2025-001 mentionne FP-ACH-001 en version 1.0, alors que la version actuelle indexée est 1.1.

Ce que cette question démontre

Cette question montre :

* la détection d’incohérence ;
* l’explication du score de confiance ;
* la réduction du score en cas d’alerte ;
* la supervision humaine ;
* les corrections automatiques de cohérence si le LLM reformule mal.

⸻

## Question bonus — Refus prudent hors corpus

Question à poser

Quelle est la politique de cybersécurité de l’entreprise ?

Objectif de la question

Montrer que l’assistant ne répond pas quand le corpus ne contient pas l’information.

Comportement attendu

L’assistant doit répondre :

Je ne peux pas répondre de manière fiable avec les documents disponibles.

Ce que cette question démontre

Cette question montre la logique anti-hallucination :

Pas de source pertinente
↓
Pas de réponse inventée

⸻

## Déroulé conseillé de la démonstration

1. Présenter rapidement le contexte

Exemple :

J’ai développé un PoC d’assistant IA RAG local pour interroger une documentation qualité ISO fictive. L’objectif n’est pas de remplacer un auditeur, mais d’aider à retrouver les informations, préparer des éléments d’audit et identifier des points de vigilance documentaire.

⸻

2. Montrer l’interface Streamlit

Afficher :

* le champ de question ;
* le choix du mode de génération ;
* l’état d’Ollama ;
* les questions de démonstration ;
* les onglets sources, extraits, limites ;
* l’onglet historique.

⸻

3. Poser les 5 questions dans l’ordre

Ordre recommandé :

1. Procédure de gestion des non-conformités.
2. Preuves d’audit.
3. Checklist d’audit achats.
4. Validité de la procédure risques.
5. Incohérence entre compte rendu et fiche processus.

⸻

4. Montrer l’historique

Après plusieurs questions, ouvrir l’onglet Historique.

Montrer :

* les questions posées ;
* les scores ;
* les intentions détectées ;
* les alertes ;
* les filtres.

⸻

5. Conclure sur les limites

Points à rappeler :

* le corpus est fictif ;
* le score de confiance reste approximatif ;
* Ollama local peut reformuler imparfaitement ;
* les réponses doivent être validées humainement ;
* l’assistant ne remplace pas un auditeur ;
* une version entreprise devrait utiliser une gouvernance documentaire et une sécurité renforcées.

⸻

Message clé de la démonstration

Ce PoC montre comment un assistant RAG peut aider à exploiter une documentation qualité en fournissant des réponses sourcées, un score de confiance, des alertes documentaires et une traçabilité des interactions, tout en conservant une logique de prudence et de validation humaine.

⸻

Validation de l’étape

L’étape est validée si :

1. le fichier suivant existe :

docs/demo_scenario.md

2. le fichier contient les 5 questions de démonstration ;
3. Streamlit affiche les questions dans la sidebar ;
4. les 5 questions fonctionnent avec :

python scripts/ask_rag.py "..." --ollama

5. l’historique journalise les interactions.

⸻

Commandes de vérification

Vérifier que le fichier existe

ls -la docs

Résultat attendu :

demo_scenario.md

⸻

Afficher le début du fichier

head -40 docs/demo_scenario.md

⸻

Vérifier les questions dans Streamlit

grep -n "demo_questions" -A 15 app/main.py

Tu dois voir notamment :

Quels documents prouvent qu’un audit interne a été réalisé ?
Cette procédure de gestion des risques est-elle encore valide ?
Quelle est la procédure de gestion des non-conformités ?
Prépare une checklist d’audit pour le processus achats.
Y a-t-il des incohérences entre le compte rendu d’audit et la fiche processus achats ?
Quelle est la politique de cybersécurité de l’entreprise ?

⸻

Tests rapides des 5 questions

python scripts/ask_rag.py "Quelle est la procédure de gestion des non-conformités ?" --ollama
python scripts/ask_rag.py "Quels documents prouvent qu'un audit interne a été réalisé ?" --ollama
python scripts/ask_rag.py "Prépare une checklist d'audit pour le processus achats." --ollama
python scripts/ask_rag.py "Cette procédure de gestion des risques est-elle encore valide ?" --ollama
python scripts/ask_rag.py "Y a-t-il des incohérences entre le compte rendu d'audit et la fiche processus achats ?" --ollama

Le plus important est de vérifier qu’il n’y a pas d’erreur Python et que les réponses affichent bien :

* les sources ;
* les extraits ;
* le niveau de confiance ;
* les alertes éventuelles ;
* les limites.