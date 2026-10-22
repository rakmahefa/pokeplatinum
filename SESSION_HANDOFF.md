# SESSION_HANDOFF — Pokémon Platinum → Rust + Bevy

> **But :** reprendre rapidement le travail dans une nouvelle session sans perdre les décisions, l'état du dépôt ni les prochaines actions.  
> **Dernière mise à jour :** 2026-10-22  
> **Dépôt :** https://github.com/rakmahefa/pokeplatinum  
> **Branche de travail :** `pc_port`  
> **Règle HEAD :** toujours lire le HEAD actuel sur GitHub avant de reprendre ; une SHA inscrite dans ce document n'est qu'un point de référence historique.

## 1. Contexte et objectif

Le propriétaire du fork prépare une migration du port PC de Pokémon Platinum vers une architecture **Rust + Bevy**, avec un objectif de performances, de maintenabilité et de fidélité fonctionnelle. Le travail convenu est progressif : préparer et instrumenter le projet avant d'implémenter le nouveau moteur.

L'utilisateur a confirmé qu'il s'agit de son fork et a demandé de supprimer les directives/docs originaux avant d'effectuer son audit. Les documents généraux originaux et `AGENTS.md` ont été supprimés par commit ; le répertoire technique `docs/` a ensuite été restauré car il demeure utile au portage.

## 2. Décisions de conception prises

- **Direction retenue : Rust + Bevy.** Ne pas construire dès le départ un moteur totalement indépendant de Bevy.
- **Séparation des responsabilités :**
  - logique métier/simulation en Rust pur, indépendante de Bevy : combat, scripts, état du monde, mouvement, collision, progression, RNG et sauvegardes ;
  - Bevy pour l'infrastructure du runtime : ECS là où il est utile, schedules, fenêtres, entrée, cycle de vie et gestion d'assets ;
  - modules personnalisés pour la compatibilité DS/Nitro : parseurs, pipeline d'assets, rendu 2D à tuiles/couches, import 3D et composition des deux écrans.
- **Éviter une conversion naïve C→Rust.** Le code existant et les données/scripts forment un système cohérent.
- **Conserver le runtime C comme oracle de comparaison** pendant la migration, tant qu'il compile et peut être exécuté.
- **Ne pas commencer P0 immédiatement.** Une phase importante **P-1 — Préparation** doit être réalisée et validée avant P0.
- **Version Bevy candidate mentionnée dans les docs : 0.20.0**, mais elle doit être validée par un spike reproductible avant de la figer dans le workspace. Vérifier la version et les compatibilités au moment de commencer l'implémentation.
- **Ressources/provenance :** ne pas versionner ni distribuer de ROM commerciale, de sauvegardes personnelles ou d'assets dont la redistribution n'est pas autorisée. CI générique sur fixtures synthétiques/légalement redistribuables.

## 3. État Git connu

HEAD avant le lot d'épinglage : `ddbd00e277f858469ca012e288cdff9e0b8384be`. Toujours relire le HEAD courant de `pc_port` avant toute écriture.

