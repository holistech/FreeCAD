// SPDX-License-Identifier: LGPL-2.1-or-later

// Known-answer unit tests for the PlaneGCS constraint solver. Each case builds a
// system whose solution (or diagnosis) is analytically known and asserts it
// directly through the GCS::System API, so a failure means the solver math is
// wrong rather than that some opaque output changed.
//
// Convention: the geometry coordinates that the solver may move are the only
// parameters passed to declareUnknowns()/solve(); constraint target values
// (coordinates, distances, angles, radii) are kept out of the unknowns so they
// act as fixed driving values. Enough CoordinateX/Y constraints are added to
// reach DoF = 0, making the numeric solution unique and pin-pointable.

#include <cmath>
#include <numbers>
#include <vector>

#include <gtest/gtest.h>

#include "Mod/Sketcher/App/planegcs/GCS.h"
#include "Mod/Sketcher/App/planegcs/Geo.h"

namespace
{
// Build a GCS::Point referencing externally-owned coordinate doubles.
GCS::Point mkPoint(double* x, double* y)
{
    GCS::Point p;
    p.x = x;
    p.y = y;
    return p;
}

GCS::Line mkLine(GCS::Point p1, GCS::Point p2)
{
    GCS::Line l;
    l.p1 = p1;
    l.p2 = p2;
    return l;
}
}  // namespace

class PlaneGCSSolverTest: public ::testing::Test
{
protected:
    GCS::System sys;
};

// 1. Two points, one fixed at the origin and the other pinned to the x-axis, with
// a distance of 10 -> the free point lands at (+/-10, 0).
TEST_F(PlaneGCSSolverTest, p2pDistanceProducesKnownCoordinates)  // NOLINT
{
    double p1x = 2.0, p1y = -3.0, p2x = 4.0, p2y = 1.0;
    GCS::Point p1 = mkPoint(&p1x, &p1y);
    GCS::Point p2 = mkPoint(&p2x, &p2y);
    double zero = 0.0, dist = 10.0;

    sys.addConstraintCoordinateX(p1, &zero, 1);
    sys.addConstraintCoordinateY(p1, &zero, 2);
    sys.addConstraintCoordinateY(p2, &zero, 3);
    sys.addConstraintP2PDistance(p1, p2, &dist, 4);

    GCS::VEC_pD params {&p1x, &p1y, &p2x, &p2y};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    ASSERT_EQ(status, GCS::Success);
    sys.applySolution();

    EXPECT_NEAR(p1x, 0.0, 1e-6);
    EXPECT_NEAR(p1y, 0.0, 1e-6);
    EXPECT_NEAR(p2y, 0.0, 1e-6);
    EXPECT_NEAR(std::abs(p2x), 10.0, 1e-6);
}

// 2. Point coincidence: a free point is dragged onto a point fixed at (3, 4).
TEST_F(PlaneGCSSolverTest, p2pCoincidentMatchesFixedPoint)  // NOLINT
{
    double ax = 3.0, ay = 4.0, bx = -7.0, by = 9.0;
    GCS::Point a = mkPoint(&ax, &ay);
    GCS::Point b = mkPoint(&bx, &by);
    double tx = 3.0, ty = 4.0;

    sys.addConstraintCoordinateX(a, &tx, 1);
    sys.addConstraintCoordinateY(a, &ty, 2);
    sys.addConstraintP2PCoincident(a, b, 3);

    GCS::VEC_pD params {&ax, &ay, &bx, &by};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    ASSERT_EQ(status, GCS::Success);
    sys.applySolution();

    EXPECT_NEAR(bx, 3.0, 1e-6);
    EXPECT_NEAR(by, 4.0, 1e-6);
}

