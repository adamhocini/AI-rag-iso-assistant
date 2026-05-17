# Pitch de présentation — Assistant IA RAG ISO

## Objectif du document

Ce document propose un pitch oral de 2 minutes pour présenter le projet **Assistant IA RAG ISO** dans un contexte professionnel, académique ou de candidature orientée IA appliquée aux systèmes d’information.

L’objectif est de pouvoir expliquer rapidement :

- le besoin auquel répond le projet ;
- l’approche technique retenue ;
- les fonctionnalités principales ;
- la valeur ajoutée du PoC ;
- les limites assumées ;
- les perspectives d’évolution.

---

# 1. Pitch principal — Version 2 minutes

> J’ai développé un PoC d’assistant IA RAG local destiné à interroger une documentation qualité ISO fictive.
>
> L’idée de départ était de ne pas créer un simple chatbot, mais un démonstrateur plus crédible d’IA appliquée aux systèmes d’information, capable de produire des réponses sourcées, traçables et prudentes.
>
> Concrètement, l’utilisateur pose une question dans une interface Streamlit, par exemple sur une procédure, une preuve d’audit ou une incohérence documentaire. Le système recherche d’abord les passages pertinents dans une base vectorielle ChromaDB, puis il sélectionne les meilleurs extraits à transmettre à un modèle local Ollama. La réponse générée affiche les sources utilisées, les extraits pertinents, un niveau de confiance et les limites d’interprétation.
>
> J’ai également ajouté plusieurs mécanismes de fiabilisation : une détection d’intention pour mieux choisir les documents utiles, un score de confiance explicable, des alertes lorsqu’un document est en révision, une détection simple d’incohérences de version entre documents, ainsi qu’un contrôle Python après génération pour corriger certaines mauvaises reformulations du modèle.
>
> Le PoC inclut aussi une journalisation des interactions et un historique consultable dans l’interface, ce qui permet de retrouver les questions posées, les sources utilisées, les alertes et les réponses générées.
>
> Ce projet montre donc comment un assistant RAG peut servir d’aide à l’analyse documentaire et à la préparation d’éléments d’audit, tout en conservant des principes essentiels : sources visibles, prudence, traçabilité et validation humaine.
>
> À terme, cette architecture pourrait évoluer vers une version entreprise intégrant SharePoint, Azure OpenAI, Azure AI Search, Microsoft Entra ID et des outils de supervision comme Power BI.

---

# 2. Décomposition du pitch par idée forte

## Partie 1 — Le besoin

```txt
Les organisations disposent souvent d’une documentation riche mais difficile à exploiter rapidement.
Dans un contexte qualité, audit ou conformité, il faut retrouver la bonne information, savoir si elle est applicable et identifier d’éventuelles incohérences.
```

## Partie 2 — La solution

```txt
J’ai développé un assistant IA RAG capable d’interroger une documentation ISO fictive et de répondre à des questions en s’appuyant explicitement sur les documents retrouvés.
```

## Partie 3 — Le fonctionnement technique

```txt
Le système combine :
- chargement documentaire ;
- découpage en chunks ;
- recherche vectorielle avec ChromaDB ;
- génération locale avec Ollama ;
- logique métier de sélection des sources ;
- score de confiance ;
- alertes et journalisation.
```

## Partie 4 — Les points différenciants

```txt
Le PoC ne se contente pas de générer du texte :
- il affiche ses sources ;
- il expose ses limites ;
- il détecte des incohérences ;
- il réduit son niveau de confiance en cas d’alerte ;
- il conserve une traçabilité des interactions.
```

## Partie 5 — La perspective

```txt
Cette approche peut évoluer vers une architecture d’entreprise sécurisée intégrant Microsoft 365, SharePoint, Azure OpenAI, Azure AI Search et Entra ID.
```

---

# 3. Version plus naturelle pour entretien

Cette version est plus conversationnelle et peut être utilisée face à un recruteur ou un enseignant.

> J’ai travaillé sur un assistant IA RAG appliqué à une documentation qualité ISO fictive. Mon objectif était de dépasser le simple chatbot et de construire un système plus proche d’un outil d’aide à la décision documentaire.
>
> L’utilisateur peut poser des questions comme : “Quelle est la procédure de gestion des non-conformités ?”, “Quels documents prouvent qu’un audit interne a été réalisé ?” ou encore “Y a-t-il une incohérence entre deux documents ?”.
>
> Techniquement, j’ai mis en place une ingestion documentaire, un chunking, une indexation vectorielle avec ChromaDB, puis une génération locale avec Ollama. Mais surtout, j’ai ajouté des briques de fiabilisation : les réponses affichent leurs sources, leur score de confiance, leurs limites, et le système peut détecter certaines incohérences simples, par exemple une différence de version entre deux documents.
>
> J’ai aussi conçu une interface Streamlit avec un historique des interactions, ce qui apporte une dimension de traçabilité. Pour moi, c’est un point important si l’on veut appliquer l’IA générative dans des systèmes d’information sensibles.
>
> Ce PoC m’a permis d’aborder à la fois les aspects IA — embeddings, RAG, LLM, hallucinations — et les aspects SI — gouvernance documentaire, sécurité, explicabilité et auditabilité.

