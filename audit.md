# Audit technique — remplacement du moteur par Rust + Bevy

> **Dépôt audité :** rakmahefa/pokeplatinum  
> **Branche :** pc_port  
> **Révision de référence :** e6a36019c67e49cd80b16a63347a16f2ca51646f  
> **Date :** 2026-10-22  
> **Objectif :** remplacer progressivement l’implémentation native actuelle par un runtime de jeu écrit en Rust et rendu par Bevy, sans prétendre que Bevy reproduit automatiquement les spécificités de la Nintendo DS.

## Phase préalable P-1 — Préparation obligatoire

**P0 ne doit pas commencer avant la clôture de cette phase.** La préparation doit établir une baseline reproductible, un corpus de parité, une cartographie des formats et dépendances, les ADR fondamentales, le workspace Rust isolé, les outils développeur et des workflows CI/cache sécurisés.

Le plan détaillé, les livrables, les commandes d'automatisation envisagées et la checklist de sortie sont documentés dans [docs/architecture/PREPARATION.md](docs/architecture/PREPARATION.md).

P-1 inclut notamment :
- geler et documenter le port C comme oracle, choisir la première tranche verticale et définir la matrice des fonctionnalités ;
- inventer les ressources/formats, générateurs, dépendances et obligations de provenance/licence ;
- valider la version Bevy avec un spike reproductible avant de la figer ;
- séparer domaine Rust pur, runtime Bevy et compatibilité Nitro/DS ;
- préparer doctor/inventory/gen-check, les fixtures synthétiques, le profilage et le cache à clés versionnées ;
- établir des workflows PR rapides, intégration, maintenance et profilage avec permissions minimales ;
- documenter les contrats d'architecture et définir les critères de sortie.

La fin de P-1 est conditionnée à une revue explicite de la checklist. Les exceptions doivent avoir une justification, un propriétaire et une date de réévaluation.

## 1. Résumé exécutif

### Conclusion

La migration est **réalisable, mais de grande ampleur**. Il ne s’agit pas de remplacer une bibliothèque de rendu par Bevy ni de traduire mécaniquement les fichiers C en Rust. Le code actuel combine le gameplay décompilé de Pokémon Platinum, des abstractions propres au jeu, des services NitroSDK/NitroSystem et une couche de compatibilité pour le PC. Les responsabilités sont réparties entre le code de terrain, les overlays, les scripts, le système de combat, les interfaces et un pipeline de données compilé avec Meson.

Bevy fournit le socle d’application, l’ECS, la gestion des assets, les systèmes de rendu, l’entrée et l’audio standard. Il ne fournit pas l’équivalent direct du matériel DS : deux écrans logiques de 256 × 192, les couches 2D tuilées et leurs palettes, les règles de priorité, les transferts VRAM/OAM, les formats Nitro 3D et les séquences audio Nintendo. Ces éléments demandent des adaptateurs, des importateurs et, pour certains effets, des systèmes de rendu spécialisés.

**Recommandation :** construire un nouveau runtime dans un workspace Rust/Bevy, faire fonctionner d’abord une tranche verticale minimale (démarrage, deux écrans, chargement d’une carte, déplacement, collision, dialogue), puis migrer les systèmes de gameplay un par un. Conserver l’exécutable C existant comme oracle de comportement et d’image jusqu’à ce que les tests de non-régression soient suffisamment solides. Ne supprimer l’ancien runtime qu’après la couverture fonctionnelle décidée par le projet.

### Décisions structurantes

1. **Séparer les règles du jeu du rendu.** Les règles de déplacement, collisions, scripts, combats, inventaire et sauvegarde ne doivent pas dépendre directement des entités Bevy ni du GPU.
2. **Adopter Bevy 0.20.0 comme version de départ épinglée**, car la version 0.20 a été publiée le 8 octobre 2026. Les mises à jour seront des changements explicites, jamais une dépendance flottante sur la dernière version. Référence : https://bevy.org/news/bevy-0-20/ et https://github.com/bevyengine/bevy/releases
3. **Préserver le modèle temporel du jeu** : ticks de simulation contrôlés, transitions d’état explicites et aléatoire reproductible là où le gameplay en dépend.
4. **Traiter les formats de ressources comme un sous-projet à part entière.** Le code du jeu et les données ne peuvent pas être migrés indépendamment.
5. **Reporter le multijoueur en ligne jusqu’à la parité solo.** La compatibilité de transport, de protocole et de services historiques n’est pas une fonctionnalité automatiquement obtenue par Bevy.
6. **Ne pas distribuer de ROM ni d’assets propriétaires extraits.** Le pipeline cible doit fonctionner sur des données légalement fournies par l’utilisateur et documenter clairement les limites de redistribution.

