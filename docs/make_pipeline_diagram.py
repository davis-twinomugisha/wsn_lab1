import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(10, 3.2), dpi=200)
ax.set_xlim(0, 10); ax.set_ylim(0, 3.2); ax.axis("off")
navy = "#1f2d3d"

def box(x, y, w, h, title, sub, fill):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                lw=1.3, ec=navy, fc=fill))
    ax.text(x + w/2, y + h*0.64, title, ha="center", va="center", fontsize=9, fontweight="bold", color=navy)
    ax.text(x + w/2, y + h*0.30, sub, ha="center", va="center", fontsize=6.8, color=navy)

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=navy, lw=1.2))

sense = "#eef4ea"; edge = "#e8eef5"; out = "#fdf3e3"
box(0.1, 2.1, 1.5, 0.85, "DHT22", "temp + humidity", sense)
box(0.1, 1.15, 1.5, 0.85, "LDR module", "light (analog)", sense)
box(0.1, 0.2, 1.5, 0.85, "PIR", "motion (digital)", sense)

steps = [("Sample", "1 Hz loop"), ("Validate", "range + NaN check"), ("Calibrate", "slope, offset"),
         ("Filter", "5-sample MA, Δx"), ("Decide", "HIGH_TEMP > 28°C")]
x = 2.15
for t, s in steps:
    box(x, 1.15, 1.05, 0.85, t, s, edge)
    x += 1.25
xs = 2.15
for i in range(len(steps) - 1):
    arrow(xs + 1.05 + i*1.25, 1.575, xs + 1.25 + i*1.25, 1.575)
for yy in (2.52, 1.575, 0.62):
    arrow(1.6, yy, 2.15, 1.575)
ax.text(2.15 + 2.5, 2.3, "ESP32 edge node (firmware)", ha="center", fontsize=9, style="italic", color=navy)
ax.add_patch(FancyBboxPatch((2.05, 1.02), 6.3, 1.5, boxstyle="round,pad=0.02,rounding_size=0.1",
                            lw=1.0, ec=navy, fc="none", ls="--"))
box(8.75, 2.1, 1.15, 0.85, "LED / buzzer", "local status", out)
box(8.75, 1.15, 1.15, 0.85, "Serial CSV", "machine-readable", out)
box(8.75, 0.2, 1.15, 0.85, "Python", "stats + plots", out)
last = 2.15 + 4*1.25 + 1.05
arrow(last, 1.75, 8.75, 2.5); arrow(last, 1.575, 8.75, 1.575); arrow(9.325, 1.15, 9.325, 1.05)
plt.tight_layout()
plt.savefig("system_architecture.png", dpi=200, bbox_inches="tight", facecolor="white")
print("saved")
