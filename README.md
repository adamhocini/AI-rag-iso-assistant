# Assistant IA RAG ISO — PoC local sécurisé

## Présentation

Ce projet est un **Proof of Concept d’assistant IA RAG** permettant d’interroger une documentation qualité ISO fictive.

L’objectif n’est pas de créer un simple chatbot, mais de construire un démonstrateur crédible d’**IA appliquée aux systèmes d’information**, capable de :

- rechercher de l’information dans un corpus documentaire ;
- produire une réponse sourcée ;
- afficher les extraits utilisés ;
- calculer un score de confiance explicable ;
- détecter certaines alertes documentaires ;
- identifier des incohérences simples ;
- journaliser les interactions ;
- conserver une logique de prudence et de validation humaine.

Le projet est conçu comme un MVP local, pédagogique et évolutif.

---

## Objectif général

Le PoC répond à la problématique suivante :

> Comment concevoir un assistant IA RAG fiable, traçable et prudent pour interroger une documentation qualité, produire des réponses sourcées et assister la préparation d’éléments d’audit ?

Le projet vise à démontrer plusieurs compétences :

- compréhension des LLM ;
- architecture RAG ;
- embeddings et recherche vectorielle ;
- chunking documentaire ;
- détection d’intention ;
- qualité de contexte transmis au modèle ;
- réduction des hallucinations ;
- calcul d’un score de confiance simple ;
- traçabilité ;
- bonnes pratiques de sécurité ;
- valorisation métier autour de la documentation qualité.

---

## Fonctionnalités principales

### 1. Corpus documentaire ISO fictif

Le projet contient 8 documents Markdown fictifs inspirés d’un système qualité ISO 9001 :

- manuel qualité fictif ;
- procédure de gestion documentaire ;
- procédure de gestion des non-conformités ;
- procédure d’audit interne ;
- procédure de gestion des risques ;
- fiche processus achats ;
- registre fictif des actions correctives ;
- compte rendu fictif d’audit interne.

Chaque document dispose de métadonnées :

- titre ;
- référence ;
- version ;
- statut ;
- date de validation ;
- propriétaire ;
- processus concerné ;
- type de document.

---

### 2. Chargement et inspection documentaire

Le projet lit les documents Markdown et sépare :

- les métadonnées ;
- le contenu textuel.

Script associé :

```bash
python scripts/inspect_documents.py
```

---

### 3. Découpage en chunks

Les documents sont découpés en segments textuels avec chevauchement afin d’améliorer la récupération d’information.

Paramètres actuels :

```txt
Taille cible : 1200 caractères
Overlap : 200 caractères
```

Script associé :

```bash
python scripts/inspect_chunks.py
```

---

### 4. Indexation vectorielle locale

Les chunks sont vectorisés et stockés dans une base locale ChromaDB.

Commande d’ingestion :

```bash
python scripts/ingest_documents.py
```

Cette étape :

- charge les documents ;
- produit les chunks ;
- les insère dans ChromaDB ;
- réinitialise la base locale ;
- vérifie le nombre de chunks présents.

---

### 5. Recherche sémantique

Le projet permet d’effectuer une recherche vectorielle sur le corpus.

Exemple :

```bash
python scripts/search_documents.py "Cette procédure de gestion des risques est-elle encore valide ?"
```

Le système retourne :

- les chunks les plus proches ;
- les scores de similarité ;
- les métadonnées des documents ;
- les extraits pertinents.

---

### 6. Moteur RAG

Le moteur RAG exécute la chaîne suivante :

```txt
Question utilisateur
↓
Détection d’intention
↓
Recherche vectorielle
↓
Filtrage des résultats pertinents
↓
Sélection du contexte envoyé au LLM
↓
Détection d’alertes
↓
Calcul du score de confiance
↓
Génération de la réponse
↓
Post-traitement de cohérence
↓
Journalisation
```

Script principal :

```bash
python scripts/ask_rag.py "Quels documents prouvent qu'un audit interne a été réalisé ?" --ollama
```

---

### 7. Génération locale avec Ollama

Le projet utilise **Ollama** pour exécuter localement un modèle de langage, sans coût API.

Modèle testé :

```txt
llama3.2:3b
```

Avantages :

- exécution locale ;
- pas de coût API ;
- pas d’envoi de documents vers un fournisseur cloud ;
- adapté à un PoC pédagogique.

Limites :

- qualité de génération inférieure à certains modèles cloud ;
- possibles reformulations imparfaites ;
- nécessité de garde-fous complémentaires côté Python.

---

### 8. Mode sans LLM

Si aucune source suffisamment pertinente n’est retrouvée, le système n’appelle pas Ollama et répond prudemment :

```txt
Je ne peux pas répondre de manière fiable avec les documents disponibles.
```

Ce mécanisme limite les hallucinations.

---

### 9. Score de confiance explicable

Le projet calcule un score de confiance simple prenant en compte :

