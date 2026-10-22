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

HEAD inspecté avant le présent lot : `445533d142aee68f87fdf0852b9f14ec00f7ca66`. Après chaque publication, relire le HEAD réel de `pc_port` sur GitHub ; cette SHA est un repère historique.

Commits vérifiés de ce chantier :
- `4e42a86afe9dcd4aff2c0cdba4a0f596a427a955` — archive exacte des trois workflows historiques ;
- `a0ab305b6fc52a0e5e2b95fd64abd31a4b388a0e` — retrait des fichiers actifs ;
- `e71df0f741f7bc18f0567f102ed46de86c020cd7` — runbook initial et outil d'inventaire ;
- `b58233c4d47f56b75d863200e557bf989948d3e6` — workflow de contrôle docs/inventaire ;
- `7a07925f620e327e2126d2af931785ed35a563a8` — workflow de build C/Linux ;
- `445533d142aee68f87fdf0852b9f14ec00f7ca66` — conservation de l'artefact d'inventaire.

Résultats vérifiés :
- [Workflow preparation-checks run 39724440638](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724440638) : `success`. Syntaxe du script validée ; deux JSON identiques ; résumé de l'arbre : 27 711 blobs et 138 519 605 octets au commit `b58233c`.
- [Workflow preparation-checks run 39724791913](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724791913) : `success`. Artefact `repository-inventory-445533d142aee68f87fdf0852b9f14ec00f7ca66`, rapport JSON de métadonnées retenu 14 jours. Son snapshot comprend 27 712 blobs et 138 524 927 octets au commit `445533d`.
- Le snapshot est résumé dans [`docs/assets/format-inventory.md`](docs/assets/format-inventory.md) : volumes par répertoire, extensions dominantes et plus gros blobs, avec les formats non confirmés marqués comme hypothèses.
- Le nouveau build [baseline-c-linux run 39724681527](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724681527) a été lancé sur le commit `7a07925`. Au dernier contrôle, `make skrew` était terminé et `make linux` était en cours ; aucun résultat final ni manifeste de checksum n'est encore confirmé.

Les workflows historiques Linux/ARM (`39722714025`, `39722714020`) ont réussi au commit `ef958c9`. Le workflow Windows historique (`39722714273`) était encore indiqué `in_progress` au dernier relevé et demeure non confirmé. Les copies des trois fichiers sont sous `docs/operations/workflow-archive/2026-10-22/`.

## 4. Documents à lire en premier

1. **[audit.md](audit.md)** — analyse du projet existant, architecture cible, matrice des systèmes, migration progressive, phases P0–P3, risques et tests.
2. **[docs/architecture/PREPARATION.md](docs/architecture/PREPARATION.md)** — plan P-1 détaillé, automatisation, workflows, caches, documentation à créer et checklist de sortie avant P0.
3. Documentation historique restaurée qui sera utile au portage :
   - [2D rendering](docs/2d_rendering.md)
   - [3D rendering](docs/3d_rendering.md)
   - [Map loading](docs/maps/loading_maps.md)
   - [Map file formats](docs/maps/file_format_specifications.md)
   - [Dynamic map features](docs/maps/dynamic_map_features.md)
   - [Documentation index](docs/index.md)

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

**Statut : P-1.1 amorcé ; P0 non commencé.** Ce lot sauvegarde et retire les workflows hérités, ajoute un runbook C/Linux initial et un premier outil d'inventaire. Ces livrables sont écrits mais pas encore tous exécutés/validés.

1. **P-1.1 — Baseline C/PC** : procédure initiale dans [`docs/operations/c-baseline.md`](docs/operations/c-baseline.md). Build local froid, sorties exactes, checksum et première scène repère restent à vérifier.
2. **P-1.2 — Inventaire** : script [`tools/scripts/repo_inventory.py`](tools/scripts/repo_inventory.py) exécuté deux fois par CI avec des sorties JSON identiques ; premier artefact obtenu et résumé dans [`docs/assets/format-inventory.md`](docs/assets/format-inventory.md). La classification sémantique, les producteurs/consommateurs, les formats et la provenance/licences restent à vérifier.
3. **P-1.3 — Parité fonctionnelle** : feature matrix, parcours vertical et fixtures.
4. **P-1.4 — ADR et spike Bevy** : frontières Bevy/domaine, deux surfaces logiques, coordonnées, tick/RNG, voie de rendu et choix final de version.
5. **P-1.5 — Toolchain/qualité** : workspace indépendant, version Rust stable fixée, `Cargo.lock`, fmt/clippy/tests.
6. **P-1.6 — CI de remplacement** : le workflow docs/inventaire est vert ; le workflow dédié au build C/Linux est ajouté dans ce lot ; la CI Rust (formatage, tests, build minimal) reste à concevoir.
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

1. Examiner le résultat du nouveau workflow `baseline-c-linux.yml` et son manifeste SHA-256 ; comparer avec le protocole froid de `docs/operations/c-baseline.md` et noter les dépendances locales restantes sans ajouter de binaire ou d'asset privé à Git.
2. Exécuter `python3 tools/scripts/repo_inventory.py --revision HEAD --output /tmp/pokeplatinum-inventory.json`, contrôler le JSON, puis archiver uniquement un rapport expurgé/non sensible si utile.
3. Compléter P-1.2 : cibles Meson/Make, dépendances/subprojects, générateurs, formats de ressources et provenance/licences.
4. Concevoir les nouveaux workflows avant de les activer : validation docs, contrôles CI Rust légers, jobs d'intégration séparés ; permissions minimales, paths pertinents, caches non essentiels et annulation obsolète.
5. Poursuivre P-1.3/P-1.4 : feature matrix, parcours vertical fondé sur les données réellement disponibles et ADR.
6. Mettre à jour ce handoff avec les résultats mesurés et le nouvel HEAD.

Ne pas déclarer la baseline validée, un script testé ou un workflow vert tant que ces résultats n'ont pas été obtenus et vérifiés.

## 10. Règle de mise à jour de ce handoff

À chaque session substantielle, actualiser cette note pour enregistrer :
- date et nouveau HEAD ;
- commits créés et chemins modifiés ;
- décisions arrêtées et points toujours ouverts ;
- commandes/tests vraiment exécutés avec leurs résultats ;
- risques nouveaux, obstacles et prochaines actions concrètes.

Garder ce fichier court et opérationnel par rapport à `audit.md` (plan global) et `PREPARATION.md` (détails de P-1). Ce document sert de point d'entrée à une nouvelle session, pas de duplication des spécifications complètes.
