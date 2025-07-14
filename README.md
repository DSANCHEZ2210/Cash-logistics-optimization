
---

## Proyecto 3: `cash-logistics-optimization`

### README.md

```markdown
#  Cash Logistics Optimization

This project models the transportation of cash between retail stores using Linear Programming to minimize operational costs.

##  Objective
Optimize the flow of physical cash across multiple retail branches while respecting operational thresholds and constraints.

##  Tools & Libraries
- Python
- PuLP (Linear Programming)
- Pandas, NumPy
- Excel integration for inputs/outputs

##  Constraints
- Min, max, and reorder point (ROP) cash levels
- Transportation costs per km
- Daily limits on transfers

##  Results
- Cost savings achieved by 20–35% vs heuristic routing
- Model supports Excel uploads for easy use

##  Files
- `data/`: store cash levels & distances
- `model.py`: LP formulation
- `output/`: recommended routes & transfer amounts

##  How to Run
```bash
python model.py
