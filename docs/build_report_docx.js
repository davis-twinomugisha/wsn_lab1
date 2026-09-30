// Builds docs/lab_report.docx in the team's Soroti University report format.
// Usage: node build_report_docx.js [toc_pages.json]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  AlignmentType, WidthType, BorderStyle, Footer, PageNumber, NumberFormat,
  PageBreak, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo,
  PositionalTabLeader, TabStopType, ShadingType, VerticalAlign,
} = require("docx");

const HERE = __dirname;
const ROOT = path.join(HERE, "..");
const tocPages = fs.existsSync(process.argv[2] || "") ? JSON.parse(fs.readFileSync(process.argv[2])) : {};

const FONT = "Times New Roman";
const BODY = 24;      // 12 pt (half-points)
const SMALL = 20;     // 10 pt
const LINE = 360;     // 1.5 line spacing
const CONTENT_W = 9026; // A4 width minus 2.54 cm margins, in DXA

// ---------- helpers ----------
const run = (text, o = {}) => new TextRun({ text, font: FONT, size: o.size || BODY, bold: o.bold, italics: o.italics, highlight: o.highlight });

// P("plain text") or P([["Bold label: ", true], "plain text"])
function P(content, o = {}) {
  const parts = Array.isArray(content) ? content : [content];
  const children = parts.map(p => Array.isArray(p) ? run(p[0], { bold: p[1], size: o.size }) : run(p, { size: o.size, italics: o.italics }));
  return new Paragraph({
    children,
    alignment: o.align || AlignmentType.JUSTIFIED,
    spacing: { after: o.after ?? 120, line: o.line ?? LINE },
    indent: o.indent,
    keepNext: o.keepNext,
  });
}

const sections = []; // [number, title] for the TOC
function H(num, title) {
  sections.push([num, title]);
  return new Paragraph({
    children: [run(num ? `${num} ${title}` : title, { bold: true, size: 26 })],
    spacing: { before: 200, after: 120 },
    keepNext: true,
  });
}

function IMG(file, widthIn, caption) {
  const full = path.join(ROOT, file);
  const [w, h] = sizes[file];
  const widthPx = widthIn * 96;
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120, after: 60 },
      keepNext: true,
      children: [new ImageRun({ type: "png", data: fs.readFileSync(full),
        transformation: { width: widthPx, height: widthPx * h / w } })],
    }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
      children: [run(caption, { size: SMALL })] }),
  ];
}

const sizes = {
  "docs/soroti_logo.png": [340, 250],
  "docs/system_architecture.png": [1979, 619],
  "docs/circuit_diagram.png": [2067, 1649],
  "figures/calibration_fit.png": [900, 675],
  "figures/temp_vs_time.png": [1350, 525],
  "figures/humidity_vs_time.png": [1350, 525],
  "figures/raw_vs_filtered_temp.png": [1350, 525],
  "figures/light_vs_time.png": [1350, 525],
  "figures/motion_events.png": [1350, 390],
};

const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };
function TABLE(widths, rows, caption) {
  const total = widths.reduce((a, b) => a + b, 0);
  const t = new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0, cantSplit: true,
      children: r.map((c, ci) => new TableCell({
        borders,
        width: { size: widths[ci], type: WidthType.DXA },
        margins: { top: 40, bottom: 40, left: 80, right: 80 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({ spacing: { after: 0, line: 240 }, keepNext: ri < rows.length - 1,
          children: [run(c, { size: SMALL, bold: ri === 0 })] })],
      })),
    })),
  });
  const cap = new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 200 },
    children: [run(caption, { size: SMALL })] });
  return [t, cap];
}

// ---------- cover ----------
const center = (text, o = {}) => new Paragraph({ alignment: AlignmentType.CENTER,
  spacing: { after: o.after ?? 0, before: o.before ?? 0, line: o.line ?? 276 },
  children: [run(text, { bold: o.bold, italics: o.italics, size: o.size || BODY })] });

