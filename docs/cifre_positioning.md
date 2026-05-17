# Positionnement du projet dans une perspective CIFRE

## Titre du projet

**Assistant IA RAG sécurisé et explicable pour l’exploitation de documentations qualité et la préparation d’éléments d’audit**

---

# 1. Présentation générale

Ce projet consiste à développer un assistant IA RAG capable d’interroger une documentation qualité ISO fictive afin de produire :

- des réponses sourcées ;
- des extraits justificatifs ;
- un score de confiance ;
- des alertes documentaires ;
- une détection simple d’incohérences ;
- une traçabilité des interactions.

L’objectif dépasse la simple génération de texte.  
Il s’agit d’étudier comment rendre un assistant IA documentaire :

- plus fiable ;
- plus explicable ;
- plus contrôlable ;
- plus adapté aux environnements d’entreprise ;
- plus facilement intégrable dans un système d’information existant.

---

# 2. Problématique générale

La problématique explorée peut être formulée ainsi :

> Comment concevoir un assistant IA RAG capable d’exploiter une documentation métier ou qualité tout en garantissant un niveau satisfaisant de fiabilité, de traçabilité, d’explicabilité et de contrôle humain ?

Cette question se situe au croisement de plusieurs domaines :

- intelligence artificielle générative ;
- systèmes d’information ;
- gouvernance documentaire ;
- qualité et conformité ;
- ingénierie logicielle ;
- sécurité des données.

---

# 3. Justification du choix du domaine qualité / audit

Le domaine de la qualité et de l’audit constitue un terrain pertinent pour étudier les assistants RAG, car il implique :

- des documents structurés ;
- des référentiels internes ;
- des exigences de versionnement ;
- des procédures applicables ou non applicables ;
- des preuves à retrouver ;
- des risques d’interprétation ;
- un besoin fort de traçabilité.

Dans ce contexte, une réponse incorrecte peut avoir plusieurs conséquences :

- interprétation erronée d’une procédure ;
- mauvaise utilisation d’un document obsolète ou en révision ;
- oubli d’une preuve attendue ;
- confusion entre une règle et un enregistrement ;
- perte de confiance dans l’outil.

Le projet permet donc d’étudier concrètement la question de la **fiabilité de l’IA générative dans un contexte documentaire sensible**.

---

# 4. Hypothèse de travail

L’hypothèse générale du projet peut être formulée ainsi :

> Un assistant RAG devient plus exploitable dans un contexte professionnel lorsqu’il associe la génération de réponses à des mécanismes de contrôle complémentaires : sélection raisonnée des sources, score de confiance explicable, alertes documentaires, détection d’incohérences et validation humaine.

Cette hypothèse repose sur l’idée que la performance d’un assistant IA ne dépend pas uniquement du modèle de langage, mais de l’ensemble du système qui l’entoure.

---

# 5. Axes de recherche possibles

## 5.1 Fiabilité des réponses RAG

Questions associées :

- Comment limiter les hallucinations ?
- Comment détecter qu’un corpus est insuffisant pour répondre ?
- Comment arbitrer entre réponse générée et refus prudent ?
- Quels critères utiliser pour estimer la fiabilité d’une réponse ?

Le PoC répond déjà partiellement à ces questions avec :

- un seuil minimal de similarité ;
- un mode “je ne sais pas” ;
- un affichage des sources ;
- un score de confiance simple.

---

## 5.2 Sélection du contexte documentaire

Questions associées :

- Faut-il transmettre tous les chunks retrouvés au LLM ?
- Comment réduire le bruit documentaire ?
- Comment intégrer des règles métier dans la sélection des sources ?
- Comment privilégier une preuve documentaire plutôt qu’un document générique ?

Le PoC explore ces enjeux avec :

- la distinction entre extraits affichés et extraits envoyés au LLM ;
- la détection d’intention ;
- des bonus métier selon le type de question ;
- des références prioritaires selon l’intention.

---

## 5.3 Explicabilité et score de confiance

Questions associées :

- Comment expliquer à un utilisateur pourquoi une réponse est considérée comme fiable ou fragile ?
- Comment agréger plusieurs signaux hétérogènes ?
- Comment rendre visible l’incertitude sans rendre l’outil inutilisable ?

Le projet propose un score calculé à partir :

- de la similarité ;
- du nombre de sources ;
- du statut documentaire ;
- des alertes ;
- des incohérences détectées.

Ce score est accompagné d’une explication textuelle.

---

## 5.4 Détection d’incohérences documentaires

Questions associées :

- Comment identifier automatiquement des conflits entre documents ?
- Comment distinguer une différence de version d’un document réellement obsolète ?
- Comment éviter que le LLM surinterprète une alerte ?

Le PoC détecte une incohérence simple :

```txt
CR-AUD-2025-001 mentionne FP-ACH-001 version 1.0
FP-ACH-001 est indexé en version 1.1
```

Le système :

- détecte l’écart ;
- produit une alerte ;
- réduit le score de confiance ;
- ajoute un contrôle de cohérence post-génération.

---

## 5.5 Gouvernance documentaire et SI d’entreprise

Questions associées :

- Comment intégrer un assistant RAG dans un environnement documentaire existant ?
- Comment respecter les droits d’accès ?
- Comment connecter l’outil à SharePoint ou Microsoft 365 ?
- Comment gérer la traçabilité des consultations ?

Une extension naturelle du PoC pourrait reposer sur :

- SharePoint comme source documentaire ;
- Azure AI Search comme moteur de recherche vectorielle ;
- Azure OpenAI pour la génération ;
- Microsoft Entra ID pour l’authentification ;
- Dataverse ou SQL pour les logs ;
- Power BI pour la supervision.

