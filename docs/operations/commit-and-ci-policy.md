# Politique de commits, publication et CI

> **Statut :** politique de travail pour le fork  
> **Branche cible actuelle :** `pc_port`  
> **Portée :** éviter les compilations inutiles, garder des commits lisibles et pouvoir reprendre le travail depuis le dépôt seul.

## 1. Résumé opérationnel

Pour une série de changements liés, l'objectif est de publier **une seule mise à jour de référence** au lieu de pousser chaque commit séparément.

- **Développement local :** faire autant de commits cohérents que nécessaire sur une branche de travail, puis pousser la série en une seule fois.
- **Modifications par API GitHub / agent :** préparer tous les blobs et arbres, créer un ou plusieurs commits liés, puis déplacer la référence de branche une seule fois. Ne pas utiliser `create_file` ou `update_file` successivement sur la branche surveillée pour chaque fichier d'un même lot.
- **Sécurité CI :** les anciens workflows Linux/Windows/ARM sont archivés sous `docs/operations/workflow-archive/2026-10-22/`. Les deux workflows qui étaient actifs avant la remise à zéro sont archivés séparément sous `docs/operations/workflow-archive/current-active-2026-10-22/` et retirés de `.github/workflows/`.
- **Transition :** deux workflows de remplacement sont ajoutés dans .github/workflows/ dans ce lot : docs-inventory.yml et baseline-c-linux.yml. Leurs nouveaux runs doivent être confirmés après publication.
- **Étape suivante :** ajouter la validation PR Rust et les tests headless seulement quand engine/ et Cargo.lock existent ; les pipelines d'intégration, maintenance et profilage restent distincts. Voir docs/operations/ci-and-caching.md.
- **Documents :** les nouveaux contrôles devront vérifier les Markdown et les liens sans lancer inutilement les compilations du jeu.
- **Publication :** ne pas mélanger les tâches de publication avec les tâches de test et de compilation.

La politique est complémentaire à `SESSION_HANDOFF.md`, `audit.md` et `docs/architecture/PREPARATION.md`. L'archive est documentée dans `docs/operations/workflow-archive/2026-10-22/README.md`.

## 2. Pourquoi la concurrence seule ne suffit pas

GitHub Actions autorise normalement plusieurs exécutions simultanées. Une concurrence déclarée avec `cancel-in-progress: true` limite à une exécution active par groupe et remplace les exécutions en attente ; elle annule aussi l'exécution active lorsqu'une nouvelle arrive.

Cela protège contre une file de plusieurs builds obsolètes, mais chaque push déclenche quand même un événement. Si quatre poussées sont envoyées l'une après l'autre, des runners peuvent avoir commencé à travailler avant leur annulation. **Le regroupement des changements avant la publication est donc la première optimisation ; la concurrence est le filet de sécurité.**

Référence officielle : https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency

## 3. Procédure recommandée pour l'humain

### A. Un lot de travail normal

1. Créer une branche pour une tâche, par exemple `prep/ci-batching` ou `prep/asset-inventory`.
2. Effectuer plusieurs commits atomiques et lisibles pendant le travail.
3. Exécuter localement les contrôles les plus rapides.
4. Faire un seul push avec l'ensemble des commits.
5. Examiner le résultat de CI du dernier commit.
6. Ouvrir ou mettre à jour la PR ; ne fusionner qu'après les contrôles requis.

Exemple :

```bash
git switch -c prep/ci-batching
# modifier plusieurs fichiers
git add .github/workflows docs
git commit -m "ci: add stale-run cancellation"
# deuxième changement lié, si nécessaire
git add docs/operations/commit-and-ci-policy.md
git commit -m "docs: document batched commits"
# Un seul push pour l'ensemble des commits locaux
git push -u origin prep/ci-batching
```

Ne pas lancer `git push` après chaque commit dans une série de commits liés. Pour corriger une erreur détectée après le push, faire la correction puis pousser une seule fois.

### B. Lot de changements réalisé par un agent/API

Sur la branche observée par les workflows, suivre cette séquence :

1. Lire le HEAD et l'arbre actuels ; ne jamais présumer qu'une ancienne SHA est encore la tête.
2. Préparer un blob pour chaque fichier modifié avec l'API Git Data **`create_blob`**.
3. Créer un arbre avec **`create_tree`**, en indiquant `base_tree_sha` et les chemins/blob SHAs du lot.
4. Créer un commit via **`create_commit`**. Si plusieurs commits logiques sont utiles, répéter les étapes arbre/commit en utilisant l'arbre précédent comme base et le commit précédent comme parent.
5. **Appeler `update_ref` une seule fois**, en fournissant le HEAD initial comme `expected_sha`, `force: false` et la SHA du dernier commit.
6. Vérifier le nouveau HEAD, les chemins et l'état des workflows.

Le dépôt voit ainsi une seule mise à jour de référence pour le lot et devrait déclencher un seul événement push par workflow concerné. Cette procédure conserve les commits intermédiaires dans l'historique si une chaîne a été créée. En cas d'échec de l'expected SHA, relire la tête de branche et intégrer les changements récents au lieu de forcer la mise à jour.

**À éviter pour un lot multi-fichiers :** appeler `create_file` ou `update_file` successivement sur `pc_port`. Ces API modifient la référence à chaque opération et peuvent déclencher la CI à chaque fois.

Si la branche a changé entre la lecture initiale et la mise à jour, ne pas forcer le ref. Relire la branche, intégrer les changements et recommencer depuis le nouvel HEAD.

## 4. Politique de commits

Privilégier un commit par changement logique, avec des messages qui décrivent l'intention. Préfixes recommandés :