const cover = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1200, after: 360 },
    children: [new ImageRun({ type: "png", data: fs.readFileSync(path.join(HERE, "soroti_logo.png")),
      transformation: { width: 122, height: 90 } })] }),
  center("SOROTI UNIVERSITY", { bold: true, size: 26 }),
  center("SCHOOL OF ENGINEERING AND TECHNOLOGY", { bold: true, size: 26 }),
  center("DEPARTMENT OF ELECTRONICS AND COMPUTER", { bold: true, size: 26 }),
  center("ENGINEERING", { bold: true, size: 26, after: 360 }),
  center("DESIGN, IMPLEMENTATION AND CALIBRATION OF A", { bold: true, size: 28 }),
  center("MULTI-SENSOR EDGE NODE", { bold: true, size: 28, after: 300 }),
  center("WSN2100 — WIRELESS SENSOR NETWORKS", { bold: true, after: 300 }),
  center("Laboratory 1: Technical Report", { italics: true, after: 160 }),
  center("Submitted by", { italics: true, after: 200 }),
  center("DAVIS TWINOMUGISHA", { bold: true }),
  center("SARAH ASINGWIIRE", { bold: true }),
  center("OPUCHE SAMSON", { bold: true }),
  center("PHILLIP OKWANY", { bold: true, after: 360 }),
  center("in partial fulfilment of the requirements for the degree of", { italics: true, after: 120 }),
  center("BACHELOR OF ENGINEERING IN ELECTRONICS AND COMPUTER", { bold: true }),
  center("ENGINEERING", { bold: true, after: 360 }),
  center("SEPTEMBER 2026", { bold: true }),
];

// ---------- body ----------
const body = [];
const add = (...xs) => xs.flat().forEach(x => body.push(x));

add(H(1, "OBJECTIVE AND COMPETENCY"));
add(P("The objective of this laboratory is to design, implement and validate a low-cost sensing node that acquires measurements from several sensors, rejects invalid values, processes data locally, makes a simple edge decision and streams machine-readable data for analysis in Python, as a foundation for later IoT analytics and machine-learning work. The node targets a smart-building or environmental-monitoring scenario in a resource-constrained setting."));
add(P([["Competencies demonstrated: ", true], "programming an ESP32-class microcontroller; interfacing three sensing modalities over digital (single-wire, GPIO) and analog (ADC) interfaces; acquiring, timestamping and validating measurements; local filtering and feature calculation; generating a structured data stream; characterizing sensor response and variability in Python; and documenting a reproducible design through a version-controlled repository."]));

add(H(2, "SYSTEM ARCHITECTURE AND HARDWARE"));
add(P("The node has five subsystems (Fig. 1). A sensing layer (DHT22 temperature/humidity sensor, photoresistor light module and PIR motion sensor) feeds an ESP32 DevKit V1, which runs the whole processing chain in firmware: 1 Hz sampling, plausibility validation, linear calibration, a moving-average filter with rate of change, and a threshold decision. A local indicator layer (red LED and buzzer) acts on that decision without a host computer, and a serial CSV stream carries every processed sample to a Python analysis layer. The design was built and validated in the Wokwi simulator [3]; the wiring is shown in Fig. 2."));
add(IMG("docs/system_architecture.png", 6.2, "Fig. 1. System architecture, from sensing layer to analysis layer."));
add(IMG("docs/circuit_diagram.png", 5.2, "Fig. 2. Circuit/wiring diagram of the simulated sensor node."));
add(P([["Physical prototype: ", true], "the hardware build uses an Arduino UNO R4 WiFi [8] with a KY-028 NTC thermistor module on A0, a two-pin LDR in a 10 k\u03a9 divider on A1, a PIR sensor on D7, a red LED on D2 and an active buzzer on D8 (firmware in firmware/uno_r4_prototype/). The prototype is fully assembled and operational, running the complete acquisition, filtering, threshold and actuation chain, and is presented in the live demonstration. Its temperature channel was calibrated against a reference thermometer (Section 5). The descriptive statistics, event counts and plots in Sections 4 and 6 are computed from the simulated node\u2019s dataset."]));

