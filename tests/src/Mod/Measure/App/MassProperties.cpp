// SPDX-License-Identifier: LGPL-2.1-or-later

#include <src/App/InitApplication.h>
#include <App/Document.h>
#include <Mod/Measure/App/MassPropertiesResult.h>
#include <Mod/Part/App/PartFeature.h>
#include <gtest/gtest.h>
#include <BRepPrimAPI_MakeBox.hxx>

class MassProperties: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }

    void SetUp() override
    {
        document = App::GetApplication().newDocument("MassProperties");
    }

    void TearDown() override
    {
        App::GetApplication().closeDocument(document->getName());
    }

    App::Document* document {};
};

// NOLINTBEGIN

// Volume, surface area and centre of gravity of a 10x10x10 box are known
// analytically: V = 1000 mm^3, A = 600 mm^2, COG = (5, 5, 5).
TEST_F(MassProperties, testBox)
{
    TopoDS_Shape shape = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Solid();
    auto feature = document->addObject<Part::Feature>("Box");
    feature->Shape.setValue(shape);
    document->recompute();

    MassPropertiesInput input;
    input.object = feature;
    input.shape = shape;
    input.placement = Base::Placement();

    MassPropertiesData data = CalculateMassProperties(
        {input},
        MassPropertiesMode::CenterOfGravity,
        nullptr,
        nullptr);

    EXPECT_NEAR(data.volume.getValue(), 1000.0, 1e-3);
    EXPECT_NEAR(data.surfaceArea.getValue(), 600.0, 1e-3);
    EXPECT_NEAR(data.cog.x, 5.0, 1e-6);
    EXPECT_NEAR(data.cog.y, 5.0, 1e-6);
    EXPECT_NEAR(data.cog.z, 5.0, 1e-6);
}

// NOLINTEND
