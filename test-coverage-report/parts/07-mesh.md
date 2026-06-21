# Test Coverage — Mesh & MeshPart Workbenches

Scope: `src/Mod/Mesh/`, `src/Mod/MeshPart/`, and the C++ GoogleTest suites under
`tests/src/Mod/Mesh/` and `tests/src/Mod/MeshPart/`.
This is a structural/qualitative assessment. No build or run was performed; coverage
levels (None/Low/Medium/High) are estimated from the mapping of test cases to source
surface, not from measured line coverage.

---

## 1. Source Surface

### Mesh workbench (`src/Mod/Mesh/`)

The Mesh module is large and splits cleanly into a geometry kernel (`App/Core/`) and a
document/feature/Python-binding layer (`App/`).

**`App/Core/` — geometry kernel (~26 `.cpp` + headers + `Core/IO/`, ~36.8k LOC total):**

- **Mesh data structure / topology**: `MeshKernel.cpp` (~1.3k LOC), `Elements.cpp`,
  `TopoAlgorithm.cpp`, `Iterator.h`, `Visitor.cpp`, `Definitions.cpp`.
- **Spatial acceleration**: `Grid.cpp`, `KDTree.cpp`.
- **Algorithms**: `Algorithm.cpp` (ray/foraminate, projection, nearest facet),
  `Smoothing.cpp`, `Decimation.cpp`, `Simplify.h`, `Triangulation.cpp`,
  `Segmentation.cpp`, `SetOperations.cpp` (boolean), `Trim.cpp`, `TrimByPlane.cpp`,
  `Projection.cpp`, `Builder.cpp`, `Tools.cpp`.
- **Fitting / approximation**: `Approximation.cpp` (polynomial/plane/quadric),
  `CylinderFit.cpp`, `SphereFit.cpp`, `Curvature.cpp`.
- **Evaluation & repair**: `Evaluation.cpp` (manifold, orientation, self-intersection,
  duplicates), `Degeneration.cpp`, `Info.cpp`.
- **Import / export**: `MeshIO.cpp` (STL ascii/binary, OBJ, PLY, OFF, SMF, 3MF, Nastran,
  BMS, Inventor/VRML, X3D, AMF) plus `Core/IO/` readers/writers for 3MF, OBJ, PLY,
  Inventor.

**`App/` — feature/document/Python layer (~25 `.cpp`, ~12.7k LOC):**

- `Mesh.cpp` (`MeshObject`, ~2.3k LOC) — high-level mesh wrapper, transforms, boolean,
  smoothing, decimation entry points, grid evaluation.
- Document features: `FeatureMeshCurvature`, `FeatureMeshDefects`,
  `FeatureMeshImport/Export`, `FeatureMeshSegmentByMesh`, `FeatureMeshSetOperations`,
  `FeatureMeshSolid`, `FeatureMeshTransform(Demolding)`.
- `Importer.cpp` / `Exporter.cpp` — document-level multi-object import/export drivers.
- Python type bindings: `MeshPyImp`, `MeshFeaturePyImp`, `MeshPointPyImp`,
  `FacetPyImp`, `EdgePyImp`; `Segment`, `MeshProperties`, `MeshTexture`.
- `App/WildMagic4/` and `App/TestData/` are vendored/excluded data; mentioned for
  completeness, not audited.

### MeshPart workbench (`src/Mod/MeshPart/App/`, ~9 `.cpp`, ~5.3k LOC)

- `Mesher.cpp` / `Mesher.h` — meshing of OCC shapes via three backends:
  Mefisto (1), Netgen (2), Standard/SMESH (3).
- `MeshAlgos.cpp` — meshing helpers / shape-to-mesh utilities.
- `CurveProjector.cpp` — projection of curves/wires onto a mesh (curve-on-mesh).
- `MeshFlattening*.cpp` (`MeshFlattening`, `LscmRelax`, `Nurbs`) — surface flattening/
  unwrapping (LSCM), plus `MeshFlatteningPy.cpp` binding.

**Approximate file count in scope:** ~60 source `.cpp` files (Mesh App 25, Mesh Core 26,
MeshPart 9) plus their headers, the Gui layers of both modules (not in test scope), and
the `.pyi`/PyImp binding files.

---

## 2. Existing Tests

### C++ GoogleTest (build targets `Mesh_tests_run` / `MeshPart_tests_run`)

| File | Fixture | Cases | Purpose |
|---|---|---|---|
| `tests/src/Mod/Mesh/App/Core/KDTree.cpp` | `KDTreeTest` | 6 | KD-tree on empty tree, nearest (incl. max-dist), exact find, range find |
| `tests/src/Mod/Mesh/App/Mesh.cpp` | `MeshTest` | 5 | Default construction; `MeshGrid` building over planar / almost-planar meshes (two grid variants each) |
| `tests/src/Mod/Mesh/App/Importer.cpp` | `ImporterTest` | 2 | Document import of 3MF and OBJ from `DATADIR/tests/` |
| `tests/src/Mod/Mesh/App/Exporter.cpp` | `ExporterTest` | 3 | Export of single mesh, multiple meshes, meshes nested in a Part |
| `tests/src/Mod/Mesh/App/MeshFeature.cpp` | `MeshFeatureTest` | 2 | `getElementTypes` / `getComplexElementTypes` on a mesh feature |
| `tests/src/Mod/MeshPart/App/MeshPart.cpp` | `SMesh` | 2 | SMESH meshing of a box: MEFISTO 2D, and regular-1D StdMeshers (node/triangle counts) |