### Limites de cet audit

L’audit repose sur l’inspection statique du dépôt GitHub, notamment le code source, les fichiers de construction, les ressources et les documents sous docs/. Je n’ai pas exécuté le build ni lancé le jeu dans un environnement de test ; les performances, l’état exact des bugs d’exécution et la parité graphique restent à mesurer. Les estimations ci-dessous sont des estimations d’architecture et de risque, non un engagement de calendrier.

## 2. Périmètre et état observé

### 2.1 Empreinte du dépôt

À la révision de référence, l’arbre Git contient environ :

| Zone | Fichiers observés | Volume indicatif | Rôle |
|---|---:|---:|---|
| src/ | 1 033 | 24,3 MB | Logique du jeu, systèmes et overlays |
| include/ | 1 986 | 3,1 MB | Interfaces C, constantes et structures |
| res/ | 24 163 | 107,4 MB | Ressources, données, scripts, graphismes et audio |
| generated/ | 108 | 0,34 MB | Constantes/données générées par les outils |
| tools/ | 235 | 2,1 MB | Convertisseurs, générateurs et outils de build |
| docs/ | 20 | 0,16 MB | Documentation technique, formats et comportement |

Les volumes sont ceux des blobs suivis par Git et ne représentent ni la taille mémoire à l’exécution, ni la taille d’un éventuel paquet final. Les dossiers docs/ ont été restaurés à partir de la révision antérieure du fork.

### 2.2 Construction actuelle

Le projet utilise Meson/Ninja et un Makefile qui pilote plusieurs cibles : ARM pour la ROM, Linux, Windows 64 bits et Nintendo Switch. Le build natif s’appuie notamment sur les sous-projets libntr et les bibliothèques NitroSDK/NitroSystem/NitroWiFi/NitroDWC fournies par cette chaîne. Le fichier subprojects/libntr.wrap suit actuellement la branche distante main, ce qui présente un risque de reproductibilité : la révision de la dépendance n’est pas épinglée à un commit immuable.

Les outils du dossier tools/ et les sous-répertoires de res/ produisent des données et fichiers de ressources utilisables par le jeu. Les fichiers generated/ et les listes d’ordre/manifestes impliquent que l’ordre et les identifiants générés peuvent faire partie du contrat entre données et code.

**Conséquence :** Cargo + Bevy ne remplace pas à lui seul l’intégralité du build. Il faut décider explicitement quels outils C/Python restent utiles au pipeline d’import, lesquels deviennent des outils Rust et comment les identifiants générés sont stabilisés.

### 2.3 Architecture actuelle constatée

- **Boucle principale :** src/main.c orchestre l’application, les tâches principales, les tâches d’impression, l’entrée et le son. src/system.c définit des tâches et callbacks associés aux événements VBlank/HBlank et à des opérations propres au cycle d’image DS.
- **Transitions d’applications :** src/overlay_manager.c implémente une machine d’état d’application/overlay (chargement, initialisation, exécution, sortie). Le système de menus et de processus repose largement sur cette convention.
- **Terrain :** src/field_system.c gère le cycle de vie du FieldSystem, les processus parent/enfant et le traitement des entrées/événements/tâches. src/overlay005/field_control.c traite une partie importante des actions de terrain, transitions, événements de coordonnées et rencontres.
- **Chargement du monde :** src/overlay005/fieldmap.c, land_data.c et loaded_map_buffers.c gèrent les données de carte, modèles, collisions BDHC et buffers. docs/maps/loading_maps.md décrit quatre cartes chargées selon un agencement 2×2, avec chargement initial et chargement paresseux en arrière-plan.
- **Objets et mouvement :** src/map_object.c et src/map_object_move.c contiennent une logique conséquente pour les objets de carte, les directions, les positions, les animations de déplacement et les interactions avec le terrain. Ce n’est pas équivalent au déplacement libre typique d’un jeu 3D Bevy.
- **Combat :** src/battle/battle_system.c, battle_main.c, battle_script.c, les modules AI et de nombreuses ressources de scripts portent la logique et la présentation du combat.
- **3D :** src/easy3d.c et src/easy3d_object.c appellent les abstractions NitroSystem/NNS G3D, gèrent les modèles, textures/palettes, animations et l’envoi de ressources vers le système graphique.
- **2D :** docs/2d_rendering.md décrit les arrière-plans en tuiles, couches, palettes, priorités, scroll, transparence et différents modes de fond. Reproduire uniquement les sprites par défaut de Bevy ne garantit pas cette composition.
- **Données et archives :** src/narc.c centralise la correspondance de nombreux identifiants NARC vers les chemins de ressources. La migration doit conserver les dépendances et les indices croisés entre archives.
- **Sauvegardes :** src/savedata.c et src/savedata/save_table.c gèrent une structure de sauvegarde en blocs et tables d’entrées, avec logique de validation et d’initialisation.
- **Audio :** src/sound_system.c initialise le système sonore Nitro et les archives SDAT. Une lecture WAV/OGG simple n’est pas un remplacement exact des séquences, banques, échantillons, effets et événements sonores du jeu.
- **Couche PC :** src/port/ contient des interfaces de configuration, debug, cheats et utilitaires PC. Cette présence ne signifie pas que la logique de jeu a déjà été découplée de la couche Nitro.

