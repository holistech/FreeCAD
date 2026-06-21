# Phase 1 — De-risk the numerical / geometry cores

**Goal:** put deterministic, analytically-verifiable tests around the engines whose silent
miscalculation corrupts user models. These are the highest-risk gaps in the codebase.

**Status:** see [COORDINATION.md](COORDINATION.md).
**Dependencies:** Phase 0 strongly recommended first (so new tests are actually run by CI and can't
go dormant). P4.1 (coverage target) is useful in parallel to measure progress.
**Effort:** P1.1 = L, others M.

Guiding principle: prefer **known-answer** tests (closed-form geometry, hand-computed expectations)
over snapshot/regression baselines, so a failure means "the math is wrong", not "the output changed".

---

## P1.1 — PlaneGCS solver unit suite
**Where:** `src/Mod/Sketcher/App/planegcs` (the constraint solver, ~13k LOC) — see `../parts/06-sketcher.md`.
Today only ~2 direct tests exist.

**Cases to cover:**
- Convergence on systems with known solutions (line/point/circle constraint sets with one analytic solution).
- Per-constraint gradient correctness: analytic Jacobian vs finite-difference for each constraint type.
- Diagnostics: redundant-constraint and conflicting-constraint detection (construct known-redundant / known-conflicting systems and assert the reported sets).
- Degenerate / non-convergence: near-singular configurations, ensure graceful failure (no crash, reported status).
- Algorithm selection (DogLeg/LM/BFGS paths) produce consistent solutions on the same well-posed system.

**Approach:** add a C++ GTest target `tests/src/Mod/Sketcher/App/planegcs/...` exercising the GCS API
directly (not via the full Sketch object), plus a few Python scenario tests in `TestSketcherApp` for
end-to-end constraint solving with asserted coordinates.

**Acceptance:** solver behavior is pinned by analytic expectations; gradient checks pass within tolerance.

## P1.2 — TechDraw HLR golden tests
**Where:** `GeometryObject`, `ProjectionAlgos`, `EdgeWalker`, `GeometryMatcher` — see `../parts/13-techdraw.md`.
Today: one 4-edge box smoke check; HLR geometry essentially unverified.

**Cases:** project known solids (box, cylinder, a solid with a through-hole) along known directions;
assert exact visible/hidden edge counts **and** representative edge endpoints; assert projection
direction handling and section geometry for a simple `DrawComplexSection`.

**Approach:** C++ GTest in `tests/src/Mod/TechDraw/` building shapes with OCC primitives and asserting
projected geometry; add pure unit tests for `DrawUtil`/`DimensionFormatter` (no document needed).

**Acceptance:** a wrong visible/hidden classification or projection vector fails a test.

## P1.3 — Assembly solver matrix
**Where:** `src/Mod/Assembly` (the Ondsel solver bridge) — see `../parts/14-assembly.md`.
Today: the single C++ test has an empty body; Python has ~9 tests using only `Part::Box`.

**Cases:** for each of the ~12 joint types, a minimal two-part assembly with a known post-solve
placement; assert resulting transform. DOF / over-constrained / unsolvable cases assert the reported
status. A drag/undo-of-solve round-trip.

**Approach:** replace the empty C++ test with real assertions; add a Python parametric suite iterating
joint types with analytic expected placements.

**Acceptance:** per-joint kinematics and DOF/over-constraint handling are asserted.

## P1.4 — Mesh repair + boolean operations
**Where:** `src/Mod/Mesh/App/Core` — see `../parts/07-mesh.md`.
Today: ~20 C++ cases (KDTree/intersection/topology); repair/booleans/decimation untested.

**Cases:** feed meshes with known defects (non-manifold edges, holes, self-intersections, duplicated
points) and assert the repair result is valid/closed; boolean union/intersection/difference on known
solids with asserted volume/face counts; decimation preserves topology within tolerance.

**Approach:** extend `Mesh_tests_run` with fixtures built programmatically (not external files where
possible) so expectations are exact.

**Acceptance:** the repair pipeline and set operations are guarded against silent corruption.

---

## Suggested branches
- `test/sketcher-planegcs-core` (P1.1, can be split into gradient-checks and convergence sub-branches)
- `test/techdraw-hlr-golden` (P1.2)
- `test/assembly-solver-matrix` (P1.3)
- `test/mesh-repair-and-booleans` (P1.4)

## Verification
```bash
pixi run build
ctest --test-dir build/debug -R "Sketcher|TechDraw|Assembly|Mesh"   # the new C++ targets
build/debug/bin/FreeCADCmd -t TestSketcherApp        # Python scenarios
build/debug/bin/FreeCADCmd -t 0                       # full suite still green
```
Update [COORDINATION.md](COORDINATION.md) as tasks move.
