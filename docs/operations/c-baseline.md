# Baseline C/Linux — procédure et première preuve

> **État au 2026-10-22 :** le workflow dédié a effectué un build C/Linux réussi sur un runner GitHub Actions Ubuntu 24.04. L'exécution locale froide et le lancement visuel du runtime restent à effectuer ; la baseline de compilation est établie, la baseline fonctionnelle ne l'est pas encore.

## 1. Révision effectivement compilée

- Dépôt : `https://github.com/rakmahefa/pokeplatinum.git`
- Branche : `pc_port`
- Commit construit : `7a07925f620e327e2126d2af931785ed35a563a8`
- Run : [baseline-c-linux — 39724681527](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724681527)
- Résultat : `success`.
- Étapes réussies : installation des paquets hôte, checkout, détection de l'environnement Docker, `make skrew`, `make linux`, validation des quatre sorties, calcul des SHA-256 et téléversement du manifeste uniquement.
- Environnement rapporté : `Linux 7.0.0-1017-azure x86_64`.
- Artefact de vérification : [c-baseline-linux-7a07925f620e327e2126d2af931785ed35a563a8](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724681527), artefact ID `12403101714`, ZIP de 485 octets. Aucun exécutable n'a été téléversé.

L'arbre de code C n'a pas été modifié dans ce lot de préparation : le commit `7a07925` est la révision exacte capturée par le workflow et doit être utilisée lorsque l'on veut reproduire **ce run précis**. Les builds Linux/ARM historiques sur `ef958c9` sont des éléments de contexte, pas un substitut à ce run.

## 2. Sorties vérifiées par SHA-256

Les quatre fichiers étaient présents, non vides, sous `build_linux/pokeplatinum/`. Les noms, tailles et empreintes suivants proviennent du manifeste téléchargé depuis le run CI :

| Sortie | Taille (octets) | SHA-256 |
|---|---:|---|
| `firmware.bin` | 1 584 | `623d2357e4dce812edae3411e7877ed2c5408953bf7cde7ec38d10a9bd0bdfb6` |
| `header.bin` | 352 | `b42bcf480f162ca32ecdaa38006ae4bf4b57e6c095006113b83a0bf9274361b3` |
| `main` | 70 963 760 | `6b2b77704f86d544bb2054c77edc11d9b4068da6502b53eb760304177ef9ccf7` |
| `pokeplatinum.AppImage` | 39 004 664 | `18ad5e3a3245afde662ac20400136af3366a89913b402617047c1fb43aeefbcf` |

SHA-256 du fichier de manifeste décompressé lui-même : `20700e4f4812727e97199acbc02fe2948cd4283ec8ea276b3eda9f51431a6159`.

Ces empreintes sont une référence observée sur ce runner, pas une garantie de reproductibilité bit à bit sur une autre machine. Le premier run ne conservait pas encore les révisions exactes des dépendances Git téléchargées ; le workflow est maintenant renforcé pour les enregistrer lors des prochains builds.

## 3. Prérequis et reproduction locale

- Git et un clone propre du dépôt.
- Docker Engine/CLI installé, démarré et utilisable par l'utilisateur courant.
- Les permissions locales requises par `drun.sh` pour utiliser Docker, `/dev/fuse` et l'affichage X11 monté dans le conteneur.
- Les paquets hôte utilisés par le runner : `fuse`, `git`, `python3`, `wget`, `zip`.
- De l'espace disque pour l'image, les dépendances téléchargées et le build.
- Une connexion réseau pour les références Meson/subprojects utilisées par le build.

Utiliser un clone séparé pour garder la révision compilée immuable. Ne pas y placer de ROM, de sauvegarde personnelle ou de ressource extraite non redistribuable.

```bash
git clone --branch pc_port https://github.com/rakmahefa/pokeplatinum.git
cd pokeplatinum
git switch --detach 7a07925f620e327e2126d2af931785ed35a563a8
git status --short
git rev-parse HEAD
docker version
GITHUB_ACTIONS=true ./drun.sh make skrew
GITHUB_ACTIONS=true ./drun.sh make linux
```

Avant le build, `git status --short` doit être vide et `git rev-parse HEAD` doit afficher exactement la SHA indiquée. `GITHUB_ACTIONS=true` demande à `drun.sh` d'utiliser `USE_DEVKITPRO=0`, comme sur GitHub Actions. Le script réutilise l'image locale `pokeplatinum-build` si elle existe déjà ; pour une comparaison propre, noter cette image et éviter de remplacer des conteneurs/volumes utilisateur.

Les dépendances `subprojects/*.wrap` contiennent encore des références Git mutables telles que `main`. Le successful run ci-dessus prouve que cette résolution a compilé à cet instant, mais son manifeste initial ne capture pas les commits réellement résolus. La revue du [registre de provenance et licences](../assets/provenance-and-licenses.md) traite ce risque ; une reproduction bit à bit ne doit pas être annoncée avant d'avoir verrouillé et vérifié ces références.

## 4. Journal local

Conserver les logs complets dans un répertoire local hors Git. La commande suivante s'arrête au premier échec et conserve la sortie pour le diagnostic :

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

Une sortie de commande locale différente doit être analysée séparément, avec le code de sortie et l'environnement. Ne pas remplacer un échec par une réussite supposée.

## 5. État de validation

| Critère | État |
|---|---|
| Révision et run CI de compilation fixés | Validé pour le build du commit `7a07925` |
| `make skrew` et `make linux` réussis | Validé sur le runner GitHub du run 39724681527 |
| Quatre sorties présentes et checksums enregistrés | Validé ; manifeste limité aux métadonnées |
| Révisions exactes des dépendances capturées dans le premier run | Non ; workflow renforcé pour le prochain run |
| Reproduction locale froide indépendante | À exécuter |
| Lancement de l'application et capture d'une scène repère | À exécuter avec les données nécessaires |
| Baseline fonctionnelle/parité visuelle | Non établie |

La baseline de **compilation CI** est donc établie. La baseline globale C/PC reste ouverte jusqu'à ce que les dépendances soient verrouillées ou enregistrées, qu'une reproduction locale soit tentée et qu'un premier scénario runtime soit documenté.

## 6. Hygiène des données

- Ne committer aucun log complet de machine, ROM, sauvegarde utilisateur, asset privé ou artefact binaire.
- Ne téléverser aucun de ces éléments dans les artefacts CI.
- Le workflow ne conserve que les métadonnées (révision, environnement, révisions de dépendances quand disponibles, tailles et empreintes SHA-256), pas les exécutables du jeu.
- Un hash prouve l'identité d'un fichier, pas son autorisation de redistribution.
- Répéter le protocole après un changement volontaire de la révision de référence, du Dockerfile ou des scripts de génération.
