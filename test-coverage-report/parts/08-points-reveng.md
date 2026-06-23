# Test Coverage — Points & ReverseEngineering

_Scope: `src/Mod/Points/`, `src/Mod/ReverseEngineering/`, and the C++ tests under
`tests/src/Mod/` for these modules. Qualitative/structural assessment only — no
build was run and no measured coverage percentages are claimed. Coverage is
estimated (None/Low/Medium/High) with justification._

## 1. Source Surface

### Points (`src/Mod/Points/`)
~93 files total; the App core is 19 `.cpp`/`.h` files, ~6,900 LOC. Build flag
`BUILD_POINTS`. Key responsibilities:

- **Point cloud data structure** — `Points.cpp/.h` (`PointKernel`, the central
  container; copy/move/swap/assign semantics), `Properties.cpp/.h`
  (per-point attributes: normals, colors, greyscale, intensity),
  `PropertyPointKernel.cpp/.h` (document property wrapping the kernel),
  `PointsFeature.cpp/.h` (document object + element-type API),
  `Structured.cpp/.h` (organized/structured point clouds with width/height grid),
  `PointsGrid.cpp/.h` (spatial grid / iterators for neighborhood queries).
- **Import/export of point formats** — `PointsAlgos.cpp/.h` defines a
  `Reader`/`Writer` class hierarchy:
  - Readers: `AscReader` (ASCII xyz), `PlyReader` (PLY, plain + properties),
    `PcdReader` (PCD, plain + properties + structured), `E57Reader` (E57, gated
    on optional library).
  - Writers: `AscWriter`, `PlyWriter`, `PcdWriter`.
- **Python bindings** — `Points.pyi` / `PointsPyImp.cpp` (`read`, `write`,
  `writeInventor`, `addPoints`, `copy`, `fromSegment`, `fromValid`, …),
  `AppPointsPy.cpp` module-level functions, `AppPoints.cpp` initialization.
- **Gui** — `Command.cpp`, `ViewProvider.cpp`, `Workbench.cpp`,
  `DlgPointsReadImp` (import dialog). Not in test scope but uncovered.

### ReverseEngineering (`src/Mod/ReverseEngineering/`)
~92 files total; App core is 8 algorithm `.cpp`/`.h` pairs, ~5,000 LOC. Build
flag `BUILD_REVERSEENGINEERING`. Most algorithms depend on optional third-party
libraries (PCL — Point Cloud Library, and OpenCASCADE B-spline math), so they
are conditionally compiled. Key responsibilities:

- **Surface fitting / approximation** — `ApproxSurface.cpp/.h` (B-spline
  surface approximation via least squares / parameter correction),
  `BSplineFitting.cpp/.h`, exposed through Python `approxSurface`, `approxCurve`,
  `fitBSpline`.
- **Triangulation / reconstruction** — `SurfaceTriangulation.cpp/.h`
  (greedy projection triangulation, Poisson reconstruction), Python
  `triangulate`, `poissonReconstruction`, `viewTriangulation`.
- **Segmentation** — `Segmentation.cpp/.h`, `RegionGrowing.cpp/.h`, exposed as
  `regionGrowingSegmentation`, `featureSegmentation`.
- **Model fitting / consensus** — `SampleConsensus.cpp/.h` (RANSAC plane,
  cylinder, sphere fitting via PCL SAC), Python `sampleConsensus`.
- **Python module** — `AppReverseEngineering.cpp` registers the nine keyword
  functions above; `Init.py`/`InitGui.py` register the workbench.
- **Gui** — `FitBSplineCurve`, `FitBSplineSurface`, `Poisson`, `Segmentation`,
  `SegmentationManual` dialogs + commands. Not in test scope, uncovered.

## 2. Existing Tests

### Points — C++ (GoogleTest, `tests/src/Mod/Points/App/`)
Registered via `tests/src/Mod/Points/App/CMakeLists.txt`
(target `Points_tests_run`, gated on `BUILD_POINTS`). **15 `TEST_F` cases**
across two fixtures:

- `Points.cpp` — fixture `PointsTest`, **13 cases**:
  - Data-structure semantics: `TestDefault`, `TestSize`, `TestCopy`,
    `TestMove`, `TestAssign`, `TestMoveAssign`, `TestSwap`.
  - Format round-trips / readers: `TestASCII`, `TestPlainPLY`,
    `TestPLYWithProperties`, `TestPlainPCD`, `TestPCDWithProperties`,
    `TestPCDStructured`. These exercise the reader/writer hierarchy
    (ASC, PLY plain + with properties, PCD plain + with properties +
    structured).
- `PointsFeature.cpp` — fixture `PointsFeatureTest`, **2 cases**:
  `getElementTypes`, `getComplexElementTypes` (document-object element API).

### Points — Python
**None.** No `Test*.py` files exist under `src/Mod/Points/`, and `Init.py`
does not register anything in `FreeCAD.__unit_test__`.

### ReverseEngineering — all tests
**NONE.** There is no `tests/src/Mod/ReverseEngineering/` directory (no C++
GoogleTest target, no `BUILD_REVERSEENGINEERING` test registration), and there
are no `Test*.py` files in the module. `Init.py` registers nothing in
`FreeCAD.__unit_test__`. Every algorithm (surface fitting, triangulation,
Poisson, segmentation, region growing, RANSAC consensus) is completely
**untested**.

## 3. Coverage Map

