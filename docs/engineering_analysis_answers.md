# Engineering analysis questions

**Q1. Major subsystems and their roles.**

Sensors provide environmental signals. The controller acquires and processes them, local indicators provide warnings, serial communication exports observations and Python computes statistics and plots. ESP32 simulation and UNO prototype wiring and firmware are documented separately.

**Q2. Effective sampling rate.**

The supplied file cannot establish an effective rate because it has no timestamps. The ESP32 loop is nominally 1 Hz, with fresh DHT22 readings approximately every two seconds. The UNO loop includes blocking delays and processing, so its counter cannot be assumed to equal elapsed seconds.

**Q3. Greatest variability.**

The supplied light channel spans 15.08–100.00%, with standard deviation 18.860 percentage points. Temperature spans 26.0–29.0 °C, with standard deviation 0.874 °C; reported humidity spans 46.0–47.5%, with standard deviation 0.245 percentage points. These describe within-channel spread. Standard deviations with different units are not a direct ranking of sensor noise.

**Q4–Q5. Systematic error revealed by calibration; change in MAE and RMSE.**

The two supplied calibration pairs show the prototype reading 1.2 and 0.7 °C below the reference. Their fitted +0.95 °C offset reduces same-pair MAE from 0.950 to 0.250 °C and RMSE from 0.982 to 0.250 °C. More points and held-out reference readings are needed to assess accuracy beyond those fitting pairs.

**Q6. Effect of filtering.**

Over the 716 samples with complete averaging windows, recorded-temperature standard deviation is 0.874 °C, compared with 0.395 °C after additional averaging. This demonstrates smoothing of the supplied sequence, not an isolated measurement of noise rejection. A five-sample average retains earlier readings and introduces response lag. Seconds of delay cannot be measured without timestamps.

**Q7. Edge vs. transmitted information.**

Immediate validity checks, conversion, calibration, filtering and alarm decisions should run locally. A deployed system can transmit periodic summaries and event records, while retaining selected raw and validity data for diagnosis. The current prototype exports serial rows and does not implement a wireless link.

**Q8. Energy if every raw sample were transmitted.**

Frequent wireless transmissions can increase radio energy and network traffic. For illustration, 50 bytes per row at 1 Hz is 4.32 MB/day; one such row every five seconds is 0.864 MB/day before protocol overhead. These are assumed data-volume calculations, not measured packet sizes or battery-life results for this serial-only recording.
