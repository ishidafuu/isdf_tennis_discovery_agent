"""
Test script for summary generation feature.

Usage:
    python test_summary_generation.py
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.obsidian_manager import ObsidianManager
from src.ai.gemini_client import GeminiClient
from src.storage.github_sync import GitHubSync
from src.storage.summary_generator import SummaryGenerator


async def test_summary_generation():
    """Test summary page generation."""
    print("🧪 まとめページ生成機能のテスト開始\n")

    # Initialize components
    print("1️⃣ コンポーネントの初期化...")
    obsidian_manager = ObsidianManager()
    gemini_client = GeminiClient()
    github_sync = GitHubSync()

    print(f"   Obsidian Vault: {obsidian_manager.vault_path}")
    print(f"   ✅ 初期化完了\n")

    # Create summary generator
    print("2️⃣ SummaryGenerator作成...")
    summary_generator = SummaryGenerator(
        obsidian_manager,
        gemini_client,
        github_sync
    )
    print("   ✅ 作成完了\n")

    # Test data collection
    print("3️⃣ データ収集テスト...")
    try:
        data = summary_generator.collect_memos_for_summary(period="recent")
        print(f"   メモ件数: {len(data['memos'])}")
        print(f"   気づき件数: {len(data['insights'])}")
        print(f"   反省点件数: {len(data['reflections'])}")
        print(f"   タグ種類: {len(data['tags'])}")
        print(f"   期間: {data['date_range']['start']} 〜 {data['date_range']['end']}")
        print("   ✅ データ収集成功\n")
    except Exception as e:
        print(f"   ❌ データ収集エラー: {e}\n")
        return

    # Test AI prompt generation
    print("4️⃣ AIプロンプト生成テスト...")
    try:
        from src.ai.summary_prompts import SummaryPrompts

        overview_prompt = SummaryPrompts.generate_overview_prompt(data)
        print(f"   総合まとめプロンプト長: {len(overview_prompt)} 文字")

        technique_prompt = SummaryPrompts.generate_technique_prompt(data, "フォアハンド")
        print(f"   技術別プロンプト長: {len(technique_prompt)} 文字")

        period_prompt = SummaryPrompts.generate_period_prompt(data, "recent")
        print(f"   期間別プロンプト長: {len(period_prompt)} 文字")

        print("   ✅ プロンプト生成成功\n")
    except Exception as e:
        print(f"   ❌ プロンプト生成エラー: {e}\n")
        return

    # Test summary generation (with user confirmation)
    print("5️⃣ まとめページ生成テスト")
    print("   ⚠️  実際にGemini APIを呼び出します。")
    print("   ⚠️  6種類のまとめページを生成し、GitHub pushします。")
    user_input = input("   実行しますか? (yes/no): ")

    if user_input.lower() != 'yes':
        print("   ⏭️  スキップしました\n")
        print("✅ テスト完了（まとめページ生成はスキップ）")
        return

    print("\n   まとめページを生成中...\n")
    try:
        success = await summary_generator.generate_all_summaries()

        if success:
            print("\n   ✅ まとめページ生成成功！\n")
            print("   生成されたファイル:")
            vault_path = Path(obsidian_manager.vault_path)
            for filename in [
                "まとめ_総合.md",
                "まとめ_最近.md",
                "まとめ_1ヶ月.md",
                "まとめ_フォアハンド.md",
                "まとめ_バックハンド.md",
                "まとめ_サーブ.md"
            ]:
                file_path = vault_path / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"   ✅ {filename} ({size} bytes)")
                else:
                    print(f"   ⚠️  {filename} (未生成)")
        else:
            print("\n   ❌ まとめページ生成失敗\n")

    except Exception as e:
        print(f"\n   ❌ エラー: {e}\n")
        import traceback
        traceback.print_exc()
        return

    print("\n✅ テスト完了")


if __name__ == "__main__":
    asyncio.run(test_summary_generation())
