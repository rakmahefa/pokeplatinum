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

HEAD confirmé au début de cette reprise : `0a47767afaaef6a0238fc71f46e7332fdb8f66e9` — commit **“docs: specify Git Data API batching procedure”**, daté du 2026-10-22 à 04:31:29 UTC. Cette SHA est le point de départ de cette inspection, pas une garantie sur la tête de branche lors d'une session future.

Commits récents vérifiés sur `pc_port` :
- `ef958c943b2fd535750e8e4c80215942aebaf465` — **“Add batched commit and stale CI run policy”** : concurrence des workflows historiques et permissions minimales ;
- `5c0b6bac5b780427ae664456e9e7372579449237` — **“docs: add migration project entrypoint”** : point d'entrée README ;
- `0a47767afaaef6a0238fc71f46e7332fdb8f66e9` — documentation de la procédure de commits groupés via Git Data API.

Les runs GitHub Actions suivants avaient été déclenchés sur le commit `ef958c943b2fd535750e8e4c80215942aebaf465` :
- Linux : [run 39722714025](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714025) ;
- Windows : [run 39722714273](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714273) ;
- ARM : [run 39722714020](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714020).

Lors de la vérification du 2026-10-22 vers 04:34 UTC, les trois runs étaient toujours signalés `in_progress`, avec l'étape de compilation en cours ; aucune conclusion réussie ou échouée n'était encore disponible. Le HEAD `0a47767` ne diffère du commit testé que par des changements documentaires (ajout de `README.md` et mise à jour de la politique CI), ignorés par les workflows historiques via `paths-ignore`. Vérifier à nouveau le HEAD et les runs avant toute nouvelle décision.

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

**Statut : plan documenté seulement. Les workflows, scripts et crates décrits ne sont pas encore implémentés.**

Le plan P-1 est divisé en paquets de travail :

1. **P-1.1 — Baseline C/PC** : commit de référence, build reproductible, procédure de lancement, scènes et événements repères.
2. **P-1.2 — Inventaire** : code, ressources, formats, générateurs, dépendances, licences/provenance.
3. **P-1.3 — Parité fonctionnelle** : feature matrix, premier parcours vertical, fixtures et critères de comparaison.
4. **P-1.4 — ADR et spike Bevy** : frontières Bevy/domaine, deux surfaces logiques, coordonnées, tick/RNG, voie de rendu et choix final de version.
5. **P-1.5 — Toolchain/qualité** : workspace indépendant, version Rust stable fixée, `Cargo.lock`, fmt/clippy/tests.
6. **P-1.6 — CI Rust** : workflow PR rapide avec permissions minimales, build et tests sans ROM/asset privé.
7. **P-1.7 — `xtask`** : `doctor`, `inventory`, contrôles de génération, vérification de manifests ; sorties déterministes et mode dry-run.
8. **P-1.8 — Documentation/sécurité** : guides de développement, provenance des assets, licences, workflows et cache.
9. **P-1.9 — Profilage** : protocole reproductible et baseline initiale, sans seuil arbitraire au début.
10. **P-1.10 — Revue de sortie** : revue de checklist avant d'autoriser P0.

L'ordre détaillé, les critères et la checklist sont dans `docs/architecture/PREPARATION.md`.

## 7.1. Politique de commits et annulation des builds obsolètes

La politique est documentée dans [docs/operations/commit-and-ci-policy.md](docs/operations/commit-and-ci-policy.md). Pour une série de changements, créer plusieurs commits localement si cela clarifie l'historique, puis faire un seul push. Depuis l'API GitHub, préparer blobs/arbre/commits puis déplacer la référence une seule fois ; éviter les écritures fichier par fichier sur la branche surveillée. Les workflows Linux/Windows/ARM ont une concurrence par workflow et branche/PR, avec annulation des runs obsolètes. Vérifier le HEAD courant au début de chaque session.

## 7. Automatisation et documentation envisagées

### Workflows à ajouter séparément des workflows historiques

