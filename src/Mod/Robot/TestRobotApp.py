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

"""Unit tests for the Robot module.

The default ``Robot6Axis`` is initialized with the KUKA IR500 DH parameters,
so forward/inverse kinematics, waypoints and trajectories can all be exercised
headless without an external kinematic-definition file. Expected values are
derived analytically (home pose, a 90 deg base rotation, straight-line path
length).
"""

import unittest

import FreeCAD
from FreeCAD import Placement, Vector, Rotation
import Robot


# Home pose of the default KUKA IR500 (all axes at zero).
HOME_X, HOME_Y, HOME_Z = 3125.0, 0.0, 1100.0


class ForwardKinematicsTest(unittest.TestCase):
    def testHomePose(self):
        """With all axes at zero the TCP sits at the known home position."""
        r = Robot.Robot6Axis()
        tcp = r.Tcp.Base
        self.assertAlmostEqual(tcp.x, HOME_X, places=5)
        self.assertAlmostEqual(tcp.y, HOME_Y, places=5)
        self.assertAlmostEqual(tcp.z, HOME_Z, places=5)

    def testAxis1RotationSwingsTcp(self):
        """Rotating axis 1 by +90 deg swings the TCP from +X to -Y."""
        r = Robot.Robot6Axis()
        r.Axis1 = 90.0
        self.assertAlmostEqual(r.Axis1, 90.0, places=6)
        tcp = r.Tcp.Base
        self.assertAlmostEqual(tcp.x, 0.0, places=4)
        self.assertAlmostEqual(tcp.y, -HOME_X, places=4)
        self.assertAlmostEqual(tcp.z, HOME_Z, places=5)

    def testAxisRoundTrips(self):
        """Setting an axis value reads back unchanged."""
        r = Robot.Robot6Axis()
        r.Axis2 = -30.0
        self.assertAlmostEqual(r.Axis2, -30.0, places=6)


class InverseKinematicsTest(unittest.TestCase):
    def testHomeRoundTrip(self):
        """Feeding the home placement back through IK recovers zero axes."""
        r = Robot.Robot6Axis()
        home = r.Tcp
        r.Tcp = home  # triggers inverse kinematics
        for axis in (r.Axis1, r.Axis2, r.Axis3, r.Axis4, r.Axis5, r.Axis6):
            self.assertAlmostEqual(axis, 0.0, places=5)

    def testReachableTargetRoundTrip(self):
        """A pose reached by FK is recovered by IK (axis-1 at 45 deg)."""
        r = Robot.Robot6Axis()
        r.Axis1 = 45.0
        target = r.Tcp
        r2 = Robot.Robot6Axis()
        r2.Tcp = target
        self.assertAlmostEqual(r2.Axis1, 45.0, places=4)


class WaypointTest(unittest.TestCase):
    def testConstruction(self):
        wp = Robot.Waypoint(
            Placement(Vector(1000, 0, 1000), Rotation()), "PTP", "Pt1"
        )
        self.assertEqual(wp.Type, "PTP")
        self.assertEqual(wp.Name, "Pt1")
        self.assertEqual(tuple(wp.Pos.Base), (1000.0, 0.0, 1000.0))


class TrajectoryTest(unittest.TestCase):
    def testLengthAndInterpolation(self):
        """A two-point straight path has the expected Euclidean length and
        its start interpolates to the first waypoint."""
        wp1 = Robot.Waypoint(
            Placement(Vector(1000, 0, 1000), Rotation()), "PTP", "Pt1"
        )
        wp2 = Robot.Waypoint(
            Placement(Vector(1500, 0, 1000), Rotation()), "PTP", "Pt2"
        )
        traj = Robot.Trajectory()
        traj.insertWaypoints(wp1)
        traj.insertWaypoints(wp2)
        self.assertEqual(len(traj.Waypoints), 2)
        self.assertAlmostEqual(traj.Length, 500.0, places=5)
        self.assertGreater(traj.Duration, 0.0)
        start = traj.position(0.0)
        self.assertAlmostEqual(start.Base.x, 1000.0, places=5)

    # NOTE: Trajectory.deleteLast() currently aborts the process with a native
    # crash, so it is intentionally not exercised here (tracked as a follow-up
    # defect). insertWaypoints / Length / Duration / position are stable.


if __name__ == "__main__":
    unittest.main()