- `feat:` nouvelle capacité ;
- `fix:` correction ;
- `refactor:` changement interne sans modification fonctionnelle voulue ;
- `perf:` amélioration mesurée ;
- `test:` tests ou fixtures ;
- `build:` toolchain ou compilation ;
- `ci:` workflows et contrôles automatiques ;
- `docs:` documentation ;
- `chore:` maintenance sans impact fonctionnel direct.

Règles :
- Aucun commit ne doit mélanger une réécriture de masse et une correction indépendante.
- Ne pas inclure des assets extraits privés, ROM, sauvegardes personnelles, caches, artefacts de build ou secrets.
- Pour chaque changement de génération, inclure un moyen de vérifier que la sortie est déterministe.
- Ne pas déclarer un test réussi s'il n'a pas été exécuté.
- Utiliser des branches de travail et des PR pour les lots de code importants. Ne pas effectuer de force-push sur la branche cible.
- Faire une seule mise à jour de référence par lot, sans sacrifier la lisibilité de l'historique.

## 5. État courant des workflows

Deux workflows de remplacement sont maintenant présents sous .github/workflows/ :

- **docs-inventory.yml** : les changements Markdown, documentation, scripts d'outillage et son propre fichier YAML déclenchent un contrôle de syntaxe Python, deux générations identiques de l'inventaire et une validation de schéma. Le rapport JSON ne contient que des métadonnées et sa rétention est de 14 jours.
- **baseline-c-linux.yml** : les changements de code C, ressources, générateurs et configuration de build pertinents déclenchent la compilation Linux ; un lancement manuel est aussi possible. Le résumé et l'artefact contiennent les révisions, dépendances, tailles et SHA-256, pas les exécutables.

Les deux workflows déclarent permissions contents: read, épinglent les actions externes à des SHA complets, ont des filtres de chemins distincts et une concurrence qui annule les validations obsolètes pour la même branche/PR. Les changements uniquement documentaires ne déclenchent donc pas le build C/Linux. Les modifications de la définition du build le déclenchent volontairement pour le vérifier sur une compilation réelle.

Les conclusions des nouveaux runs restent à confirmer sur le commit qui introduit ces fichiers. Le succès d'un ancien build sur 7a07925 et les anciens contrôles d'inventaire sont des preuves historiques, pas les résultats des nouveaux workflows.

Les définitions historiques Linux/Windows/ARM restent dans docs/operations/workflow-archive/2026-10-22/. Les anciennes versions des deux workflows de préparation sont conservées séparément dans docs/operations/workflow-archive/current-active-2026-10-22/. La branche backup/pc-port-before-workflow-reset-2026-10-22 conserve l'état complet antérieur.

La CI Rust PR, les tests d'intégration/headless, les contrôles de dépendances planifiés et le profilage manuel restent à ajouter quand les cibles et commandes correspondantes existent. Les archives ne doivent pas être réactivées telles quelles.
## 6. Politique de regroupement et moment où exécuter la CI

| Type de changement | Quand vérifier | Doit compiler le jeu ? |
|---|---|---|
| Rust, Cargo, build/configuration moteur | CI PR rapide à chaque nouvelle tête publiée | Oui, après le squelette Rust |
| Parseurs, manifests, convertisseurs d'assets | Tests parser/assets + vérification de génération | Seulement si le build concerné le requiert |
| Documentation uniquement | Workflow docs dédié, sans jobs GPU/build historiques | Non |
| Workflows, scripts de CI ou outil de build | Validation de workflow + build ciblé après regroupement | Oui, selon l'impact |
| Mesure de performance | Workflow manuel sur machine/runner fixé | Oui, benchmark uniquement |
| Série de commits liée | Un push / une mise à jour de ref après la série | Une fois par workflow et par référence |
| Pushs successifs malgré tout | Annulation des exécutions obsolètes via concurrency | Le dernier résultat est prioritaire |

Ne pas utiliser de délais artificiels ou de sleep pour « attendre que les commits arrivent » : c'est fragile et rend la CI moins prévisible. Le lot doit être groupé avant publication ; la concurrence gère les pushs successifs qui restent inévitables.

## 7. Reprise automatique en nouvelle session

Pour reprendre uniquement avec l'URL du dépôt :

1. Lire la tête actuelle de `pc_port` via GitHub ; le HEAD écrit dans un handoff peut être ancien dès qu'un nouveau commit existe.
2. Lire `SESSION_HANDOFF.md` pour le contexte, les décisions et les prochaines actions.
3. Lire `audit.md` pour la stratégie globale et `docs/architecture/PREPARATION.md` pour l'état et les critères de P-1.
4. Vérifier l'état courant des workflows et des fichiers — le handoff n'est pas une preuve que du code ou des tests ont été exécutés.
5. Mettre à jour le handoff dans le même lot que les changements associés, et toujours signaler clairement ce qui est fait, en cours et non vérifié.

Cette routine est une convention de dépôt, pas une mémoire magique : les décisions qui changent doivent être écrites ici ou dans un ADR afin qu'une session neuve puisse les reconstruire depuis l'historique du fork.

## 8. Vérification et évolution de cette politique

Après plusieurs lots, relever :
- combien d'événements CI sont générés par lot ;
- combien d'exécutions sont annulées ;
- temps et minutes runner économisés ;
- taux de cache, temps de build à froid et à chaud ;
- taux de succès des workflows de validation rapides ;
- fausses annulations ou besoin de garder une exécution historique.

Si des workflows de release ou de déploiement sont ajoutés, ne pas leur appliquer aveuglément `cancel-in-progress: true` : il faudra une politique de sérialisation sans annulation pour les étapes qui effectuent une publication réelle.