## 3. Objectifs fonctionnels à verrouiller

Avant toute réécriture, le projet doit définir le niveau de compatibilité visé. Le choix recommandé est une **réimplémentation fidèle du gameplay solo**, avec interfaces et rendu adaptés au PC, en évitant de promettre une émulation bit à bit du matériel DS.

### Indispensable au socle

- Démarrage et transitions d’état prévisibles.
- Présentation des deux écrans logiques, avec agencement configurable (vertical, côte à côte et mode fenêtré agrandi), tout en conservant une résolution logique native de 256 × 192 par écran.
- Entrées clavier/manette ; pointeur/souris mappé sur les coordonnées de l’écran inférieur et les interactions tactiles.
- Chargement de cartes, caméra, altitude, collisions, limites de déplacement, objets, PNJ, transitions/warps et interactions.
- Machine de scripts du terrain et dialogues afin que la progression et les événements soient pilotés par les données du jeu, et non par des scènes codées en dur.
- Combat solo avec état déterministe, calculs des actions, statistiques, effets, capacités, objets, changements d’état et scripts de combat.
- Inventaire, équipe, Pokédex, menus essentiels, progression et sauvegarde.
- Sons, musique, animations et transitions visuelles suffisants pour le périmètre déclaré.

### Compatibilité à décider séparément

- Import des sauvegardes d’origine et éventuelle compatibilité binaire avec les sauvegardes DS.
- Connexion/multijoueur, fonctionnalités Wi-Fi/WFC historiques, échange et combat en réseau.
- Fonctionnalités périphériques du matériel DS (micro, clapet, vibration/rumble si concerné).
- Parité exacte des glitches et effets de synchronisation matérielle.

Il ne faut pas qualifier de « terminé » un port qui ne fait que rendre une carte : la progression réelle dépend fortement des scripts, overlays, interfaces et données événementielles.

## 4. Architecture cible recommandée

Créer un workspace Rust indépendant du runtime C, sans mélanger immédiatement les deux modèles de mémoire et de cycle de vie. Exemple de découpage :

| Crate | Responsabilité |
|---|---|
| platinum_app | Entrée du programme, fenêtre, configuration, états globaux et sélection de mode de rendu |
| platinum_domain | Modèles indépendants du moteur : joueur, équipe, objets, progression, règles et identifiants |
| platinum_sim | Tick déterministe, transitions d’état, RNG seedé et orchestration de simulation |
| platinum_assets | Manifeste de ressources, identifiants stables, cache, chargement et validation |
| platinum_nitro | Parseurs NARC et formats Nitro nécessaires, avec limites et tests robustes |
| platinum_field | Cartes, grille, terrain, mouvement, collisions, PNJ, interactions, warps et scripts de terrain |
| platinum_battle | Moteur de combat, scripts, calculs, effets, IA, état de combat et RNG |
| platinum_ui | Menus, textes, fenêtres, transitions et navigation clavier/manette/pointeur |
| platinum_audio | Adaptateur de lecture des musiques, sons, cries et événements de gameplay |
| platinum_save | Modèle de sauvegarde versionné, stockage atomique et import/export optionnel |
| platinum_render | Rendu 2D, rendu 3D, composition des écrans, palettes, priorités et shaders particuliers |
| platinum_tools | CLI d’inspection/conversion des assets, vérification des manifestes et diagnostics |

Les crates de domaine doivent pouvoir être testées sans fenêtre, World Bevy ou GPU. Bevy est utilisé à la frontière d’exécution : les systèmes Bevy collectent les entrées, pilotent les étapes de simulation et projettent l’état de domaine dans les composants/entités de rendu.

### 4.1 Entités et données

Exemples de composants ECS visés : MapObjectId, GridPosition, Facing, MovementState, TileCollision, CharacterVisual, AnimationState, Interactable et RenderLayer. Une carte chargée peut être représentée par des ressources de carte typées et un ensemble d’entités de terrain, d’objets et de déclencheurs.

Ne pas stocker l’intégralité de l’état métier uniquement dans les composants visuels. Un changement d’asset, d’animation ou de caméra ne doit pas altérer une sauvegarde, une collision ou l’ordre d’exécution du script.

