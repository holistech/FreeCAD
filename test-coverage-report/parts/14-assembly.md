# Test Coverage — Assembly Workbench

Scope: `src/Mod/Assembly/` and `tests/src/Mod/Assembly/`. This is a
structural/qualitative assessment. No build was performed and no coverage
was measured; coverage levels (None/Low/Medium/High) are estimates justified
by mapping existing tests to the source surface.

## 1. Source Surface

The Assembly workbench is the FreeCAD assembly-modelling environment built on
top of the Ondsel multibody solver (`OndselSolver`, vendored under
`src/3rdParty/OndselSolver` or used as the external dependency
`FREECAD_USE_EXTERNAL_ONDSELSOLVER`). The solver is a C++ dependency linked
into the `Assembly` library, not a Python dependency; the joint kinematics and
constraint assembly are translated to Ondsel `ASMT*` objects in C++.

### App layer (C++, document objects + solver, ~5,060 LOC of .cpp)
- `AssemblyObject.cpp` (~2,167 LOC) — the central object. Owns the solver
  integration: `solve()`, `generateSimulation()`, `updateForFrame()`,
  drag handling (`preDrag`/`doDragStep`/`postDrag`), undo of solves, ASMT
  export, and the full translation of FreeCAD joints into Ondsel
  `ASMTAssembly`/`ASMTPart`/`ASMTMarker`/`ASMTJoint`. Handles grounded parts
  (`getGroundedParts`, `fixGroundedParts`, `syncGroundedJoints`) and joint
  enumeration (`getJoints`, `getJointsOfPart`, etc.).
- `AssemblyUtils.cpp` (~836 LOC) — joint-type enum (`Fixed, Revolute,
  Cylindrical, Slider, Ball, Distance, Parallel, Perpendicular, RackPinion,
  Screw, Gears, Belt`), distance-type classification, and joint distance
  helpers.
- Document object types: `JointGroup`, `BomGroup`, `BomObject`,
  `SimulationGroup`, `ViewGroup`, `AssemblyLink` — each with a Py-imp wrapper
  (`*PyImp.cpp`, `*.pyi`).
- `AppAssembly.cpp`, `AppAssemblyPy.cpp` — module init and Python module API.

### Gui layer (C++, ~3,100 LOC of .cpp)
- `Commands.cpp`, `ViewProviderAssembly.cpp` (+ AssemblyLink, JointGroup,
  Bom, BomGroup, SimulationGroup, ViewGroup view providers),
  `TaskAssemblyMessages.cpp`.

### Python layer (~8,860 LOC across `*.py`)
- `JointObject.py` (~2,320 LOC) — `Joint` and `GroundedJoint` feature-python
  proxies, placement finding (`findPlacement`), joint connectors
  (`setJointConnectors`), and joint task panels.
- `UtilsAssembly.py` (~1,410 LOC) — reference resolution, element/placement
  utilities.
- Command modules: `CommandCreateAssembly/Bom/Joint/Simulation/View`,
  `CommandInsertLink`, `CommandInsertNewPart`, `CommandSolveAssembly`,
  `CommandExportASMT`, `AssemblyImport`, `Preferences`, `SoSwitchMarker`,
  `Init.py`, `InitGui.py`.

Approx. file count in scope: ~70 source files (App ~30, Gui ~24, Python ~16),
plus the test tree.

## 2. Existing Tests

### C++ (GoogleTest) — `tests/src/Mod/Assembly/`
Target `Assembly_tests_run` (built when `BUILD_ASSEMBLY`), links `Assembly`,
GTest, and includes the OndselSolver headers.

| File | Fixture | Cases | Purpose |
|------|---------|-------|---------|
| `App/AssemblyObject.cpp` | `AssemblyObjectTest` | 1 (`TEST_F`) | Creates a document, an `AssemblyObject` and a `JointGroup` in `SetUp`; the single test `createAssemblyObject` has an empty Arrange/Act/Assert body — it is effectively a smoke/scaffold test that only exercises construction/teardown. |

C++ total: 1 `TEST_F`, no meaningful assertions.

### Python (unittest) — registered via `Init.py`
`FreeCAD.__unit_test__ += ["TestAssemblyWorkbench"]`. The entry module
`TestAssemblyWorkbench.py` imports two suites from the `AssemblyTests` package.

