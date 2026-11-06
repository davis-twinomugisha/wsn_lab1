# Dataset provenance

| File | Role | Used for current report statistics |
|---|---|---|
| sensor_data_light_regimes_720rows.csv | User-supplied Arduino recording, 720 rows, no timestamps | Yes |
| wokwi_serial_log.csv | Archived Wokwi simulation, 723 rows | No |
| wokwi_serial_dump.txt | Original text dump of that Wokwi run | No |
| sample_serial_log.csv | Synthetic reference example, 650 rows | No |

The primary file is copied byte-for-byte from the supplied attachment. No generated light
variant is used in the current report. Source rows are not padded, deduplicated or timestamped
retrospectively. The previous 145-row file is not merged into the latest 720-row recording.

Primary SHA-256: 061a05d9a00fc9fac238ebe99a821b1414c165688bdb97f2ea7ccf1ff4ecef9f
