# Explication technique défendable en entretien — Assistant IA RAG ISO

## Objectif du document

Ce document prépare une présentation technique du projet **Assistant IA RAG ISO** dans un contexte d’entretien, de soutenance ou d’échange avec un recruteur technique.

Il permet d’expliquer de manière structurée :

- l’architecture choisie ;
- le fonctionnement du pipeline RAG ;
- les choix technologiques ;
- les garde-fous mis en place ;
- les limites du PoC ;
- les améliorations possibles.

---

# 1. Présentation technique synthétique

Le projet est un assistant IA RAG local permettant d’interroger une documentation qualité ISO fictive.

Le système combine :

- un corpus documentaire Markdown avec métadonnées ;
- un pipeline d’ingestion ;
- un découpage en chunks ;
- une indexation vectorielle locale avec ChromaDB ;
- un moteur de recherche sémantique ;
- une détection d’intention ;
- une sélection raisonnée des extraits envoyés au LLM ;
- une génération locale avec Ollama ;
- un score de confiance explicable ;
- des alertes documentaires ;
- une détection d’incohérences simples ;
- une interface Streamlit ;
- une journalisation des interactions.

---

# 2. Pourquoi utiliser une architecture RAG ?

Un LLM seul ne connaît pas naturellement la documentation spécifique d’une organisation.

Le RAG permet de :

1. retrouver des extraits pertinents dans un corpus documentaire ;
2. transmettre ces extraits au modèle ;
3. générer une réponse ancrée dans les documents disponibles.

L’objectif est de réduire les hallucinations et de rendre la réponse vérifiable.

Dans le projet :

```txt
Question utilisateur
↓
Recherche documentaire
↓
Sélection des bons extraits
↓
Génération d’une réponse sourcée
```

---

# 3. Pourquoi utiliser des documents fictifs ?

Le corpus est volontairement fictif pour plusieurs raisons :

- éviter tout risque lié à l’exposition de documents sensibles ;
- faciliter l’expérimentation ;
- contrôler les cas de test ;
- introduire volontairement certaines incohérences ;
- démontrer les mécanismes de détection et de prudence.

Cette approche est adaptée à un PoC pédagogique.

---

# 4. Pourquoi structurer les documents avec des métadonnées ?

Chaque document possède :

```yaml
titre:
reference:
version:
statut:
date_validation:
proprietaire:
processus:
type_document:
```

Ces métadonnées permettent :

- d’identifier précisément les sources ;
- de savoir si un document est validé ou en révision ;
- de produire des réponses plus lisibles ;
- de détecter certains risques documentaires ;
- d’alimenter le score de confiance.

Exemple :

```txt
PROC-RISK-001
Version : 0.9
Statut : En révision
```

Le système peut alors répondre avec prudence.

---

# 5. Pourquoi découper les documents en chunks ?

Envoyer un document entier au moteur de recherche ou au LLM est inefficace.

Le chunking permet :

- d’isoler les passages réellement utiles ;
- d’améliorer la précision de la recherche ;
- de limiter le volume de contexte ;
- de réduire le bruit transmis au modèle.

Le projet utilise :

```txt
Taille cible : 1200 caractères
Overlap : 200 caractères
```

L’overlap évite de couper brutalement une information importante entre deux chunks.

---

# 6. Pourquoi utiliser une base vectorielle ?

Une base vectorielle permet de retrouver des passages non seulement par mots-clés, mais aussi par proximité sémantique.

Exemple :

```txt
Question :
Quels documents prouvent qu’un audit interne a été réalisé ?
```

Le moteur peut retrouver :

- la procédure d’audit ;
- le compte rendu d’audit ;
- les extraits parlant de preuves.

La base utilisée est :

```txt
ChromaDB
```

Ce choix est adapté au MVP car elle est :

- locale ;
- simple à mettre en œuvre ;
- suffisante pour un petit corpus ;
- compatible avec une montée en complexité ultérieure.

---

# 7. Pourquoi ne pas envoyer tous les chunks au LLM ?

Envoyer trop de chunks peut dégrader la qualité de la réponse.

Risques :

- mélange d’informations ;
- citations inutiles ;
- réponse trop large ;
- perte de précision ;
- surinterprétation de passages secondaires.

Le projet distingue donc :

```txt
Extraits pertinents affichés à l’utilisateur
≠
Extraits réellement transmis au LLM
```

Cette séparation améliore :

- la transparence ;
- la qualité du contexte ;
- la maîtrise de la génération.

---

# 8. Pourquoi avoir ajouté une détection d’intention ?

La recherche vectorielle mesure une proximité sémantique, mais ne comprend pas toujours l’objectif métier de la question.

Exemple :

```txt
Cette procédure de gestion des risques est-elle encore valide ?
```

La question ne demande pas seulement de parler des risques.  
Elle demande de vérifier la **validité documentaire**.