### 4.2 Simulation temporelle et ordre d’exécution

Utiliser un schedule de simulation à pas fixe pour les règles qui doivent suivre les ticks historiques. Le taux nominal doit être confirmé par mesures du port de référence avant d’être figé ; ne pas assimiler automatiquement le FPS de rendu au rythme du gameplay. Le rendu peut interpoler visuellement, mais ne doit pas faire avancer les scripts deux fois ou omettre des transitions.

Représenter les transitions en états nommés (démarrage, titre, terrain, dialogue, menu, combat, sauvegarde) et expliciter les conditions d’entrée/sortie. L’ordre des scripts et événements doit être couvert par tests. Les opérations asynchrones de chargement doivent publier leurs résultats au tick contrôlé, sans exposer des accès concurrents non déterministes au gameplay.

### 4.3 Deux écrans logiques

Créer deux cibles de rendu internes dimensionnées 256 × 192 (écran principal et écran inférieur), puis une composition PC configurable. Le mode par défaut doit conserver la lisibilité et la disposition des deux écrans DS. Prévoir une échelle entière optionnelle, une interpolation contrôlée et une transformation inverse des coordonnées de souris.

La composition doit prendre en charge :
- une scène 3D principale et plusieurs plans 2D composités ;
- une interface/écran inférieur distinct, dont le Pokétch si inclus au périmètre ;
- les fades, transitions et états visuels qui traversent les écrans ;
- une priorité d’affichage reproductible pour les sprites et couches ;
- un mode capture qui puisse enregistrer les deux images logiques pour les tests.

### 4.4 Renderer 2D et 3D

**Ne pas convertir toutes les ressources en sprites aplatis.** Cela serait simple pour une démo, mais ne préserverait ni les cartes, ni les animations, ni les palettes, ni les interactions de calques.

- Créer des parseurs/convertisseurs pour les formats réellement présents et utilisés : archives NARC, tilesets/cellules/palettes et cartes 2D, modèles/textures/animations Nitro 3D et données de collision BDHC. L’inventaire des formats devra être construit depuis les ressources du dépôt, puis validé sur échantillons connus.
- Pour la 3D, comparer deux approches : conversion hors ligne vers un format intermédiaire documenté (par exemple des meshes/materials internes ou un format d’échange), ou chargement direct dans des structures propriétaires. Le format d’échange ne doit pas perdre les couleurs de sommet, les matrices, les UV, les textures 4×4/palettes, les keyframes, les matériaux ou les conventions de coordonnées.
- Pour la 2D DS, conserver un modèle explicite des tuiles, cartes de tuiles, palettes, couches, priorités et effets. Un pipeline de conversion qui résout visuellement ces couches en une image par frame peut servir de prototype de validation, mais ne doit pas devenir l’architecture principale.
- Ajouter des tests de parseur pour les offsets, tailles, bornes, padding, endianess, entrées invalides et indices hors plage. Aucun asset malformé ne doit provoquer une lecture hors limites ou faire planter silencieusement l’outil.

Le renderer Bevy standard est un point de départ, pas une spécification du rendu DS. Le projet devra développer les extensions de matériaux/shaders ou passes de composition nécessaires après comparaison d’images.

### 4.5 Pipeline de données et identifiants

Le pipeline d’import doit produire un manifeste contenant au minimum : chemin source, type de format, identifiant logique, dépendances, taille, hash et état de conversion. Les identifiants utilisés dans le gameplay doivent être stables ; ne pas utiliser l’ordre d’itération d’un HashMap ou d’un dossier comme identité.

Les outils existants de traitement du dépôt peuvent être conservés temporairement comme outils d’extraction de référence, puis remplacés un par un. Ajouter des commandes déterministes du type « inspecter », « valider » et « convertir » et un test CI qui rejette toute ressource absente, doublon d’identifiant ou sortie générée non reproductible.

## 5. Matrice de migration : système actuel vers cible

