# Phase 1 — De-risk the numerical / geometry cores

**Goal:** put deterministic, analytically-verifiable tests around the engines whose silent
miscalculation corrupts user models. These are the highest-risk gaps in the codebase.

**Status:** see [COORDINATION.md](COORDINATION.md).
**Dependencies:** Phase 0 strongly recommended first (so new tests are actually run by CI and can't
go dormant). P4.1 (coverage target) is useful in parallel to measure progress.

Guiding principle: prefer **known-answer** tests (closed-form geometry, hand-computed expectations)
over snapshot/regression baselines, so a failure means "the math is wrong", not "the output changed".

> This plan was refined against the actual code (2026-06-22). Every target directory and GTest
> executable below **already exists**; adding tests is a `.cpp` file + one `target_sources`/`add_executable`
> line, never a new test binary. All C++ tests are gated by `ENABLE_DEVELOPER_TESTS=ON` and the module's
> `BUILD_*` flag, and must be run with `pixi run ctest` (conda toolchain), not the system ctest.

**Recommended order** (value ÷ risk): **P1.1 → P1.4 → P1.2 → P1.3.**
P1.1 and P1.4 are pure headless engines with closed-form expected values (cleanest wins). P1.2 needs a
one-time golden calibration of hidden-edge counts. P1.3 is the largest and partly needs new C++ assertions
because the solver diagnostics are not exposed to Python.

---

## P1.1 — PlaneGCS solver unit suite  *(effort: L)*

**Where:** `src/Mod/Sketcher/App/planegcs` (the constraint solver). Compiled **into** the `Sketcher`
shared lib (no separate planegcs library). Depends only on Eigen / boost.math / `Base::Console` — **no
App/Document/GUI** — so `GCS::System` can be instantiated directly in a GTest.

**Current coverage (verified):** only **2** C++ tests exist —
`tests/src/Mod/Sketcher/App/planegcs/GCS.cpp` (`GCSTest.clearConstraints`, bookkeeping only, no solve) and
`tests/src/Mod/Sketcher/App/planegcs/Constraints.cpp` (`ConstraintsTest.tangentBSplineAndArc`, one solve;
its own comments flag the 0.005 tolerance as too loose). Python `SketcherTests/TestSketcherSolver.py`
(19 tests) exercises the solver only through the high-level `SketchObject`/`Sketcher.Constraint` API,
never `GCS::System` directly. **The solver's own API is effectively untested.**

**Infrastructure to reuse:** append a new file to the existing target.
- `tests/src/Mod/Sketcher/App/planegcs/CMakeLists.txt`: add `target_sources(Sketcher_tests_run PRIVATE SolverNumeric.cpp)`.
- Links against `Sketcher` + `GTest::gtest_main` + `${Python3_LIBRARIES}` (already wired in
  `tests/src/Mod/Sketcher/CMakeLists.txt`).
- Classes are exported via `SketcherExport`. Existing tests define a local `SystemTest` subclass to reach
  the `protected` `_getNumberOfConstraints` — reuse that pattern.

**Minimal API sequence (verified signatures):**
```cpp
GCS::System sys;
double p1x=0,p1y=0, p2x=5,p2y=0;                 // parameters live in the test, solver holds pointers
GCS::Point p1(&p1x,&p1y), p2(&p2x,&p2y);
double d=10.0;
sys.addConstraintP2PDistance(p1, p2, &d, /*tagId*/1);
GCS::VEC_pD params{&p1x,&p1y,&p2x,&p2y,&d};
sys.declareUnknowns(params);
sys.initSolution(GCS::DogLeg);
int dof = sys.dofsNumber();                       // -1 until diagnosed
sys.getConflicting(/*VEC_I&*/...); sys.getRedundant(...);   // hasConflicting()/hasRedundant()
int status = sys.solve(params, true, GCS::DogLeg);// Success=0,Converged=1,Failed=2,...
if (status==GCS::Success) sys.applySolution();    // writes results back into the doubles
double err = sys.calculateConstraintErrorByTag(1);
```
Useful adders: `addConstraintP2PCoincident`, `addConstraintPointOnLine`, `addConstraintP2LDistance(...,ccw)`,
`addConstraintL2LAngle`, `addConstraintCircleRadius`, `addConstraintPointOnCircle`,
`addConstraintCoordinateX/Y`, `addConstraintParallel/Perpendicular`, `addConstraintEqual`.

