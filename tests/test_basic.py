"""
Basic tests for Tennis Discovery Agent components.

These tests are meant to verify that the core components are properly set up.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_environment_variables():
    """Test that required environment variables are set."""
    required_vars = [
        "GEMINI_API_KEY",
        "DISCORD_BOT_TOKEN",
        "GITHUB_TOKEN",
        "GITHUB_REPO"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return False
    else:
        print("✅ All required environment variables are set")
        return True


def test_imports():
    """Test that all modules can be imported."""
    try:
        from src.models.session import PracticeSession
        from src.ai.gemini_client import GeminiClient
        from src.storage.markdown_builder import MarkdownBuilder
        from src.storage.github_sync import GitHubSync
        from src.bot.client import TennisDiscoveryBot

        print("✅ All modules can be imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_data_model():
    """Test that data models work correctly."""
    try:
        from src.models.session import PracticeSession, SuccessPattern, NextAction

        # Create a test session
        session = PracticeSession(
            tags=["serve", "test"],
            condition="good",
            somatic_marker="Test marker",
            success_patterns=[
                SuccessPattern(
                    description="Test success",
                    context="Test context"
                )
            ],
            next_actions=[
                NextAction(
                    theme="Test theme",
                    focus_point="Test focus"
                )
            ]
        )

        assert session.condition == "good"
        assert len(session.success_patterns) == 1
        print("✅ Data models work correctly")
        return True
    except Exception as e:
        print(f"❌ Data model error: {e}")
        return False


def test_markdown_generation():
    """Test markdown generation."""
    try:
        from src.models.session import PracticeSession, SuccessPattern
        from src.storage.markdown_builder import MarkdownBuilder

        session = PracticeSession(
            tags=["serve"],
            condition="good",
            somatic_marker="小指を締める感覚",
            success_patterns=[
                SuccessPattern(
                    description="トスの精度が向上",
                    context="脱力を意識した時"
                )
            ]
        )

        builder = MarkdownBuilder()
        markdown = builder.build(session)

        assert "---" in markdown  # Frontmatter
        assert "小指を締める感覚" in markdown
        assert "トスの精度が向上" in markdown

        print("✅ Markdown generation works correctly")
        return True
    except Exception as e:
        print(f"❌ Markdown generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_github_connection():
    """Test GitHub connection (requires valid token)."""
    try:
        from src.storage.github_sync import GitHubSync

        sync = GitHubSync()
        result = sync.check_connection()

        if result:
            print("✅ GitHub connection successful")
            return True
        else:
            print("⚠️ GitHub connection failed (check token and repo name)")
            return False
    except Exception as e:
        print(f"❌ GitHub connection error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Running Basic Tests")
    print("=" * 60)
    print()

    tests = [
        ("Environment Variables", test_environment_variables),
        ("Module Imports", test_imports),
        ("Data Models", test_data_model),
        ("Markdown Generation", test_markdown_generation),
        ("GitHub Connection", test_github_connection),
    ]

    results = []
    for name, test_func in tests:
        print(f"\n📝 Testing: {name}")
        print("-" * 60)
        result = test_func()
        results.append((name, result))
        print()

    print("=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
