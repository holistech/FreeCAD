# Phase 3 — Fill the zero-coverage modules

**Goal:** give the modules that currently have *no* tests a first, meaningful safety net. Focus on the
ones with real algorithmic/geometric logic (where untested code is genuinely risky), not cosmetic UI.

**Status:** see [COORDINATION.md](COORDINATION.md).
**Dependencies:** Phase 0 (registration/CI). Independent of Phases 1–2; parallelizable.
**Effort:** M (P3.3 S–M).

---

## P3.1 — ReverseEngineering algorithms
**Where:** `src/Mod/ReverseEngineering` — see `../parts/08-points-reveng.md`. Today: **zero** tests.

**Cases:** drive each algorithm with **synthetic ground-truth** geometry where the answer is known:
- `approxSurface`/`approxCurve`/`fitBSpline`: sample points from a known surface/curve, fit, assert max
  deviation below tolerance.
- `triangulate`, `poissonReconstruction`: reconstruct from a sampled sphere/box, assert closed mesh +
  bounding box.
- `regionGrowingSegmentation`/`featureSegmentation`: a point cloud of two known planes → assert 2 segments.
- `sampleConsensus`: points on a known plane/sphere → assert recovered parameters.

**Approach:** Python suite registered via `Init.py` (`__unit_test__`); **guard** on optional PCL/OCC
backends (skip cleanly if unavailable) and add a `BUILD_REVERSEENGINEERING` CI test target.

## P3.2 — Measure — all 7 measurement types
**Where:** `src/Mod/Measure` — see `../parts/16-measure.md`. Today: only distance, 3 C++ cases, 0 Python.

**Cases:** per-type GTest fixtures (distance, angle, radius, diameter, length, area, position) on known
shapes with hand-computed expectations; `ShapeFinder`/`SubnameHelper` sub-element resolution
(incl. linked/nested); MassProperties (COM/COV/inertia) on a known solid; negative/edge cases.

**Approach:** extend `Measure_tests_run`; add a Python `__unit_test__` suite for the scripting API.

## P3.3 — Points persistence/E57 + JtReader parser
**Where:** `src/Mod/Points`, `src/Mod/JtReader` — see `../parts/08`, `../parts/19`.

**Cases:** `PropertyPointKernel` save→restore round-trip; E57 import of a small fixture; malformed
input handling. JtReader: replace the assertion-free harness with real assertions on a small `.jt`
fixture (node/geometry counts) and register it.

## P3.4 — Robot / Inspection logic
**Where:** `src/Mod/Robot`, `src/Mod/Inspection` — see `../parts/19-smaller-workbenches.md`. Today: zero.

**Cases (Robot):** forward/inverse kinematics for a known trajectory/waypoint; `Trajectory`/`Waypoint`
math; placement composition. **Cases (Inspection):** distance-to-reference computation on a known
shape pair with hand-computed expected deviations.

**Approach:** Python suites registered via each module's `Init.py`; these modules carry non-trivial
numeric/geometry logic, so prioritize them over the purely-cosmetic small workbenches.

> The remaining tiny/cosmetic workbenches (Web, Show, Cloud, Help, Plot, Tux) are intentionally lower
> priority; add smoke tests only if cheap. Note any deliberate omission in COORDINATION.md.

---

## Suggested branches
`test/reverseeng-synthetic` (P3.1) · `test/measure-all-types` (P3.2) ·
`test/points-jt-parsers` (P3.3) · `test/robot-inspection-logic` (P3.4)

## Verification
```bash
pixi run build
ctest --test-dir build/debug -R "Measure|Points"
build/debug/bin/FreeCADCmd -t TestSurfaceApp   # example registered-module run pattern
# plus the new module test names once registered, e.g. -t TestReverseEngineering / -t TestMeasure
build/debug/bin/FreeCADCmd -t 0
```
Update [COORDINATION.md](COORDINATION.md) as tasks move.
