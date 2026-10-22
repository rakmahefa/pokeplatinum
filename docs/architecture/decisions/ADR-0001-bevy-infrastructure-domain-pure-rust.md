# ADR-0001 — Bevy comme infrastructure, domaine en Rust pur

- **Statut : accepté**
- **Date : 2026-10-22**
- **Périmètre :** architecture du runtime de remplacement ; cette décision ne fige ni la version exacte de Bevy, ni le renderer, ni les formats d'assets.

## Contexte

Le port PC C existant associe gameplay, services inspirés du SDK Nintendo DS, données/scripts générés et particularités de rendu. Une traduction mécanique C→Rust ou une dépendance directe de toutes les règles métier aux composants ECS rendrait les tests différentiels, le déterminisme et la migration progressive difficiles.

Le projet a retenu Rust + Bevy comme direction. Cette ADR formalise cette limite et ne signifie pas que le workspace Rust est déjà implémenté.

## Décision

1. **Rust pur pour le domaine.** Les modèles et règles de combat, scripts, état du monde, mouvement/collision, progression, RNG et logique de sauvegarde vivent dans des crates qui n'ont pas besoin de dépendre de Bevy.
2. **Bevy pour l'infrastructure runtime.** Utiliser Bevy pour l'application, la fenêtre, les entrées, les schedules, le cycle de vie des systèmes, les assets et l'ECS lorsque celle-ci simplifie réellement le système.
3. **Frontière explicite.** Les composants/ressources Bevy adaptent les entrées et états du domaine ; ils ne deviennent pas la source de vérité des règles métier. Les données de gameplay ne doivent pas dépendre de l'heure murale, du framerate, d'un backend graphique ou d'un type de rendu.
4. **Compatibilité DS spécialisée.** Les archives Nitro/NARC, les formats de ressources, le rendu 2D en couches/palettes/priorités, l'import 3D et la composition de deux surfaces logiques font l'objet de modules dédiés. On n'assume pas que les sprites ou l'AssetServer standards reproduisent automatiquement leur sémantique.
5. **Oracle C conservé.** Le runtime C reste la référence de comparaison tant que la cible compile et peut être exécutée. Le chemin C/Meson n'est pas supprimé pendant cette architecture de transition.

## Conséquences positives

- Les règles du domaine peuvent être testées en Rust sans fenêtre, GPU, asset commercial ou World Bevy.
- Des tests déterministes peuvent comparer l'état métier C/Rust en isolant le rendu et le backend d'entrée.
- Le renderer et le pipeline Nitro restent remplaçables sans réécrire le gameplay.
- La migration peut livrer une tranche verticale et conserver l'ancien runtime jusqu'à une preuve de parité suffisante.

## Coûts et contraintes acceptés

- Une frontière domaine/Bevy ajoute des adaptateurs explicites.
- Il faut décider quels objets sont des données de domaine et lesquels sont des entités de présentation ; éviter de générer systématiquement des composants pour chaque struct.
- Le modèle de temps, l'ordre des systèmes, la gestion RNG, les erreurs de chargement et les identifiants d'assets doivent être décrits dans des ADR/tests séparés.
- Le rendu DS demande du travail spécifique et ne peut pas être considéré comme terminé par la seule ouverture d'une fenêtre Bevy.

## Non décidé par cette ADR

- Version définitive de Bevy et ensemble de features : à sélectionner après un spike reproductible et un contrôle de compatibilité des APIs.
- Backend de rendu exact, architecture des deux targets de 256 × 192, gestion des shaders et stratégie de captures : ADR séparées.
- Schéma exact du workspace Cargo et découpage complet des crates : ADR-0002.
- Cadence/tick simulation et RNG : ADR séparée à valider par des tests différentiels.
- Import des sauvegardes DS, fonctionnalités Wi-Fi et parité des glitches matériels : décisions de périmètre distinctes.

## Validation attendue avant le premier code de gameplay

- Un crate de domaine compile/teste sans dépendance Bevy.
- Une coquille Bevy démarre avec une fenêtre et une journalisation contrôlée sans ROM/asset de jeu.
- Un test démontre que le résultat métier d'un scénario synthétique ne dépend pas du nombre d'images rendues.
- Le premier spike note la version Bevy exacte, les features activées, la plateforme, les commandes et le résultat.

## Références

- [Audit technique](../../../audit.md)
- [Plan de préparation P-1](../PREPARATION.md)
- [Matrice fonctionnelle provisoire](../../migration/feature-matrix.md)
