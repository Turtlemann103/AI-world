# AI World Simulation

This project simulates a small world of beings who survive based on random genes and reproduce across generations.

## CLI Run

```bash
python3 main.py --population 60 --generations 25 --seed 42
```

You can tune the mutation settings:

```bash
python3 main.py --mutation-rate 0.2 --mutation-strength 0.25
```

## GUI Run

Launch a simple Tkinter visualization where each square is a being colored by survival fitness (red = lower, green = higher).

```bash
python3 gui.py
```

Use **New World** to reseed the population, **Step** to advance one generation, and **Run** to auto-advance by the configured number of generations.
