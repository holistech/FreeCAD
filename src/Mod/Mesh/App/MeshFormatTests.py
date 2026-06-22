# SPDX-License-Identifier: LGPL-2.1-or-later

# Round-trip fidelity tests for the mesh IO formats. Pattern: build a known mesh
# -> write -> read back -> compare facet/point counts and bounding-box extent.
# Indexed formats (PLY/OFF/SMF/OBJ) preserve the topology exactly; STL stores
# unindexed triangles but the kernel re-merges coincident points on read. VRML/
# X3D/AMF are export-only (no importer), which is asserted as a guard.

import os
import tempfile
import unittest

import FreeCAD
import Mesh


def _bbox_dims(mesh):
    pts = mesh.Points
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))


class MeshFormatRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fc_mesh_fmt_")

    def tearDown(self):
        for name in os.listdir(self.tmp):
            try:
                os.remove(os.path.join(self.tmp, name))
            except OSError:
                pass
        os.rmdir(self.tmp)

    def _path(self, name):
        return os.path.join(self.tmp, name)

    def _assertSameExtent(self, a, b, delta=1e-4):
        da, db = _bbox_dims(a), _bbox_dims(b)
        for x, y in zip(da, db):
            self.assertAlmostEqual(x, y, delta=delta)

    # --- indexed formats preserve point and facet counts exactly ------------
    def _roundtripIndexed(self, mesh, ext):
        path = self._path("mesh" + ext)
        mesh.write(path)
        back = Mesh.read(path)
        self.assertEqual(back.CountFacets, mesh.CountFacets)
        self.assertEqual(back.CountPoints, mesh.CountPoints)
        self._assertSameExtent(mesh, back)

    def testPlyRoundTrip(self):
        self._roundtripIndexed(Mesh.createSphere(5.0, 30), ".ply")

    def testOffRoundTrip(self):
        self._roundtripIndexed(Mesh.createCylinder(2, 10, 1, 1.0, 30), ".off")

    def testSmfRoundTrip(self):
        self._roundtripIndexed(Mesh.createTorus(10, 2, 30), ".smf")

    def testObjRoundTrip(self):
        self._roundtripIndexed(Mesh.createCone(2, 4, 10, 1, 1.0, 30), ".obj")

    # --- STL: unindexed triangles, facet count + extent preserved -----------
    def testStlBinaryRoundTrip(self):
        box = Mesh.createBox(10, 20, 30)
        path = self._path("box.stl")
        box.write(path)
        back = Mesh.read(path)
        self.assertEqual(back.CountFacets, 12)
        self._assertSameExtent(box, back)

    def testStlAsciiRoundTrip(self):
        box = Mesh.createBox(10, 20, 30)
        path = self._path("box.ast")
        box.write(path)  # .ast extension selects ASCII STL
        back = Mesh.read(path)
        self.assertEqual(back.CountFacets, 12)
        self._assertSameExtent(box, back)

    def testStlBinaryAndAsciiAgree(self):
        box = Mesh.createBox(7, 11, 13)
        pb = self._path("b.stl")
        pa = self._path("a.ast")
        box.write(pb)
        box.write(pa)
        bbin = Mesh.read(pb)
        basc = Mesh.read(pa)
        self.assertEqual(bbin.CountFacets, basc.CountFacets)
        self._assertSameExtent(bbin, basc, delta=1e-3)

    # --- export-only formats have no importer -------------------------------
    def testVrmlIsExportOnly(self):
        box = Mesh.createBox(10, 10, 10)
        path = self._path("box.wrl")
        box.write(path)
        self.assertTrue(os.path.getsize(path) > 0)
        # VRML/WRL has no mesh importer, so reading it back must fail cleanly.
        with self.assertRaises(Exception):
            Mesh.read(path)

    # --- malformed / unknown inputs fail cleanly ----------------------------
    def testReadingMissingFileRaises(self):
        with self.assertRaises(Exception):
            Mesh.read(self._path("does_not_exist.stl"))

    def testExportUnknownExtensionRaises(self):
        box = Mesh.createBox(1, 1, 1)
        with self.assertRaises(Exception):
            box.write(self._path("box.unknownext"))
