# FreeCAD — Test Coverage Report

A consolidated, structural assessment of automated test coverage across the FreeCAD
codebase (C++ GoogleTest suites, Python `unittest` suites, and build/dev tooling tests).

- **Generated:** 2026-06-21
- **Branch:** `main`
- **Authors:** produced by 21 specialised analysis agents, one per subsystem, then consolidated.

---

## 1. Scope & Methodology

This report covers three test layers (as requested):

1. **C++ unit tests** — GoogleTest, under `tests/src/{Base,App,Gui,Mod}/`, run via `ctest`.
2. **Python tests** — `unittest`, registered per module via `FreeCAD.__unit_test__`, run inside
   the FreeCAD binary via `FreeCADCmd -t 0` / `FreeCAD -t 0`.
3. **Build/dev tooling tests** — pure-Python suites under `src/Tools/`.

CI & visual snapshot tests were explicitly out of scope (the snapshot harness is summarised in
§7 only because it is part of the infrastructure).

### Important caveat — this is a *structural* assessment, not measured coverage

The original request was for **measured + qualitative** coverage. Measured line/branch coverage
could **not** be produced: this checkout has **no compiled build and no toolchain** (`pixi` is not
installed, there is no `build/` directory, and only `gcov` — not `lcov`/`gcovr` — is present).
Real numbers would require a from-scratch instrumented build (estimated 1–3 h, plus a multi-GB
dependency download) and a full test run. By agreement, this report delivers the **structural /
qualitative** analysis now; §9 documents exactly how to obtain measured numbers later.

Consequently, **all coverage ratings (None / Low / Medium / High) and all test-case counts are
estimates** derived by reading the repository — counting `TEST`/`TEST_F` macros and `def test_`
methods, and weighing tested vs. untested source surface. Treat counts as ±10%.

> **Update (2026-06-22):** the suites have since been **actually built and executed** on a debug
> build. Empirical pass/fail results (C++ 1661/1661 green; 19/20 Python modules green; CAM analysed
> per-suite) are documented separately in
> [parts/22-test-execution-results.md](parts/22-test-execution-results.md). It is still not
> coverage-instrumented, so it reports execution outcomes, not measured percentages.

---

## 2. Executive Summary

FreeCAD has a **large and genuinely valuable test base** — on the order of **~1,700 C++ test
cases and ~2,800 Python test methods (~4,500 total)** — but coverage is **highly uneven**, and the
gaps cluster precisely where the project is most algorithmically risky.

**The good:**

- The **Base** layer (math, units, persistence primitives) is the best-tested foundation.
- **Part / TopoShape** and its topological-naming machinery, the **Sketcher** *object* layer, the
  **CAM** post-processor/G-code engine, and the **Material** value system are all well exercised.
- The harness design is clean: self-registering Python tests and **headless-by-design** GUI tests
  (`QT_QPA_PLATFORM=offscreen`).

**The concerning, recurring patterns:**

1. **Numerical / geometry cores are under-tested.** The PlaneGCS constraint solver (~13k LOC, **2**
   direct tests), TechDraw's HLR projection (smoke-only), the Assembly/Ondsel solver (1 test with an
   **empty body**), mesh repair, and ReverseEngineering fitting are the engines users depend on — and
   the least verified.
2. **Data-exchange round-trip fidelity is largely unverified.** STEP is thin; IGES / glTF / DXF have
   no tests; IFC round-trip is untested in CI; mesh IO formats (STL/PLY/OFF/…) and CSV/XLSX are
   untested. Silent geometry/units/metadata regressions would pass CI.
3. **GUI layers are broadly untested** across nearly every workbench (task panels, view providers,
   commands, dialogs).
4. **Dead / unregistered tests** — a striking, *cheap-to-fix* theme: many test files exist but are
   never run because they aren't registered (see §5). This is false confidence, not missing work.
5. **Two disconnected run-modes.** Python suites are **not** in `ctest`, so a green `ctest` does
   **not** mean the Python tests passed.
6. **The Python-binding generator** — which generates the *entire* C++↔Python API — has only 6 tests,
   and CI doesn't even run them.

---

## 3. Coverage Heatmap (by subsystem)

