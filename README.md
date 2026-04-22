# Mini-Projet OIE : Optimisation de la Diffusion d'Informations sur les Réseaux Sociaux

Ce dépôt contient le code source et le rapport académique pour le Mini-Projet du cours d'**Optimisation Industrielle et Économique (OIE)**. Ce projet s'inscrit dans le cadre du Master 1 Systèmes d'Information et Données (SID) à l'Université des Sciences et de la Technologie d'Oran (USTO).

**Thème 17 :** Optimisation de la diffusion d’informations sur les réseaux sociaux.

## 📋 Description du Projet
Le projet vise à résoudre le problème de **Maximisation de l'Influence** sous contrainte budgétaire. L'objectif est de sélectionner un ensemble optimal d'utilisateurs initiaux ("nœuds sources") pour maximiser la propagation d'une information sur un réseau social. 

Contrairement aux approches déterministes classiques, ce projet modélise la diffusion comme un processus probabiliste basé sur les compétences sociales des utilisateurs. L'approche choisie est une modélisation par Programmation Linéaire en Nombres Entiers (MILP) stochastique basée sur des scénarios.

## 📁 Structure du Dépôt
* `AMPL/`
  * `diffusion.mod` : Fichier de modélisation mathématique contenant les variables, la fonction objectif et les contraintes.
  * `diffusion.dat` : Fichier de données contenant l'instance testée (graphe, scénarios stochastiques, budget).
  * `diffusion.run` : Script d'exécution paramétré pour utiliser le solveur CPLEX.
* `Python/`
  * `influence_maximization.py` : Script Python utilisant PuLP / Amplpy pour modéliser le problème.
  * `example_instance.py` : Script Python pour résoudre une instance du problème.
* `Docs/`
  * `Rapport_OIE.pdf` : Le rapport final détaillant la modélisation mathématique, l'implémentation et l'analyse des résultats.

## 🚀 Comment exécuter le code

### 1. Implémentation AMPL (avec CPLEX)
Prérequis : Avoir AMPL et le solveur CPLEX installés.
1. Ouvrez l'interface de ligne de commande AMPL.
2. Naviguez vers le dossier contenant les fichiers AMPL.
3. Exécutez la commande suivante :
   ```ampl
   include diffusion.run;
   ```
4. Les résultats optimaux (nœuds sources choisis et espérance de la diffusion) s'afficheront dans la console.

### 2. Implémentation Python
Prérequis : Avoir Python installé avec les bibliothèques requises.
1. Installez les dépendances nécessaires (ex: `pip install pulp amplpy`).
2. Exécutez le script depuis votre terminal :
   ```bash
   python Python/main.py
   ```

## 👥 Équipe du Projet (Groupe G1) 
* **MELLIKECHE Yanis** - Tâche 1 : Description du problème, Analyse des résultats, Conclusion et Bibliographie.
* **AMOURI Abdelillah** - Tâche 2 : Hypothèses et Modélisation mathématique.
* **BENDOUKHA Mohammed El Amine** - Tâche 3 : Modèle AMPL et Résolution.
* **BOUGHANMI Aymène** - Tâche 4 : Code Python et Résolution.

## 📚 Références Principales
* DEKHICI L. (2025). *Optimization in Industry and Economy*. Cours Master 1 SID, USTO.
* Kempe D., Kleinberg J., Tardos E. (2003). *Maximizing the Spread of Influence through a Social Network*.
* Kermani, M. A. M. A., et al. (2021). *A robust optimization model for influence maximization in social networks with heterogeneous nodes*. Computational Social Networks, 8(17).
