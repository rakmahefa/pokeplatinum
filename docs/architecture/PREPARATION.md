# Phase Préparation — sécuriser le chantier Rust + Bevy

> Statut : proposition de plan, préalable obligatoire à P0  
> Dépôt : rakmahefa/pokeplatinum — branche de travail : pc_port  
> Date de rédaction : 2026-10-22  
> Référence de stratégie : audit.md

## 1. Pourquoi ajouter une phase avant P0 ?

P0 supposait que le périmètre, l'environnement de développement, les formats, les références de comparaison et les automatismes étaient suffisamment compris. Ce serait prématuré. Une migration de cette taille risque de perdre beaucoup de temps si le projet commence par écrire du gameplay avant d'avoir une baseline reproductible, une cartographie des données, une politique de compatibilité, des outils de diagnostic et des workflows fiables.

La phase Préparation, notée **P-1**, n'implémente pas encore le moteur de jeu. Elle crée le filet de sécurité qui rend P0 rapide, observable, reproductible et réversible.

### Résultat recherché

Avant de commencer P0, nous devons pouvoir répondre, preuves à l'appui, aux questions suivantes :

- Quelle révision C est notre référence, comment la compiler et comment vérifier que la référence n'a pas changé ?
- Quelles fonctionnalités sont prioritaires, comment mesurer la parité, et quelles divergences PC sont acceptées ?
- Quels formats de ressources existent, lesquels sont nécessaires à une première carte, et comment les valider ?
- Quelle version de Rust/Bevy, quelles features et quelles cibles sont réellement nécessaires ?
- Comment diagnostiquer une machine de développement en une commande ?
- Comment les tests, les caches, les benchmarks et les outils d'asset sont-ils déclenchés en local et en CI ?
- Quelles données sont reproductibles et versionnables, et lesquelles doivent rester locales car issues d'une ROM ou d'assets non redistribuables ?
- Comment une future contribution sera-t-elle testée, examinée, documentée et intégrée sans casser la cible PC existante ?

La phase est terminée lorsque chaque point de la checklist de sortie de la section 12 est validé ou explicitement accepté comme risque.

## 2. Principes directeurs et décisions à ne pas différer

1. **Préserver le port existant comme oracle.** Ne pas supprimer les chemins C, Meson ou libntr durant la préparation. Ils servent à compiler la référence et à comparer les comportements.
2. **Rust pur pour le domaine, Bevy pour l'infrastructure.** Les règles du jeu ne doivent pas dépendre du World Bevy, de composants de rendu, de l'horloge graphique ou du backend GPU.
3. **Ne pas confondre simulation et rendu.** Déplacement, scripts, RNG, combat et sauvegardes doivent avancer selon un tick de simulation contrôlé. Le FPS d'affichage peut être indépendant.
4. **Données explicitement versionnées.** Les parseurs, manifests, formats intermédiaires, tables générées et caches doivent chacun porter une version ou un hash qui permet de détecter une incompatibilité.
5. **Cache = accélérateur, jamais vérité.** Il doit être sûr de supprimer tous les caches et de reconstruire les mêmes résultats.
6. **Fail closed sur les assets invalides.** Les formats externes, binaires et archives doivent être validés avant d'alimenter le runtime.
7. **Pas de ROM dans GitHub Actions.** Les tests CI utilisent des fixtures synthétiques et des échantillons légalement redistribuables. Les tests nécessitant des données locales sont séparés et ne téléversent ni journaux sensibles ni assets extraits.
8. **Mesurer avant d'optimiser.** Aucun objectif chiffré de FPS, mémoire ou temps de chargement n'est inventé avant l'établissement de la baseline et du matériel de référence.
9. **Automatisation non destructive par défaut.** Les scripts de nettoyage, génération et synchronisation exposent un mode dry-run et ne suppriment rien sans confirmation explicite.
10. **Pas de migration globale en une PR.** Garder les étapes petites, testables, réversibles et assorties d'un critère d'acceptation.

