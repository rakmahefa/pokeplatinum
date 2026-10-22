# Workflows actifs avant la remise à zéro — 2026-10-22

Ces deux fichiers sont des copies exactes des définitions présentes sous `.github/workflows/` juste avant le lot de remise à zéro CI. Ils sont archivés sous `docs/` et ne sont pas interprétés comme des workflows GitHub Actions.

## Révision source

- Dépôt : `rakmahefa/pokeplatinum`
- Branche source : `pc_port`
- HEAD source : `b702c73c6a2f172bd6e86363e319ec0507e81222`
- Branche de sauvegarde complète : `backup/pc-port-before-workflow-reset-2026-10-22`
- Motif : permettre de concevoir une nouvelle CI pendant P-1 sans perdre les workflows de préparation précédents.
- Périmètre : les deux workflows actifs seulement ; l'archive des workflows historiques Linux/Windows/ARM se trouve séparément sous `docs/operations/workflow-archive/2026-10-22/`.

## Manifeste des copies

| Fichier source | Copie d'archive | SHA-1 du blob source |
|---|---|---|
| `.github/workflows/baseline-c-linux.yml` | `baseline-c-linux.yml` | `a11ed3d1c0670e0275abac5b28125326165358e3` |
| `.github/workflows/preparation-checks.yml` | `preparation-checks.yml` | `a21ebcdc37bfd00be052e45e61edf739676f0bf9` |

Les fichiers d'archive sont créés à partir du contenu lu sur le HEAD source ci-dessus. Après l'ajout, le SHA Git du blob de chaque copie doit être comparé au SHA source indiqué ici ; une correspondance signifie que le contenu est identique octet pour octet.

## État après la suppression

Les deux chemins sources sont retirés de `.github/workflows/` sur `pc_port` par un seul commit. Aucune CI active n'est conservée durant cette transition. Les réussites de runs passés sont seulement des éléments de preuve pour les révisions qu'ils ont construites et ne valident pas les futurs workflows.

Ne pas copier de nouveau ces fichiers sous `.github/workflows/` sans revoir leurs déclencheurs, permissions, filtres de chemins, concurrence, dépendances et artefacts.