Ratings are heuristic. "C++ / Py" columns give approximate test-case counts.

| # | Subsystem | C++ cases | Python cases | Maturity | Headline risk |
|---|-----------|----------:|-------------:|:--------:|---------------|
| 01 | [Base](parts/01-base.md) | ~554 | ~63 | **Medium-High** | type system / persistence round-trip thin |
| 02 | [App core](parts/02-app.md) | ~508 | ~190 | **Medium** | `Document`, `PropertyLinks` only smoke-tested in C++ |
| 03 | [Gui](parts/03-gui.md) | ~139 | ~44 | **Low** | one High island (StyleParameters); rest untested |
| 04 | [Part](parts/04-part.md) | ~276 | ~154 | **Medium-High** | GUI + STEP/IGES/BREP import untested |
| 05 | [PartDesign](parts/05-partdesign.md) | 10 | ~189 | **Medium** / GUI Low | dress-up features, GUI workflow |
| 06 | [Sketcher](parts/06-sketcher.md) | 107 | 98 | **Medium-High** / solver **critical** | PlaneGCS solver has 2 tests |
| 07 | [Mesh & MeshPart](parts/07-mesh.md) | 20 | 42 | **Low-Medium** | repair, booleans, IO formats untested |
| 08 | [Points & ReverseEng](parts/08-points-reveng.md) | 15 | 0 | Points Medium / RevEng **None** | all RE fitting algorithms uncovered |
| 09 | [FEM](parts/09-fem.md) | 0 | 115 | **Medium** (Py only) | no C++ tests; GUI + post-proc untested |
| 10 | [CAM](parts/10-cam.md) | 0 | ~1305 | **Medium-High** | legacy posts + simulator/libarea untested |
| 11 | [Draft](parts/11-draft.md) | 0 | ~119 | **Medium** core / Low overall | DXF importer (~5k LOC) barely tested |
| 12 | [BIM](parts/12-bim.md) | 0 | ~313 | **Medium** / IFC **high-risk** | IFC round-trip untested in CI |
| 13 | [TechDraw](parts/13-techdraw.md) | 2 | ~12 | **Low** | HLR projection core smoke-only |
| 14 | [Assembly](parts/14-assembly.md) | 1* | 9 | **Low** | solver / joint kinematics untested |
| 15 | [Spreadsheet](parts/15-spreadsheet.md) | 5 | 87 | **Medium** engine / I/O None | CSV/XLSX, dependency graph |
| 16 | [Measure](parts/16-measure.md) | 3 | 0 | **Low** | 1 of 7 measurement types tested |
| 17 | [Material](parts/17-material.md) | 35 | 18 | **Medium-High** | card-parsing error paths, library lookup |
| 18 | [Import & OpenSCAD](parts/18-import-openscad.md) | 0 | 28 | Import **Low** / OpenSCAD-import Medium | STEP thin; IGES/glTF/DXF none |
| 19 | [Smaller workbenches](parts/19-smaller-workbenches.md) | ~11 | ~1 | mostly **None** | 8 of 13 have zero tests |
| 20 | [Test harness](parts/20-test-harness.md) | — | — | infrastructure | Python not in ctest; no coverage target |
| 21 | [Build/Dev tooling](parts/21-tooling.md) | — | 48 | **uneven** | binding generator ~untested, not in CI |

\* Assembly's single C++ test has an empty body and asserts nothing.

**Estimated totals:** ~1,700 C++ GoogleTest cases · ~2,800 Python `unittest` methods.

---

## 4. Cross-cutting findings

### 4.1 The riskiest code is the least tested
A clear inverse correlation exists between algorithmic risk and test depth. The constraint solver,
HLR projection, the assembly solver, mesh repair, and the numeric fitting in ReverseEngineering are
all engines whose silent miscomputation would corrupt user models — and all are at None/Low direct
coverage. High-level Python scenarios touch some of them indirectly, but cannot localise a failure to
a solver branch or pin numerical regressions.

### 4.2 Data exchange is a systemic blind spot
Across Part (STEP/IGES/BREP), Import (IGES/glTF/DXF/PLMXML), Mesh (STL/PLY/OFF/SMF/VRML/X3D/AMF),
BIM (IFC2X3/IFC4), and Spreadsheet (CSV/XLSX), **round-trip fidelity is essentially unverified**.
This is the single most repeated gap in the report and the one most likely to cause silent,
hard-to-trace data loss.

