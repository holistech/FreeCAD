# Test Coverage — FEM Workbench

Scope: `/home/soeren/src/FreeCAD/src/Mod/Fem/` and any C++ tests under `tests/src/Mod/Fem/`.

Method note: This is a structural/qualitative assessment. No build or test execution was
performed. Coverage levels (None/Low/Medium/High) are estimates justified by mapping existing
test cases against the source surface. No measured percentages are claimed.

---

## 1. Source Surface

The FEM workbench is one of the largest FreeCAD modules and is **heavily Python**. A thin C++
core (`App`/`Gui`) provides mesh geometry, constraint document objects, and the VTK-based
post-processing pipeline; the entire solver/IO/object-logic layer is Python.

### File counts (approximate)

| Layer | Location | Files |
|-------|----------|-------|
| C++ App (`*.cpp`/`*.h`) | `App/` | ~94 |
| C++ Gui (`*.cpp`/`*.h`) | `Gui/` | ~169 (263 App+Gui combined) |
| Python (all, incl. tests/examples) | `src/Mod/Fem/` | ~433 |
| Python (excl. `femtest/`, `femexamples/`) | — | ~300 |
| `femexamples/` (test input data, style-excluded) | `femexamples/` | ~69 |

### C++ App surface (`App/`)
- **Constraints/loads (document objects):** 17 `FemConstraint*.cpp` — Bearing, Contact,
  Displacement, Fixed, FluidBoundary, Force, Gear, Heatflux, InitialTemperature, PlaneRotation,
  Pressure, Pulley, RigidBody, Spring, Temperature, Transform, plus base `FemConstraint`.
- **Mesh:** `FemMesh`, `FemMeshObject`, `FemMeshProperty`, `FemMeshShapeObject`,
  `FemMeshShapeNetgenObject`, plus the Python binding `FemMeshPyImp.cpp` (`FemMesh.pyi`).
- **Post-processing (VTK):** `FemPostObject`, `FemPostPipeline`, `FemPostFilter`,
  `FemPostFunction`, `FemPostBranchFilter`, `FemPostGroupExtension` + their `*PyImp.cpp` bindings.
- **Analysis container:** `FemAnalysis.cpp`.
- **Module init / Python API:** `AppFem.cpp`, `AppFemPy.cpp`.

### C++ Gui surface (`Gui/`)
~169 files: task panels (`Task*`), view providers (`ViewProvider*`), settings dialogs
(`DlgSettingsFemCcx/Elmer/Gmsh/Z88/Mystran/ExportAbaqus/General/InOutVtk`), widgets
(Box/Cylinder/Plane/Sphere `.ui`), Abaqus syntax highlighter, selection gate, commands.

### Python surface (by subpackage)
- **`femobjects/` (~50):** document-object proxies — constraints (centrif, selfweight, tie,
  sectionprint, bodyheatsource, electromagnetic, currentdensity, magnetization, flow/pressure...),
  elements (fluid1D, geometry1D/2D, rotation1D), materials (common, mechanicalnonlinear,
  reinforced), meshes (gmsh, netgen, region, boundarylayer, group, transfinite curve/surface/
  volume), post objects (extract1D/2D, glyphfilter, histogram, lineplot, table), results
  (mechanical), solvers (calculix, ccxtools, elmer, z88).
- **`femsolver/` (~97):** solver integration layer.
  - **CalculiX:** `calculix/writer.py` + ~25 `write_constraint_*`/`write_*` modules,
    `calculixtools.py`, `calculixutils.py`.
  - **Elmer:** `elmer/writer.py`, `sifio.py`, `elmertools.py`, and ~12 equation modules
    (heat, elasticity, deformation, flow, flux, electrostatic, electricforce, magnetodynamic,
    magnetodynamic2D, staticcurrent) each with a `*_writer.py`.
  - **Z88:** `z88/writer.py` + `write_*` element/constraint/material modules, `z88tools.py`.
  - **Mystran:** `mystran/writer.py`, `solver.py`, `tasks.py`, `add_*` modules.
  - **Fenics:** `fenics/fenics_tools.py` (experimental).
  - **Framework:** `run.py`, `task.py`, `report.py`, `settings.py`, `solverbase.py`,
    `writerbase.py`, `equationbase.py`, `signal.py`.
- **`feminout/` (~17):** importers/exporters — CCX `.dat`/`.frd` results, Inp/Z88/Yaml-Json/
  Py/Fenics mesh I/O, VTK results, Nastran export, Fenics XML/XDMF read/write, `importToolsFem.py`.