---

# 6. Intérêt pour les systèmes d’information

Ce projet s’inscrit pleinement dans le champ des systèmes d’information, car il traite :

- l’accès à la connaissance ;
- la structuration de l’information ;
- l’intégration de composants IA dans un SI ;
- la gouvernance des données ;
- la traçabilité ;
- la confiance dans les outils numériques ;
- l’automatisation raisonnée des processus documentaires.

Il ne s’agit pas seulement d’un problème de modèle d’IA, mais d’un problème d’**architecture de système**, de **qualité de données** et de **maîtrise des usages**.

---

# 7. Intérêt industriel potentiel

Dans un contexte d’entreprise, un assistant de ce type pourrait contribuer à :

- retrouver plus vite des procédures internes ;
- accompagner la préparation d’audits ;
- fiabiliser l’accès à la documentation ;
- aider à identifier des écarts documentaires ;
- réduire le temps passé à rechercher de l’information ;
- renforcer la traçabilité des consultations ;
- faciliter l’appropriation des référentiels internes.

Des secteurs particulièrement concernés pourraient être :

- industrie ;
- énergie ;
- qualité ;
- santé ;
- défense ;
- finance ;
- secteurs fortement réglementés.

---

# 8. Formulation possible pour une candidature CIFRE

## Version courte

> Je souhaite approfondir les problématiques de fiabilité, d’explicabilité et de gouvernance des assistants IA RAG appliqués aux systèmes d’information. Mon PoC d’assistant documentaire ISO m’a permis d’explorer les fondations techniques d’un tel système : recherche vectorielle, génération contrôlée, détection d’intention, score de confiance, alertes documentaires et traçabilité. Une poursuite en CIFRE me permettrait d’étudier ces enjeux dans un cadre industriel réel, en lien avec la gestion documentaire, la conformité et l’intégration de l’IA dans les SI.

---

## Version plus développée

> Dans le cadre de mon travail personnel, j’ai conçu un PoC d’assistant IA RAG destiné à interroger une documentation qualité ISO fictive. L’outil ne se limite pas à générer une réponse textuelle : il restitue les sources, affiche les extraits pertinents, fournit un score de confiance explicable, signale les documents fragiles ou en révision, détecte certaines incohérences de version et journalise les interactions.
>
> Ce projet m’a amené à m’intéresser à une question plus large : comment concevoir des assistants IA documentaires réellement fiables, intégrables et acceptables dans des environnements d’entreprise où la qualité de l’information, la traçabilité et la responsabilité restent essentielles ?
>
> Une CIFRE sur ce sujet me semblerait particulièrement pertinente pour approfondir la fiabilité des architectures RAG, leur gouvernance dans les systèmes d’information, les méthodes d’évaluation des réponses, ainsi que les conditions d’industrialisation dans un environnement documentaire réel.

---

# 9. Ce que ce projet met en valeur dans mon profil

Ce PoC valorise plusieurs dimensions de mon parcours :

## Compétences techniques

- Python ;
- architecture RAG ;
- ChromaDB ;
- Ollama ;
- Streamlit ;
- structuration documentaire ;
- logs et supervision ;
- règles métier de post-traitement.

## Compétences SI

- modélisation d’un flux documentaire ;
- gouvernance de l’information ;
- auditabilité ;
- traçabilité ;
- sécurité ;
- intégration future à Microsoft 365 et Azure.

## Compétences analytiques

- capacité à identifier les limites d’un système ;
- volonté de réduire les hallucinations ;
- compréhension du rôle de la validation humaine ;
- raisonnement orienté qualité et fiabilité.

---

# 10. Limites actuelles du PoC dans une perspective de recherche

Le PoC reste volontairement simple :

- corpus limité ;
- documents fictifs ;
- détection d’incohérences élémentaire ;
- modèle local léger ;
- score de confiance heuristique ;
- pas encore de benchmark automatique ;
- pas encore de véritable gestion des habilitations ;
- pas de connecteur réel à un SI documentaire d’entreprise.

Ces limites sont intéressantes, car elles ouvrent justement sur des perspectives de recherche et d’industrialisation.

---

# 11. Pistes d’approfondissement pour un travail de recherche

Plusieurs prolongements peuvent être envisagés :

- comparaison de stratégies de chunking ;
- comparaison de bases vectorielles ;
- étude de différentes méthodes de reranking ;
- mesure de la robustesse face aux documents contradictoires ;
- évaluation automatique des citations ;
- conception d’indicateurs de confiance plus rigoureux ;
- génération de jeux de tests RAG ;
- étude de l’acceptabilité utilisateur ;
- intégration de politiques de sécurité et d’accès documentaires ;
- journalisation auditable des interactions avec un assistant IA.

---

# 12. Conclusion

Ce projet constitue une première approche concrète d’un sujet au cœur de l’IA appliquée aux systèmes d’information :

> Concevoir des assistants capables d’exploiter efficacement la connaissance de l’entreprise tout en restant fiables, transparents, gouvernés et compatibles avec des exigences métier fortes.

Le PoC développé montre déjà plusieurs principes essentiels :

- réponse sourcée ;
- prudence face aux données insuffisantes ;
- détection d’alertes ;
- traçabilité ;
- intégration d’une logique métier ;
- validation humaine maintenue au centre du dispositif.

Dans une perspective CIFRE, il pourrait devenir le point de départ d’un travail plus approfondi sur les assistants IA documentaires fiables pour les organisations.
