#!/usr/bin/env python3
"""
Reuse-cycle TEA/LCA analysis for P66614Cl treatment of PTFE.

This script reruns the complete Monte Carlo TEA/LCA calculation at each fixed
reuse-cycle count from 1 through 40. It does not impose an assumed cost or
environmental-impact decay curve. Each point is calculated from the process model.

Required file:
    assumptions.xlsx
with sheets:
    General, design, LCA

Outputs:
    reuse_cycle_results.xlsx
    reuse_cycle_cost.png
    reuse_cycle_impacts.png

Important configuration choices are located immediately below.
"""

from __future__ import annotations

from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# =============================================================================
# USER SETTINGS
# =============================================================================

ASSUMPTIONS_FILE = "assumptions.xlsx"
OUTPUT_DIRECTORY = "reuse_cycle_model_outputs"

MIN_REUSE_CYCLES = 1
MAX_REUSE_CYCLES = 40

# True: acetone and 6 M NaOH are used after every treatment/reuse cycle.
# False: acetone and NaOH are used only once for the full reuse sequence.
CLEANING_AFTER_EVERY_CYCLE = True

# True: lost ionic-liquid inventory is replaced after every cycle.
# False: makeup is calculated only from cumulative inventory loss after all cycles.
MAKEUP_AFTER_EVERY_CYCLE = True

# NaOH solution is prepared from beads at 6 mol/L.
NAOH_MOLARITY_MOL_L = 6.0
NAOH_MOLAR_MASS_G_MOL = 40.0

# Current model follows the original energy boundary:
# one hotplate synthesis/heating event supplies the reusable inventory.
# Set True only if the hotplate heating step is repeated for every reuse cycle.
HEATING_AFTER_EVERY_CYCLE = False

# If hotplate_load_factor is absent from the workbook, use this value.
DEFAULT_HOTPLATE_LOAD_FACTOR = 0.50

# Percentiles reported for each cycle.
LOW_PERCENTILE = 5
MID_PERCENTILE = 50
HIGH_PERCENTILE = 95

RANDOM_SEED = 42


# =============================================================================
# INPUT AND SAMPLING HELPERS
# =============================================================================

def load_assumptions(path: str | Path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path.resolve()}. Put this script in the same "
            "folder as assumptions.xlsx or change ASSUMPTIONS_FILE."
        )

    general = pd.read_excel(path, sheet_name="General", index_col="Parameter")
    design = pd.read_excel(path, sheet_name="design", index_col="Parameter")
    lca = pd.read_excel(path, sheet_name="LCA", index_col="Parameter")
    return general, design, lca


def clean_distribution_name(value) -> str:
    if pd.isna(value):
        return "constant"
    return str(value).strip().lower()


def sample_parameter(
    table: pd.DataFrame,
    parameter: str,
    n: int,
    rng: np.random.Generator,
    *,
    default: float | None = None,
) -> np.ndarray:
    """
    Sample one assumptions-sheet parameter.

    Supported distributions: constant, uniform, triangular, normal.
    For malformed bounds, the function provides a warning and uses a defensible
    fallback rather than silently producing invalid samples.
    """
    if parameter not in table.index:
        if default is None:
            raise KeyError(f"Parameter '{parameter}' is missing from the assumptions sheet.")
        return np.full(n, default, dtype=float)

    row = table.loc[parameter]
    expected = pd.to_numeric(row.get("expected"), errors="coerce")
    low = pd.to_numeric(row.get("low"), errors="coerce")
    high = pd.to_numeric(row.get("high"), errors="coerce")
    distribution = clean_distribution_name(row.get("distribution"))

    if pd.isna(expected):
        if default is None:
            raise ValueError(f"Parameter '{parameter}' has no expected value.")
        expected = default

    if distribution in {"constant", "nan", ""}:
        return np.full(n, float(expected))

    if distribution == "uniform":
        if pd.isna(low) or pd.isna(high):
            warnings.warn(
                f"{parameter}: uniform distribution lacks bounds; using constant expected value."
            )
            return np.full(n, float(expected))
        lo, hi = sorted((float(low), float(high)))
        return rng.uniform(lo, hi, n)

    if distribution == "triangular":
        if pd.isna(low) or pd.isna(high):
            warnings.warn(
                f"{parameter}: triangular distribution lacks bounds; using constant expected value."
            )
            return np.full(n, float(expected))
        lo, hi = sorted((float(low), float(high)))
        mode = float(expected)
        if not lo <= mode <= hi:
            warnings.warn(
                f"{parameter}: expected value is outside [{lo}, {hi}]. "
                "Using the interval midpoint as the triangular mode."
            )
            mode = (lo + hi) / 2
        return rng.triangular(lo, mode, hi, n)

    if distribution == "normal":
        sd = pd.to_numeric(row.get("sd"), errors="coerce")
        if pd.isna(sd):
            if not pd.isna(low) and not pd.isna(high):
                sd = (float(high) - float(low)) / 4
            else:
                raise ValueError(f"{parameter}: normal distribution requires sd or bounds.")
        return rng.normal(float(expected), float(sd), n)

    raise ValueError(
        f"{parameter}: unsupported distribution '{distribution}'. "
        "Use constant, uniform, triangular, or normal."
    )