| Area | Source | Tests | Est. Coverage | Justification |
|------|--------|-------|---------------|---------------|
| Points: PointKernel value semantics | `Points.cpp` | 7 `TEST_F` | **High** | copy/move/assign/swap/size all exercised |
| Points: ASCII I/O | `PointsAlgos` (Asc) | `TestASCII` | **Medium** | round-trip covered; edge cases (malformed, large) not |
| Points: PLY I/O | `PointsAlgos` (Ply) | 2 cases | **Medium** | plain + properties covered; binary/endianness, errors not |
| Points: PCD I/O | `PointsAlgos` (Pcd) | 3 cases | **Medium-High** | plain, properties, structured covered |
| Points: E57 reader | `PointsAlgos` (E57) | none | **None** | optional-lib reader untested |
| Points: Structured cloud | `Structured.cpp` | via PCD structured | **Low** | indirect only; grid API not directly tested |
| Points: PointsGrid / neighbor queries | `PointsGrid.cpp` | none | **None** | spatial grid untested |
| Points: Properties (normals/colors) | `Properties.cpp` | indirect via I/O | **Low** | no direct property-API tests |
| Points: PropertyPointKernel (persistence) | `PropertyPointKernel.cpp` | none | **None** | save/restore round-trip untested |
| Points: PointsFeature element API | `PointsFeature.cpp` | 2 `TEST_F` | **Medium** | element-type queries covered |
| Points: Python bindings | `PointsPyImp.cpp` | none | **None** | no Python tests |
| Points: Gui (commands, dialogs, VP) | `Gui/*` | none | **None** | out of scope, untested |
| RE: ApproxSurface / B-spline fitting | `ApproxSurface`, `BSplineFitting` | none | **None** | no tests at all |
| RE: SurfaceTriangulation / Poisson | `SurfaceTriangulation` | none | **None** | no tests |
| RE: Segmentation / RegionGrowing | `Segmentation`, `RegionGrowing` | none | **None** | no tests |
| RE: SampleConsensus (RANSAC) | `SampleConsensus` | none | **None** | no tests |
| RE: Python module functions | `AppReverseEngineering.cpp` | none | **None** | 9 functions, all untested |

## 4. Gaps & Risks (prioritized)

1. **ReverseEngineering has zero tests (Critical).** Nine numerically
   sensitive algorithms (B-spline approximation, Poisson, RANSAC, region
   growing) have no regression safety net. These produce geometry whose
   correctness is hard to eyeball; silent regressions in fitting tolerance,
   pole counts, or convergence would go undetected. Heavy reliance on optional
   external libraries (PCL/OCC) also means behavior can drift with dependency
   versions with no test to catch it.
2. **Points persistence untested (High).** `PropertyPointKernel`
   save/restore (document round-trip) is the path most users depend on; a
   serialization regression would silently corrupt or lose point clouds.
3. **E57 reader untested (High).** A whole import format (and its optional-lib
   conditional path) has no coverage; format regressions ship unnoticed.
4. **No error / malformed-input tests (Medium).** All Points I/O tests use
   well-formed data. Truncated files, wrong headers, NaN coordinates, and
   binary-vs-ASCII PLY/PCD variants are unverified — these are common
   real-world failure modes.
5. **Spatial structures untested (Medium).** `PointsGrid` neighbor queries and
   the `Structured` grid API are only exercised indirectly; off-by-one and
   indexing bugs in nearest-neighbor logic would be invisible.
6. **No Python-level tests for either module (Medium).** The scripted API
   (`Points.read/write`, `reen.approxSurface`, etc.) — the primary automation
   surface — is entirely unverified.
7. **Gui layers uncovered (Low).** Commands/dialogs/view providers untested,
   consistent with the rest of FreeCAD; lower priority.

## 5. Recommendations

1. **Bootstrap ReverseEngineering tests.** Add a Python `TestReverseEngineering.py`
   registered in `Init.py` `FreeCAD.__unit_test__`, generating synthetic point
   sets with known ground truth (planar grid → `sampleConsensus(Plane)` should
   recover the plane normal; sampled cylinder → cylinder fit; analytic surface →
   `approxSurface` residual below tolerance). Guard each test with an
   availability check so it skips cleanly when PCL/OCC are absent.
2. **Add a `PropertyPointKernel` persistence test (C++).** Build a kernel with
   normals/colors, Save then Restore via the document, and assert byte/value
   equality — closes the highest-impact data-loss gap.
3. **Add an E57 reader test** behind the optional-library guard, mirroring the
   existing PLY/PCD round-trip pattern in `Points.cpp`.
4. **Add negative/edge-case I/O tests** for ASC/PLY/PCD: truncated file, bad
   header, NaN/Inf coordinates, and binary PLY/PCD variants.
5. **Add direct `PointsGrid` and `Structured` unit tests** (insert known
   points, assert neighbor-query results and grid dimensions).
6. **Add a Points Python smoke test** covering `read`/`write` round-trip and
   `addPoints`/`fromSegment`/`fromValid`.
7. **Register a `BUILD_REVERSEENGINEERING` C++ test target** (even minimal) so
   the module participates in CI like Points does.

## 6. Quick Stats

| Metric | Value |
|--------|-------|
| Points C++ test cases (`TEST_F`) | 15 (Points.cpp: 13, PointsFeature.cpp: 2) |
| Points C++ test fixtures | 2 (`PointsTest`, `PointsFeatureTest`) |
| Points Python test cases | 0 |
| ReverseEngineering test cases (any) | 0 |
| Points App source files (`.cpp`/`.h`) | 19 (~6,900 LOC) |
| ReverseEngineering App source files | 16 (~5,000 LOC) |
| Point formats with import tests | 3 of 4 (ASC, PLY, PCD; E57 none) |
| RE algorithms with tests | 0 of ~6 |
| Overall Points coverage estimate | Medium (strong data-structure + I/O core; gaps in persistence, grid, Python, Gui) |
| Overall RE coverage estimate | None |
