# Architecture de CI et de cache — préparation P-1

> **État au 2026-10-22 :** les workflows docs-inventory.yml et baseline-c-linux.yml viennent d'être ajoutés. docs-inventory.yml a réussi sur le commit 3d9b0b8. Le build C/Linux a révélé une erreur de quoting dans la vérification de la SHA Meson du Makefile ; un correctif est soumis dans le lot suivant et doit être vérifié par un nouveau run. Les autres pipelines ci-dessous restent des cibles de conception.

## 1. Objectifs

1. Pouvoir reprendre le projet depuis son URL et ce dépôt : la source de vérité est le HEAD de `pc_port`, puis `SESSION_HANDOFF.md` et les documents liés.
2. Publier un lot logique avec une seule mise à jour de la référence afin que GitHub Actions reçoive un seul événement de push pour ce lot.
3. Ne jamais compiler le port C à cause d'une modification documentaire sans lien avec le build.
4. Séparer les validations rapides des compilations de référence, tests d'intégration et benchmarks.
5. Garder les permissions minimales et exclure ROM, sauvegardes personnelles, ressources propriétaires non redistribuables, clés et données locales des logs/artifacts.

## 2. Règle principale : grouper avant de publier

Un push contenant quatre commits entraîne un seul événement push et donc, au plus, une exécution de chaque workflow correspondant à cet événement. Quatre pushes distincts peuvent en revanche déclencher quatre exécutions ; la concurrence n'évite pas nécessairement qu'un runner ait déjà commencé à consommer des ressources avant l'annulation.

### Pour un agent ou une session qui utilise l'API GitHub

- Lire le HEAD de `pc_port` immédiatement avant toute écriture et conserver sa SHA comme expected head.
- Créer tous les blobs du lot puis l'arbre à partir de l'arbre de base.
- Créer une chaîne de commits logique si plusieurs étapes historiques sont utiles.
- Mettre à jour `pc_port` une seule fois avec `expected_sha`, `force: false`, vers le commit final.
- En cas de rejet de la mise à jour, relire le HEAD et intégrer les changements concurrents ; ne pas forcer.
- Pour ce lot d'archivage, la sauvegarde complète est la branche `backup/pc-port-before-workflow-reset-2026-10-22`.

### Pour un checkout local

Effectuer les commits séparés et lisibles nécessaires, exécuter les contrôles rapides en local, puis pousser la série une seule fois. Éviter de pousser après chaque commit lié.

## 3. Pipelines cibles

| Pipeline proposé | Déclenchement souhaité | Travaux | Compiler le jeu ? |
|---|---|---|---|
| `docs-inventory.yml` | Markdown, `docs/**`, `tools/scripts/**` et son YAML ; PR/push ciblés | Syntaxe Python, génération en double, comparaison octet par octet et validation du schéma de l'inventaire | Non |
| `baseline-c-linux.yml` | Changements C/build strictement pertinents sur `pc_port`, plus `workflow_dispatch` | Build Linux de référence, capture des dépendances, manifeste SHA-256 uniquement | Oui, uniquement quand le périmètre C/build l'exige |
| `rust-pr.yml` | Changements sous `engine/**`, fichiers Rust/Cargo/toolchain, config de CI ; PR/push pertinents | `cargo fmt --check`, lint, tests rapides, fixtures synthétiques et build minimal | Oui, après création du workspace |
| `rust-integration.yml` | PR importante, merge queue si activée, ou déclenchement manuel | Tests headless, parsers/assets, génération déterministe, intégration | Oui |
| `rust-nightly.yml` | Planifié et manuel | Advisories/licences, contrôles de docs, rapport de tendances de compilation/cache ; benchmarks non bloquants au départ | Oui selon la tâche |
| `rust-profile.yml` | Manuel sur runner/matériel identifié | Profilage et résultats JSON comparables | Oui, benchmark dédié |
| `release.yml` | À concevoir plus tard, déclenchement versionné et explicite | Packaging autorisé et signatures si prévues | Oui ; jamais partagé avec les jobs de test privilégiés |

