# Discord Bot 実装

## main.py

```python
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# Bot設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)

# モジュールのインポート
from src.bot.channel_handler import handle_voice_message
from src.bot.action_buttons import create_action_buttons
from src.bot.scheduler import start_scheduler

@bot.event
async def on_ready():
    """Bot起動時の処理"""
    print(f'{bot.user} has connected to Discord!')
    start_scheduler()  # スケジューラー起動

    # 未処理DMをチェック（Bot停止時の対応）
    await process_pending_dms()

async def process_pending_dms():
    """Bot停止中に送られたDMの音声メッセージを処理"""
    try:
        admin_user_id = int(os.getenv('ADMIN_USER_ID'))
        admin_user = await bot.fetch_user(admin_user_id)
        dm_channel = await admin_user.create_dm()

        pending_count = 0
        async for message in dm_channel.history(limit=50):
            # 処理済み（✅）をスキップ
            if any(r.emoji == '✅' for r in message.reactions):
                continue

            # 音声メッセージを処理
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('audio/'):
                        scene = extract_scene_from_text(message.content)
                        await handle_voice_message(message, attachment, scene)
                        await message.add_reaction('✅')
                        pending_count += 1

        if pending_count > 0:
            await dm_channel.send(f"Bot復旧後、未処理メモを {pending_count} 件処理しました ✅")
    except Exception as e:
        print(f"DM処理エラー: {e}")

def extract_scene_from_text(text: str) -> str:
    """テキストからシーンを抽出"""
    scene_keywords = {
        "壁打ち": "壁打ち",
        "スクール": "スクール",
        "試合": "試合",
    }
    for keyword, scene in scene_keywords.items():
        if keyword in text:
            return scene
    return "壁打ち"  # デフォルト

@bot.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return

    # コマンド処理
    if message.content.startswith('!'):
        await bot.process_commands(message)
        return

    # シーン判定
    scene = detect_scene_from_channel(message.channel.name)
    if not scene:
        return  # シーンチャンネル以外は無視

    # 添付ファイルの処理
    if message.attachments:
        for attachment in message.attachments:
            content_type = attachment.content_type or ""

            # 音声メッセージ
            if content_type.startswith('audio/'):
                await handle_voice_message(message, attachment, scene)
                return

            # 画像
            elif content_type.startswith('image/'):
                await handle_image_message(message, attachment, scene)
                return

            # 動画
            elif content_type.startswith('video/'):
                await handle_video_message(message, attachment, scene)
                return

    # テキストメッセージ
    if message.content:
        await handle_text_message(message, scene)
        return

    # コマンドの処理
    await bot.process_commands(message)

# Bot起動
if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
```

---

## channel_handler.py

