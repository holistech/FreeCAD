// SPDX-License-Identifier: LGPL-2.1-or-later

// Tests for the mesh repair pipeline (defect detection + fixup), the boolean set
// operations and decimation, none of which were covered by the existing C++ suite.
// Defects are built programmatically so the expected outcome is exact.
//
// NOTE on booleans: the built-in mesh boolean backend (MeshCore::SetOperations,
// used by MeshObject::unite/intersect/subtract) does NOT produce watertight,
// volumetrically-correct results even for trivial axis-aligned cubes (union and
// difference come out geometrically wrong and the volumes vary between runs). So
// these tests only assert what is reliably true (the operation runs and yields a
// non-empty result, and intersection stays within the overlap bounds); the
// inaccuracy itself is recorded as a follow-up (FU-3), not asserted as correct.

#include <gtest/gtest.h>

#include <Mod/Mesh/App/Mesh.h>
#include <Mod/Mesh/App/Core/Evaluation.h>
#include <Mod/Mesh/App/Core/Degeneration.h>
#include <Mod/Mesh/App/Core/MeshKernel.h>

#include <Base/BoundBox.h>
#include <Base/Vector3D.h>
#include <src/App/InitApplication.h>

#include <memory>

class MeshRepairTest: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }
};

// NOLINTBEGIN(cppcoreguidelines-*,readability-*)

// 1. A pristine cube is a valid closed solid with the expected topology and volume.
TEST_F(MeshRepairTest, cubeIsSolidWithKnownVolume)
{
    std::unique_ptr<Mesh::MeshObject> cube(Mesh::MeshObject::createCube(2.0F, 2.0F, 2.0F));
    ASSERT_NE(cube, nullptr);
    EXPECT_EQ(cube->countPoints(), 8);
    EXPECT_EQ(cube->countFacets(), 12);
    EXPECT_TRUE(cube->isSolid());
    EXPECT_FALSE(cube->hasNonManifolds());
    EXPECT_NEAR(cube->getVolume(), 8.0, 1e-4);
}

// 2. Removing a facet opens the mesh: it is no longer solid and has one less facet.
TEST_F(MeshRepairTest, deletingFacetBreaksSolid)
{
    std::unique_ptr<Mesh::MeshObject> cube(Mesh::MeshObject::createCube(2.0F, 2.0F, 2.0F));
    ASSERT_NE(cube, nullptr);
    ASSERT_TRUE(cube->isSolid());

    cube->deleteFacets({0});
    EXPECT_EQ(cube->countFacets(), 11);
    EXPECT_FALSE(cube->isSolid());
}

// 3. Three facets sharing one edge form a non-manifold edge, which is detected and
// can be removed.
TEST_F(MeshRepairTest, nonManifoldEdgeDetectedAndRemoved)
{
    MeshCore::MeshKernel kernel;
    Base::Vector3f a {0, 0, 0};
    Base::Vector3f b {1, 0, 0};
    Base::Vector3f c {0, 1, 0};
    Base::Vector3f d {0, -1, 0};
    Base::Vector3f e {0, 0, 1};
    // All three facets share edge a-b -> non-manifold.
    kernel.AddFacet(MeshCore::MeshGeomFacet(a, b, c));
    kernel.AddFacet(MeshCore::MeshGeomFacet(a, b, d));
    kernel.AddFacet(MeshCore::MeshGeomFacet(a, b, e));

    EXPECT_FALSE(MeshCore::MeshEvalTopology(kernel).Evaluate());

    Mesh::MeshObject obj(kernel);
    EXPECT_TRUE(obj.hasNonManifolds());
    obj.removeNonManifolds();
    EXPECT_FALSE(obj.hasNonManifolds());
}

// 4. Two identical facets are reported as duplicates and merged by the fixer.
TEST_F(MeshRepairTest, duplicateFacetsDetectedAndFixed)
{
    MeshCore::MeshKernel kernel;
    Base::Vector3f p1 {0, 0, 0};
    Base::Vector3f p2 {1, 0, 0};
    Base::Vector3f p3 {0, 1, 0};
    kernel.AddFacet(MeshCore::MeshGeomFacet(p1, p2, p3));
    kernel.AddFacet(MeshCore::MeshGeomFacet(p1, p2, p3));  // exact duplicate
    ASSERT_EQ(kernel.CountFacets(), 2);

    EXPECT_FALSE(MeshCore::MeshEvalDuplicateFacets(kernel).Evaluate());
    EXPECT_TRUE(MeshCore::MeshFixDuplicateFacets(kernel).Fixup());
    EXPECT_EQ(kernel.CountFacets(), 1);
    EXPECT_TRUE(MeshCore::MeshEvalDuplicateFacets(kernel).Evaluate());
}

