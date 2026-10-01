# BioSim — island ecosystem simulation

A population simulation of herbivores and carnivores on an island, written as an object-oriented
system from scratch. Animals are born, eat, lose weight, migrate between cells, age and die, and
the landscape they live on decides how much food is available and whether they can enter at all.

Course project (INF200, NMBU), written with **Khalid Rashed**.

## Model

**Animals.** Herbivores and carnivores share a base class and differ in their parameters and in how
they feed. Each animal carries age, weight and fitness, and fitness drives birth probability,
killing probability, migration and death.

**Landscape.** Lowland, highland, desert and water. Each cell type sets the fodder available each
year, and water cannot be entered, which is what gives the island its shape.

**Island.** A map parsed from a multi-line string of terrain letters, with migration between the
four neighbouring cells each year.

**Simulation.** Runs the annual cycle, collects population numbers, and draws the island, the
population curves and the age, weight and fitness histograms as the years pass.

## Layout

| File | What it does |
|---|---|
| `Animals.py` | herbivore and carnivore classes, the annual cycle for one animal |
| `landscape.py` | cell types, fodder growth, feeding, procreation, death |
| `Island_map.py` | parses the map string, holds the grid, handles migration |
| `simulation.py` | runs the years, collects statistics, draws the live visualisation |

## Running it

```python
from simulation import BioSim

island = """\\
WWWWW
WLHLW
WLDLW
WWWWW"""

sim = BioSim(island_map=island, ini_pop=[...], seed=1)
sim.simulate(num_years=100)
```

`simulation.py` draws with matplotlib and can write the frames out as a movie, which needs ffmpeg
on the path.