```python
import discord
from src.ai.transcription import transcribe_audio
from src.ai.structured_extraction import extract_structured_data
from src.storage.obsidian_manager import ObsidianManager
from src.storage.markdown_templates import generate_markdown
from src.bot.action_buttons import create_action_buttons

def detect_scene_from_channel(channel_name: str) -> str:
    """チャンネル名からシーンを判定"""
    scene_mapping = {
        "壁打ち": "壁打ち",
        "スクール": "スクール",
        "試合": "試合",
        "フリー練習": "フリー練習",
        "振り返り": "振り返り",
        "質問": "質問",
        "分析": "分析"
    }
    return scene_mapping.get(channel_name, None)

async def handle_voice_message(message: discord.Message, attachment: discord.Attachment, scene: str):
    """音声メッセージの処理"""

    try:
        await message.add_reaction('⏳')

        # 1. 音声を文字起こし
        audio_url = attachment.url
        transcribed_text = await transcribe_audio(audio_url)

        if not transcribed_text:
            await message.add_reaction('❌')
            await message.channel.send("文字起こしに失敗しました")
            return

        # 2. 構造化データを抽出
        structured_data = await extract_structured_data(transcribed_text, scene)

        # 3. ボタンを表示
        view = create_action_buttons(transcribed_text, scene, structured_data)

        await message.remove_reaction('⏳', message.guild.me)
        await message.channel.send(
            f"**文字起こし完了:**\n```{transcribed_text}```\n\nどのように処理しますか？",
            view=view
        )

    except Exception as e:
        await message.add_reaction('❌')
        await message.channel.send(f"エラーが発生しました: {str(e)}")
        print(f"Voice message processing error: {e}")

async def handle_text_message(message: discord.Message, scene: str):
    """テキストメッセージの処理"""

    try:
        await message.add_reaction('⏳')

        # URLの抽出
        import re
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message.content)

        # Geminiで構造化
        from src.ai.structured_extraction import structure_text_memo
        memo_data = await structure_text_memo(
            text=message.content,
            scene_type=scene,
            urls=urls
        )

        # メタデータ追加
        memo_data['timestamp'] = message.created_at
        memo_data['input_type'] = 'text'
        memo_data['urls'] = urls

        # Obsidianに保存
        obsidian = ObsidianManager(os.getenv('OBSIDIAN_VAULT_PATH'))
        file_path = await obsidian.save_memo(memo_data, scene)

        # GitHub Push
        from src.storage.git_manager import push_changes
        await push_changes(f"Add text memo: {scene}")

        # 完了通知
        await message.remove_reaction('⏳', message.guild.me)
        await message.add_reaction('✅')
        await message.reply(f"テキストメモを保存しました ✅")

    except Exception as e:
        await message.add_reaction('❌')
        await message.reply(f"エラーが発生しました: {str(e)}")

async def handle_image_message(message: discord.Message, attachment: discord.Attachment, scene: str):
    """画像メッセージの処理（解析なし）"""

    try:
        await message.add_reaction('⏳')

        # ファイルサイズチェック
        if attachment.size > 20 * 1024 * 1024:  # 20MB
            await message.reply("ファイルサイズが大きすぎます（上限20MB）")
            return

        # 画像をダウンロード・保存
        image_data = await attachment.read()

        from datetime import datetime
        from pathlib import Path
        import os

        date_str = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%H%M%S')
        ext = os.path.splitext(attachment.filename)[1]
        filename = f"{date_str}_{scene}_{timestamp}{ext}"

        vault_path = os.getenv('OBSIDIAN_VAULT_PATH')
        attachments_dir = Path(vault_path) / "attachments" / date_str
        attachments_dir.mkdir(parents=True, exist_ok=True)

        file_path = attachments_dir / filename
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # メモデータ作成
        memo_data = {
            'timestamp': message.created_at,
            'input_type': 'image',
            'file_path': f"attachments/{date_str}/{filename}",
            'user_comment': message.content if message.content else "",
            'scene': scene,
        }

        # Obsidianに保存
        from src.storage.obsidian_manager import save_media_memo
        saved_path = await save_media_memo(memo_data, scene, 'image')

        # 完了通知
        await message.remove_reaction('⏳', message.guild.me)
        await message.add_reaction('✅')
        await message.reply(f"画像メモを保存しました ✅")

    except Exception as e:
        await message.add_reaction('❌')
        await message.reply(f"エラーが発生しました: {str(e)}")

async def handle_video_message(message: discord.Message, attachment: discord.Attachment, scene: str):
    """動画メッセージの処理（解析なし）"""

    try:
        await message.add_reaction('⏳')

        # ファイルサイズチェック
        if attachment.size > 20 * 1024 * 1024:  # 20MB
            await message.reply(
                f"動画サイズが大きすぎます（上限20MB）\n"
                f"現在のサイズ: {attachment.size / 1024 / 1024:.1f}MB"
            )
            return

        # 動画をダウンロード・保存
        video_data = await attachment.read()

        from datetime import datetime
        from pathlib import Path
        import os

        date_str = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%H%M%S')
        ext = os.path.splitext(attachment.filename)[1]
        filename = f"{date_str}_{scene}_{timestamp}{ext}"

        vault_path = os.getenv('OBSIDIAN_VAULT_PATH')
        attachments_dir = Path(vault_path) / "attachments" / date_str
        attachments_dir.mkdir(parents=True, exist_ok=True)

        file_path = attachments_dir / filename
        with open(file_path, 'wb') as f:
            f.write(video_data)

        # メモデータ作成
        memo_data = {
            'timestamp': message.created_at,
            'input_type': 'video',
            'file_path': f"attachments/{date_str}/{filename}",
            'user_comment': message.content if message.content else "",
            'scene': scene,
        }

        # Obsidianに保存
        from src.storage.obsidian_manager import save_media_memo
        saved_path = await save_media_memo(memo_data, scene, 'video')

        # 完了通知
        await message.remove_reaction('⏳', message.guild.me)
        await message.add_reaction('✅')
        await message.reply(f"動画メモを保存しました ✅")

    except Exception as e:
        await message.add_reaction('❌')
        await message.reply(f"エラーが発生しました: {str(e)}")
```