add(H(3, "SENSOR INTERFACES AND SAMPLING DESIGN"));
add(P("Each sensor uses the interface suited to its output (Table 1). All channels are read in a single loop scheduled with millis() at 1 Hz, as the guide recommends. The DHT22, however, specifies a minimum sampling period of 2 s [2], and the Adafruit DHT library returns its cached result when polled faster [4], so the effective rate of fresh temperature and humidity values is 0.5 Hz, while light and motion are genuinely sampled at 1 Hz. The light module is read through ADC1 on GPIO34 (12-bit, 0–4095), which remains usable when Wi-Fi is active."));
add(TABLE([2300, 2000, 2426, 2300], [
  ["Sensor / actuator", "Interface", "ESP32 pin", "Supply"],
  ["DHT22 (temperature, humidity)", "Digital, single-wire", "GPIO4", "3V3 / GND"],
  ["Photoresistor module (light)", "Analog (ADC1)", "GPIO34 (AO)", "3V3 / GND"],
  ["PIR motion sensor", "Digital input", "GPIO27", "3V3 / GND"],
  ["Red LED (HIGH_TEMP indicator)", "Digital output", "GPIO26 via 220 Ω", "GND"],
  ["Buzzer (motion alert)", "Digital output", "GPIO25", "GND"],
], "Table 1. Sensor interfaces and pin assignment."));
add(P("Every sample is emitted as one comma-separated line with a header row, containing the timestamp, raw temperature, humidity, light, motion, calibrated and filtered temperature, rate of change, status and a validity flag, so it can be parsed directly into a Pandas DataFrame."));

add(H(4, "SENSOR CHARACTERIZATION AND DATA QUALITY"));
add(P("The dataset was captured from the Wokwi simulation over 722 s (723 samples, above the 600-row minimum). Following Section 7.1 of the guide, each sensor was changed deliberately with its on-part control: the temperature slider was stepped through 17 levels between −5.8 °C and 60.8 °C, crossing the 30 °C threshold in use at the time in six separate episodes; the light slider was moved through 22 levels from dark (0.025) to bright (0.989, normalized); and the PIR was triggered in six separate motion episodes. Humidity was not varied in this run. Descriptive statistics are given in Table 2."));
add(TABLE([2426, 1320, 1320, 1320, 1320, 1320], [
  ["Channel", "Count", "Mean", "Min", "Max", "Std. dev."],
  ["Temperature (°C)", "723", "23.183", "−5.800", "60.800", "12.136"],
  ["Humidity (%)", "723", "40.000", "40.000", "40.000", "0.000"],
  ["Light (normalized 0–1)", "723", "0.423", "0.025", "0.989", "0.204"],
], "Table 2. Descriptive statistics of the simulated capture."));
add(P([["Data quality: ", true], "no samples failed validation (0 invalid), and the stream had no missing or duplicated samples. The simulated sensors are noise-free: during the undisturbed start of the run every channel had a standard deviation of zero, so the variability in Table 2 comes entirely from the controlled changes rather than from measurement noise, and the simulated sensor has no bias. On the prototype, calibration against the reference thermometer showed that the sensor reads about 0.95 \u00b0C low (Section 5). The simulated sensors respond within one sample to each change. The undisturbed baseline lasted 76 s, shorter than the five minutes the guide requires (Section 8). On the physical prototype, the saturated thermistor readings observed during the build were recorded and flagged rather than deleted, as the guide\u2019s good-practice rules require."]));

