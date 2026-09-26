# Evaluation DevOps

Projet réalisé dans le cadre de l'évaluation DevOps.

Ce projet met en œuvre une chaîne DevOps complète autour d'une application
Flask utilisant Redis, Docker, GitHub Actions, GitHub Container Registry
et Prometheus.

## Architecture

Les principaux composants sont :

- **Flask** : API HTTP
- **Redis** : stockage du compteur de visites
- **Gunicorn** : serveur WSGI
- **Docker** : conteneurisation
- **Docker Compose** : environnement local
- **GitHub Actions** : CI/CD
- **GHCR** : registre des images Docker
- **Prometheus** : métriques et alerting
- **Self-hosted runner** : déploiement de production

Architecture simplifiée :

    GitHub
       |
    CI + CD
       |
      GHCR
       |
    Self-hosted Runner
       |
    Docker Production
       |
    +-------+
    |       |
   Flask   Redis
    |
 Port 5050

## Endpoints

### GET /

Retourne l'état de l'application et incrémente le compteur de visites stocké
dans Redis.

Exemple :

    {
      "message": "Evaluation DevOps ESIEA",
      "status": "ok",
      "visits": 1,
      "version": "1.0.0",
      "sha": "<commit>"
    }

### GET /health

Vérifie l'état de l'application et la connexion à Redis.

Une application fonctionnelle retourne HTTP 200 :

    {
      "status": "healthy",
      "redis": "ok",
      "version": "1.0.0",
      "sha": "<commit>"
    }

Si Redis n'est pas disponible, le endpoint retourne HTTP 503.

### GET /metrics

Expose les métriques au format Prometheus.

Métriques principales :

- `http_requests_total`
- `http_request_duration_seconds`
- `app_info`

## Installation locale

### Prérequis

- Git
- Python 3.12
- Docker
- Docker Compose

### Cloner le dépôt

    git clone https://github.com/Cronix2/evaluation-devops.git
    cd evaluation-devops

### Installer les dépendances Python

Sous PowerShell :

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt

## Docker Compose

Construire et démarrer l'environnement :

    docker compose up -d --build

Vérifier les conteneurs :

    docker compose ps

L'application locale est disponible sur :

    http://localhost:5000

Tests rapides :

    Invoke-RestMethod http://127.0.0.1:5000/
    Invoke-RestMethod http://127.0.0.1:5000/health
    Invoke-WebRequest http://127.0.0.1:5000/metrics

Arrêter l'environnement :

    docker compose down

## Tests

Les tests utilisent **pytest**.

Le projet contient :

- des tests unitaires avec Redis simulé ;
- un test du endpoint `/health` ;
- un test du endpoint `/metrics` ;
- un test d'intégration utilisant une véritable instance Redis.

Exécution :

    python -m pytest -v

Avec couverture :

    python -m pytest --cov=app --cov-report=term-missing tests

## Qualité du code

Flake8 vérifie la qualité du code Python :

    python -m flake8 app tests

## Docker

Le projet utilise un **Dockerfile multi-stage**.

Le premier stage installe les dépendances Python.

Le second stage construit l'image d'exécution.

Le conteneur :

- utilise Python 3.12 ;
- utilise Gunicorn ;
- fonctionne avec un utilisateur non-root ;
- possède un HEALTHCHECK ;
- expose le port 5000.

## Intégration continue

Le workflow CI se trouve dans :

    .github/workflows/ci.yml

Il est exécuté lors :

- des push sur `main` ;
- des pull requests vers `main`.

La CI réalise :

1. le lint avec Flake8 ;
2. les tests sous Python 3.11 ;
3. les tests sous Python 3.12 ;
4. les tests d'intégration avec Redis ;
5. la génération des rapports de tests et de couverture ;
6. la construction de l'image Docker ;
7. la publication de l'image comme artifact GitHub Actions.

Le build Docker n'est exécuté que si le lint et les tests réussissent.

## Déploiement continu

Le workflow CD se trouve dans :

    .github/workflows/cd.yml

Après une CI réussie sur `main`, le pipeline :

1. construit l'image Docker ;
2. publie l'image sur GHCR ;
3. applique les tags ;
4. utilise le runner self-hosted de production ;
5. démarre Redis ;
6. déploie l'application ;
7. effectue plusieurs healthchecks ;
8. valide le déploiement ou déclenche un rollback.

## GitHub Container Registry

Les images sont publiées dans :

    ghcr.io/cronix2/evaluation-devops

Les tags utilisés comprennent :

- `latest`
- le SHA court du commit
- `1.0.0`

Exemple :

    docker pull ghcr.io/cronix2/evaluation-devops:latest

## Production

La production utilise deux conteneurs :

- `evaluation-devops-production`
- `evaluation-devops-redis`

Ils communiquent via :

    evaluation-devops-production-net

L'application de production est exposée sur :

    http://127.0.0.1:5050

Vérification :

    Invoke-RestMethod http://127.0.0.1:5050/
    Invoke-RestMethod http://127.0.0.1:5050/health

## Rollback automatique

Avant un nouveau déploiement, le workflow mémorise l'image actuellement
déployée.

Si le nouveau conteneur ne passe pas le healthcheck :

1. le nouveau conteneur est supprimé ;
2. l'image précédente est récupérée ;
3. l'ancienne version est redéployée ;
4. son endpoint `/health` est vérifié.

Cette stratégie permet de revenir automatiquement à la dernière version
fonctionnelle.

## Observabilité

L'application expose les métriques Prometheus via :

    /metrics

Elles permettent notamment de suivre :

- le nombre de requêtes HTTP ;
- les codes HTTP ;
- la latence ;
- la version de l'application ;
- le commit actuellement déployé.

## Alerting Prometheus

Les règles sont définies dans :

    prometheus/alerts.yml

### HighHttp5xxErrorRate

Déclenchée lorsque plus de **5 % des requêtes HTTP retournent un code 5xx
pendant au moins 5 minutes**.

### HighHttpRequestLatencyP95

Déclenchée lorsque le **p95 de latence dépasse 500 ms pendant au moins
10 minutes**.

## Structure

    evaluation-devops/
    |
    |-- .github/
    |   `-- workflows/
    |       |-- ci.yml
    |       `-- cd.yml
    |
    |-- app/
    |   |-- __init__.py
    |   `-- main.py
    |
    |-- prometheus/
    |   `-- alerts.yml
    |
    |-- tests/
    |   |-- test_app.py
    |   `-- test_integration_redis.py
    |
    |-- .dockerignore
    |-- .flake8
    |-- .gitignore
    |-- docker-compose.yml
    |-- Dockerfile
    |-- pytest.ini
    |-- requirements.txt
    `-- README.md

## Technologies

- Python 3.12
- Flask
- Redis
- Gunicorn
- pytest
- Flake8
- Docker
- Docker Compose
- GitHub Actions
- GitHub Container Registry
- Prometheus

## Auteur

Cronix2

Projet réalisé dans le cadre de l'évaluation DevOps.
