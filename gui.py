#!/usr/bin/env python3
"""Tkinter GUI for the AI world simulation."""
from __future__ import annotations

import math
import random
import tkinter as tk
from dataclasses import dataclass
from typing import List, Tuple

from main import Environment, GENE_NAMES, Being, fitness, random_being, reproduce


@dataclass
class WorldState:
    population: List[Being]
    generation: int
    env: Environment


def seed_population(size: int, rng: random.Random) -> List[Being]:
    return [random_being(rng) for _ in range(size)]


def build_grid(population: List[Being], grid_size: int) -> List[List[Being]]:
    padded = population + [population[-1]] * max(0, grid_size * grid_size - len(population))
    return [
        padded[row * grid_size : (row + 1) * grid_size]
        for row in range(grid_size)
    ]


def fitness_color(score: float) -> str:
    score = max(0.0, min(1.0, score))
    red = int(255 * (1 - score))
    green = int(255 * score)
    return f"#{red:02x}{green:02x}40"


class WorldApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("AI World Simulator")
        self.rng = random.Random()

        self.population_size = tk.IntVar(value=64)
        self.mutation_rate = tk.DoubleVar(value=0.1)
        self.mutation_strength = tk.DoubleVar(value=0.15)
        self.auto_generations = tk.IntVar(value=10)
        self.generations = tk.IntVar(value=0)
        self.running = False

        self.canvas = tk.Canvas(root, width=480, height=480, bg="#1f2933")
        self.canvas.grid(row=0, column=0, rowspan=6, padx=10, pady=10)

        control = tk.Frame(root)
        control.grid(row=0, column=1, sticky="n")

        tk.Label(control, text="Population").grid(row=0, column=0, sticky="w")
        tk.Entry(control, textvariable=self.population_size, width=8).grid(row=0, column=1)

        tk.Label(control, text="Mutation rate").grid(row=1, column=0, sticky="w")
        tk.Entry(control, textvariable=self.mutation_rate, width=8).grid(row=1, column=1)

        tk.Label(control, text="Mutation strength").grid(row=2, column=0, sticky="w")
        tk.Entry(control, textvariable=self.mutation_strength, width=8).grid(row=2, column=1)

        tk.Label(control, text="Auto generations").grid(row=3, column=0, sticky="w")
        tk.Entry(control, textvariable=self.auto_generations, width=8).grid(row=3, column=1)

        self.env_label = tk.Label(control, text="Environment: --")
        self.env_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.summary_label = tk.Label(control, text="Summary: --", justify="left")
        self.summary_label.grid(row=5, column=0, columnspan=2, sticky="w")

        tk.Button(control, text="New World", command=self.reset_world).grid(
            row=6, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )
        tk.Button(control, text="Step", command=self.step_world).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(5, 0)
        )
        tk.Button(control, text="Run", command=self.run_generations).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=(5, 0)
        )

        self.state = WorldState(
            population=seed_population(self.population_size.get(), self.rng),
            generation=0,
            env=Environment.random(self.rng),
        )
        self.draw_world()

    def reset_world(self) -> None:
        self.state = WorldState(
            population=seed_population(self.population_size.get(), self.rng),
            generation=0,
            env=Environment.random(self.rng),
        )
        self.generations.set(0)
        self.draw_world()

    def step_world(self, *, manual: bool = True) -> None:
        if manual and self.running:
            self.running = False
        env = Environment.random(self.rng)
        survivors = [
            being for being in self.state.population if self.rng.random() < fitness(being, env, self.rng)
        ]
        self.state = WorldState(
            population=reproduce(
                survivors,
                self.population_size.get(),
                self.rng,
                self.mutation_rate.get(),
                self.mutation_strength.get(),
            ),
            generation=self.state.generation + 1,
            env=env,
        )
        self.generations.set(self.state.generation)
        self.draw_world()

    def run_generations(self) -> None:
        if self.running:
            return
        total = max(0, self.auto_generations.get())
        if total == 0:
            return
        self.running = True
        self._run_step(remaining=total)

    def _run_step(self, remaining: int) -> None:
        if not self.running or remaining <= 0:
            self.running = False
            return
        self.step_world(manual=False)
        self.root.after(200, lambda: self._run_step(remaining - 1))

    def draw_world(self) -> None:
        self.canvas.delete("all")
        population = self.state.population
        grid_size = math.ceil(math.sqrt(len(population)))
        cell_size = 480 / grid_size
        grid = build_grid(population, grid_size)
        for row, beings in enumerate(grid):
            for col, being in enumerate(beings):
                score = fitness(being, self.state.env, self.rng)
                x0 = col * cell_size
                y0 = row * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                self.canvas.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=fitness_color(score),
                    outline="#0b0f14",
                )

        env = self.state.env
        self.env_label.config(
            text=(
                f"Environment: resources={env.resources:.2f}, hazards={env.hazards:.2f}, "
                f"crowding={env.crowding:.2f}"
            )
        )
        averages = [
            sum(getattr(being, gene) for being in population) / len(population)
            for gene in GENE_NAMES
        ]
        summary = ", ".join(f"{gene}={avg:.2f}" for gene, avg in zip(GENE_NAMES, averages))
        self.summary_label.config(text=f"Summary: Gen {self.state.generation} | {summary}")


def main() -> None:
    root = tk.Tk()
    app = WorldApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
