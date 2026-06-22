// SPDX-License-Identifier: LGPL-2.1-or-later

#include <src/App/InitApplication.h>
#include <App/Document.h>
#include <Mod/Measure/App/MeasureAngle.h>
#include <Mod/Measure/App/MeasureArea.h>
#include <Mod/Measure/App/MeasureDiameter.h>
#include <Mod/Measure/App/MeasureLength.h>
#include <Mod/Measure/App/MeasurePosition.h>
#include <Mod/Measure/App/MeasureRadius.h>
#include <Mod/Part/App/PartFeature.h>
#include <gtest/gtest.h>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>

class MeasureTypes: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }

    void SetUp() override
    {
        document = App::GetApplication().newDocument("MeasureTypes");
    }

    void TearDown() override
    {
        App::GetApplication().closeDocument(document->getName());
    }

    Part::Feature* addBox(const char* name = "Box")
    {
        auto box = document->addObject<Part::Feature>(name);
        box->Shape.setValue(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Solid());
        return box;
    }

    Part::Feature* addCylinder(const char* name = "Cylinder")
    {
        auto cyl = document->addObject<Part::Feature>(name);
        cyl->Shape.setValue(BRepPrimAPI_MakeCylinder(3.0, 20.0).Solid());
        return cyl;
    }

    App::Document* document {};
};

// NOLINTBEGIN

// A 10x10x10 box: any face has area 100 regardless of OCCT face ordering.
TEST_F(MeasureTypes, testArea)
{
    auto box = addBox();
    document->recompute();

    auto measure = document->addObject<Measure::MeasureArea>("Area");
    measure->Elements.setValue(box, std::vector<std::string> {"Face1"});
    document->recompute();

    EXPECT_NEAR(measure->Area.getValue(), 100.0, 1e-6);
}

// A 10x10x10 box: any edge has length 10 regardless of OCCT edge ordering.
TEST_F(MeasureTypes, testLength)
{
    auto box = addBox();
    document->recompute();

    auto measure = document->addObject<Measure::MeasureLength>("Length");
    measure->Elements.setValue(box, std::vector<std::string> {"Edge1"});
    document->recompute();

    EXPECT_NEAR(measure->Length.getValue(), 10.0, 1e-6);
}

// The cylindrical face of a r=3 cylinder reports radius 3 and diameter 6.
TEST_F(MeasureTypes, testRadius)
{
    auto cyl = addCylinder();
    document->recompute();

    auto measure = document->addObject<Measure::MeasureRadius>("Radius");
    measure->Element.setValue(cyl, {"Face1"});
    document->recompute();

    EXPECT_NEAR(measure->Radius.getValue(), 3.0, 1e-6);
}

TEST_F(MeasureTypes, testDiameter)
{
    auto cyl = addCylinder();
    document->recompute();

    auto measure = document->addObject<Measure::MeasureDiameter>("Diameter");
    measure->Element.setValue(cyl, {"Face1"});
    document->recompute();

    EXPECT_NEAR(measure->Diameter.getValue(), 6.0, 1e-6);
}

// Two adjacent faces of a box meet at a right angle.
TEST_F(MeasureTypes, testAngle)
{
    auto box = addBox();
    document->recompute();

    auto measure = document->addObject<Measure::MeasureAngle>("Angle");
    measure->Element1.setValue(box, {"Face1"});
    measure->Element2.setValue(box, {"Face3"});
    document->recompute();

    EXPECT_NEAR(measure->Angle.getValue(), 90.0, 1e-6);
}

// A box vertex sits at one of the eight corners; every coordinate is 0 or 10.
TEST_F(MeasureTypes, testPosition)
{
    auto box = addBox();
    document->recompute();

    auto measure = document->addObject<Measure::MeasurePosition>("Position");
    measure->Element.setValue(box, {"Vertex1"});
    document->recompute();

    Base::Vector3d pos = measure->Position.getValue();
    for (double coord : {pos.x, pos.y, pos.z}) {
        const bool isCorner = std::abs(coord) < 1e-6 || std::abs(coord - 10.0) < 1e-6;
        EXPECT_TRUE(isCorner) << "coordinate " << coord << " is not a box corner";
    }
}

// NOLINTEND
