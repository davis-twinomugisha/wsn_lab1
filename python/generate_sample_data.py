"""
Generates a synthetic serial-log CSV that mirrors EXACTLY what sensor_node.ino
streams over Serial (same columns, same on-device processing logic). This is
a stand-in dataset so the acquisition/analysis notebooks can be built and
verified end-to-end before real Wokwi or hardware data has been captured.

Once you have a real capture (from Wokwi's serial monitor log, or from the
real ESP32 via acquisition.ipynb), just point analysis.ipynb at that file
instead -- nothing else about the pipeline changes.

Timeline simulated (~650 seconds ~= 10.8 minutes, satisfies the >=5 min
baseline and >=600 row requirements from the lab guide):
  0-300s   : stable baseline (Section 6, step 4)
  300-420s : LDR characterization -- dark -> normal -> bright (Section 7.1)
  420-480s : temperature nudged above 30C to trigger HIGH_TEMP (Section 7.1/7.2)
  480-650s : a handful of PIR motion events + a few invalid/NaN glitches
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N = 650  # seconds / samples at 1 Hz
t = np.arange(1, N + 1)

# ---------------- Raw temperature (deg C) ----------------
temp_raw = np.full(N, 24.5)
temp_raw += rng.normal(0, 0.15, N)                      # sensor noise
temp_raw += 0.003 * t                                    # slow warm-up drift
# nudge above 30 during the "controlled change" window
high_temp_mask = (t >= 420) & (t < 480)
temp_raw[high_temp_mask] += np.linspace(0, 8, high_temp_mask.sum())
temp_raw[t >= 480] += 6.0  # stays elevated briefly, then decays back toward baseline
post_spike = t >= 480
decay = np.exp(-(t[post_spike] - 480) / 40.0)
temp_raw[post_spike] = 24.8 + (temp_raw[479] - 24.8) * decay + rng.normal(0, 0.15, post_spike.sum())

# ---------------- Humidity (%) -- loosely inverse to temperature ----------------
humidity = 62 - (temp_raw - 24.5) * 1.1 + rng.normal(0, 0.6, N)
humidity = np.clip(humidity, 30, 90)

# ---------------- Light, normalized 0-1 ----------------
light = np.full(N, 0.45)
ldr_mask = (t >= 300) & (t < 420)
# dark -> normal -> bright sweep
ldr_phase = np.linspace(0, 1, ldr_mask.sum())
light[ldr_mask] = np.where(ldr_phase < 0.5, 0.03 + ldr_phase, 0.9)
light += rng.normal(0, 0.01, N)
light = np.clip(light, 0, 1)

# ---------------- Motion, digital 0/1 ----------------
motion = np.zeros(N, dtype=int)
event_starts = [140, 500, 512, 560, 610]
for s in event_starts:
    dur = rng.integers(3, 7)
    motion[s:s + dur] = 1

# ---------------- Inject a few invalid/NaN glitches (sensor read failures) ----------------
glitch_idx = rng.choice(np.arange(50, N - 1), size=6, replace=False)
temp_raw_glitched = temp_raw.copy()
humidity_glitched = humidity.copy()
temp_raw_glitched[glitch_idx] = np.nan
humidity_glitched[glitch_idx] = np.nan

# ---------------- Reproduce the firmware's exact on-device processing ----------------
TEMP_CAL_SLOPE, TEMP_CAL_OFFSET = 1.0, 0.0
MA_WINDOW = 5

rows = []
ma_buffer = []
last_cal_temp = np.nan
event_count = 0

for i in range(N):
    tr = temp_raw_glitched[i]
    hu = humidity_glitched[i]
    li = light[i]
    mo = int(motion[i])

    valid = not (np.isnan(tr) or np.isnan(hu)) and (-40 <= tr <= 80) and (0 <= hu <= 100) and (0 <= li <= 1)

    temp_cal = tr * TEMP_CAL_SLOPE + TEMP_CAL_OFFSET if valid else np.nan

    ma_input = temp_cal if valid else (ma_buffer[-1] if ma_buffer else 0.0)
    ma_buffer.append(ma_input)
    if len(ma_buffer) > MA_WINDOW:
        ma_buffer.pop(0)
    temp_ma = float(np.mean(ma_buffer))

    temp_roc = 0.0 if np.isnan(last_cal_temp) else (temp_cal - last_cal_temp if valid else 0.0)
    if valid:
        last_cal_temp = temp_cal

    if not valid:
        status = "INVALID"
    elif temp_cal > 30.0:
        status = "HIGH_TEMP"
        event_count += 1
    else:
        status = "NORMAL"
    if mo == 1:
        event_count += 1

    rows.append({
        "sample": i + 1,
        "temp_raw": round(tr, 2) if valid else "",
        "humidity": round(hu, 2) if valid else "",
        "light": round(li, 3),
        "motion": mo,
        "temp_cal": round(temp_cal, 2) if valid else "",
        "temp_ma": round(temp_ma, 2),
        "temp_roc": round(temp_roc, 2),
        "status": status,
        "valid": int(valid),
    })

df = pd.DataFrame(rows)
out_path = "../data/raw/sample_serial_log.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df)} rows to {out_path}")
print(df.head())
print("\nStatus counts:\n", df["status"].value_counts())
print("\nInvalid rows:", (df["valid"] == 0).sum())
print("Motion-high rows:", (df["motion"] == 1).sum())
