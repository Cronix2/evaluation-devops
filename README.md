# Evaluation DevOps — CI/CD, Docker & Observabilité

[![CI](https://github.com/Cronix2/evaluation-devops/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Cronix2/evaluation-devops/actions/workflows/ci.yml)
[![CD](https://github.com/Cronix2/evaluation-devops/actions/workflows/cd.yml/badge.svg?branch=main)](https://github.com/Cronix2/evaluation-devops/actions/workflows/cd.yml)

Projet réalisé dans le cadre de l'évaluation DevOps.

L'objectif est de mettre en place une chaîne DevOps complète autour d'une application Flask utilisant Redis, avec conteneurisation Docker, intégration continue, déploiement continu, publication d'images sur GitHub Container Registry et observabilité Prometheus.

---

## Sommaire

- [Architecture](#architecture)
- [Technologies utilisées](#technologies-utilisées)
- [Structure du projet](#structure-du-projet)
- [Installation et lancement](#installation-et-lancement)
- [Endpoints](#endpoints)
- [Tests](#tests)
- [Docker](#docker)
- [Intégration continue — CI](#intégration-continue--ci)
- [Déploiement continu — CD](#déploiement-continu--cd)
- [GitHub Container Registry](#github-container-registry)
- [Action GitHub locale réutilisable](#action-github-locale-réutilisable)
- [Observabilité Prometheus](#observabilité-prometheus)
- [Alertes Prometheus](#alertes-prometheus)
- [Sécurité](#sécurité)
- [Validation du projet](#validation-du-projet)

---

# Architecture

Le projet repose sur les composants suivants :

```text
                         GitHub
                           │
                     Push / Pull Request
                           │
                           ▼
                  ┌─────────────────┐
                  │   GitHub CI     │
                  │                 │
                  │ • Flake8        │
                  │ • YAML lint     │
                  │ • Python 3.11   │
                  │ • Python 3.12   │
                  │ • Redis         │
                  │ • Pytest        │
                  │ • Coverage      │
                  │ • Docker build  │
                  └────────┬────────┘
                           │
                      CI réussie
                           │
                           ▼
                  ┌─────────────────┐
                  │   GitHub CD     │
                  │                 │
                  │ Build image     │
                  │ Push GHCR       │
                  │ Deploy          │
                  │ Healthcheck     │
                  │ Rollback        │
                  └────────┬────────┘
                           │
                           ▼
              ghcr.io/cronix2/evaluation-devops
                           │
                           ▼
                  ┌─────────────────┐
                  │   Production    │
                  │                 │
                  │ Flask/Gunicorn  │
                  │ Redis           │
                  │ /health         │
                  │ /metrics        │
                  └─────────────────┘
```

---

# Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python 3.11 / 3.12 | Application et matrice de tests |
| Flask | API HTTP |
| Gunicorn | Serveur WSGI de production |
| Redis 7.4.1 Alpine | Service de données |
| Pytest | Tests automatisés |
| pytest-cov | Couverture des tests |
| Flake8 | Lint Python |
| yamllint | Validation des fichiers YAML |
| Docker | Conteneurisation |
| Docker Compose | Orchestration locale |
| GitHub Actions | CI/CD |
| GitHub Container Registry | Registry d'images Docker |
| Prometheus Client | Exposition des métriques |

---

# Structure du projet

```text
evaluation-devops/
│
├── .github/
│   ├── actions/
│   │   └── setup-python/
│   │       └── action.yml
│   │
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── prometheus/
│   └── alerts.yml
│
├── tests/
│   ├── test_app.py
│   └── test_integration_redis.py
│
├── .dockerignore
├── .flake8
├── .gitignore
├── .yamllint.yml
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# Installation et lancement

## Prérequis

Les outils suivants sont nécessaires :

- Git
- Docker
- Docker Compose

Pour le développement ou l'exécution des tests hors Docker :

- Python 3.11 ou Python 3.12

---

## Cloner le dépôt

```bash
git clone https://github.com/Cronix2/evaluation-devops.git
cd evaluation-devops
```

---

## Lancement avec Docker Compose

Construire et démarrer l'ensemble de l'environnement :

```bash
docker compose up -d --build
```

Vérifier les conteneurs :

```bash
docker compose ps
```

L'application est alors accessible sur :

```text
http://localhost:5050
```

---

## Vérifier l'application

Endpoint principal :

```bash
curl http://localhost:5050/
```

Healthcheck :

```bash
curl http://localhost:5050/health
```

Métriques Prometheus :

```bash
curl http://localhost:5050/metrics
```

---

## Arrêter l'environnement

```bash
docker compose down
```

---

# Endpoints

## `GET /`

Endpoint principal de l'application.

Exemple de réponse :

```json
{
  "message": "Hello DevOps!",
  "status": "ok"
}
```

---

## `GET /health`

Endpoint utilisé pour vérifier l'état de l'application et de Redis.

Il expose notamment :

- l'état général de l'application ;
- l'état de Redis ;
- la version de l'application ;
- le SHA du commit déployé.

Exemple :

```json
{
  "redis": "ok",
  "sha": "9708fc3",
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## `GET /metrics`

Expose les métriques de l'application au format Prometheus.

```bash
curl http://localhost:5050/metrics
```

---

# Tests

Les tests sont situés dans :

```text
tests/
├── test_app.py
└── test_integration_redis.py
```

Le projet contient à la fois des tests applicatifs et un test d'intégration avec Redis.

## Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

## Lancer les tests

```bash
python -m pytest tests
```

## Tests avec couverture

```bash
python -m pytest \
  --cov=app \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml \
  tests
```

Le workflow CI génère également des rapports JUnit et les publie comme artifacts GitHub Actions.

---

# Lint Python

Le code Python est contrôlé avec Flake8.

```bash
python -m flake8 app tests
```

Configuration :

```text
.flake8
```

---

# Lint YAML

Les fichiers YAML du projet sont contrôlés avec `yamllint`.

Installation :

```bash
python -m pip install yamllint==1.35.1
```

Validation :

```bash
python -m yamllint \
  -c .yamllint.yml \
  .github/workflows/ci.yml \
  .github/workflows/cd.yml \
  .github/actions/setup-python/action.yml \
  prometheus/alerts.yml \
  docker-compose.yml
```

---

# Docker

## Dockerfile

L'application utilise un Dockerfile multi-stage afin de séparer la construction des dépendances de l'image finale.

L'image finale :

- utilise une version Python précise ;
- repose sur une image légère ;
- fonctionne avec un utilisateur non-root ;
- possède un `HEALTHCHECK` réel ;
- utilise Gunicorn pour servir l'application.

---

## Docker Compose

Docker Compose orchestre au minimum :

```text
Application Flask
       │
       ▼
     Redis
```

Le service Redis utilise une image versionnée :

```text
redis:7.4.1-alpine
```

Le démarrage complet de l'environnement s'effectue avec :

```bash
docker compose up -d --build
```

---

# Intégration continue — CI

Workflow :

```text
.github/workflows/ci.yml
```

La CI est exécutée lors :

- d'un push sur `main` ;
- d'une Pull Request vers `main`.

Elle est organisée autour de quatre jobs.

## `lint`

Effectue :

- installation de Python ;
- restauration du cache pip ;
- installation des dépendances ;
- lint Python avec Flake8 ;
- lint YAML avec yamllint.

## `test`

Utilise une matrice :

```text
Python 3.11
Python 3.12
```

Un véritable service Redis est lancé dans GitHub Actions.

Le job vérifie Redis avant d'exécuter les tests.

Il génère :

- un rapport de couverture ;
- un rapport XML de couverture ;
- un rapport JUnit pour chaque version de Python.

Les rapports sont conservés comme artifacts GitHub Actions.

## `build`

Ce job :

- configure Docker Buildx ;
- construit l'image Docker ;
- utilise le cache GitHub Actions ;
- inspecte l'image ;
- exporte l'image ;
- publie l'image comme artifact.

## `ci-ok`

Le dernier job vérifie explicitement que les jobs nécessaires ont réussi.

La CI n'est considérée comme valide que si :

```text
lint  = success
test  = success
build = success
```

Chaque job possède également un `timeout-minutes` afin d'éviter une exécution bloquée indéfiniment.

---

# Cache CI

Le projet utilise plusieurs mécanismes de cache.

Pour Python :

```yaml
cache: pip
```

Le cache est partagé via `actions/setup-python`.

Pour Docker Buildx :

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

Cela permet d'accélérer les exécutions suivantes de la CI.

---

# Déploiement continu — CD

Workflow :

```text
.github/workflows/cd.yml
```

Le CD est séparé de la CI.

Il peut être déclenché après la réussite de la CI sur `main` et dispose également d'un déclenchement manuel `workflow_dispatch`.

Le déploiement cible l'environnement :

```text
production
```

---

## Publication de l'image

Lorsque les conditions de déploiement sont satisfaites, une image Docker est construite et publiée sur GitHub Container Registry.

Registry :

```text
ghcr.io
```

Image :

```text
ghcr.io/cronix2/evaluation-devops
```

L'authentification utilise le `GITHUB_TOKEN` fourni par GitHub Actions avec des permissions explicites.

---

# GitHub Container Registry

Les images de l'application sont publiées sous :

```text
ghcr.io/cronix2/evaluation-devops
```

Les images utilisent plusieurs types de tags permettant notamment d'identifier :

- la version courante ;
- le commit correspondant ;
- la version de release.

Exemple de récupération d'une image :

```bash
docker pull ghcr.io/cronix2/evaluation-devops:latest
```

---

# Déploiement en production

Le déploiement est effectué par le workflow CD sur un runner self-hosted.

Le processus :

```text
CI réussie
    │
    ▼
Construction image
    │
    ▼
Publication GHCR
    │
    ▼
Récupération de l'image
    │
    ▼
Déploiement du conteneur
    │
    ▼
Vérification /health
    │
    ├── OK ──► déploiement validé
    │
    └── KO ──► rollback
```

---

# Healthcheck et rollback

Après le déploiement, le workflow vérifie réellement :

```text
/health
```

Plusieurs tentatives sont réalisées afin de laisser le temps à l'application de démarrer.

Si l'application ne devient pas saine, le workflow échoue et le mécanisme de rollback permet de revenir à l'image précédente.

Cela évite de conserver en production une version défectueuse.

---

# Action GitHub locale réutilisable

Une action composite locale est disponible dans :

```text
.github/actions/setup-python/action.yml
```

Elle centralise la préparation de l'environnement Python.

Elle réalise notamment :

1. l'installation de la version Python demandée ;
2. la restauration du cache pip ;
3. la mise à jour de pip ;
4. l'installation des dépendances du projet.

Elle accepte la version de Python comme paramètre :

```yaml
with:
  python-version: "3.12"
```

Elle est réutilisée par plusieurs jobs de la CI afin d'éviter la duplication de la logique de configuration Python.

---

# Observabilité Prometheus

L'application expose :

```text
GET /metrics
```

Les métriques sont générées avec `prometheus-client`.

---

## Compteur de requêtes HTTP

La métrique :

```text
http_requests_total
```

permet de compter les requêtes HTTP.

Elle permet notamment une différenciation selon la route et le code HTTP.

---

## Histogramme de latence

La métrique :

```text
http_request_duration_seconds
```

mesure la durée des requêtes HTTP.

Elle permet notamment de calculer les percentiles de latence comme le p95.

---

## Informations de l'application

La métrique :

```text
app_info
```

expose des informations permettant d'identifier la version de l'application et le commit correspondant au déploiement.

---

# Alertes Prometheus

Les règles sont définies dans :

```text
prometheus/alerts.yml
```

Deux situations principales sont surveillées.

## Taux d'erreurs HTTP 5xx

Une alerte permet de détecter une proportion anormalement importante de réponses HTTP `5xx`.

L'objectif est de détecter rapidement une dégradation fonctionnelle de l'application.

## Latence p95 élevée

Une seconde alerte surveille le percentile 95 de la latence HTTP.

Elle permet de détecter une dégradation persistante des performances.

---

# Sécurité

Plusieurs mesures sont appliquées dans le projet :

- utilisation d'un utilisateur non-root dans l'image Docker ;
- permissions GitHub Actions explicitement définies ;
- utilisation du `GITHUB_TOKEN` plutôt que d'un token stocké dans le dépôt ;
- absence de credentials codés en dur ;
- `.gitignore` pour éviter de versionner les fichiers locaux inutiles ;
- `.dockerignore` pour limiter le contexte envoyé au daemon Docker ;
- healthchecks avant validation d'un déploiement ;
- rollback en cas d'échec du déploiement.

---

# Validation du projet

La chaîne complète a été testée avec succès :

```text
Push Git
   │
   ▼
CI
   ├── Flake8                    ✓
   ├── YAML lint                 ✓
   ├── Python 3.11 + Redis       ✓
   ├── Python 3.12 + Redis       ✓
   ├── Coverage / JUnit          ✓
   ├── Build Docker              ✓
   └── CI OK                     ✓
          │
          ▼
CD
   ├── Build image              ✓
   ├── Publication GHCR         ✓
   ├── Déploiement              ✓
   ├── Healthcheck              ✓
   └── Production               ✓
          │
          ▼
Application
   ├── GET /                    ✓
   ├── GET /health              ✓
   ├── Redis                    ✓
   └── GET /metrics             ✓
```

Le déploiement permet ainsi de conserver une correspondance entre :

```text
Commit Git
    ↓
Image Docker
    ↓
Déploiement
    ↓
SHA exposé par /health
```

---

# Commandes essentielles

## Lancer le projet

```bash
docker compose up -d --build
```

## Vérifier les conteneurs

```bash
docker compose ps
```

## Tester l'application

```bash
curl http://localhost:5050/
curl http://localhost:5050/health
curl http://localhost:5050/metrics
```

## Lancer les tests

```bash
python -m pytest tests
```

## Lancer Flake8

```bash
python -m flake8 app tests
```

## Arrêter le projet

```bash
docker compose down
```

---

# Auteur

**Clément Linossier**

Projet réalisé dans le cadre de l'évaluation DevOps.