## 3. Chantier A — périmètre, provenance et cartographie du projet

### A1. Geler la baseline C/PC

- Enregistrer le commit de référence, les sous-modules/sous-projets, les versions d'outils et les commandes de compilation.
- Faire au moins un build Linux propre documenté et définir ce que signifie « build de référence valide ».
- Conserver les logs de compilation et les checksums de sortie comme artefacts temporaires de référence, sans publier de données propriétaires.
- Capturer des scènes repères à des moments reproductibles : titre, intérieur, route, dialogue, menu, transition de carte, rencontre, combat, sauvegarde/chargement.
- Documenter la procédure de lancement, la configuration de touches et les raccourcis de debug existants.
- Établir une règle de changement : la baseline ne change qu'avec un commit volontaire et une note expliquant les nouveaux résultats attendus.

### A2. Produire une carte du code et des dépendances

Un outil d'inventaire, non un audit manuel ponctuel, devra générer des rapports stables :

- fichiers et volume par répertoire et extension ;
- grandes unités et modules, liens include/appels lorsqu'ils sont extractibles ;
- inventaire des sous-projets Meson, dépendances, versions et révisions ;
- cibles du Makefile/Meson, outils générateurs, entrées/sorties et dépendances ;
- ressources et formats par famille ;
- fichiers produits automatiquement et endroits qui les génèrent ;
- code PC-port spécifique séparé du code de gameplay ou du chemin ARM.

Le rapport doit distinguer le code du jeu, les outils, les ressources brutes, les données générées et les dépendances vendoriées ou téléchargées. Il ne doit pas considérer automatiquement chaque fichier du dépôt comme une ressource à convertir.

### A3. Inventaire de provenance et licences

- Dresser la liste des licences et notices propres au code, aux sous-projets, outils et dépendances.
- Identifier les catégories d'assets dont la redistribution est interdite ou incertaine.
- Repérer les fichiers générés, importés, extraits ou convertis et enregistrer leur provenance.
- Documenter les données nécessaires localement et les chemins exclus du contrôle de version.
- Établir une politique de CI et de packaging qui interdit l'envoi de ROM ou d'assets privés vers les logs et les artefacts.
- Ne supprimer aucune notice de licence sous prétexte qu'elle est issue de la documentation initiale.

**Livrables A :** baseline documentée, inventaire de l'arbre, inventaire des dépendances et registre de provenance/licences.

## 4. Chantier B — spécification fonctionnelle et contrat de parité

### B1. Matrice de fonctionnalités

Créer une table suivie en Git, par fonctionnalité et non par pourcentage abstrait :

- fonctionnalité et identifiant stable ;
- zone source C et overlay concernés ;
- données/archives/commandes de script nécessaires ;
- dépendances fonctionnelles ;
- priorité P0/P1/P2/P3 ;
- statut : inconnu, inventorié, prototypé, testé, porté, comparé, accepté ;
- test qui prouve le résultat ;
- divergences connues et décision produit.

Commencer par le « parcours vertical » choisi : démarrer, afficher deux écrans, entrer dans une carte, déplacer le personnage, collisionner avec un obstacle, parler à un PNJ, exécuter un petit script et déclencher une transition. Le parcours doit être choisi à partir des ressources réelles du dépôt et documenté avec les IDs nécessaires.

### B2. Contrat de compatibilité

Trancher dans un ADR les points suivants avant P0 :

- le rendu est-il pixel-identique, visuellement équivalent ou adapté au PC ?
- quelle disposition des écrans est le défaut et lesquelles sont optionnelles ?
- quelle précision des animations, fades, sons et temporisations est nécessaire ?
- le gameplay doit-il reproduire certains glitches historiques ?
- quel est le périmètre des langues et variantes de ROM ?
- l'import des sauvegardes DS est-il une exigence initiale ou une phase séparée ?
- quelles fonctionnalités réseau historiques sont explicitement hors périmètre initial ?
- quels comportements sont les invariants non négociables : collisions, scripts, RNG de test, effets de combat, flags/variables et progression ?

