# Provenance des dépendances et des ressources — premier relevé

> **Statut :** relevé initial, non exhaustif ; il ne constitue pas une validation juridique. Sources examinées : `subprojects/*.wrap`, `subprojects/update.ini`, `.gitignore`, `.gitattributes` et les fichiers suivis dont le nom indique une licence.

## 1. Dépendances Meson déclarées

La révision examinée utilise neuf fichiers `.wrap` sous `subprojects/`. Le run [39725655227](https://github.com/rakmahefa/pokeplatinum/actions/runs/39725655227) a capturé les commits effectifs des checkouts Git présents ; six dépendances résolues sont épinglées dans ce lot. Le build suivant doit les valider.

| Fichier | Source / identifiant déclaré | Type | Risque / action |
|---|---|---|---|
| `libntr.wrap` | `https://github.com/cybervisi0n/libntr.git`, `revision = 1555d911ac80c0190ac1c321f99f1323de8b3c09` | Git SHA, profondeur 1 | Épinglé à la révision observée ; rebuild de validation requis. |
| `libntrdwc.wrap` | `https://github.com/cybervisi0n/libntrdwc.git`, `revision = 16246ba7b4269e6686f3e4da068e3c996a103739` | Git SHA, profondeur 1 | Épinglé à la révision observée ; rebuild de validation requis. |
| `libntrsystem.wrap` | `https://github.com/cybervisi0n/libntrsystem.git`, `revision = cd778c9d5e45869f8ecb8245b316ac20ea576958` | Git SHA, profondeur 1 | Épinglé à la révision observée ; rebuild de validation requis. |
| `libntrwifi.wrap` | `https://github.com/cybervisi0n/libntrwifi.git`, `revision = 067dabb137dfaf80b8ceeb3b3c4a7256bfabc3e0` | Git SHA, profondeur 1 | Épinglé à la révision observée ; rebuild de validation requis. |
| `libvct.wrap` | `https://github.com/cybervisi0n/libvct.git`, `revision = a34ad47fc0d7d964483c287759b704b3b1f3b967` | Git SHA, profondeur 1 | Épinglé à la révision observée ; rebuild de validation requis. |
| `metang.wrap` | `https://github.com/lhearachel/metang.git`, `revision = d616519ce37bc9ceef556969a1ca2dc64bf88390` | Git SHA, profondeur 1 | Épinglé à la révision observée ; rebuild de validation requis. |
| `tracy.wrap` | `https://github.com/cybervisi0n/tracy.git`, `revision = nx_support` | Git, branche/ref nommée | Pas une SHA explicite ; confirmer le commit utilisé. |
| `rapidjson.wrap` | Archive amont `v1.1.0`, SHA-256 source `bf7ced29704a1e696fbccf2a2b4ea068e7774fa37f6d7dd4039d0787f8bed98e` ; patch WrapDB `1.1.0-2`, SHA-256 `c1480d0ecef09dbaa4b4d85d86090205386fb2c7e87f4f158b20dbbda14c9afc` | Archive versionnée et hashée | Hachages déclarés dans le wrap ; confirmer licences de l'archive et des patches. |
| `yyjson.wrap` | Archive amont `0.12.0`, SHA-256 source `b16246f617b2a136c78d73e5e2647c6f1de1313e46678062985bdcf1f40bb75d` ; patch WrapDB `0.12.0-1`, SHA-256 `014582b328e13671dea64fcb49a795e70142360216a505212b8045134781b3b5` | Archive versionnée et hashée | Hachages déclarés dans le wrap ; confirmer licences de l'archive et des patches. |

`subprojects/update.ini` est épinglé sur les mêmes SHAs pour NitroDWC, NitroSDK, NitroSystem, NitroWiFi et libvct. Tracy (`nx_support`) reste la seule référence nommée de ce groupe ; son checkout n'a pas été détecté dans le run Linux et devra être épinglé avant d'utiliser cette cible.

Le répertoire `subprojects/.wraplock` est présent mais vide dans le run observé ; les checkouts sont ignorés par `.gitignore`. Le manifeste enrichi 39725655227 capture l'identifiant Docker, les hashes des définitions `.wrap` et les commits résolus. Les SHAs de six dépendances détectées ont été épinglées ; le build suivant doit confirmer la résolution de ces commits.

### Politique de verrouillage proposée

1. Lors d'un run de build accepté, relever chaque commit de sous-projet effectivement utilisé.
2. Valider les épingles SHA déjà appliquées avec un build propre ; examiner aussi la provenance et la licence de chaque dépendance.
3. Résoudre et épingler séparément Tracy lors d'un build qui utilise réellement cette dépendance.
4. Conserver les hashes déclarés des sources d'archives et patches ; une vérification de hash n'est pas, à elle seule, une preuve de licence ou de provenance.
5. Démontrer qu'un build sans cache reconstruit les mêmes dépendances. Les caches Meson/Cargo restent des accélérateurs, pas la source de vérité.

Ne pas prétendre que le build actuel est entièrement hermétique : il est **compilé avec succès**, mais les commits externes exacts du premier run ne sont pas consignés.

## 2. Fichiers de licence explicitement repérés

Une recherche des noms de fichiers `LICENSE`, `LICENCE`, `COPYING`, `COPYRIGHT` et `NOTICE` sur l'arbre suivi a donné quatre fichiers portant clairement un texte de licence et trois ressources de l'écran-titre dont le nom contient `copyright` (les images/palettes ne sont pas des fichiers de licence).

| Fichier repéré | En-tête / licence lisible | Observation prudente |
|---|---|---|
| `tools/nitrogfx/LICENSE` | Permission permissive de type MIT | Conserver le texte, notices et attribution avec les copies du logiciel correspondant. |
| `tools/nitrosfx/LICENSE` | GNU Lesser General Public License 2.1 (LGPL-2.1) | Vérifier la portée exacte et les conditions de distribution de l'outil concerné. |
| `tools/nitrobtx/LICENSE` | GNU General Public License 3.0 (GPL-3.0) | Vérifier la portée exacte et les conditions de distribution de l'outil concerné. |
| `tools/msgenc/LICENSE.pugixml.md` | MIT License, copyright Arseny Kapoulkine | Le nom indique la licence d'un composant pugixml ; ne pas la considérer automatiquement comme la licence de tout `msgenc`. |

La recherche a aussi trouvé `res/graphics/title_screen/copyright.NSCR`, `copyright.pal` et `copyright.png` : ce sont des ressources portant un nom associé à l'écran de copyright, et non des déclarations de licence. Le relevé par nom ne détecte pas toutes les notices en-tête, licences d'assets, contrats ou conditions de provenance. **Absence de fichier LICENSE identifié ne signifie pas autorisation de redistribution.**

## 3. Exclusions locales et normalisation Git déjà observées

- `.gitignore` exclut les répertoires de build tels que `build/`, `build_linux/`, `build_win64/`, les téléchargements et caches Meson (`subprojects/packagecache`, checkouts de sous-projets), les fichiers `baserom.*`, plusieurs dumps/objets générés, et les sauvegardes utilisateur (`*.dsv`, `*.sav`, savestates). Conserver ces exclusions ; ne pas ajouter une ROM ou une sauvegarde au dépôt ou aux artefacts CI.
- `.gitattributes` classe notamment `*.bin` comme binaire, impose LF à plusieurs types de source/docs, et des règles de fin de ligne CRLF à `/res/**/*.txt` et `*.pal`. Ces règles peuvent affecter les diff et checksums de fichiers convertis ; les respecter dans tout pipeline futur.
- L'inventaire Git mesure le contenu des blobs versionnés, pas l'usage des assets par le runtime ni la légalité de leur distribution. Les gros fichiers `res/prebuilt/*` demandent une analyse de provenance par famille avant d'être copiés ou repackagés.

## 4. Prochaines actions

1. Valider le build de confirmation après l'épinglage des SHAs et comparer ses dépendances effectives aux valeurs attendues.
2. Construire une matrice dépendance → origine → commit/version → licence → usage → redistribution permise/interdite/inconnue.
3. Examiner les licences amont et les notices des composants non couverts par les quatre fichiers recensés.
4. Définir les fixtures autorisées pour les tests Rust, sans extraire ni téléverser des ressources privées.
5. Mettre en place un contrôle automatisé qui signale une ref Git mutable, une licence inconnue et une notice manquante sans bloquer silencieusement le diagnostic.
