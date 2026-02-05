#!/usr/bin/env python3
"""Small world evolution simulation."""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List, Tuple


GENE_NAMES = ("speed", "resilience", "sociability", "foraging")


@dataclass(frozen=True)
class Being:
    genes: Tuple[float, float, float, float]

    @property
    def speed(self) -> float:
        return self.genes[0]

    @property
    def resilience(self) -> float:
        return self.genes[1]

    @property
    def sociability(self) -> float:
        return self.genes[2]

    @property
    def foraging(self) -> float:
        return self.genes[3]


@dataclass
class Environment:
    resources: float
    hazards: float
    crowding: float

    @classmethod
    def random(cls, rng: random.Random) -> "Environment":
        return cls(
            resources=rng.uniform(0.2, 1.0),
            hazards=rng.uniform(0.0, 1.0),
            crowding=rng.uniform(0.0, 1.0),
        )


def random_being(rng: random.Random) -> Being:
    genes = tuple(rng.uniform(0.0, 1.0) for _ in GENE_NAMES)
    return Being(genes=genes)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def fitness(being: Being, env: Environment, rng: random.Random) -> float:
    """Return a survival score in [0, 1]."""
    resource_score = env.resources * (0.5 * being.foraging + 0.5 * being.sociability)
    hazard_resist = (1 - env.hazards) * (0.7 * being.resilience + 0.3 * being.speed)
    crowding_effect = (1 - env.crowding) * (0.6 * being.sociability + 0.4 * being.speed)

    base = (resource_score + hazard_resist + crowding_effect) / 3
    luck = rng.uniform(-0.05, 0.05)
    return clamp(base + luck)


def survives(being: Being, env: Environment, rng: random.Random) -> bool:
    return rng.random() < fitness(being, env, rng)


def mutate_gene(value: float, rng: random.Random, rate: float, strength: float) -> float:
    if rng.random() > rate:
        return value
    shift = rng.uniform(-strength, strength)
    return clamp(value + shift)


def reproduce(
    parents: Iterable[Being],
    target_size: int,
    rng: random.Random,
    mutation_rate: float,
    mutation_strength: float,
) -> List[Being]:
    parent_list = list(parents)
    if not parent_list:
        return [random_being(rng) for _ in range(target_size)]

    offspring: List[Being] = []
    while len(offspring) < target_size:
        mom = rng.choice(parent_list)
        dad = rng.choice(parent_list)
        genes = tuple(
            mutate_gene(rng.choice([g1, g2]), rng, mutation_rate, mutation_strength)
            for g1, g2 in zip(mom.genes, dad.genes)
        )
        offspring.append(Being(genes=genes))
    return offspring


def summarize(population: Iterable[Being]) -> str:
    pop = list(population)
    if not pop:
        return "no survivors"
    averages = [mean(getattr(being, gene) for being in pop) for gene in GENE_NAMES]
    parts = ", ".join(f"{name}={avg:.2f}" for name, avg in zip(GENE_NAMES, averages))
    return f"avg genes: {parts}"


def run_simulation(
    *,
    population_size: int,
    generations: int,
    mutation_rate: float,
    mutation_strength: float,
    seed: int | None,
) -> None:
    rng = random.Random(seed)
    population = [random_being(rng) for _ in range(population_size)]

    for generation in range(1, generations + 1):
        env = Environment.random(rng)
        survivors = [being for being in population if survives(being, env, rng)]
        print(
            f"Gen {generation:02d}: env(resources={env.resources:.2f}, "
            f"hazards={env.hazards:.2f}, crowding={env.crowding:.2f}) -> "
            f"{len(survivors)}/{len(population)} survived; {summarize(survivors)}"
        )
        population = reproduce(
            survivors,
            population_size,
            rng,
            mutation_rate,
            mutation_strength,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulate a small world of evolving beings.",
    )
    parser.add_argument("--population", type=int, default=50)
    parser.add_argument("--generations", type=int, default=20)
    parser.add_argument("--mutation-rate", type=float, default=0.1)
    parser.add_argument("--mutation-strength", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_simulation(
        population_size=args.population,
        generations=args.generations,
        mutation_rate=args.mutation_rate,
        mutation_strength=args.mutation_strength,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