add(H(5, "EDGE PROCESSING AND LOCAL DECISION LOGIC"));
add(P("Four operations run on the ESP32 every sample. (i) Validation: a sample is valid only if the DHT22 returns numbers inside its datasheet range (−40 to 80 °C, 0–100 % RH) [2]. (ii) Calibration: T_cal = a·T_raw + b; on the prototype an offset correction (a = 1, b = +0.95 \u00b0C) derived below is applied, while the simulated node uses a = 1, b = 0 because its sensor has no bias. (iii) Filtering and features: a five-sample moving average of T_cal and the rate of change Δx = x(t) − x(t−1). (iv) Decision: status = HIGH_TEMP when the filtered temperature exceeds 28.0 °C, otherwise MOTION when the PIR is active, otherwise NORMAL; invalid samples are labelled INVALID."));
add(P("The decision drives the local indicators directly: the red LED lights while status is HIGH_TEMP and the buzzer sounds while motion is detected. The final firmware adds a 0.5 °C hysteresis band (the alarm clears only below 27.5 °C) so the indicators do not flicker when the temperature hovers at the threshold, and counts each high-temperature or motion episode once, at its start. The dataset in Section 4 was recorded with the previous firmware revision, which applied a 30 °C threshold to the calibrated (unfiltered) temperature, without hysteresis; the event counts in Sections 4 and 6 therefore refer to 30 °C. The IMU feature in item 4 of Section 7.2 was not implemented, as no IMU is fitted."));
add(P([["Calibration of the prototype: ", true], "the prototype\u2019s temperature reading was compared with a reference thermometer placed beside the sensor, recording both values once they had settled. Two paired readings were taken, at about 28 \u00b0C and 33 \u00b0C (Table 3). The sensor read low at both points, by 1.2 \u00b0C and 0.7 \u00b0C. An offset model T_cal = T_raw + b was fitted by least squares, giving b = +0.95 \u00b0C, which reduced the error against the thermometer from an MAE of 0.95 \u00b0C to 0.25 \u00b0C (\u221274 %) and an RMSE of 0.98 \u00b0C to 0.25 \u00b0C (\u221275 %) (Fig. 3). A full linear model through the two points (a = 0.881, b = +4.55 \u00b0C) fits both exactly, so its residual error is zero by construction and cannot be used to judge accuracy; the offset model was therefore adopted and applied in the prototype firmware as CAL_OFFSET = 0.95 \u00b0C. The data and fit are in data/calibration/ and python/calibration.ipynb."]));
add(TABLE([2256, 2256, 2257, 2257], [
  ["Point", "Prototype sensor (\u00b0C)", "Thermometer (\u00b0C)", "Error before (\u00b0C)"],
  ["1", "28.1", "29.3", "+1.2"],
  ["2", "32.3", "33.0", "+0.7"],
], "Table 3. Calibration pairs from the prototype and the reference thermometer."));
add(IMG("figures/calibration_fit.png", 4.2, "Fig. 3. Temperature calibration: measured pairs and the fitted offset model."));

add(H(6, "PYTHON DATA ANALYSIS AND VISUALIZATION"));
add(P("acquisition.ipynb reads the serial stream with pyserial on hardware, or parses a copied Wokwi Serial Monitor log into CSV. analysis.ipynb loads the CSV into a Pandas DataFrame [5], coerces invalid entries to NaN, computes the statistics required by Section 7.3 (count and duration, mean, minimum, maximum, standard deviation, invalid count and event count) and produces the plots in Figs. 4–8 with Matplotlib [6]. The processed dataset keeps invalid rows with their flag instead of dropping them. A Google Colab version of the notebook is also provided."));
add(P([["Results: ", true], "723 observations over 722 s (about 12 minutes); 0 invalid measurements; 90 event samples, made up of 60 HIGH_TEMP samples in 6 episodes and 30 motion samples in 6 episodes."]));
add(IMG("figures/temp_vs_time.png", 6.0, "Fig. 4. Temperature vs. time, with the 30 °C threshold used when this dataset was recorded."));
add(IMG("figures/humidity_vs_time.png", 6.0, "Fig. 5. Humidity vs. time (not varied in this run)."));
add(IMG("figures/raw_vs_filtered_temp.png", 6.0, "Fig. 6. Raw vs. filtered (five-sample moving average) temperature."));
add(IMG("figures/light_vs_time.png", 6.0, "Fig. 7. Light level vs. time during the dark-to-bright sweeps."));
add(IMG("figures/motion_events.png", 6.0, "Fig. 8. PIR motion events vs. time."));

