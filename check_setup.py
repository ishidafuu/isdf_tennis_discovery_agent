#!/usr/bin/env python3
"""
Setup checker for Tennis Discovery Agent.
Verifies that all required environment variables and dependencies are configured.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_env_var(var_name: str, description: str) -> bool:
    """Check if environment variable is set."""
    value = os.getenv(var_name)
    if value:
        # Mask sensitive data
        if "TOKEN" in var_name or "KEY" in var_name:
            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            print(f"  ✅ {var_name}: {masked}")
        else:
            print(f"  ✅ {var_name}: {value}")
        return True
    else:
        print(f"  ❌ {var_name}: NOT SET")
        print(f"     → {description}")
        return False


def check_imports() -> bool:
    """Check if required packages are installed."""
    required_packages = [
        ("discord", "Discord.py"),
        ("google.generativeai", "Google Generative AI"),
        ("github", "PyGithub"),
        ("pydantic", "Pydantic"),
        ("dotenv", "Python-dotenv"),
        ("yaml", "PyYAML"),
    ]

    all_ok = True
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - Run: pip install -r requirements.txt")
            all_ok = False

    return all_ok


def check_github_repo() -> bool:
    """Check if GitHub repository is accessible."""
    try:
        from src.storage.github_sync import GitHubSync

        sync = GitHubSync()
        result = sync.check_connection()
        return result
    except Exception as e:
        print(f"  ❌ GitHub connection failed: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 70)
    print("🎾 Tennis Discovery Agent - Setup Checker")
    print("=" * 70)
    print()

    # Check .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Run: cp .env.example .env")
        print("   Then edit .env and add your API keys")
        return 1

    print("✅ .env file found")
    print()

    # Check environment variables
    print("📋 Checking Environment Variables...")
    print("-" * 70)

    env_checks = [
        ("DISCORD_BOT_TOKEN", "Discord Bot Token from https://discord.com/developers/applications"),
        ("GEMINI_API_KEY", "Gemini API Key from https://aistudio.google.com/app/apikey"),
        ("GITHUB_TOKEN", "GitHub Personal Access Token from https://github.com/settings/tokens"),
        ("GITHUB_REPO", "GitHub Repository (format: username/repo-name)"),
    ]

    env_ok = all(check_env_var(var, desc) for var, desc in env_checks)
    print()

    # Check optional variables
    obsidian_path = os.getenv("OBSIDIAN_PATH", "sessions")
    debug = os.getenv("DEBUG", "false")
    print(f"  ℹ️  OBSIDIAN_PATH: {obsidian_path} (optional, using default)")
    print(f"  ℹ️  DEBUG: {debug}")
    print()

    # Check Python packages
    print("📦 Checking Python Packages...")
    print("-" * 70)
    packages_ok = check_imports()
    print()

    # Check GitHub connection
    if env_ok:
        print("🔗 Checking GitHub Connection...")
        print("-" * 70)
        github_ok = check_github_repo()
        print()
    else:
        print("⏭️  Skipping GitHub check (environment variables not set)")
        github_ok = False
        print()

    # Summary
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)

    checks = [
        ("Environment Variables", env_ok),
        ("Python Packages", packages_ok),
        ("GitHub Connection", github_ok if env_ok else None),
    ]

    all_passed = True
    for name, result in checks:
        if result is None:
            print(f"  ⏭️  {name}: SKIPPED")
        elif result:
            print(f"  ✅ {name}: OK")
        else:
            print(f"  ❌ {name}: FAILED")
            all_passed = False

    print()

    if all_passed:
        print("🎉 All checks passed! You're ready to run the bot.")
        print()
        print("Next steps:")
        print("  1. Create and invite Discord Bot: see docs/DISCORD_SETUP.md")
        print("  2. Run the bot: python main.py")
        print("  3. Send a voice message in Discord!")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Setup guides:")
        print("  - Discord Bot: docs/DISCORD_SETUP.md")
        print("  - Full setup: SETUP.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
