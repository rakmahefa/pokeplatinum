# Matrice initiale des fonctionnalités et de la parité

> **Statut : brouillon de cadrage issu de `audit.md`, pas encore un contrat produit approuvé.** Aucun système Rust de gameplay n'est implémenté à ce stade. Il faut choisir et tester un parcours vertical sur des ressources réellement disponibles, sans code dupliqué en dur ni asset de provenance inconnue.

## 1. État global constaté

| Élément | État vérifié | Conséquence |
|---|---|---|
| Référence C/Linux | Build CI réussi sur `7a07925f620e327e2126d2af931785ed35a563a8` ; quatre sorties et empreintes dans [le runbook](../operations/c-baseline.md). | La compilation est une base ; le lancement local et les captures de scènes restent ouverts. |
| Inventaire de l'arbre Git | Outil exécuté deux fois en CI avec JSON identiques ; snapshot dans [l'inventaire](../assets/format-inventory.md). | Les volumes sont connus ; les formats, producteurs/consommateurs et droits de ressources restent à analyser. |
| Dépendances externes | Premier relevé dans [le registre de provenance](../assets/provenance-and-licenses.md) ; plusieurs refs Git sont mutables. | La reproductibilité doit être renforcée avant d'utiliser le build comme oracle strict. |
| Runtime Rust/Bevy | Aucun workspace moteur Rust validé. | Ne pas marquer une fonction « portée » ou « testée » côté Rust. |

Les statuts à employer dans cette matrice sont : **inconnu**, **inventorié**, **prototypé**, **testé**, **porté**, **comparé**, **accepté**. « Implémenté » sans test associé ne suffit pas pour « testé ».

## 2. Matrice fonctionnelle provisoire

