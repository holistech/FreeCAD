# Test Coverage — Spreadsheet Workbench

Scope: `/home/soeren/src/FreeCAD/src/Mod/Spreadsheet/` and the C++ unit tests in
`/home/soeren/src/FreeCAD/tests/src/Mod/Spreadsheet/`.

This is a structural/qualitative assessment. No build or test run was performed;
coverage levels are estimates (None/Low/Medium/High) justified by mapping existing
test cases onto the source surface.

---

## 1. Source Surface

The workbench splits into an App (engine/data model) layer and a Gui layer, plus a
small pure-Python XLSX import path.

### App layer (`App/`, ~21 .cpp/.h files)

| Area | Files | Responsibility |
|------|-------|----------------|
| Sheet document object | `Sheet.cpp/.h` (~1850 LOC), `SheetPyImp.cpp`, `Sheet.pyi`, `SheetObserver.cpp/.h` | DocumentObject holding the cell grid; recompute, dependency propagation, CSV `importFromFile`/`exportToFile`, `getUsedCells`/`getColumns`/`getRows`, row/column width & height, merge handling, Python bindings (`set`, `get`, `setAlias`, `importFile`, `exportFile`, `insertRows`/`Columns`, `removeRows`/`Columns`, `mergeCells`). |
| Cell model | `Cell.cpp/.h` (~1170 LOC) | Per-cell state: content/expression, alias, display unit, alignment, style, foreground/background, span, persistence (save/restore), copy/paste. |
| Property container | `PropertySheet.cpp/.h` (~2370 LOC), `PropertySheetPyImp.cpp` | The map of address→Cell; cell **address/range parsing & validation** (`isValidCellAddressName`, `isValidAlias`), alias registry, the **cell dependency graph** (`addDependencies`, `recomputeDependencies`, `providesTo`, topological resolution), expression rewriting on row/column insert/remove and on rename. |
| Address/range utilities | `Utils.cpp/.h` (~240 LOC) | `columnName`/`rowName`, `createRectangles` (range → rectangles), `quote`/`unquote`, string-to-address decoding via generated regexps (`create_regexps.sh`). |
| Auxiliary properties | `PropertyColumnWidths.*`, `PropertyRowHeights.*` (+ PyImp + .pyi), `DisplayUnit.h` | Specialized properties for grid geometry and per-cell unit display. |
| Module init | `AppSpreadsheet.cpp`, `SpreadsheetGlobal.h` | Type registration, expression-function registration. |

Expression integration is **not** local to this module: cell contents are parsed/evaluated
by `App/Expression` (core), but the Spreadsheet adds spreadsheet-specific aggregate
functions (sum, average, count, min, max, stddev, …) and resolves cell-address/alias
references against the `PropertySheet`. The dependency graph that drives recompute order
lives in `PropertySheet`.

### Gui layer (`Gui/`, ~32 .cpp/.h files) — model/view, commands, dialogs

`SheetModel`, `SheetTableView` (+ accessibility interface), `SpreadsheetView`,
`SpreadsheetDelegate`, `ViewProviderSpreadsheet`, `Command.cpp`, `Workbench`,
`LineEdit`, `ZoomableView`, and dialogs `DlgBindSheet`, `DlgSheetConf`, `DlgSettings`,
`PropertiesDialog`, plus a `qtcolorpicker`. These are interactive/QWidget code.

### Pure-Python

- `importXLSX.py` (~510 LOC): XLSX → spreadsheet importer including an OpenFormula→FreeCAD
  formula translator.
- `Init.py` / `InitGui.py`: registration; `Init.py:42` adds `TestSpreadsheet` to
  `App.__unit_test__`.

Approximate counted source: ~21 App files, ~32 Gui files, ~3 Python module files.

---

## 2. Existing Tests

### C++ (GoogleTest) — `tests/src/Mod/Spreadsheet/App/`

Target `Spreadsheet_tests_run` (gated by `BUILD_SPREADSHEET`), links the `Spreadsheet`
library. **2 test files, 5 `TEST_F` cases.**

| File | Test (fixture) | Purpose |
|------|----------------|---------|
| `PropertySheet.cpp` | `isValidCellAddressNameValidNames` | Asserts valid cell-address strings are accepted (address parsing). |
| `PropertySheet.cpp` | `isValidCellAddressNameInvalidNames` | Asserts malformed addresses are rejected. |
| `PropertySheet.cpp` | `validAliases` | Asserts acceptable alias names pass `isValidAlias`. |
| `PropertySheet.cpp` | `invalidAliases` | Asserts illegal alias names are rejected. |
| `RenameProperty.cpp` | `renameProperty` | Verifies property/reference rename propagates through the sheet. |

### Python — `src/Mod/Spreadsheet/Test*.py` and `test_importXLSX.py`

