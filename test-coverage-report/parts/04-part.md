# Test Coverage — Part Workbench

Scope: `src/Mod/Part/` (App, Gui, parttests/, TestPartApp.py, TestPartGui.py) and the
C++ GoogleTest suite under `tests/src/Mod/Part/`.

Method: structural/qualitative only. No build was run; no measured coverage percentages
are reported. Coverage is estimated as None/Low/Medium/High from the mapping of test
cases to source surface. Case counts are from `TEST`/`TEST_F` macros (C++) and
`def test_` definitions (Python).

---

## 1. Source surface

The Part workbench is large and OCCT-centric, split into an App (data/algorithm) layer
and a Gui (commands/dialogs/scene-graph) layer.

- **App** — ~140 `.cpp` files (~436 `.cpp`/`.h` total across the module).
  - **TopoShape & topology**: ~26 `TopoShape*.cpp` files (`TopoShape.cpp`,
    `TopoShapeExpansion.cpp`, `TopoShapePyImp.cpp`, edge/face/wire/solid/shell/vertex/
    compound element wrappers, element-map / naming support). This is the core data type.
  - **Geometry classes**: ~13 `Geom*.cpp` (`Geometry.cpp`, `Geometry2d.cpp`,
    `GeometryExtension`, B-spline curve/surface, conics, etc.).
  - **Primitives / Features**: `PrimitiveFeature.cpp` (box, cylinder, cone, sphere,
    torus, etc.), `FeaturePartBox.cpp`, `FeaturePartCircle.cpp`, `FeaturePartPolygon.cpp`,
    `FeaturePartSpline.cpp`, plus extrusion/revolution/offset/fillet/chamfer features.
  - **Boolean ops / BOPTools**: `FeaturePartBoolean.cpp`, `FeaturePartCommon.cpp`,
    `FeaturePartCut.cpp`, `FeaturePartFuse.cpp`, `FeaturePartSection.cpp`,
    `FCBRepAlgoAPI_BooleanOperation.cpp`; FaceMakers (`FaceMakerBullseye.cpp`,
    `FaceMakerCheese.cpp`, `FaceMakerBuildFace.cpp`); `WireJoiner`. Python-side BOPTools
    package adds the higher-level boolean feature wrappers.
  - **Attachment**: `Attacher.cpp`, `AttachExtension.cpp`, `AttachEngine*`.
  - **Import/export**: BREP/IGES/STEP feature importers.
  - **Python bindings**: ~55 `*PyImp.cpp` files — a very large Python-exposed API surface.
- **Gui** — ~79 `.cpp` files: commands (`Command*.cpp`), parametric/primitive dialogs
  (`DlgPrimitives`, `DlgExtrusion`, `DlgRevolution`, `DlgFilletEdges`,
  `DlgBooleanOperation`, `DlgProjectionOnSurface`, …), task panels (`TaskAttacher`,
  `TaskLoft`, `TaskOffset`, `TaskCheckGeometry`, `TaskFaceAppearances`), scene-graph
  nodes (`SoBrepFaceSet`, `SoBrepEdgeSet`, `SoBrepPointSet`, `SoFCShapeObject`),
  `CrossSections`, `SectionCutting`, `ShapeFromMesh`, `ReferenceHighlighter`.

---

## 2. Existing tests

### C++ (GoogleTest, `tests/src/Mod/Part/App/`) — gated by `BUILD_PART`, run via ctest as `Part_tests_run`

~276 test cases across 28 test source files (plus `PartTestHelpers.{h,cpp}` fixtures and
`brepfiles/` test data). Per file:

