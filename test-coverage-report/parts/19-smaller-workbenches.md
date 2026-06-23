# Test Coverage — Smaller Workbenches

Scope: the remaining smaller FreeCAD workbenches/modules. For each, coverage is
estimated qualitatively (None / Low / Medium / High) from the presence and breadth
of registered unit tests, `Test*.py` files, and C++ tests under `tests/src/Mod/<Module>/`
or in-tree. No build was run; no measured percentages are reported.

## Surface (`src/Mod/Surface`)
Surface/blend-curve modelling workbench (filling, sections, blend curves, GeomFillSurface).
Tests: YES — `Surface/Init.py` registers `FreeCAD.__unit_test__ += ["TestSurfaceApp"]`;
`TestSurfaceApp.py` imports `SurfaceTests/TestBlendCurve.py`, which has a single test
method (`test_blend_curve`). Wired into the FreeCAD Python test runner.
Estimated coverage: **Low** — registered and runnable, but only one feature (blend curve)
of many is exercised.

## Inspection (`src/Mod/Inspection`)
Workbench for comparing/inspecting shape-vs-mesh deviation.
Tests: NO — no `Test*.py`, no `__unit_test__` registration, no C++ tests.
Estimated coverage: **None**.

## Robot (`src/Mod/Robot`)
6-axis robot simulation/trajectory workbench (Kuka export, trajectories).
Tests: NO — `RobotExample.py` / `RobotExampleTrajectoryOutOfShapes.py` are usage
example scripts, not unit tests; nothing registered, no C++ tests.
Estimated coverage: **None**.

## Web (`src/Mod/Web`)
Embedded browser / web-UI module (App only, no Gui Init test hooks).
Tests: NO — no `Test*.py`, no registration, no C++ tests.
Estimated coverage: **None**.

## Start (`src/Mod/Start`)
Start page / launcher workbench (recent files, examples, thumbnails).
Tests: YES (C++) — `tests/src/Mod/Start/App/` builds the `Start_tests_run` GTest target
(`GTest::gtest_main`). `FileUtilities.cpp` has ~11 `TEST_F` cases (human-readable size
formatting); `ThumbnailSource.cpp` is present in the target but currently carries no
active `TEST_F` cases. This is the only module in this group with real, build-wired C++ tests.
Estimated coverage: **Low–Medium** — solid coverage of file-size utility logic, but the
models (RecentFiles, Examples, CustomFolder, FcstdInfo) and Gui are untested.

## Show (`src/Mod/Show`)
Pure-Python temporary-visibility / scene-detail helper library (TempoVis, dependency-graph tools).
Tests: NO — no `Test*.py`, no registration, no C++ tests.
Estimated coverage: **None**.

## Cloud (`src/Mod/Cloud`)
Cloud storage / synchronization module (App + Gui).
Tests: NO — no `Test*.py`, no registration, no C++ tests.
Estimated coverage: **None**.

## Help (`src/Mod/Help`)
Python help-viewer module (`Help.py`, preferences dialog, CSS).
Tests: NO — `Help.py` contains zero `def test_`; nothing registered.
Estimated coverage: **None**.

## AddonManager (`src/Mod/AddonManager`)
Add-on / package manager. This is a **git submodule** (`.gitmodules`:
`https://github.com/FreeCAD/AddonManager.git`) and the directory is **not checked out**
in this working tree (empty), so no tests are present locally.
Note: the upstream AddonManager repository ships an extensive `AddonManagerTest` Python
suite; that coverage lives in the submodule and is not visible/runnable here until the
submodule is initialized.
Estimated coverage: **N/A locally** (upstream: **Medium–High** in submodule, not assessable here).

## Plot (`src/Mod/Plot`)
Python matplotlib-based 2D plotting workbench.
Tests: NO — `Plot.py` contains zero `def test_`; nothing registered, no C++ tests.
Estimated coverage: **None**.

## JtReader (`src/Mod/JtReader`)
C++ importer for Siemens JT files.
Tests: only nominal — `App/TestJtReader.{h,cpp}` exist and are compiled into the module,
but `TestJtReader` is a class derived from `JtReader` exposing a manual `read()` method
with **no GTest/CppUnit assertions** and no registration in any test runner. It is a
developer scratch/demo harness, not an automated test.
Estimated coverage: **None** (effectively).

## Tux (`src/Mod/Tux`)
GUI-only theme/customization helper (navigation indicator, persistent toolbars).
Tests: NO — no `Test*.py`, no registration, no C++ tests.
Estimated coverage: **None**.