### B3. Corpus de parité

Construire un corpus versionné de scénarios avec :

- état de départ et révision de la baseline ;
- séquence d'entrées horodatée par tick, non par durée murale ;
- événements et résultats métier attendus ;
- captures des deux écrans quand cela a du sens ;
- sauvegarde d'entrée/sortie anonymisée ou fixture synthétique ;
- règles de comparaison et tolérances documentées.

Prévoir trois niveaux :
1. **fixtures synthétiques** en CI, redistribuables et rapides ;
2. **fixtures de référence locale** pour les données nécessitant une installation utilisateur ;
3. **tests manuels documentés** pour les effets impossibles à vérifier de manière fiable sur chaque runner.

Les captures GPU peuvent varier légèrement selon la plateforme. Comparer séparément les valeurs métier, les dimensions, les palettes/layers attendus et le diff visuel ; ne pas faire d'une égalité pixel absolue entre tous les GPU un critère universel.

**Livrables B :** matrice de fonctionnalités, ADR du contrat de parité, corpus versionné et procédure pour ajouter un cas.

## 5. Chantier C — architecture et décisions (ADR)

Avant d'écrire des systèmes de gameplay, créer un dossier docs/architecture/decisions/ et y consigner des décisions courtes, datées, discutables et révisables.

ADR prioritaires :

- **ADR-0001 :** Bevy comme infrastructure ; code du domaine indépendant du moteur.
- **ADR-0002 :** frontières du workspace et responsabilité de chaque crate.
- **ADR-0003 :** coordonnées, unités, axes, origines, conversion fixed-point DS et positions sur grille.
- **ADR-0004 :** ticks, ordre des systèmes, déterminisme, RNG et traitement des opérations asynchrones.
- **ADR-0005 :** composition des écrans, pipeline 2D DS et voie de rendu 3D.
- **ADR-0006 :** politique des IDs stables, manifests, formats intermédiaires et cache de ressources.
- **ADR-0007 :** scripts de terrain/combat : bytecode, validation, erreurs et traces.
- **ADR-0008 :** format de sauvegarde, migrations et compatibilité DS.
- **ADR-0009 :** journalisation, télémétrie locale, snapshots et profilage.
- **ADR-0010 :** versions, features Bevy, dépendances et politique de mise à jour.

Chaque ADR inclut le contexte, les options considérées, la décision, les conséquences, le coût d'un changement futur et le test ou prototype qui pourra invalider la décision.

### Version Bevy

Bevy 0.20.0 est la candidate actuelle et sa publication officielle date du 8 octobre 2026. Avant de la figer, réaliser un spike technique court et reproductible avec la version stable candidate et, à titre de comparaison, la version précédente maintenue si un blocage apparaît. Tester au minimum : compilation Linux propre, création de fenêtre, deux cibles de rendu logique, texture/compute ou pipeline personnalisé envisagé, gestion d'assets, test headless et intégration du profiler. Après décision : version exacte, Cargo.lock commité, features minimales explicites et mise à jour uniquement par PR planifiée. La date récente de publication impose une vérification des plugins compatibles et des changements d'API, pas un rejet automatique de la version.

Références : https://bevy.org/news/bevy-0-20/ et https://github.com/bevyengine/bevy/releases

### Workspace proposé

Garder le projet C/Meson actuel intact et isoler la nouvelle chaîne dans un répertoire dédié, par exemple engine/. Ce choix évite que Cargo, les scripts de ressources, le répertoire target/ et les builds natifs se gênent.

Préparer les frontières suivantes sans obligation de créer toutes les crates immédiatement :