| Système actuel | Cible Rust/Bevy | Risque / approche |
|---|---|---|
| main.c, system.c, SysTask, VBlank/HBlank | App Bevy, schedules, ressources de simulation et systèmes ordonnés | Élevé : sémantique temporelle matérielle à abstraire explicitement |
| ApplicationManager / overlays | États de jeu, machines à états et sous-états typés | Élevé : nombreux processus parent/enfant et opérations de sortie |
| FieldSystem et field_control | Service de terrain + systèmes ECS + file d’événements | Très élevé : règles, quêtes, entrée et scripts couplés |
| fieldmap, land_data, map matrix | MapAsset typé, MapRuntime, chargeur asynchrone avec génération de version | Très élevé : données entrelacées, cartes voisines et chargement paresseux |
| map_object / map_object_move | MapObject domaine, GridPosition, MovementState et pilote de rendu | Très élevé : mouvement sur grille, terrain, altitude, actions conditionnelles |
| Script Manager / scr_seq et commandes générées | Interpréteur de bytecode/script versionné, commandes typées, contexte et traces | Très élevé : priorité de migration fonctionnelle |
| BattleSystem / BattleMain / scripts | Moteur de combat pur avec état explicite et adaptateur d’affichage | Très élevé : nombreux effets et ordre précis des actions |
| Easy3D / NNS G3D | Importateur Nitro + assets internes + composants d’animation et matériaux | Très élevé : conversion, animations, textures et pipeline de rendu |
| BgConfig, fenêtres, sprites, palettes | UI à résolution logique + renderer 2D spécialisé | Élevé : il faut préserver l’ordre des plans, l’alignement pixel et les effets |
| NARC / archives Nitro | Bibliothèque d’assets Rust, validée, testée et découplée de la logique | Moyen/élevé : nombreux indices et formats imbriqués |
| SoundSystem / SDAT | Audio backend + lecteur de ressources ou conversion contrôlée | Élevé : séquences et synthèse instrumentale ne sont pas des fichiers audio simples |
| SaveData / SaveTable | Modèle versionné, sérialisation stable, sauvegarde atomique et import optionnel | Très élevé si compatibilité binaire recherchée |
| DWC/Wi-Fi/communication | Trait de transport isolé + protocole documenté, implémentation réseau séparée | Très élevé ; hors MVP |
| Meson/Ninja / générations C | Cargo workspace + CLI d’assets + CI reproductible | Moyen/élevé : ne pas perdre les règles de génération ni la cible ROM existante |

## 6. Plan d’exécution par phases et critères d’acceptation

Chaque phase est soumise à validation avant d’élargir le périmètre. Les pourcentages de couverture ne sont pas des critères suffisants : chaque étape doit avoir des tests et une démonstration reproductible.

### Phase 0 — Baseline et contrat de compatibilité (P0)

**Travail**
- Geler la révision de référence et documenter comment construire la cible Linux actuelle.
- Épingler les sous-projets et outils externes à des versions/commits précis, notamment libntr ; vérifier les checksums des ressources et des sorties générées.
- Créer un corpus de scènes de référence : titre, carte intérieure, route, animation de déplacement, dialogue, menu, rencontre sauvage, combat et sauvegarde.
- Capturer les deux écrans à des ticks déterminés, le log des événements et l’état de sauvegarde pertinent.
- Établir un tableau des fonctionnalités incluses/exclues du premier objectif.

**Acceptation**
- Build de référence reproductible documenté.
- Captures et cas de test versionnés ou reproductibles localement.
- Les différences permises (résolution fenêtrée, interpolation, contrôles PC) sont distinguées des différences de gameplay.

### Phase 1 — Workspace Rust et coquille d’application (P0)

**Travail**
- Créer le workspace avec une version de Rust fixée dans rust-toolchain.toml et Bevy 0.20.0 épinglé dans Cargo.toml/Cargo.lock.
- Créer l’application fenêtre, la configuration, la journalisation et la gestion explicite des états.
- Implémenter deux cibles logiques de 256 × 192, leur composition, le redimensionnement, le mode plein écran et le mapping du pointeur.
- Ajouter des contrôles clavier/manette configurables et un diagnostic des événements.

**Acceptation**
- Démarrage propre sur Linux et au moins un pipeline CI de compilation.
- Les deux écrans sont capturables séparément et correctement composités.
- Les entrées du pointeur sont exactes après changement de taille, d’échelle et d’agencement.
- Aucun système de gameplay ni ressource Nintendo n’est requis pour lancer cette coquille.

### Phase 2 — Importateur et visualiseur d’assets (P0)

**Travail**
- Inventorier les formats réels, leurs dépendances et leur couverture.
- Implémenter d’abord le lecteur NARC et les parseurs dont dépend la première carte.
- Ajouter un outil de ligne de commande d’inspection et un visualiseur d’assets de diagnostic.
- Produire un format intermédiaire versionné et documenté, sans perdre les propriétés nécessaires au gameplay.

**Acceptation**
- Tests unitaires et corpus d’archives valides/invalides.
- Chaque ressource de la tranche verticale est résolue via son identifiant logique.
- Les sorties sont stables entre deux exécutions et accompagnées d’un manifeste/hash.
- Les outils refusent les données tronquées ou incohérentes avec une erreur localisée et exploitable.

### Phase 3 — Première tranche jouable de terrain (P0)