Résultats CI confirmés :
- [Preparation checks 39726156234](https://github.com/rakmahefa/pokeplatinum/actions/runs/39726156234) : `success`, contrôle de l'inventaire/déterminisme.
- [Preparation checks 39726461321](https://github.com/rakmahefa/pokeplatinum/actions/runs/39726461321) : `success`, handoff/ADR.
- [Baseline C/Linux 39724681527](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724681527) : `success`, build de référence au commit `7a07925`.
- [Baseline enrichie 39725655227](https://github.com/rakmahefa/pokeplatinum/actions/runs/39725655227) : `success` au commit `15da327`. Le manifeste capture Docker Engine 28.0.4, l'image custom et les SHAs de sous-projets Git détectées.
- Les deux builds ont les mêmes tailles et SHA pour `firmware.bin`/`header.bin`, mais des SHA différentes pour `main`/AppImage, malgré un diff Git entre HEAD composé uniquement de docs/workflows. Cause inconnue ; reproductibilité bit à bit non validée.
- Les SHAs de libntr, libntrdwc, libntrsystem, libntrwifi, libvct et metang observées dans le manifeste sont épinglées dans les wrappers et `update.ini`. Le Makefile vérifie le commit exact de Meson 1.12.0 ; le build suivant doit valider ces épingles.
- Les anciens workflows C Linux/ARM/Windows ont terminé avec `success` sur le commit historique `ef958c9`. Les originaux sont archivés à l'identique dans `docs/operations/workflow-archive/2026-10-22/`.

Workflows actifs : `.github/workflows/preparation-checks.yml` et `.github/workflows/baseline-c-linux.yml`. Les actions checkout/upload-artifact y sont épinglées par SHA complète dans le présent lot.

## 4. Documents à lire en premier

1. **[`audit.md`](audit.md)** — analyse source, architecture cible et phases P0–P3.
2. **[`docs/architecture/PREPARATION.md`](docs/architecture/PREPARATION.md)** — état et critères de sortie de P-1.
3. **[`docs/operations/c-baseline.md`](docs/operations/c-baseline.md)** — build C/Linux vérifié et critères runtime encore ouverts.
4. **[`docs/assets/format-inventory.md`](docs/assets/format-inventory.md) et [`docs/assets/provenance-and-licenses.md`](docs/assets/provenance-and-licenses.md)** — volumes, formats présumés, wrappers et licences visibles.
5. **[`docs/migration/feature-matrix.md`](docs/migration/feature-matrix.md)** — matrice fonctionnelle provisoire et premier parcours proposé.
6. **[`docs/architecture/decisions/README.md`](docs/architecture/decisions/README.md)** — ADR acceptée et décisions encore ouvertes.
7. **[`docs/operations/commit-and-ci-policy.md`](docs/operations/commit-and-ci-policy.md)** — batching des commits et stratégie CI.
8. Références techniques C : [rendu 2D](docs/2d_rendering.md), [rendu 3D](docs/3d_rendering.md), [chargement des cartes](docs/maps/loading_maps.md).

## 5. Ce que l'audit a observé

L'inventaire récursif de l'arbre Git à la révision auditée comptait approximativement :
- `src/` : 1 033 fichiers, environ 24,3 MB ;
- `include/` : 1 986 fichiers, environ 3,1 MB ;
- `res/` : 24 163 fichiers, environ 107,4 MB ;
- `generated/` : 108 fichiers ;
- `tools/` : 235 fichiers ;
- `docs/` : 20 fichiers restaurés.

Les valeurs correspondent aux blobs Git de la révision examinée, pas à la consommation mémoire ni au paquet distribué.

Systèmes source à traiter attentivement :
- `src/main.c`, `src/system.c` : boucle principale, tâches et temporisation spécifique DS/PC ;
- `src/overlay_manager.c`, `src/field_system.c` : transitions d'applications et runtime de terrain ;
- `src/overlay005/fieldmap.c`, `land_data.c`, `loaded_map_buffers.c` : chargement de cartes, modèles et données BDHC ;
- `src/map_object.c`, `src/map_object_move.c` : objets et mouvement sur grille ;
- `src/battle/battle_system.c`, `battle_main.c` et scripts : simulation de combat ;
- `src/easy3d.c`, `src/easy3d_object.c` : wrappers de rendu Nitro 3D ;
- `src/narc.c` : correspondance entre IDs NARC et chemins ;
- `src/savedata.c`, `src/savedata/save_table.c` : sauvegardes ;
- `src/sound_system.c` : audio basé sur SDAT/Nitro ;
- `meson.build`, `meson.options`, Makefile et `.github/workflows/` : chaîne de build existante.

La chaîne Meson/Linux/Windows/ARM doit continuer à fonctionner pendant P-1. Ne pas remplacer ou supprimer les workflows historiques au moment de créer les workflows Rust.

## 6. Phase en cours : P-1 — Préparation

**Statut : P-1.1 compilation CI validée, reproductibilité bit à bit et parité runtime encore ouvertes ; P-1.2 inventaire amorcé ; P-1.3 matrice provisoire créée ; P-1.4 ADR-0001 formalisée. P0 non commencé.** Le run enrichi a capturé les dépendances ; leurs SHAs sont épinglées dans ce lot et restent à valider par un nouveau build.

1. **P-1.1 — Baseline C/PC** : build GitHub réussi, quatre sorties et SHA-256 documentés dans [`docs/operations/c-baseline.md`](docs/operations/c-baseline.md). Exécution locale froide, capture d'une scène repère et validation runtime restent à faire.
2. **P-1.2 — Inventaire** : script [`tools/scripts/repo_inventory.py`](tools/scripts/repo_inventory.py) exécuté deux fois par CI avec des JSON identiques ; premier artefact résumé dans [`docs/assets/format-inventory.md`](docs/assets/format-inventory.md). Les refs Git mutables et les licences visibles sont consignées dans [`docs/assets/provenance-and-licenses.md`](docs/assets/provenance-and-licenses.md). Il reste à cartographier les producteurs/consommateurs et à verrouiller les dépendances.
3. **P-1.3 — Parité fonctionnelle** : feature matrix, parcours vertical et fixtures.
4. **P-1.4 — ADR et spike Bevy** : ADR-0001 acceptée pour la frontière Bevy/domaine ; workspace, écrans, tick/RNG, pipeline d'assets et version exacte de Bevy restent à décider/tester.
5. **P-1.5 — Toolchain/qualité** : workspace indépendant, version Rust stable fixée, `Cargo.lock`, fmt/clippy/tests.
6. **P-1.6 — CI de remplacement** : les workflows docs/inventaire et C/Linux sont actifs ; tous deux ont déjà réussi au moins un run. La CI Rust (formatage, tests, build minimal) reste à concevoir.
7. **P-1.7 — `xtask`** : `doctor`, `inventory`, contrôles de génération, vérification de manifests ; sorties déterministes et mode dry-run.
8. **P-1.8 — Documentation/sécurité** : guides de développement, provenance des assets, licences, workflows et cache.
9. **P-1.9 — Profilage** : protocole reproductible et baseline initiale, sans seuil arbitraire au début.
10. **P-1.10 — Revue de sortie** : revue de checklist avant d'autoriser P0.

L'ordre détaillé et les critères restent dans `docs/architecture/PREPARATION.md`.

## 7.1. Politique de commits et de ref

La procédure documentée dans [`docs/operations/commit-and-ci-policy.md`](docs/operations/commit-and-ci-policy.md) reste en vigueur : faire les commits logiques en chaîne, créer les blobs/arbres/commits, puis déplacer `pc_port` une seule fois avec un contrôle `expected_sha` et sans force-push. Les vieux groupes de concurrence sont conservés uniquement dans l'archive ; `preparation-checks.yml` et `baseline-c-linux.yml` sont les workflows de remplacement, avec des périmètres distincts.

## 7. Automatisation et documentation envisagées

### Workflows actifs et prévus pendant P-1

- `.github/workflows/preparation-checks.yml` : actif ; syntaxe Python et déterminisme de l'inventaire, sans compilation du jeu ;
- `.github/workflows/baseline-c-linux.yml` : build C/Linux de référence ; manifeste SHA-256 uniquement, sans publication d'exécutables ;
- `.github/workflows/rust-pr.yml` : fmt, lint, tests rapides, validation des fixtures, build Linux minimal ;
- `.github/workflows/rust-integration.yml` : tests headless et d'intégration, génération et assets avec fixtures approuvées ;
- `.github/workflows/rust-nightly.yml` : maintenance planifiée, licences/advisories, docs et tendance des benchmarks ;
- `.github/workflows/rust-profile.yml` : profilage lancé manuellement sur un runner connu ;
- vérification documentaire déclenchée sur les modifications Markdown ;
- workflow de release seulement plus tard, avec permissions de publication strictement isolées.

Caches proposés :
- cache Cargo versionné par OS/toolchain/`Cargo.lock`/features ;
- évaluer `sccache` seulement après mesure du temps de compilation ;
- futur cache d'assets fondé sur hash source + version parseur + schéma + options ;
- aucun cache ne doit être source de vérité ; reconstruire sans cache doit rester possible.

Documents de préparation proposés dans `docs/architecture/`, `docs/migration/`, `docs/assets/`, `docs/operations/` : ADR, feature matrix, source map, stratégie de parité, inventaire des formats, provenance/licences, setup, CI/cache, profiling et stratégie de tests.

## 8. État de la CI après archivage

Les copies des workflows historiques sont sous `docs/operations/workflow-archive/2026-10-22/`, avec un manifeste et les SHA des blobs originaux. Les trois fichiers ont été retirés de `.github/workflows/`.

Les workflows actifs ont été recréés séparément : `.github/workflows/preparation-checks.yml` contrôle les docs/l'inventaire ; `.github/workflows/baseline-c-linux.yml` construit la référence C/Linux et ne conserve qu'un manifeste de checksums, pas les exécutables. La CI Rust rapide, les tests d'intégration et le profilage restent à établir. Les runs lancés avant la suppression des anciens fichiers peuvent encore terminer ; ils ne signifient pas que ces anciens workflows sont toujours actifs.

## 9. Prochaines actions recommandées

1. Vérifier le run C/Linux suivant l'épinglage des SHAs ; confirmer les révisions attendues et réparer toute erreur de résolution.
2. Enquêter sur la différence de hashes de `main`/AppImage entre les runs 39724681527 et 39725655227. Le Dockerfile utilise encore `FROM debian:13` et des versions de paquets non figées ; relever les versions et isoler la cause au lieu de supposer qu'une variable temporelle suffit.
3. Exécuter un build local froid, puis lancer l'application et documenter une scène repère.
4. Compléter P-1.2 avec la cartographie des producteurs/consommateurs, formats et provenance/licences ; épingler Tracy lors d'un build qui l'utilise réellement.
5. Poursuivre P-1.3/P-1.4 : choisir une carte pilote à partir des ressources disponibles, fixer le contrat de parité et rédiger les ADR restantes.
6. Créer le workspace/toolchain Rust seulement après un spike Bevy reproductible et des frontières de crates approuvées.

Ne pas déclarer la baseline globale validée tant que le runtime, la scène repère, le build local et les divergences de hashes ne sont pas traités.

## 10. Règle de mise à jour de ce handoff

À chaque session substantielle, actualiser cette note pour enregistrer :
- date et nouveau HEAD ;
- commits créés et chemins modifiés ;
- décisions arrêtées et points toujours ouverts ;
- commandes/tests vraiment exécutés avec leurs résultats ;
- risques nouveaux, obstacles et prochaines actions concrètes.

Garder ce fichier court et opérationnel par rapport à `audit.md` (plan global) et `PREPARATION.md` (détails de P-1). Ce document sert de point d'entrée à une nouvelle session, pas de duplication des spécifications complètes.
