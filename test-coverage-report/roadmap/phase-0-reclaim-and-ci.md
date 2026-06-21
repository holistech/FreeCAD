# Phase 0 — Reclaim dead tests & make CI trustworthy

**Goal:** make the existing test signal honest and complete before adding new tests. Until CI runs and
reports the Python suites and stops hiding failures, any new test can silently rot the same way the
CAM `TestOutputOptions` suite did (written, never registered, fully stale).

**Status:** see [COORDINATION.md](COORDINATION.md). **Dependencies:** none (do this phase first).
**Effort:** mostly S, one or two M.

---

## P0.1 — Register / re-enable dormant test suites

Many suites exist but are never imported/registered, so they never run.

Known dormant suites (verify each still exists; search for more with the recipe below):
- FEM: `test_solver_mystran` (missing `FemTest12` slot in `TestFemApp.py`), `function_tests`, disabled GUI tests.
- Spreadsheet: `test_importXLSX.py`, `TestSpreadsheetGui.py` (not in `Init.py __unit_test__`).
- Material: GUI appearance tests (not registered).
- Draft: commented-out DWG/OCA/AirfoilDAT importer suites in `drafttests/`.
- Gui: `TestTreeSelection.py` (not in `InitGui.py`).
- TemplatePyMod: working 7-method suite, unregistered.

**Approach:** for each, add the class/module to the module's `Init.py`/`InitGui.py` `__unit_test__`
list (or the module's `Test*App` aggregator). Run it; if it fails because it is *stale* (like the CAM
case), fix it to the current API or, if genuinely obsolete, delete it with a one-line rationale — do
not silently leave it dormant.

**Find candidates:**
```bash
# Test files that define TestCase classes but are never imported by a registered aggregator:
grep -rl "unittest.TestCase\|PathTestBase" src/Mod --include="Test*.py" --include="test_*.py"
grep -rn "__unit_test__" src/Mod/*/Init.py src/Mod/*/InitGui.py
# Disabled tests:
grep -rn "expectedFailure\|@unittest.skip\|# *FreeCAD.__unit_test__\|^# *from .*[Tt]est" src/Mod
```

**Acceptance:** every revived suite runs and is green (or is deleted as obsolete); `FreeCADCmd -t 0`
test count increases; no new failures.

## P0.2 — Offline IFC fixture + re-enable NativeIFC self-test

`src/Mod/BIM/nativeifc/ifc_selftest.py` (~20 tests) is the only real IFC round-trip test but is
disabled because it downloads a file over the network.

**Approach:** commit a small `.ifc` fixture under `src/Mod/BIM/.../TestData/` (or generate one in
`setUp` via ifcopenshell), point the self-test at it, and re-enable it offline in `InitGui.py`.

**Acceptance:** NativeIFC self-test runs offline and is green in `-t TestArch`/`-t TestArchGui`.

## P0.3 — CI runs the binding-generator tests

CI only discovers `src/Tools/tests`, so `src/Tools/bindings/tests/` (6 tests guarding the generator
that produces the *entire* C++↔Python API) never runs.

**Approach:** extend the CI step (the `python3 -m unittest discover` invocation in the build
workflows) to also discover `src/Tools/bindings/tests` and `src/Tools/typing` checks.

**Acceptance:** CI logs show the bindings tests executing.

## P0.4 — Wire the Python suites into ctest

Today `pixi run test` (ctest) covers only C++; a green ctest does **not** mean Python passed.

**Approach:** in `tests/CMakeLists.txt`, add one ctest entry per registered Python module, e.g.
`add_test(NAME py_<module> COMMAND FreeCADCmd -t <module>)`, with `QT_QPA_PLATFORM=offscreen` and the
appropriate working dir. Drive the module list from the same source as `FreeCAD.__unit_test__` (or a
small generated list). Mark GUI-only ones to run under the offscreen platform.

**Acceptance:** `ctest` runs both C++ and Python suites; one command reflects true project health.

## P0.5 — Runner-wide fd / teardown guard

Generalize the CAM `TestCAMSanity` fix (a native `close(1)` aborted the whole run). Protect the
shared runner so one misbehaving test cannot poison the rest.

**Approach:** in `src/Mod/Test/TestApp.py` (the `TestText`/run path), snapshot fd 1 (and fd 2) before
each test/module and restore with `os.dup2` afterward; optionally assert `os.fstat(1)` validity to
surface the offending test.

**Acceptance:** deliberately closing stdout inside a throwaway test no longer aborts `-t 0`.

## P0.6 — Fail CI on import-failed registered modules

`TestApp.tryLoadingTest` already degrades a missing/broken module into a failing `TestCase`. Make sure
that failure is **visible** in CI (non-zero exit / reported failure), so a broken registration can't
pass unnoticed.

**Acceptance:** a registered-but-unimportable module makes the suite (and CI) fail clearly.

---

## Suggested branches
- `test/reclaim-dead-suites` — P0.1 + P0.3 (+ P0.2 if the fixture is quick).
- `test/wire-python-into-ctest` — P0.4 + P0.5 + P0.6.

## Verification (whole phase)
```bash
pixi run build                       # copy changed .py
pixi run test                        # C++ (and Python once P0.4 lands)
build/debug/bin/FreeCADCmd -t 0      # full Python suite still completes; count went up
```
Update [COORDINATION.md](COORDINATION.md) (task rows, Last updated, Session Log) as tasks move.
