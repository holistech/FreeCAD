# SPDX-License-Identifier: LGPL-2.1-or-later

# ***************************************************************************
# *   Copyright (c) 2026 FreeCAD Project Association                        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""Unit tests for the Points module.

Covers the point-kernel scripting API, ASCII file round-trips and
PropertyPointKernel persistence through an FCStd save/restore cycle.

Notes on coverage:
- E57: this build links E57Format and can *read* .e57 files, but there is no
  E57 writer and no committed .e57 fixture, so a self-contained round-trip is
  not possible and E57 import is intentionally not exercised here.
- Only the ASCII (.asc) format is round-tripped through PointKernel.write/read:
  PointKernel.write always emits an ASCII payload regardless of the file
  extension, so writing then reading a .ply/.pcd through the kernel cannot
  round-trip. The format-aware document-level Points.export path is not stable
  headless, so it is left to the GUI test layer.
"""

import os
import tempfile
import unittest

import FreeCAD as App
import Points


_SAMPLE = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0), (7.0, 8.0, 9.0), (-1.5, 0.0, 2.25)]


def _coords(kernel):
    return [(round(p.x, 6), round(p.y, 6), round(p.z, 6)) for p in kernel.Points]


class PointKernelTest(unittest.TestCase):
    def testConstructAndCount(self):
        kernel = Points.Points()
        self.assertEqual(kernel.CountPoints, 0)
        kernel.addPoints([App.Vector(*p) for p in _SAMPLE])
        self.assertEqual(kernel.CountPoints, len(_SAMPLE))
        self.assertEqual(_coords(kernel), [tuple(round(c, 6) for c in p) for p in _SAMPLE])

    def testCopyIsIndependent(self):
        kernel = Points.Points()
        kernel.addPoints([App.Vector(*p) for p in _SAMPLE])
        clone = kernel.copy()
        self.assertEqual(clone.CountPoints, kernel.CountPoints)
        clone.addPoints([App.Vector(10, 10, 10)])
        self.assertEqual(clone.CountPoints, len(_SAMPLE) + 1)
        self.assertEqual(kernel.CountPoints, len(_SAMPLE))


class PointsFileRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fc_points_")

    def tearDown(self):
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def _round_trip(self, ext):
        kernel = Points.Points()
        kernel.addPoints([App.Vector(*p) for p in _SAMPLE])
        path = os.path.join(self.tmp, "cloud" + ext)
        kernel.write(path)
        self.assertTrue(os.path.exists(path))
        reloaded = Points.Points()
        reloaded.read(path)
        self.assertEqual(reloaded.CountPoints, len(_SAMPLE))
        return reloaded

    def testAsciiRoundTrip(self):
        reloaded = self._round_trip(".asc")
        self.assertEqual(_coords(reloaded), [tuple(round(c, 6) for c in p) for p in _SAMPLE])


class PropertyPointKernelPersistenceTest(unittest.TestCase):
    """PropertyPointKernel must survive an FCStd save/restore cycle."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="fc_points_fcstd_")
        self.doc = None

    def tearDown(self):
        if self.doc is not None:
            App.closeDocument(self.doc.Name)
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def testSaveRestore(self):
        kernel = Points.Points()
        kernel.addPoints([App.Vector(*p) for p in _SAMPLE])
        self.doc = App.newDocument("PointsPersistence")
        feature = self.doc.addObject("Points::Feature", "Cloud")
        feature.Points = kernel
        self.doc.recompute()
        self.assertEqual(feature.Points.CountPoints, len(_SAMPLE))

        path = os.path.join(self.tmp, "cloud.FCStd")
        self.doc.saveAs(path)
        name = self.doc.Name
        App.closeDocument(name)
        self.doc = None

        self.doc = App.open(path)
        restored = self.doc.getObject("Cloud")
        self.assertIsNotNone(restored)
        self.assertEqual(restored.Points.CountPoints, len(_SAMPLE))
        self.assertEqual(
            _coords(restored.Points),
            [tuple(round(c, 6) for c in p) for p in _SAMPLE],
        )


if __name__ == "__main__":
    unittest.main()
