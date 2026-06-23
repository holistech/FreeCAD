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

"""Unit tests for the ReverseEngineering module.

The tests drive each algorithm with synthetic ground-truth geometry so the
expected answer is known analytically. ``approxSurface`` and ``approxCurve``
are OCC-only and always available. The remaining algorithms are backed by the
Point Cloud Library (PCL); they are guarded with ``skipUnless`` so the suite
runs cleanly on builds compiled without the optional PCL components.
"""

import math
import unittest

import FreeCAD as App
import Points
import ReverseEngineering as Reen


def _plane_cloud(samples=11, fz=lambda x, y: 0.0):
    """A regular grid of points over [0, 1]^2 with z given by ``fz``."""
    kernel = Points.Points()
    step = 1.0 / (samples - 1)
    pts = [
        App.Vector(i * step, j * step, fz(i * step, j * step))
        for i in range(samples)
        for j in range(samples)
    ]
    kernel.addPoints(pts)
    return kernel


def _has(name):
    return hasattr(Reen, name)


class ApproxSurfaceTest(unittest.TestCase):
    """approxSurface is OCC-only and always present."""

    def testPlaneFit(self):
        """A B-spline fitted to a planar point set reproduces the plane."""
        # z = 2x + 3y + 1 sampled on an 11x11 grid
        cloud = _plane_cloud(11, lambda x, y: 2.0 * x + 3.0 * y + 1.0)
        surf = Reen.approxSurface(
            Points=cloud, UDegree=3, VDegree=3, NbUPoles=6, NbVPoles=6
        )
        self.assertEqual(surf.TypeId, "Part::GeomBSplineSurface")
        for u in (0.2, 0.5, 0.8):
            for v in (0.2, 0.5, 0.8):
                pt = surf.value(u, v)
                self.assertAlmostEqual(
                    pt.z, 2.0 * pt.x + 3.0 * pt.y + 1.0, places=4
                )

    def testPoleCountHonored(self):
        """The requested number of poles is reflected in the result."""
        cloud = _plane_cloud(11, lambda x, y: x + y)
        surf = Reen.approxSurface(
            Points=cloud, UDegree=3, VDegree=3, NbUPoles=6, NbVPoles=6
        )
        self.assertEqual(surf.NbUPoles, 6)
        self.assertEqual(surf.NbVPoles, 6)


class ApproxCurveTest(unittest.TestCase):
    """approxCurve is OCC-only and always present."""

    def testLineFit(self):
        """A B-spline fitted to a straight line reproduces the line."""
        # (t, 2t + 1, 0) for t in [0, 1]; approxCurve needs (x, y, z) tuples.
        pts = [(i / 20.0, 2.0 * (i / 20.0) + 1.0, 0.0) for i in range(21)]
        curve = Reen.approxCurve(pts)
        self.assertEqual(curve.TypeId, "Part::GeomBSplineCurve")
        end = curve.value(curve.LastParameter)
        self.assertAlmostEqual(end.x, 1.0, places=4)
        self.assertAlmostEqual(end.y, 3.0, places=4)
        self.assertAlmostEqual(end.z, 0.0, places=4)
        for p in (0.25, 0.5, 0.75):
            param = curve.FirstParameter + p * (
                curve.LastParameter - curve.FirstParameter
            )
            pt = curve.value(param)
            self.assertAlmostEqual(pt.y, 2.0 * pt.x + 1.0, places=3)
            self.assertAlmostEqual(pt.z, 0.0, places=4)


@unittest.skipUnless(_has("normalEstimation"), "PCL filters not available")
class NormalEstimationTest(unittest.TestCase):
    def testFlatPlaneNormals(self):
        """Normals of a flat z=0 cloud all point along +/-Z."""
        cloud = _plane_cloud(11, lambda x, y: 0.0)
        normals = Reen.normalEstimation(cloud, KSearch=5)
        self.assertEqual(len(normals), cloud.CountPoints)
        for n in normals:
            self.assertAlmostEqual(abs(n.z), 1.0, places=5)


@unittest.skipUnless(_has("sampleConsensus"), "PCL sample consensus not available")
class SampleConsensusTest(unittest.TestCase):
    def testPlane(self):
        """RANSAC recovers a unit Z normal and full inlier set for a plane."""
        cloud = _plane_cloud(11, lambda x, y: 0.0)
        result = Reen.sampleConsensus(SacModel="Plane", Points=cloud)
        params = result["Parameters"]
        # plane: a*x + b*y + c*z + d = 0 -> normal (a, b, c) is +/-Z, d = 0
        self.assertAlmostEqual(abs(params[2]), 1.0, places=3)
        self.assertAlmostEqual(params[0], 0.0, places=3)
        self.assertAlmostEqual(params[1], 0.0, places=3)
        self.assertEqual(len(result["Model"]), cloud.CountPoints)

    def testSphere(self):
        """RANSAC recovers the center and radius of a sampled sphere."""
        cx, cy, cz, r = 2.0, 3.0, 4.0, 1.0
        kernel = Points.Points()
        pts = []
        n = 12
        for i in range(1, n):
            theta = math.pi * i / n
            for j in range(2 * n):
                phi = 2.0 * math.pi * j / (2 * n)
                pts.append(
                    App.Vector(
                        cx + r * math.sin(theta) * math.cos(phi),
                        cy + r * math.sin(theta) * math.sin(phi),
                        cz + r * math.cos(theta),
                    )
                )
        kernel.addPoints(pts)
        result = Reen.sampleConsensus(SacModel="Sphere", Points=kernel)
        params = result["Parameters"]
        self.assertAlmostEqual(params[0], cx, places=3)
        self.assertAlmostEqual(params[1], cy, places=3)
        self.assertAlmostEqual(params[2], cz, places=3)
        self.assertAlmostEqual(params[3], r, places=3)


@unittest.skipUnless(_has("triangulate"), "PCL surface not available")
class TriangulateTest(unittest.TestCase):
    def testGreedyTriangulation(self):
        """Greedy triangulation of a height field yields a non-empty mesh
        that preserves the input point count."""
        cloud = _plane_cloud(21, lambda x, y: 0.05 * math.sin(6.0 * x))
        mesh = Reen.triangulate(Points=cloud, SearchRadius=0.3)
        self.assertEqual(mesh.CountPoints, cloud.CountPoints)
        self.assertGreater(mesh.CountFacets, 0)


@unittest.skipUnless(
    _has("regionGrowingSegmentation"), "PCL segmentation not available"
)
class SegmentationTest(unittest.TestCase):
    def testSingleSmoothSurface(self):
        """A single smooth surface segments into at least one region whose
        indices all reference valid points."""
        cloud = _plane_cloud(21, lambda x, y: 0.0)
        clusters = Reen.regionGrowingSegmentation(cloud, KSearch=10)
        self.assertGreaterEqual(len(clusters), 1)
        for cluster in clusters:
            for idx in cluster:
                self.assertTrue(0 <= idx < cloud.CountPoints)


if __name__ == "__main__":
    unittest.main()
