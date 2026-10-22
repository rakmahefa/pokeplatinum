# Baseline C/Linux — procédure et première preuve

> **État au 2026-10-22 :** un ancien workflow C/Linux a réussi sur Ubuntu 24.04 à la révision indiquée ci-dessous. Une nouvelle définition baseline-c-linux.yml vient d'être ajoutée avec des filtres ciblés ; son premier run a mis en évidence un défaut de quoting dans la garde SHA de Meson au Makefile ; le correctif effectif du Makefile est publié dans ce commit et doit être confirmé par le build déclenché sur cette nouvelle révision. L'exécution locale froide et le lancement visuel du runtime restent à effectuer ; la baseline fonctionnelle n'est pas encore établie.

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

Ces empreintes sont des observations CI, pas une garantie de reproductibilité bit à bit. Le deuxième build a capturé les dépendances, mais les SHA de `main`/AppImage diffèrent du premier run ; la cause reste ouverte.


## 3. Deuxième build, dépendances capturées et divergence

- Run [39725655227](https://github.com/rakmahefa/pokeplatinum/actions/runs/39725655227), conclusion `success`, commit source `15da327073d76246fd36e0fd24ac588dff014716`.
- Artefact ID `12403386690`, ZIP de 1 590 octets, [manifeste enrichi](sandbox:/mnt/data/c-baseline-linux-enriched-manifest.zip). Il contient des métadonnées et SHA-256 uniquement, jamais les exécutables.
- Environnement : `Linux 6.17.0-1022-azure x86_64`, Docker Engine `28.0.4`, image custom ID `sha256:885286ae5f84383c2cede5e3345e6a1d47b409796a9a51961464802a22f0bbce`.
- Meson `1.12.0` : commit observé `ab4508e6abe338a3bd2e6eb5da1d18b8cf55dc93`.
- `subprojects/.wraplock` était présent mais vide.

SHAs Git des sous-projets détectés par ce run :

| Checkout | Commit |
|---|---|
| `libntr` | `1555d911ac80c0190ac1c321f99f1323de8b3c09` |
| `libntrdwc` | `16246ba7b4269e6686f3e4da068e3c996a103739` |
| `libntrsystem` | `cd778c9d5e45869f8ecb8245b316ac20ea576958` |
| `libntrwifi` | `067dabb137dfaf80b8ceeb3b3c4a7256bfabc3e0` |
| `libvct` | `a34ad47fc0d7d964483c287759b704b3b1f3b967` |
| `metang` | `d616519ce37bc9ceef556969a1ca2dc64bf88390` |
| `meson-1.12.0` | `ab4508e6abe338a3bd2e6eb5da1d18b8cf55dc93` |

Sorties du deuxième run :

| Sortie | Taille (octets) | SHA-256 |
|---|---:|---|
| `firmware.bin` | 1 584 | `623d2357e4dce812edae3411e7877ed2c5408953bf7cde7ec38d10a9bd0bdfb6` |
| `header.bin` | 352 | `b42bcf480f162ca32ecdaa38006ae4bf4b57e6c095006113b83a0bf9274361b3` |
| `main` | 70 963 760 | `4ff7240efd8fde741c4984f48ca77760e80ca08f0aa3f7e254c2c2c1c2f2e739` |
| `pokeplatinum.AppImage` | 39 004 664 | `dd05742932447ae9514ad927004f12d9ac90406fd7923242632df44af2092939` |

### Divergence à résoudre

Les deux builds gardent les mêmes tailles et SHA pour `firmware.bin` et `header.bin`, mais les hashes de `main` et de l'AppImage diffèrent. Le diff Git entre les révisions `7a07925` et `15da327` ne comprend que des changements de CI et de documentation, pas les sources C ou les fichiers de build. La cause exacte est inconnue. Des variables à contrôler — et non des causes déjà prouvées — incluent le tag Docker mutable `debian:13`, les versions de paquets non figées, des données générées ou des métadonnées de liaison/paquetage.

Les SHAs observées pour six dépendances Git sont épinglées dans les wrappers et `subprojects/update.ini`. Le Makefile vérifie également que le tag Meson `1.12.0` correspond au commit ci-dessus. Le run suivant doit confirmer ces épingles. `tracy.wrap` reste non épinglé : son checkout n'a pas été détecté par le build Linux.

## 4. Prérequis et reproduction locale

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

Les dépendances Git détectées par la baseline Linux sont maintenant épinglées. Le prochain run doit confirmer leur récupération et la compilation avant de considérer ces épingles comme validées.

## 5. Journal local

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

## 6. État de validation

| Critère | État |
|---|---|
| Révision et run CI de compilation fixés | Validé pour le build du commit `7a07925` |
| `make skrew` et `make linux` réussis | Validé sur le runner GitHub du run 39724681527 |
| Quatre sorties présentes et checksums enregistrés | Validé ; manifeste limité aux métadonnées |
| Révisions exactes des dépendances capturées | Oui au run 39725655227 ; épingles appliquées, build de confirmation en attente |
| Reproduction locale froide indépendante | À exécuter |
| Lancement de l'application et capture d'une scène repère | À exécuter avec les données nécessaires |
| Baseline fonctionnelle/parité visuelle | Non établie |

La baseline de **compilation CI** est donc établie. La baseline globale C/PC reste ouverte jusqu'à ce que les dépendances soient verrouillées ou enregistrées, qu'une reproduction locale soit tentée et qu'un premier scénario runtime soit documenté.

## 7. Hygiène des données

- Ne committer aucun log complet de machine, ROM, sauvegarde utilisateur, asset privé ou artefact binaire.
- Ne téléverser aucun de ces éléments dans les artefacts CI.
- Le workflow ne conserve que les métadonnées (révision, environnement, révisions de dépendances quand disponibles, tailles et empreintes SHA-256), pas les exécutables du jeu.
- Un hash prouve l'identité d'un fichier, pas son autorisation de redistribution.
- Répéter le protocole après un changement volontaire de la révision de référence, du Dockerfile ou des scripts de génération.
