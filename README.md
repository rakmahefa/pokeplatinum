# Pokémon Platinum — préparation du runtime Rust + Bevy

Ce fork prépare une migration progressive du port PC de Pokémon Platinum vers une architecture **Rust + Bevy**, en conservant temporairement le runtime C comme référence de comparaison.

> **État actuel : phase P-1 (Préparation).** Le nouveau moteur Rust n'est pas encore implémenté. Ne pas considérer P0 comme commencé.

## Point d'entrée pour reprendre le travail

Si tu arrives dans ce dépôt avec seulement son URL, suis cet ordre :

1. **[SESSION_HANDOFF.md](SESSION_HANDOFF.md)** — état connu, décisions déjà prises, lots achevés, points ouverts et prochaines actions.
2. **[audit.md](audit.md)** — audit du code source, architecture cible et plan des phases P0–P3.
3. **[docs/architecture/PREPARATION.md](docs/architecture/PREPARATION.md)** — checklist détaillée P-1, livrables et conditions obligatoires avant P0.
4. **[Politique commits et CI](docs/operations/commit-and-ci-policy.md)** — comment regrouper plusieurs commits pour déclencher une seule mise à jour de branche, annuler les builds obsolètes et reprendre le HEAD en direct.
5. Les documents techniques historiques sous **[docs/](docs/)** pour comprendre le rendu DS, les formats de cartes et les ressources.

Toujours vérifier le HEAD réel de la branche `pc_port` sur GitHub avant de commencer. Les SHAs notées dans un handoff sont des repères historiques, pas une source d'état plus récente que le dépôt.

## Décisions d'architecture

- Les règles de gameplay et la simulation sont écrites en Rust pur et indépendantes de Bevy.
- Bevy fournit l'infrastructure du runtime, les schedules, fenêtres, entrées et les systèmes ECS là où ils sont utiles.
- Les particularités de la Nintendo DS sont prises en charge par des modules spécifiques : formats Nitro/NARC, rendu 2D en couches, import 3D et composition des deux écrans logiques.
- Le port C reste un oracle de comportement tant qu'il peut être construit et exécuté.
- Le périmètre réseau historique et l'import de sauvegarde DS sont des décisions séparées, pas des fonctions implicites de Bevy.

## État de l'automatisation

- Les anciens workflows Linux, Windows et ARM ont été copiés à l'identique dans `docs/operations/workflow-archive/2026-10-22/`, puis retirés de `.github/workflows/` pour commencer la refonte P-1. Ils ne doivent pas être réactivés sans revue.
- Les anciens workflows Linux, Windows et ARM sont archivés et ne sont pas actifs. Deux workflows de remplacement sont prévus pour cette phase : `preparation-checks.yml` vérifie la syntaxe et le déterminisme de l'inventaire ; `baseline-c-linux.yml` construit la référence C/Linux sans publier les exécutables, et conserve uniquement un manifeste SHA-256 de sorties.
- Le runbook initial de baseline C/Linux se trouve dans `docs/operations/c-baseline.md`. L'exécution locale froide et les preuves d'artefacts restent à enregistrer.
- `tools/scripts/repo_inventory.py` inventorie l'arbre Git versionné de façon déterministe. Le workflow `preparation-checks.yml` compare deux rapports identiques et téléverse le JSON de métadonnées (chemins, tailles, SHA des blobs, sans contenu de fichier) comme artefact conservé 14 jours.
- Les lots liés doivent toujours être publiés en une seule mise à jour de référence ; voir la politique commits/CI.
- Le workspace Rust `engine/`, `xtask` et les nouveaux workflows restent à créer pendant P-1.

## Première étape recommandée

Reprendre **P-1.1 — Baseline C/PC reproductible** avec le [runbook initial](docs/operations/c-baseline.md), puis exécuter et consigner le [premier inventaire Git](tools/scripts/repo_inventory.py) pour alimenter P-1.2. Ne déclarer aucun build ou test réussi sans l'avoir exécuté.

## Règle de travail

Petits changements cohérents, tests vérifiables, commits groupés avant publication, aucune ROM/sauvegarde personnelle/ressource propriétaire ajoutée aux commits ou aux artefacts CI, et handoff mis à jour à chaque session substantielle.