| File | Class(es) | `def test_` count | Purpose |
|------|-----------|-------------------|---------|
| `TestSpreadsheet.py` (~2030 LOC) | `SpreadsheetAggregates`, `SpreadsheetFunction`, `SpreadsheetCases` | **87** (10 / 24 / 53) | The core suite (registered in `__unit_test__`). |
| `TestSpreadsheetGui.py` | `SpreadsheetGuiCases` | **1** (`testCopySingleCell`) | Single Gui clipboard test; **not** registered in `Init.py`. |
| `test_importXLSX.py` | `TestFormulaTranslator` | **3** | Standalone tests of the OpenFormula→FreeCAD formula translator (expression translation, multi-char branching operators, nested expressions). Not registered in `__unit_test__`. |

Breakdown of the registered core suite (87 cases):

- `SpreadsheetAggregates` (10): sum, min, max, stddev, count, average, range, range_invalid, and/or aggregate functions.
- `SpreadsheetFunction` (24): math/scalar functions — cos, sin, tan, abs, exp, log, log10, round, trunc, ceil, floor, asin, acos, atan, asinh, cosh, tanh, sqrt, mod, atan2, pow, hypot, cath, not.
- `SpreadsheetCases` (53): operators & precedence (relational, ternary, implicit/explicit rel-op chains, precedence, parens), numbers/quantities/units, **row/column insert & remove**, **alias** lifecycle (create/rename/clear/ambiguous/invalid/reuse-after-remove/undo), cross-document & cross-sheet links, binding (`testBindAcrossSheets`, hidden-ref bind), **merge cells** (+ merge & bind), used/non-empty cell & range queries, vector & matrix expressions, distant cells, and many regression tests keyed to specific issue numbers (Issue3225, 3363, 3432, 4156, 6395, 6840, 6844, 19517, PR6843, involute-gear / sketcher integration scenarios).

---

## 3. Coverage Map

| Source area | Tested by | Estimated coverage | Notes |
|-------------|-----------|--------------------|-------|
| Cell address parsing/validation (`isValidCellAddressName`) | C++ valid/invalid name tests | **Medium–High** | Directly unit-tested both ways. |
| Alias name validation (`isValidAlias`) | C++ valid/invalid alias tests | **Medium–High** | Directly unit-tested both ways. |
| Alias lifecycle (set/rename/clear/ambiguous/reuse/undo) | Python `SpreadsheetCases` (≈10 alias tests) | **High** | Strong behavioral coverage incl. undo & name-reuse edge cases. |
| Aggregate functions (sum/avg/min/max/stddev/count/and/or/range) | Python `SpreadsheetAggregates` | **High** | One test per function incl. an invalid-range case. |
| Scalar/math functions | Python `SpreadsheetFunction` (24) | **High** | Broad per-function coverage. |
| Operators / precedence / ternary / rel-op chaining | Python `SpreadsheetCases` | **High** | Several dedicated tests. |
| Units / quantities / numbers in cells | Python (`testUnits`, `testNumbers`, `testQuantities…`) | **Medium–High** | Good but value-focused. |
| Row/column insert & remove (incl. expression rewrite) | Python (`testInsertRows`/`RemoveRows`/…Alias) | **High** | Includes alias-aware variants. |
| Cell dependency graph / recompute ordering | Indirectly via cross-link / insert-remove / regression tests | **Medium** | Exercised indirectly; no dedicated cycle/ordering/dirty-propagation unit tests. |
| Merge cells / spans | Python (`testMergeCells`, `testMergeCellsAndBind`) | **Medium** | Basic; split/overlap/undo of merges less covered. |
| Used/non-empty cell & range queries | Python (`testGetUsedCells`/`UsedRange`/`NonEmpty…`) | **High** | Directly tested. |
| Cross-document / cross-sheet links & binding | Python (cross-link, bind tests) | **Medium–High** | Covered, incl. hidden-ref bind. |
| Property/reference rename propagation | C++ `renameProperty`, Python `testRenameAlias*` | **Medium–High** | Both layers touch it. |
| CSV import/export (`importFromFile`/`exportToFile`, `importFile`/`exportFile`) | none found | **None** | No test references `importFile`/`exportFile`/`.csv`. |
| Range/address utilities (`createRectangles`, `quote`/`unquote`, `columnName`/`rowName`) | indirect only | **Low–Medium** | No direct unit tests; only exercised transitively. |
| Cell persistence (save/restore round-trip) | indirect via regression tests | **Low** | No explicit save→reload→assert test located. |
| Display unit / per-cell formatting & style | none direct | **Low** | Style/foreground/background/alignment essentially untested. |
| XLSX import (`importXLSX.py`) — full import | only formula translator tested | **Low** | 3 tests cover the translator; cell/style/sheet import untested. |
| Gui (model/view, delegate, commands, dialogs, view provider) | `TestSpreadsheetGui.py` (1 test, unregistered) | **None–Low** | Effectively untested; the one test is not in `__unit_test__`. |