### 4.3 GUI is structurally untested
Nearly every workbench reports its Gui layer (task panels, view providers, commands, `Dlg*`) as the
largest untested surface. The infrastructure for headless GUI testing already exists
(`QT_QPA_PLATFORM=offscreen`, the `setup_qt_test` helper, live `FreeCADGui` Python sessions) but is
used by only a handful of suites.

### 4.4 Two test worlds that don't meet
C++ runs under `ctest`; Python runs inside the FreeCAD binary. There is no single command that runs
both, and **`ctest` green ≠ Python green**. This makes the true pass/fail state of the project
non-obvious from any one signal.

---

## 5. Quick wins — already-written tests that never run

These suites exist in the tree but are **not registered / disabled**, so they provide zero protection
today. Re-enabling them is the highest value-per-effort work available:

| Suite | Where | Why it doesn't run |
|-------|-------|--------------------|
| FEM Mystran (`test_solver_mystran.py`, 7) | `src/Mod/Fem/femtest/` | not registered in `TestFemApp.py` (missing `FemTest12`) |
| FEM `function_tests` (13) + GUI (3) | `src/Mod/Fem/` | unregistered / disabled |
| Spreadsheet XLSX import (3) + GUI (1) | `src/Mod/Spreadsheet/` | not in `Init.py` `__unit_test__` |
| Material GUI appearance (3) | `src/Mod/Material/` | not registered |
| BIM NativeIFC self-test (20) | `src/Mod/BIM/nativeifc/` | commented out in `InitGui.py:853` (downloads test file) |
| Draft importer suites (DWG/OCA/AirfoilDAT) | `src/Mod/Draft/drafttests/` | commented out |
| `TestTreeSelection.py` | `src/Mod/Test/` | not in `InitGui.py` |
| TemplatePyMod (7) | `src/Mod/TemplatePyMod/` | not registered |
| Binding-generator tests (6) | `src/Tools/bindings/tests/` | CI only discovers `src/Tools/tests/` |
| JtReader (`TestJtReader`) | `src/Mod/JtReader/` | manual harness, no assertions, no runner |

---

## 6. Prioritised recommendations (project-wide)

**P1 — Reclaim existing tests (days, not weeks).**
Register/re-enable every suite in §5; for the few needing network/data, commit a small offline
fixture. Fix CI test discovery so `src/Tools/bindings/tests/` actually runs.

**P2 — Unify the run-modes.**
Wire the Python `unittest` suites into `ctest` (e.g. one `add_test` per registered module invoking
`FreeCADCmd -t <name>`) so a single `ctest` run reflects true project health.

**P3 — Golden tests for the high-risk cores.**
Add deterministic, analytically-known-answer tests for: PlaneGCS (convergence, per-constraint
gradient checks, conflict/redundancy diagnostics), TechDraw HLR (visible/hidden edge classification
on known solids), the Assembly solver (per-joint-type DOF / over-constraint matrix), and mesh repair.

**P4 — Data-exchange round-trip suites.**
For each format, `export → import → compare` against geometric invariants (volume/area/COM, unit
scaling, color/metadata). Start with STEP, IFC (both schemas), and the mesh IO formats.

**P5 — Add a measured-coverage target.**
Provide a CMake coverage preset (gcov/lcov for C++, `coverage.py` for the Python-in-FreeCAD layer)
and publish numbers in CI so this report can become quantitative (see §9).

**P6 — Backfill GUI tests** using the existing offscreen patterns, starting with the shared
`src/Gui` subsystems (Command framework, TaskView, ViewProvider base) that every workbench depends on.

---

## 7. Test infrastructure (summary)

See [parts/20-test-harness.md](parts/20-test-harness.md) for the full analysis. In brief:

- **Python layer** (`src/Mod/Test/`): self-registration via `FreeCAD.__unit_test__` (≈29
  registrations across 28 `Init.py`/`InitGui.py` files); `TestApp.All/PrintAll` aggregate and run.