**Cases (8). Pin enough `CoordinateX/Y` to reach DoF=0 so the solution is unique; assert with `EXPECT_NEAR`, tol ~1e-6:**
1. **P2P distance** — p1 fixed (0,0), p2 on x-axis, distance 10 → p2→(10,0).
2. **P2P coincident** — p1 fixed (3,4) → p2→(3,4); `dofsNumber()==0`.
3. **Point-on-line + P2L distance** — line = x-axis, q.x fixed 4, distance 3, ccw → q→(4,3); flip ccw → (4,-3).
4. **L2L angle** — two lines, shared fixed point, angle π/2 → dot(dir1,dir2)≈0.
5. **Circle radius + point-on-circle** — center (0,0), r=5, p.x fixed 3 → p→(3,±4); invariant px²+py²=25.
6. **Well-posed DoF diagnosis** — fully-constrained rectangle → `dofsNumber()==0`, no conflict, no redundant.
7. **Redundant set** — same P2PDistance twice (different tags) → `solve==Success`, `hasRedundant()`, `getRedundant()` non-empty.
8. **Conflicting set** — two contradictory distances (10 and 20) on one pair → `hasConflicting()`, solve ≠ Success for both; `calculateConstraintErrorByTag` as residual.

**Acceptance:** solver behaviour is pinned by analytic expectations; conflict/redundancy diagnostics
return the constructed tag sets.

## P1.4 — Mesh repair + boolean operations  *(effort: M)*

**Where:** `src/Mod/Mesh/App/Core` (Evaluation.h, Degeneration.h, SetOperations.h, Decimation.h) and the
`Mesh::MeshObject` high-level wrappers. Headless (MeshCore is GUI-free; `tests::initApplication()` only
needed once `MeshObject`/volume is used).

**Current coverage (verified):** **18** C++ tests — `App/Core/KDTree.cpp` (6), `App/Mesh.cpp` (5,
kernel build + facet grid), `MeshFeature.cpp` (2), `Importer.cpp` (2), `Exporter.cpp` (3). **Repair
(MeshEval*/MeshFix*), boolean (SetOperations / unite·intersect·subtract) and decimation are entirely
untested in C++.** (Python `MeshTestsApp.py` has some intersection/topology checks but no volume booleans
and no decimation.)

**Infrastructure to reuse:** add `.cpp` under `tests/src/Mod/Mesh/App/` (or `App/Core/`) to the
`add_executable(Mesh_tests_run ...)` list in `tests/src/Mod/Mesh/App/CMakeLists.txt`. Links against `Mesh`.

**Minimal API:**
```cpp
auto* a = Mesh::MeshObject::createCube(2,2,2);          // 12 facets / 8 points, volume 8
// defined defects: fill MeshPointArray + MeshFacetArray (indices) and kernel.Adopt(points, facets);
MeshCore::MeshEvalDuplicatePoints(k).Evaluate();        // false if defect present
MeshCore::MeshFixDuplicatePoints(k).Fixup();
a->isSolid(); a->hasNonManifolds(); a->hasSelfIntersections();
a->getVolume(); a->countFacets(); a->countPoints();
MeshObject* u = a->unite(*b);  a->intersect(*b);  a->subtract(*b);
a->decimate(tolerance, reduction);  // or decimate(targetSize)
```

**Cases (9). Repair via known defects, booleans with closed-form volumes:**
1. **Duplicate points** — Adopt two identical coords → `MeshEvalDuplicatePoints` false; after `Fixup`,
   true, `CountPoints()-1`, facets unchanged.
2. **Non-manifold edge** — 3 facets sharing one edge → `hasNonManifolds()` true; after `removeNonManifolds()`, false.
3. **Self-intersection** — two interpenetrating triangle groups → `hasSelfIntersections()` true; after fix, false.
4. **Hole / not solid** — `createCube(1,1,1)`, delete one facet → `isSolid()` false, `countFacets()==11`;
   after `fillupHoles(...)`, solid, 12 facets.
5. **Degenerate facet** — append collinear-point facet → `MeshEvalDegeneratedFacets` false; after `Fixup`, removed.
6. **Union** — two 2³ cubes overlapping by 1×2×2 → `unite`, volume ≈ 12 (8+8−4), solid.
7. **Difference** — same pair, `subtract` → volume ≈ 4, solid.
8. **Intersection** — same pair, `intersect` → volume ≈ 4.
9. **Decimation** — `createSphere(10,50)`, `decimate(0.1,0.5)` → ~½ facets, still solid/no non-manifolds,
   volume within ±2 % of original.