| File | Cases | Purpose |
|------|------:|---------|
| `TopoShapeExpansion.cpp` | 87 | Element-map / topological-naming expansion of TopoShape (largest suite) |
| `TopoShape.cpp` | 18 | Core TopoShape construction, queries, transforms |
| `FeatureExtrusion.cpp` | 16 | Extrusion feature behavior |
| `FaceMakerBullseye.cpp` | 16 | Bullseye face maker (nested wires → faces) |
| `TopoShapeCache.cpp` | 13 | TopoShape caching layer |
| `WireJoiner.cpp` | 12 | Joining edges into wires |
| `FeaturePartFuse.cpp` | 10 | Boolean fuse feature |
| `FeaturePartCommon.cpp` | 9 | Boolean common (intersection) feature |
| `PropertyTopoShape.cpp` | 8 | TopoShape property (de)serialization |
| `PartFeature.cpp` | 8 | Base Part::Feature behavior |
| `FeatureRevolution.cpp` | 8 | Revolution feature |
| `FeaturePartCut.cpp` | 8 | Boolean cut feature |
| `Attacher.cpp` | 8 | Attachment engine modes/computation |
| `TopoShapeMakeShapeWithElementMap.cpp` | 7 | Shape construction with element map |
| `PartFeatures.cpp` | 6 | Misc Part features |
| `TopoShapeMapper.cpp` | 5 | Element mapping helpers |
| `FuzzyBoolean.cpp` | 5 | Fuzzy-tolerance boolean operations |
| `TopoShapeMakeShape.cpp` | 4 | Generic make-shape operations |
| `TopoDS_Shape.cpp` | 4 | OCCT TopoDS_Shape wrapper assumptions |
| `FeatureFillet.cpp` | 4 | Fillet feature |
| `FeatureChamfer.cpp` | 4 | Chamfer feature |
| `BRepMesh.cpp` | 4 | BRep meshing |
| `FeatureOffset.cpp` | 3 | Offset feature |
| `AttachExtension.cpp` | 3 | AttachExtension property wiring |
| `FeatureMirroring.cpp` | 2 | Mirroring feature |
| `FeatureCompound.cpp` | 2 | Compound feature |
| `TopoShapeMakeElementRefine.cpp` | 1 | Refine element-map operation |
| `Geometry.cpp` | 1 | Geometry base class (minimal) |
| `FeaturePartBoolean.cpp` | 0 | Header/shared scaffolding only (no cases) |
| `PartTestHelpers.cpp` | 0 | Shared fixtures/utilities (`PartTestHelpers.h`) |

### Python (registered via `src/Mod/Part/Init.py` → `TestPartApp`, `src/Mod/Part/InitGui.py` → `TestPartGui`)

- `TestPartApp.py` — **74** `test_` methods in 18 `TestCase` classes. Covers B-spline
  curve/surface, curve-to-NURBS, surface normals, shape rotation, 2D circle, cone,
  ChFi2d (2D fillet/chamfer) algorithms, ruled surface, ShapeFix, BOP container
  (via `BOPTools.BOPFeatures`), geometry curve/edge/face edge cases, extrusion, and
  face-maker build-face. Also aggregates the parttests suites below via imports.
- `TestPartGui.py` — **2** `test_` methods locally; imports/aggregates the GUI parttests
  (`ColorPerFaceTest`, `ColorTransparencyTest`, `TaskFaceAppearancesTest`).
