# Test Coverage — Test Harness & Infrastructure

*Structural / qualitative review of the FreeCAD test machinery. No build was
performed; no measured coverage percentages are reported. All figures below are
file/registration counts obtained by static inspection of the source tree.*

FreeCAD runs **two largely independent test layers**:

1. A **Python `unittest` layer** driven from inside a running FreeCAD process
   (`src/Mod/Test/`), self-registered via `FreeCAD.__unit_test__` and launched
   with the `FreeCADCmd -t` / `FreeCAD -t` run-test flag.
2. A **C++ GoogleTest layer** (`tests/`) built only when
   `ENABLE_DEVELOPER_TESTS` is on, wired into **CTest** and invoked through
   `ctest` (`pixi run test`).

These two layers do not share a runner: C++ tests are in CTest, Python tests are
not. This split is the single most important structural fact about the harness.

---

## 1. Python test framework — `src/Mod/Test/`

The `Test` module is itself a FreeCAD workbench/module. Its `Init.py` /
`InitGui.py` run at startup and populate the global registry, and `TestApp.py`
provides the runner entry points.

### Runner — `TestApp.py`
- `All()` — builds a `unittest.TestSuite` from **every** name in
  `FreeCAD.__unit_test__`, using `tryLoadingTest()` which wraps each module name
  in a `LoadFailed` dummy `TestCase` on `ImportError` (so a missing/optional
  module reports as a clean test failure instead of aborting the whole run).
- `PrintAll()` — prints the registered test units and instructs the user to pass
  `0` for "all" (this is the listing shown when `-t` is given no argument).
- `TestText(s)` / `RunConfiguredTextTest()` — `RunConfiguredTextTest` reads the
  test name from `FreeCAD.ConfigGet("TestCase")` (set by the C++ `--run-test`
  handler) and runs it through a `TextTestRunner(verbosity=2)`, flushing stdout
  so results survive process teardown.
- Helpers: `Test(s)`, `testAll()`, `testUnit()`, `testDocument()`.

### Registration mechanism — `FreeCAD.__unit_test__`
`FreeCAD.__unit_test__` is a plain Python list owned by the App. Each module's
`Init.py` (and `InitGui.py` for GUI tests) appends the importable test-module
names it wants registered, e.g. the Test module's own `Init.py`:

```python
FreeCAD.__unit_test__ += [
    "BaseTests", "UnitTests", "Document", "Metadata",
    "StringHasher", "UnicodeTests", "TestPythonSyntax",
]
```

`InitGui.py` additionally appends the GUI/visual suites (`Workbench`, `Menu`,
`Menu.MenuDeleteCases`, `Menu.MenuCreateCases`, `GuiDocument`,
`TestRubberbandSelection`, `TestCoinSelectionVisual`, `TestCoinNodeSnapshots`,
`TestViewProviderLink`). Across the repo **28 `Init*.py` files** contribute to
`__unit_test__` (≈29 append statements), so each workbench self-declares its
Python tests; running `-t 0` aggregates all of them in one process.

### Core tests living directly in `src/Mod/Test/`
| File | Purpose |
|------|---------|
| `BaseTests.py` | Base-system Python bindings: Console, Vector/Matrix/Placement, parameters, units glue, etc. |
| `Document.py` (~112 KB) | The largest single suite: App document lifecycle — create/save/restore, transactions/undo, dependency graph & recompute, links, expressions, properties. |
| `UnitTests.py` | `FreeCAD.Units` quantity parsing, schema translation, imperial/SI conversions, formatting. |
| `Metadata.py` | `Metadata` (package.xml) parsing; consumes `TestData/*.xml` fixtures. |
| `StringHasher.py` | App `StringHasher` persistence/behavior. |
| `UnicodeTests.py` | Unicode handling across strings/properties. |
| `TestPythonSyntax.py` | Static guard that scans FreeCAD's Python sources for syntax errors. |
| `TestPerf.py` | Lightweight performance/timing smoke checks (not a benchmark gate). |
| `AutoSaverStress.py` + `RunAutoSaverStress.py` | Auto-save stress scenario and its standalone runner. |
| `GuiDocument.py` | GUI-side document/view-provider behavior. |
| `Workbench.py`, `Menu.py` | Workbench API and menu create/delete cases (GUI). |
| `TestGui.py`, `InitGui.py` | Test workbench UI, commands, toolbars, and GUI registration. |
| `TestCoinNodeSnapshots.py` (~63 KB) | **Visual regression**: renders curated Coin3D scene nodes offscreen to PNG and compares against checked-in baselines in `tests/visual/baselines/coin-nodes/`. |
| `TestCoinSelectionVisual.py` | Coin selection/preselection ordering visual check. |
| `TestRubberbandSelection.py`, `TestTreeSelection.py`, `TestViewProviderLink.py` | GUI selection / tree / view-provider-link behavior. |
| `testmakeWireString.py`, `testPathArray.py`, `testPathArraySel.py` | Misc geometry/UI helpers. |
| `unittestgui.py` | A bundled Tk-style unittest GUI runner (legacy convenience). |