**Acceptance:** the repair pipeline and set operations are guarded against silent corruption with exact
volume/topology expectations (relative tol ~1e-3 for booleans).

## P1.2 — TechDraw HLR golden tests  *(effort: M)*

**Where:** `src/Mod/TechDraw/App` — `ProjectionAlgos`, `GeometryObject`, `EdgeWalker`, `DrawUtil`.
HLR runs OCCT `HLRBRep_Algo` directly on a `TopoDS_Shape`; **no Document needed** (only
`tests::initApplication()` for Base/Console, as in the existing `LineFormat.cpp`).

**Current coverage (verified — corrects the original plan):** the only C++ test file is
`tests/src/Mod/TechDraw/App/LineFormat.cpp` (2 tests, colour/alpha only). **There is no C++ box smoke test
and nothing exercises HLR.** The "box test" is Python (`TDTest/DrawProjectionGroupTest.py`) and asserts
only `"Up-to-date" in group.State` — no edge counts, no endpoints, no visibility. HLR geometry is wholly
unverified.

**Infrastructure to reuse:** add `.cpp` to `add_executable(TechDraw_tests_run ...)` in
`tests/src/Mod/TechDraw/App/CMakeLists.txt`. Links against `TechDraw` (+ `Part` if using `GeometryMatcher`).

**API — prefer `ProjectionAlgos` for golden endpoints (no Y-inversion, no overlap scrubbing):**
```cpp
TopoDS_Shape box = BRepPrimAPI_MakeBox(10.,10.,10.).Shape();
TechDraw::ProjectionAlgos algos(box, Base::Vector3d(0,0,1));   // HLR runs in the ctor
// visible compounds: V (hard) VO (outline) VN (contour) V1 (smooth) VI (iso); hidden: H HO HN H1 HI
int nVis = TechDraw::DrawUtil::countSubShapes(algos.V, TopAbs_EDGE);   // guard IsNull() first
// endpoints via TechDraw::ShapeUtils::getEdgeEnds(edge)
```
Use `GeometryObject::projectShape(shape, ShapeUtils::getViewAxis(origin,dir))` for the production path
(includes Y-inversion + `getEdgeGeometry()` TD conversion) on one mirrored case.

**Cases (golden). Assert visible-edge counts exactly; hidden counts only after one-time calibration
(OCCT emits coincident front/back edges) — before calibration assert `>=` or bounding-box.**
1. Box(10³), dir (0,0,1) → `V`==4 (face square). Calibrate `H`.
2. Box(10,20,30), dir (0,0,1) → `V`==4, endpoints (0,0),(10,0),(10,20),(0,20) (axis/scale mapping).
3. Box(10³), dir (1,1,1) iso → `V`==9 (hexagon silhouette + 3 front edges), `H`==3 (back-corner edges) — the discriminating visible-vs-hidden test.
4. Cylinder(r5,h20), dir (0,1,0) side → 2 outline verticals in `VO` + top/bottom as lines; separates `VO`/`V`/`H`.
5. Cylinder(r5,h20), dir (0,0,1) end → `V`/`VO` one circle; bbox X,Y∈[-5,5].
6. Box(20³) `Cut` Cylinder(r5,h20) on Z (through-hole), dir (0,0,1) → `V`==4 outline + 1 front hole circle.
7. Same, dir (0,1,0) across the bore → `H`>=2 (back bore-wall edges hidden) — strongest hidden-line test.
8. Two boxes fused into an L-profile, dir (0,0,1) → `V`==6; optional `EdgeWalker::execute` → 1 closed wire of 6 edges.

Also add pure-unit tests for document-free `DrawUtil` helpers (`countSubShapes`, `angleWithX`,
`intersect2Lines3d`, `fpCompare`, …) and `EdgeWalker` (takes a `std::vector<TopoDS_Edge>`).

**Acceptance:** a wrong visible/hidden classification or projection vector fails a test. Record the
calibrated hidden-edge counts in the test as named constants with a comment on the OCCT coincidence.

## P1.3 — Assembly solver matrix  *(effort: L)*

**Where:** `src/Mod/Assembly/App/AssemblyObject.cpp` (the Ondsel-solver bridge). Ondsel is a vendored
**C++** library (`src/3rdParty/OndselSolver`) linked into `Assembly` — there is **no Python solver module**.

