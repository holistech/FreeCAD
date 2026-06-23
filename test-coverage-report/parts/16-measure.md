# Test Coverage — Measure Workbench

*Scope: `/home/soeren/src/FreeCAD/src/Mod/Measure/` and C++ tests `tests/src/Mod/Measure/`. Qualitative/structural assessment — no build was run, coverage is estimated, not measured.*

## 1. Source Surface

The Measure workbench provides interactive and scripted measurement objects (distance, angle, radius, diameter, length, area, position) plus mass-property analysis (center of mass, center of volume, inertia). It is split into an App (headless/logic) layer and a Gui (view providers, task panels, commands) layer, with a small Python overlay.

### App layer (logic — primary test target)

| Area | Files | Notes |
|------|-------|-------|
| Measurement core | `Measurement.cpp/.h` (1147 lines), `MeasurementPyImp.cpp`, `Measurement.pyi` | Legacy geometry-driven measurement engine; largest single source file. |
| Measure base / factory | `MeasureBase.cpp/.h`, `MeasureBasePyImp.cpp` | Base document object, selection validation, geometry handler registration. |
| Measurement types | `MeasureDistance` (468), `MeasureAngle` (543), `MeasureRadius` (192), `MeasureDiameter` (167), `MeasureLength` (162), `MeasureArea` (170), `MeasurePosition` (157) | Each is a `DocumentObject` with `isValidSelection`, recompute/`execute`, result properties. |
| Mass properties | `MassPropertiesObject.cpp/.h`, `MassPropertiesResult.cpp/.h` | COM / COV / inertia results. |
| Geometry resolution | `ShapeFinder.cpp/.h` (438), `SubnameHelper.cpp/.h` | Resolve sub-element references (links, placements, sub-shapes) to TopoDS shapes. |
| Module / Python init | `AppMeasure.cpp`, `AppMeasurePy.cpp`, `Preferences.cpp/.h` | |

Approx. App C++ files: ~24 (12 implementation pairs + Py imp/pyi).

### Gui layer (largely untestable headless, ~5,600 lines)

`TaskMeasure.cpp` (813), `TaskMassProperties.cpp` (1550), `QuickMeasure.cpp` (343, on-hover quick measurement), `Command.cpp` (129), view providers for base/distance/angle (`ViewProviderMeasure*`, `ViewProviderMassPropertiesResult`), `SoScreenSpaceScale.cpp` (Coin3D node), preference dialog `DlgPrefsMeasureAppearanceImp`.

### Python overlay

`Init.py` (24 lines, no logic), `InitGui.py` (workbench registration), `MeasureCOM.py` (159), `MassProperties.py`/`MassPropertiesGui.py`, `UtilsMeasure.py` (53). These hold light helper logic only.

## 2. Existing Tests

### C++ (GoogleTest)

- **`tests/src/Mod/Measure/App/MeasureDistance.cpp`** — fixture `MeasureDistance` (GTest `TEST_F`). Build target `Measure_tests_run`, gated by `BUILD_MEASURE` in `tests/CMakeLists.txt`. Links the `Measure` library.
  - `testCurvedFaceValidSelection` — regression for issue #29235; validates `MeasureDistance::isValidSelection` accepts sphere face + box face.
  - `testCurvedFaceDistance` — regression #29235; sphere-face to box-face distance == 15.0.
  - `testCircleCircle` — circle edge to circle edge: checks `Distance`, `DistanceX/Y/Z`, `Position1`, `Position2`.
  - **Case count: 3 `TEST_F`.**

### Python

- **No Python unit tests exist.** `Init.py` does **not** register `FreeCAD.__unit_test__`, and there are no `Test*.py` files anywhere under `src/Mod/Measure/`. `grep` for `def test_` returns nothing.
  - **Case count: 0.**

## 3. Coverage Map

