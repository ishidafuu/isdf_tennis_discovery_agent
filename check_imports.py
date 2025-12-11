"""
Check if new modules can be imported correctly.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 インポートチェック開始\n")

# Test 1: SummaryGenerator
print("1️⃣ SummaryGenerator のインポート...")
try:
    from src.storage.summary_generator import SummaryGenerator
    print("   ✅ src.storage.summary_generator.SummaryGenerator")
except Exception as e:
    print(f"   ❌ エラー: {e}")

# Test 2: SummaryPrompts
print("\n2️⃣ SummaryPrompts のインポート...")
try:
    from src.ai.summary_prompts import SummaryPrompts
    print("   ✅ src.ai.summary_prompts.SummaryPrompts")
except Exception as e:
    print(f"   ❌ エラー: {e}")

# Test 3: Check methods exist
print("\n3️⃣ メソッドの確認...")
try:
    # SummaryGenerator methods
    methods = [
        'generate_all_summaries',
        'generate_summary_overview',
        'generate_summary_period',
        'generate_summary_technique',
        'collect_memos_for_summary'
    ]
    for method in methods:
        if hasattr(SummaryGenerator, method):
            print(f"   ✅ SummaryGenerator.{method}")
        else:
            print(f"   ❌ SummaryGenerator.{method} が存在しません")

    # SummaryPrompts methods
    prompt_methods = [
        'generate_overview_prompt',
        'generate_technique_prompt',
        'generate_period_prompt'
    ]
    for method in prompt_methods:
        if hasattr(SummaryPrompts, method):
            print(f"   ✅ SummaryPrompts.{method}")
        else:
            print(f"   ❌ SummaryPrompts.{method} が存在しません")

except Exception as e:
    print(f"   ❌ エラー: {e}")

# Test 4: SchedulerManager
print("\n4️⃣ SchedulerManager の更新確認...")
try:
    from src.scheduler.scheduler_manager import SchedulerManager

    # Check if new method exists
    if hasattr(SchedulerManager, '_check_and_generate_summaries'):
        print("   ✅ SchedulerManager._check_and_generate_summaries")
    else:
        print("   ❌ SchedulerManager._check_and_generate_summaries が存在しません")

    if hasattr(SchedulerManager, 'trigger_summary_generation_now'):
        print("   ✅ SchedulerManager.trigger_summary_generation_now")
    else:
        print("   ❌ SchedulerManager.trigger_summary_generation_now が存在しません")

except Exception as e:
    print(f"   ❌ エラー: {e}")

print("\n✅ インポートチェック完了")