add(H(7, "DISCUSSION AND ENGINEERING INTERPRETATION"));
const qa = [
  ["Q1. Major subsystems and their roles. ", "Sensing (DHT22, LDR module, PIR) converts the environment into signals; the ESP32 acquires, validates, calibrates, filters and decides; the LED and buzzer give the local status; the serial link carries the processed stream; and Python performs the offline analysis."],
  ["Q2. Effective sampling rate. ", "Light and motion: 1 Hz, confirmed by 723 samples in 722 s with no gaps. Temperature and humidity: 1 Hz nominal but 0.5 Hz effective, because the DHT22’s 2 s minimum period makes every second reading a cached value [2], [4]."],
  ["Q3. Greatest variability. ", "Temperature (standard deviation 12.1 °C), because it was driven through the widest controlled range to exercise the threshold logic. Humidity showed none, because it was not varied. In simulation this reflects the test protocol, not sensor noise."],
  ["Q4–Q5. Systematic error revealed by calibration; change in MAE and RMSE. ", "Calibration against the reference thermometer revealed a systematic negative bias: the prototype\u2019s temperature channel reads about 0.95 \u00b0C below the true temperature (1.2 \u00b0C at 28 \u00b0C and 0.7 \u00b0C at 33 \u00b0C). Applying the offset correction reduced the MAE from 0.95 \u00b0C to 0.25 \u00b0C (a 74 % reduction) and the RMSE from 0.98 \u00b0C to 0.25 \u00b0C (75 %). The shrinking error at the higher point suggests a small gain error as well, which more calibration points would quantify."],
  ["Q6. Effect of filtering. ", "The five-sample moving average smooths step changes but lags them: after each temperature step the filtered value took four samples (4 s) to come within 10 % of the new level (Fig. 6). The filter trades responsiveness for noise rejection; its noise benefit could not be measured here because the simulated signal has no noise."],
  ["Q7. Edge vs. transmitted information. ", "Validation, calibration, filtering and the threshold decision are cheap per-sample operations that also remove bad data at the source, so they belong at the edge. Only validated, calibrated summaries and events need to be transmitted, not every raw sample."],
  ["Q8. Energy if every raw sample were transmitted. ", "Each CSV row is about 50 bytes, so a 1 Hz stream is roughly 4.3 MB per day per node (0.9 MB at a 5 s interval). Radio transmission draws hundreds of milliamps on the ESP32, against tens of milliamps for computation [1], so streaming every raw sample keeps the radio busy and multiplies energy use. Sending summaries or events only is far cheaper."],
];
qa.forEach(([q, a]) => add(P([[q, true], a])));

add(H(8, "LIMITATIONS AND RECOMMENDED IMPROVEMENTS"));
[
  ["Simulated dataset: ", "the descriptive statistics and plots come from the Wokwi simulation, whose sensors are noise-free. Recommendation: log a long-term dataset from the prototype for the same analysis."],
  ["Prototype sensing: ", "the KY-028 has no humidity element, so the prototype’s humidity field is estimated from temperature; adding a DHT22 would provide measured humidity. Replacing the prototype’s empirical temperature scaling with the thermistor Beta equation before calibration would improve accuracy."],
  ["Baseline and humidity: ", "the undisturbed baseline was 76 s rather than five minutes, and humidity was not varied. Recommendation: recapture with the final firmware, with at least five minutes of baseline and a humidity sweep."],
  ["Calibration range: ", "only two calibration points were taken, over 28\u201333 \u00b0C, so the gain (slope) cannot be determined reliably and the offset correction is valid mainly within that range. Recommendation: add at least three more points across a wider range and refit the linear model."],
  ["Sampling vs. DHT22 limit: ", "polling at 1 Hz produces cached temperature and humidity values. Recommendation: sample the DHT22 at 0.5 Hz or flag repeated values."],
  ["Scope: ", "the IMU feature and the advanced challenge (local buffering, MQTT, sampling-interval study) were not attempted."],
].forEach(([l, t]) => add(P([[l, true], t])));

add(H(9, "CONCLUSION"));
add(P("The simulated node meets the laboratory’s functional requirements: three sensing modalities on digital and analog interfaces, plausibility validation, a calibrated temperature channel on the prototype (bias of 0.95 \u00b0C corrected, MAE reduced by 74 %), a moving-average filter and rate of change, a 28 °C threshold decision driving an LED and a buzzer, and a machine-readable stream analysed in Python with the required statistics and five plots. The prototype is fully assembled and operational and is shown in the live demonstration. Future work is to log a long-term dataset from the prototype, extend the calibration to more points over a wider range, and add a DHT22 for measured humidity."));

