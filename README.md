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
6. **[Politique commits/CI](docs/operations/commit-and-ci-policy.md)** — grouper les commits pour une seule mise à jour de branche et éviter les builds obsolètes.
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

- Les workflows historiques Linux, Windows et ARM sont archivés à l'identique dans `docs/operations/workflow-archive/2026-10-22/` et retirés de `.github/workflows/`.
- Deux workflows de préparation sont actifs : `preparation-checks.yml` vérifie la syntaxe et le déterminisme de l'inventaire, puis conserve un JSON de métadonnées ; `baseline-c-linux.yml` construit le port C/Linux et conserve les empreintes de sorties sans publier les exécutables.
- Le run [baseline-c-linux 39724681527](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724681527) a terminé avec succès sur `7a07925`. Le runbook consigne tailles et SHA-256 : [baseline C/Linux](docs/operations/c-baseline.md).
- `tools/scripts/repo_inventory.py` a été exécuté deux fois par CI avec des sorties identiques. Son premier snapshot et les extensions à confirmer sont documentés dans [l'inventaire des formats](docs/assets/format-inventory.md).
- L'audit de wrappers a identifié des références Git mutables (`main`, `nx_support`) et des notices de licence à vérifier ; voir [provenance et licences](docs/assets/provenance-and-licenses.md).
- Une matrice provisoire formalise les priorités et la preuve attendue avant de porter chaque système : [matrice fonctionnelle](docs/migration/feature-matrix.md).
- [ADR-0001](docs/architecture/decisions/ADR-0001-bevy-infrastructure-domain-pure-rust.md) formalise la séparation Rust pur/Bevy ; la version Bevy et la forme du workspace restent à valider par spike.
- Les lots liés doivent toujours être publiés en une seule mise à jour de référence ; voir la politique commits/CI.
- Le workspace Rust `engine/`, `xtask`, le spike Bevy et la CI Rust restent à créer pendant P-1.

## Première étape recommandée

Continuer P-1.1 en reproduisant localement le [build C/Linux](docs/operations/c-baseline.md) et en lançant une première scène repère ; poursuivre P-1.2 avec le [rapport d'inventaire](docs/assets/format-inventory.md) et le [relevé de provenance/licences](docs/assets/provenance-and-licenses.md). Le build GitHub de référence est passé, mais la parité runtime n'est pas encore établie.

## Règle de travail

Petits changements cohérents, tests vérifiables, commits groupés avant publication, aucune ROM/sauvegarde personnelle/ressource propriétaire ajoutée aux commits ou aux artefacts CI, et handoff mis à jour à chaque session substantielle.