Le système détecte donc plusieurs intentions :

- validité documentaire ;
- preuve d’audit ;
- checklist d’audit ;
- procédure métier ;
- incohérence documentaire ;
- question générale.

Cette détection permet de :

- mieux sélectionner les sources ;
- prioriser certains documents ;
- transmettre un contexte plus pertinent au modèle.

---

# 9. Pourquoi avoir ajouté des références obligatoires selon l’intention ?

Pour certaines questions, un document métier précis doit absolument être privilégié.

Exemple :

```txt
Quels documents prouvent qu’un audit interne a été réalisé ?
```

Les documents essentiels sont :

```txt
CR-AUD-2025-001
PROC-AUD-001
```

Même si la procédure d’audit a un score vectoriel très élevé, le compte rendu d’audit reste indispensable, car il constitue la preuve documentaire concrète.

Cela montre que :

```txt
Pertinence vectorielle ≠ pertinence métier
```

---

# 10. Comment fonctionne le score de confiance ?

Le score de confiance est un indicateur heuristique.

Il repose sur plusieurs signaux :

- meilleur score de similarité ;
- score moyen de similarité ;
- nombre de sources pertinentes ;
- statut documentaire ;
- alertes documentaires ;
- incohérences détectées.

Exemple :

```txt
Faible (0.47)
```

Explication possible :

```txt
- Meilleur score de similarité : 0.707
- Score moyen de similarité : 0.662
- 4 sources distinctes pertinentes
- 1 incohérence de version détectée
```

Ce score ne représente pas une vérité absolue.  
Il sert à expliquer pourquoi une réponse doit être utilisée avec plus ou moins de prudence.

---

# 11. Comment le système limite-t-il les hallucinations ?

Le projet applique plusieurs garde-fous :

## 11.1 Refus de répondre sans source pertinente

Si le corpus ne permet pas de répondre :

```txt
Je ne peux pas répondre de manière fiable avec les documents disponibles.
```

## 11.2 Réponses sourcées

Les documents et extraits utilisés sont affichés.

## 11.3 Prompt strict

Ollama reçoit des instructions visant à :

- ne pas inventer de sources ;
- ne pas produire de certitude excessive ;
- respecter les alertes ;
- citer les références utilisées.

## 11.4 Score de confiance

Une réponse fragile est signalée comme telle.

## 11.5 Post-traitement Python

Le système corrige certaines formulations incorrectes du LLM si elles contredisent directement les métadonnées.

---

# 12. Pourquoi avoir ajouté une détection d’incohérences ?

Dans un contexte qualité, deux documents peuvent être liés mais pas totalement alignés.

Le PoC détecte un cas simple :

```txt
CR-AUD-2025-001 mentionne FP-ACH-001 version 1.0
FP-ACH-001 est actuellement indexé en version 1.1
```

Le système produit alors une alerte.

Cette fonctionnalité montre que l’assistant peut servir à autre chose qu’à répondre :

- il peut aussi soutenir une analyse documentaire ;
- il peut signaler des points à vérifier ;
- il peut contribuer à la préparation d’un audit.

---

# 13. Pourquoi avoir ajouté un post-traitement après le LLM ?

Même avec un bon prompt, le modèle peut reformuler de manière incorrecte.

Exemple observé :

```txt
Erreur du LLM :
FP-ACH-001 est en révision.
```

Alors que les métadonnées indiquent :

```txt
FP-ACH-001 est Validé.
```

Le post-traitement ajoute donc une correction automatique.

Cela montre un principe important :

```txt
Le LLM ne doit pas être la seule source d’autorité.
Les règles structurées du système doivent garder la priorité.
```

---

# 14. Pourquoi avoir choisi Ollama ?

Ollama permet d’exécuter un modèle localement.

Avantages :

- pas de coût API ;
- cohérent avec un PoC sans budget ;
- documents conservés localement ;
- bon support pour expérimenter.

Limites :

- modèles plus légers ;
- reformulations parfois imparfaites ;
- qualité parfois inférieure à un service cloud avancé.

Ce choix est pertinent pour une première version locale, avant une éventuelle évolution vers Azure OpenAI ou un autre service d’entreprise.

---

# 15. Pourquoi avoir créé une interface Streamlit ?

Streamlit permet de construire rapidement une interface fonctionnelle pour démontrer le projet.

L’interface permet :

- de poser une question ;
- de choisir le mode de génération ;
- de consulter les sources ;
- de lire les extraits ;
- de voir le score ;
- d’afficher les alertes ;
- de consulter l’historique.

Cela rend le PoC beaucoup plus démonstratif qu’un simple script terminal.

---

# 16. Pourquoi journaliser les interactions ?

La journalisation sert à conserver une trace de :

- la question ;
- la réponse ;
- l’intention détectée ;
- les sources ;
- les alertes ;
- le score ;
- les raisons du score.

Cela apporte :