- la similarité vectorielle ;
- le nombre de sources pertinentes ;
- le statut documentaire ;
- les alertes détectées ;
- les incohérences de version.

Exemple :

```txt
Faible (0.47)
```

Avec explication :

```txt
- Meilleur score de similarité : 0.707
- Score moyen de similarité : 0.662
- 4 sources distinctes retrouvées
- 1 incohérence de version détectée
```

---

### 10. Détection d’intention

Le moteur reconnaît plusieurs types de questions :

- validité documentaire ;
- preuve d’audit ;
- checklist d’audit ;
- procédure métier ;
- incohérence documentaire ;
- question générale.

Cette logique permet d’améliorer la sélection des chunks envoyés au modèle.

---

### 11. Détection d’incohérences simples

Le système détecte une incohérence volontairement intégrée au corpus :

```txt
CR-AUD-2025-001 mentionne FP-ACH-001 version 1.0
FP-ACH-001 est indexé en version 1.1
```

Alerte produite :

```txt
Incohérence de version détectée : l'extrait issu de CR-AUD-2025-001 mentionne FP-ACH-001 en version 1.0, alors que la version actuelle indexée est 1.1.
```

---

### 12. Post-traitement de cohérence

Si le LLM reformule mal une alerte, le système peut ajouter une correction automatique.

Exemple :

```txt
Correction automatique : FP-ACH-001 a le statut indexé 'Validé'. Il ne doit donc pas être présenté comme étant en révision.
```

Cette approche montre que le projet ne fait pas confiance aveuglément au LLM.

---

### 13. Interface Streamlit

Une interface web locale permet de :

- poser une question ;
- choisir le mode de génération ;
- consulter la réponse ;
- afficher les sources ;
- afficher les extraits ;
- consulter les alertes ;
- voir le score de confiance ;
- accéder à l’historique des interactions.

Lancement :

```bash
python -m streamlit run app/main.py
```

---

### 14. Historique et journalisation

Les interactions sont enregistrées dans :

```txt
logs/rag_interactions.csv
```

Les informations journalisées incluent :

- date et heure ;
- question ;
- intention détectée ;
- mode de génération ;
- score de confiance ;
- explication du score ;
- sources utilisées ;
- alertes ;
- nombre d’extraits affichés ;
- nombre d’extraits transmis au LLM ;
- réponse générée.

L’interface Streamlit permet également de filtrer :

- par niveau de confiance ;
- par intention ;
- par présence d’alertes.

---

## Architecture fonctionnelle

```txt
Utilisateur
↓
Interface Streamlit ou CLI
↓
Détection d’intention
↓
Recherche vectorielle ChromaDB
↓
Filtrage des chunks
↓
Sélection métier du contexte
↓
Détection d’alertes documentaires
↓
Score de confiance
↓
Génération Ollama locale
↓
Contrôles de cohérence Python
↓
Réponse sourcée + alertes + limites
↓
Journalisation CSV
```

---

## Stack technique

| Composant | Technologie |
|---|---|
| Langage principal | Python |
| Interface | Streamlit |
| Base vectorielle | ChromaDB |
| Modèle local | Ollama |
| LLM testé | llama3.2:3b |
| Documents | Markdown |
| Configuration | `.env` |
| Journalisation | CSV |
| Données | Corpus ISO fictif |

---

## Arborescence du projet

```txt
rag-iso-assistant/
│
├── app/
│   ├── __init__.py
│   ├── chunker.py
│   ├── consistency_checker.py
│   ├── document_loader.py
│   ├── intent_detector.py
│   ├── llm_client.py
│   ├── logger.py
│   ├── main.py
│   ├── ollama_client.py
│   ├── rag_engine.py
│   └── vector_store.py
│
├── data/
│   ├── documents/
│   │   ├── compte_rendu_audit_interne.md
│   │   ├── fiche_processus_achats.md
│   │   ├── manuel_qualite.md
│   │   ├── procedure_audit_interne.md
│   │   ├── procedure_gestion_documentaire.md
│   │   ├── procedure_gestion_risques.md
│   │   ├── procedure_non_conformites.md
│   │   └── registre_actions_correctives.md
│   │
│   └── vector_store/
│
├── docs/
│   └── demo_scenario.md
│
├── logs/
│   ├── archive/
│   └── rag_interactions.csv
│
├── scripts/
│   ├── ask_rag.py
│   ├── ingest_documents.py
│   ├── inspect_chunks.py
│   ├── inspect_documents.py
│   ├── search_documents.py
│   └── test_consistency_checker.py
│
├── .env
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Prérequis

### Logiciels

- Python 3.12 recommandé ;
- Ollama installé ;
- environnement macOS, Linux ou Windows compatible Python ;
- terminal.

### Modèle Ollama

Télécharger le modèle utilisé dans le PoC :

```bash
ollama pull llama3.2:3b
```

Tester Ollama :

```bash
ollama run llama3.2:3b "Explique ce qu'est un RAG dans le domaine de l'IA."
```

---

## Installation du projet

### 1. Se placer dans le projet

```bash
cd /Users/adamhocini/Desktop/ProjectRAG_ISO/rag-iso-assistant
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv .venv
```

### 3. Activer l’environnement virtuel

Sur macOS / Linux :

```bash
source .venv/bin/activate
```

### 4. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

---

## Configuration

Créer un fichier `.env` à la racine du projet.

Exemple :

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
LOGS_PATH=./logs/rag_interactions.csv
```