| Domaine / identifiant | Sources C et documentation à comparer | Priorité provisoire | Preuve d'acceptation côté Rust | Statut |
|---|---|---|---|---|
| `BOOT-001` — démarrage et cycle de vie de l'application | `src/main.c`, `src/system.c`, boucle principale, tâches et transitions | P0 — coquille | L'application démarre/ferme proprement ; les états/erreurs sont explicites ; cycle de vie testable headless. | Inventaire C existant ; Rust non commencé |
| `SCREEN-001` — composition des deux écrans | `docs/2d_rendering.md`, architecture PC, affichage de fenêtres/sprites | P0 — coquille | Deux surfaces logiques de 256 × 192, captures séparées et composition configurable (verticale/côte à côte) ; redimensionnement sans décaler les coordonnées logiques. | Inventaire documentaire ; Rust non commencé |
| `INPUT-001` — clavier/manette/pointeur | Entrées de terrain, `src/overlay005/field_control.c`, position du pointeur DS | P0 — coquille/parcours | Mapping reproductible sur la bonne surface ; test de coordonnées après changements d'échelle/agencement ; séquence d'entrées enregistrée par tick. | À détailler dans le corpus |
| `ASSET-001` — lecteur NARC et résolution d'identifiants | `src/narc.c`, archives et tables de correspondance IDs/chemins | P0 — outils d'assets | Tests sur archives synthétiques valides, tronquées et incohérentes ; membres listés de façon déterministe ; erreurs localisées. | Volumes inventoriés ; format/IDs à analyser |
| `MAP-001` — chargement d'une carte pilote | `src/overlay005/fieldmap.c`, `land_data.c`, `loaded_map_buffers.c`, `docs/maps/loading_maps.md` | P0 — parcours vertical | Carte choisie avec liste d'IDs/ressources ; chargement/déchargement répétés sans fuite ; données validées avant utilisation. | À choisir après revue des ressources et de leur provenance |
| `RENDER-001` — rendu 2D en couches et 3D nécessaire à la carte pilote | `src/easy3d.c`, `src/easy3d_object.c`, `docs/2d_rendering.md`, `docs/3d_rendering.md` | P0 — tranche minimale | Priorités, palettes, alignement des tuiles et géométrie 3D documentés ; comparaison d'images expliquée sur la scène choisie. | Inventaire documentaire ; non porté |
| `MOVE-001` — mouvement, altitude et collisions | `src/map_object.c`, `src/map_object_move.c`, données de collision BDHC | P0 — parcours vertical | Sur un corpus d'entrées fixé par tick, destination, obstacle, occupation et événements de collision correspondent à la référence C. | Non testé à ce stade |
| `SCRIPT-001` — PNJ, dialogue et script de terrain réel | `src/field_system.c`, `src/overlay005/field_control.c`, gestionnaire `scr_seq` et commandes générées | P0 — parcours vertical | Dialogue piloté par un script réel ou fixture autorisée ; trace des commandes et changements d'état ; pas de narration codée en dur pour simuler la progression. | Format/commandes à inventorier |
| `STATE-001` — transition/warp et cycle de vie de la carte | `src/overlay_manager.c`, `src/field_system.c`, données de transition | P0 — parcours vertical | Déclenchement, sortie et entrée de carte et nettoyage reproductibles ; pas d'entités/assets résiduels après répétition. | Non porté |
| `BATTLE-001` — combat solo déterministe | `src/battle/battle_system.c`, `src/battle/battle_main.c`, scripts de combat | P1 | Tests différentiels des séquences/actions/effets et RNG fixé ; état explicite, indépendant du framerate. | Hors tranche initiale |
| `PROGRESS-001` — menus, inventaire, équipe, Pokédex et progression | Overlays/UI, tables de progression et données correspondantes | P2 après terrain jouable | Parcours déclarés par système et comparaison métier sur fixtures/scénarios. | Non commencé |
| `SAVE-001` — modèle et sérialisation de sauvegarde | `src/savedata.c`, `src/savedata/save_table.c` | P2 ; import DS à décider séparément | Sauvegarde/chargement stables, atomiques et testés sur fixtures ; import/migration comme contrat distinct. | Non commencé ; compatibilité binaire à décider |
| `AUDIO-001` — musiques, effets et événements | `src/sound_system.c`, SDAT et tables audio | P2 | Reproduction d'un événement par identifiant/tick sur périmètre déclaré ; moteur audio séparé de la logique. | Formats/producteurs à qualifier |
| `NET-001` — WFC, échange/combat réseau | Composants DWC/Wi-Fi et fonctions réseau héritées | Hors MVP proposé | ADR spécifique, protocole et contraintes juridiques/opérationnelles définis avant implémentation. | Hors périmètre initial proposé |
| `DS-001` — import sauvegarde DS, périphériques, glitches matériels | Couche de compatibilité et comportements matériels historiques | Décision séparée | Critère explicite par capacité ; ne pas promettre une émulation bit à bit du matériel. | À décider dans le contrat de parité |

## 3. Parcours vertical proposé

La proposition initiale est : démarrage → deux écrans → une carte → déplacement et collision → interaction PNJ/dialogue pilotée par un script réel → transition/warp. Le choix d'une carte et de ses IDs n'est **pas encore arrêté** : il dépend de la disponibilité des ressources, de la compréhension des formats et de leur provenance.

Pour chaque scénario accepté, conserver la SHA de la révision C et l'environnement de build ; l'état de départ ; une séquence d'entrée horodatée par tick ; les événements/métadonnées métier attendus ; les identifiants des cartes/ressources/scripts et les dépendances ; les captures autorisées des deux écrans ; les méthodes de comparaison et les écarts PC acceptés.

Aucun corpus ne doit embarquer ROM, sauvegarde personnelle ou asset non redistribuable. Les tests CI utiliseront des fixtures synthétiques ; les essais qui exigent les données locales seront séparés.

## 4. Questions à résoudre avant de figer P0

1. Quelle carte pilote dispose de tous les fichiers nécessaires et d'une provenance acceptable ?
2. Quel niveau de comparaison visuelle est requis : pixel-identique ou équivalent adapté au PC ?
3. Quels IDs, formats et commandes de script minimaux couvrent la carte/PNJ/transition ?
4. Quels événements métier seront comparés au runtime C et quels écarts sont acceptables ?
5. Quelle version exacte de Rust/Bevy est validée par un spike technique, sans la figer seulement sur recommandation ?

La matrice sera mise à jour à chaque décision/validation ; les lignes « à décider » ne deviennent pas implicitement acceptées faute de temps.
