# FreeCAD Test-Coverage — Prioritized Roadmap

> **Execution & tracking:** per-phase implementation plans and a cross-session coordination hub live in
> [`roadmap/`](roadmap/) — start at [roadmap/COORDINATION.md](roadmap/COORDINATION.md), which holds the
> live task status and is updated every working session.

Derived from the structural analysis (`parts/01–21`) and the empirical run
(`parts/22-test-execution-results.md`). Ordered by **value per effort**: each phase delivers
standalone benefit, and earlier phases unblock later ones (e.g. measuring coverage, or making CI
trustworthy, multiplies the value of everything after).

Effort key: **S** ≈ hours–1 day · **M** ≈ days · **L** ≈ weeks.
Value = risk reduced × surface affected.

---

## Phase 0 — Reclaim & make CI trustworthy (do first; mostly S)

The cheapest wins: tests that already exist but don't run, plus the structural gaps that let
failures hide. Highest value-per-effort in the whole roadmap.

| # | Action | Where | Effort | Why |
|---|--------|-------|:------:|-----|
| 0.1 | Register/re-enable dead test suites | FEM `test_solver_mystran` (+`function_tests`, GUI), Spreadsheet XLSX/Gui, Material Gui, Draft importer suites, `TestTreeSelection`, TemplatePyMod | S | Tests written, just not wired in → instant coverage |
| 0.2 | Commit a small offline IFC fixture and re-enable NativeIFC self-test | `src/Mod/BIM/nativeifc/ifc_selftest.py` (disabled because it downloads) | S–M | Only real IFC round-trip test in the tree |
| 0.3 | Fix CI test discovery to include `src/Tools/bindings/tests/` | CI `sub_build*` / unittest discover path | S | The binding-generator's 6 tests never run today |
| 0.4 | Wire the Python suites into ctest (one `add_test` per registered module → `FreeCADCmd -t <name>`) | `tests/CMakeLists.txt` | M | Today a green `ctest` ≠ Python passed; unify the signal |
| 0.5 | Harden the runner against fd/teardown corruption suite-wide | `src/Mod/Test/TestApp.py` (fd snapshot/restore per run) | S | Generalizes the CAM `TestCAMSanity` fix so one bad test can't abort the whole run |
| 0.6 | Add a "no silent skips" check — fail CI if a registered module fails to import | `TestApp.tryLoadingTest` already degrades to a failing case; surface it in CI | S | Stops dormant/broken tests from passing unnoticed |

> Note: the CAM `TestCAMSanity` fd-abort + `OutputOptions`/post-resolution bugs from this audit are
> **already fixed** (branch `fix/cam-outputoptions-sanity-and-tests`) — that work is the template
> for 0.1/0.5.

## Phase 1 — De-risk the numerical / geometry cores (high impact; M–L)

The engines whose silent miscalculation corrupts user models. Use deterministic, analytically-known
golden tests.

| # | Target | Where | Effort | Why |
|---|--------|-------|:------:|-----|
| 1.1 | PlaneGCS solver unit suite | `src/Mod/Sketcher/App/planegcs` (`parts/06`) | L | ~13k LOC, only 2 direct tests; convergence, per-constraint gradients (analytic vs finite-diff), conflict/redundancy diagnostics, degenerate/non-convergence cases |
| 1.2 | TechDraw HLR golden tests | `GeometryObject`/`ProjectionAlgos`/`EdgeWalker` (`parts/13`) | M | Visible/hidden edge classification + projection direction on known solids; today only a 4-edge box smoke check |
| 1.3 | Assembly solver matrix | `src/Mod/Assembly` (`parts/14`) | M | Per-joint-type translation + DOF/over-constraint/failure cases; replace the empty-body C++ test |
| 1.4 | Mesh repair + boolean ops | `src/Mod/Mesh/App/Core` (`parts/07`) | M | Repair pipeline (silent data-corruption risk), set operations, decimation/smoothing |

