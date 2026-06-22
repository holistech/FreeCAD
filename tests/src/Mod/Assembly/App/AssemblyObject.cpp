// SPDX-License-Identifier: LGPL-2.1-or-later

#include <gtest/gtest.h>

#include <FCConfig.h>

#include <App/Application.h>
#include <App/Document.h>
#include <App/Expression.h>
#include <App/ObjectIdentifier.h>
#include <Mod/Assembly/App/AssemblyObject.h>
#include <Mod/Assembly/App/JointGroup.h>
#include <src/App/InitApplication.h>

class AssemblyObjectTest: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }

    void SetUp() override
    {
        _docName = App::GetApplication().getUniqueDocumentName("test");
        auto _doc = App::GetApplication().newDocument(_docName.c_str(), "testUser");
        _assemblyObj = _doc->addObject<Assembly::AssemblyObject>();
        _jointGroupObj = _assemblyObj->addObject<Assembly::JointGroup>("jointGroupTest");
    }

    void TearDown() override
    {
        App::GetApplication().closeDocument(_docName.c_str());
    }

    Assembly::AssemblyObject* getObject()
    {
        return _assemblyObj;
    }

private:
    // TODO: use shared_ptr or something else here?
    Assembly::AssemblyObject* _assemblyObj;
    Assembly::JointGroup* _jointGroupObj;
    std::string _docName;
};

TEST_F(AssemblyObjectTest, createAssemblyObject)  // NOLINT
{
    // The bare fixture has an assembly with an (empty) joint group and no parts.
    Assembly::AssemblyObject* assembly = getObject();
    ASSERT_NE(assembly, nullptr);
    EXPECT_NE(assembly->getJointGroup(), nullptr);
}

TEST_F(AssemblyObjectTest, emptyAssemblySolvesTriviallyWithZeroDof)  // NOLINT
{
    // An assembly with no parts and no joints has nothing to solve: the solver
    // succeeds (status 0) and reports zero remaining degrees of freedom. These
    // C++ getters (DoF / solver status) are not exposed to the Python API, so
    // this can only be checked here.
    Assembly::AssemblyObject* assembly = getObject();
    int result = assembly->solve();
    EXPECT_EQ(result, 0);
    EXPECT_EQ(assembly->getLastDoF(), 0);
    EXPECT_EQ(assembly->getLastSolverStatus(), 0);
    EXPECT_FALSE(assembly->getLastHasConflicts());
    EXPECT_FALSE(assembly->getLastHasRedundancies());
}