Une clé OpenAI peut exister dans `.env`, mais elle n’est pas nécessaire dans la version locale du PoC.

---

## Ingestion des documents

Avant de lancer l’assistant, construire la base vectorielle :

```bash
python scripts/ingest_documents.py
```

Résultat attendu :

```txt
Documents chargés : 8
Chunks créés : 15
Chunks insérés : 15
Chunks présents dans ChromaDB : 15
```

---

## Lancer l’assistant en ligne de commande

### Question simple avec Ollama

```bash
python scripts/ask_rag.py "Quels documents prouvent qu'un audit interne a été réalisé ?" --ollama
```

### Question de validité documentaire

```bash
python scripts/ask_rag.py "Cette procédure de gestion des risques est-elle encore valide ?" --ollama
```

### Question hors corpus

```bash
python scripts/ask_rag.py "Quelle est la politique de cybersécurité de l'entreprise ?" --ollama
```

---

## Lancer l’interface Streamlit

```bash
python -m streamlit run app/main.py
```

Puis ouvrir :

```txt
http://localhost:8501
```

---

## Scénario de démonstration

Le scénario complet est disponible dans :

```txt
docs/demo_scenario.md
```

Les 5 questions principales sont :

1. Quelle est la procédure de gestion des non-conformités ?
2. Quels documents prouvent qu’un audit interne a été réalisé ?
3. Prépare une checklist d’audit pour le processus achats.
4. Cette procédure de gestion des risques est-elle encore valide ?
5. Y a-t-il des incohérences entre le compte rendu d’audit et la fiche processus achats ?

Question bonus :

```txt
Quelle est la politique de cybersécurité de l'entreprise ?
```

---

## Principes de sécurité et de prudence

Le projet intègre plusieurs bonnes pratiques :

- utilisation d’un corpus fictif ;
- exécution locale avec Ollama ;
- non-envoi de documents sensibles à un service tiers ;
- stockage de la configuration dans `.env` ;
- refus de répondre sans sources pertinentes ;
- affichage des sources ;
- affichage des limites ;
- rappel de la validation humaine ;
- détection d’alertes documentaires ;
- journalisation des interactions ;
- contrôle Python complémentaire après génération.

---

## Limites du PoC

Ce projet reste un MVP. Ses limites sont importantes :

- corpus fictif et volontairement réduit ;
- absence d’authentification ;
- absence de gestion fine des droits documentaires ;
- score de confiance approximatif ;
- détection d’incohérences volontairement simple ;
- modèle local léger parfois imprécis ;
- pas de reranking avancé ;
- pas d’évaluation quantitative automatique ;
- journalisation CSV simple ;
- pas de base SQL ou de persistance métier avancée ;
- pas de connecteur SharePoint ou Microsoft 365 dans cette version.

---

## Améliorations futures

Une version plus professionnelle pourrait intégrer :

- Azure OpenAI ;
- Azure AI Search ;
- SharePoint comme source documentaire ;
- Microsoft Entra ID ;
- gestion des droits d’accès ;
- Power Apps ou interface web complète ;
- Dataverse ou SQL pour les logs ;
- Power BI pour le suivi ;
- modèles d’évaluation de qualité des réponses ;
- tests automatiques de non-régression RAG ;
- reranking avancé ;
- analyse documentaire multi-fichiers PDF/Office ;
- citation précise par page et section.

---

## Intérêt du projet pour une candidature CIFRE ou IA appliquée aux SI

Ce projet illustre une approche concrète de l’IA appliquée aux systèmes d’information :

- automatisation raisonnée de l’accès à l’information ;
- articulation entre IA générative et gouvernance documentaire ;
- prise en compte de la qualité, de l’auditabilité et de la confiance ;
- explicabilité des réponses ;
- intégration de garde-fous contre les hallucinations ;
- passage d’un MVP local à une architecture d’entreprise sécurisée.

Il constitue une base crédible pour approfondir des sujets de recherche ou d’ingénierie autour de :

- la fiabilité des assistants RAG ;
- la traçabilité des réponses ;
- l’évaluation de la confiance ;
- la gouvernance de la connaissance ;
- la qualité documentaire assistée par IA.

---

## Message clé

> Ce PoC montre comment un assistant RAG peut aider à exploiter une documentation qualité en fournissant des réponses sourcées, un score de confiance, des alertes documentaires et une traçabilité des interactions, tout en conservant une logique de prudence et de validation humaine.
