# Engineering Analysis Questions (Section 8.1)

Answered against the real Wokwi capture in `data/raw/wokwi_serial_log.csv`
(723 rows, ~12 minutes, 0 invalid readings, 90 detected events).

1. **Major subsystems and their roles.** The ESP32 is the controller: it runs
   the sampling loop, validation, calibration, filtering, and decision logic.
   The DHT22 handles temperature/humidity sensing, the photoresistor (with
   its voltage divider) handles light sensing, and the PIR handles motion
   sensing. The LED is a local visual status indicator (`status == HIGH_TEMP`),
   the buzzer is a local audible event indicator (`motion == 1`), and the
   serial/USB link carries the processed rows out for Python analysis.

2. **Effective sampling rate of each sensor.** All three are read in the same
   loop, once per second — 1 Hz for all of them. Confirmed by the capture:
   723 rows over 722 seconds, sample counter incrementing by exactly 1 each
   row, no missed or duplicated samples.

3. **Which sensor showed the greatest variability, and why.** Temperature:
   std ≈ 12.1°C, range -5.8°C to 60.8°C — by far the largest, because the
   slider was deliberately swung to extremes to exercise the `HIGH_TEMP`
   logic. Light: std ≈ 0.20 (0-1 scale), moderate, from deliberate sweeps.
   Humidity: std = 0.0 (flat at 40% the whole run) — an artifact of this test
   run (the humidity slider was never touched), not a real sensor property.

4-5. **What did calibration reveal? Did it reduce MAE/RMSE?** Pending —
   `tempCalSlope`/`tempCalOffset` are still placeholders (1.0 / 0.0); no
   paired sensor-vs-reference-instrument readings exist yet from the real
   hardware build. `python/calibration.ipynb` is ready to fit the line and
   compute before/after MAE/RMSE as soon as that data exists.

6. **Effect of filtering on noise and responsiveness.** The 5-sample moving
   average (`temp_ma`) smooths the sharp, step-like jumps from slider moves,
   taking ~5 seconds to catch up after each change. Wokwi's simulated sensor
   adds no random jitter, so here the filter mainly rounded off deliberate
   step changes rather than suppressing noise; on real hardware, with genuine
   DHT22 sample-to-sample jitter, the same filter would smooth that too, at
   the same few-second lag cost.

7. **What should be processed locally vs. transmitted?** Locally: sampling,
   plausibility checks, calibration, moving average, rate-of-change, and the
   threshold decision — cheap arithmetic, and it catches bad readings before
   they'd ever need to be sent. Transmitted: the cleaned, decision-ready row
   (calibrated value, filtered value, status, motion flag) rather than raw
   sensor counts.

8. **Effect on energy if every raw measurement were transmitted.** Radio
   transmission is typically the most power-hungry operation on a
   microcontroller. Transmitting every 1 Hz raw reading instead of a
   filtered/reduced summary would key up the radio far more often, draining
   a battery-powered node faster and adding unnecessary network traffic —
   the core argument for doing edge processing at all.