The **visual snapshot harness** (`TestCoinNodeSnapshots.py`) is configurable via
environment variables: `FC_VISUAL_BASELINE_DIR` (baseline override),
`FC_VISUAL_UPDATE_BASELINE` (regenerate baselines),
`FC_VISUAL_MAX_MISMATCH_PCT` (default 0.20% mismatch tolerance). It refuses to
run without a headless QPA (`offscreen`/`minimal`/`eglfs`/`linuxfb`/`vnc`) or a
real display, and self-skips otherwise.

---

## 2. C++ GoogleTest wiring — `tests/`

Gated entirely behind `ENABLE_DEVELOPER_TESTS` (default `ON`, see
`InitializeFreeCADBuildOptions.cmake`). The root `CMakeLists.txt` only descends
into `tests/` when it is set:

```cmake
if (ENABLE_DEVELOPER_TESTS)
    include(CTest)
    enable_testing()
    find_package(GTest REQUIRED)
    add_subdirectory(tests)
endif()
```

### `tests/CMakeLists.txt`
- Defines a base `TestExecutables` list — `App_tests_run`, `Base_tests_run`,
  `Zipios_tests_run` — and **conditionally appends per-workbench executables**
  guarded by their `BUILD_*` options (`BUILD_GUI`, `BUILD_PART`,
  `BUILD_SKETCHER`, `BUILD_MESH`, `BUILD_PART_DESIGN`, `BUILD_MATERIAL`,
  `BUILD_MEASURE`, `BUILD_POINTS`, `BUILD_SPREADSHEET`, `BUILD_START`,
  `BUILD_TECHDRAW`, `BUILD_ASSEMBLY`, `BUILD_MESH_PART`). A workbench compiled
  out drops its test executable automatically.
- **Test discovery is platform-split:**
  - Non-Windows: `gtest_discover_tests(${exe})` (PRE_TEST discovery mode) — every
    `TEST()`/`TEST_F()` becomes an individual CTest case; binaries land in
    `${CMAKE_BINARY_DIR}/tests`.
  - Windows: `gtest_discover_tests` is **deliberately not used** (it must run the
    exe to enumerate tests, which fails because third-party DLLs are not on PATH
    during CMake configure). Instead each executable is registered as a **single
    `add_test(NAME ${exe} COMMAND ${exe})`**, with `ENVIRONMENT_MODIFICATION`
    prepending `bin/`, the conda/pixi `Library/bin`, and every `Mod/*` dir to
    PATH so DLLs/`.pyd` load. Consequence: on Windows CTest sees one coarse entry
    per binary, not per-test granularity.

### `setup_qt_test()` helper (`tests/src/CMakeLists.txt` level)
A `function(setup_qt_test)` builds Qt-based test executables (`AUTOMOC ON`):
for each name it creates `<name>_Tests_run`, links `FreeCADApp`, `FreeCADGui`,
`QtTest` (and `Python3_LIBRARIES` unless `BUILD_DYNAMIC_LINK_PYTHON`), and sets
the CTest property **`ENVIRONMENT "QT_QPA_PLATFORM=offscreen"`** plus label
`"Qt"` so GUI tests run headless. On Windows it additionally applies the PATH
`ENVIRONMENT_MODIFICATION`. `QtTest` itself is only required when
`ENABLE_DEVELOPER_TESTS` is set (`SetupQt.cmake`).

### Layout & link pattern
`tests/src/CMakeLists.txt` descends into `Base`, `App`, `Gui`, `Mod`,
`zipios++`. Each executable links `GTest::gtest_main` (+ `gmock_main` for App)
and the library under test (e.g. `Part_tests_run` links `Part`). Test data paths
are injected via compile definitions, e.g.
`target_compile_definitions(App_tests_run PRIVATE DATADIR="${CMAKE_SOURCE_DIR}/data")`.