| File | Class | `test_` count | Purpose |
|------|-------|---------------|---------|
| `AssemblyTests/TestCore.py` | `TestCore` | 7 | Core object lifecycle and solver: `test_create_assembly`, `test_create_jointGroup`, `test_create_joint`, `test_create_grounded_joint`, `test_toggle_grounded_joint` (regression for issue #28440), `test_find_placement` (5 element/sub-element placement cases for a placed box: face+vertex, edge+vertex, vertex, face), `test_solve_assembly` (two boxes, one grounded, a single joint, asserts the two placements coincide after solve). |
| `AssemblyTests/TestCommandInsertLink.py` | `TestCommandInsertLink` | 2 | `test_mixed_valid_and_invalid_objects` and `test_empty_insertion_stack`, both using `unittest.mock` patches (`MockGui`) of UI calls (`adjustTreeSize`, `loadUi`) to test the insert-link command logic without a GUI. |
| `AssemblyTests/TestTEMPLATE.py` | — | 0 | Copy-paste template, not registered/run. |
| `AssemblyTests/mocks/MockGui.py` | — | — | GUI mock helpers for headless command tests. |

Python total: 9 `test_` methods across 2 active suites (10 source `def test_`
incl. the unused TEMPLATE — but TEMPLATE is not imported, so 9 effective).

## 3. Coverage Map

| Source area | Tested by | Est. coverage | Notes |
|-------------|-----------|--------------|-------|
| AssemblyObject construction / JointGroup | C++ smoke + TestCore create tests | Low–Medium | Creation paths touched; no state assertions in C++. |
| Grounded parts / grounded joint | `test_create_grounded_joint`, `test_toggle_grounded_joint` | Medium | Create, set, remove, regression #28440 covered. |
| Joint creation (FeaturePython proxy) | `test_create_joint` | Low | Only `JointType` attribute existence checked; one joint type, no per-type behaviour. |
| Placement finding (`findPlacement`) | `test_find_placement` | Medium | Good multi-case coverage for box sub-elements; single geometry primitive only. |
| Solver (`solve`) end-to-end | `test_solve_assembly` | Low | One scenario (1 joint, 2 boxes), single coincidence assertion. No per-joint-type kinematics, no DOF/over-constraint, no failure paths. |
| Joint types (12 types in enum) | — | None | Only the generic type-0 joint is exercised; revolute/cylindrical/slider/ball/distance/screw/gears/belt/rack-pinion untested. |
| `makeMbdJoint*` C++ translation | — (indirect via solve) | Low | Per-type ASMT mapping not directly verified. |
| Simulation (`generateSimulation`, frames) | — | None | No tests. |
| Drag (`preDrag`/`doDragStep`/`postDrag`) | — | None | No tests. |
| Undo of solve / `savePlacementsForUndo` | — | None | No tests. |
| ASMT export (`exportAsASMT`, CommandExportASMT) | — | None | No tests. |
| BOM (`BomObject`, `BomGroup`, CommandCreateBom) | — | None | No tests. |
| Exploded / ViewGroup | — | None | No tests. |
| AssemblyLink | — | None | No tests. |
| Insert link command | `TestCommandInsertLink` (mocked) | Medium | Logic paths for valid/invalid/empty covered. |
| Other commands (CreateJoint/View/Simulation, InsertNewPart, SolveAssembly) | — | None | No command-level tests. |
| Gui (view providers, task panels, Commands.cpp) | — | None | No Gui tests; only mock-based headless command test. |
| UtilsAssembly reference resolution | partial via TestCore | Low | Exercised indirectly only. |

## 4. Gaps & Risks (prioritized)

1. **Solver correctness is barely tested (highest risk).** The whole value of
   the workbench is the Ondsel solver producing correct placements. There is a
   single `test_solve_assembly` with one assertion. No verification of solved
   positions/orientations per joint type, no DOF counting, no detection of
   under/over-constrained or unsolvable assemblies, no convergence/failure
   handling. Regressions in `AssemblyObject::solve` or `makeMbdJoint*` would
   pass CI.
2. **Joint kinematics untested per type.** Twelve joint types exist
   (`Fixed, Revolute, Cylindrical, Slider, Ball, Distance, Parallel,
   Perpendicular, RackPinion, Screw, Gears, Belt`) but tests only create a
   generic type-0 joint. Each maps to distinct `ASMT*Joint` C++ code with no
   targeted test — the most behaviour-dense, least-covered area.
3. **C++ test is a no-op.** `createAssemblyObject` has an empty body and
   asserts nothing; it provides scaffolding only and gives false confidence.
4. **Simulation, drag, undo-of-solve, ASMT export, BOM, exploded views,
   AssemblyLink — all zero coverage.** These are substantial features.
5. **No GUI / command coverage** except two mocked insert-link tests; task
   panels and view providers untested.
6. **Single geometry primitive.** Placement and solve tests use only
   `Part::Box`; behaviour with cylinders, cones, imported solids, and
   sub-assemblies (nested links) is unverified.
7. **Solver dependency coupling.** Tests silently depend on a functioning
   Ondsel solver; a misconfigured/external-solver build path is not guarded by
   a dedicated availability test.

## 5. Recommendations

1. Replace the empty C++ test with assertions (object identity, JointGroup
   membership, default properties) and add C++ unit tests for
   `makeMbdJointOfType` translation per joint type.
2. Add a Python solver test matrix: one focused `test_solve_<type>` per joint
   type asserting the resulting placement/relative DOF for a known geometry.
3. Add over/under-constrained and unsolvable-assembly tests asserting the
   solver return code and that placements are left unchanged / errors raised.
4. Cover simulation generation + `updateForFrame`/`numberOfFrames`, and the
   undo-of-solve round trip (`savePlacementsForUndo`/`undoSolve`).
5. Add ASMT export tests (export a small assembly, assert key ASMT structure)
   and BOM generation tests.
6. Extend `findPlacement` tests beyond `Part::Box` (cylinder, sub-assembly
   references) and add nested-link / sub-joint cases.
7. Add command tests (mock GUI) for CreateJoint, SolveAssembly, InsertNewPart,
   following the `TestCommandInsertLink` pattern.
8. Remove or activate `TestTEMPLATE.py` so the suite list is honest.

## 6. Quick Stats

- Source files in scope: ~70 (App ~30, Gui ~24, Python ~16).
- Source size: App ~5.1k LOC .cpp; Gui ~3.1k LOC .cpp; Python ~8.9k LOC.
- C++ tests: 1 file, 1 `TEST_F`, 0 effective assertions.
- Python tests: 2 active suites, 9 `test_` methods (3 of them — find_placement,
  solve, toggle-grounded — carry real assertions; rest are creation smoke
  tests). 1 unused template suite.
- Joint types in enum: 12; types meaningfully tested: ~1 (generic).
- Overall estimated coverage: **Low.** Object lifecycle and grounded-part
  handling reach Medium; the safety-critical solver and per-joint kinematics
  are Low-to-None.
