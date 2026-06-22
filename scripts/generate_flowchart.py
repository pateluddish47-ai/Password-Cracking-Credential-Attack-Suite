"""Generates a professional architecture flowchart for the project report."""
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

STAGES = [
    ("START", "terminator"),
    ("User Input\n(usernames / password samples / hash files)", "process"),
    ("Dictionary Generator\n(patterns, mutations, leet-speak)", "process"),
    ("Hash Extraction\n(Linux shadow / Windows SAM, offline)", "process"),
    ("Attack Simulation\n(dictionary attack, brute-force estimate,\nreal crypt verification)", "process"),
    ("Password Strength Analysis\n(entropy, complexity, patterns)", "process"),
    ("NIST SP 800-63B Compliance Check\n(breach corpus, policy rules)", "process"),
    ("Audit Report Generation\n(charts + markdown report)", "process"),
    ("END", "terminator"),
]

BOX_W, BOX_H, GAP = 4.6, 1.0, 0.55
FIG_H = len(STAGES) * (BOX_H + GAP)

fig, ax = plt.subplots(figsize=(7.5, FIG_H * 0.62))
ax.set_xlim(0, 10)
ax.set_ylim(0, FIG_H)
ax.axis("off")

PROCESS_COLOR = "#1e3a5f"
TERMINATOR_COLOR = "#2e7d32"
TEXT_COLOR = "white"

y = FIG_H - BOX_H
centers = []
for label, kind in STAGES:
    x = (10 - BOX_W) / 2
    if kind == "terminator":
        box = mpatches.FancyBboxPatch(
            (x, y), BOX_W, BOX_H,
            boxstyle="round,pad=0.02,rounding_size=0.5",
            linewidth=1.5, edgecolor="#1b1b1b", facecolor=TERMINATOR_COLOR,
        )
    else:
        box = mpatches.FancyBboxPatch(
            (x, y), BOX_W, BOX_H,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.5, edgecolor="#1b1b1b", facecolor=PROCESS_COLOR,
        )
    ax.add_patch(box)
    ax.text(x + BOX_W / 2, y + BOX_H / 2, label, ha="center", va="center",
            color=TEXT_COLOR, fontsize=9.5, fontweight="bold", linespacing=1.4)
    centers.append((x + BOX_W / 2, y))
    y -= (BOX_H + GAP)

for i in range(len(centers) - 1):
    x0, y0 = centers[i]
    x1, y1 = centers[i + 1]
    arrow = FancyArrowPatch(
        (x0, y0), (x1, y1 + BOX_H),
        arrowstyle="-|>", mutation_scale=18,
        linewidth=1.8, color="#444444",
    )
    ax.add_patch(arrow)

ax.set_title(
    "Password Cracking & Credential Attack Suite\nSystem Architecture / Workflow",
    fontsize=13, fontweight="bold", pad=14,
)

fig.tight_layout()
fig.savefig("reports/flowchart.png", dpi=200, bbox_inches="tight", facecolor="white")
print("saved reports/flowchart.png")
