# Test Coverage — Sketcher Workbench

Scope: `src/Mod/Sketcher/` (App, App/planegcs, Gui, Python tests) and the C++
GoogleTest suite under `tests/src/Mod/Sketcher/`.

This is a structural/qualitative assessment. No build was run and no measured
coverage percentages are claimed. Coverage levels (None/Low/Medium/High) are
estimates justified by mapping existing tests against the source surface.

---

## 1. Source Surface

### App layer (~59 `.cpp`/`.h` files)

The App layer holds all the headless, scriptable logic and is where the
numerically and topologically interesting code lives.

- **`App/planegcs/` — the constraint solver (11 files, ~13,300 LOC).** This is
  the critical numerical kernel. It is a self-contained 2D geometric constraint
  solver (PlaneGCS):
  - `GCS.cpp/.h` (~5,800 LOC) — the solver core: DogLeg / Levenberg-Marquardt /
    BFGS algorithms, subsystem decomposition, diagnostics (redundant /
    conflicting / partially-redundant constraint detection), dependent-parameter
    analysis, QR/SparseQR rank computation.
  - `Constraints.cpp/.h` (~3,200 LOC) — the analytic constraint equations and
    their gradients (equal, distance, tangent, perpendicular, angle, point-on-
    object, internal-alignment, snell's-law, B-spline constraints, etc.).
  - `Geo.cpp/.h` — parametric geometry primitives (line, circle, ellipse,
    hyperbola, parabola, B-spline) and their derivatives.
  - `SubSystem.cpp/.h`, `qp_eq.cpp/.h` (equality-constrained QP), `Util.h`.
  This is the highest-risk component in the workbench: it is pure numerical code
  whose correctness, convergence and robustness directly determine whether any
  sketch solves.
- **`Sketch.cpp` (~5,770 LOC) + `Sketch.h`.** The bridge object that translates
  FreeCAD geometry + `Constraint` objects into PlaneGCS parameters/constraints,
  invokes the solver, and reads results back. Effectively the API boundary to
  planegcs.
- **`SketchObject*` (split across `SketchObject.cpp`, `...Constraints.cpp`,
  `...Geometry.cpp`, `...External.cpp`, `...Operations.cpp`, plus `SketchObjectSF`
  and `SketchObjectPyImp`).** The persistent `DocumentObject`: geometry list,
  constraint list, external geometry, geometry operations (split, trim, extend,
  fillet, symmetry, carbon-copy, offset), internal-geometry exposure, element
  naming (TNP / topological naming).
- **Constraints & geometry model:** `Constraint.cpp/.h`, `ConstraintPyImp`,
  `PropertyConstraintList`, `GeoList`, `GeoEnum`.
- **Facades / extensions:** `GeometryFacade`, `SketchGeometryExtension`,
  `SolverGeometryExtension`, `ExternalGeometryExtension`,
  `ExternalGeometryFacade` (+ their PyImp wrappers).
- **Analysis & misc:** `SketchAnalysis.cpp` / `Analyse.h` (open vertices,
  missing coincidences/point-on-object/vertical-horizontal, redundancy/
  conflict reporting, autoconstrain), `Measure.cpp`, `PythonConverter`,
  `SketchObjectSF` (spreadsheet-fit / external file support).

### Gui layer (~125 `.cpp`/`.h` files)

Interactive tooling: `DrawSketchHandler*` (one per drawing tool: line, arc,
circle, ellipse, B-spline, slot, fillet, offset, extend, external, carbon-copy,
plus the controller/widget framework), `Command*` (`CommandConstraints`,
`CommandCreateGeo`, `CommandSketcherTools`, `CommandSketcherBSpline`,
`CommandSketcherOverlay`, `CommandSketcherVirtualSpace`,
`CommandAlterGeometry`), view providers, task panels, auto-constraint UI
(`AutoConstraint.h`, `DrawSketchHandlerDragAutoConstraint`), preselection,
on-view parameters. Almost all of this is GUI/event-driven and only reachable
through the GUI Python tests.

---

## 2. Existing Tests

### C++ GoogleTest suite (`tests/src/Mod/Sketcher/`) — 107 cases

Builds target `Sketcher_tests_run` (gated by `BUILD_SKETCHER`), links the
`Sketcher` App library. A `SketcherTestHelpers.{cpp,h}` fixture provides shared
setup.

| Test file | Cases | Purpose |
|---|---:|---|
| `App/Constraint.cpp` | 18 | `ConstraintPointsAccess` fixture: constraint point-element serialization, forward/backward read-write compatibility (old↔new format), index/pos substitution, `involvesGeoId`, legacy-field synchronization. |
| `App/SketchObject.cpp` | 35 | GeoId↔shape-type mapping (edge/vertex/external/axes/root point), `getPoint` for every geometry type (point, line, circle, ellipse, all arc/conic types, periodic & non-periodic B-spline), internal-geometry exposure & deletion for ellipse/hyperbola/parabola/B-spline, reverse-angle-to-supplementary expression handling (with/without units), `getElementName`. |
| `App/SketchObjectChanges.cpp` | 42 | External-geometry add/delete counts & edge cases, `replaceGeometries` (1→1, 2→1, 1→2), and split/trim of every geometry type (line, circle, ellipse, arc-of-circle, arc-of-conic, periodic & non-periodic B-spline), including no-intersection and end/mid cases. |
| `App/SketchObjectSymmetric.cpp` | 10 | `addSymmetric`: with/without constraints, coincident-topology preservation, tangent→coincident downgrade, on-axis-point handling, line-reference, shared-vertex dedup, point symmetry, circle center-symmetry+equal. |
| `App/planegcs/GCS.cpp` | 1 | `clearConstraints` only — adds 100 constraints and verifies `clear()` empties the system. |
| `App/planegcs/Constraints.cpp` | 1 | `tangentBSplineAndArc` — a single tangency constraint scenario. |

### Python tests

App-registered via `Init.py` (`__unit_test__ += ["TestSketcherApp"]`); the
module re-exports test classes from the `SketcherTests/` package. **82 App-level
`def test*` methods.**

| Module | Cases | Purpose |
|---|---:|---|
| `SketcherTests/TestSketcherSolver.py` | 19 | End-to-end solver/object behavior: box & slot constraint sets, regression issues, block-constraint on ellipse, three-lines-with-coincidences, oriented/signed distance constraints (circle-to-line driving/reference/secant/legacy-negative, point-to-line signed, circle-to-circle, circle-line tangent), external-geometry reference removal, save/load with external geometry, TNP (topological naming) for stored/construction-toggled external geometry. |
| `SketcherTests/TestSketchInternalFaces.py` | 45 | Detection/derivation of internal faces from sketch wires across many geometric configurations. |
| `SketcherTests/TestSketchFillet.py` | 11 | Fillet creation across geometry combinations. |
| `SketcherTests/TestSketchValidateCoincidents.py` | 5 | Validation/repair of coincident constraints. |
| `SketcherTests/TestSketchExpression.py` | 1 | Constraint driven by a spreadsheet/expression. |
| `SketcherTests/TestSketchCarbonCopyReverseMapping.py` | 1 | Carbon-copy reverse element mapping (uses a fixture `.FCStd`). |

GUI-registered via `InitGui.py` (`__unit_test__ += ["TestSketcherGui"]`).
**16 GUI `def test*` methods** (a shared `GuiTestCase.py`/`SketcherGuiTestCase`
base):

| Module | Cases | Purpose |
|---|---:|---|
| `SketcherTests/TestOnViewParameterGui.py` | 8 | On-view parameter entry widgets during drawing. |
| `SketcherTests/TestPlacementUpdate.py` | 4 | Sketch placement update propagation. |
| `SketcherTests/TestExternalFacePreselection.py` | 3 | External-face preselection in the 3D view. |
| `SketcherTests/TestConstraintPreselectionGui.py` | 1 | Constraint preselection. |

---

## 3. Coverage Map

| Source area | Approx size | Test assets | Est. coverage | Notes |
|---|---|---|---|---|
| **planegcs solver core** (`GCS.cpp`) | ~5.8k LOC | 1 C++ unit test + indirect via Python solver | **Low** | Only `clearConstraints` is directly tested. Convergence, diagnostics, redundancy/conflict detection untested at unit level. |
| **planegcs constraint equations** (`Constraints.cpp`) | ~3.2k LOC | 1 C++ unit test + indirect | **Low** | Only one tangent scenario directly; the ~dozens of constraint types are exercised only end-to-end. |
| **planegcs geometry/QP/subsystem** | several files | none directly | **None–Low** | `Geo`, `qp_eq`, `SubSystem` have no dedicated unit tests. |
| **`Sketch.cpp`** (GCS bridge) | ~5.8k LOC | indirect only | **Low–Medium** | No direct unit tests; covered transitively by Python solver tests. |
| **SketchObject geometry ops** (split/trim/replace) | large | 42 C++ (`SketchObjectChanges`) | **Medium–High** | Strong per-type coverage. |
| **SketchObject symmetry** | — | 10 C++ | **Medium–High** | Good case spread. |
| **SketchObject geo mapping / getPoint / internal geo** | — | 35 C++ | **Medium–High** | Broad geometry-type coverage. |
| **Constraint serialization / point access** | — | 18 C++ | **High** | Back-compat well covered. |
| **External geometry** | `SketchObjectExternal`, facades | C++ add/del + Python TNP | **Medium** | Add/delete & persistence covered; projection edge cases thin. |
| **Internal faces** | — | 45 Python | **Medium–High** | Large dedicated suite. |
| **Fillet** | — | 11 Python | **Medium** | |
| **Carbon-copy / expressions / coincident validation** | — | 1 / 1 / 5 Python | **Low–Medium** | Shallow. |
| **SketchAnalysis / autoconstrain** | `SketchAnalysis.cpp` | none found | **None–Low** | Missing-constraint detection, redundancy/conflict analysis, open-vertex detection untested. |
| **Geometry facades / extensions** | several files | none directly | **Low** | Exercised indirectly only. |
| **Gui drawing handlers / commands** | ~125 files | 16 Python GUI tests | **Low** | Vast majority of drawing tools & commands untested; only preselection, on-view-params, placement, external-face. |
| **Auto-constraints (drag)** | `DrawSketchHandlerDragAutoConstraint` | none | **None–Low** | No direct tests. |

---

## 4. Gaps & Risks (prioritized)

1. **Solver robustness — HIGHEST RISK.** PlaneGCS is ~13k LOC of pure numerical
   code, yet has only 2 direct C++ unit tests. There is essentially no unit-level
   coverage of: convergence/non-convergence behavior, algorithm selection
   (DogLeg vs LM vs BFGS), ill-conditioned/near-singular systems, redundant /
   conflicting / partially-redundant constraint *diagnostics* (a heavily
   user-facing feature), dependent-parameter and rank/DoF computation, or
   numerical stability near degenerate geometry (zero-length lines, coincident
   points, tangent singularities). Regressions here can silently produce wrong
   solutions or solver hangs and would not be caught.

2. **Per-constraint-type equation correctness.** Each constraint in
   `Constraints.cpp` defines an error function and an analytic gradient; an
   incorrect gradient degrades convergence subtly. Only `tangentBSplineAndArc`
   is directly tested. Gradient correctness (e.g. finite-difference checks per
   constraint type) is not verified anywhere.

3. **B-spline and conic edge cases.** Periodic/non-periodic B-splines,
   knot/multiplicity changes, and conic internal-alignment constraints are
   numerically delicate; tested only through high-level scenarios, not at the
   solver/constraint unit level.

4. **SketchAnalysis / autoconstrain has no apparent tests.** Missing-coincidence
   detection, redundancy/conflict reporting, open-vertex detection and the
   autoconstrain feature are untested, despite being correctness- and
   data-integrity-sensitive.

5. **GUI drawing tools largely untested.** ~125 Gui files vs 16 GUI tests. The
   `DrawSketchHandler*` tool family (line, arc, circle, ellipse, B-spline,
   slot, offset, extend, fillet) and most `Command*` actions have no automated
   coverage; auto-constraint-on-drag and snapping logic in particular.

6. **Geometry facades/extensions** (`GeometryFacade`, `SolverGeometryExtension`,
   `SketchGeometryExtension`) have no direct tests; bugs surface only indirectly.

7. **Persistence/TNP breadth.** Save/load and topological-naming are tested for
   external geometry but not broadly across all geometry+constraint combinations.

---

## 5. Recommendations

1. **Build a dedicated PlaneGCS unit-test suite** (extend
   `tests/src/Mod/Sketcher/App/planegcs/GCS.cpp` and `Constraints.cpp`). Target:
   small well-known systems with analytically known solutions; assert solved
   parameter values and final residual; cover under-/exactly-/over-constrained
   systems and verify the diagnostic API returns the correct
   redundant/conflicting sets.
2. **Add per-constraint gradient checks** — for each constraint type, compare the
   analytic gradient against a finite-difference approximation at random feasible
   points. Cheap to write, high regression value.
3. **Add convergence/robustness cases**: near-singular and degenerate geometry,
   forced algorithm selection, and iteration-budget/non-convergence handling, so
   solver hangs/regressions are caught.
4. **Cover `SketchAnalysis`/autoconstrain** with C++ unit tests (open vertices,
   missing/redundant/conflicting constraint detection, autoconstrain results).
5. **Expand GUI handler coverage** using the existing `SketcherGuiTestCase`
   harness — at least one create-and-constrain smoke test per drawing tool and
   for auto-constraint-on-drag.
6. **Add facade/extension unit tests** for `GeometryFacade` and the solver/
   geometry extensions.
7. **Broaden round-trip/TNP tests** across mixed geometry+constraint sketches.

---

## 6. Quick Stats

- App source files (`.cpp`/`.h`): ~59; Gui: ~125.
- PlaneGCS solver: 11 files, ~13,300 LOC (critical numerical kernel).
- Largest source files: `GCS.cpp` ~5,818, `Sketch.cpp` ~5,772,
  `Constraints.cpp` ~3,232, `SketchObject.cpp` ~2,225 LOC.
- **C++ tests: 107** `TEST_F` across 6 files
  (Constraint 18, SketchObject 35, SketchObjectChanges 42, Symmetric 10,
  planegcs/GCS 1, planegcs/Constraints 1).
- **Python tests: 98** total — 82 App-level (Solver 19, InternalFaces 45,
  Fillet 11, ValidateCoincidents 5, Expression 1, CarbonCopy 1) + 16 GUI
  (OnViewParameter 8, Placement 4, ExternalFacePreselection 3,
  ConstraintPreselection 1).
- Direct solver (planegcs) unit tests: **2** out of ~13k LOC → biggest risk.
