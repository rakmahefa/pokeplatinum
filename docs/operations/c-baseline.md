# Baseline C/Linux — procédure reproductible

> **État au 2026-10-22 :** runbook initial écrit ; une exécution locale froide n'a pas encore été réalisée dans cette session. Ne pas déclarer la baseline reproductible avant d'avoir enregistré les preuves d'une exécution propre.

## 1. Révision candidate

- Dépôt : `https://github.com/rakmahefa/pokeplatinum.git`
- Branche : `pc_port`
- Révision candidate déjà utilisée par la CI historique : `ef958c943b2fd535750e8e4c80215942aebaf465`
- Build Linux historique : [run 39722714025](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714025), conclusion GitHub Actions `success`.
- Build ARM historique : [run 39722714020](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714020), conclusion `success`.
- Build Windows historique : [run 39722714273](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714273), encore indiqué `in_progress` lors du dernier relevé ; résultat final non confirmé.

Ces statuts attestent uniquement de l'exécution des jobs historiques. Le workflow nouveau [baseline-c-linux.yml](../../.github/workflows/baseline-c-linux.yml) est conçu pour effectuer un build ciblé sur les changements C/build ou sur déclenchement manuel, puis conserver un manifeste des tailles et SHA-256 sans téléverser les exécutables. Tant que son premier run n'a pas fini et que ses sorties ne sont pas examinées, la baseline reste **candidate**, pas validée.

## 2. Prérequis

- Git et un clone propre du dépôt.
- Docker Engine/CLI installé, démarré et utilisable par l'utilisateur courant.
- Les permissions locales requises par `drun.sh` pour utiliser Docker, `/dev/fuse` et l'affichage X11 monté dans le conteneur.
- Les paquets hôte présents dans le runner historique Linux : `fuse`, `git`, `python3`, `wget`, `zip`. Le runner GitHub disposait aussi de Docker.
- Assez d'espace disque pour l'image Docker, les dépendances téléchargées et le build.

`drun.sh` ne construit l'image `pokeplatinum-build` que si elle n'existe pas. Une ancienne image locale peut donc affecter la reproductibilité. Sur une machine persistante, utiliser une image fraîche et vérifier sa provenance. Ne supprimer aucun conteneur ou volume utilisateur pour « nettoyer » le build.

## 3. Protocole Linux

Utiliser un clone séparé afin de garder la révision candidate immuable. Ne pas placer de ROM, de sauvegarde personnelle ou de ressource extraite non redistribuable dans ce clone pour ce protocole.

```bash
git clone --branch pc_port https://github.com/rakmahefa/pokeplatinum.git
cd pokeplatinum
git switch --detach ef958c943b2fd535750e8e4c80215942aebaf465
git status --short
git rev-parse HEAD
docker version
```

Avant le build, `git status --short` doit être vide et `git rev-parse HEAD` doit afficher exactement la SHA de la révision candidate.

Reproduire les commandes de compilation utilisées dans le runner Linux historique :

```bash
GITHUB_ACTIONS=true ./drun.sh make skrew
GITHUB_ACTIONS=true ./drun.sh make linux
```

La variable `GITHUB_ACTIONS=true` demande à `drun.sh` d'utiliser l'argument de build Docker `USE_DEVKITPRO=0`, comme dans GitHub Actions. Sur un runner vierge, l'image du projet est absente et le wrapper la construit automatiquement. Sur une machine persistante, utiliser une image fraîche et noter sa provenance.

Le workflow historique exécutait ensuite `tools/scripts/package_artifacts_linux.sh` ; sa cible configurée était `build_linux/pokeplatinum/release_linux`. Ne considérer l'empaquetage comme faisant partie de la baseline qu'après confirmation des sorties exactes du build.

## 4. Journal de preuve local

Depuis la racine du clone, stocker la sortie complète dans un répertoire local **hors Git**. Ne pas ajouter automatiquement ce journal à un artefact CI ou au dépôt.

```bash
set -euo pipefail
LOG_DIR="$(mktemp -d /tmp/pokeplatinum-baseline.XXXXXX)"
{
  date -u
  git rev-parse HEAD
  git status --short
  docker version
  GITHUB_ACTIONS=true ./drun.sh make skrew
  GITHUB_ACTIONS=true ./drun.sh make linux
} 2>&1 | tee "$LOG_DIR/build-linux.log"
printf 'Journal local : %s\n' "$LOG_DIR/build-linux.log"
```

En cas d'échec, conserver le code de sortie et le premier message d'erreur utile. Si l'environnement est corrigé puis qu'une nouvelle tentative est lancée, enregistrer cette tentative séparément avec le changement effectué.

## 5. Critères de validation

La baseline n'est validée que si :

1. la SHA de référence est fixée et l'arbre de travail était propre avant le build ;
2. l'image Docker, les variables du chemin de compilation et les prérequis sont identifiés ;
3. `make skrew` et `make linux` terminent tous deux avec un code 0 ;
4. la sortie attendue est identifiée dans le dossier de build, avec sa taille et son SHA-256 consignés localement ;
5. les besoins de données et les dépendances locales éventuelles sont compris et documentés ;
6. une procédure de lancement et une première scène repère fonctionnent sur une machine disposant des données nécessaires.

Les points 3 à 6 ne sont pas confirmés par une exécution locale enregistrée dans le handoff.

## 6. Hygiène des données

- Ne committer aucun log complet de machine, ROM, sauvegarde utilisateur, asset privé, licence confidentielle ou artefact binaire.
- Ne téléverser aucun de ces éléments dans les artefacts CI.
- Un hash prouve l'identité d'un fichier, pas son autorisation de redistribution.
- Répéter le protocole après un changement volontaire de la révision de référence, du Dockerfile ou des scripts de génération.
