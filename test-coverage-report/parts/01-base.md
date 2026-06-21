# Test Coverage — Base Layer

Scope: the foundational `Base` layer — math primitives, units/quantities, the
type system, persistence/serialization, console/logging, parameters, and
low-level utilities. Source lives in `/home/soeren/src/FreeCAD/src/Base/`; C++
GoogleTest suites in `/home/soeren/src/FreeCAD/tests/src/Base/` (plus the
`zipios++` archive tests in `/home/soeren/src/FreeCAD/tests/src/zipios++/`),
and Python `unittest` suites registered through `src/Mod/Test/Init.py`.

This is a qualitative assessment. No build was performed and no coverage was
measured; ratings (None/Low/Medium/High) are estimated from the mapping of
test files and case counts onto the source surface.

## 1. Source surface

The Base layer is large and central: roughly **147 source files** (72 `.cpp`
+ 75 `.h`) under `src/Base/`. Key areas:

- **Math / geometry primitives**: `Vector3D`, `Matrix`, `Rotation`,
  `Placement`, `Axis`, `BoundBox`, `CoordinateSystem`, `Tools2D`, `Tools3D`,
  `ViewProj`, `DualNumber`, `DualQuaternion`, `Precision`.
- **Units & quantities**: `Unit`, `Quantity` (with a Flex/Bison parser:
  `Quantity.l`/`Quantity.y` → `Quantity.lex.c`/`Quantity.tab.c`), `UnitsApi`,
  `UnitsSchema(s)`, `UnitsSchemasSpecs`, `UnlimitedUnsigned`.
- **Type system & RTTI**: `Type`, `BaseClass`, `Factory`, `ExceptionFactory`,
  `Handle` (reference-counted smart pointers), `Bitmask`.
- **Persistence / serialization**: `Persistence`, `Writer`, `Reader`,
  `Stream`, `InputSource`, `XMLTools`, `Base64`/`Base64Filter`, `ZipHeader`,
  `Swap`.
- **Parameters / configuration**: `Parameter` (XML parameter tree),
  `ParameterPy`.
- **Console / diagnostics**: `Console`, `ConsoleObserver`, `Observer`,
  `Sequencer`, `StackWalker`, `Debugger`, `Profiler`.
- **Exceptions**: `Exception` (hierarchy), `PyException`.
- **Python binding infrastructure**: `PyObjectBase`, `PyExport`,
  `Interpreter`, `GeometryPyCXX`, `BindingManager`, `swigpyrun`, plus the
  `*PyImp.cpp` generated implementation files.
- **Utilities / system**: `Color`, `Uuid`, `FileInfo`, `FileLock`,
  `TimeInfo`, `Tools`, `Translate`/`Translation`, `UniqueNameManager`,
  `ServiceProvider`, `SystemHandler`, `Builder3D`.

## 2. Existing tests

### C++ (GoogleTest) — `tests/src/Base/` (~43 test files, ~546 cases)

| Test file | ~Cases | Purpose |
|---|---|---|
| `SchemaTests.cpp` | 75 | Units-schema formatting/conversion across all unit schemas |
| `Matrix.cpp` | 41 | 4x4 matrix arithmetic, inversion, decomposition, transforms |
| `Vector3D.cpp` | 39 | 3D vector ops, dot/cross, normalization, comparisons |
| `Quantity.cpp` | 31 | Quantity parsing, arithmetic, unit-string round-trips |
| `Unit.cpp` | 28 | Unit algebra (dimensions, multiply/divide, equality) |
| `UnitsApi.cpp` | 27 | High-level units API, parsing, user-string formatting |
| `Reader.cpp` | 26 | XML/restore reading, attribute parsing |
| `Parameter.cpp` | 24 | Parameter tree get/set, nesting, import/export |
| `FileInfo.cpp` | 23 | Path/file metadata, extensions, existence |
| `BoundBox.cpp` | 22 | Bounding-box construction, intersection, containment |
| `DualQuaternion.cpp` | 19 | Dual-quaternion math (rigid transforms) |
| `Placement.cpp` | 16 | Placement composition, inversion, interpolation |
| `Tools.cpp` | 15 | Misc string/number utility helpers |
| `Color.cpp` | 13 | Color packing/unpacking, conversions |
| `Stream.cpp` | 12 | Stream read/write primitives |
| `CoordinateSystem.cpp` | 11 | Coordinate-system transforms |
| `XMLTools.cpp` | 10 | XML encode/escape helpers |
| `UniqueNameManager.cpp` | 10 | Unique-name generation/collision handling |
| `Writer.cpp` | 9 | Serialization writer output |
| `Tools3D.cpp` | 9 | 3D geometric helper routines |
| `Tools2D.cpp` | 8 | 2D geometric helper routines |
| `DualNumber.cpp` | 8 | Dual-number arithmetic |
| `Axis.cpp` | 8 | Axis construction/rotation |
| `PyException.cpp` | 7 | C++↔Python exception translation |
| `Handle.cpp` | 6 | Reference-counted handle/smart-pointer semantics |
| `ServiceProvider.cpp` | 5 | Service registration/lookup |
| `Rotation.cpp` | 5 | Rotation representation/conversion |
| `Uuid.cpp` | 4 | UUID generation/format |
| `UnlimitedUnsigned.cpp` | 4 | Big-unsigned arithmetic |
| `UnitsSchemaFormat.cpp` | 4 | Units-schema number formatting |
| `Translation.cpp` | 4 | Translation/i18n helpers |
| `TimeInfo.cpp` | 4 | Time/timestamp utilities |
| `Console.cpp` | 4 | Console message routing |
| `Base64.cpp` | 4 | Base64 encode/decode |
| `Persistence.cpp` | 3 | Persistence interface basics |
| `ViewProj.cpp` | 2 | View projection |
| `Translate.cpp` | 2 | Translate helper |
| `InputSource.cpp` | 1 | Input-source wrapper (smoke) |
| `FileLock.cpp` | 1 | File-lock (smoke) |
| `Builder3D.cpp` | 1 | Inventor builder (smoke) |
| `Bitmask.cpp` | 1 | Bitmask enum flags (smoke) |
| `InventorBuilder.cpp` | 0 | Helpers only, no test cases |