---

## 4. Gaps & Risks (prioritized)

1. **CSV import/export — untested (high risk).** `Sheet::importFromFile` /
   `exportToFile` and their Python wrappers `importFile`/`exportFile` handle delimiter
   selection (tab/comma/semicolon), quoting, and escaping (boost
   `escaped_list_separator`). No test exercises any of this. Quoting/escaping and
   round-trip (export→import) edge cases (embedded delimiters, quotes, newlines, empty
   cells) are exactly where regressions hide.

2. **Cell dependency graph — only indirect coverage (high risk).** The recompute
   ordering, cyclic-dependency detection, and dirty-cell propagation in `PropertySheet`
   are core correctness machinery but lack dedicated unit tests (no explicit
   circular-reference, diamond-dependency, or cascade-recompute test). Failures here can
   produce silently stale values.

3. **Expression/aliasing edge cases (medium–high risk).** Although aliasing has good
   functional coverage, gaps remain: alias colliding with a valid cell address
   (e.g. an alias literally named like `AB12`), expression references surviving combined
   insert+remove operations, and address rewriting when ranges straddle the
   inserted/removed band. `testAmbiguousAlias` touches this but corner cases are thin.

4. **Persistence / round-trip (medium risk).** No located test saves a sheet, reloads,
   and asserts cells, aliases, spans, units, and styles survive. Cell save/restore is a
   large surface in `Cell.cpp`.

5. **XLSX full import (medium risk).** Only the formula translator is tested;
   actual `.xlsx` ingestion (cell values, merged cells, multiple sheets, styles) is not.

6. **Range/address utilities direct tests (low–medium risk).** `createRectangles`,
   `quote`/`unquote`, and `columnName`/`rowName` (including the generated-regexp decode
   path) deserve direct unit tests, especially boundary columns (Z→AA, ZZ→AAA) and
   malformed input.

7. **Gui layer effectively untested (medium risk, but interactive).** `SheetModel`,
   delegate, table view, commands, and the bind/conf/properties dialogs have no
   automated coverage; the lone `TestSpreadsheetGui.py` test is not registered in
   `Init.py`, so it does not run with `__unit_test__`.

8. **Formatting/style/display-unit (low risk).** Alignment, colors, and display units
   on cells are essentially untested.

---

## 5. Recommendations

1. **Add CSV round-trip tests** (Python, fast): for each delimiter, set a grid →
   `exportFile` → `importFile` into a fresh sheet → assert equality; include cells with
   embedded delimiters, quotes, and newlines, and verify quote/escape handling.
2. **Add dependency-graph unit tests** (C++ or Python): direct/indirect circular
   references (expect rejection/error), diamond dependencies, and cascade recompute
   verifying values update in the correct order after a single edit.
3. **Add a persistence round-trip test**: save a document containing aliases, merged
   cells, units, and styles; reload and assert full fidelity.
4. **Add direct utility unit tests** (C++) for `createRectangles`, `quote`/`unquote`,
   and `columnName`/`rowName` boundary cases.
5. **Register the Gui test**: add `TestSpreadsheetGui` to `App.__unit_test__` (or the
   Gui test registry) so `testCopySingleCell` actually runs, then grow it (paste,
   multi-cell copy, merged-cell copy).
6. **Expand XLSX coverage** beyond the formula translator to cover value/merge/multi-sheet
   import using a small fixture `.xlsx`.
7. **Add adversarial alias/address tests**: alias spelled like a cell address, alias
   reuse across insert+remove sequences, and reference rewriting across straddling ranges.

---

## 6. Quick Stats

- Source: ~21 App files (Sheet/Cell/PropertySheet/Utils + properties + PyImp), ~32 Gui
  files, ~3 Python module files (+ `importXLSX.py` ~510 LOC).
- C++ tests: **2 files, 5 `TEST_F`** (4 address/alias validation + 1 rename).
- Python tests: **91 `def test_` total** — `TestSpreadsheet.py` **87** (registered),
  `test_importXLSX.py` **3** (unregistered), `TestSpreadsheetGui.py` **1** (unregistered).
- Registered-and-running cases: **87** (the core App suite).
- Strong areas: aggregate & scalar functions, operators/precedence, alias lifecycle,
  row/column insert/remove, used/range queries.
- Zero-coverage areas: CSV import/export, full XLSX import, Gui model/view, cell
  styling/persistence round-trip, direct address-utility tests.
- Overall estimated coverage: **Medium** for the App expression/cell engine,
  **None–Low** for I/O (CSV/XLSX) and the entire Gui layer.
