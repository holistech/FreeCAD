# Test-Coverage Roadmap — Coordination Hub

**Living document.** This is the single source of truth for the status of the test-coverage roadmap.
It is meant to be updated every working session (by a human or an AI assistant) so progress is never
lost between sessions.

- **Last updated:** 2026-06-22
- **Roadmap overview:** [../ROADMAP.md](../ROADMAP.md)
- **Per-phase implementation plans:** `phase-0` … `phase-4` in this directory.
- **Source analysis:** [../README.md](../README.md) and `../parts/`.

---

## How to use / update this document

Whenever you start, finish, or change a roadmap task **in the same session you make the change**:

1. **Update the task row** in the [Task Tracker](#task-tracker): set `Status`, `Branch/PR`, and
   `Last update` (YYYY-MM-DD).
2. **Bump** the `Last updated` date at the top of this file.
3. **Append a dated entry** to the [Session Log](#session-log) describing what changed (1–3 lines):
   which tasks moved, which branches/commits/PRs were created, and any decisions or new findings.
4. If you discover new work, **add a new task row** (keep the `Pn.m` ID scheme) and mention it in the
   log. Don't delete tasks — mark them `Dropped` with a one-line reason.
5. Keep the corresponding **phase plan** (`phase-n-*.md`) in sync if scope changes.

Status values: `Not started` · `In progress` · `In review` · `Done` · `Blocked` · `Dropped`.

Conventions (apply to all roadmap work):
- One branch per task or per small task group, named as the phase plan suggests
  (e.g. `test/reclaim-dead-suites`). Branch off `main`.
- Author = the contributor's git identity. Commit trailers: `Assisted-by: <model>` (FreeCAD
  AI_POLICY) and, per this user's preference, `Co-Authored-By: <model>`.
- Verify before marking `Done`: see each phase plan's verification section. Minimum bar:
  `pixi run test` (C++) green **and** the relevant `FreeCADCmd -t <module>` green, and the full
  `FreeCADCmd -t 0` still completes.
- Never commit `test-coverage-report/` or `CLAUDE.md` inside a code-fix branch unless that is the
  branch's explicit purpose.

---

## Phase status overview

| Phase | Theme | Plan | Status | Notes |
|------|-------|------|--------|-------|
| 0 | Reclaim dead tests & make CI trustworthy | [phase-0](phase-0-reclaim-and-ci.md) | Not started | Highest value/effort; do first |
| 1 | De-risk numerical/geometry cores | [phase-1](phase-1-numeric-cores.md) | Not started | PlaneGCS, HLR, Assembly solver, Mesh repair |
| 2 | Data-exchange round-trips | [phase-2](phase-2-data-exchange.md) | Not started | STEP/IGES/glTF, IFC, mesh, CSV/XLSX, DXF |
| 3 | Fill zero-coverage modules | [phase-3](phase-3-zero-coverage-modules.md) | Not started | ReverseEngineering, Measure, Points, Robot/Inspection |
| 4 | GUI tests + coverage measurement | [phase-4](phase-4-gui-and-coverage.md) | Not started | Coverage target unlocks quantitative tracking |

---

## Task Tracker

Status legend above. `Branch/PR` holds the branch name and/or PR link once it exists.

### Phase 0 — Reclaim & CI
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P0.1 | Register/re-enable dormant test suites | Not started | — | 2026-06-22 |
| P0.2 | Offline IFC fixture + re-enable NativeIFC self-test | Not started | — | 2026-06-22 |
| P0.3 | CI discovery includes `src/Tools/bindings/tests/` | Not started | — | 2026-06-22 |
| P0.4 | Wire Python suites into ctest | Not started | — | 2026-06-22 |
| P0.5 | Runner-wide fd/teardown guard | Not started | — | 2026-06-22 |
| P0.6 | Fail CI on import-failed registered modules | Not started | — | 2026-06-22 |

### Phase 1 — Numerical / geometry cores
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P1.1 | PlaneGCS solver unit suite | Not started | — | 2026-06-22 |
| P1.2 | TechDraw HLR golden tests | Not started | — | 2026-06-22 |
| P1.3 | Assembly solver matrix | Not started | — | 2026-06-22 |
| P1.4 | Mesh repair + boolean ops | Not started | — | 2026-06-22 |

### Phase 2 — Data-exchange round-trips
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P2.1 | STEP/IGES/glTF/BREP round-trip | Not started | — | 2026-06-22 |
| P2.2 | IFC2X3 + IFC4 round-trip | Not started | — | 2026-06-22 |
| P2.3 | Mesh formats round-trip | Not started | — | 2026-06-22 |
| P2.4 | Spreadsheet CSV + XLSX | Not started | — | 2026-06-22 |
| P2.5 | Draft DXF import corpus | Not started | — | 2026-06-22 |

### Phase 3 — Zero-coverage modules
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P3.1 | ReverseEngineering algorithms | Not started | — | 2026-06-22 |
| P3.2 | Measure — all 7 measurement types | Not started | — | 2026-06-22 |
| P3.3 | Points persistence/E57 + JtReader parser | Not started | — | 2026-06-22 |
| P3.4 | Robot / Inspection logic | Not started | — | 2026-06-22 |

### Phase 4 — GUI + coverage measurement
| ID | Task | Status | Branch/PR | Last update |
|----|------|--------|-----------|-------------|
| P4.1 | Coverage-measurement target (gcov/lcov + coverage.py) | Not started | — | 2026-06-22 |
| P4.2 | Shared Gui subsystem tests (offscreen) | Not started | — | 2026-06-22 |
| P4.3 | Per-workbench GUI smoke tests under xvfb | Not started | — | 2026-06-22 |

---

## Current focus

> Recommended next branch: **P0.1 + P0.3** (`test/reclaim-dead-suites`). See
> [phase-0](phase-0-reclaim-and-ci.md).

---

## Session Log

Append newest entries at the top. Format: `### YYYY-MM-DD — <who>`.

### 2026-06-22 — initial setup
- Created the roadmap coordination hub and the five per-phase implementation plans.
- Context: precursor work already merged-ready on branch `fix/cam-outputoptions-sanity-and-tests`
  (pushed to `origin` = holistech fork). It fixed CAM `OutputOptions` bugs, post-class resolution,
  `OUTPUT_UNITS` robustness, and the CAM `TestCAMSanity` fd-abort — the latter is the template for
  task **P0.5**, and reviving CAM's `TestOutputOptions`/`TestEmptyMoveSuppression` is the template
  for **P0.1**.
- All roadmap tasks are `Not started`. Recommended entry point: P0.1 + P0.3.
