// SPDX-License-Identifier: LGPL-2.1-or-later

// Golden tests for the TechDraw hidden-line-removal (HLR) projection. The HLR
// stage (ProjectionAlgos -> OCCT HLRBRep_Algo) had no coverage at all. Each case
// projects a known OCC solid along a known direction and asserts the visible (V)
// and hidden (H) edge counts, plus the outline (VO) for the cylinder. The exact
// counts depend on how OCCT classifies coincident front/back edges, so they were
// calibrated against the first green run and are pinned here as expectations. A
// wrong visible/hidden classification or projection direction breaks a test.

#include <gtest/gtest.h>

#include <Bnd_Box.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepBndLib.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <TopoDS_Shape.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include "Mod/TechDraw/App/DrawUtil.h"
#include "Mod/TechDraw/App/ProjectionAlgos.h"
#include "src/App/InitApplication.h"

class HlrGoldenTest: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }

    static int edges(const TopoDS_Shape& s)
    {
        return s.IsNull() ? 0 : TechDraw::DrawUtil::countSubShapes(s, TopAbs_EDGE);
    }
};

// NOLINTBEGIN(cppcoreguidelines-*,readability-*)

namespace
{
TopoDS_Shape boxShape(double dx, double dy, double dz)
{
    return BRepPrimAPI_MakeBox(dx, dy, dz).Shape();
}

TopoDS_Shape cylinderZ(double r, double h)
{
    return BRepPrimAPI_MakeCylinder(r, h).Shape();
}

// 20-cube with a radius-5 bore drilled all the way through along Z at (10,10).
TopoDS_Shape cubeWithThroughHole()
{
    TopoDS_Shape cube = BRepPrimAPI_MakeBox(20.0, 20.0, 20.0).Shape();
    gp_Ax2 axis(gp_Pnt(10.0, 10.0, -5.0), gp_Dir(0.0, 0.0, 1.0));
    TopoDS_Shape bore = BRepPrimAPI_MakeCylinder(axis, 5.0, 30.0).Shape();
    return BRepAlgoAPI_Cut(cube, bore).Shape();
}
}  // namespace

// Frontal view of a cube: four visible outline edges, four coincident hidden
// back-face edges.
TEST_F(HlrGoldenTest, boxFrontView)
{
    TopoDS_Shape box = boxShape(10, 10, 10);
    Base::Vector3d dir(0, 0, 1);
    TechDraw::ProjectionAlgos algo(box, dir);
    EXPECT_EQ(edges(algo.V), 4);
    EXPECT_EQ(edges(algo.H), 4);
}

// Isometric view of a cube: the silhouette hexagon plus the three front edges to
// the near corner are visible (9); the three edges to the far corner are hidden.
TEST_F(HlrGoldenTest, boxIsometricViewSeparatesVisibleFromHidden)
{
    TopoDS_Shape box = boxShape(10, 10, 10);
    Base::Vector3d dir(1, 1, 1);
    TechDraw::ProjectionAlgos algo(box, dir);
    EXPECT_EQ(edges(algo.V), 9);
    EXPECT_EQ(edges(algo.H), 3);
}

// A non-cubic box viewed along Z: the visible outline is a 10 x 20 rectangle, so
// the projected visible compound must span exactly those dimensions.
TEST_F(HlrGoldenTest, rectangularBoxProjectionHasCorrectExtent)
{
    TopoDS_Shape box = boxShape(10, 20, 30);
    Base::Vector3d dir(0, 0, 1);
    TechDraw::ProjectionAlgos algo(box, dir);
    EXPECT_EQ(edges(algo.V), 4);
    EXPECT_EQ(edges(algo.H), 4);

    ASSERT_FALSE(algo.V.IsNull());
    Bnd_Box bb;
    BRepBndLib::Add(algo.V, bb);
    Standard_Real xmin, ymin, zmin, xmax, ymax, zmax;
    bb.Get(xmin, ymin, zmin, xmax, ymax, zmax);
    double w = xmax - xmin;
    double h = ymax - ymin;
    // The 10 and 20 extents must appear (order/sign depends on the projection axis).
    double lo = std::min(w, h);
    double hi = std::max(w, h);
    EXPECT_NEAR(lo, 10.0, 1e-6);
    EXPECT_NEAR(hi, 20.0, 1e-6);
}

// Cylinder seen from the side: two outline generators (one classified into VO) plus
// the visible end edge; the far end edge is hidden.
TEST_F(HlrGoldenTest, cylinderSideView)
{
    TopoDS_Shape cyl = cylinderZ(5, 20);
    Base::Vector3d dir(0, 1, 0);
    TechDraw::ProjectionAlgos algo(cyl, dir);
    EXPECT_EQ(edges(algo.V), 3);
    EXPECT_EQ(edges(algo.VO), 1);
    EXPECT_EQ(edges(algo.H), 2);
}

// Cylinder seen end-on: one visible outline circle, one coincident hidden circle.
TEST_F(HlrGoldenTest, cylinderEndView)
{
    TopoDS_Shape cyl = cylinderZ(5, 20);
    Base::Vector3d dir(0, 0, 1);
    TechDraw::ProjectionAlgos algo(cyl, dir);
    EXPECT_EQ(edges(algo.V), 1);
    EXPECT_EQ(edges(algo.H), 1);
}

// Through-hole cube viewed along the bore: four outline edges plus the near hole
// circle are visible (5); the back outline and far hole circle are hidden (5).
TEST_F(HlrGoldenTest, throughHoleAlongBore)
{
    TopoDS_Shape hole = cubeWithThroughHole();
    Base::Vector3d dir(0, 0, 1);
    TechDraw::ProjectionAlgos algo(hole, dir);
    EXPECT_EQ(edges(algo.V), 5);
    EXPECT_EQ(edges(algo.H), 5);
}

// Through-hole cube viewed across the bore: the bore walls behind the front face
// are hidden, so the hidden-edge set is substantially richer than the visible one.
TEST_F(HlrGoldenTest, throughHoleAcrossBore)
{
    TopoDS_Shape hole = cubeWithThroughHole();
    Base::Vector3d dir(0, 1, 0);
    TechDraw::ProjectionAlgos algo(hole, dir);
    EXPECT_EQ(edges(algo.V), 4);
    EXPECT_GE(edges(algo.H), 2);  // hidden back bore-wall edges must be present
}

// NOLINTEND(cppcoreguidelines-*,readability-*)
