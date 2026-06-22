// SPDX-License-Identifier: LGPL-2.1-or-later

#include <gtest/gtest.h>

#include <string>
#include <vector>

#include <src/App/InitApplication.h>

#include <Gui/Command.h>

namespace
{

// A minimal concrete command. Gui::Command is abstract; the manager only needs
// the name/group/module accessors and never executes the command in these
// tests, so the overridden hooks are intentionally empty.
class TestCommand: public Gui::Command
{
public:
    explicit TestCommand(const char* name)
        : Gui::Command(name)
    {}

    const char* className() const override
    {
        return "TestCommand";
    }

protected:
    void activated(int) override
    {}
    void languageChange() override
    {}
    void updateAction(int) override
    {}
};

class CommandManagerTest: public ::testing::Test
{
protected:
    static void SetUpTestSuite()
    {
        tests::initApplication();
    }
};

// NOLINTBEGIN

TEST_F(CommandManagerTest, addAndLookupCommand)
{
    Gui::CommandManager manager;
    manager.addCommand(new TestCommand("Test_Lookup"));

    Gui::Command* found = manager.getCommandByName("Test_Lookup");
    ASSERT_NE(found, nullptr);
    EXPECT_STREQ(found->getName(), "Test_Lookup");
    EXPECT_EQ(manager.getCommandByName("Test_DoesNotExist"), nullptr);
}

TEST_F(CommandManagerTest, getAllCommandsAndMap)
{
    Gui::CommandManager manager;
    manager.addCommand(new TestCommand("Test_A"));
    manager.addCommand(new TestCommand("Test_B"));

    EXPECT_EQ(manager.getAllCommands().size(), 2U);
    EXPECT_EQ(manager.getCommands().size(), 2U);
    EXPECT_EQ(manager.getCommands().count("Test_A"), 1U);
    EXPECT_EQ(manager.getCommands().count("Test_B"), 1U);
}

TEST_F(CommandManagerTest, revisionTracksAddAndRemove)
{
    Gui::CommandManager manager;
    const int start = manager.getRevision();

    auto* command = new TestCommand("Test_Revision");
    manager.addCommand(command);
    EXPECT_EQ(manager.getRevision(), start + 1);

    manager.removeCommand(command);  // deletes the command
    EXPECT_EQ(manager.getRevision(), start + 2);
    EXPECT_EQ(manager.getCommandByName("Test_Revision"), nullptr);
}

TEST_F(CommandManagerTest, duplicateNameIsIgnored)
{
    Gui::CommandManager manager;
    auto* command = new TestCommand("Test_Duplicate");
    manager.addCommand(command);
    const int afterFirst = manager.getRevision();

    // Adding the same command again is a no-op (no second slot, no revision bump).
    manager.addCommand(command);
    EXPECT_EQ(manager.getAllCommands().size(), 1U);
    EXPECT_EQ(manager.getRevision(), afterFirst);
}

TEST_F(CommandManagerTest, filterByModuleAndGroup)
{
    Gui::CommandManager manager;
    auto* inModule = new TestCommand("Test_InModule");
    inModule->setAppModuleName("TestModule");
    inModule->setGroupName("TestGroup");
    manager.addCommand(inModule);

    auto* other = new TestCommand("Test_Other");
    other->setAppModuleName("OtherModule");
    other->setGroupName("OtherGroup");
    manager.addCommand(other);

    std::vector<Gui::Command*> moduleCommands = manager.getModuleCommands("TestModule");
    ASSERT_EQ(moduleCommands.size(), 1U);
    EXPECT_STREQ(moduleCommands.front()->getName(), "Test_InModule");

    std::vector<Gui::Command*> groupCommands = manager.getGroupCommands("TestGroup");
    ASSERT_EQ(groupCommands.size(), 1U);
    EXPECT_STREQ(groupCommands.front()->getName(), "Test_InModule");
}

TEST_F(CommandManagerTest, removeCommandDropsIt)
{
    Gui::CommandManager manager;
    auto* command = new TestCommand("Test_Remove");
    manager.addCommand(command);
    ASSERT_NE(manager.getCommandByName("Test_Remove"), nullptr);

    manager.removeCommand(command);
    EXPECT_EQ(manager.getCommandByName("Test_Remove"), nullptr);
    EXPECT_TRUE(manager.getAllCommands().empty());
}

// NOTE: CommandManager::checkAcceleratorForConflicts is intentionally not
// covered here. Despite being a non-static member, it ignores *this and queries
// the global Gui::Application::Instance->commandManager(), so it cannot be
// exercised against a standalone manager without bringing up a full
// Gui::Application — out of scope for an offscreen unit test.

// NOLINTEND

}  // namespace