- platinum_app : entrée, fenêtre et configuration ;
- platinum_domain : règles et identifiants métier ;
- platinum_sim : tick, ordonnanceur de simulation et RNG ;
- platinum_assets : manifests, cache et interfaces d'assets ;
- platinum_nitro : parseurs NARC/Nitro et validation ;
- platinum_field : cartes, mouvement, collisions, interactions ;
- platinum_scripts : interpréteur de scripts de terrain/combat ;
- platinum_battle : règles de combat et IA ;
- platinum_render : composition deux écrans, rendu 2D/3D ;
- platinum_ui : menus, texte et navigation ;
- platinum_audio : traduction des commandes sonores ;
- platinum_save : état persistant, migration et import/export ;
- xtask : commandes d'ingénierie et orchestration d'outils.

Ne pas créer d'emblée une micro-crate pour chaque fichier C. Une séparation est justifiée par une responsabilité, un contrat de test ou une frontière de dépendance, pas par le nombre de dossiers.

## 6. Chantier D — automatisation de développeur

Préparer une seule interface de commandes, idéalement un outil xtask compilé en Rust, pour que les développeurs et la CI appellent les mêmes opérations. Les commandes initiales envisagées :

- **doctor** : contrôle des outils, versions, OS, place disque, dépendances graphiques et état du dépôt ; imprime des actions correctives sans modifier la machine ;
- **inventory** : régénère l'inventaire code/ressources/dépendances dans un format déterministe ;
- **assets list** : répertorie les types de ressources et les membres d'archives ;
- **assets verify** : vérifie hashes, bornes, manifestes, références manquantes et versions de formats ;
- **assets diff** : compare deux manifestes et explique les ajouts, suppressions ou changements d'ID ;
- **gen check** : régénère les sorties dans un répertoire temporaire et échoue si le diff n'est pas vide ;
- **fixtures check** : confirme que le corpus de test présent est complet et conforme à sa provenance ;
- **parity capture / parity compare** : capture ou compare une scène avec les paramètres décrits par le test ;
- **bench** : lance les benchmarks autorisés et exporte des résultats JSON avec commit, machine et toolchain ;
- **docs check** : valide les liens internes, liens externes configurés, fichiers attendus et références aux ADR ;
- **licenses report** : sort l'inventaire de licences et des dépendances ;
- **clean generated --dry-run** : liste ce qui serait supprimé, sans effacer par défaut.

Toutes les sorties générées doivent être déterministes (tri explicite, chemins normalisés, locale fixée, timestamps exclus sauf besoin). Les commandes qui écrivent doivent proposer un mode vérification sans écriture et retourner des codes de sortie exploitables par CI.

Ne jamais introduire une commande d'extraction ou de téléversement qui envoie automatiquement le contenu d'une ROM, des textures, modèles, sauvegardes personnelles ou chemins locaux vers une API distante.

## 7. Chantier E — workflows GitHub Actions, caches et performance de CI

### E1. Séparer les workflows

Ne pas remplacer les workflows existants ARM/Linux/Windows qui construisent le port courant. Ajouter des workflows Rust dédiés, puis améliorer la politique actuelle par des changements indépendants.

