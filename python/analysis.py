# %%
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

filename = 'sensor_data_light_regimes_720rows.csv'
candidates = [Path.cwd(), Path.cwd().parent]
if '__file__' in globals():
    candidates.insert(0, Path(__file__).resolve().parents[1])
ROOT = next((p for p in candidates if (p / 'data/raw' / filename).exists()), None)
if ROOT is None:
    raise FileNotFoundError('Extract the full ZIP, then open python/analysis.ipynb.')
RAW_PATH = ROOT / 'data/raw' / filename
FIG_DIR = ROOT / 'figures'
OUT_DIR = ROOT / 'data/processed'
FIG_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)
WINDOW = 5
HIGH_THRESHOLD_C = 28.0  # device configuration, not the guide's illustrative 30 C
SAMPLE_INTERVAL_S = None  # no time interval has been verified

source = pd.read_csv(RAW_PATH)
expected = ['temperature', 'humidity', 'light_pct', 'motion', 'temp_status', 'motion_status']
if not set(expected).issubset(source.columns):
    raise ValueError('Unexpected source columns; review the mapping before proceeding.')
d = source.copy(deep=True)
d.insert(0, 'sample_number', np.arange(1, len(d) + 1))
print('Observations:', len(d))
print('Original source SHA-256:', hashlib.sha256(RAW_PATH.read_bytes()).hexdigest())
print(source.head().to_string(index=False))

# %%
numeric = d[['temperature', 'humidity', 'light_pct', 'motion']].apply(pd.to_numeric, errors='coerce')
valid_temp = np.isfinite(numeric.temperature) & numeric.temperature.ne(-999)
valid_humidity = np.isfinite(numeric.humidity) & numeric.humidity.between(0, 100)
valid_light = np.isfinite(numeric.light_pct) & numeric.light_pct.between(0, 100)
valid_motion = numeric.motion.isin([0, 1])
valid = valid_temp & valid_humidity & valid_light & valid_motion
d['passes_numeric_range_checks'] = valid
temperature = numeric.temperature.where(valid_temp)
d['temperature_ma5'] = temperature.rolling(WINDOW, min_periods=WINDOW).mean()
d['temperature_change_per_sample'] = temperature.diff()
d['temperature_ma5_change_per_sample'] = d.temperature_ma5.diff()
d['temperature_std5'] = temperature.rolling(WINDOW, min_periods=WINDOW).std(ddof=1)
d['high_temperature_28c'] = pd.Series(pd.NA, index=d.index, dtype='boolean')
d.loc[valid_temp, 'high_temperature_28c'] = temperature.loc[valid_temp].gt(HIGH_THRESHOLD_C)
d['high_temperature_ma5_28c'] = pd.Series(pd.NA, index=d.index, dtype='boolean')
ready = d.temperature_ma5.notna()
d.loc[ready, 'high_temperature_ma5_28c'] = d.loc[ready, 'temperature_ma5'].gt(HIGH_THRESHOLD_C)

motion = numeric.motion.where(valid_motion)
high = d.high_temperature_28c
d['new_motion_event'] = motion.eq(1) & motion.shift().eq(0)
d['new_high_temperature_event'] = (high.eq(True) & high.shift().eq(False)).fillna(False)
motion_run_starts = motion.eq(1) & ~motion.shift().eq(1)
high_run_starts = high.eq(True) & ~high.shift(fill_value=False).eq(True)

if SAMPLE_INTERVAL_S is not None:
    if SAMPLE_INTERVAL_S <= 0:
        raise ValueError('Sample interval must be positive.')
    d['estimated_time_s'] = (d.sample_number - 1) * SAMPLE_INTERVAL_S
    d['temperature_change_per_second_assumed_interval'] = d.temperature_change_per_sample / SAMPLE_INTERVAL_S

print(d[['sample_number', 'temperature', 'temperature_ma5',
         'temperature_change_per_sample', 'high_temperature_28c']].head(10).to_string(index=False))
print('IMU feature: unavailable, no IMU channels supplied.')

# %%
statistics = numeric[['temperature', 'humidity', 'light_pct']].agg(['count', 'mean', 'min', 'max', 'std']).T
statistics.index.name = 'channel'
expected_temp = pd.Series(np.where(numeric.temperature > 28, 'TEMP_HIGH',
                         np.where(numeric.temperature < 18, 'TEMP_LOW', 'TEMP_NORMAL')), index=d.index)
