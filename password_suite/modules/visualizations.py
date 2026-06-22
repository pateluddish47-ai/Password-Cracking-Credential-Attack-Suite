"""Chart helpers shared by the CLI report generator and the Streamlit dashboard."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .strength_analyzer import StrengthResult

SEVERITY_COLORS = {
    "Critical": "#d32f2f",
    "High": "#f57c00",
    "Medium": "#fbc02d",
    "Low": "#388e3c",
}


def plot_entropy_histogram(results: list[StrengthResult], output_path: str | Path | None = None):
    entropies = [r.entropy_bits for r in results]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(entropies, bins=min(10, max(3, len(entropies))), color="#1976d2", edgecolor="white")
    ax.set_xlabel("Entropy (bits)")
    ax.set_ylabel("Number of passwords")
    ax.set_title("Password Entropy Distribution")
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150)
    return fig


def plot_severity_pie(results: list[StrengthResult], output_path: str | Path | None = None):
    counts = Counter(r.severity for r in results)
    labels = [s for s in ("Critical", "High", "Medium", "Low") if s in counts]
    sizes = [counts[s] for s in labels]
    colors = [SEVERITY_COLORS[s] for s in labels]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.0f%%", startangle=90)
    ax.set_title("Severity Distribution")
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150)
    return fig


def plot_risk_ranking(results: list[StrengthResult], output_path: str | Path | None = None):
    ranked = sorted(results, key=lambda r: r.entropy_bits)
    labels = [r.password for r in ranked]
    entropies = [r.entropy_bits for r in ranked]
    colors = [SEVERITY_COLORS[r.severity] for r in ranked]

    fig, ax = plt.subplots(figsize=(7, max(3, 0.4 * len(ranked))))
    ax.barh(labels, entropies, color=colors)
    ax.set_xlabel("Entropy (bits)")
    ax.set_title("Per-Account Risk Ranking (lowest entropy = highest risk)")
    fig.tight_layout()
    if output_path:
        fig.savefig(output_path, dpi=150)
    return fig