// 3. Point-to-line distance: the line is the x-axis, the free point's x is pinned
// to 4, the perpendicular distance to the line is 3 -> point at distance 3 from y=0.
TEST_F(PlaneGCSSolverTest, pointToLineDistanceProducesKnownOffset)  // NOLINT
{
    double l1x = 0.0, l1y = 0.0, l2x = 10.0, l2y = 0.0;  // the x-axis
    double qx = 4.0, qy = 6.0;
    GCS::Point lp1 = mkPoint(&l1x, &l1y);
    GCS::Point lp2 = mkPoint(&l2x, &l2y);
    GCS::Line line = mkLine(lp1, lp2);
    GCS::Point q = mkPoint(&qx, &qy);
    double zero = 0.0, ten = 10.0, four = 4.0, dist = 3.0;

    // Fix the line onto the x-axis and the query point's x coordinate.
    sys.addConstraintCoordinateX(lp1, &zero, 1);
    sys.addConstraintCoordinateY(lp1, &zero, 2);
    sys.addConstraintCoordinateX(lp2, &ten, 3);
    sys.addConstraintCoordinateY(lp2, &zero, 4);
    sys.addConstraintCoordinateX(q, &four, 5);
    sys.addConstraintP2LDistance(q, line, &dist, /*ccw*/ true, 6);

    GCS::VEC_pD params {&l1x, &l1y, &l2x, &l2y, &qx, &qy};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    ASSERT_EQ(status, GCS::Success);
    sys.applySolution();

    EXPECT_NEAR(qx, 4.0, 1e-6);
    // The signed-distance sign depends on orientation; the magnitude is the invariant.
    EXPECT_NEAR(std::abs(qy), 3.0, 1e-6);
}

// 4. Angle between two lines sharing a fixed origin: l1 along +x, the angle is 90
// degrees -> l2's free endpoint sits on the y-axis (x ~ 0), i.e. directions are
// perpendicular.
TEST_F(PlaneGCSSolverTest, l2lAngleMakesLinesPerpendicular)  // NOLINT
{
    double o1x = 0.0, o1y = 0.0, e1x = 10.0, e1y = 0.0;  // l1 = +x axis
    double o2x = 0.0, o2y = 0.0, e2x = 5.0, e2y = 5.0;   // l2 free end
    GCS::Point o1 = mkPoint(&o1x, &o1y);
    GCS::Point e1 = mkPoint(&e1x, &e1y);
    GCS::Point o2 = mkPoint(&o2x, &o2y);
    GCS::Point e2 = mkPoint(&e2x, &e2y);
    GCS::Line l1 = mkLine(o1, e1);
    GCS::Line l2 = mkLine(o2, e2);
    double zero = 0.0, ten = 10.0;
    double angle = std::numbers::pi / 2;

    sys.addConstraintCoordinateX(o1, &zero, 1);
    sys.addConstraintCoordinateY(o1, &zero, 2);
    sys.addConstraintCoordinateX(e1, &ten, 3);
    sys.addConstraintCoordinateY(e1, &zero, 4);
    sys.addConstraintCoordinateX(o2, &zero, 5);
    sys.addConstraintCoordinateY(o2, &zero, 6);
    sys.addConstraintL2LAngle(l1, l2, &angle, 7);

    GCS::VEC_pD params {&o1x, &o1y, &e1x, &e1y, &o2x, &o2y, &e2x, &e2y};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    ASSERT_EQ(status, GCS::Success);
    sys.applySolution();

    // l1 direction is (1,0); perpendicular means l2's endpoint x-component vanishes.
    double len2 = std::hypot(e2x - o2x, e2y - o2y);
    ASSERT_GT(len2, 1e-6);
    double dot = (e1x - o1x) * (e2x - o2x) + (e1y - o1y) * (e2y - o2y);
    EXPECT_NEAR(dot / (10.0 * len2), 0.0, 1e-6);
}

// 5. Circle radius + point-on-circle: centre at origin, radius 5, the point's x is
// pinned to 3 -> the point lands at (3, +/-4) and satisfies x^2 + y^2 = 25.
TEST_F(PlaneGCSSolverTest, circleRadiusAndPointOnCircle)  // NOLINT
{
    double cx = 0.0, cy = 0.0, r = 2.0;
    double px = 3.0, py = 7.0;
    GCS::Point center = mkPoint(&cx, &cy);
    GCS::Circle circle;
    circle.center = center;
    circle.rad = &r;
    GCS::Point p = mkPoint(&px, &py);
    double zero = 0.0, three = 3.0, radius = 5.0;

    sys.addConstraintCoordinateX(center, &zero, 1);
    sys.addConstraintCoordinateY(center, &zero, 2);
    sys.addConstraintCircleRadius(circle, &radius, 3);
    sys.addConstraintCoordinateX(p, &three, 4);
    sys.addConstraintPointOnCircle(p, circle, 5);

    GCS::VEC_pD params {&cx, &cy, &r, &px, &py};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    ASSERT_EQ(status, GCS::Success);
    sys.applySolution();

    EXPECT_NEAR(r, 5.0, 1e-6);
    EXPECT_NEAR(px, 3.0, 1e-6);
    EXPECT_NEAR(std::abs(py), 4.0, 1e-6);
    EXPECT_NEAR((px - cx) * (px - cx) + (py - cy) * (py - cy), 25.0, 1e-5);
}