## TemplatePyMod (`src/Mod/TemplatePyMod`)
Developer template / example collection demonstrating the Python module API.
Tests: PARTIAL — `Tests.py` defines `ParameterTestCase(unittest.TestCase)` with 7
`def testXxx` methods (parameter group/int/bool/float/string/nesting/export-import).
However it is **NOT** registered via `__unit_test__` in `Init.py`/`InitGui.py`, so it is
not run as part of the standard suite (it is a template example).
Estimated coverage: **Low** — tests exist but are not wired into the runner.

---

## Coverage Map

| Module | C++ tests? | Python tests? | Est. coverage | Notes |
|---|---|---|---|---|
| Surface | No | Yes (registered, 1 method) | Low | `TestSurfaceApp` → `TestBlendCurve.test_blend_curve` |
| Inspection | No | No | None | No tests at all |
| Robot | No | No | None | Example scripts only, not tests |
| Web | No | No | None | No tests at all |
| Start | Yes (GTest, ~11 TEST_F) | No | Low–Medium | `Start_tests_run`; FileUtilities covered, models/Gui not |
| Show | No | No | None | Pure-Python lib, untested |
| Cloud | No | No | None | No tests at all |
| Help | No | No | None | No tests at all |
| AddonManager | (submodule) | (submodule) | N/A locally | Not checked out; extensive suite upstream |
| Plot | No | No | None | No tests at all |
| JtReader | Stub only (no asserts) | No | None | `TestJtReader` is a manual harness, not registered |
| Tux | No | No | None | GUI-only, untested |
| TemplatePyMod | No | Yes (7 methods, NOT registered) | Low | Template example; not in test runner |

## Gaps & Risks (prioritized)

1. **Robot (None)** — non-trivial geometry/kinematics (trajectory generation, Kuka export);
   regressions in math/export are hard to catch manually. Highest functional risk among the untested.
2. **Inspection (None)** — numeric mesh-vs-shape deviation; silent accuracy regressions possible. High risk.
3. **JtReader (None / misleading)** — a C++ "test" file exists but asserts nothing and is
   compiled into the product. Risk of false confidence; binary file-format parser with no validation.
4. **Show (None)** — TempoVis is widely used by other workbenches (Assembly, PartDesign,
   TechDraw); breakage has broad blast radius despite the module being small.
5. **Surface (Low)** — registered but only one of many features tested; the rest of the
   surface-creation features are unverified.
6. **Start (Low–Medium)** — best in this group, but only the file-size utility is covered;
   `ThumbnailSource` is in the GTest target yet has no active cases; data models untested.
7. **TemplatePyMod (Low)** — working tests exist but are not registered, so they never run
   in CI; easy win to wire up (or intentionally excluded as a template).
8. **Cloud, Web, Help, Plot, Tux (None)** — lower-risk (UI/IO/glue), but zero safety net.

## Recommendations

1. Replace the JtReader stub with real GTest assertions on a small reference `.jt` fixture,
   or remove the dead harness from the build to avoid false coverage signals.
2. Add a minimal registered Python test for Robot (build a trajectory, assert waypoint count/values)
   and Inspection (deviation on a known shape/mesh pair) — highest risk-reduction per effort.
3. Expand `Surface/SurfaceTests` beyond blend curve to cover filling/sections/GeomFillSurface,
   reusing the already-wired `TestSurfaceApp` entry point.
4. Add `ThumbnailSource` GTest cases (the target already exists) and cover the Start data models.
5. Decide on TemplatePyMod's `Tests.py`: either register it via `__unit_test__` so it runs,
   or document it explicitly as a non-executed template.
6. Ensure the AddonManager submodule is initialized in CI so its upstream test suite actually
   runs against the integrated build.
7. For Show (TempoVis), add a small Python test given its heavy cross-workbench use.

## Quick Stats

- Modules reviewed: **13**.
- Zero automated tests: **8** — Inspection, Robot, Web, Show, Cloud, Help, Plot, Tux
  (**9** if counting JtReader, whose only "test" asserts nothing).
- Some Python tests: **3** — Surface (registered, 1 method), TemplatePyMod (7 methods, not registered),
  and (upstream-only) AddonManager.
- C++ tests: **1** — Start (`Start_tests_run`, ~11 `TEST_F`), the only build-wired C++ suite here.
- Registered into the FreeCAD Python test runner: **1** — Surface (`TestSurfaceApp`).
- Special cases: AddonManager (submodule, not checked out locally); JtReader (compiled stub, no assertions).