**C++ total: 20 test cases across 6 files** (Mesh 18, MeshPart 2).

### Python (`unittest`, registered via `src/Mod/Mesh/Init.py` → `FreeCAD.__unit_test__ += ["MeshTestsApp"]`)

Single file `src/Mod/Mesh/App/MeshTestsApp.py` (689 LOC), **42 `test*` methods** in 8
TestCase classes:

| Class | Cases | Purpose |
|---|---|---|
| `MeshTopoTestCases` | 4 | Facet collapse (single/multiple/all) and corrupted-facet handling (topology/repair) |
| `MeshSplitTestCases` | 9 | Splitting a facet on one/two edges in all permutations + multi-step split (`TopoAlgorithm`) |
| `MeshGeoTestCases` | 18 | `findNearest`, `foraminate` (+placement), and an extensive ray/segment **intersection** and **self-intersection** matrix (transformed, parallel, coplanar, overlap, collinear, warped, edge cases) |
| `LoadMeshInThreadsCases` | 2 | Build a sphere mesh; concurrent mesh loading (thread safety) |
| `PolynomialFitCases` | 3 | `Approximation` polynomial fit on good/exact/bad data |
| `NastranReader` | 4 | Nastran GRID parsing (8-char, delimited, 16-char/GRIDSTAR, CTRIA3) against `.bdf` fixtures |
| `MeshSubElement` | 5 | Center of gravity, sub-element extraction/counting, faces from sub-element, segment sub-element |
| `MeshProperty` | 1 | Mesh material property round-trip |

Fixtures: Nastran `.bdf` files in `App/TestData/`; binary test meshes (`mesh.3mf`,
`mesh.obj`) under the C++ test `DATADIR/tests/`.

---

## 3. Coverage Map

| Source area | Test assets | Est. coverage | Justification |
|---|---|---|---|
| KD-tree (`Core/KDTree`) | C++ `KDTreeTest` ×6 | **High** | Empty, nearest, max-dist, exact, range all exercised |
| Spatial grid (`Core/Grid`) | C++ `MeshTest` grid cases ×4 | **Medium** | Grid build tested on planar/near-planar only; non-planar/large meshes untested |
| Topology / split / collapse (`TopoAlgorithm`, `MeshKernel`) | Py topo ×4 + split ×9 | **Medium** | Good split/collapse permutation coverage; broader kernel mutation (insert/remove/merge) untested |
| Ray / intersection / nearest (`Algorithm`) | Py geo ×18 | **High** | Very thorough intersection & self-intersection matrix incl. degenerate cases |
| Approximation / fitting (`Approximation`) | Py `PolynomialFitCases` ×3 | **Low–Medium** | Polynomial fit only; plane/quadric, `CylinderFit`, `SphereFit`, `Curvature` untested |
| Import (`MeshIO`, `Core/IO`, `Importer`) | C++ Importer ×2 (3MF, OBJ); Py Nastran ×4 | **Low–Medium** | 3MF/OBJ/Nastran touched; STL (ascii+binary), PLY, OFF, SMF, VRML/Inventor, X3D, AMF, BMS untested |
| Export (`Exporter`, `MeshIO` writers) | C++ Exporter ×3 | **Low** | Driver paths (single/multi/in-Part) tested but format correctness/round-trip per format not asserted |
| Sub-elements / segments (`Segment`, `MeshObject`) | Py `MeshSubElement` ×5 | **Medium** | CoG, sub-element & segment extraction covered |
| Mesh properties / material | Py `MeshProperty` ×1; C++ `MeshFeature` ×2 | **Low–Medium** | Material + element-type queries only |
| Thread safety / load | Py `LoadMeshInThreadsCases` ×2 | **Low** | Single concurrency scenario |
| Smoothing (`Smoothing`) | — | **None** | No tests |
| Decimation / simplify (`Decimation`, `Simplify`) | — | **None** | No tests |
| Boolean / set operations (`SetOperations`, `FeatureMeshSetOperations`) | — | **None** | No tests |
| Trim / TrimByPlane / Projection | — | **None** | No tests |
| Segmentation (`Segmentation`) | — | **None** | No tests |
| Evaluation & repair (`Evaluation`, `Degeneration`) | indirect via Py self-intersection/corrupted-facet | **Low** | Manifold/orientation/duplicate/degenerate detection & fixers largely untested |
| Triangulation / Builder | — | **None** | No tests |
| Curvature (`Curvature`, `FeatureMeshCurvature`) | — | **None** | No tests |
| Transform / Demolding / Solid features | — | **None** | No tests |
| **MeshPart** meshing (`Mesher`) | C++ `SMesh` ×2 | **Low** | Only SMESH/MEFISTO + regular-1D on a box; Netgen and Standard backends, curved/complex shapes, hypotheses untested |
| **MeshPart** curve-on-mesh (`CurveProjector`) | — | **None** | No tests |
| **MeshPart** flattening (`MeshFlattening*`, LSCM) | — | **None** | No tests |
| Python type bindings (`MeshPyImp`, etc.) | partial via Py suite | **Low** | Exercised incidentally, not systematically |
| Gui layers (both modules) | — | **None** | Out of typical unit-test scope |

