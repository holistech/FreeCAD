# Phase 4 — GUI tests + coverage measurement

**Goal:** make progress *measurable* (real coverage numbers) and start covering the GUI layers that
are untested across nearly every workbench. P4.1 is the enabler that turns the whole roadmap from
qualitative to quantitative.

**Status:** see [COORDINATION.md](COORDINATION.md).
**Dependencies:** P4.1 is independent and can start immediately (parallel to Phase 1). P4.2/P4.3
benefit from Phase 0's ctest/CI work.
**Effort:** P4.1 M, P4.2 L, P4.3 M.

---

## P4.1 — Coverage-measurement target (the enabler)
**Where:** CMake presets + CI.

**Approach:**
- Add a coverage build flavor: `-DCMAKE_CXX_FLAGS="--coverage -O0"` +
  `-DCMAKE_EXE_LINKER_FLAGS="--coverage"` and `-DENABLE_DEVELOPER_TESTS=ON` (a `conda-linux-coverage`
  preset, or a `FREECAD_COVERAGE` option). Note: coverage flags invalidate ccache → expect a full rebuild.
- Run **both** layers so `.gcda` is produced: `ctest` **and** `FreeCADCmd -t 0`
  (+ `xvfb-run FreeCAD -t 0` for GUI once P4.3 lands).
- Aggregate C++ with `gcovr -r . --html-details` (or `lcov`+`genhtml`); aggregate Python with
  `coverage.py` run through the embedded FreeCAD interpreter, then `coverage html`.
- Add a CI job (can be non-blocking initially) that publishes the numbers, so each PR shows its
  coverage delta.

**Acceptance:** a single command/CI job produces per-module C++ and Python coverage percentages.
Once available, backfill the real numbers into `../README.md` §3 (replacing the heuristic ratings) and
record the baseline in [COORDINATION.md](COORDINATION.md).

**Tooling needed (not currently installed):** `lcov`/`gcovr`, `coverage.py` — add to `pixi.toml`.

## P4.2 — Shared Gui subsystem tests (offscreen)
**Where:** `src/Gui` — the Command framework, `TaskView`/task panels, the `ViewProvider` base
hierarchy, selection — see `../parts/03-gui.md`. These are exercised by nearly every workbench yet are
almost entirely untested (the one well-covered island is `StyleParameters`).

**Approach:** reuse the existing headless pattern — C++ via the `setup_qt_test` helper
(`QT_QPA_PLATFORM=offscreen`), Python via a live `FreeCADGui` session. Start with the highest-leverage
shared pieces (Command registration/execution, ViewProvider base lifecycle, selection gates) rather
than per-dialog tests.

**Acceptance:** the shared Gui infrastructure that every workbench depends on has a baseline of tests.

## P4.3 — Per-workbench GUI smoke tests under xvfb
**Where:** workbench `*Gui` test suites that need a real display — e.g. the 5 CAM
`TestPathToolBit*Widget` suites that abort headless with "Must construct a QApplication before a
QWidget" (`../parts/22-test-execution-results.md`), plus other registered-but-display-needing GUI tests.

**Approach:** add a CI job that runs `xvfb-run build/debug/bin/FreeCAD -t 0` (GUI binary + virtual
display) so GUI-registered suites actually execute; ensure local docs mention the `xvfb-run` pattern.
Make sure such tests are skipped (not errored) when no display is available, so headless
`FreeCADCmd -t 0` stays clean.

**Acceptance:** GUI-only suites run green under xvfb in CI; headless runs skip them cleanly.

---

## Suggested branches
- `ci/coverage-target` (P4.1) — highest leverage; start early.
- `test/gui-shared-subsystems` (P4.2)
- `ci/gui-tests-xvfb` (P4.3)

## Verification
```bash
# P4.1 (coverage flavor)
cmake --preset conda-linux-coverage && cmake --build build/coverage
ctest --test-dir build/coverage && build/coverage/bin/FreeCADCmd -t 0
gcovr -r . build/coverage --html-details -o coverage/index.html

# P4.2 / P4.3
ctest --test-dir build/debug -R Gui
xvfb-run build/debug/bin/FreeCAD -t 0
```
Update [COORDINATION.md](COORDINATION.md) as tasks move; record the first measured coverage baseline.
