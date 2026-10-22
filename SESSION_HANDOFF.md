# SESSION_HANDOFF — Pokémon Platinum → Rust + Bevy

> **But :** reprendre rapidement le travail dans une nouvelle session sans perdre les décisions, l'état du dépôt ni les prochaines actions.  
> **Dernière mise à jour :** 2026-10-22  
> **Dépôt :** https://github.com/rakmahefa/pokeplatinum  
> **Branche de travail :** `pc_port`  
> **Règle HEAD :** toujours lire le HEAD actuel sur GitHub avant de reprendre ; une SHA inscrite dans ce document n'est qu'un point de référence historique.

## Dernier lot — 2026-10-22 : remise en place des premiers workflows

- HEAD antérieur au lot : 4c39ff6c580ea4a8e8ba64de64fee03059dcc1e4 sur pc_port ; la branche de sauvegarde complète backup/pc-port-before-workflow-reset-2026-10-22 est toujours disponible.
- Deux workflows sont maintenant ajoutés dans .github/workflows/ par une seule mise à jour de référence : docs-inventory.yml et baseline-c-linux.yml.
- docs-inventory.yml cible les Markdown, docs/**, scripts d'outillage et sa propre définition ; il vérifie la syntaxe Python, compare deux rapports d'inventaire déterministes et conserve seulement un JSON de métadonnées.
- baseline-c-linux.yml cible les sources C, ressources et fichiers de build pertinents, propose un lancement manuel et conserve un manifeste/checksums sans téléverser les exécutables. Les modifications uniquement documentaires ne déclenchent pas le build C/Linux.
- Les anciennes définitions sont conservées dans les deux répertoires d'archive. Aucune CI Rust n'est encore ajoutée car engine/ et Cargo.lock n'existent pas.
- Les runs déclenchés par ce commit doivent être vérifiés sur la SHA réellement exécutée ; ne pas annoncer de réussite avant la conclusion GitHub Actions.
- README, PREPARATION.md, la politique commits/CI, la conception workflows/caches et le runbook C/Linux ont été actualisés dans le même lot.

## 1. Contexte et objectif

Le propriétaire du fork prépare une migration du port PC de Pokémon Platinum vers une architecture **Rust + Bevy**, avec un objectif de performances, de maintenabilité et de fidélité fonctionnelle. Le travail convenu est progressif : préparer et instrumenter le projet avant d'implémenter le nouveau moteur.

L'utilisateur a confirmé qu'il s'agit de son fork et a demandé de supprimer les directives/docs originaux avant d'effectuer son audit. Les documents généraux originaux et `AGENTS.md` ont été supprimés par commit ; le répertoire technique `docs/` a ensuite été restauré car il demeure utile au portage.

**Règle impérative de passation :** à chaque lot de changements publié sur `pc_port`, mettre à jour `SESSION_HANDOFF.md` dans ce même lot, avant l'unique mise à jour de référence. Une session qui reprend le dépôt doit lire ce fichier et le HEAD réel avant d'agir, puis actualiser le handoff avec le nouvel état, les changements du lot, les tests réellement exécutés, l'état des workflows et la prochaine action. Cette règle évite de répéter une opération déjà terminée ou de repartir d'un état périmé.

**Archivage des workflows : deux lots distincts, tous deux préservés.** Les anciens workflows Linux/Windows/ARM restent dans `docs/operations/workflow-archive/2026-10-22/`. Les workflows de préparation qui étaient actifs jusque-là ont maintenant leurs propres copies exactes dans `docs/operations/workflow-archive/current-active-2026-10-22/` et ont été retirés de `.github/workflows/`. La branche `backup/pc-port-before-workflow-reset-2026-10-22` conserve aussi l'état complet antérieur. Ne pas confondre ces archives avec une CI active.

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

Les anciens workflows de préparation étaient `.github/workflows/preparation-checks.yml` et `.github/workflows/baseline-c-linux.yml` ; leurs copies exactes se trouvent désormais dans `docs/operations/workflow-archive/current-active-2026-10-22/`. Aucun workflow n'est actuellement actif sur `pc_port`.

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

La chaîne Meson/C/Linux/Windows/ARM existante doit rester utilisable pendant P-1. À la suite de la remise à zéro du 2026-10-22, aucun workflow n'est actif dans `.github/workflows/`. Les définitions précédentes sont archivées ; les workflows de remplacement doivent être écrits à partir de la politique actuelle, après vérification de leurs déclencheurs, chemins, permissions, concurrence et artefacts.

## 6. Phase en cours : P-1 — Préparation

**Statut : P-1.1 compilation CI historique validée, mais le run des workflows réintroduits reste à vérifier ; reproductibilité bit à bit et parité runtime encore ouvertes ; P-1.2 inventaire amorcé ; P-1.3 matrice provisoire créée ; P-1.4 ADR-0001 formalisée. P0 non commencé.** Le run enrichi précédent a capturé les dépendances et leurs SHAs ; le nouveau build doit confirmer qu'elles se résolvent encore.

1. **P-1.1 — Baseline C/PC** : build GitHub réussi, quatre sorties et SHA-256 documentés dans [`docs/operations/c-baseline.md`](docs/operations/c-baseline.md). Exécution locale froide, capture d'une scène repère et validation runtime restent à faire.
2. **P-1.2 — Inventaire** : script [`tools/scripts/repo_inventory.py`](tools/scripts/repo_inventory.py) exécuté deux fois par CI avec des JSON identiques ; premier artefact résumé dans [`docs/assets/format-inventory.md`](docs/assets/format-inventory.md). Les refs Git mutables et les licences visibles sont consignées dans [`docs/assets/provenance-and-licenses.md`](docs/assets/provenance-and-licenses.md). Il reste à cartographier les producteurs/consommateurs et à verrouiller les dépendances.
3. **P-1.3 — Parité fonctionnelle** : feature matrix, parcours vertical et fixtures.
4. **P-1.4 — ADR et spike Bevy** : ADR-0001 acceptée pour la frontière Bevy/domaine ; workspace, écrans, tick/RNG, pipeline d'assets et version exacte de Bevy restent à décider/tester.
5. **P-1.5 — Toolchain/qualité** : workspace indépendant, version Rust stable fixée, `Cargo.lock`, fmt/clippy/tests.
6. **P-1.6 — CI de remplacement** : docs-inventory.yml et baseline-c-linux.yml sont ajoutés avec filtres séparés, permissions minimales, actions épinglées et concurrence. Leur réussite n'est confirmée qu'après vérification des nouveaux runs. La CI PR Rust reste à ajouter après création du workspace.
7. **P-1.7 — `xtask`** : `doctor`, `inventory`, contrôles de génération, vérification de manifests ; sorties déterministes et mode dry-run.
8. **P-1.8 — Documentation/sécurité** : guides de développement, provenance des assets, licences, workflows et cache.
9. **P-1.9 — Profilage** : protocole reproductible et baseline initiale, sans seuil arbitraire au début.
10. **P-1.10 — Revue de sortie** : revue de checklist avant d'autoriser P0.

L'ordre détaillé et les critères restent dans `docs/architecture/PREPARATION.md`.

## 7.1. Politique de commits et de ref

La procédure documentée dans [`docs/operations/commit-and-ci-policy.md`](docs/operations/commit-and-ci-policy.md) reste en vigueur : faire les commits logiques en chaîne, créer les blobs/arbres/commits, puis déplacer `pc_port` une seule fois avec un contrôle `expected_sha` et sans force-push. Aucun workflow n'est actif au checkpoint courant ; les archives ne sont pas exécutables depuis `docs/`. À chaque lot, mettre à jour ce handoff dans la même chaîne de commits puis publier en une seule mise à jour de référence.

## 7. Automatisation et documentation envisagées

### Workflows de remplacement prévus pendant P-1

- docs-inventory.yml : actif ; syntaxe Python, déterminisme de l'inventaire et JSON métadonnées ; nouveau run à vérifier ;
- baseline-c-linux.yml : actif ; build C/Linux ciblé aux chemins source/build et lancement manuel ; manifeste sans exécutables ; nouveau run à vérifier ;
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

## 8. État courant de la CI — premiers workflows de remplacement

docs-inventory.yml et baseline-c-linux.yml sont maintenant présents sous .github/workflows/. Le premier ne compile pas le jeu et vérifie la syntaxe Python et l'inventaire ; le second cible les modifications de sources et de build C et produit un manifeste de métadonnées/checksums uniquement.

Les archives Linux/Windows/ARM restent sous docs/operations/workflow-archive/2026-10-22/. Les deux anciennes définitions de préparation sont conservées sous docs/operations/workflow-archive/current-active-2026-10-22/. La branche backup/pc-port-before-workflow-reset-2026-10-22 préserve l'état complet antérieur à la remise à zéro.

Les résultats des nouveaux runs doivent être lus directement dans GitHub Actions et consignés dans le handoff si nécessaire. Les réussites d'anciens runs ne valident pas les nouveaux fichiers. La CI Rust PR, les tests d'intégration/headless, l'audit de dépendances planifié et le profiling manuel restent à créer après le workspace Rust.

## 9. Prochaines actions recommandées

1. Vérifier les runs GitHub Actions déclenchés par le commit qui a ajouté docs-inventory.yml et baseline-c-linux.yml, puis noter leurs conclusions et la SHA construite. Corriger toute erreur dans un lot groupé.
2. Enquêter sur la différence de hashes de `main`/AppImage entre les runs 39724681527 et 39725655227. Le Dockerfile utilise encore `FROM debian:13` et des versions de paquets non figées ; relever les versions et isoler la cause au lieu de supposer qu'une variable temporelle suffit.
3. Exécuter un build local froid, puis lancer l'application et documenter une scène repère.
4. Compléter P-1.2 avec la cartographie des producteurs/consommateurs, formats et provenance/licences ; épingler Tracy lors d'un build qui l'utilise réellement.
5. Poursuivre P-1.3/P-1.4 : choisir une carte pilote à partir des ressources disponibles, fixer le contrat de parité et rédiger les ADR restantes.
6. Créer le workspace/toolchain Rust seulement après un spike Bevy reproductible et des frontières de crates approuvées.

Ne pas déclarer la baseline globale validée tant que le runtime, la scène repère, le build local et les divergences de hashes ne sont pas traités.

## 10. Règle obligatoire de mise à jour du handoff

**Mettre à jour ce fichier à chaque lot de commits avant de publier ce lot sur `pc_port`.** Cela s'applique même si le lot ne modifie que la CI ou la documentation. Construire la chaîne de commits logiques voulue, inclure la mise à jour de `SESSION_HANDOFF.md`, puis déplacer la référence une seule fois avec `expected_sha` et sans force-push.

À chaque mise à jour, consigner :
- date, HEAD précédent et nouveau HEAD (le HEAD indiqué ici reste un repère historique après le commit) ;
- résumé du lot et chemins modifiés ;
- décisions arrêtées et points toujours ouverts ;
- contrôles/tests réellement exécutés et leurs résultats, sans inventer de succès ;
- workflows actifs au moment de la passation, statut connu des runs pertinents et éventuel changement de CI ;
- risques/obstacles et prochaine action concrète.

À chaque nouvelle session, lire d'abord le HEAD actuel de pc_port, puis ce fichier et les documents de référence utiles. Ne jamais déduire l'état actuel d'une ancienne SHA ou d'une ancienne note. Vérifier .github/workflows/ : docs-inventory.yml et baseline-c-linux.yml sont les workflows actifs au checkpoint courant ; la CI Rust reste à créer. Les archives restent conservées hors du répertoire de workflows.

Garder ce fichier opérationnel par rapport à `audit.md` (plan global) et `PREPARATION.md` (détails de P-1). Il sert de point d'entrée fiable pour une nouvelle session, pas de duplication des spécifications complètes.