def lca_vector(lca_table: pd.DataFrame, parameter: str) -> np.ndarray:
    if parameter not in lca_table.index:
        raise KeyError(f"LCA parameter '{parameter}' is missing.")
    # First two columns are Description and Unit.
    return lca_table.loc[parameter].iloc[2:].to_numpy(dtype=float)


def as_fraction(values: np.ndarray, name: str) -> np.ndarray:
    """
    Convert values such as 35 to 0.35 when a fraction was entered as a percentage.
    """
    values = np.asarray(values, dtype=float)
    if np.nanmedian(values) > 1:
        warnings.warn(f"{name} appears to be entered as percent; dividing by 100.")
        values = values / 100.0
    return values


def summary(values: np.ndarray) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    return {
        "mean": float(np.mean(values)),
        "p05": float(np.percentile(values, LOW_PERCENTILE)),
        "median": float(np.percentile(values, MID_PERCENTILE)),
        "p95": float(np.percentile(values, HIGH_PERCENTILE)),
    }


# =============================================================================
# MODEL
# =============================================================================

def main() -> None:
    general, design, lca = load_assumptions(ASSUMPTIONS_FILE)

    n_samples = int(general.loc["n_samples", "expected"])
    rng = np.random.default_rng(RANDOM_SEED)
    eps = 1e-12

    # Use common random numbers for every cycle count. This makes differences
    # across the reuse curve attributable to reuse cycles rather than resampling.
    discount_rate = sample_parameter(general, "discount_rate", n_samples, rng)
    analysis_period = sample_parameter(general, "analysis_period", n_samples, rng)

    steel_fraction = as_fraction(
        sample_parameter(design, "steel_fraction", n_samples, rng),
        "steel_fraction",
    )
    concrete_fraction = as_fraction(
        sample_parameter(design, "concrete_fraction", n_samples, rng),
        "concrete_fraction",
    )
    electricity_cost = sample_parameter(design, "electricity_cost", n_samples, rng)

    ptfe_throughput_t_per_year = sample_parameter(
        design, "ptfe_throughput_t_per_year", n_samples, rng
    )
    hotplate_power = sample_parameter(design, "hotplate_power", n_samples, rng)
    hotplate_weight = sample_parameter(design, "hotplate_weight", n_samples, rng)
    time_100C = sample_parameter(design, "time_100C", n_samples, rng)
    hotplate_load_factor = sample_parameter(
        design,
        "hotplate_load_factor",
        n_samples,
        rng,
        default=DEFAULT_HOTPLATE_LOAD_FACTOR,
    )

    P66614_Cl_amount = sample_parameter(design, "P66614_Cl_amount", n_samples, rng)
    HCL_amount = sample_parameter(design, "HCL_amount", n_samples, rng)
    H2O2_amount = sample_parameter(design, "H2O2_amount", n_samples, rng)
    acetone_amount = sample_parameter(design, "acetone_amount", n_samples, rng)
    NaOH_amount = sample_parameter(design, "NaOH_amount", n_samples, rng)

    density_P66614_Cl = sample_parameter(
        design, "density_P66614_Cl", n_samples, rng
    )
    density_HCL = sample_parameter(design, "density_HCL", n_samples, rng)
    density_H2O2 = sample_parameter(design, "density_H2O2", n_samples, rng)
    density_acetone = sample_parameter(
        design, "density_acetone", n_samples, rng
    )

    PTFE_mass = sample_parameter(design, "PTFE_mass", n_samples, rng)
    recovery_fraction = np.clip(
        sample_parameter(design, "recovery_fraction", n_samples, rng), 0.0, 1.0
    )
    reconditioning_cost = sample_parameter(
        design, "reconditioning_cost_per_cycle_USD", n_samples, rng
    )

    P66614_Cl_cost = sample_parameter(design, "P66614_Cl_cost", n_samples, rng)
    HCL_cost = sample_parameter(design, "HCL_cost", n_samples, rng)
    H2O2_cost = sample_parameter(design, "H2O2_cost", n_samples, rng)
    acetone_cost = sample_parameter(design, "acetone_cost", n_samples, rng)
    hotplate_cost = sample_parameter(design, "hotplate_cost", n_samples, rng)
    NaOH_cost = sample_parameter(design, "NaOH_cost", n_samples, rng)

    # LCA characterization vectors.
    stainless_steel_LCA = lca_vector(lca, "stainless_steel")
    concrete_LCA = lca_vector(lca, "concrete")
    electricity_LCA = lca_vector(lca, "electricity")
    HCL_LCA = lca_vector(lca, "HCL_LCA")
    H2O2_LCA = lca_vector(lca, "H2O2_LCA")
    acetone_LCA = lca_vector(lca, "acetone_LCA")
    P66614_Cl_LCA = lca_vector(lca, "P66614_Cl_LCA")
    NaOH_LCA = lca_vector(lca, "NaOH_LCA")

    impact_names = [
        "AP",
        "GWP",
        "EFW",
        "EP",
        "HTC",
        "HTNC",
        "ODP",
        "PMFP",
        "MIR",
    ]

    # Per-preparation masses, g.
    mass_P66614_Cl = P66614_Cl_amount * density_P66614_Cl
    mass_HCL = HCL_amount * density_HCL
    mass_H2O2 = H2O2_amount * density_H2O2
    mass_acetone = acetone_amount * density_acetone

    # Active NaOH mass from 6 M solution, not total solution mass.
    mass_NaOH = (
        NaOH_amount / 1000.0
        * NAOH_MOLARITY_MOL_L
        * NAOH_MOLAR_MASS_G_MOL
    )

    mass_reagent_prepared_kg = np.maximum(
        (mass_P66614_Cl + mass_HCL + mass_H2O2) / 1000.0,
        eps,
    )
    PTFE_mass_kg = np.maximum(PTFE_mass / 1000.0, eps)

    # Per-preparation costs.
    cost_P66614 = mass_P66614_Cl * P66614_Cl_cost / 1000.0
    cost_HCL = mass_HCL * HCL_cost / 1000.0
    cost_H2O2 = mass_H2O2 * H2O2_cost / 1000.0
    batch_synthesis_cost = cost_P66614 + cost_HCL + cost_H2O2

    cost_acetone_event = mass_acetone * acetone_cost / 1000.0
    cost_NaOH_event = mass_NaOH * NaOH_cost / 1000.0

    # Energy per heating event.
    energy_per_heating_event_kWh = (
        hotplate_power / 1000.0
        * time_100C
        * hotplate_load_factor
    )

    # Capital allocation.
    capital_recovery_factor = (
        discount_rate * (1 + discount_rate) ** analysis_period
        / ((1 + discount_rate) ** analysis_period - 1)
    )
    hotplate_capital_annual = hotplate_cost * capital_recovery_factor
    capital_cost_per_kg = (
        hotplate_capital_annual
        / np.maximum(ptfe_throughput_t_per_year, eps)
        / 1000.0
    )

    steel_hotplate_kg = hotplate_weight * steel_fraction
    concrete_hotplate_kg = hotplate_weight * concrete_fraction
    construction_impacts = (
        steel_hotplate_kg[:, None] * stainless_steel_LCA[None, :]
        + concrete_hotplate_kg[:, None] * concrete_LCA[None, :]
    )
    annual_construction_impacts = construction_impacts / analysis_period[:, None]
    capital_impacts_per_kg = (
        annual_construction_impacts
        / np.maximum(ptfe_throughput_t_per_year[:, None], eps)
        / 1000.0
    )

    cost_rows = []
    impact_rows = []
    all_cost_runs = {}
    all_gwp_runs = {}

    for cycles in range(MIN_REUSE_CYCLES, MAX_REUSE_CYCLES + 1):
        total_PTFE_kg = PTFE_mass_kg * cycles

        if MAKEUP_AFTER_EVERY_CYCLE:
            makeup_needed_kg = (
                mass_reagent_prepared_kg
                * (1.0 - recovery_fraction)
                * max(cycles - 1, 0)
            )
        else:
            makeup_needed_kg = (
                mass_reagent_prepared_kg
                * (1.0 - recovery_fraction ** max(cycles - 1, 0))
            )

        synthesis_cost_per_kg_inventory = (
            batch_synthesis_cost / mass_reagent_prepared_kg
        )
        total_synthesis_cost = (
            batch_synthesis_cost
            + synthesis_cost_per_kg_inventory * makeup_needed_kg
        )

        cleaning_events = cycles if CLEANING_AFTER_EVERY_CYCLE else 1
        heating_events = cycles if HEATING_AFTER_EVERY_CYCLE else 1

        total_cleaning_cost = (
            cost_acetone_event + cost_NaOH_event
        ) * cleaning_events

        # Reconditioning is treated as a per-reuse event after the initial use.
        reconditioning_events = max(cycles - 1, 0)
        total_reconditioning_cost = (
            reconditioning_cost * reconditioning_events
        )

        OM_cost_per_kg = (
            total_synthesis_cost
            + total_cleaning_cost
            + total_reconditioning_cost
        ) / total_PTFE_kg

        energy_demand_kWh = energy_per_heating_event_kWh * heating_events
        energy_cost_per_kg = (
            energy_demand_kWh * electricity_cost / total_PTFE_kg
        )

        total_cost_per_kg = (
            capital_cost_per_kg
            + OM_cost_per_kg
            + energy_cost_per_kg
        )

        # LCA inventory multiplier for initial synthesis plus makeup.
        inventory_multiplier = (
            mass_reagent_prepared_kg + makeup_needed_kg
        ) / mass_reagent_prepared_kg

        synthesis_impacts = (
            mass_HCL[:, None] / 1000.0 * HCL_LCA[None, :]
            + mass_H2O2[:, None] / 1000.0 * H2O2_LCA[None, :]
            + mass_P66614_Cl[:, None] / 1000.0 * P66614_Cl_LCA[None, :]
        ) * inventory_multiplier[:, None]

        cleaning_impacts = (
            mass_acetone[:, None] / 1000.0 * acetone_LCA[None, :]
            + mass_NaOH[:, None] / 1000.0 * NaOH_LCA[None, :]
        ) * cleaning_events

        OM_impacts_per_kg = (
            synthesis_impacts + cleaning_impacts
        ) / total_PTFE_kg[:, None]

        energy_impacts_per_kg = (
            energy_demand_kWh[:, None]
            * electricity_LCA[None, :]
            / total_PTFE_kg[:, None]
        )

        total_impacts_per_kg = (
            capital_impacts_per_kg
            + OM_impacts_per_kg
            + energy_impacts_per_kg
        )

        all_cost_runs[f"cycle_{cycles}"] = total_cost_per_kg
        all_gwp_runs[f"cycle_{cycles}"] = total_impacts_per_kg[:, 1]

        cost_summary = summary(total_cost_per_kg)
        cost_rows.append({"reuse_cycles": cycles, **cost_summary})

        for index, impact_name in enumerate(impact_names):
            impact_summary = summary(total_impacts_per_kg[:, index])
            impact_rows.append(
                {
                    "reuse_cycles": cycles,
                    "impact_category": impact_name,
                    **impact_summary,
                }
            )

    cost_summary_df = pd.DataFrame(cost_rows)
    impact_summary_df = pd.DataFrame(impact_rows)
    cost_runs_df = pd.DataFrame(all_cost_runs)
    gwp_runs_df = pd.DataFrame(all_gwp_runs)

    output_dir = Path(OUTPUT_DIRECTORY)
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_path = output_dir / "reuse_cycle_results.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        cost_summary_df.to_excel(writer, sheet_name="cost_summary", index=False)
        impact_summary_df.to_excel(writer, sheet_name="impact_summary", index=False)
        cost_runs_df.to_excel(writer, sheet_name="cost_all_runs", index=False)
        gwp_runs_df.to_excel(writer, sheet_name="GWP_all_runs", index=False)

    # Cost figure.
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    x = cost_summary_df["reuse_cycles"].to_numpy()
    median = cost_summary_df["median"].to_numpy()
    p05 = cost_summary_df["p05"].to_numpy()
    p95 = cost_summary_df["p95"].to_numpy()

    ax.fill_between(x, p05, p95, alpha=0.22, label="5th-95th percentile")
    ax.plot(x, median, marker="o", markersize=3.5, linewidth=1.8, label="Median")
    ax.set_xlabel("Reuse cycles")
    ax.set_ylabel("Treatment cost (USD/kg PTFE)")
    ax.set_title("Treatment cost versus reuse cycles")
    ax.set_xlim(MIN_REUSE_CYCLES, MAX_REUSE_CYCLES)
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(output_dir / "reuse_cycle_cost.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # Environmental impacts normalized to each category's cycle-1 median.
    pivot = impact_summary_df.pivot(
        index="reuse_cycles",
        columns="impact_category",
        values="median",
    )
    normalized = pivot / pivot.iloc[0]

    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    for impact_name in impact_names:
        ax.plot(
            normalized.index,
            normalized[impact_name],
            marker="o",
            markersize=2.8,
            linewidth=1.3,
            label=impact_name,
        )
    ax.set_xlabel("Reuse cycles")
    ax.set_ylabel("Impact relative to one-cycle case")
    ax.set_title("Environmental impacts versus reuse cycles")
    ax.set_xlim(MIN_REUSE_CYCLES, MAX_REUSE_CYCLES)
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout()
    fig.savefig(
        output_dir / "reuse_cycle_impacts.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(fig)

    print(f"Completed reuse-cycle analysis for cycles {MIN_REUSE_CYCLES}-{MAX_REUSE_CYCLES}.")
    print(f"Results: {excel_path}")
    print(f"Cost figure: {output_dir / 'reuse_cycle_cost.png'}")
    print(f"Impact figure: {output_dir / 'reuse_cycle_impacts.png'}")


if __name__ == "__main__":
    main()