- traçabilité ;
- auditabilité ;
- possibilité d’analyse a posteriori ;
- amélioration continue du système.

---

# 17. Limites techniques du PoC

Le projet reste volontairement limité.

Principales limites :

- corpus petit et fictif ;
- score de confiance heuristique ;
- détection d’incohérences simple ;
- absence de tests automatiques avancés ;
- pas de benchmark RAG quantitatif ;
- pas de gestion d’accès par utilisateur ;
- pas d’ingestion de PDF réels ;
- pas d’intégration SharePoint ;
- modèle local relativement léger.

---

# 18. Améliorations techniques possibles

Évolutions possibles :

- reranking avancé ;
- évaluation automatique des réponses ;
- benchmark de qualité RAG ;
- citations par section/page ;
- ingestion PDF/Word ;
- métadonnées enrichies ;
- base SQL pour les logs ;
- interface plus avancée ;
- API backend ;
- intégration SharePoint ;
- Azure AI Search ;
- Azure OpenAI ;
- authentification Entra ID ;
- observabilité et supervision.

---

# 19. Questions d’entretien possibles et réponses préparées

## Question 1 — Pourquoi avoir choisi une architecture RAG ?

Réponse :

> Parce qu’un LLM seul ne connaît pas la documentation métier spécifique du projet. Le RAG permet de retrouver des extraits pertinents avant la génération, afin de produire une réponse plus ancrée dans les sources disponibles et plus facilement vérifiable.

---

## Question 2 — Pourquoi chunker les documents ?

Réponse :

> Le chunking permet de travailler sur des passages ciblés plutôt que sur des documents entiers. Cela améliore la recherche documentaire, réduit le bruit, limite la taille du contexte transmis au LLM et permet d’afficher précisément les extraits justificatifs.

---

## Question 3 — Pourquoi ne pas envoyer tous les chunks au LLM ?

Réponse :

> Parce qu’un contexte trop large peut dégrader la génération. Le modèle risque de mélanger les informations, de citer des sources secondaires ou de répondre trop largement. Je préfère sélectionner un petit nombre d’extraits vraiment utiles, tout en affichant davantage d’extraits à l’utilisateur pour conserver la transparence.

---

## Question 4 — Pourquoi utiliser ChromaDB ?

Réponse :

> ChromaDB est suffisante pour un MVP local : elle est simple à intégrer, légère, persistante et adaptée à l’expérimentation sur un petit corpus. Dans une architecture entreprise, on pourrait envisager Azure AI Search ou un moteur plus robuste.

---

## Question 5 — Pourquoi utiliser Ollama ?

Réponse :

> Je voulais un PoC sans coût API et avec une exécution locale pour éviter l’envoi de documents à un fournisseur externe. Ollama correspond bien à cet objectif, même si la qualité de génération peut être inférieure à un modèle cloud plus puissant.

---

## Question 6 — Comment le score de confiance est-il calculé ?

Réponse :

> J’utilise un score heuristique basé sur la similarité des extraits, le nombre de sources, le statut des documents et les alertes détectées. Il ne s’agit pas d’une vérité probabiliste, mais d’un indicateur explicatif destiné à aider l’utilisateur à interpréter la réponse.

---

## Question 7 — Comment limitez-vous les hallucinations ?

Réponse :

> J’utilise plusieurs mécanismes : seuil minimal de pertinence, refus de répondre sans sources suffisantes, affichage des extraits, prompt contraint, score de confiance, alertes, et contrôle Python post-génération pour corriger certaines erreurs factuelles liées aux métadonnées.

---

## Question 8 — Pourquoi détecter les incohérences documentaires ?

Réponse :

> Dans un contexte audit ou qualité, il est utile d’identifier automatiquement des écarts entre documents. Mon PoC détecte par exemple une différence de version entre un compte rendu d’audit et une fiche processus. Cela permet d’aller au-delà de la simple réponse à une question.

---

## Question 9 — Quelles seraient les prochaines étapes pour industrialiser le projet ?

Réponse :

> Je commencerais par intégrer une source documentaire réelle, comme SharePoint, ajouter une authentification Entra ID, remplacer ou compléter ChromaDB par Azure AI Search, renforcer l’évaluation du RAG, ajouter une base structurée pour les logs et améliorer la gestion des droits d’accès.

---

## Question 10 — Quelle est la principale valeur ajoutée du projet ?

Réponse :

> Sa valeur est de montrer qu’un assistant IA documentaire peut être conçu de manière plus fiable qu’un chatbot générique : avec des sources visibles, une prudence explicite, une traçabilité, des alertes documentaires et une logique de validation humaine.

---

# 20. Message clé à retenir

> Ce projet illustre une architecture RAG complète et pédagogique, pensée non seulement pour générer une réponse, mais aussi pour garantir un minimum de fiabilité, d’explicabilité et d’auditabilité dans un contexte documentaire métier.
