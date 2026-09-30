from _nb_builder import md, code, write_notebook

cells = []

cells.append(md("""\
# WSN Lab 1 — Temperature calibration (Section 9.1g)

Paired readings from the UNO R4 prototype's temperature channel and a
reference thermometer, taken at the same moment once both had settled.
The data lives in `data/calibration/calibration_pairs.csv`; add more rows
there and re-run to refine the model.

Two models are fitted:

- **Offset model** `T_cal = T_sensor + b` — the primary model. With only two
  pairs it leaves residuals, so its before/after error is meaningful.
- **Linear model** `T_cal = a·T_sensor + b` — reported for completeness. With
  two pairs a line passes through both points exactly, so its "after" error
  is zero by construction and says nothing about accuracy. It needs five or
  more pairs across a wider range to be trustworthy.
"""))

cells.append(code("""\
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/calibration/calibration_pairs.csv")
s, r = df["sensor_c"].to_numpy(), df["thermometer_c"].to_numpy()
df["error_before"] = r - s
df
"""))

cells.append(md("## Offset model (primary)"))
cells.append(code("""\
def mae(e):  return np.mean(np.abs(e))
def rmse(e): return np.sqrt(np.mean(e ** 2))

b = np.mean(r - s)
after = r - (s + b)
print(f"Offset b = {b:+.2f} C  (the sensor reads {b:.2f} C low on average)")
print(f"Before: MAE = {mae(r - s):.3f} C   RMSE = {rmse(r - s):.3f} C")
print(f"After : MAE = {mae(after):.3f} C   RMSE = {rmse(after):.3f} C")
print(f"MAE reduced by {(1 - mae(after)/mae(r - s))*100:.0f}%, RMSE by {(1 - rmse(after)/rmse(r - s))*100:.0f}%")
"""))

cells.append(md("## Linear model (needs more points to be reliable)"))
cells.append(code("""\
a, c = np.polyfit(s, r, 1)
print(f"Two-point line: T_cal = {a:.3f} * T_sensor + {c:.3f}")
print("Exact fit through both points -> residuals are zero by construction, not a measure of accuracy.")
"""))

cells.append(md("## Plot"))
cells.append(code("""\
fig, ax = plt.subplots(figsize=(6, 4.5))
lo, hi = min(s.min(), r.min()) - 1.5, max(s.max(), r.max()) + 1.5
x = np.linspace(lo, hi, 50)
ax.plot(x, x, "--", color="gray", lw=1, label="y = x (no error)")
ax.plot(x, x + b, color="crimson", lw=1.5, label=f"offset model: y = x {b:+.2f}")
ax.scatter(s, r, zorder=3, label="measured pairs")
ax.set_xlabel("Prototype sensor reading (°C)")
ax.set_ylabel("Reference thermometer (°C)")
ax.set_title("Temperature calibration")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("../figures/calibration_fit.png", dpi=150)
plt.show()
"""))

write_notebook("calibration.ipynb", cells)