---

# 4. Messages clés à faire ressortir

Pendant la présentation, les idées suivantes doivent être visibles :

## 4.1 Ce n’est pas juste un chatbot

```txt
Le projet met l’accent sur la recherche documentaire, la fiabilité et la traçabilité.
```

## 4.2 Les réponses sont justifiées

```txt
Chaque réponse doit être reliée à des sources et à des extraits.
```

## 4.3 La confiance est explicitée

```txt
Le système affiche un score de confiance et explique pourquoi il est faible, moyen ou élevé.
```

## 4.4 Les incohérences sont valorisées

```txt
Le PoC peut détecter certaines alertes documentaires, ce qui le rend pertinent pour un usage d’assistance à l’audit.
```

## 4.5 L’humain reste au centre

```txt
L’assistant aide à analyser, mais ne remplace ni un auditeur, ni un responsable qualité, ni une validation documentaire officielle.
```

---

# 5. Variante courte — Pitch 45 secondes

Cette version peut servir si l’on te demande de résumer très rapidement ton projet.

> J’ai développé un PoC d’assistant IA RAG local pour interroger une documentation qualité ISO fictive. L’objectif était de créer un outil plus fiable qu’un chatbot classique, avec des réponses sourcées, un score de confiance, des alertes documentaires et un historique des interactions.
>
> Le système utilise Python, ChromaDB, Streamlit et Ollama. Il retrouve les passages pertinents, génère une réponse à partir de ces sources, puis signale par exemple qu’un document est en révision ou qu’il existe une incohérence de version entre deux documents.
>
> Ce projet m’a permis de travailler à la fois sur l’IA générative et sur les enjeux de gouvernance, de traçabilité et de sécurité dans les systèmes d’information.

---

# 6. Variante orientée candidature CIFRE

Cette variante insiste davantage sur la problématique de recherche et l’industrialisation possible.

> J’ai développé un PoC d’assistant IA RAG appliqué à une documentation qualité ISO fictive, avec l’objectif d’étudier comment l’IA générative peut améliorer l’accès à l’information tout en restant traçable et contrôlable.
>
> Au-delà de la réponse automatique, j’ai intégré plusieurs mécanismes de fiabilisation : sources visibles, extraits justificatifs, détection d’intention, score de confiance explicable, alertes sur les documents en révision, détection d’incohérences de version et journalisation des échanges.
>
> Ce projet constitue pour moi une première exploration d’un sujet plus large : comment concevoir des assistants IA réellement exploitables dans des environnements d’entreprise où la qualité des données, la gouvernance documentaire, la sécurité et la confiance sont centrales.
>
> Une suite naturelle serait de faire évoluer cette architecture vers un environnement Microsoft 365 avec SharePoint, Azure AI Search, Azure OpenAI et Entra ID, tout en approfondissant les méthodes d’évaluation de la fiabilité des réponses RAG.

---

# 7. Conseils d’utilisation à l’oral

## 7.1 Bien gérer le temps

Pour tenir en 2 minutes :

- 20 secondes pour le contexte ;
- 40 secondes pour la solution ;
- 35 secondes pour les mécanismes différenciants ;
- 15 secondes pour la valeur ajoutée ;
- 10 secondes pour les perspectives.

---

## 7.2 Éviter de tout détailler immédiatement

Ne commence pas par :

```txt
J’ai créé un chunker avec un overlap de 200 caractères...
```

Commence par :

```txt
J’ai voulu concevoir un assistant IA qui réponde de manière sourcée et traçable sur une base documentaire qualité.
```

Les détails techniques arrivent ensuite si l’interlocuteur te questionne.

---

## 7.3 Insister sur le caractère raisonné du projet

Toujours rappeler :

```txt
Le but n’est pas de remplacer la décision humaine, mais d’assister l’analyse documentaire.
```

---

## 7.4 Mettre en avant les limites

Dire qu’un PoC a des limites n’est pas une faiblesse. C’est professionnel.

Exemples :

- modèle local léger ;
- corpus fictif ;
- score de confiance approximatif ;
- détection d’incohérences encore simple ;
- pas encore d’authentification ni de gouvernance d’accès.

---

# 8. Ce que ce pitch doit faire comprendre

À la fin de ton pitch, ton interlocuteur doit avoir compris que :

1. le projet répond à un vrai besoin métier ;
2. tu maîtrises les bases du RAG ;
3. tu as pensé au-delà de la simple génération de texte ;
4. tu as intégré la qualité, la sécurité et l’auditabilité ;
5. tu sais envisager une architecture d’entreprise plus ambitieuse.

---

# 9. Message final à retenir

> Ce projet montre qu’un assistant RAG peut devenir un véritable outil d’aide à l’analyse documentaire lorsqu’il combine recherche sémantique, génération contrôlée, sources visibles, score de confiance, alertes et traçabilité.