## Phase 2 — Data-exchange round-trips (systemic blind spot; M each)

The most repeated gap in the report. Pattern for every format: `export → import → compare` against
geometric invariants (volume/area/COM), unit scaling, and color/metadata.

| # | Target | Where | Effort |
|---|--------|-------|:------:|
| 2.1 | STEP / IGES / glTF / BREP | `src/Mod/Import`, `src/Mod/Part` (`parts/18`, `04`) | M |
| 2.2 | IFC2X3 + IFC4 round-trip | `src/Mod/BIM` (`parts/12`) | M |
| 2.3 | Mesh formats (STL/PLY/OFF/AMF/…) | `src/Mod/Mesh` (`parts/07`) | M |
| 2.4 | Spreadsheet CSV + XLSX | `src/Mod/Spreadsheet` (`parts/15`) | S–M |
| 2.5 | Draft DXF import corpus | `src/Mod/Draft/importDXF.py` (~5k LOC, `parts/11`) | M |

## Phase 3 — Fill the zero-coverage modules (M; synthetic ground-truth)

| # | Target | Where | Effort | Approach |
|---|--------|-------|:------:|----------|
| 3.1 | ReverseEngineering algorithms | `src/Mod/ReverseEngineering` (`parts/08`) | M | Synthetic geometry with known fit/segmentation answers; guard on optional PCL/OCC backends |
| 3.2 | Measure — all 7 measurement types | `src/Mod/Measure` (`parts/16`) | M | Per-type GTest fixtures + `ShapeFinder`/MassProperties + a Python `__unit_test__` suite |
| 3.3 | Points persistence + E57, JtReader parser | `parts/08`, `parts/19` | S–M | `PropertyPointKernel` save/restore; real assertions for the Jt binary parser |
| 3.4 | Smaller workbenches with real logic | Inspection, Robot (kinematics) first (`parts/19`) | M | Robot/Inspection carry non-trivial numeric/geometry logic |

## Phase 4 — GUI testing + coverage measurement (L; enables the rest)

| # | Action | Where | Effort | Why |
|---|--------|-------|:------:|-----|
| 4.1 | Coverage-measurement target | CMake preset (gcov/lcov for C++, `coverage.py` for the in-FreeCAD Python) + CI report | M | Turns this qualitative report quantitative; makes regressions visible |
| 4.2 | Shared Gui subsystem tests (offscreen) | `src/Gui`: Command framework, TaskView, ViewProvider base (`parts/03`) | L | Every workbench flows through these; reuse the existing `QT_QPA_PLATFORM=offscreen` pattern |
| 4.3 | Per-workbench GUI smoke tests under xvfb | the 5 CAM widget suites + others (`parts/22`) | M | Many GUI tests exist but need a display; wire `xvfb-run FreeCAD -t` into CI |

---

## Sequencing rationale

1. **Phase 0 first, always.** It is mostly hours of work, and until CI actually runs and reports the
   Python suites (0.3/0.4) and stops hiding failures (0.5/0.6), every later test you add can silently
   rot the same way `TestOutputOptions` did.
2. **Phase 1 before Phase 2/3** because a wrong solver/HLR result is more damaging and harder to detect
   than a missing module test.
3. **Phase 4.1 (coverage measurement) can run in parallel** with Phase 1 — it doesn't block anything and
   immediately quantifies progress.
4. Phases 2 and 3 are largely independent and can be parallelized across contributors.

## Suggested first three branches (concrete, CAM-fix-sized)

1. `test/reclaim-dead-suites` — Phase 0.1 + 0.3 (register everything dormant, fix CI discovery).
2. `test/wire-python-into-ctest` — Phase 0.4 + 0.5 (unify the test signal, generalize the fd guard).
3. `test/sketcher-planegcs-core` — Phase 1.1 starter (a first analytic golden-test suite for the solver).