// 6. A fully-constrained system has zero remaining degrees of freedom and no
// conflicts or redundancies.
TEST_F(PlaneGCSSolverTest, fullyConstrainedSystemHasZeroDof)  // NOLINT
{
    double ax = 1.0, ay = 1.0, bx = 2.0, by = 2.0;
    GCS::Point a = mkPoint(&ax, &ay);
    GCS::Point b = mkPoint(&bx, &by);
    double tax = 0.0, tay = 0.0, tbx = 3.0, tby = 4.0;

    sys.addConstraintCoordinateX(a, &tax, 1);
    sys.addConstraintCoordinateY(a, &tay, 2);
    sys.addConstraintCoordinateX(b, &tbx, 3);
    sys.addConstraintCoordinateY(b, &tby, 4);

    GCS::VEC_pD params {&ax, &ay, &bx, &by};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    ASSERT_EQ(status, GCS::Success);

    EXPECT_EQ(sys.dofsNumber(), 0);
    EXPECT_FALSE(sys.hasConflicting());
    EXPECT_FALSE(sys.hasRedundant());
}

// 7. Two identical distance constraints on the same point pair: the second is
// redundant. The system still solves, but the redundancy is reported.
TEST_F(PlaneGCSSolverTest, duplicateDistanceIsReportedRedundant)  // NOLINT
{
    double p1x = 0.0, p1y = 0.0, p2x = 4.0, p2y = 0.0;
    GCS::Point p1 = mkPoint(&p1x, &p1y);
    GCS::Point p2 = mkPoint(&p2x, &p2y);
    double zero = 0.0, distA = 10.0, distB = 10.0;

    sys.addConstraintCoordinateX(p1, &zero, 1);
    sys.addConstraintCoordinateY(p1, &zero, 2);
    sys.addConstraintCoordinateY(p2, &zero, 3);
    sys.addConstraintP2PDistance(p1, p2, &distA, 4);
    sys.addConstraintP2PDistance(p1, p2, &distB, 5);  // redundant duplicate

    GCS::VEC_pD params {&p1x, &p1y, &p2x, &p2y};
    sys.declareUnknowns(params);
    int status = sys.solve(params);
    // A redundant-but-consistent system still solves; the solver may report
    // Converged rather than an exact Success because of the extra constraint.
    ASSERT_TRUE(status == GCS::Success || status == GCS::Converged);

    EXPECT_TRUE(sys.hasRedundant());
    GCS::VEC_I redundant;
    sys.getRedundant(redundant);
    EXPECT_FALSE(redundant.empty());
    EXPECT_FALSE(sys.hasConflicting());
}

// 8. Two contradictory distance constraints (10 and 20) on the same pinned point
// pair: the system is conflicting.
TEST_F(PlaneGCSSolverTest, contradictoryDistancesAreReportedConflicting)  // NOLINT
{
    double p1x = 0.0, p1y = 0.0, p2x = 4.0, p2y = 0.0;
    GCS::Point p1 = mkPoint(&p1x, &p1y);
    GCS::Point p2 = mkPoint(&p2x, &p2y);
    double zero = 0.0, distA = 10.0, distB = 20.0;

    sys.addConstraintCoordinateX(p1, &zero, 1);
    sys.addConstraintCoordinateY(p1, &zero, 2);
    sys.addConstraintCoordinateY(p2, &zero, 3);
    sys.addConstraintP2PDistance(p1, p2, &distA, 4);
    sys.addConstraintP2PDistance(p1, p2, &distB, 5);  // contradicts tag 4

    GCS::VEC_pD params {&p1x, &p1y, &p2x, &p2y};
    sys.declareUnknowns(params);
    sys.solve(params);

    EXPECT_TRUE(sys.hasConflicting());
    GCS::VEC_I conflicting;
    sys.getConflicting(conflicting);
    EXPECT_FALSE(conflicting.empty());
}
