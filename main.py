#!/usr/bin/env python3
"""
Tennis Discovery Agent - Main entry point

Usage:
    python main.py
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.bot.client import run_bot


def main():
    """Main entry point for the Tennis Discovery Agent."""
    print("=" * 60)
    print("🎾 Tennis Discovery Agent - Phase 1")
    print("=" * 60)
    print()
    print("Starting Discord bot...")
    print("Press Ctrl+C to stop")
    print()

    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
