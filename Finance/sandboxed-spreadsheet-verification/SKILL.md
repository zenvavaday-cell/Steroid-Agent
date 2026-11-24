---
name: sandboxed-spreadsheet-verification
description: Recalculates Excel and ODS workbooks in an isolated environment, inventories formulas, detects hardcodes, broken links, error cells, and balance failures, and reports every issue with a cell reference. Use when auditing a spreadsheet, validating a model before distribution, or checking that cached values match live formulas.
license: MIT
metadata:
  author: zenvada
  version: "1.0.0"
  domain: finance
---

# Sandboxed Spreadsheet Verification

## Overview

Spreadsheet files store cached values alongside formulas. Those cached values can be stale, wrong, or manually patched. Verification means forcing a recalculation in a clean environment, comparing the recalculated values to the stored ones, and inspecting the formula graph for structural defects.

Never open an untrusted workbook with macros enabled on a host machine. Copy it to a disposable directory, disable macros, and use a headless converter.

## When to use

- Auditing a financial model, budget, or data workbook.
- Checking a workbook received from a third party.
- Verifying that a model still works after edits.
- Producing an evidence trail for audit or investment committee.

## Required tools

- `libreoffice` or `soffice` for headless recalculation.
- Python 3.10+ with `openpyxl` for XLSX/XLSM inspection.
- `odfpy` for ODS files if needed.
- Optional: `formulas` or `pycel` for independent formula evaluation.

## Workflow

### 1. Isolate the file

```bash
set -Eeuo pipefail
WORKDIR="$(mktemp -d /tmp/xlsx-audit.XXXXXX)"
cp -- "$1" "$WORKDIR/input.xlsx"
cd "$WORKDIR"
```

Refuse to proceed if the workbook contains macros and the task does not explicitly require them. Rename `.xlsm` to `.xlsx` only after confirming no macro is needed for calculation.

### 2. Recalculate with LibreOffice

```bash
soffice --headless --norestore --convert-to xlsx \
  --outdir "$WORKDIR/recalc" "$WORKDIR/input.xlsx"
```

LibreOffice may reuse cached values unless recalculation is forced. Set the recalc mode in a user profile or use a macro-free conversion followed by an independent evaluator. Always compare both cached and recalculated values; a match is evidence, not proof.

### 3. Inventory the workbook

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx", data_only=False)
for ws in wb.worksheets:
    formulas = sum(
        1 for row in ws.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and cell.value.startswith("=")
    )
    print(f"{ws.title}: {ws.max_row}x{ws.max_column}, {formulas} formulas, state={ws.sheet_state}")
```

Report hidden sheets, very hidden sheets, merged cells, external links, defined names, data validation, and conditional formatting.

### 4. Scan for error values and hardcodes

```python
ERRORS = {"#REF!", "#DIV/0!", "#VALUE!", "#N/A", "#NAME?", "#NUM!", "#NULL!"}

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value in ERRORS:
                print(f"ERROR {ws.title}!{cell.coordinate}: {cell.value}")
            if cell.data_type == "f":
                # A formula that is only a constant is a disguised hardcode.
                if cell.value.replace("=", "").replace("-", "").replace(".", "").isdigit():
                    print(f"HARDCODE {ws.title}!{cell.coordinate}: {cell.value}")
```

Also flag formulas containing suspicious constants (for example `=B2*1.07`) and formulas that differ from their row or column neighbours.

### 5. Compare cached versus recalculated values

```python
cached = load_workbook("input.xlsx", data_only=True)
recalc = load_workbook("recalc/input.xlsx", data_only=True)

for ws_c, ws_r in zip(cached.worksheets, recalc.worksheets):
    for row_c, row_r in zip(ws_c.iter_rows(), ws_r.iter_rows()):
        for c, r in zip(row_c, row_r):
            if isinstance(c.value, (int, float)) and isinstance(r.value, (int, float)):
                if abs(c.value - r.value) > max(0.01, abs(r.value) * 1e-9):
                    print(f"DRIFT {ws_c.title}!{c.coordinate}: cached={c.value} recalc={r.value}")
```

Report drift in absolute and relative terms. A drift of 0.01 on a 10-million cell is noise; a drift of 0.01 on a 0.05 margin is material.

### 6. Check structural invariants

For financial models, assert:

- Balance sheet: assets = liabilities + equity in every period.
- Cash flow: ending cash = balance sheet cash.
- Retained earnings roll-forward.
- Debt schedule opening/closing continuity.
- Sum of segments equals consolidated total.
- No negative values where the business logic forbids them (unless a credit balance is valid).
- Dates are real dates, not text that looks like a date.

### 7. Produce the report

| Severity | Meaning | Examples |
| --- | --- | --- |
| Critical | Output is wrong or untrustworthy | Error cell, balance failure, broken external link |
| High | Material risk of wrong output | Hardcode in calc, stale cached value, sign error |
| Medium | Maintainability or audit risk | Inconsistent formula row, hidden sheet, merged cells |
| Low | Cosmetic | Formatting, label typo |

Each finding includes sheet, cell, formula or value, expected result, observed result, and suggested fix.

## Gotchas

- `openpyxl` with `data_only=True` returns `None` for formulas that were never calculated by Excel. A blank is not a zero.
- LibreOffice may not recalculate on load. Verify with a deliberately changed input before trusting the output.
- Iterative calculation settings are stored in the workbook but may not carry over to the converter.
- External links can silently resolve to cached values on the auditor's machine.
- 1900 versus 1904 date systems shift every date by four years.
- Merged cells hide values outside the top-left cell.
- Macros can rewrite values on open. Never enable them for verification.
- Floating-point comparisons need tolerances; exact equality produces false positives.

## Output contract

```
Workbook: <name>
Sheets: <count> (<hidden>, <very hidden>)
Formulas: <count>
Recalculation: <forced / not forced>
Critical findings: <count>
High findings: <count>
Drift cells: <count>
Invariant results: <pass/fail table>
```

List every finding with a cell reference. Do not summarize away the coordinate.

## Checklist

- [ ] File copied to an isolated directory.
- [ ] Macros disabled and external links noted.
- [ ] Recalculation forced and verified with a changed input.
- [ ] Error values scanned.
- [ ] Hardcodes and suspicious constants scanned.
- [ ] Cached versus recalculated values compared.
- [ ] Structural invariants checked.
- [ ] Findings ranked by severity with cell references.

## Related skills

- `deterministic-financial-modeling` for the model architecture being verified.
- `automated-tax-document-parsing` when the workbook is a tax source document.
- `confidence-threshold-output-gating` before releasing an audit opinion.