- **`femmesh/` (~8):** `gmshtools.py`, `netgentools.py`, `meshtools.py`, `meshsetsgetter.py`,
  `femmesh2mesh.py`, `adaptivetools.py`, `transfinitetools.py`.
- **`femresult/` (~2):** result math/post (von Mises, principal stress, reinforced).
- **`femtools/` (~11):** `ccxtools.py`, `checksanalysis.py`, `femutils.py`, `membertools.py`,
  `geomtools.py`, `objecttools.py`, `migrate_app.py`, `errors.py`, `constants.py`, `tokrules.py`.
- **`femtaskpanels/` (~44), `femviewprovider/` (~50), `femguiutils/`, `femcommands/`,
  `fempreferencepages/`:** GUI-side proxies, task dialogs, view providers, commands, prefs.

---

## 2. Existing Tests

### Registration
- **App tests:** `src/Mod/Fem/Init.py` registers `FreeCAD.__unit_test__ += ["TestFemApp"]`.
  `TestFemApp.py` aggregates the test classes (see gap note below).
- **Gui tests:** `InitGui.py` has the registration **commented out**
  (`# FreeCAD.__unit_test__ += ["TestFemGui"]`) — GUI tests are **not run** by default.
- C++ tests: **none.** No `tests/src/Mod/Fem/` directory exists; there are zero GoogleTest
  `TEST`/`TEST_F` cases for the FEM module.

### Python test files (`femtest/`)

All test counts are `def test_` counts (the `test_00print` banner method is counted but is a
no-op print, not a real assertion-bearing test).

| File | Class(es) | `def test_` | Purpose |
|------|-----------|-------------|---------|
| `femtest/app/test_femimport.py` | TestFemImport, TestObjectexistence | 4 | Import the FEM module; assert expected document objects exist. |
| `femtest/app/test_common.py` | TestFemCommon | 3 | Add reference shapes; **import-all** sanity (`test_pyimport_all_FEM_modules`). |
| `femtest/app/test_object.py` | TestObjectCreate, TestObjectType | 7 | Create every `ObjectsFem` object; verify type, `isDerivedFrom`, FEM/Std derivation. Large coverage of object factory. |
| `femtest/app/test_open.py` | TestObjectOpen | 3 | Open `all_objects_*.FCStd`, verify objects survive load/migration. |
| `femtest/app/test_material.py` | TestMaterialUnits | 3 | Known quantity units; material-card quantity parsing. |
| `femtest/app/test_mesh.py` | TestMeshCommon, TestMeshEleTetra10, TestMeshGroups | 17 | Python-built seg2/seg3 meshes; UNV save/load; Abaqus write precision; tetra10 round-trip across inp/unv/vtk/yml/z88; mesh group add/delete/elements/VTK handling. Strongest single area. |
| `femtest/app/test_result.py` | TestResult | 6 | Result math: von Mises, principal stress (std + reinforced), rho, abs displacement. |
| `femtest/app/test_ccxtools.py` | TestCcxTools | 33 | **Largest test.** For each example: writes CalculiX `.inp` and compares to a stored reference (`compare_inp_files`), then reads pre-stored `.frd`/`.dat` results and compares stats. Covers cantilever element types, beam sections, faceload/nodeload/displacement, contact, tie, transform, centrif, selfweight, sectionprint, frequency, buckling, multi-material, nonlinear, thermomech. Calls `check_prerequisites` but does **not** require the ccx binary for the input-writing path. |
| `femtest/app/test_gmsh.py` | TestGMSHBase, TestGMSHTransfinite, TestGMSHRefinements | 5 | Transfinite (manual/automated) and adaptive refinement; compares meshes to stored `.vtk`. Requires Gmsh. |
| `femtest/app/test_solver_elmer.py` | TestSolverElmer | 6 | Writes Elmer `.sif` files and compares to stored references (mm + SI unit schemes). |
| `femtest/app/test_solver_z88.py` | TestSolverZ88 | 5 | Writes Z88 input set and compares to stored references. |
| `femtest/app/test_solver_mystran.py` | TestSolverMystran | 7 | Writes Mystran `.bdf` and compares to stored references. **NOT registered** in `TestFemApp.py` (see gap). |
| `femtest/gui/test_open.py` | TestObjectOpen | 3 | GUI-side document open with view providers. **NOT run** (Gui registration disabled). |
| `femtest/function_tests/test_support_utils.py` | TestParse_Diff | 13 | Unit tests for the CI diff-rounding helper used by the test harness itself; **not registered** as a FreeCAD unit test. |