// 5. A facet whose three points are collinear is degenerate; detection flags it and
// the fixer removes it.
TEST_F(MeshRepairTest, degenerateFacetDetectedAndFixed)
{
    MeshCore::MeshKernel kernel;
    Base::Vector3f p1 {0, 0, 0};
    Base::Vector3f p2 {1, 0, 0};
    Base::Vector3f p3 {0, 1, 0};
    kernel.AddFacet(MeshCore::MeshGeomFacet(p1, p2, p3));   // valid
    Base::Vector3f c1 {0, 0, 0};
    Base::Vector3f c2 {1, 0, 0};
    Base::Vector3f c3 {2, 0, 0};                            // collinear -> degenerate
    kernel.AddFacet(MeshCore::MeshGeomFacet(c1, c2, c3));
    ASSERT_EQ(kernel.CountFacets(), 2);

    const float eps = 1.0e-6F;
    EXPECT_FALSE(MeshCore::MeshEvalDegeneratedFacets(kernel, eps).Evaluate());
    EXPECT_TRUE(MeshCore::MeshFixDegeneratedFacets(kernel, eps).Fixup());
    EXPECT_TRUE(MeshCore::MeshEvalDegeneratedFacets(kernel, eps).Evaluate());
}

// --- boolean set operations on overlapping axis-aligned cubes ---------------
// A = [0,2]x[0,2]x[0,2], B = [1,3]x[0,2]x[0,2]; overlap is [1,2]x[0,2]x[0,2].
// See the file header: the built-in mesh booleans are not volumetrically
// reliable, so we only smoke-test that each operation runs and returns a
// non-empty result, and that intersection stays within the overlap box.

namespace
{
std::unique_ptr<Mesh::MeshObject> makeBoxBetween(double x0, double x1)
{
    Base::BoundBox3d bb(x0, 0.0, 0.0, x1, 2.0, 2.0);
    return std::unique_ptr<Mesh::MeshObject>(Mesh::MeshObject::createCube(bb));
}
}  // namespace

TEST_F(MeshRepairTest, booleanOperationsReturnNonEmptyResults)
{
    auto a = makeBoxBetween(0.0, 2.0);
    auto b = makeBoxBetween(1.0, 3.0);
    ASSERT_NE(a, nullptr);
    ASSERT_NE(b, nullptr);

    std::unique_ptr<Mesh::MeshObject> u(a->unite(*b));
    std::unique_ptr<Mesh::MeshObject> i(a->intersect(*b));
    std::unique_ptr<Mesh::MeshObject> d(a->subtract(*b));
    ASSERT_NE(u, nullptr);
    ASSERT_NE(i, nullptr);
    ASSERT_NE(d, nullptr);
    EXPECT_GT(u->countFacets(), 0u);
    EXPECT_GT(i->countFacets(), 0u);
    EXPECT_GT(d->countFacets(), 0u);
}

TEST_F(MeshRepairTest, booleanIntersectionStaysWithinOverlap)
{
    auto a = makeBoxBetween(0.0, 2.0);
    auto b = makeBoxBetween(1.0, 3.0);
    std::unique_ptr<Mesh::MeshObject> i(a->intersect(*b));
    ASSERT_NE(i, nullptr);
    ASSERT_GT(i->countFacets(), 0u);

    // The intersection cannot lie outside the [1,2] overlap slab in x.
    Base::BoundBox3d bb = i->getBoundBox();
    EXPECT_GE(bb.MinX, 1.0 - 1e-6);
    EXPECT_LE(bb.MaxX, 2.0 + 1e-6);
}

// 9. Decimation reduces the facet count while preserving the closed-solid topology
// and the volume within tolerance.
TEST_F(MeshRepairTest, decimationPreservesTopologyAndVolume)
{
    std::unique_ptr<Mesh::MeshObject> sphere(Mesh::MeshObject::createSphere(10.0F, 50));
    ASSERT_NE(sphere, nullptr);
    ASSERT_TRUE(sphere->isSolid());
    unsigned long facets0 = sphere->countFacets();
    double volume0 = sphere->getVolume();
    ASSERT_GT(facets0, 0u);

    sphere->decimate(0.1F, 0.5F);

    EXPECT_LT(sphere->countFacets(), facets0);
    EXPECT_FALSE(sphere->hasNonManifolds());
    EXPECT_NEAR(sphere->getVolume(), volume0, 0.05 * volume0);
}

// NOLINTEND(cppcoreguidelines-*,readability-*)