| Component | Source | Test asset | Est. coverage |
|-----------|--------|-----------|---------------|
| MeasureDistance (face/edge, vertex, X/Y/Z, positions) | `MeasureDistance.cpp` | 3 C++ TEST_F | **Medium** (3 cases, incl. curved-face regression; misses vertex/line/plane combos) |
| MeasureAngle | `MeasureAngle.cpp` (543) | — | **None** |
| MeasureRadius / MeasureDiameter | `MeasureRadius.cpp`, `MeasureDiameter.cpp` | — | **None** |
| MeasureLength | `MeasureLength.cpp` | — | **None** |
| MeasureArea | `MeasureArea.cpp` | — | **None** |
| MeasurePosition | `MeasurePosition.cpp` | — | **None** |
| Measurement core engine | `Measurement.cpp` (1147) | indirect only | **Low** |
| MassProperties (COM/COV/inertia) | `MassProperties*.cpp` | — | **None** |
| ShapeFinder / SubnameHelper (sub-element resolution) | `ShapeFinder.cpp` (438) | indirect via distance test | **Low** |
| MeasureBase / selection / factory | `MeasureBase.cpp` | partial (isValidSelection for distance) | **Low** |
| Python API (MeasurementPyImp, MeasureBasePyImp) | `*PyImp.cpp` | — | **None** |
| Python helpers (MeasureCOM, UtilsMeasure) | `*.py` | — | **None** |
| Gui (tasks, view providers, QuickMeasure, commands) | `Gui/*.cpp` (~5,600) | — | **None** (hard to test headless) |

## 4. Gaps & Risks (prioritized)

1. **No coverage for 6 of 7 measurement types** (angle, radius, diameter, length, area, position). Angle (543 lines) and radius/diameter involve non-trivial geometry math and are entirely untested — high regression risk. *(High)*
2. **`Measurement.cpp` (1147 lines), the core engine, has no direct tests.** Only exercised indirectly through the distance object. *(High)*
3. **`ShapeFinder`/`SubnameHelper` (438+ lines) resolve sub-element references through links, sub-assemblies and placements** — a common source of bugs — yet are only touched incidentally by the simple distance cases. No tests for nested links, transformed placements, or App::Link chains. *(High)*
4. **MassProperties (COM, COV, inertia)** are completely untested; numerical correctness of inertia tensors is error-prone. *(Medium)*
5. **No Python-level tests and no `__unit_test__` registration**, so the scripted Measurement API (`MeasurementPyImp`, `MeasureBasePyImp`) and Python helpers are unverified and excluded from the test discovery harness. *(Medium)*
6. **Distance tests are happy-path only**: no vertex-vertex, vertex-face, parallel/intersecting planes, invalid/empty selection, or degenerate-geometry edge cases. *(Medium)*
7. **Entire Gui layer (~5,600 lines)** including QuickMeasure hover logic is untested; partly unavoidable headless, but selection-validation and value-formatting logic could be extracted and tested. *(Low)*

## 5. Recommendations

1. Add GTest fixtures mirroring `MeasureDistance.cpp` for **`MeasureAngle`, `MeasureRadius`, `MeasureDiameter`, `MeasureLength`, `MeasureArea`, `MeasurePosition`** — one file each, covering valid-selection + a known numeric result. Add each to `tests/src/Mod/Measure/App/CMakeLists.txt`.
2. Add **`ShapeFinder`/`SubnameHelper` unit tests** covering links, nested groups, and placement transforms with expected resolved world coordinates — the highest-value risk reduction.
3. Add **MassProperties tests** for a unit box / sphere with analytically known COM and inertia values (`EXPECT_NEAR`).
4. Expand distance tests with **negative/edge cases**: empty selection, single element, vertex-vertex, plane-plane.
5. Register a Python test suite (`TestMeasure.py`) via `FreeCAD.__unit_test__` in `Init.py` to exercise the scripting API and pull Measure into the standard Python test run.

## 6. Quick Stats

- App source files: ~24 C++ files (~5,400 lines logic, of which `Measurement.cpp` = 1147).
- Gui source: ~13 C++ files (~5,600 lines), no tests.
- Python files: ~7 (~330 lines logic), no tests.
- C++ test files: **1** (`MeasureDistance.cpp`); test cases: **3** `TEST_F`; build target `Measure_tests_run` (`BUILD_MEASURE`).
- Python test cases: **0**; no `__unit_test__` registration.
- Measurement types with any direct test: **1 of 7** (distance only).
- **Overall estimated coverage: Low.**
