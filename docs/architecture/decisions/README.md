# Décisions d'architecture

Les ADR consignent les décisions qui affectent durablement le runtime Rust + Bevy. Une décision doit préciser son statut, contexte, alternatives, conséquences et critères de validation. Une ADR acceptée n'affirme pas que son implémentation est déjà terminée.

| ADR | Sujet | Statut |
|---|---|---|
| [ADR-0001](ADR-0001-bevy-infrastructure-domain-pure-rust.md) | Bevy comme infrastructure ; domaine en Rust pur | Accepté |
| ADR-0002 | Frontières du workspace et responsabilités des crates | À rédiger |
| ADR-0003 | Tick de simulation, ordre d'exécution et déterminisme RNG | À rédiger |
| ADR-0004 | Deux surfaces logiques, mapping de coordonnées et captures | À rédiger |
| ADR-0005 | Pipeline Nitro/NARC, versions de schémas, validation et cache d'assets | À rédiger |
| ADR-0006 | Version Bevy et features après un spike reproductible | À rédiger |

Les ADR-0002 à ADR-0006 sont des sujets ouverts, pas des décisions implicites. Les références aux versions candidates dans l'audit restent provisoires jusqu'au spike technique.
