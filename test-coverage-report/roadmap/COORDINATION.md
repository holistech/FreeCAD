# Test-Coverage Roadmap — Coordination Hub

**Living document.** This is the single source of truth for the status of the test-coverage roadmap.
It is meant to be updated every working session (by a human or an AI assistant) so progress is never
lost between sessions.

- **Last updated:** 2026-06-22
- **Roadmap overview:** [../ROADMAP.md](../ROADMAP.md)
- **Per-phase implementation plans:** `phase-0` … `phase-4` in this directory.
- **Source analysis:** [../README.md](../README.md) and `../parts/`.

---

## How to use / update this document

Whenever you start, finish, or change a roadmap task **in the same session you make the change**:

1. **Update the task row** in the [Task Tracker](#task-tracker): set `Status`, `Branch/PR`, and
   `Last update` (YYYY-MM-DD).
2. **Bump** the `Last updated` date at the top of this file.
3. **Append a dated entry** to the [Session Log](#session-log) describing what changed (1–3 lines):
   which tasks moved, which branches/commits/PRs were created, and any decisions or new findings.
4. If you discover new work, **add a new task row** (keep the `Pn.m` ID scheme) and mention it in the
   log. Don't delete tasks — mark them `Dropped` with a one-line reason.
5. Keep the corresponding **phase plan** (`phase-n-*.md`) in sync if scope changes.

Status values: `Not started` · `In progress` · `In review` · `Done` · `Blocked` · `Dropped`.

Conventions (apply to all roadmap work):
- One branch per task or per small task group, named as the phase plan suggests
  (e.g. `test/reclaim-dead-suites`). Branch off `main`.
- Author = the contributor's git identity. Commit trailers: `Assisted-by: <model>` (FreeCAD
  AI_POLICY) and, per this user's preference, `Co-Authored-By: <model>`.
- Verify before marking `Done`: see each phase plan's verification section. Minimum bar:
  `pixi run test` (C++) green **and** the relevant `FreeCADCmd -t <module>` green, and the full
  `FreeCADCmd -t 0` still completes.
- **Always run ctest via `pixi run ctest …`** (or `pixi run test`), never the bare system `ctest`.
  The build is configured with conda's CMake 4.2, whose generated GoogleTest includes require CMake
  ≥3.30; the system `ctest` (3.28) fails with "CMake 3.30 or higher is required". After changing
  `tests/CMakeLists.txt` you must `pixi run configure` (reconfigure), not just `pixi run build`.
- Never commit `test-coverage-report/` or `CLAUDE.md` inside a code-fix branch unless that is the
  branch's explicit purpose.

---

## Phase status overview

| Phase | Theme | Plan | Status | Notes |
|------|-------|------|--------|-------|
| 0 | Reclaim dead tests & make CI trustworthy | [phase-0](phase-0-reclaim-and-ci.md) | Largely done | P0.4–P0.6 done; P0.1 reclaimed; P0.3 awaits human push; P0.2 blocked by a bug (FU-1) |
| 1 | De-risk numerical/geometry cores | [phase-1](phase-1-numeric-cores.md) | Done | All 4 suites pushed (PlaneGCS, HLR, Assembly, Mesh); 29 new tests green; found FU-3 |
| 2 | Data-exchange round-trips | [phase-2](phase-2-data-exchange.md) | Done | All 5 suites pushed; 27 new tests green; found FU-4/FU-5 |
| 3 | Fill zero-coverage modules | [phase-3](phase-3-zero-coverage-modules.md) | Not started | ReverseEngineering, Measure, Points, Robot/Inspection |
| 4 | GUI tests + coverage measurement | [phase-4](phase-4-gui-and-coverage.md) | Not started | Coverage target unlocks quantitative tracking |

---

## Task Tracker

Status legend above. `Branch/PR` holds the branch name and/or PR link once it exists.

### Phase 0 — Reclaim & CI
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P0.1 | Register/re-enable dormant test suites | Done (reclaimable parts) | `test/reclaim-dead-suites` + `test/reclaim-gui-and-ifc` (pushed) | 2026-06-22 |
| P0.2 | Offline IFC fixture + re-enable NativeIFC self-test | Blocked | needs NativeIFC recompute-hang fixed first (FU-1) | 2026-06-22 |
| P0.3 | CI discovery includes `src/Tools/bindings/tests/` | In review | `ci/run-binding-generator-tests` (local; push needs `workflow` OAuth scope) | 2026-06-22 |
| P0.4 | Wire Python suites into ctest | Done | `test/wire-python-into-ctest` (pushed; based on P0.5) | 2026-06-22 |
| P0.5 | Runner-wide fd/teardown guard | Done | `test/runner-fd-guard` (pushed) | 2026-06-22 |
| P0.6 | Fail CI on import-failed registered modules | Done | `test/wire-python-into-ctest` (pushed) | 2026-06-22 |

### Phase 1 — Numerical / geometry cores
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P1.1 | PlaneGCS solver unit suite | Done | `test/sketcher-planegcs-core` (pushed; 8 tests green) | 2026-06-22 |
| P1.2 | TechDraw HLR golden tests | Done | `test/techdraw-hlr-golden` (pushed; 7 tests green) | 2026-06-22 |
| P1.3 | Assembly solver matrix | Done | `test/assembly-solver-matrix` (pushed; C++ 2 + Python 4 green) | 2026-06-22 |
| P1.4 | Mesh repair + boolean ops | Done | `test/mesh-repair-and-booleans` (pushed; 8 tests green) | 2026-06-22 |

### Phase 2 — Data-exchange round-trips
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P2.1 | STEP/IGES/glTF/BREP round-trip | Done | `test/exchange-step-iges-gltf` (pushed; 7 tests) | 2026-06-22 |
| P2.2 | IFC2X3 + IFC4 round-trip | Done | `test/exchange-ifc-roundtrip` (pushed; 3 tests; found FU-4/FU-5) | 2026-06-22 |
| P2.3 | Mesh formats round-trip | Done | `test/exchange-mesh-formats` (pushed; 10 tests) | 2026-06-22 |
| P2.4 | Spreadsheet CSV + XLSX | Done | `test/spreadsheet-csv-xlsx` (pushed; 5 tests) | 2026-06-22 |
| P2.5 | Draft DXF import corpus | Done | `test/draft-dxf-corpus` (pushed; 2 new round-trips) | 2026-06-22 |

### Phase 3 — Zero-coverage modules
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P3.1 | ReverseEngineering algorithms | Not started | — | 2026-06-22 |
| P3.2 | Measure — all 7 measurement types | Not started | — | 2026-06-22 |
| P3.3 | Points persistence/E57 + JtReader parser | Not started | — | 2026-06-22 |
| P3.4 | Robot / Inspection logic | Not started | — | 2026-06-22 |

### Phase 4 — GUI + coverage measurement
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P4.1 | Coverage-measurement target (gcov/lcov + coverage.py) | Not started | — | 2026-06-22 |
| P4.2 | Shared Gui subsystem tests (offscreen) | Not started | — | 2026-06-22 |
| P4.3 | Per-workbench GUI smoke tests under xvfb | Not started | — | 2026-06-22 |

---

## Follow-up bugs found (not reclaim work — real defects to fix separately)

| ID | Bug | Where | Status | Notes |
|----|-----|-------|--------|-------|
| FU-1 | NativeIFC self-test: multiple defects + GUI-runner hang | `src/Mod/BIM/nativeifc/` | **Partly fixed** (`fix/nativeifc-selftest-bugs`, pushed) | 4 genuine bugs fixed (below). Suite **not yet enableable**: 2 stale assertions + a systemic GUI hang remain. |
| FU-2 | `TestSpreadsheetGui` hung headless, errored on args, never installed | `src/Mod/Spreadsheet/` | **Fixed & enabled** (`fix/spreadsheet-gui-test`, pushed) | Now green under `xvfb-run FreeCAD -t TestSpreadsheetGui`; wired into CMakeLists + GUI `__unit_test__`. |
| FU-3 | Built-in mesh booleans are not volumetrically reliable | `src/Mod/Mesh/App/Core/SetOperations` | Open (found during P1.4) | For two trivial overlapping axis-aligned cubes, `MeshObject::unite`/`subtract` produce geometrically wrong, non-watertight results and volumes vary between runs (union came out 6.7 < a single cube's 8; only `intersect` had a plausible bbox). P1.4 therefore only smoke-tests the booleans. Needs a maintainer / possibly the GTS/OpenVDB backend. |
| FU-4 | Legacy IFC importer broken against ifcopenshell 0.8 | `src/Mod/BIM/importers/importIFC.py` (+ `importIFCmulticore.py`) | Open (found during P2.2) | Both the single-core and multicore import paths set `ifcopenshell.geom.settings.USE_BREP_DATA`, which was removed in ifcopenshell 0.8 → `AttributeError`, so legacy IFC import fails entirely. P2.2 verifies the export via ifcopenshell instead of FreeCAD re-import. Needs the flag updated to the 0.8 API. |
| FU-5 | Structure export to IFC2X3 uses an IFC4-only entity | `src/Mod/BIM/importers/exportIFC.py` | Open (found during P2.2) | Exporting an Arch Structure to IFC2X3 raises `IfcCartesianPointList3D not found in schema IFC2X3` (a tessellation entity that only exists in IFC4). P2.2's structure test is restricted to IFC4. Needs a SweptSolid/faceted fallback for IFC2X3. |

### FU-2 — fixed (branch `fix/spreadsheet-gui-test`)
Not a "stale test needing rewrite" — four concrete defects:
- File missing from the module `CMakeLists.txt` → never copied to the build → dead.
- `view.select()` takes the selection flags as a plain int, but since the Qt6/PySide6 migration
  `QItemSelectionModel.SelectCurrent` is an enum that no longer converts to int → `TypeError`. Pass `.value`.
- Copy/paste went through `runCommand("Std_Copy"/"Std_Paste")`, which is **not routed to the spreadsheet
  view** in headless runs → clipboard stayed empty. Use `SendMsgToActiveView("Copy"/"Paste")` (verified:
  routes to the active view, clipboard gets `'1'`).
- `tearDown` never closed the document → the open MDI view kept the event loop alive → runner hung.

### FU-1 — partly fixed (branch `fix/nativeifc-selftest-bugs`)
Fixed (verified; `TestArch` still 273 OK, no regression):
- `ifc_materials.load_materials()`: `for child in group` → `obj.Group` (was an outright `NameError`).
- `ifc_tools.recompute()`: guard `c.touch()` against already-deleted objects (deferred QTimer callbacks).
- `ifc_status.on_activate()/set_menu()`: return early when `not FreeCAD.GuiUp` (GUI-only API was crashing
  the observer in console/test mode).
- `ifc_selftest.tearDown`: remove the document observer left installed by `test12` and drain pending
  deferred callbacks before closing the document.
Result: in **console** mode the suite now runs to completion (was aborting); in **GUI** mode all 20 tests
now execute (was hanging immediately).
**Still blocking enablement (needs a NativeIFC maintainer / deeper work — NOT auto-fixed):**
- **GUI-runner hang**: after the tests finish, deferred `QtCore.QTimer` callbacks (ArchSite sun position,
  view-provider icons, `onDocumentRestored` recompute) fire on torn-down documents and a ~1 s recompute
  loop keeps the event loop alive forever. Systemic across Arch/NativeIFC; risky to fix blindly.
- **`test09_CreateBIMObjects`**: asserts `ifco == 12` but the code now creates **14** `IfcRoot` entities —
  a stale count. Left unchanged: a maintainer must confirm whether 14 is correct or an over-creation bug.
- **`test11_ChangeGeometry`**: assumes `IfcObject004` is a plain extrusion and reads `ExtrusionDepth`,
  which `add_geom_properties` only adds for `IfcExtrudedAreaSolid`; the picked object isn't one. Data-dependent.

These came from the P0.1/P0.2 reclaim attempt; FU-2 is done, FU-1 delivered the safe bug fixes and
documented the remaining maintainer-level blockers.

---

## Current focus

> **Phases 0, 1 and 2 are done and pushed.** Phase 0: P0.4/P0.5/P0.6 + P0.1 reclaim (P0.3 awaits a
> human workflow-scope push; P0.2 blocked by FU-1). Phase 1: four numeric-core suites (29 tests).
> Phase 2: five data-exchange suites pushed (`test/exchange-step-iges-gltf`, `test/exchange-mesh-formats`,
> `test/spreadsheet-csv-xlsx`, `test/draft-dxf-corpus`, `test/exchange-ifc-roundtrip`) — 27 new tests,
> all green via `FreeCADCmd -t`.
> **Follow-up bugs:** FU-2 fixed; FU-1 partly fixed; FU-3 (mesh booleans), **FU-4** (legacy IFC import
> broken on ifcopenshell 0.8) and **FU-5** (IFC2X3 structure export uses IFC4-only entity) found in P1/P2.
> **Recommended next:** start **Phase 3** (zero-coverage modules: ReverseEngineering, Measure, Points,
> Robot/Inspection). All Phase-1/2 branches still need a human review + upstream PR per the AI policy;
> FU-1/FU-3/FU-4/FU-5 need the relevant maintainers.
> **Action needed from a human:** push `ci/run-binding-generator-tests` after granting the `workflow`
> OAuth scope (`gh auth refresh -h github.com -s workflow`), or apply that one-line workflow change via
> the GitHub web UI.

---

## Session Log

Append newest entries at the top. Format: `### YYYY-MM-DD — <who>`.

### 2026-06-22 — Phase 2 complete: data-exchange round-trips (5 branches pushed)
- **P2.1 STEP/IGES/glTF/BREP** (`test/exchange-step-iges-gltf`): headless `TestImportApp.py` (7 tests) —
  BREP exact (file + string), STEP near-exact, IGES via area/bbox, glTF export-file check, malformed
  STEP. glTF re-import is GUI-path-bound (export-only headless), noted in the test.
- **P2.3 Mesh** (`test/exchange-mesh-formats`): `MeshFormatTests.py` (10 tests) — PLY/OFF/SMF/OBJ exact
  point+facet counts, binary/ASCII STL agree, VRML asserted export-only, clean failure on missing/unknown.
- **P2.4 Spreadsheet** (`test/spreadsheet-csv-xlsx`): `TestSpreadsheetExchange.py` (5 tests) — CSV tab/
  comma round-trips, formula-as-value, a generated-on-the-fly minimal XLSX import, FCStd persistence.
- **P2.5 Draft DXF** (`test/draft-dxf-corpus`): replaced the fake-function export stub with two real
  C++-backend round-trips (line+circle edge lengths; multi-segment wire total length); no download.
- **P2.2 IFC** (`test/exchange-ifc-roundtrip`): `bimtests/TestArchIFCRoundTrip.py` (3 tests, run via
  TestArch → 276 total) — exports a wall/structure to IFC2X3+IFC4 and verifies schema/classes/spatial
  root with ifcopenshell. **Found FU-4** (legacy importer broken on ifcopenshell 0.8 — USE_BREP_DATA)
  and **FU-5** (IFC2X3 structure export uses the IFC4-only IfcCartesianPointList3D). Verified the export
  via ifcopenshell rather than FreeCAD re-import, and restricted the structure test to IFC4.
- All verified with `build/debug/bin/FreeCADCmd -t <module>`. The refined plan (`phase-2-data-exchange.md`)
  drove all five. Branches await human review + upstream PR.

### 2026-06-22 — Phase 1 complete: numeric-core test suites (4 branches pushed)
- **P1.1 PlaneGCS** (`test/sketcher-planegcs-core`): 8 known-answer GTest cases driving `GCS::System`
  directly (distance, coincident, point-on-line, L2L angle, circle+point-on-circle, zero-DoF, redundant,
  conflicting). All green via `pixi run ctest -R PlaneGCSSolverTest`.
- **P1.4 Mesh** (`test/mesh-repair-and-booleans`): 8 cases — repair (duplicate/degenerate/non-manifold/
  hole) + decimation are exact; **discovered FU-3** (built-in mesh booleans give wrong, non-watertight,
  run-varying volumes for trivial cubes) so the boolean tests were reduced to honest smoke checks.
- **P1.2 TechDraw HLR** (`test/techdraw-hlr-golden`): 7 golden ProjectionAlgos cases (cube front/iso,
  rectangular extent, cylinder side/end, through-hole along/across bore); edge counts calibrated and
  pinned. The iso cube gives the textbook 9 visible / 3 hidden.
- **P1.3 Assembly** (`test/assembly-solver-matrix`): filled the empty C++ test (empty assembly solves
  with DoF 0; getters only reachable in C++) + 4 Python cases (revolute/ball JCS-origin coincidence,
  fixed global-JCS identity, undo round-trip).
- Each verified with `pixi run ctest` (conda toolchain) / `FreeCADCmd -t TestAssemblyWorkbench`. The
  refined plan (`phase-1-numeric-cores.md`) drove all four. Branches await human review + upstream PR.

### 2026-06-22 — FU-1 + FU-2 fixes (`fix/nativeifc-selftest-bugs`, `fix/spreadsheet-gui-test`, pushed)
- **FU-2 fully fixed & enabled.** Diagnosed it was not a "stale rewrite" but four concrete defects
  (missing from CMakeLists; PySide6 enum-not-int `TypeError`; `Std_Copy`/`Std_Paste` not routed to the
  view headless — replaced with `SendMsgToActiveView`; `tearDown` never closed the doc → hang). Wired
  into CMakeLists + GUI `__unit_test__`. Verified green under xvfb. Branch pushed.
- **FU-1 partly fixed.** Found & fixed 4 genuine bugs (materials `group` NameError; `recompute()`
  deleted-object guard; `ifc_status` `GuiUp` guards; `ifc_selftest.tearDown` observer cleanup). Console
  run now completes; GUI run executes all 20 tests instead of hanging immediately. `TestArch` still
  273 OK (no regression). Branch pushed.
- **FU-1 not closed:** enabling the suite is still blocked by a systemic deferred-`QTimer` GUI hang
  (post-teardown callbacks on deleted objects + ~1 s recompute loop) and two stale assertions
  (`test09` count 14≠12, `test11` extrusion). Deliberately **not** masked — flagged for a NativeIFC
  maintainer. Details in the Follow-up bugs section above.

### 2026-06-22 — P0.1 GUI reclaim + P0.2 investigation (`test/reclaim-gui-and-ifc`, pushed)
- Verified the dormant GUI suites under xvfb (`xvfb-run FreeCAD -t <module>`):
  - **TestTreeSelection**: 3 tests OK → registered in `src/Mod/Test/InitGui.py`.
  - **TestSpreadsheetGui**: hangs/timeouts headless and was also missing from the Spreadsheet
    CMakeLists (never copied to the build). Reverted the registration + CMake change; logged as FU-2.
  - Material GUI (`TestMaterialsGui`) is **already registered** — the original report was wrong; no action.
- **P0.2**: discovered the NativeIFC self-test needs **no network** (embedded `IFCFILECONTENT`); the
  real blocker is a recursive-recompute hang (FU-1). Corrected the misleading "requires internet"
  comment in `src/Mod/BIM/InitGui.py`; kept the test disabled.
- Net: Phase 0 reclaim is done for everything that actually runs; two genuine bugs (FU-1, FU-2) are
  logged for separate fixes.

### 2026-06-22 — P0.4 + P0.6 done (Python in ctest)
- **P0.4 done** (`test/wire-python-into-ctest`, pushed; branched on top of `test/runner-fd-guard` so
  the suite is fd-robust): added a `Python_unittests` ctest entry running `FreeCADCmd -t 0`
  (label "Python", TIMEOUT 1800) in `tests/CMakeLists.txt`. Verified: `pixi run ctest -R
  Python_unittests` → Passed in 145s, rc=0.
- **P0.6 done** (same branch): `tryLoadingTest` now catches any load exception (not only
  `ImportError`) and reports it as a failing test, so a broken registered module can't abort suite
  construction.
- **Gotcha recorded** (now in Conventions): ctest must be run via `pixi run ctest`; the bare system
  ctest 3.28 fails on conda-CMake-4.2-generated GoogleTest includes ("CMake 3.30 or higher
  required"). Reconfigure with `pixi run configure` after editing `tests/CMakeLists.txt`.

### 2026-06-22 — P0.5 done (runner fd-guard)
- **P0.5 done** (`test/runner-fd-guard`, pushed): `src/Mod/Test/TestApp.py` `TestText` now runs the
  reporter on a private dup of fd 1 and restores fd 1 after every test (TestResult.stopTest hook).
- Demonstrated value: on `main` (no CAM fix) `FreeCADCmd -t 0` previously aborted after ~355 tests
  with `[Errno 9] Bad file descriptor`; it now runs to completion — **2445 tests OK** (14 skipped,
  6 expected failures, 0 errors). First run with only the report-stream protected still showed 2
  errors (`TestPathHelixGenerator.test00` etc.) from a `print()` on the closed fd left by
  `TestCAMSanity`; the per-test restore fixes that — that was the reason for the stopTest hook.
- This generically protects the whole suite against fd corruption, independent of the CAM-specific
  fix on `fix/cam-...`.

### 2026-06-22 — P0.1 first wave + P0.3
- **P0.3 done** (`ci/run-binding-generator-tests`, local only): added a CI step running the
  binding-generator tests from `src/Tools/bindings/tests`. Push blocked by missing `workflow` OAuth
  scope — needs a human to push or apply via web UI.
- **P0.1 partial** (`test/reclaim-dead-suites`, pushed): registered Spreadsheet `test_importXLSX`
  (3 tests, green) and FEM `TestSolverMystran` as `FemTest12`, guarded with `skipUnless(pyNastran)`
  (pyNastran is an optional dep absent in the pixi env → 7 tests skip cleanly instead of erroring).
- Verified locally: `-t test_importXLSX` 3 OK, `-t TestSpreadsheet` 87 OK, `-t TestFemApp` 97 OK
  (7 skipped). NB: `-t 0` still fails on this branch — that is the CAM `TestCAMSanity` fd-abort, which
  is fixed only on `fix/cam-...` (not on `main`), unrelated to these changes.
- **Remaining in P0.1:** GUI-side dormant suites (`TestTreeSelection`, Material GUI,
  `TestSpreadsheetGui`) need an xvfb run to verify (couple with P4.3); Draft DWG/OCA/AirfoilDAT
  importer suites need data/investigation; FEM `function_tests`/GUI; TemplatePyMod (template module,
  low value).

### 2026-06-22 — initial setup
- Created the roadmap coordination hub and the five per-phase implementation plans.
- Context: precursor work already merged-ready on branch `fix/cam-outputoptions-sanity-and-tests`
  (pushed to `origin` = holistech fork). It fixed CAM `OutputOptions` bugs, post-class resolution,
  `OUTPUT_UNITS` robustness, and the CAM `TestCAMSanity` fd-abort — the latter is the template for
  task **P0.5**, and reviving CAM's `TestOutputOptions`/`TestEmptyMoveSuppression` is the template
  for **P0.1**.
- All roadmap tasks are `Not started`. Recommended entry point: P0.1 + P0.3.