- `parttests/` (imported into the two suites above):
  - `TopoShapeTest.py` — **51** tests; broad TopoShape Python-API coverage (largest Py file).
  - `regression_tests.py` — **9** tests; reproduce specific fixed issues (e.g. #4456 Plane.Intersect).
  - `ColorPerFaceTest.py` — **5** tests (Gui); per-face color assignment.
  - `BRep_tests.py` — **3** tests; BRep construction/round-trip.
  - `ColorTransparencyTest.py` — **3** tests (Gui); per-face transparency.
  - `TestPartMirror.py` — **3** tests; mirroring regression.
  - `Geom2d_tests.py` — **2** tests; 2D geometry classes.
  - `TaskFaceAppearancesTest.py` — **1** test (Gui); face appearances task panel.
  - `TopoShapeListTest.py` — **1** test; TopoShape list property.
  - `part_test_objects.py`, `__init__.py` — helpers/fixtures (no test cases).

Total Python: ~76 in the two top-level files + ~78 in parttests ≈ **~154** `test_` methods
(GUI-tagged ones require a GUI session).

---

## 3. Coverage map

| Component | C++ tests? | Python tests? | Est. coverage | Notes |
|-----------|:---------:|:-------------:|:-------------:|-------|
| TopoShape core + Python API | Yes (heavy) | Yes (heavy) | **High** | `TopoShape*` (87+18+13+...) plus `TopoShapeTest.py` (51); best-covered area |
| Topological naming / element map | Yes (heavy) | Indirect | **High** | `TopoShapeExpansion`, `TopoShapeMapper`, `MakeShapeWithElementMap`, `MakeElementRefine` |
| Boolean ops (cut/fuse/common/section) | Yes | Yes (BOPTools) | **Medium–High** | Cut/Fuse/Common + Fuzzy covered; Section feature only indirectly; `FeaturePartBoolean.cpp` base has 0 cases |
| FaceMakers / WireJoiner | Yes | Partial | **Medium–High** | Bullseye (16) + WireJoiner (12); Cheese/BuildFace less directly tested |
| Primitives (box/cyl/cone/sphere/torus) | Partial | Partial | **Medium** | `PrimitiveFeature.cpp` not directly unit-tested; cone & circle2D in Python; most primitives only exercised indirectly |
| Geometry classes (curves/surfaces) | Minimal (1) | Yes | **Medium** | `Geometry.cpp` only 1 case; B-spline/NURBS/ruled-surface/Geom2d covered in Python |
| Extrusion / Revolution / Offset | Yes | Partial | **Medium–High** | Dedicated C++ suites (16/8/3) + Python extrusion tests |
| Fillet / Chamfer (3D + ChFi2d) | Yes | Yes | **Medium** | 4+4 C++ cases; ChFi2d algos in Python; thin given option matrix |
| Mirroring / Compound | Yes | Yes | **Medium** | 2+2 C++ cases, plus mirror regression Python |
| Attachment (Attacher/AttachExtension) | Yes | No | **Medium** | 8+3 C++ cases cover engine modes; no Python-level tests |
| ShapeFix / healing | No | Yes | **Medium** | `PartTestShapeFix` (large Python class); no C++ |
| Property serialization (PropertyTopoShape) | Yes | Indirect | **Medium** | 8 C++ cases |
| BRep meshing | Yes | No | **Low–Medium** | `BRepMesh.cpp` (4) |
| Import/export (BREP/IGES/STEP) | No (BREP fixtures only) | No | **Low** | Feature importers untested; brepfiles used only as input data |
| Gui commands / dialogs / task panels | No | Minimal | **Low** | Only color/appearance task panels tested; primitives/extrusion/revolution/fillet/boolean dialogs untested |
| Gui scene-graph (SoBrep* nodes, CrossSections, SectionCutting) | No | No | **None** | No automated tests |
| ShapeFromMesh / ProjectionOnSurface / CheckGeometry | No | No | **None–Low** | No targeted tests |

---

## 4. Gaps & risks (prioritized)

1. **Gui layer is almost entirely untested (High risk).** ~79 Gui `.cpp` files —
   commands, parametric/primitive dialogs, task panels, and `SoBrep*` scene-graph
   nodes — have essentially no automated coverage beyond color/appearance panels.
   Regressions in primitive/extrusion/revolution/fillet/boolean dialogs and selection
   highlighting would not be caught.
2. **Import/export untested (High risk).** STEP/IGES/BREP importer features have no
   tests; format round-trip and unit/precision handling are common bug sources.
3. **PrimitiveFeature parametric features lack direct unit tests (Medium).** Box,
   cylinder, sphere, torus, etc. are only exercised indirectly; parameter validation,
   placement, and recompute edge cases are under-covered.
4. **Geometry base/extension C++ coverage is thin (Medium).** `Geometry.cpp` has a
   single case despite a large `Geom*` surface; most geometry confidence rests on the
   Python suite.
5. **`FeaturePartBoolean.cpp` and `FeaturePartSection` base behavior (Medium).** The
   shared boolean base has 0 C++ cases; Section is only indirectly tested.
6. **Large Python-binding surface (~55 `*PyImp.cpp`) (Medium).** Well-covered for
   TopoShape and core geometry, but many Py wrappers (extensions, less-common geometry,
   attach engine) have little direct exercise.
7. **GUI-tagged Python tests require a display session (Low–Medium).** Color/transparency/
   appearance tests will be skipped in headless CI unless a virtual display is configured.

---

## 5. Recommendations

1. Add headless-friendly C++/Python tests for `PrimitiveFeature` parametric primitives
   (construction, parameter bounds, placement, recompute) — currently the biggest App
   gap with low effort to close.
2. Add import/export round-trip tests using small fixture files (extend the existing
   `brepfiles/` pattern to IGES/STEP) to guard the importers.
3. Introduce document-level Python tests for boolean Section and the shared boolean base,
   and broaden FaceMakerCheese/BuildFace coverage.
4. Expand C++ `Geometry.cpp` to match the breadth already present in the Python geometry
   suite (curves, surfaces, extensions), reducing reliance on Python-only coverage.
5. For the Gui layer, add logic-level tests for command/dialog parameter handling where
   separable from the widget (e.g. extrusion/revolution/fillet parameter assembly), and
   ensure GUI Python tests run under an offscreen/virtual display in CI.
6. Keep growing the regression suite (`parttests/regression_tests.py`) — pairing each
   fixed Part bug with a test is already established and effective.

---

## 6. Quick stats

- App source: ~140 `.cpp` files (~436 `.cpp`/`.h` total); Gui source: ~79 `.cpp` files.
- Python bindings: ~55 `*PyImp.cpp`.
- C++ tests: 28 test source files, **~276** `TEST`/`TEST_F` cases (`Part_tests_run`,
  gated by `BUILD_PART`); dominated by TopoShape/element-map (`TopoShapeExpansion.cpp` = 87).
- Python tests: `TestPartApp.py` 74 + `TestPartGui.py` 2 + parttests ~78 ≈ **~154**
  `test_` methods (some GUI-tagged, need a display).
- Best-covered: TopoShape core and topological naming (High). Weakest: Gui
  commands/dialogs/scene-graph and import/export (None–Low).
