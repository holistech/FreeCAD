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
| 1 | De-risk numerical/geometry cores | [phase-1](phase-1-numeric-cores.md) | Not started | PlaneGCS, HLR, Assembly solver, Mesh repair |
| 2 | Data-exchange round-trips | [phase-2](phase-2-data-exchange.md) | Not started | STEP/IGES/glTF, IFC, mesh, CSV/XLSX, DXF |
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
| P1.1 | PlaneGCS solver unit suite | Not started | — | 2026-06-22 |
| P1.2 | TechDraw HLR golden tests | Not started | — | 2026-06-22 |
| P1.3 | Assembly solver matrix | Not started | — | 2026-06-22 |
| P1.4 | Mesh repair + boolean ops | Not started | — | 2026-06-22 |

### Phase 2 — Data-exchange round-trips
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P2.1 | STEP/IGES/glTF/BREP round-trip | Not started | — | 2026-06-22 |
| P2.2 | IFC2X3 + IFC4 round-trip | Not started | — | 2026-06-22 |
| P2.3 | Mesh formats round-trip | Not started | — | 2026-06-22 |
| P2.4 | Spreadsheet CSV + XLSX | Not started | — | 2026-06-22 |
| P2.5 | Draft DXF import corpus | Not started | — | 2026-06-22 |

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

| ID | Bug | Where | Notes |
|----|-----|-------|-------|
| FU-1 | NativeIFC self-test hangs in a recursive document-recompute loop | `src/Mod/BIM/nativeifc/ifc_selftest.py` | blocks P0.2; "Recursive calling of recompute for document IfcTest" repeats indefinitely. Test is offline-ready (embedded IFC); only the recompute loop blocks enabling it. |
| FU-2 | `TestSpreadsheetGui` hangs headless (and was never installed) | `src/Mod/Spreadsheet/TestSpreadsheetGui.py` | times out under `xvfb-run FreeCAD -t`; raises a cell-name/SelectionFlags arg error then never completes. Also missing from the module CMakeLists (not copied to the build). Likely a stale GUI test needing a rewrite. |

These came from the P0.1/P0.2 reclaim attempt; they are genuine bugs, out of scope for "reclaim", and should each get their own fix branch (Phase-1-style).

---

## Current focus

> **Phase 0 is effectively complete for everything achievable now.** Done & pushed: P0.4, P0.5, P0.6,
> P0.1 (all reclaimable suites). P0.3 is implemented but **awaits a human push** (workflow scope).
> P0.2 is **blocked by FU-1** (a real NativeIFC bug), not by missing fixtures.
> **Recommended next:** start **Phase 1** (P1.1 PlaneGCS), or opportunistically fix FU-1/FU-2.
> **Action needed from a human:** push `ci/run-binding-generator-tests` after granting the `workflow`
> OAuth scope (`gh auth refresh -h github.com -s workflow`), or apply that one-line workflow change via
> the GitHub web UI.

---

## Session Log

Append newest entries at the top. Format: `### YYYY-MM-DD — <who>`.

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