### C++ test inventory (file counts, static)
| Area | `.cpp` test files |
|------|------------------:|
| `tests/src/Base` | 42 |
| `tests/src/App` | 25 |
| `tests/src/Gui` | 13 |
| `tests/src/Mod` (all) | 64 |
| **Total** | **146** |

Mod breakdown: Part 30, Material 7, Sketcher 7, Mesh 5, PartDesign 5,
Spreadsheet 2, Start 2, Points 2, Assembly 1, Measure 1, MeshPart 1, TechDraw 1.
The C++ layer is heavily weighted toward Base/App kernel and Part geometry; most
workbenches have only token C++ coverage.

---

## 3. How the two layers are invoked

- **C++ / GoogleTest → CTest.** `pixi run test` aliases `test-debug`, which runs
  `ctest --test-dir build/debug` (`test-release` → `build/release`). CTest
  executes the discovered gtest cases (per-test on Linux/macOS, per-binary on
  Windows).
- **Python → in-process run-test flag.** `Application::initConfig` registers the
  Boost.Program_options option `("run-test,t", ...)`. When `--run-test` (`-t`) is
  given, it sets `TestCase` (`0` → `TestApp.All`, empty → `TestApp.PrintAll`),
  `RunMode=Internal`, `ScriptFileName=FreeCADTest`, and `ExitTests=yes` (the
  variant `--run-open` keeps the GUI open). At run time the Internal mode invokes
  `TestApp.RunConfiguredTextTest`. So `FreeCADCmd -t 0` runs all registered
  Python tests headless; `FreeCAD -t 0` does the same inside the full GUI process
  (needed for the Coin/visual suites).

**The split:** CTest knows nothing about the Python suites; they are reached only
through the FreeCAD binary's own `-t` flag. CI must therefore run *both* `ctest`
*and* `FreeCAD(Cmd) -t 0` to exercise everything.

---

## 4. Test data management

- **`tests/data/`** — directory passed to C++ tests via the `DATADIR` compile
  definition (e.g. `App_tests_run`). (Currently sparse in the working tree.)
- **`tests/visual/`** — `baselines/coin-nodes/*.png` reference images for the
  visual-regression suite, plus `fonts/` (`NotoSans-Regular.ttf`) to make text
  rendering deterministic across machines.
- **`src/Mod/Test/TestData/`** — Python fixtures listed explicitly in the module
  `CMakeLists.txt` and copied next to the test sources at build time:
  `basic_metadata.xml`, `bad_root_node.xml`, `bad_xml.xml`, `bad_version.xml`,
  `content_items.xml`, `DXFSample.dxf`. Consumed by `Metadata.py` etc.
- **Per-module fixtures** — workbenches keep their own data near the code, e.g.
  `src/Mod/Mesh/App/TestData/`. There is no single central fixtures root; data is
  scattered between `tests/data`, `tests/visual`, and per-module `TestData/`
  folders, with copy-to-build handled ad hoc per `CMakeLists.txt`.

---

## 5. Assessment of the harness

### Strengths
- **Clean self-registration.** `FreeCAD.__unit_test__` + per-module `Init.py`
  means a workbench declares its own tests with one list append; `-t 0`
  aggregates everything with zero central wiring.
- **Robust optional-module handling.** `tryLoadingTest()`/`LoadFailed` converts
  missing optional modules into reported failures instead of crashing the run.
- **Proper CTest integration for C++** with per-test granularity on Linux/macOS
  via `gtest_discover_tests`, and `BUILD_*`-gated executables that track the
  build configuration automatically.
- **Headless GUI testing is designed in:** `QT_QPA_PLATFORM=offscreen` set both
  in `setup_qt_test()` (C++ Qt tests) and enforced by the Python visual suite.
- **Visual regression exists** with configurable tolerance, baseline-update mode,
  and bundled fonts for determinism — relatively advanced for a CAD project.

### Friction points / risks
- **Python tests are outside CTest.** `ctest` does not run any Python suite;
  they require a separate `FreeCAD(Cmd) -t 0` invocation. A green `pixi run test`
  does **not** mean the Python layer passed. This is the biggest gap.
- **No coverage measurement in-tree.** No `gcov`/`llvm-cov`/`coverage.py` wiring,
  no coverage target, no thresholds. Coverage can only be assessed structurally
  (as in this report).
- **Coarse Windows discovery.** Each C++ binary is one CTest entry on Windows, so
  failures report at executable granularity, not per-test — worse triage and no
  per-test parallelism there.