Built as the `Base_tests_run` executable (`tests/src/Base/CMakeLists.txt`),
run via `ctest`.

### C++ — `tests/src/zipios++/` (~8 cases)

| Test file | ~Cases | Purpose |
|---|---|---|
| `collectioncollection.cpp` | 5 | zipios++ collection-of-collections behavior |
| `zipfile.cpp` | 3 | zipios++ zip-file entry reading |

### Python (`unittest`) — registered in `src/Mod/Test/Init.py`

| Test file | ~`test_` defs | Purpose |
|---|---|---|
| `BaseTests.py` | 49 | Console logging, Parameter tree, vector/matrix/rotation/placement algebra, matrix operators, filesystem encoding — exercises the Python bindings of Base math + Console + Parameter + FileInfo |
| `UnitTests.py` | 12 | `FreeCAD.Units.Quantity` conversions, parsing, user-string round-trips |
| `UnicodeTests.py` | 2 | Unicode path/string handling |

(`BaseTests`, `UnitTests`, `UnicodeTests` are registered alongside
non-Base suites in the same `__unit_test__` list.)

## 3. Coverage map

| Component | C++ tests? | Python tests? | Est. coverage | Notes |
|---|---|---|---|---|
| Vector3D / Matrix / BoundBox | Yes (102) | Yes (algebra) | High | Strong dual coverage of core math |
| Rotation / Placement / Axis / CoordinateSystem | Yes (40) | Yes | Medium–High | Good; rotation edge cases (gimbal, quaternion normalization) thinner in C++ (5 cases) |
| DualNumber / DualQuaternion | Yes (27) | No | Medium | C++-only; reasonable |
| Tools2D / Tools3D / Tools / ViewProj | Yes (34) | No | Medium | Helpers covered, ViewProj light (2) |
| Unit / Quantity / UnitsApi / Schemas | Yes (165) | Yes (12) | High | Best-covered area; parser exercised via Quantity tests |
| Quantity lexer/parser (`.l`/`.y`) | Indirect | Indirect | Medium | No direct grammar/error-path tests; only via Quantity inputs |
| Type system (`Type`, `BaseClass`) | No | No (indirect) | Low | No dedicated `Type.cpp`/`BaseClass.cpp` suite |
| Factory / ExceptionFactory | No | No | Low | Untested registration/creation paths |
| Handle / smart pointers | Yes (6) | No | Medium | Basic ref-count behavior |
| Persistence / Writer / Reader / Stream | Yes (50) | No (indirect) | Medium | Reader/Writer decent; full restore/round-trip integration thin |
| Base64 / XMLTools / ZipHeader / Swap | Yes (14) | No | Medium | ZipHeader/Swap untested directly |
| zipios++ archive I/O | Yes (8) | No | Low–Medium | Minimal; thin error/corruption paths |
| Parameter / ParameterPy | Yes (24) | Yes | High | Well covered both layers |
| Console / ConsoleObserver / Observer | Yes (4) | Yes (4) | Medium | Routing covered; observer/threading lightly |
| Sequencer / progress | No | No | None | Untested |
| Exception hierarchy | Partial | No | Low | `PyException` (7) only; base `Exception` types untested |
| PyException / binding infra (`PyObjectBase`, `Interpreter`) | Partial (7) | Indirect | Low | Binding glue exercised only indirectly |
| Color / Uuid / FileInfo / TimeInfo / FileLock | Yes (44) | Yes (encoding) | Medium–High | FileLock smoke-only (1) |
| UniqueNameManager / ServiceProvider | Yes (15) | No | Medium | |
| Translate / Translation | Yes (6) | No | Low–Medium | i18n logic lightly covered |
| StackWalker / Debugger / Profiler / SystemHandler | No | No | None | Diagnostics untested (platform-dependent) |
| Builder3D / InventorBuilder | Yes (1) | No | Low | Smoke only |
| Precision | Indirect | Indirect | Low | Constants used everywhere, no own suite |