- `.github/workflows/rust-pr.yml` : fmt, lint, tests rapides, validation des fixtures, build Linux minimal ;
- `.github/workflows/rust-integration.yml` : tests headless et d'intégration, génération et assets avec fixtures approuvées ;
- `.github/workflows/rust-nightly.yml` : maintenance planifiée, licences/advisories, docs et tendance des benchmarks ;
- `.github/workflows/rust-profile.yml` : profilage lancé manuellement sur un runner connu ;
- politique de commits groupés et d'annulation CI : [commit-and-ci-policy.md](docs/operations/commit-and-ci-policy.md) ;
- workflow de release seulement plus tard, avec permissions de publication strictement isolées.

Caches proposés :
- cache Cargo versionné par OS/toolchain/`Cargo.lock`/features ;
- évaluer `sccache` seulement après mesure du temps de compilation ;
- futur cache d'assets fondé sur hash source + version parseur + schéma + options ;
- aucun cache ne doit être source de vérité ; reconstruire sans cache doit rester possible.

Documents de préparation proposés dans `docs/architecture/`, `docs/migration/`, `docs/assets/`, `docs/operations/` : ADR, feature matrix, source map, stratégie de parité, inventaire des formats, provenance/licences, setup, CI/cache, profiling et stratégie de tests.

## 8. État après politique CI

Les workflows historiques `.github/workflows/build_linux.yml`, `build_win.yml` et `build_arm.yml` possèdent une clé de concurrence par workflow et par branche/PR avec `cancel-in-progress: true`, ainsi que `permissions: contents: read`. Les builds historiques ignorent les changements uniquement Markdown. Cela évite les compilations jeu pour la documentation, mais aucun workflow de validation documentaire dédié n'existe encore.

La dernière observation des runs Linux/Windows/ARM est consignée en section 3. Tant qu'une conclusion finale n'est pas visible dans GitHub Actions, ne pas annoncer la baseline ou ces builds comme réussis. Aucun workflow Rust, workspace `engine/` ou outil `xtask` n'est déclaré opérationnel à ce stade.

## 9. Prochaines actions recommandées dans la nouvelle session

Commencer par examiner l'état actuel du dépôt et reprendre **P-1.1**, sans démarrer P0 prématurément :

1. Lire `SESSION_HANDOFF.md`, [la politique de commits/CI](docs/operations/commit-and-ci-policy.md), `audit.md`, `docs/architecture/PREPARATION.md` et les workflows/builds actuels.
2. Vérifier si la cible Linux C peut être compilée de façon reproductible dans l'environnement disponible ; enregistrer les prérequis et les éventuels blocages sans inventer de résultats.
3. Créer une procédure de baseline sous `docs/operations/`, avec commit source, commandes exactes, sortie attendue, logs et limitation liée aux données nécessitant une installation locale.
4. Construire un inventaire reproductible, en commençant par un script qui analyse l'arbre Git, les extensions, tailles, fichiers générés et dépendances Meson.
5. Proposer/committer les premiers ADR essentiels, puis choisir un premier parcours vertical à partir des ressources réellement disponibles.
6. Une fois cela établi, préparer le squelette `engine/` et le workflow Rust PR.
7. Mettre à jour cette note à la fin de chaque session avec le nouveau HEAD, les commits, les décisions, les tests effectivement exécutés et le prochain objectif.

Ne pas prétendre qu'un build, une capture, un benchmark ou un test est passé tant qu'il n'a pas été réellement exécuté.

## 10. Règle de mise à jour de ce handoff

À chaque session substantielle, actualiser cette note pour enregistrer :
- date et nouveau HEAD ;
- commits créés et chemins modifiés ;
- décisions arrêtées et points toujours ouverts ;
- commandes/tests vraiment exécutés avec leurs résultats ;
- risques nouveaux, obstacles et prochaines actions concrètes.

Garder ce fichier court et opérationnel par rapport à `audit.md` (plan global) et `PREPARATION.md` (détails de P-1). Ce document sert de point d'entrée à une nouvelle session, pas de duplication des spécifications complètes.
