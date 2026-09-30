import json, subprocess, re, sys
labels = json.load(open("_toc_labels.json"))
n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo","lab_report.pdf"],capture_output=True,text=True).stdout).group(1))
pages = {}
body_start = 3  # cover = 1, TOC = 2 (roman i), body page 1 = PDF page 3
for p in range(body_start, n+1):
    txt = subprocess.run(["pdftotext","-f",str(p),"-l",str(p),"-layout","lab_report.pdf","-"],capture_output=True,text=True).stdout
    lines = [l.strip() for l in txt.splitlines()]
    for lab in labels:
        if lab not in pages and any(l == lab or l.startswith(lab) and len(l) < len(lab)+3 for l in lines):
            pages[lab] = p - body_start + 1
missing = [l for l in labels if l not in pages]
print("pages:", n, pages, "missing:", missing)
json.dump(pages, open("_toc_pages.json","w"))