**Périmètre choisi**
- Une carte intérieure et/ou extérieure représentative, le joueur, quelques objets/NPC, collisions et un déclencheur de transition.
- Caméra et couche 3D principale ; sprites et plans UI indispensables.
- Dialogue minimal piloté par le vrai format de script, sans recopier l’histoire en dur.
- Chargement/déchargement des assets et retour au titre.

**Acceptation**
- Même destination de déplacement et mêmes décisions de collision que le runtime C pour le corpus retenu.
- Comparaison d’images avec différences expliquées (polices, mise à l’échelle ou effet non encore porté).
- Pas de fuite d’entités/assets lors des changements de carte répétés.
- La progression peut être exécutée uniquement à partir des données chargées et du runtime Rust.

### Phase 4 — Systèmes de terrain et interpréteur de scripts (P1)

**Travail**
- Porter les comportements de grille, altitudes, terrains spéciaux, transitions, interactions, événements de coordonnées, objets et PNJ.
- Représenter les commandes de script par un enum Rust exhaustif pour le périmètre pris en charge, avec validation du bytecode/paramètres.
- Mettre des traces de script (PC/offset, opcode, arguments, état, attente ou erreur) et un outil pour détecter les scripts non pris en charge.
- Réimplémenter chargement paresseux, files de tâches et invalidation des demandes obsolètes.

**Acceptation**
- Couverture des commandes nécessaire à une progression définie du jeu, calculée automatiquement.
- Test différentiel des séquences de script et des transitions.
- Chaque commande inconnue échoue explicitement sans corrompre l’état du monde.
- Les changements rapides de carte ne font apparaître ni assets obsolètes ni callbacks sur des entités détruites.

### Phase 5 — Moteur de combat (P1)

**Travail**
- Porter séparément le modèle de combat : ordre des tours, précision, dégâts, types, capacité, altérations d’état, effets, objets, changements, capture, expérience, évolution et fin de combat.
- Réutiliser les tables et scripts de données après validation de leur format et de leurs identifiants.
- Isoler le RNG ; fournir une graine dans les tests et des journaux de décision.
- Connecter ensuite le moteur pur aux animations, écrans, textes, sons et contrôles.

**Acceptation**
- Tests différentiels sur un corpus de combats contenant les cas normaux, doubles, effets de statut, changements de statistiques, capacités, objets, cas limites et événements aléatoires contrôlés.
- Égalité des résultats de règles pour les scénarios de référence ; chaque divergence est documentée.
- Aucun accès au renderer requis pour tester la résolution des tours.
- Scénarios de capture, victoire, défaite, fuite, expérience et évolution couverts.

### Phase 6 — Menus, progression, sauvegarde et audio (P1/P2)

**Travail**
- Porter équipe, sac, Pokédex, résumé Pokémon, menus, Pokétch et autres applications par ordre de dépendance gameplay.
- Définir un schéma de sauvegarde Rust versionné et des écritures atomiques (fichier temporaire, validation, remplacement).
- Décider explicitement si un importeur de sauvegarde DS est requis ; ne pas supposer que les structs internes C peuvent être sérialisées directement en Rust avec la même disposition.
- Étudier la conversion ou l’interprétation des séquences/banques SDAT et les commandes d’audio dynamiques. Séparer le backend audio de la logique qui demande un son.

**Acceptation**
- La progression principale peut être sauvegardée puis rechargée avec une validation des données.
- Les versions inconnues/corrompues déclenchent une récupération lisible au lieu d’une corruption silencieuse.
- Les tests valident les transitions musicales, boucles, fades et effets requis par la tranche couverte.
- Les sauvegardes d’origine, si exigées, ont leur propre corpus d’essai et un outil de diagnostic versionné.

### Phase 7 — Complétude, performance, fonctionnalités avancées (P2/P3)

**Travail**
- Compléter les applications restantes, toutes les cartes et les cas spéciaux.
- Mettre en place des profils de performance sur machine définie, chargements d’assets et budgets de mémoire.
- Définir le support des langues et la séparation des ressources de langue.
- Évaluer seulement alors le réseau/multijoueur et les périphériques non essentiels.

**Acceptation**
- Matrice de fonctionnalités reliée à des tests ou à une décision explicite de non-support.
- Pas de régression mesurable sur les scènes de référence au-delà du budget adopté.
- Sauvegarde, rechargement, retour au titre et parcours complet fonctionnent de façon répétée.
- Toutes les fonctionnalités exclues sont annoncées clairement.

### Phase 8 — Décommissionnement de l’ancien runtime (P3)

Ne supprimer le runtime C/libntr qu’après avoir démontré que le périmètre choisi est couvert, que les tests différentiels sont stables et que les outils d’import ne dépendent plus de l’exécutable C. Si le code historique reste juridiquement et techniquement conservable comme référence, l’isoler dans une branche ou un sous-projet documenté plutôt que d’en mélanger les conventions dans les crates Rust.