## 4. Gaps & risks (prioritized)

1. **Type system & object factories untested (high risk).** `Type`,
   `BaseClass`, `Factory`, and `ExceptionFactory` have no dedicated suites.
   These underpin RTTI, dynamic creation, and the persistence/restore
   mechanism for the entire application; a regression here breaks document
   loading silently. Currently exercised only indirectly.
2. **Exception hierarchy under-tested.** Only `PyException` has a suite. The
   `Base::Exception` family (and `ExceptionFactory` reconstruction during XML
   restore) lacks tests for type fidelity, message/what(), and round-trip.
3. **Persistence round-trip / integration thin.** `Reader` and `Writer` have
   unit coverage, but full `Persistence` save→restore round-trips (including
   `ZipHeader`, `Base64Filter`, `Swap` endian handling) are not covered;
   `Persistence.cpp` has only 3 cases.
4. **Quantity grammar error paths.** The Flex/Bison `Quantity` parser is only
   exercised through valid inputs; malformed-input, locale, and overflow
   error handling are largely untested.
5. **Diagnostics & progress untested.** `Sequencer`/progress, `StackWalker`,
   `Debugger`, `Profiler`, `SystemHandler` have no tests (some are
   platform-specific and hard to test, but progress/sequencer logic is
   portable).
6. **Concurrency/observer edges.** Console observer notification and
   thread-safety are only lightly touched (Python `testSynchron/Asynchron`
   thread tests in `BaseTests.py`); C++ `Console.cpp` has 4 cases.
7. **Smoke-only files.** `Bitmask`, `FileLock`, `Builder3D`, `InputSource`
   each have a single case; `InventorBuilder` has none.

## 5. Recommendations

- Add `tests/src/Base/Type.cpp` and `BaseClass.cpp` suites: register/lookup
  types, parent/child `isDerivedFrom`, `createInstanceByName`, bad-name
  handling, and singleton init ordering.
- Add `Factory.cpp` / `ExceptionFactory.cpp` suites covering registration,
  unknown-key behavior, and exception reconstruction by type name.
- Add an `Exception.cpp` suite for the full exception hierarchy
  (what()/message, type preservation, Python translation parity).
- Add a `Persistence` round-trip test: serialize a representative object
  graph to an in-memory document and restore it, validating
  `Writer`+`Reader`+`ZipHeader`+`Base64Filter`+`Swap` together.
- Extend `Quantity` tests with malformed/edge inputs to exercise the parser
  error grammar and overflow/locale handling.
- Promote smoke-only files (`FileLock`, `Bitmask`, `Builder3D`,
  `InventorBuilder`, `InputSource`) to meaningful assertions, or document
  why they remain smoke tests.
- Add a small `Sequencer`/progress test (portable logic) and consider
  guarded tests for platform diagnostics where feasible.

## 6. Quick stats

- Source files in scope (`src/Base/`): ~147 (72 `.cpp` + 75 `.h`).
- C++ test files: ~43 in `tests/src/Base/` + 2 in `tests/src/zipios++/`.
- C++ test cases: ~546 (Base) + ~8 (zipios++) ≈ **554**.
- Python test files in scope: 3 (`BaseTests.py`, `UnitTests.py`,
  `UnicodeTests.py`), ~63 `test_` methods combined.
- Heaviest-tested areas: Units/Quantity (~165 C++ cases) and core math
  Vector/Matrix/BoundBox (~102 C++ cases).
- Largest untested-or-low areas: Type system, Factory/ExceptionFactory,
  Exception hierarchy, Persistence round-trip, diagnostics/Sequencer.