---

## 4. Gaps & Risks (prioritized)

1. **Mesh repair/healing pipeline untested (high risk).** `Evaluation.cpp` and
   `Degeneration.cpp` implement the manifold/orientation/duplicate/degenerate detectors
   and fixers that users rely on to clean imported meshes. Only indirect coverage exists
   (corrupted-facet, self-intersection). Regressions here corrupt user data silently.

2. **Boolean / set operations (`SetOperations`) have zero tests.** A complex,
   correctness-critical, numerically fragile algorithm with no safety net.

3. **Decimation and smoothing untested.** Core editing operations; silent quality/
   topology regressions would go unnoticed.

4. **Import/export format matrix is thin.** STL (the dominant mesh format), PLY, OFF,
   SMF, VRML/Inventor, X3D, AMF have no tests, and export tests assert driver flow rather
   than per-format round-trip fidelity. High user-facing impact.

5. **MeshPart meshing backends barely covered.** Only MEFISTO + regular-1D on a box;
   Netgen and the Standard (`createStandard`) path, plus curved/multi-face shapes and
   hypothesis combinations, are untested — and results are hardware/version-sensitive
   (hard-coded node counts may be brittle).

6. **MeshPart flattening (LSCM) and CurveProjector untested.** Mathematically involved
   features (`MeshFlattening*`, ~ several files) with no verification.

7. **Curvature, segmentation, trim, projection, transforms** — whole feature families
   with no tests.

8. **Fitting coverage narrow** — only polynomial fit; cylinder/sphere/curvature fitters
   unverified despite being used for reverse-engineering workflows.

---

## 5. Recommendations

1. Add a **MeshIO round-trip suite**: write a known mesh to each supported format and
   re-read it, asserting point/facet counts, bounding box, and (for ascii) byte stability.
   Prioritize STL ascii+binary, PLY, OFF.
2. Add **Evaluation/repair tests**: construct meshes with known non-manifold edges,
   flipped normals, duplicated points/facets, and degenerate triangles; assert detectors
   flag them and fixers produce a valid manifold.
3. Add **SetOperations tests** with simple analytic solids (two overlapping cubes/spheres)
   verifying volume/closedness of union/intersection/difference.
4. Add **decimation & smoothing tests** asserting invariants (facet-count reduction within
   tolerance, bbox preservation, no new non-manifold edges).
5. Expand **MeshPart Mesher** to cover Netgen and Standard backends and at least one
   curved shape; prefer tolerance-based assertions (ranges, watertightness) over exact
   node counts to reduce brittleness across SMESH/OCC versions.
6. Add focused tests for **CurveProjector** and **MeshFlattening (LSCM)** on small inputs
   with analytic expectations.
7. Broaden **fitting** tests to cylinder/sphere/curvature with synthetic sampled surfaces.
8. Consolidate Python tests: the single `MeshTestsApp.py` is healthy but monolithic;
   consider splitting by concern as new suites are added, keeping `Init.py` registration
   in sync.

---

## 6. Quick Stats

- **Source in scope:** ~60 `.cpp` files — Mesh App 25 (~12.7k LOC), Mesh Core 26 + IO
  (~36.8k LOC), MeshPart App 9 (~5.3k LOC); Gui layers and vendored `WildMagic4`/
  `TestData` excluded from audit.
- **C++ tests:** 6 files, **20 cases** (Mesh 18: KDTree 6, Mesh 5, Exporter 3, Importer 2,
  MeshFeature 2; MeshPart 2). Targets: `Mesh_tests_run` (BUILD_MESH),
  `MeshPart_tests_run` (BUILD_MESH_PART).
- **Python tests:** 1 file (`MeshTestsApp.py`, 689 LOC), **42 cases** in 8 TestCase
  classes; registered via `Init.py` (`__unit_test__ += ["MeshTestsApp"]`).
- **Total: ~62 test cases.**
- **Overall coverage estimate: Low–Medium.** Strong on KD-tree, ray/intersection
  geometry, and facet split/collapse topology; weak-to-absent on import/export formats,
  mesh repair/evaluation, boolean ops, decimation/smoothing, curvature/segmentation, and
  most of MeshPart (meshing backends, flattening, curve projection).