**Total `def test_` in `femtest/`: 115** (across all files, including unregistered/disabled ones).

**Registered-and-running App test methods:** test classes FemTest01–FemTest16 (note: there is
**no FemTest12**), i.e. test_femimport, test_common, test_object, test_open, test_material,
test_mesh, test_result, test_ccxtools, test_solver_elmer, test_solver_z88, test_gmsh.

### Test support / data
- `femtest/app/support_utils.py` — shared helpers (`compare_inp_files`, `compare_stats`,
  `get_fem_test_*_dir`, etc.).
- `femexamples/` (~69 files) — model setup functions reused as test fixtures (`setup(...,
  test_mode=True)`); style-excluded but functionally critical test input.
- `femtest/data/` — reference artifacts: `calculix/` (.inp/.frd/.dat/expected_values),
  `elmer/` (.sif), `mystran/` (.bdf), `z88/` (full input dirs), `gmsh/` (~45 .vtk),
  `mesh/` (tetra10 in 5 formats), `open/` (all_objects FCStd).
- `femtest/failing_tests.md` — documents CI-flaky tests; **stale**: it references
  `test_solver_calculix.TestSolverCalculix` which no longer exists (renamed to `test_ccxtools`).

---

## 3. Coverage Map

| Source area | Tests touching it | Est. coverage | Justification |
|-------------|-------------------|---------------|---------------|
| Object factory (`ObjectsFem`, `femobjects/`) | test_object (create/type/derivation), test_open | **High** | Every makeable object is created and type-checked. |
| Mesh I/O & groups (`femmesh/`, `feminout/` mesh) | test_mesh (17) | **Medium-High** | Round-trips multiple formats; group ops well covered. Netgen path lightly tested. |
| CalculiX writer (`femsolver/calculix/`, `femtools/ccxtools.py`) | test_ccxtools (33) | **Medium-High** | Broad example coverage via input-file comparison; result reading from stored data. Actual ccx execution not exercised in CI. |
| Elmer writer (`femsolver/elmer/`) | test_solver_elmer (6) | **Low-Medium** | Only ~5 models; many of the ~12 equation types (magnetodynamic, electrostatic, flow, flux, staticcurrent) untested. |
| Z88 writer (`femsolver/z88/`) | test_solver_z88 (5) | **Low-Medium** | Few models; one case flagged CI-flaky. |
| Mystran writer (`femsolver/mystran/`) | test_solver_mystran (7) | **Low** | Tests exist but are **NOT registered**, so effectively not run. |
| Result math (`femresult/`) | test_result (6) | **Medium** | Core stress/displacement formulas covered. |
| Materials (`femobjects/material_*`) | test_material (3), test_object | **Low-Medium** | Unit/card-quantity parsing only; reinforced/nonlinear logic largely indirect. |
| Gmsh meshing (`femmesh/gmshtools.py`) | test_gmsh (5) | **Low-Medium** | Transfinite + adaptive only; general meshing/boundary-layer/region paths untested. |
| Netgen meshing (`femmesh/netgentools.py`, `FemMeshShapeNetgenObject`) | — | **None** | No dedicated test. |
| VTK post-processing pipeline (C++ `FemPost*`, `femobjects/post_*`) | — (indirect via VTK I/O) | **Low/None** | No tests for filters, pipeline, glyph/histogram/lineplot/table extraction. |
| Constraints (C++ `FemConstraint*`) | test_object (existence), test_ccxtools (writer side) | **Low-Medium** | Created and exercised via writers; geometry/solver-semantics not unit-tested. |
| `feminout/` results import (Ccx Frd/Dat, VTK, Z88O2) | test_ccxtools (frd/dat), test_mesh (vtk) | **Medium** | Result readers exercised; Fenics XML/XDMF, Nastran export untested. |
| GUI (`Gui/`, `femtaskpanels/`, `femviewprovider/`) | femtest/gui/test_open (disabled) | **None** | Gui tests disabled; ~219 GUI files untested. |
| Fenics solver (`femsolver/fenics/`) | — | **None** | Experimental, untested. |

---

## 4. Gaps & Risks (prioritized)