expected_motion = pd.Series(np.where(motion.eq(1), 'MOTION_DETECTED', 'NO_MOTION'), index=d.index)
summary = {
    'source_file': filename,
    'observations': len(d),
    'meets_600_row_minimum': len(d) >= 600,
    'missing_source_cells': int(source.isna().sum().sum()),
    'rows_flagged_by_numeric_range_checks': int((~valid).sum()),
    'identical_source_rows_retained': int(source.duplicated().sum()),
    'measured_duration_seconds': None,
    'duration_if_one_second_interval_seconds': len(d) - 1,
    'motion_positive_samples': int(motion.eq(1).sum()),
    'motion_runs_observed': int(motion_run_starts.sum()),
    'new_motion_rising_edges': int(d.new_motion_event.sum()),
    'high_temperature_samples_above_28c': int(high.sum()),
    'high_temperature_runs_observed': int(high_run_starts.sum()),
    'high_temperature_active_at_first_sample': bool(high.iloc[0]),
    'new_high_temperature_rising_edges': int(d.new_high_temperature_event.sum()),
    'samples_above_30c': int(temperature.gt(30).sum()),
    'samples_with_motion_and_high_temperature': int((motion.eq(1) & high.fillna(False)).sum()),
    'samples_with_either_condition': int((motion.eq(1) | high.fillna(False)).sum()),
    'temperature_status_mismatches_at_28c_18c': int(source.temp_status.ne(expected_temp).sum()),
    'motion_status_mismatches': int(source.motion_status.ne(expected_motion).sum()),
    'source_labelled_high_temperature_samples': int(source.temp_status.eq('TEMP_HIGH').sum()),
    'source_labelled_high_temperature_runs': int((source.temp_status.eq('TEMP_HIGH') & ~source.temp_status.shift().eq('TEMP_HIGH')).sum()),
    'printed_28c_rows_labelled_high': int((numeric.temperature.eq(28) & source.temp_status.eq('TEMP_HIGH')).sum()),
    'ma5_warmup_samples': int(d.temperature_ma5.iloc[:WINDOW-1].isna().sum()),
    'assumed_sample_interval_seconds': SAMPLE_INTERVAL_S,
}
statistics.to_csv(OUT_DIR / 'descriptive_statistics.csv', float_format='%.6f')
d.to_csv(OUT_DIR / 'sensor_data_processed.csv', index=False, float_format='%.6f')
(OUT_DIR / 'summary.json').write_text(json.dumps(summary, indent=2))
print(statistics.round(4).to_string())
print(json.dumps(summary, indent=2))
print('Measured duration is unknown. At an assumed 1 Hz, the first-to-last span would be', len(d)-1, 'seconds.')
print('Source TEMP_HIGH labels:', summary['source_labelled_high_temperature_samples'])
print('Labels at printed 28.0 C:', summary['printed_28c_rows_labelled_high'])
print('Rounding or unlogged logic may explain boundary disagreements.')
source_high = source.temp_status.eq('TEMP_HIGH')
summary['source_labelled_high_temperature_new_edges'] = int((source_high & source_high.shift().eq(False)).sum())
summary['source_labelled_high_and_motion_samples'] = int((source_high & motion.eq(1)).sum())
summary['source_labelled_high_or_motion_samples'] = int((source_high | motion.eq(1)).sum())
summary['recorded_temperature_std_on_ma5_rows'] = float(temperature[d.temperature_ma5.notna()].std(ddof=1))
summary['additional_ma5_temperature_std'] = float(d.temperature_ma5.std(ddof=1))
summary['statistics'] = statistics.to_dict(orient='index')
summary['source_sha256'] = hashlib.sha256(RAW_PATH.read_bytes()).hexdigest()
summary['analysis_date'] = '6 November 2026'
summary['measured_duration_seconds'] = None
(OUT_DIR / 'report_summary.json').write_text(json.dumps(summary, indent=2))
d.to_csv(OUT_DIR / 'cleaned_log.csv', index=False, float_format='%.6f')


# %%
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10,
                     'axes.titlesize':15, 'axes.labelsize':11})
x = d.sample_number if SAMPLE_INTERVAL_S is None else d.estimated_time_s
xlabel = 'Sample number' if SAMPLE_INTERVAL_S is None else 'Estimated time (s)'
def setup_plot(title, ylabel):
    fig, ax = plt.subplots(figsize=(10.5, 3.6), dpi=160)
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=0.2)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlim(float(x.iloc[0]), float(x.iloc[-1]))
    return fig, ax
def save_plot(fig, name):
    fig.tight_layout()
    fig.savefig(FIG_DIR / name, dpi=200)
    plt.show()
    plt.close(fig)

fig, ax = setup_plot('Temperature', 'Temperature (°C)')
ax.plot(x, numeric.temperature, color='#126b98', lw=1.1, label='Recorded temperature')
ax.axhline(HIGH_THRESHOLD_C, color='#bc4b37', ls='--', lw=1, label='28°C threshold')
ax.legend(frameon=False, fontsize=9)
save_plot(fig, 'temp_vs_time.png')

fig, ax = setup_plot('Humidity', 'Humidity (%)')
ax.plot(x, numeric.humidity, color='#168277', lw=1.1, label='Humidity')
ax.legend(frameon=False)
save_plot(fig, 'humidity_vs_time.png')

fig, ax = setup_plot('Recorded vs filtered temperature', 'Temperature (°C)')
ax.plot(x, numeric.temperature, color='#8eafc3', lw=0.9, alpha=0.8, label='Recorded')
ax.plot(x, d.temperature_ma5, color='#d97627', lw=1.6, label='Additional 5-sample average')
ax.legend(frameon=False, fontsize=9)
save_plot(fig, 'raw_vs_filtered_temp.png')

fig, ax = setup_plot('Light', 'Light (%)')
ax.plot(x, numeric.light_pct, color='#b17d19', lw=1.1, label='Supplied light')
ax.set_ylim(0, 102)
ax.legend(frameon=False)
save_plot(fig, 'light_vs_time.png')

fig, ax = setup_plot('Motion', 'Motion')
ax.step(x, motion, where='post', color='#4b7d45', lw=0.9)
ax.fill_between(x, motion, step='post', color='#72a168', alpha=0.25)
ax.set_yticks([0, 1])
ax.set_ylim(-0.08, 1.15)
save_plot(fig, 'motion_events.png')