- **Flakiness risk in visual tests.** PNG snapshot comparison is sensitive to GL
  driver / Coin version / font rendering despite the 0.20% tolerance and bundled
  fonts; these suites need a stable headless GL stack to be trustworthy and are
  prime candidates for intermittent CI failures.
- **All-in-one-process Python run.** `-t 0` runs every registered suite in a
  single FreeCAD process; one suite that corrupts global state or crashes can
  take down or skew unrelated suites, and there is no per-suite isolation.
- **Scattered, ad-hoc test data.** No single fixtures root; copy rules are
  duplicated across `CMakeLists.txt` files.
- **Uneven C++ depth.** Base/App/Part are well covered at the unit level; most
  workbenches have 0–2 C++ test files and rely entirely on the Python layer.

### Coverage map — where each layer/run-mode is wired
| Layer / run-mode | Built by | Run by | In CTest? | Granularity | Headless |
|---|---|---|---|---|---|
| C++ GoogleTest (Base/App/Gui/Mod) | `ENABLE_DEVELOPER_TESTS` + `BUILD_*` | `ctest` / `pixi run test` | Yes | Per-test (Linux/mac); per-binary (Windows) | `offscreen` via `setup_qt_test` (Qt tests) |
| Python `unittest` core (`Init.py`) | `Test` module copy targets | `FreeCADCmd -t 0` | **No** | Per `TestCase` | Yes (Cmd) |
| Python GUI/visual (`InitGui.py`) | `Test` module (BUILD_GUI) | `FreeCAD -t 0` | **No** | Per `TestCase` | `QT_QPA_PLATFORM=offscreen` + bundled fonts |
| Visual baselines (`tests/visual`) | checked-in PNGs | via `TestCoinNodeSnapshots` | **No** (under Python run) | Per node/image | offscreen required |

---

## 6. Recommendations

1. **Register the Python suites with CTest.** Add a CTest entry that runs
   `FreeCADCmd -t 0` (and a GUI `FreeCAD -t 0` job under offscreen/xvfb) so a
   single `ctest` exercises both layers and CI cannot pass while Python tests are
   broken.
2. **Add a coverage target.** Wire `gcovr`/`llvm-cov` for C++ and `coverage.py`
   for the Python run behind an opt-in CMake option, and publish a coverage
   artifact — turning future versions of this report from structural to measured.
3. **Improve Windows discovery.** Investigate post-build `gtest_discover_tests`
   with the DLL PATH already populated, or generate per-test CTest entries from a
   manifest, to recover per-test granularity on Windows.
4. **Harden visual tests.** Pin the headless GL stack (e.g. llvmpipe) in CI,
   document a baseline-refresh workflow (`FC_VISUAL_UPDATE_BASELINE`), and
   consider quarantining them in a separate, non-blocking CTest label until
   stability is proven.
5. **Isolate Python suites.** Optionally run heavy/risky suites (Document,
   AutoSaverStress, visual) in their own FreeCAD subprocesses to contain crashes
   and global-state bleed.
6. **Consolidate test data.** Adopt a single fixtures convention and a shared
   CMake helper for copy-to-build to replace the per-module ad-hoc rules.
7. **Backfill C++ unit tests** for workbenches currently at 0–2 files, so they
   are not solely dependent on the (un-CTest-wired) Python layer.

---

## Quick stats
- **C++ gtest source files:** 146 — Base 42, App 25, Gui 13, Mod 64.
- **Mod C++ leaders:** Part 30, Material 7, Sketcher 7, Mesh 5, PartDesign 5.
- **Python test registrations:** ~29 append statements across **28 `Init*.py`**
  files feeding `FreeCAD.__unit_test__`.
- **Core Python suites in `src/Mod/Test/`:** ~25 files; largest is
  `Document.py` (~112 KB), then `TestCoinNodeSnapshots.py` (~63 KB).
- **Test-data fixtures:** `tests/data` (DATADIR), `tests/visual/baselines`
  (28 reference PNGs + fonts), `src/Mod/Test/TestData` (6 files), plus
  per-module dirs (e.g. `Mesh/App/TestData`).
- **Gating flags:** `ENABLE_DEVELOPER_TESTS` (C++ build), `BUILD_*` (per-WB test
  exe), `BUILD_TEST` (Python Test module).
- **Run entry points:** `pixi run test` → `ctest` (C++); `FreeCAD(Cmd) -t 0`
  → `TestApp.All` (Python).
