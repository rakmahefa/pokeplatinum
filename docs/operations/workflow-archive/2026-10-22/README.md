# Workflows historiques archivés — 2026-10-22

Copies exactes des trois workflows auparavant actifs sous `.github/workflows/`.
Ces fichiers se trouvent volontairement sous `docs/` : GitHub Actions ne les traite pas comme des workflows actifs.

## Révision source

- Branche : `pc_port`
- HEAD source : `7cbf682c0a8ec8a6729baeb00fb98e596a0c739d`
- Motif : démarrer P-1 en concevant une CI adaptée au plan Rust + Bevy plutôt que de conserver inchangés les workflows historiques.
- Portée : sauvegarde ; ne pas réactiver les fichiers sans revue de leurs déclencheurs, permissions, dépendances et artefacts.

## Copies exactes

| Fichier d'origine | Copie d'archive | SHA du blob source |
|---|---|---|
| `.github/workflows/build_linux.yml` | `build_linux.yml` | `f69f65a781b096793f1525541d40f4b7d06a7342` |
| `.github/workflows/build_win.yml` | `build_win.yml` | `925de0767a5b56e48e4de3e7fbf2857c6b923c81` |
| `.github/workflows/build_arm.yml` | `build_arm.yml` | `0d7c4d61b9aaa15a0b95f3eccd0b74102d369dc5` |

Les SHA des blobs d'archive ont été comparées à celles des sources ; les contenus sont identiques. L'historique Git conserve aussi la révision source.

## État des runs observés avant retrait

- Linux : run [39722714025](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714025), conclusion `success`.
- ARM : run [39722714020](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714020), conclusion `success`.
- Windows : run [39722714273](https://github.com/rakmahefa/pokeplatinum/actions/runs/39722714273), indiqué `in_progress` au dernier relevé ; son résultat final n'est pas confirmé.

Ces statuts ne valident ni un build local froid et reproductible, ni les futurs workflows. Les runs déjà démarrés peuvent continuer après le retrait de leurs fichiers YAML.