## 7. Stratégie de tests et de qualité

### 7.1 Tests unitaires et différentiels

- **Parsers :** bornes, tailles, endianess, offset relatif/absolu, padding, entrées tronquées et valeurs invalides.
- **Simulation :** mouvement sur grille, collisions, altitudes, ordre de script, déclenchement de rencontres et transitions.
- **Combat :** RNG contrôlé, actions, dégâts, calculs de statut, changements de statistiques, effets de fin de tour et cas limites.
- **Sauvegarde :** sérialisation, migrations de schéma, interruption au milieu d’une écriture et restauration.
- **Rendu :** captures automatiques des deux écrans, avec seuils adaptés aux différences de rendu plutôt qu’une comparaison aveugle pixel par pixel sur GPU hétérogènes.

Le runtime C existant doit servir d’oracle fonctionnel au début : donner les mêmes états initiaux et entrées, capturer les événements/résultats et comparer avec Rust. Une divergence doit devenir un cas de test, pas seulement un bug observé manuellement.

### 7.2 Déterminisme

Ajouter un mode test dans lequel :
- l’horloge et le tick sont contrôlés ;
- le RNG est seedé ;
- les événements de chargement asynchrones sont committés à des points définis ;
- les états importants peuvent être sérialisés dans des snapshots de debug ;
- les journaux utilisent des IDs stables, pas l’ordre accidentel des entités.

### 7.3 Observabilité

Prévoir des canaux distincts pour simulation, scripts, assets, rendu, audio et sauvegardes. Les erreurs doivent inclure le fichier/ID de ressource, l’offset lorsqu’il existe, la carte/état et le contexte. Ajouter une interface de diagnostic pour afficher la carte, les collisions, les déclencheurs, le script courant et les ressources chargées.

### 7.4 Critères globaux de sortie

- CI : formatage, clippy selon les règles du projet, tests unitaires, tests de parsers, test de lancement headless et build Linux.
- Corpus de non-régression versionné et taille contrôlée.
- Aucun panic attendu sur des ressources invalides et aucune donnée de sauvegarde perdue sans diagnostic.
- Les logs n’exposent pas de données privées ; les sauvegardes de test ne doivent pas contenir les données personnelles du joueur.
- Le build de référence et la révision des dépendances sont traçables.

## 8. Risques principaux et mitigations

| Risque | Niveau | Mitigation |
|---|---|---|
| Explosion de périmètre : tout le jeu, toutes les interfaces et fonctionnalités en une fois | Critique | Tranches verticales et critère de sortie par phase |
| Rendu DS incorrect si l’on se repose sur le renderer standard | Critique | Renderer 2D explicite, captures de référence et analyse des effets |
| Formats Nitro partiellement convertis (matériaux, animations, palettes, audio) | Critique | Inventaire de couverture et tests par type avant migration massive |
| Scripts portés de manière incomplète ou scènes codées en dur | Critique | Interpréteur de scripts et couverture mesurée des opcodes |
| Non-déterminisme lié au temps ou au chargement asynchrone | Élevé | Tick fixe, événements contrôlés, RNG seedé |
| Réécriture des combats avec régressions de règles | Critique | Moteur pur, corpus de cas et comparaison différentielle |
| Sauvegarde incompatible ou corrompue | Élevé | Schéma versionné, writes atomiques, import séparé, tests de restauration |
| Dépendances du build qui évoluent à distance | Élevé | Verrouillage des versions et commits, CI reproductible |
| Conflit entre architecture ECS et logique de gameplay historique | Élevé | Modèle de domaine séparé ; ECS pour l’orchestration et la présentation |
| Redistribuer accidentellement des données protégées | Critique | Import local depuis une source fournie par l’utilisateur, vérification des fichiers et politique de packaging |
| Multiplayer/WFC plus coûteux que prévu | Élevé | Hors MVP, interfaces de transport abstraites, étude séparée |
| Suppression prématurée du runtime fonctionnel | Élevé | Ne décommissionner qu’après la matrice de parité et un parcours de bout en bout |

## 9. Licences, provenance et distribution des ressources

La réécriture du moteur ne donne pas de droits supplémentaires sur les ressources, sons, modèles, textes ou autres éléments de Pokémon Platinum. L’état du fork et l’origine précise de chaque ressource doivent être audités avant toute distribution de binaire ou de paquet d’assets.

Recommandations :
- Ne jamais committer ni distribuer une ROM commerciale.
- Pour un pipeline d’extraction, demander un fichier ROM fourni localement par l’utilisateur et effectuer les contrôles nécessaires sans l’envoyer à un serveur.
- Ne pas distribuer les fichiers extraits, compilés ou convertis si leur redistribution n’est pas autorisée.
- Distribuer l’outil, le moteur et les métadonnées originales pouvant être légalement redistribuées, et documenter le processus d’installation de ressources séparées.
- Conserver les notices de licences des dépendances open source. Établir un inventaire SBOM et de provenance des bibliothèques et outils.

