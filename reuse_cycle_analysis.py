#!/usr/bin/env python3
"""
Monte Carlo reuse-cycle analysis.

Outputs:
- all simulated reuse trajectories
- cycle-by-cycle summary statistics
- a two-panel reuse-cycle figure

Default model:
    value_n = initial_value * recovery_fraction**n
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


Distribution = Literal["constant", "uniform", "triangular", "normal"]


@dataclass
class Parameter:
    distribution: Distribution
    expected: float
    low: float | None = None
    high: float | None = None
    sd: float | None = None

    def sample(self, rng: np.random.Generator, n: int) -> np.ndarray:
        if self.distribution == "constant":
            return np.full(n, self.expected, dtype=float)

        if self.distribution == "uniform":
            if self.low is None or self.high is None:
                raise ValueError("Uniform distribution requires low and high.")
            return rng.uniform(self.low, self.high, size=n)

        if self.distribution == "triangular":
            if self.low is None or self.high is None:
                raise ValueError("Triangular distribution requires low and high.")
            if not (self.low <= self.expected <= self.high):
                raise ValueError("Need low <= expected <= high.")
            return rng.triangular(self.low, self.expected, self.high, size=n)

        if self.distribution == "normal":
            if self.sd is None:
                raise ValueError("Normal distribution requires sd.")
            return rng.normal(self.expected, self.sd, size=n)

        raise ValueError(f"Unsupported distribution: {self.distribution}")


@dataclass
class Scenario:
    name: str
    recovery_fraction: Parameter
    initial_value: Parameter
    max_cycles: int = 20
    n_runs: int = 10000
    seed: int = 42
    cycle_noise_sd: float = 0.0
    minimum_value: float = 0.0
    maximum_value: float = 1.0


def simulate_reuse(scenario: Scenario):
    rng = np.random.default_rng(scenario.seed)

    recovery = np.clip(
        scenario.recovery_fraction.sample(rng, scenario.n_runs), 0.0, 1.0
    )
    initial = scenario.initial_value.sample(rng, scenario.n_runs)

    cycles = np.arange(scenario.max_cycles + 1)
    values = np.empty((scenario.n_runs, len(cycles)))
    values[:, 0] = initial

    for cycle in range(1, len(cycles)):
        values[:, cycle] = values[:, cycle - 1] * recovery

        if scenario.cycle_noise_sd > 0:
            noise = rng.normal(0.0, scenario.cycle_noise_sd, scenario.n_runs)
            values[:, cycle] *= 1.0 + noise

        values[:, cycle] = np.clip(
            values[:, cycle],
            scenario.minimum_value,
            scenario.maximum_value,
        )

    runs_df = pd.DataFrame(
        values,
        columns=[f"cycle_{c}" for c in cycles]
    )
    runs_df.insert(0, "run", np.arange(1, scenario.n_runs + 1))
    runs_df["sampled_recovery_fraction"] = recovery
    runs_df["sampled_initial_value"] = initial

    summary_df = pd.DataFrame({
        "cycle": cycles,
        "mean": values.mean(axis=0),
        "median": np.median(values, axis=0),
        "p05": np.percentile(values, 5, axis=0),
        "p25": np.percentile(values, 25, axis=0),
        "p75": np.percentile(values, 75, axis=0),
        "p95": np.percentile(values, 95, axis=0),
    })

    return runs_df, summary_df


def plot_reuse(scenario, runs_df, summary_df, output_path, y_label):
    cycle_columns = [c for c in runs_df.columns if c.startswith("cycle_")]
    cycles = summary_df["cycle"].to_numpy()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

    ax = axes[0]
    n_to_plot = min(250, len(runs_df))
    for _, row in runs_df.iloc[:n_to_plot].iterrows():
        ax.plot(
            cycles,
            row[cycle_columns].to_numpy(dtype=float),
            linewidth=0.6,
            alpha=0.08,
        )

    ax.fill_between(
        cycles,
        summary_df["p05"].to_numpy(),
        summary_df["p95"].to_numpy(),
        alpha=0.22,
        label="5th-95th percentile",
    )
    ax.plot(
        cycles,
        summary_df["median"].to_numpy(),
        linewidth=2.2,
        label="Median",
    )
    ax.set_title("(a) Monte Carlo reuse trajectories")
    ax.set_xlabel("Reuse cycle")
    ax.set_ylabel(y_label)
    ax.set_xlim(0, scenario.max_cycles)
    ax.set_ylim(scenario.minimum_value, scenario.maximum_value)
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)

    ax = axes[1]
    lower = summary_df["median"].to_numpy() - summary_df["p05"].to_numpy()
    upper = summary_df["p95"].to_numpy() - summary_df["median"].to_numpy()

    ax.errorbar(
        cycles,
        summary_df["median"].to_numpy(),
        yerr=np.vstack([lower, upper]),
        marker="o",
        markersize=5,
        linewidth=1.8,
        capsize=3,
    )
    ax.set_title("(b) Median reuse profile")
    ax.set_xlabel("Reuse cycle")
    ax.set_ylabel(y_label)
    ax.set_xlim(0, scenario.max_cycles)
    ax.set_ylim(scenario.minimum_value, scenario.maximum_value)
    ax.grid(alpha=0.2)

    fig.suptitle(scenario.name)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_scenario(scenario, output_directory="reuse_cycle_outputs"):
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = scenario.name.lower().replace(" ", "_").replace("/", "_")

    runs_df, summary_df = simulate_reuse(scenario)

    runs_df.to_csv(output_dir / f"{safe_name}_all_runs.csv", index=False)
    summary_df.to_csv(output_dir / f"{safe_name}_summary.csv", index=False)

    plot_reuse(
        scenario,
        runs_df,
        summary_df,
        output_dir / f"{safe_name}_reuse_cycles.png",
        y_label="Fraction of initial inventory remaining",
    )

    print(f"Completed: {scenario.name}")


if __name__ == "__main__":

    scenarios = [
        Scenario(
            name="P66614Cl reuse",
            recovery_fraction=Parameter(
                distribution="triangular",
                expected=0.90,
                low=0.80,
                high=0.95,
            ),
            initial_value=Parameter(
                distribution="constant",
                expected=1.00,
            ),
            max_cycles=20,
            n_runs=10000,
            seed=42,
        ),

        # Example second scenario. Delete if not needed.
        Scenario(
            name="P66614Cl reuse high recovery",
            recovery_fraction=Parameter(
                distribution="triangular",
                expected=0.95,
                low=0.90,
                high=0.98,
            ),
            initial_value=Parameter(
                distribution="constant",
                expected=1.00,
            ),
            max_cycles=20,
            n_runs=10000,
            seed=43,
        ),
    ]

    for scenario in scenarios:
        run_scenario(scenario)