---

## action_buttons.py

```python
import discord
from src.storage.obsidian_manager import ObsidianManager
from src.ai.question_generation import generate_follow_up_question
from src.analysis.comparison import compare_with_past

def create_action_buttons(text: str, scene_type: str, structured_data: dict) -> discord.ui.View:
    """アクションボタンを生成"""

    view = discord.ui.View(timeout=30)

    # 1. 深堀質問ボタン
    deep_dive_btn = discord.ui.Button(
        label="深堀質問",
        style=discord.ButtonStyle.secondary,
        emoji="🤔"
    )

    async def deep_dive_callback(interaction: discord.Interaction):
        question = await generate_follow_up_question(text, scene_type)
        await interaction.response.send_message(
            f"🤔 {question}\n\n回答を音声で送信してください（スキップ可能）"
        )

    deep_dive_btn.callback = deep_dive_callback

    # 2. 過去と比較ボタン
    compare_btn = discord.ui.Button(
        label="過去と比較",
        style=discord.ButtonStyle.secondary,
        emoji="📊"
    )

    async def compare_callback(interaction: discord.Interaction):
        comparison = await compare_with_past(text)
        await interaction.response.send_message(f"📊 過去のメモと比較:\n\n{comparison}")
        structured_data['comparison'] = comparison
        obsidian = ObsidianManager(os.getenv('OBSIDIAN_VAULT_PATH'))
        await obsidian.save_memo(structured_data, scene_type)

    compare_btn.callback = compare_callback

    # 3. 重要マークボタン
    important_btn = discord.ui.Button(
        label="重要マーク",
        style=discord.ButtonStyle.secondary,
        emoji="🔖"
    )

    async def important_callback(interaction: discord.Interaction):
        structured_data['important'] = True
        obsidian = ObsidianManager(os.getenv('OBSIDIAN_VAULT_PATH'))
        await obsidian.save_memo(structured_data, scene_type)
        await interaction.response.send_message("🔖 重要メモとして保存しました！")

    important_btn.callback = important_callback

    # 4. そのまま保存ボタン
    save_btn = discord.ui.Button(
        label="そのまま保存",
        style=discord.ButtonStyle.primary,
        emoji="💾"
    )

    async def save_callback(interaction: discord.Interaction):
        obsidian = ObsidianManager(os.getenv('OBSIDIAN_VAULT_PATH'))
        await obsidian.save_memo(structured_data, scene_type)
        await interaction.response.send_message("💾 保存しました！")

    save_btn.callback = save_callback

    # ボタンを追加
    view.add_item(deep_dive_btn)
    view.add_item(compare_btn)
    view.add_item(important_btn)
    view.add_item(save_btn)

    return view
```

---

## 次のドキュメント

- [ai-processing.md](ai-processing.md) - AI処理