Une revue juridique du mode de distribution est requise avant de publier des exécutables ou des paquets contenant des ressources.

## 10. Structure de dépôt proposée

La structure proposée, à adapter avant de déplacer les répertoires existants :

- crates/platinum_app/
- crates/platinum_domain/
- crates/platinum_sim/
- crates/platinum_assets/
- crates/platinum_nitro/
- crates/platinum_field/
- crates/platinum_battle/
- crates/platinum_ui/
- crates/platinum_audio/
- crates/platinum_save/
- crates/platinum_render/
- crates/platinum_tools/
- assets/manifest/ (manifestes textuels et tests autorisés ; pas d’assets propriétaires ajoutés sans contrôle)
- tests/fixtures/ (échantillons minimaux et légalement redistribuables)
- docs/architecture/ (décisions ADR, formats internes, contrats de compatibilité, couverture de migration)

Garder les sources C et la chaîne existante dans leurs chemins actuels au début réduit le risque de casser la construction de référence. Les déplacements et suppressions doivent intervenir après stabilisation du pipeline Rust.

## 11. Ordre de priorité recommandé

**P0 — Conditions préalables**
- Geler la baseline, les dépendances et les références d’image/état.
- Créer le workspace et la coquille à deux écrans.
- Tester les premiers parseurs d’archives et le pipeline de ressources.

**P1 — Premier parcours jouable**
- Carte pilote, joueur, collisions, PNJ, script de dialogue, transitions.
- Moteur de script de terrain couvrant le parcours pilote.
- Combat sauvage minimum avec tests différentiels.

**P2 — Progression et complétude**
- Sauvegarde, menus, équipe/sac/Pokédex, audio et assets du périmètre principal.
- Couverture des cartes, scripts et cas de combat à partir d’une matrice mesurée.

**P3 — Nettoyage et fonctions avancées**
- Parité des applications restantes, optimisation, compatibilité de sauvegarde DS et réseau si explicitement requis.
- Décommissionnement de l’ancien runtime seulement après preuve de couverture.

## 12. Première tranche concrète à implémenter

La première PR ne devrait **pas** essayer de porter le jeu entier. Elle devrait livrer :

1. Un workspace Cargo compilable avec Bevy 0.20.0 épinglé et les instructions de build Linux.
2. Une fenêtre avec deux targets logiques 256 × 192, un composite configurable et un mapping souris correct.
3. Un crate platinum_nitro contenant un lecteur NARC minimal, avec tests valides/invalides.
4. Un outil de diagnostic capable de lister une archive et ses membres, sans encore charger tous les assets du jeu.
5. Une CI qui exécute tests et build de la coquille sur une machine propre.

Le résultat attendu est une base technique testée qui valide les choix de fenêtre, d’asset pipeline et d’architecture avant de construire les systèmes de terrain.

## 13. Références internes et externes

### Dépôt audité
- Révision de référence : https://github.com/rakmahefa/pokeplatinum/tree/pc_port
- Construction Meson : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/meson.build
- Options de construction : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/meson.options
- Boucle principale : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/main.c
- Système : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/system.c
- Terrain : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/field_system.c
- Chargement/rendu des cartes : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/overlay005/fieldmap.c
- Chargement de données de terrain : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/overlay005/land_data.c
- Objets de carte : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/map_object.c
- Combat : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/battle/battle_system.c
- Sauvegarde : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/src/savedata.c
- Documentation 2D : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/docs/2d_rendering.md
- Documentation 3D : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/docs/3d_rendering.md
- Formats de carte : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/docs/maps/file_format_specifications.md
- Chargement des cartes : https://github.com/rakmahefa/pokeplatinum/blob/pc_port/docs/maps/loading_maps.md

### Bevy
- Annonce et notes de version Bevy 0.20 : https://bevy.org/news/bevy-0-20/
- Dépôt et releases Bevy : https://github.com/bevyengine/bevy/releases
- Guide d’introduction à l’ECS : https://bevy.org/learn/quick-start/getting-started/ecs/

---

**Verdict final :** choisir Bevy 0.20 comme base d’application, mais construire explicitement les couches de compatibilité pour les données, le rendu et la simulation de Platinum. Le principal facteur de succès ne sera pas la vitesse de traduction C→Rust : ce sera la capacité à mesurer la parité, stabiliser le pipeline d’assets et migrer progressivement les systèmes pilotés par scripts sans perdre le comportement de jeu.