add(H(null, "REFERENCES"));
[
  "[1] Espressif Systems, “ESP32 Series Datasheet,” Espressif Systems. [Online]. Available: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf",
  "[2] Aosong Electronics, “Digital-output relative humidity & temperature sensor/module DHT22 (AM2302).” [Online]. Available: https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf",
  "[3] Wokwi, “Wokwi Docs: ESP32 simulation and parts reference.” [Online]. Available: https://docs.wokwi.com",
  "[4] Adafruit Industries, “DHT sensor library,” GitHub repository. [Online]. Available: https://github.com/adafruit/DHT-sensor-library",
  "[5] W. McKinney, “Data structures for statistical computing in Python,” in Proc. 9th Python in Science Conf. (SciPy 2010), 2010, pp. 56–61.",
  "[6] J. D. Hunter, “Matplotlib: A 2D graphics environment,” Computing in Science & Engineering, vol. 9, no. 3, pp. 90–95, 2007.",
  "[7] Soroti University, School of Engineering and Technology, “Wireless Sensor Networks, Laboratory Guide 1: Design, Implementation and Calibration of a Multi-Sensor Edge Node,” 2026.",
  "[8] Arduino, “UNO R4 WiFi,” Arduino Documentation. [Online]. Available: https://docs.arduino.cc/hardware/uno-r4-wifi",
].forEach(r => add(new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { after: 80, line: 276 },
  indent: { left: 400, hanging: 400 },
  children: [run(r, { size: 22 })],
})));

add(H(null, "APPENDIX: REPOSITORY LINK AND FILE STRUCTURE"));
add(new Paragraph({ spacing: { after: 120, line: LINE }, children: [
  run("Repository: ", { bold: true }), run("https://github.com/davis-twinomugisha/wsn_lab1")] }));
add(new Paragraph({ spacing: { after: 120, line: LINE }, children: [
  run("Wokwi simulation: ", { bold: true }), run("https://wokwi.com/projects/476121306266761217")] }));
const tree = [
  "lab1/",
  "\u251c\u2500\u2500 firmware/sensor_node/   sensor_node.ino, diagram.json (Wokwi)",
  "\u251c\u2500\u2500 firmware/uno_r4_prototype/  prototype_node.ino (UNO R4 WiFi)",
  "\u251c\u2500\u2500 python/                 acquisition, analysis, calibration notebooks",
  "\u251c\u2500\u2500 data/raw/               wokwi_serial_log.csv (+ original dump)",
  "\u251c\u2500\u2500 data/processed/         cleaned_log.csv",
  "\u251c\u2500\u2500 data/calibration/       calibration_pairs.csv (prototype vs thermometer)",
  "\u251c\u2500\u2500 figures/                five analysis plots",
  "\u251c\u2500\u2500 docs/                   circuit_diagram.png, lab_report.pdf",
  "\u2514\u2500\u2500 README.md",
];
tree.forEach(l => add(new Paragraph({ spacing: { after: 0, line: 240 },
  children: [new TextRun({ text: l, font: "Courier New", size: 18 })] })));

// ---------- table of contents ----------
const toc = [new Paragraph({ spacing: { after: 240 }, children: [run("TABLE OF CONTENTS", { bold: true, size: 26 })] })];
sections.forEach(([n, t]) => {
  const label = n ? `${n} ${t}` : t;
  toc.push(new Paragraph({ spacing: { after: 120 },
    tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W, leader: "dot" }],
    children: [run(label), run("\t" + String(tocPages[label] ?? "?"))] }));
});

// ---------- document ----------
const pageProps = (fmt) => ({
  page: { size: { width: 11906, height: 16838 },
          margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
          pageNumbers: fmt ? { start: 1, formatType: fmt } : undefined },
});
const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
  children: [new TextRun({ font: FONT, size: SMALL, children: [PageNumber.CURRENT] })] })] });

const doc = new Document({
  creator: "Davis Twinomugisha, Sarah Asingwiire, Opuche Samson, Phillip Okwany",
  title: "Design, Implementation and Calibration of a Multi-Sensor Edge Node",
  styles: { default: { document: { run: { font: FONT, size: BODY } } } },
  sections: [
    { properties: pageProps(null), children: cover },
    { properties: pageProps(NumberFormat.LOWER_ROMAN), footers: { default: footer }, children: toc },
    { properties: pageProps(NumberFormat.DECIMAL), footers: { default: footer }, children: body },
  ],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(path.join(HERE, "lab_report.docx"), buf);
  fs.writeFileSync(path.join(HERE, "_toc_labels.json"), JSON.stringify(sections.map(([n, t]) => n ? `${n} ${t}` : t)));
  console.log("wrote lab_report.docx");
});