docs-inventory.yml et baseline-c-linux.yml sont présents dans .github/workflows/ ; leurs déclencheurs et commandes sont définis. Les autres noms du tableau sont des cibles de conception, pas des workflows implémentés. La mise en service des deux premiers ne sera confirmée qu'après vérification de leurs runs sur le commit qui les introduit.

## 4. Déclencheurs, filtres et concurrence

- Toute définition de workflow doit expliciter les branches, événements et chemins. Des changements `*.md` ne doivent pas démarrer un build C ni un build Rust.
- Utiliser un groupe de concurrence par nom de workflow et référence/PR, par exemple `${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}`.
- Pour les validations, `cancel-in-progress: true` supprime du travail devenu obsolète lorsqu'une nouvelle tête arrive. C'est un filet de sécurité, pas un substitut au batching.
- Un workflow de profilage manuel peut annuler un ancien profilage de la même branche s'il est explicitement relançable.
- Ne pas employer cette annulation sans réflexion pour des opérations de publication ou release : sérialiser celles-ci et ne pas annuler une publication déjà engagée.
- Les modifications des workflows eux-mêmes doivent déclencher au moins leur validation syntaxique et un test pertinent, sans lancer automatiquement tous les builds lourds.

## 5. Permissions, dépendances et artefacts

- Définir `permissions: contents: read` au niveau minimal utile pour les jobs de validation ; ne pas donner d'écriture à la CI PR.
- Épingler chaque action externe à un SHA complet vérifié, avec le tag indiqué seulement en commentaire.
- Ne jamais exposer de secrets aux contributions non fiables.
- Les artefacts par défaut se limitent aux rapports textuels, manifestes, checksums et mesures nécessaires à la revue ; pas d'exécutables ou assets propriétaires par défaut.
- N'envoyer ni ROM, sauvegardes personnelles, répertoires extraits, fichiers sensibles, chemins privés ou dump de mémoire dans les artefacts ou logs.
- Contrôler la taille, le type et les chemins d'un artifact avant son upload ; appliquer une rétention raisonnable.
- La réussite d'un run doit être liée à la SHA réellement construite et apparaître dans son résumé.

## 6. Cache

### Cargo

- Ne mettre en place le cache Cargo qu'après choix du toolchain et création de `Cargo.lock`.
- Clés au minimum sur OS, version de Rust, `Cargo.lock` et les options/features qui changent les artefacts.
- Traiter un cache miss comme une condition normale ; le build doit rester possible sans cache.
- Mesurer d'abord les temps à froid et à chaud avant d'ajouter `sccache` ou plusieurs couches de cache qui se recouvrent.

### Ressources et génération

- Clé de contenu : hash source + version parser + schéma intermédiaire + options de conversion.
- Valider chaque sortie et la remplacer atomiquement ; les caches ne sont jamais la source de vérité.
- Conserver les fixtures synthétiques et redistribuables dans Git ; garder localement les ressources dont la provenance ou la redistribution n'est pas autorisée.

## 7. Critères de mise en service

Un workflow n'est réputé opérationnel qu'après :
- validation de la syntaxe YAML ;
- revue des déclencheurs/filtres, permissions et groupe de concurrence ;
- vérification que les artefacts et journaux n'embarquent aucune donnée interdite ;
- exécution réussie sur la révision attendue et lien vers le run enregistré dans le handoff ;
- confirmation qu'un lot multi-commits publié en un push génère un run correspondant par workflow, et qu'une mise à jour de la même branche annule bien les validations obsolètes comme prévu.

## 8. Décision de transition

Les deux premiers workflows de remplacement (docs-inventory.yml et baseline-c-linux.yml) ont été ajoutés en un seul lot avec leurs mises à jour documentaires. docs-inventory.yml est vert sur son premier commit. Le succès de baseline-c-linux doit être confirmé après la correction du test de SHA Meson dans le Makefile. La branche de sauvegarde et les archives fournissent un retour arrière ; la prochaine étape est d'ajouter la CI Rust après création du workspace.
