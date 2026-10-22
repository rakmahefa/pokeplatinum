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

HEAD vérifié avant ce lot : `0ab58358753f32e2c247a6bdde98fdce0f9e2103`. Toujours relire le HEAD réel de `pc_port` avant d'agir ; cette SHA est un repère historique.

Commits vérifiés de ce chantier :
- `4e42a86afe9dcd4aff2c0cdba4a0f596a427a955` — archive exacte des trois workflows historiques ;
- `a0ab305b6fc52a0e5e2b95fd64abd31a4b388a0e` — retrait des trois entrées actives ;
- `e71df0f741f7bc18f0567f102ed46de86c020cd7` — runbook initial et script d'inventaire ;
- `b58233c4d47f56b75d863200e557bf989948d3e6` — workflow de contrôle docs/inventaire ;
- `7a07925f620e327e2126d2af931785ed35a563a8` — workflow C/Linux ;
- `445533d142aee68f87fdf0852b9f14ec00f7ca66` — artefact d'inventaire initial ;
- `fef27a2cb5c31356ddddcf14693784febea56b08` et `f5e12b8325f0941a7fa901aa88e28a5090cd8fb1` — premier snapshot des formats/volumes ;
- `15da327073d76246fd36e0fd24ac588dff014716` — runbook de baseline, registre de provenance/licences et instrumentation des dépendances du prochain run ;
- `0ab58358753f32e2c247a6bdde98fdce0f9e2103` — matrice fonctionnelle provisoire.

Résultats CI confirmés :
- [Preparation checks 39724440638](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724440638) : `success`, syntaxe Python et déterminisme de l'inventaire validés.
- [Preparation checks 39724791913](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724791913) : `success`, artefact JSON ; snapshot au commit `445533d` : 27 712 blobs / 138 524 927 octets.
- [Preparation checks 39725079397](https://github.com/rakmahefa/pokeplatinum/actions/runs/39725079397) : `success`.
- [Preparation checks 39725655240](https://github.com/rakmahefa/pokeplatinum/actions/runs/39725655240) : `success`.
- [Preparation checks 39726156234](https://github.com/rakmahefa/pokeplatinum/actions/runs/39726156234) : `success`.
- [Baseline C/Linux 39724681527](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724681527) : `success` sur `7a07925`. Les étapes `make skrew`, `make linux`, les quatre sorties attendues et le manifeste SHA-256 sont validés. La taille du ZIP manifeste est 485 octets ; aucun exécutable n'a été téléversé.
- [Baseline C/Linux enrichi 39725655227](https://github.com/rakmahefa/pokeplatinum/actions/runs/39725655227) : `in_progress` au dernier contrôle sur `15da327`. `make skrew` est terminé ; `make linux` est encore indiqué en cours. Pas de résultat final ni de manifeste enrichi confirmé à ce stade.
- L'ancien Windows [run 39722714273](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714273) a terminé avec `success`. Les anciens Linux/ARM (`39722714025`, `39722714020`) avaient aussi réussi au commit `ef958c9`.

État des actifs CI : seuls `.github/workflows/preparation-checks.yml` et `.github/workflows/baseline-c-linux.yml` sont actifs. Les trois anciens workflows restent copiés à l'identique dans `docs/operations/workflow-archive/2026-10-22/`.

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

**Statut : P-1.1 compilation CI validée, parité runtime encore ouverte ; P-1.2 inventaire amorcé ; P-1.3 matrice provisoire créée ; P-1.4 ADR-0001 formalisée. P0 non commencé.** Le premier build C/Linux passe sur `7a07925`; un second run capture les dépendances, mais demeure en cours au dernier contrôle.

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

1. Relancer `baseline-c-linux.yml` enrichi and review the recorded Docker image, wrap hashes and resolved dependency SHAs; pin mutable refs only after review and a successful rebuild.
2. Exécuter le protocole local de build à froid and document the launch/configuration requirements for a scene-reference capture.
3. Terminer P-1.2 en cartographiant les producteurs/consommateurs des ressources, les fichiers générés, les usages des dépendances et les licences/provenance.
4. Poursuivre P-1.3/P-1.4 : matrice de fonctionnalités, parcours vertical fondé sur les ressources réellement disponibles et ADR.
5. Créer le workspace/toolchain Rust et un `rust-pr.yml` minimal uniquement après approbation du spike Bevy et des frontières de workspace.
6. Mettre à jour ce handoff avec les résultats mesurés et le nouveau HEAD.

Ne pas déclarer la baseline validée, un script testé ou un workflow vert tant que ces résultats n'ont pas été obtenus et vérifiés.

## 10. Règle de mise à jour de ce handoff

À chaque session substantielle, actualiser cette note pour enregistrer :
- date et nouveau HEAD ;
- commits créés et chemins modifiés ;
- décisions arrêtées et points toujours ouverts ;
- commandes/tests vraiment exécutés avec leurs résultats ;
- risques nouveaux, obstacles et prochaines actions concrètes.

Garder ce fichier court et opérationnel par rapport à `audit.md` (plan global) et `PREPARATION.md` (détails de P-1). Ce document sert de point d'entrée à une nouvelle session, pas de duplication des spécifications complètes.