1. **No C++ unit tests at all.** ~263 App+Gui C++ files (mesh geometry, constraint objects, the
   entire VTK post-processing pipeline, `FemMeshPyImp`) have zero GoogleTest coverage. The
   post-processing pipeline (`FemPostPipeline`/`FemPostFilter`/`FemPostFunction`) is complex,
   binary, and completely untested. **High risk.**
2. **Mystran tests are written but never run.** `test_solver_mystran.py` is absent from
   `TestFemApp.py` (the FemTest12 slot is missing), so 7 tests provide false confidence.
   **Easy, high-value fix.**
3. **GUI layer entirely untested.** `TestFemGui` registration is commented out in `InitGui.py`;
   ~219 task-panel/view-provider/command files (the bulk of user interaction) are uncovered.
4. **No actual solver-execution tests.** CalculiX/Elmer/Z88/Mystran are validated only by
   comparing generated input files to stored references; numerical correctness of an actual solve
   is not verified in CI (and `failing_tests.md` shows execution-path flakiness when it is tried).
5. **Solver equation breadth is thin.** Elmer has ~12 equation types but only elasticity/heat-like
   cases are tested; electromagnetics (magnetodynamic, electrostatic, electricforce,
   currentdensity), flow, and flux equations are essentially uncovered.
6. **Netgen and general Gmsh meshing untested.** Only transfinite/adaptive Gmsh paths are tested;
   Netgen has no tests, despite being a primary meshing backend.
7. **Post-processing Python objects untested.** `post_extract1D/2D`, glyph, histogram, lineplot,
   table extractors have no tests.
8. **Reference-comparison fragility.** Many tests assert byte/line equality against stored `.inp`/
   `.sif`/`.bdf` references; benign formatting or numeric-precision changes cause failures unrelated
   to behavior, discouraging refactoring.
9. **Stale test documentation.** `failing_tests.md` references the removed
   `test_solver_calculix`; the `data/calculix` dir name no longer matches the `ccxtools` solver
   (noted as a TODO in the source).

---

## 5. Recommendations

1. **Register the Mystran tests** — add the missing `FemTest12` import/line to `TestFemApp.py`.
   Lowest-effort coverage gain available.
2. **Introduce C++ GoogleTests under `tests/src/Mod/Fem/`** (gated by `BUILD_FEM`), starting with
   the highest-risk, most-testable units: `FemMesh` geometry/properties, the VTK
   `FemPostPipeline`/`FemPostFilter` graph, and constraint object property round-trips.
3. **Re-enable a minimal headless GUI test set** (or move view-provider logic behind testable,
   non-GUI helpers) so the ~219 GUI files gain at least smoke coverage.
4. **Add opt-in solver-execution tests** that run when the ccx/Elmer/Z88 binaries are present,
   comparing numerical results against `expected_values`, separated from the always-on
   input-writing tests so binary absence does not break CI.
5. **Broaden Elmer equation coverage** — one model per untested equation type (electrostatic,
   magnetodynamic, flow, flux, staticcurrent) with a stored `.sif` reference.
6. **Add Netgen meshing and post-extractor tests** to cover the currently-zero areas.
7. **Reduce reference brittleness** — compare parsed/normalized structures or use numeric
   tolerances instead of raw text equality where practical.
8. **Clean up test docs** — update/remove `failing_tests.md`, fix the `calculix`→`ccxtools`
   naming TODO.

---

## 6. Quick Stats

- C++ tests (`tests/src/Mod/Fem/`): **0 files, 0 TEST/TEST_F.**
- Python test files in `femtest/`: **14** (10 app + 1 gui + 1 function_tests + support_utils +
  `__init__`).
- Total `def test_` in `femtest/`: **115**.
- Registered & running App test classes: **FemTest01–FemTest16, minus FemTest12** (Mystran gap).
- Effectively unrun tests: **Mystran (7)** + **gui/test_open (3)** + **function_tests (13)** =
  ~23 `def test_` not executed by the default FreeCAD test run.
- Largest test file: `test_ccxtools.py` (33), then `test_mesh.py` (17).
- Source surface: ~94 App C++, ~169 Gui C++ (263 combined), ~300 non-test Python files,
  ~69 `femexamples/` fixtures.
- Reference data sets: calculix, elmer, mystran, z88, gmsh (~45 vtk), mesh (5 formats), open.
- Overall FEM coverage estimate: **Medium for Python App/solver-writer/object/mesh logic; Low for
  Elmer-equation breadth, materials, meshing backends; None for C++ core, VTK post-processing,
  and the entire GUI.**
