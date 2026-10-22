# Pokémon Platinum — préparation du runtime Rust + Bevy

Ce fork prépare une migration progressive du port PC de Pokémon Platinum vers une architecture **Rust + Bevy**, en conservant temporairement le runtime C comme référence de comparaison.

> **État actuel : phase P-1 (Préparation).** Le nouveau moteur Rust n'est pas encore implémenté. Ne pas considérer P0 comme commencé.

## Point d'entrée pour reprendre le travail

Si tu arrives dans ce dépôt avec seulement son URL, suis cet ordre :

1. **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)** — état connu, décisions déjà prises, lots achevés et prochaines actions.
2. **[audit.md](audit.md)** — analyse source, architecture cible et phases P0–P3.
3. **[docs/architecture/PREPARATION.md](docs/architecture/PREPARATION.md)** — checklist P-1 et conditions de sortie avant P0.
4. **[Matrice fonctionnelle](docs/migration/feature-matrix.md)** — priorités provisoires, parcours proposé et preuves de parité attendues.
5. **[Baseline C/Linux](docs/operations/c-baseline.md)** et **[provenance/licences](docs/assets/provenance-and-licenses.md)** — état compilé, checksums, dépendances et risques connus.
6. **[Politique commits/CI](docs/operations/commit-and-ci-policy.md)** — grouper les commits pour une seule mise à jour de branche ; voir aussi la [conception des workflows et caches](docs/operations/ci-and-caching.md).
7. [ADR d'architecture](docs/architecture/decisions/README.md) — décisions acceptées et sujets ouverts.
8. Les documents techniques historiques sous **[docs/](docs/)** pour le rendu DS, les cartes et les ressources.
Toujours vérifier le HEAD réel de la branche `pc_port` sur GitHub avant de commencer. Les SHAs notées dans un handoff sont des repères historiques, pas une source d'état plus récente que le dépôt.

## Décisions d'architecture

- Les règles de gameplay et la simulation sont écrites en Rust pur et indépendantes de Bevy.
- Bevy fournit l'infrastructure du runtime, les schedules, fenêtres, entrées et les systèmes ECS là où ils sont utiles.
- Les particularités de la Nintendo DS sont prises en charge par des modules spécifiques : formats Nitro/NARC, rendu 2D en couches, import 3D et composition des deux écrans logiques.
- Le port C reste un oracle de comportement tant qu'il peut être construit et exécuté.
- Le périmètre réseau historique et l'import de sauvegarde DS sont des décisions séparées, pas des fonctions implicites de Bevy.

## État de l'automatisation

- Les anciens workflows Linux, Windows et ARM restent archivés à l'identique dans `docs/operations/workflow-archive/2026-10-22/`.
- Les deux workflows qui étaient actifs au début de cette remise à zéro ont été sauvegardés à l'identique dans `docs/operations/workflow-archive/current-active-2026-10-22/`, puis retirés de `.github/workflows/` dans une seule mise à jour de référence.
- La branche `backup/pc-port-before-workflow-reset-2026-10-22` conserve l'intégralité du dépôt au HEAD précédant cette modification (`b702c73`). Les copies d'archive distinctes facilitent aussi la revue et la réutilisation éventuelle de ces fichiers.
- **Aucun workflow GitHub Actions n'est actif sur `pc_port` à ce point de transition.** Les derniers résultats CI restent des preuves historiques limitées aux révisions qu'ils ont construites ; ils ne signifient pas qu'une CI fonctionne actuellement.
- La compilation C/Linux a précédemment réussi sur le commit `7a07925`, et le script `tools/scripts/repo_inventory.py` a produit deux rapports identiques en CI. La reproductibilité bit à bit du binaire, l'exécution locale et la parité runtime restent à vérifier.
- La suite est de concevoir et d'ajouter nos workflows spécialisés selon la [politique commits/CI](docs/operations/commit-and-ci-policy.md) et le [plan de workflows/caches](docs/operations/ci-and-caching.md), en gardant les builds lourds séparés des changements documentaires.
- Le workspace Rust `engine/`, `xtask`, le spike Bevy et la CI Rust restent à créer pendant P-1.

## Première étape recommandée

Continuer P-1.1 en reproduisant localement le [build C/Linux](docs/operations/c-baseline.md) et en lançant une première scène repère ; poursuivre P-1.2 avec le [rapport d'inventaire](docs/assets/format-inventory.md) et le [relevé de provenance/licences](docs/assets/provenance-and-licenses.md). Le build GitHub de référence est passé, mais la parité runtime n'est pas encore établie.

## Règle de travail

Petits changements cohérents, tests vérifiables, commits groupés avant publication, aucune ROM/sauvegarde personnelle/ressource propriétaire ajoutée aux commits ou aux artefacts CI, et handoff mis à jour à chaque session substantielle.
