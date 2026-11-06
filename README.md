# WSN Lab 1: Multi-Sensor Edge Node

Updated 6 November 2026. Soroti University, WSN2100.

The project contains an ESP32 Wokwi simulation, an Arduino UNO R4 WiFi prototype,
and Python analysis of the supplied 720-row Arduino CSV. The report preserves the
original university cover, authors, section order, tables and figure numbering.

GitHub repository: https://github.com/davis-twinomugisha/wsn_lab1

Wokwi simulation: https://wokwi.com/projects/476121306266761217

## Primary recording and results

The active source is `data/raw/sensor_data_light_regimes_720rows.csv`.
Its 720 rows and original columns are unchanged. The synthetic light variant generated
separately during development is not part of the primary measurement results.

| Channel | Count | Mean | Minimum | Maximum | Sample standard deviation |
|---|---:|---:|---:|---:|---:|
| Temperature (C) | 720 | 27.473 | 26.000 | 29.000 | 0.874 |
| Reported humidity (%) | 720 | 46.796 | 46.000 | 47.500 | 0.245 |
| Light (%) | 720 | 87.911 | 15.080 | 100.000 | 18.860 |

- No missing source cells or rows flagged by the applied numeric/range checks.
- One identical row is retained. Identical readings do not establish duplicate logging.
- Source labels: 235 TEMP_HIGH samples in 160 runs, including one already active at capture start.
- Motion: 211 positive samples in 139 runs.
- Source-label overlap: 52 rows with both conditions and 394 unique rows with either condition.
- Reconstructed printed-temperature >28 C: 215 samples in 155 runs. None exceed 30 C.
- Twenty source TEMP_HIGH rows print exactly 28.0 C. Rounding or other device logic may
  explain the boundary differences. Source labels remain unchanged.

There are no timestamps. Measured duration, effective sampling rate, dropped samples,
latency and a five-minute stable baseline cannot be established from this file.
At an explicitly assumed one-second interval the first-to-last span would be 719 seconds.
Default plots therefore use sample number. No timestamp column is invented.

The prototype code estimates humidity from temperature. The supplied CSV alone does not
establish an independently measured humidity channel. It also does not retain original raw
or unfiltered temperature. The comparison graph is recorded temperature versus an additional
five-sample average, not a reconstruction of missing raw readings. No second calibration
offset is added to the recording.

## Repository structure

- `firmware/sensor_node/`: original ESP32 simulation sketch, wiring and library list.
- `firmware/uno_r4_prototype/`: original physical prototype sketch, including +0.95 C offset.
- `python/`: acquisition instructions, analysis, Colab and calibration notebooks and builders.
- `data/raw/`: primary 720-row recording and the earlier Wokwi/synthetic reference files.
- `data/processed/`: preserved source columns, derived features, statistics and summaries.
- `data/calibration/`: the two supplied sensor/reference thermometer pairs.
- `figures/`: five updated sensor plots and calibration fit.
- `figures/archive/wokwi/`: plots from the earlier simulation analysis.
- `docs/lab_report.pdf` and `docs/lab_report.docx`: updated final report.
- `docs/archive/`: prior report versions from the uploaded repository.
- `docs/SUBMISSION_STATUS.md`: mapping to the guide's submission requirements.

## Reproduce the results

From the repository root:

```bash
python -m pip install -r requirements.txt
python python/reproduce.py
python python/build_acquisition_nb.py
python docs/build_report_content.py
```

Alternatively, open `python/analysis.ipynb` in Jupyter and run all cells in order.
The saved notebook includes actual executed results and plot outputs.
`python/analysis_colab.ipynb` supports uploading the original CSV into Google Colab.

The analysis performs finite/range checks, five-sample trailing averaging, consecutive
sample differences, a rolling temperature standard deviation, threshold reconstruction,
status consistency checks and separate sample/run event counts. The first four averaging
outputs remain blank until five samples are available. Invalid rows would remain in the
processed file. IMU features are unavailable because no IMU channels were supplied.

## Build the report in its original format

The DOCX builder requires Node.js and the `docx` dependency declared in `docs/package.json`.
LibreOffice and Poppler are needed for PDF export and the table-of-contents page pass.

```bash
npm --prefix docs install
node docs/build_report_docx.js docs/_toc_pages.json
libreoffice --headless --convert-to pdf --outdir docs docs/lab_report.docx
```

After a layout change, run `python toc_pass.py` from `docs/`, rebuild with the generated
`docs/_toc_pages.json`, and export again. The report content comes from
`docs/build_report_content.py` and the computed summary, rather than old hardcoded statistics.

## Sensor interfaces

| Channel | ESP32 simulation | UNO R4 prototype |
|---|---|---|
| Temperature | DHT22, GPIO4 | KY-028 AO, A0 |
| Humidity | DHT22, GPIO4 | Estimated from temperature |
| Light | Photoresistor AO, GPIO34 | LDR divider, A1 |
| Motion | PIR, GPIO27 | PIR, D7 |
| Red LED | GPIO26 through 220 ohm resistor | D2 |
| Buzzer | GPIO25 | D8 |

The ESP32 uses a nominal one-second schedule with fresh DHT22 values approximately every
two seconds. Its temperature alarm has a 28.0/27.5 C hysteresis band. The UNO sketch uses
blocking delays, lacks that hysteresis and activates a continuous buzzer for high temperature
or a short pulse for motion. Their firmware behavior must not be described as identical.
Both original sketches are retained unchanged in this update.

## Calibration

The supplied pairs are 28.1/29.3 C and 32.3/33.0 C (sensor/reference).
The fitted offset is +0.95 C. On those same fitting pairs, MAE changes from 0.950 to
0.250 C and RMSE from 0.982 to 0.250 C. These are fitting residuals, not independently
validated accuracy. A two-point linear fit has zero residual by construction.
Extend the range and evaluate additional independent reference readings.

## Capture a new log with host receipt timestamps

Close Arduino Serial Monitor, connect the board and run:

```bash
python python/capture_serial.py --port COM6 --rows 600
```

Replace COM6 with the connected serial port. Reset the board after capture begins to emit
its header. The helper adds `host_elapsed_s` and retains a supplied device counter as
`device_counter`. Host receipt times include serial and host scheduling delays.
This helper has not been run against hardware during preparation of this update.
The primary notebook remains configured for the original timestamp-free CSV.

## Archived datasets

`wokwi_serial_log.csv` is the earlier 723-row simulation capture. `sample_serial_log.csv`
is the earlier 650-row synthetic reference dataset. Neither supplies the current reported
statistics. Their provenance is preserved in `data/raw/DATA_PROVENANCE.md`.
