import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

Path("plots").mkdir(exist_ok=True)

with open("results/decisions.csv", newline="") as f:
    clear = list(csv.DictReader(f))
with open("results/hard_decisions.csv", newline="") as f:
    hard = list(csv.DictReader(f))
with open("data/ground_truth.jsonl") as f:
    clear_truth = {r["event_id"]: r["expected"] for r in map(json.loads, f)}
with open("data/hard_ground_truth.jsonl") as f:
    hard_truth = {r["event_id"]: r["expected"] for r in map(json.loads, f)}

plt.style.use("dark_background")
fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor="#0b1220")
for ax in axes:
    ax.set_facecolor("#111d30")
    ax.grid(axis="y", alpha=0.15)
    ax.spines[["top", "right"]].set_visible(False)

accuracy = [
    sum(r["decision"] == clear_truth[r["event_id"]] for r in clear) / len(clear),
    sum(r["decision"] == hard_truth[r["event_id"]] for r in hard) / len(hard),
]
bars = axes[0].bar(
    ["Clear cases\nn=32", "Mixed-signal cases\nn=16"],
    [v * 100 for v in accuracy],
    color=["#37d5a6", "#fbad57"],
    width=0.55,
)
axes[0].set_ylim(0, 110)
axes[0].set_ylabel("Model decisions matching test labels (%)")
axes[0].set_title("Accuracy falls on mixed-signal events", fontsize=14, pad=18)
for bar, value in zip(bars, accuracy):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 2,
        f"{value:.1%}",
        ha="center",
        fontsize=14,
        fontweight="bold",
    )

axes[1].boxplot(
    [
        [float(r["latency_ms"]) for r in clear],
        [float(r["latency_ms"]) for r in hard],
    ],
    tick_labels=["Clear\nn=32", "Mixed-signal\nn=16"],
    patch_artist=True,
    showfliers=True,
    boxprops={"facecolor": "#277da1", "edgecolor": "#b5d9ed"},
    medianprops={"color": "#fbad57", "linewidth": 2},
    whiskerprops={"color": "#b5d9ed"},
    capprops={"color": "#b5d9ed"},
    flierprops={"markerfacecolor": "#fbad57", "markeredgecolor": "#fbad57"},
)
axes[1].set_ylabel("Jev API round-trip latency (ms)")
axes[1].set_title("Observed client-side decision latency", fontsize=14, pad=18)

fig.suptitle("Can Jev route Kafka events that pass schema validation?", fontsize=18, weight="bold")
fig.text(
    0.5, 0.01,
    "48 synthetic events  •  1 worker  •  local Kafka  •  Jev API  •  Sep 2026",
    ha="center", color="#a3b7c9", fontsize=10,
)
fig.tight_layout(rect=(0, 0.05, 1, 0.92))
fig.savefig("plots/jev_kafka_results.png", dpi=180, facecolor=fig.get_facecolor())
print("Saved plots/jev_kafka_results.png")
