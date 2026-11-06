// Builds docs/lab_report.docx in the team's Soroti University report format.
// Run python docs/build_report_content.py after reproducing the data analysis.
// Usage: node docs/build_report_docx.js [docs/_toc_pages.json]
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
  "docs/soroti_logo.png": [
    344,
    296
  ],
  "docs/system_architecture.png": [
    1979,
    619
  ],
  "docs/circuit_diagram.png": [
    2067,
    1649
  ],
  "figures/calibration_fit.png": [
    900,
    675
  ],
  "figures/temp_vs_time.png": [
    2100,
    720
  ],
  "figures/humidity_vs_time.png": [
    2100,
    720
  ],
  "figures/raw_vs_filtered_temp.png": [
    2100,
    720
  ],
  "figures/light_vs_time.png": [
    2100,
    720
  ],
  "figures/motion_events.png": [
    2100,
    720
  ]
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
  center("WSN2100 - WIRELESS SENSOR NETWORKS", { bold: true, after: 300 }),
  center("Laboratory 1: Technical Report", { italics: true, after: 160 }),
  center("Submitted by", { italics: true, after: 200 }),
  center("DAVIS TWINOMUGISHA", { bold: true }),
  center("SARAH ASINGWIIRE", { bold: true }),
  center("OPUCHE SAMSON", { bold: true }),
  center("PHILLIP OKWANY", { bold: true, after: 360 }),
  center("in partial fulfilment of the requirements for the degree of", { italics: true, after: 120 }),
  center("BACHELOR OF ENGINEERING IN ELECTRONICS AND COMPUTER", { bold: true }),
  center("ENGINEERING", { bold: true, after: 360 }),
  center("6 NOVEMBER 2026", { bold: true }),
];

// ---------- body ----------
const body = [];
const add = (...xs) => xs.flat().forEach(x => body.push(x));
const report = JSON.parse(fs.readFileSync(path.join(HERE, "report_content.json"), "utf8"));
for (const item of report) {
  if (item.type === "heading") add(H(item.number, item.title));
  else if (item.type === "paragraph") add(P(item.content));
  else if (item.type === "figure") add(IMG(item.file, item.width, item.caption));
  else if (item.type === "table") add(TABLE(item.widths, item.rows, item.caption));
  else if (item.type === "tree") item.lines.forEach(text => add(new Paragraph({
    spacing: { after: 0, line: 240 }, children: [new TextRun({ text, font: "Courier New", size: 18 })]
  })));
}

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