- **C++ layer** (`tests/`, 146 `.cpp`: Base 42 · App 25 · Gui 13 · Mod 64): gated by
  `ENABLE_DEVELOPER_TESTS` + per-workbench `BUILD_*`; `gtest_discover_tests` on Linux/macOS, a single
  per-binary `add_test` on Windows (DLL-PATH limitation); GUI tests headless via `setup_qt_test`.
- **Test data**: `tests/data` (`DATADIR`), `tests/visual/baselines` (28 reference PNGs for the Coin
  snapshot regression suite), `src/Mod/Test/TestData`, and per-module `TestData/`.

---

## 8. How to run the tests

```bash
# C++ (GoogleTest) — requires a build configured with -DENABLE_DEVELOPER_TESTS=ON
pixi run test                                   # ctest in build/debug
ctest --test-dir build/debug -R Base            # a subset
build/debug/tests/App_tests_run --gtest_filter='Document.*'   # one binary/case

# Python (unittest) — run inside the FreeCAD binary
build/debug/bin/FreeCADCmd -t 0                 # all CLI-registered Python tests
build/debug/bin/FreeCADCmd -t TestPartApp       # one module
xvfb-run build/debug/bin/FreeCAD -t 0           # incl. GUI-registered tests

# Tooling (pure Python)
python3 -m unittest discover -s src/Tools/tests -p "test_*.py"
python3 -m unittest discover -s src/Tools/bindings/tests -p "test_*.py"   # not in CI today
```

---

## 9. Obtaining measured coverage (deferred step)

To turn the heuristic ratings in this report into real numbers:

1. **Bootstrap toolchain:** install `pixi`; `pixi run initialize` (submodules).
2. **Instrumented configure (C++):** configure with coverage flags, e.g.
   `-DCMAKE_CXX_FLAGS="--coverage -O0" -DCMAKE_EXE_LINKER_FLAGS="--coverage"` and
   `-DENABLE_DEVELOPER_TESTS=ON`. Note: coverage flags invalidate the ccache cache → expect a full
   ~1–3 h build.
3. **Build & run both layers** so `.gcda` files are produced: `ctest` **and** `FreeCADCmd -t 0`
   (+ `xvfb-run FreeCAD -t 0` for GUI).
4. **Aggregate C++:** `gcovr -r . --html-details` or `lcov --capture` → `genhtml`.
5. **Python-in-FreeCAD:** run the suites under `coverage.py` (the FreeCAD Python interpreter), then
   `coverage html`. This is fiddly because tests execute inside the embedded interpreter.
6. Merge per-subsystem numbers back into §3.

---

## Roadmap

A prioritized, value-per-effort plan to close the gaps in this report lives in
[ROADMAP.md](ROADMAP.md).

## 10. Index of detailed reports

Each subsystem has a standalone report under [`parts/`](parts/):

1. [Base Layer](parts/01-base.md)
2. [App Core](parts/02-app.md)
3. [Gui Layer](parts/03-gui.md)
4. [Part Workbench](parts/04-part.md)
5. [PartDesign Workbench](parts/05-partdesign.md)
6. [Sketcher Workbench](parts/06-sketcher.md)
7. [Mesh & MeshPart Workbenches](parts/07-mesh.md)
8. [Points & ReverseEngineering](parts/08-points-reveng.md)
9. [FEM Workbench](parts/09-fem.md)
10. [CAM Workbench](parts/10-cam.md)
11. [Draft Workbench](parts/11-draft.md)
12. [BIM Workbench](parts/12-bim.md)
13. [TechDraw Workbench](parts/13-techdraw.md)
14. [Assembly Workbench](parts/14-assembly.md)
15. [Spreadsheet Workbench](parts/15-spreadsheet.md)
16. [Measure Workbench](parts/16-measure.md)
17. [Material Workbench](parts/17-material.md)
18. [Import & OpenSCAD (Data Exchange)](parts/18-import-openscad.md)
19. [Smaller Workbenches](parts/19-smaller-workbenches.md)
20. [Test Harness & Infrastructure](parts/20-test-harness.md)
21. [Build & Dev Tooling](parts/21-tooling.md)
22. [Test Execution Results — Empirical Run (2026-06-22)](parts/22-test-execution-results.md)