**Politique de commits et de concurrence CI :** voir [docs/operations/commit-and-ci-policy.md](../operations/commit-and-ci-policy.md). Les lots liés doivent être poussés en une seule mise à jour de référence (même si l'historique contient plusieurs commits). Les workflows lourds annulent les exécutions obsolètes pour la même branche/PR. Le batching limite les événements CI ; la concurrence n'est qu'un filet de sécurité, car un job annulé peut avoir déjà utilisé des ressources.

1. **rust-pr.yml — rapide, à chaque PR**
   - checkout ;
   - installation du toolchain exact ;
   - restauration du cache Rust ;
   - formatage (cargo fmt --check) ;
   - contrôles de dépendances/manifestes ;
   - clippy sur les crates créées ;
   - tests unitaires et tests de parseurs synthétiques ;
   - compilation Linux de l'application minimale.

2. **rust-integration.yml — intégration**
   - compilation de tous les targets réellement supportés ;
   - tests headless ;
   - vérification du pipeline d'assets avec fixtures redistribuables ;
   - tests de génération déterministe ;
   - tests différentiels locaux désactivés quand les assets requis ne sont pas installés.

3. **rust-nightly.yml — maintenance programmée**
   - audit des dépendances et licences ;
   - validation de la documentation ;
   - benchmark de référence non bloquant initialement ;
   - signalement des dépendances obsolètes et changements Bevy à examiner ;
   - rapport du taux de cache, temps de compilation et taille des artefacts.

4. **rust-profile.yml — manuel**
   - lancer un benchmark précis sur un runner connu ;
   - archiver les mesures JSON et les symboles nécessaires au profiling ;
   - ne jamais exécuter automatiquement des benchmarks coûteux sur chaque modification documentaire.

5. **release.yml — ultérieur**
   - droits d'écriture accordés uniquement à l'étape de publication ;
   - aucun secret ni permission de publication dans les jobs de test/PR.

### E2. Droits et chaîne d'approvisionnement

- Déclarer les permissions au niveau de chaque workflow/job ; la CI de test devrait n'avoir que contents: read, sans accès à des secrets de publication.
- Épingler les actions tierces à un SHA complet vérifié, ou adopter un mécanisme de verrouillage de dépendances de workflow équivalent si le dépôt l'active.
- Limiter les déclenchements des workflows de publication et séparer les jobs de build non privilégiés des jobs qui publient.
- Ne pas exposer de secrets à des workflows déclenchés par des contributions externes.
- Contrôler les artifacts : taille, chemins, types et absence de ROM, sauvegarde utilisateur, dumps ou ressource propriétaire non autorisée.

GitHub recommande les permissions minimales et l'épinglage des actions à des SHA complets : https://docs.github.com/en/actions/reference/security/secure-use

### E3. Stratégie de cache, par couches

**Cache Cargo/compilation**
- Commencer avec une action de cache Rust maintenue, par exemple Swatinem/rust-cache, après sélection du toolchain : https://github.com/Swatinem/rust-cache
- La clé de cache doit varier au minimum selon l'OS, la version de Rust, le Cargo.lock et les paramètres/features qui changent les artefacts. Séparer les caches incompatibles ; accepter les cache misses comme un fonctionnement normal.
- Cacher le registre Cargo, les dépendances Git approuvées et les artefacts de compilation quand cela reste compatible avec le runner et l'espace disponible.
- Ne pas cacher des secrets, ROM, sauvegardes, assets extraits privés ou fichiers de sortie considérés comme source de vérité.
- Mesurer le temps de build à froid/chaud avant de décider des caches additionnels.

**sccache — étape facultative après mesure**
- Tester sccache si les recompilations de dépendances dominent le temps de CI.
- Vérifier ses limites (incrémental, macros procédurales et commandes externes) et comparer son coût de stockage aux gains réels.
- Ne pas empiler sans preuve plusieurs caches qui se recouvrent. Documenter la procédure de purge/versionnement du cache.

Références : https://github.com/mozilla/sccache et https://github.com/mozilla/sccache/blob/main/docs/Rust.md

**Cache de ressources — propre au projet**
- Construire une clé de contenu à partir du hash de la ressource source, de la version du parseur, de la version du schéma intermédiaire et des options de conversion.
- Écrire dans un fichier temporaire, valider la sortie, puis effectuer un remplacement atomique.
- Séparer cache d'archives décompressées, cache des structures parsées, cache de conversion graphique et cache des résultats de tests.
- En cas de mismatch de hash/version, invalider la sortie et convertir à nouveau ; ne jamais deviner qu'une ancienne sortie est valide.
- Stocker les entrées de cache sous un identifiant stable, jamais seulement sous le nom de fichier.
- Prévoir une commande de diagnostic montrant les hits/misses, l'origine de l'entrée et la raison d'une invalidation.

**Cache local de développeur**
- Configurer des chemins clairs sous un répertoire ignoré, avec une commande pour afficher taille, âge et purge simulée.
- Ajouter un mode « cache vide » en CI pour prouver que le build est reproductible sans cache.
- Les caches doivent pouvoir être effacés à tout moment sans perte de donnée suivie par Git.

### E4. Quand un workflow doit tourner ?

Définir des filtres de chemins explicites, mais ne pas ignorer aveuglément tous les .md : la documentation d'architecture, les décisions et les guides de build doivent subir le contrôle de liens et de cohérence. Exemple de règle :
- code ou Cargo : vérification Rust + tests concernés ;
- assets/parseurs/manifests : tests d'assets et de génération ;
- docs uniquement : docs check ;
- modification workflows/outils de build : validation de configuration et workflow complet pertinent ;
- nightly : audits coûteux et benchmarks ;
- manuel : profiling, purge de cache et diagnostics approfondis.

Les workflows doivent rester compréhensibles : préférer quelques pipelines spécialisés à un méga-workflow conditionnel illisible. Toute optimisation de CI doit afficher le temps économisé et le taux de cache après plusieurs exécutions.

## 8. Chantier F — outillage, qualité et observabilité

### F1. Toolchain fixée

- Ajouter rust-toolchain.toml avec une version stable déterminée lors du spike, composants nécessaires uniquement (rustfmt, clippy).
- Commettre Cargo.lock pour l'application/workspace afin que CI et développeurs construisent les mêmes versions.
- Préparer une configuration cargo explicite pour les features de Bevy et la compilation multi-plateforme.
- Éviter le recours implicite à nightly ; toute dépendance nightly doit être justifiée par ADR.
- Documenter les prérequis Linux et le mode sans GPU lorsqu'il est disponible.

### F2. Contrôles qualité à sélectionner

- rustfmt et clippy dès le début ;
- tests unitaires natifs, tests d'intégration et fixtures synthétiques ;
- cargo-deny ou équivalent pour licences, advisories et sources de dépendances ;
- cargo-audit selon le flux de mise à jour des advisories ;
- cargo-nextest si le volume de tests le justifie ;
- cargo-llvm-cov après l'établissement d'une vraie suite de tests ;
- Criterion ou un harness équivalent pour les benchmarks stables ;
- snapshot tests pour les manifestes et rapports textuels déterministes ;
- validation YAML/workflows et vérification des liens de documentation.

Ne pas traiter un score de couverture comme objectif isolé : la priorité est la couverture des comportements critiques et des formats malformés.

### F3. Observabilité utilisable dès le premier jour

- Utiliser des spans/traces structurés séparés par domain : app, sim, field, scripts, battle, assets, render, audio, save.
- Attacher aux logs des identifiants stables (carte, script, offset, ressource, tick), en évitant les données personnelles.
- Définir les niveaux et conventions de nommage dans un guide.
- Créer dès le début une commande de dump de configuration/version et un mode diagnostic.
- Le profiler doit pouvoir distinguer CPU simulation, attente de chargement, préparation des assets et GPU.
- Ajouter des snapshots d'état métier activables en mode debug, sans dépendre de la présentation visuelle.

### F4. Politique de performance

Avant P0, définir la méthode de mesure, mais ne pas fixer de chiffre arbitraire. Les premiers résultats doivent enregistrer :
- OS/CPU/GPU/RAM du runner ou poste ;
- commit, versions de Rust/Bevy, paramètres de build et features ;
- durée de lancement, chargement à froid/chaud, latence p95/p99 si pertinente ;
- temps CPU par système, GPU par passe si disponible, mémoire résidente et allocation/chargement ;
- taux de cache des dépendances et assets.

Commencer par publier une tendance non bloquante. Les seuils CI ne seront activés que lorsque la variance de mesure est connue et que les runners sont suffisamment comparables.

## 9. Chantier G — documentation à établir en amont

Ne pas écrire une encyclopédie avant d'avoir testé les décisions. Les documents ci-dessous sont des contrats courts, maintenus avec le code.

### À créer pendant la préparation

- **docs/architecture/README.md** — index, liens et règles de mise à jour.
- **docs/architecture/decisions/0001-bevy-boundary.md** — frontière Bevy/domaine.
- **docs/architecture/decisions/0002-workspace.md** — crates et dépendances permises.
- **docs/architecture/decisions/0003-deterministic-simulation.md** — tick, RNG et ordonnance.
- **docs/architecture/decisions/0004-rendering-model.md** — écrans logiques, coordonnées et pipeline.
- **docs/architecture/decisions/0005-asset-cache.md** — manifests, versions et invalidation.
- **docs/migration/feature-matrix.md** — couverture fonctionnelle.
- **docs/migration/source-map.md** — ancien fichier/système, futur module, tests, progression.
- **docs/migration/parity-testing.md** — corpus, captures et critères de comparaison.
- **docs/assets/format-inventory.md** — formats observés, outils producteurs/consommateurs et priorités.
- **docs/assets/provenance-and-licenses.md** — provenance, usages autorisés et politique de packaging.
- **docs/operations/developer-setup.md** — setup reproductible et dépanneur.
- **docs/operations/ci-and-caching.md** — workflows, clés de cache, invalidation et sécurité.
- **docs/operations/profiling.md** — benchmark, captures et interprétation.
- **docs/quality/testing-strategy.md** — niveaux de tests, fixtures et couverture.

### À créer lors du P0/P1, pas avant de disposer d'évidence

- guide du moteur de scripts ;
- spécification détaillée du format intermédiaire de modèles ;
- catalogue des passes de rendu ;
- format des sauvegardes et plan de migration ;
- guide de contribution au gameplay ;
- procédure d'import de sauvegarde DS si cette compatibilité est retenue.

Toute documentation qui décrit l'existant doit distinguer explicitement les faits vérifiés, les hypothèses et les fonctionnalités non encore portées. Chaque décision doit être liée à un test ou à une question restant à résoudre.

## 10. Arborescence préparatoire

Conserver la structure historique intacte et ajouter les artefacts de préparation progressivement :

- engine/ : workspace Rust/Bevy, indépendant du build C/Meson ;
- engine/.cargo/ : config locale au workspace, si nécessaire ;
- engine/crates/ : premières crates par responsabilité ;
- engine/tools/xtask/ : commandes d'ingénierie ;
- engine/tests/fixtures/synthetic/ : petites fixtures synthétiques ;
- docs/architecture/ et docs/architecture/decisions/ ;
- docs/migration/ ;
- docs/assets/ ;
- docs/operations/ ;
- .github/workflows/rust-pr.yml ;
- .github/workflows/rust-integration.yml ;
- .github/workflows/rust-nightly.yml ;
- .github/workflows/rust-profile.yml ;
- .github/dependabot.yml ou processus documenté de mise à jour des dépendances/actions.

Ne pas déplacer les répertoires C existants dans cette phase. Ajouter au .gitignore les sorties Rust (engine/target/), les caches d'assets, les dumps et les captures locales sensibles. Les fixtures petites et redistribuables restent suivies par Git.

## 11. Exécution proposée : paquets de travail P-1

| Paquet | Travail | Sortie vérifiable | Bloque P0 si absent ? |
|---|---|---|---|
| P-1.1 | Baseline C/PC reproductible | Runbook, commit, logs et scènes repères | Oui |
| P-1.2 | Cartographie code/données/dépendances | Rapport généré et inventaire des formats | Oui |
| P-1.3 | Contrat fonctionnel et corpus de parité | Feature matrix + premier parcours choisi | Oui |
| P-1.4 | ADR fondamentales et essai Bevy | Décisions et résultat reproductible du spike | Oui |
| P-1.5 | Toolchain, structure et contrôles qualité | Toolchain fixée, conventions et commandes documentées | Oui |
| P-1.6 | CI Rust et cache initial | PR workflow vert sans asset privé | Oui |
| P-1.7 | xtask doctor/inventory/gen-check | Commandes deterministes et mode dry-run | Recommandé ; doctor obligatoire |
| P-1.8 | Documentation et sécurité de la chaîne | Index, runbook, provenance/licences et CI à permissions minimales | Oui |
| P-1.9 | Profilage initial | Méthode, machine et résultats de référence initiaux | Méthode obligatoire, seuils non |
| P-1.10 | Revue de sortie | Checklist signée dans une PR dédiée | Oui |

Ordre conseillé : P-1.1 et P-1.2 en premier ; P-1.3 en parallèle de l'inventaire ; décisions P-1.4 avant de figer le workspace ; P-1.5 et P-1.7 ensemble ; CI/cache P-1.6 après un premier squelette compilable ; sécurité/documentation en continu ; revue finale avant P0.

## 12. Checklist de sortie — autorisation de démarrer P0

P0 peut débuter lorsque :

- [ ] Le commit C de référence et la commande de build sont documentés et reproductibles.
- [ ] La stratégie CI de remplacement est documentée et vérifiable ; les workflows historiques sont archivés hors de `.github/workflows/` et ne sont pas réactivés tels quels.
- [ ] La cartographie générée distingue code, ressources, générateurs, dépendances et sorties de build ; le script d'inventaire a été exécuté et son rapport examiné.
- [ ] La provenance/licence des dépendances et règles de distribution sont documentées.
- [ ] Le parcours vertical est choisi et les ressources/IDs nécessaires sont identifiés.
- [ ] Les comportements à préserver et les divergences PC autorisées sont écrits.
- [ ] Le spike Bevy démontre la fenêtre, les deux surfaces logiques et le test headless ; la version exacte est décidée.
- [ ] Les conventions de coordonnées, tick, RNG, IDs stables et erreurs sont approuvées.
- [ ] Un workspace Rust séparé compile sur Linux et son Cargo.lock est commité.
- [ ] Une commande doctor donne des diagnostics actionnables sans effectuer de modification cachée.
- [ ] Un workflow PR effectue formatage, lint, tests et build minimal avec permissions minimales.
- [ ] Le cache Cargo est facultatif, versionné par des clés explicites et ne contient aucune donnée propriétaire.
- [ ] Les fixtures synthétiques passent sans ROM/asset privé.
- [ ] Les rapports de génération sont déterministes et un gen-check détecte les écarts.
- [ ] Les docs de préparation ont un index et leurs décisions/hypothèses sont clairement marquées.
- [ ] La méthode de benchmark est en place, même si les seuils de performance sont encore inconnus.
- [ ] Une PR de synthèse présente les risques résiduels et reçoit une revue.

Tout élément non rempli doit être accepté explicitement comme une exception documentée, avec responsable et moment de réévaluation. « On le fera plus tard » sans propriétaire ni critère de sortie ne vaut pas validation.

## 13. Recommandation finale

Le plus grand gain de cette phase sera de supprimer les opérations manuelles répétitives et de transformer l'incertitude en rapports testables. La première ligne de code Rust ne doit pas être le début de la découverte de l'architecture : elle doit être le début de l'implémentation d'une architecture déjà suffisamment comprise et mesurable.

Je recommande de terminer P-1 par une PR unique et relisible qui contient le workspace minimal, les conventions, la CI initiale, l'inventaire, les ADR essentiels et ce plan. La création des systèmes de gameplay reste en dehors de cette PR. Une fois la checklist validée, P0 devient un objectif borné, avec des étapes, des critères et des outils déjà prêts.
