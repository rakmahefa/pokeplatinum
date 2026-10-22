# Inventaire initial des formats et volumes du dépôt

> **Snapshot initial :** commit `445533d142aee68f87fdf0852b9f14ec00f7ca66`, généré par le workflow [preparation-checks, run 39724791913](https://github.com/rakmahefa/pokeplatinum/actions/runs/39724791913). Ce document résume une sortie automatisée, il ne remplace pas le JSON complet conservé comme artefact CI pendant 14 jours.

## Portée et limites

L'outil `tools/scripts/repo_inventory.py` a lu l'arbre Git commité, compté les blobs et demandé leurs tailles au serveur Git. Deux exécutions successives ont produit des JSON identiques.

- **27 712 blobs suivis**, soit **138 524 927 octets** de contenu de blob.
- **0 gitlink** et **0 lien symbolique** observés à cette révision.
- Les tailles représentent les objets blob Git ; elles n'incluent ni la surcharge des arbres Git, ni d'éventuels objets LFS décompressés, ni le contenu externe de sous-modules.
- L'inventaire ne lit pas les octets des ressources. Une extension identifie une famille probable, pas la spécification complète, le consommateur, la provenance ou l'autorisation de redistribution.
- Les fichiers de ce snapshot sont au commit indiqué ; après changement de la branche, regénérer l'artefact plutôt que copier ces chiffres comme s'ils étaient actuels.

## Volumes par répertoire de premier niveau

| Répertoire | Fichiers | Octets de blobs |
|---|---:|---:|
| `res/` | 24 163 | 107 430 964 |
| `src/` | 1 033 | 24 309 947 |
| `include/` | 1 986 | 3 115 042 |
| `tools/` | 236 | 2 078 743 |
| `lib/` | 75 | 405 058 |
| `generated/` | 108 | 338 126 |
| `docs/` | 27 | 217 863 |
| `platinum.us/` | 17 | 154 716 |
| `asm/` | 9 | 287 067 |
| Racine | 19 | 87 763 |
| `subprojects/` | 24 | 71 623 |
| `.github/` | 6 | 9 930 |
| `.vscode/` | 1 | 1 911 |
| `images/` | 1 | 14 161 |
| `meson/` | 7 | 2 013 |

Les ressources sont la plus grande part de l'arbre suivi. Elles ne doivent pas toutes être converties automatiquement : les ressources brutes, fichiers générés, ressources préconstruites, outils et formats propriétaires doivent être identifiés par usage.

## Extensions dominantes observées

Les nombres ci-dessous comptent les suffixes des chemins Git, sans interpréter le contenu des fichiers.

| Extension | Fichiers | Octets de blobs | Travail d'analyse |
|---|---:|---:|---|
| `.narc` | 115 | 28 937 472 | Confirmer structure des archives, consommateurs et mapping des membres ; le code comporte `src/narc.c`. |
| `.c` | 1 108 | 25 254 338 | Code source C à cartographier par système et cible PC/ARM. |
| `.bin` | 711 | 17 999 026 | Catégorie trop générale ; qualifier chaque famille par chemin et générateur. |
| `.json` | 6 623 | 17 676 591 | Distinguer données source, manifestes, métadonnées et sorties générées. |
| `.wav` | 874 | 10 770 636 | Relier les échantillons audio aux outils et au chemin de lecture. |
| `.sdat` | 1 | 7 484 768 | Archive sonore Nitro présumée ; confirmer lecteur et extraction. |
| `.png` | 4 755 | 4 469 908 | Images et outils associés ; distinguer source de travail et fichier de jeu. |
| `.s` | 2 843 | 4 155 527 | Code assembleur ; identifier l'assembleur et les cibles. |
| `.nsbtx` | 156 | 3 509 956 | Ressources de texture 3D ; confirmer format et importeur. |
| `.mid` | 967 | 2 743 441 | Ressources MIDI ; relier aux séquences et à la chaîne audio. |
| `.nsbmd` | 619 | 2 398 884 | Ressources modèles 3D ; consulter `docs/3d_rendering.md` et cartographier les consommateurs. |
| `.pal` | 1 983 | 1 827 258 | Palettes ; déterminer les générateurs, références et consommateurs. |
| `.spa` | 615 | 2 799 640 | Famille d'extension à identifier à partir des outils et des lecteurs avant toute conversion. |
| `.nscr` | 288 | 779 164 | Ressources d'écran/tilemap présumées ; confirmer leur usage exact dans le rendu 2D. |
| `.ncgr` | 44 | 105 776 | Graphiques de tuiles présumés ; rapprocher de `.nclr` et `.nscr`. |
| `.nclr` | 40 | 21 120 | Palettes Nitro présumées ; vérifier le pipeline. |
| `.ncer` | 10 | 9 693 | Cellules/objets 2D présumés ; vérifier les consommateurs. |
| `.nanr` | 11 | 2 288 | Ressources d'animation 2D présumées ; vérifier les consommateurs. |
| `.nsbca`, `.nsbta`, `.nsbtp`, `.nsbma` | 106 au total | 99 028 | Familles d'animation 3D présumées ; consolider la classification à partir des parseurs et fichiers producteurs. |

Le suffixe ne suffit pas à prouver un format. Les familles qualifiées « présumées » doivent être confirmées dans le code et la documentation avant de définir un parseur Rust.

## Dix plus gros blobs du snapshot

| Taille (octets) | Chemin |
|---:|---|
| 11 778 676 | `res/prebuilt/poketool/pokegra/pokegra.narc` |
| 7 484 768 | `res/prebuilt/data/sound/sound_data.sdat` |
| 2 695 184 | `res/prebuilt/msgdata/msg.narc` |
| 1 257 224 | `res/prebuilt/demo/title/op_demo.narc` |
| 953 056 | `res/prebuilt/arc/demo_tengan_gra.narc` |
| 929 852 | `res/prebuilt/data/utility.bin` |
| 929 852 | `res/prebuilt/dwc/utility.bin` |
| 890 604 | `res/prebuilt/poketool/pokegra/otherpoke.narc` |
| 852 772 | `res/prebuilt/battle/graphic/pl_batt_bg.narc` |
| 821 528 | `res/prebuilt/graphic/wifi2dchar.narc` |

## Prochaines étapes de l'inventaire

1. Lister les consommateurs et producteurs des familles NARC/Nitro/audio, en commençant par `src/narc.c`, le rendu 2D/3D et les outils de `tools/scripts/`.
2. Distinguer ressource préconstruite, source éditable, génération déterministe et sortie de build.
3. Compléter les exigences de provenance/licences par famille ; aucun contenu ne doit être re-distribué sur la seule base de son extension.
4. Régénérer ce résumé après revue, à partir d'un artefact et d'une SHA explicitement documentés ; ne pas modifier les nombres à la main sans rattacher le rapport source.