**Current coverage (verified):** the single C++ test `tests/src/Mod/Assembly/App/AssemblyObject.cpp`
(`AssemblyObjectTest.createAssemblyObject`) has an **empty body** — but its fixture already builds a doc +
`AssemblyObject` + `JointGroup`. Python `AssemblyTests/TestCore.py` has 7 tests (+2 in
`TestCommandInsertLink.py`), all `Part::Box`; only `test_solve_assembly` touches the solver (one Fixed
joint) and it doesn't even call `solve()` explicitly (relies on `setJointConnectors` → `solveIfAllowed`).

**Key constraint (drives the design):** DOF / conflict / redundancy are exposed **only via C++ getters**
(`getLastDoF()`, `getLastHasConflicts()`, `getLastHasRedundancies()`, `getLastConflicting()`, …, inline in
`AssemblyObject.h`) — **not** in the Python API. `solve(bool)` returns only `0` (ok), `-1` (solver
exception), `-6` (nothing grounded) — the `-2..-5` codes in the `.pyi` docstring are not produced. So:
**DOF/over-constraint/redundancy assertions must live in the C++ GTest; Python tests can only assert
resulting placements.**

**Joint types — 13 (not 12)**, from `AssemblyUtils.h` `enum class JointType` (mirrored in `JointObject.py`
`JointTypes`, index == enum): Fixed, Revolute, Cylindrical, Slider, Ball, Distance, Parallel,
Perpendicular, Angle, RackPinion, Screw, Gears, Belt.

**API:**
- C++ solve: `int AssemblyObject::solve(bool enableRedo=false)` (builds `makeMbdAssembly()`, `fixGroundedParts`,
  `runPreDrag()`, `setNewPlacements()`, `updateSolveStatus()`). Drag round-trip: `preDrag` → `doDragStep` →
  `postDrag`; undo: `solve(true)` → `undoSolve()` → `clearUndo()` (these three are also exposed to Python).
- Python build (from `TestCore.test_solve_assembly`): `addObject("Assembly::AssemblyObject")`;
  `newObject("Assembly::JointGroup")`; two `Part::Box`; `JointObject.GroundedJoint(g, box2)`;
  `JointObject.Joint(j, type_index)`; `j.Proxy.setJointConnectors(j, refs)`; read `box.Placement`.

**Cases:**
- **C++ GTest (fill the empty test):** per representative joint, a minimal two-box assembly (box2 grounded
  at identity) with analytic post-solve placement **and** the expected residual DOF via the getters:
  Fixed → `box1.Placement == box2.Placement`, DoF 0 (port the existing Python baseline);
  Revolute → coincident JCS origins, collinear Z, `getLastDoF()==1`;
  Slider → parallel axes, DoF 1; Cylindrical → DoF 2; Ball → coincident origin, DoF 3;
  Distance d → offset == d along the JCS normal; Angle θ → axis angle == θ.
  Status cases: no grounded part → `solve()==-6`; degenerate JCS → `solve()==-1`;
  duplicate identical joints → `getLastHasRedundancies()`, `getLastRedundant()` lists the joint;
  fully constrained → `getLastDoF()==0`, no conflicts.
- **Python (`TestCore`):** the placement-level cases above (Fixed/Revolute/Slider/Distance) asserting
  `Placement.isSame(expected, 1e-6)`, plus a `solve(True)` → `undoSolve()` → `clearUndo()` placement round-trip.
- Gears / RackPinion / Screw / Belt are ratio/motion joints → cover via a simulation step, not a static placement.

**Acceptance:** per-joint kinematics asserted at the placement level (Python + C++) and DOF/over-constraint/
redundancy asserted via the C++ getters; the empty C++ test is replaced with real assertions.

---

## Suggested branches
- `test/sketcher-planegcs-core` (P1.1; can split into convergence vs. diagnostics)
- `test/mesh-repair-and-booleans` (P1.4)
- `test/techdraw-hlr-golden` (P1.2)
- `test/assembly-solver-matrix` (P1.3)

## Verification
```bash
export PATH="/home/soeren/.pixi/bin:$PATH"
pixi run configure   # only needed after editing a tests/.../CMakeLists.txt
pixi run build
pixi run ctest --test-dir build/debug -R "Sketcher|TechDraw|Assembly|Mesh"   # the new C++ targets
build/debug/bin/FreeCADCmd -t TestSketcherApp        # Python scenarios (P1.1) / TestAssemblyWorkbench (P1.3)
build/debug/bin/FreeCADCmd -t 0                      # full suite still green
```
Update [COORDINATION.md](COORDINATION.md) as tasks move.
