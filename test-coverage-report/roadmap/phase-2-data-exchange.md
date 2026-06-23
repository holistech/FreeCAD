# Phase 2 — Data-exchange round-trips

**Goal:** close the most repeated gap in the report — import/export fidelity. A regression here causes
silent data loss (geometry, units, metadata) that passes CI today.

**Status:** see [COORDINATION.md](COORDINATION.md).
**Dependencies:** Phase 0 (so the tests are actually run). Independent of Phase 1; parallelizable.
**Effort:** M each (P2.4 S–M).

**Universal pattern for every format:** `build known model → export → import → compare`.
Assert against **invariants**, not byte-for-byte output:
- geometry: volume, surface area, bounding box, center of mass within tolerance;
- units: correct scaling (mm/inch) round-trips;
- structure/metadata: object hierarchy, colors, names, assembly structure where applicable.
Include negative paths (malformed input → clean error, not crash).

---

## P2.1 — STEP / IGES / glTF / BREP
**Where:** `src/Mod/Import`, `src/Mod/Part` — see `../parts/18-import-openscad.md`, `../parts/04-part.md`.
Today: only a GUI-gated STEP color test; IGES/glTF/BREP untested.

**Cases:** export a parametric solid (with per-face colors and an assembly of 2–3 parts) to each
format and re-import; assert geometry invariants, unit scaling, and color/structure preservation.
Add a headless (non-GUI) STEP test so it runs in `FreeCADCmd`.

## P2.2 — IFC2X3 + IFC4 round-trip
**Where:** `src/Mod/BIM` (`exportIFC`/`importIFC` legacy stack + NativeIFC) — see `../parts/12-bim.md`.
Today: legacy IFC export/import has zero registered tests.

**Cases:** build a small Arch model (Wall + Structure + Space), export to IFC2X3 and IFC4, re-import,
compare object count/types, placements, and key properties. Reuse / extend the P0.2 offline fixture.

## P2.3 — Mesh formats round-trip
**Where:** `src/Mod/Mesh` IO (STL/PLY/OFF/SMF/VRML/X3D/AMF) — see `../parts/07-mesh.md`.
Today: importer/exporter format fidelity untested.

**Cases:** a known mesh (fixed vertex/facet counts) round-trips through each format; assert
vertex/facet counts and bounding box; binary vs ASCII STL; malformed-file handling.

## P2.4 — Spreadsheet CSV + XLSX
**Where:** `src/Mod/Spreadsheet` (CSV import/export, pure-Python XLSX importer) — see `../parts/15-spreadsheet.md`.
Today: CSV completely untested; `test_importXLSX.py` exists but is unregistered (also covered by P0.1).

**Cases:** CSV round-trip with delimiter/quote/escape edge cases; XLSX import of a known sheet
(values, formulas, aliases); persistence round-trip of a populated sheet.

## P2.5 — Draft DXF import corpus
**Where:** `src/Mod/Draft/importDXF.py` (~5,100 LOC) — see `../parts/11-draft.md`.
Today: ~1 read fixture, 1 export.

**Cases:** a small corpus of `.dxf` fixtures covering common entities (LINE, ARC, CIRCLE, LWPOLYLINE,
SPLINE, TEXT, BLOCK/INSERT, layers); assert imported object counts/types and geometry; one export +
re-import round-trip. (Re-enable the dormant DWG/OCA suites per P0.1 or mark them explicitly skipped.)

---

## Suggested branches
`test/exchange-step-iges-gltf` (P2.1) · `test/exchange-ifc-roundtrip` (P2.2) ·
`test/exchange-mesh-formats` (P2.3) · `test/spreadsheet-csv-xlsx` (P2.4) · `test/draft-dxf-corpus` (P2.5)

## Verification
```bash
pixi run build
build/debug/bin/FreeCADCmd -t TestPartApp        # P2.1 (Import/Part)
build/debug/bin/FreeCADCmd -t TestArch           # P2.2 (BIM/IFC)
build/debug/bin/FreeCADCmd -t MeshTestsApp       # P2.3
build/debug/bin/FreeCADCmd -t TestSpreadsheet    # P2.4
build/debug/bin/FreeCADCmd -t TestDraft          # P2.5
build/debug/bin/FreeCADCmd -t 0                   # full suite still green
```
Fixtures: keep small; prefer programmatic generation; store under each module's `TestData/`.
Update [COORDINATION.md](COORDINATION.md) as tasks move.
