# Phase 1: 入力機能

## 概要

入力フェーズでは、ユーザーがどのように情報を記録するかを定義します。

**設計原則:**
- **Voice First**: 音声入力が基本
- **シンプルさ優先**: 複雑な操作は避ける
- **2つのフロー**: コート上（リアルタイム）と家で振り返り（後日）

---

## 入力手段の比較

| 入力方法 | 速度 | 場所制約 | 用途 |
|---------|------|---------|------|
| 音声 | 速い | あり | コート上の即座のメモ |
| テキスト | 中程度 | なし | 記事共有、詳細記録 |
| 画像 | 中程度 | なし | フォーム記録、図解保存 |
| 動画 | やや遅い | なし | スイング分析、試合記録 |

---

## チャンネル分けによるシーン区別

### Discordチャンネル構成

```
リアルタイム記録
├── #壁打ち
├── #スクール
├── #試合
└── #フリー練習
```

### チャンネルの役割

| チャンネル | 用途 | 抽出すべき情報 |
|-----------|------|---------------|
| **#壁打ち** | 基礎練習、反復ドリル | ドリル内容、時間、身体感覚 |
| **#スクール** | コーチの指導あり | コーチの指摘、新技術、課題 |
| **#試合** | 実戦、練習試合 | 対戦相手、スコア、戦術、メンタル |
| **#フリー練習** | 友人との自由練習 | 練習内容、気づき |

### 実装コード

```python
def detect_scene_from_channel(channel_name: str) -> str:
    """チャンネル名からシーンを判定"""
    scene_mapping = {
        "壁打ち": "壁打ち",
        "スクール": "スクール",
        "試合": "試合",
        "フリー練習": "フリー練習",
        "振り返り": "振り返り"
    }
    return scene_mapping.get(channel_name, "その他")
```

---

## 音声入力

### 基本フロー

```
1. ユーザーがチャンネルを選択（例: #スクール）

2. 音声メッセージを送信
   「今日はバックハンドのスライスを教わった。
    コーチが『もっと低い位置で』って言ってた」

3. Bot が受信・処理
   - 音声を文字起こし
   - チャンネル名を取得（scene: スクール）
   - 構造化データを抽出
   - Markdown生成・保存

4. Bot が応答
   「スクールでのメモを保存しました！」
```

### 実装コード

```python
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 音声メッセージの場合
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('audio/'):
                channel_name = message.channel.name
                scene_type = detect_scene_from_channel(channel_name)

                # 音声を文字起こし
                transcribed_text = await transcribe_audio(attachment.url)

                # 構造化データを抽出
                structured_data = await extract_structured_data(
                    text=transcribed_text,
                    scene_type=scene_type
                )

                # Markdown生成・保存
                await save_memo(structured_data, scene_type)

                await message.channel.send(f"✅ {scene_type}でのメモを保存しました！")
```

---

## テキスト入力

### ユースケース

- ネット記事・動画の共有
- 静かな場所での記録（電車、カフェなど）
- 構造化データの入力（試合スコア、練習メニュー）
- 後日の追記・補足

### URL付きメモ

**入力例:**
```
#スクール チャンネルで：
「このフォアハンドの記事が参考になった」
https://tennis-navi.jp/forehand-topspin-technique
```

### 実装コード

```python
import re

def extract_urls(text: str) -> list:
    """テキストからURLを抽出"""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)

async def handle_text_message(message, scene):
    """テキストメッセージの処理"""
    urls = extract_urls(message.content)

    memo_data = await structure_text_memo(
        text=message.content,
        scene_type=scene,
        urls=urls
    )

    memo_data['input_type'] = 'text'
    memo_data['urls'] = urls

    await save_memo(memo_data, scene)
    await message.reply("✅ テキストメモを保存しました！")
```

---

## 画像入力

### ユースケース

- フォームの写真記録
- コート図・戦術図の保存
- スコアボードの記録
- 参考資料（ホワイトボード、図解など）

### 基本フロー

```
1. 該当チャンネルで画像を添付
   [サーブフォームの写真を添付]
   「今日のサーブフォーム。トスの位置を記録。」

2. Bot が受信・処理
   - 画像をダウンロード
   - attachments/ フォルダに保存
   - ユーザーのコメントをそのまま記録
   - Markdownに埋め込み

3. Bot が応答
   「✅ 画像メモを保存しました！」
```

**重要:** 画像の自動解析は行いません。ユーザーのコメントのみ記録します。

### 実装コード

```python
async def handle_image_message(message, attachment, scene):
    """画像メッセージの処理（解析なし）"""

    # ファイルサイズチェック
    if attachment.size > 20 * 1024 * 1024:  # 20MB
        await message.reply("ファイルサイズが大きすぎます（上限20MB）")
        return

    # 画像をダウンロード・保存
    image_data = await attachment.read()
    date_str = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%H%M%S')
    ext = os.path.splitext(attachment.filename)[1]
    filename = f"{date_str}_{scene}_{timestamp}{ext}"

    save_path = Path(VAULT_PATH) / "attachments" / date_str
    save_path.mkdir(parents=True, exist_ok=True)

    with open(save_path / filename, 'wb') as f:
        f.write(image_data)

    # メモデータ作成
    memo_data = {
        'input_type': 'image',
        'file_path': f"attachments/{date_str}/{filename}",
        'user_comment': message.content if message.content else ""
    }

    await save_media_memo(memo_data, scene, 'image')
```

### 制限事項

- ファイルサイズ: 20MB以下
- 対応形式: JPG, PNG, GIF
- 画像解析: なし（ユーザーのコメントのみ記録）

---

## 動画入力

### ユースケース

- スイング動画の記録
- 試合動画の保存
- コーチの指導動画
- フォームチェック用

### 基本フロー

```
1. 該当チャンネルで動画を添付
   [フォアハンドのスロー動画]
   「今日のフォアハンド。回転量が増えた感じ。」

2. Bot が受信・処理
   - 動画をダウンロード
   - attachments/ フォルダに保存
   - ユーザーのコメントをそのまま記録
   - Markdownに埋め込み

3. Bot が応答
   「✅ 動画メモを保存しました！」
```

**重要:** 動画の自動解析は行いません。ユーザーのコメントのみ記録します。

### 制限事項

- ファイルサイズ: 20MB以下
- 対応形式: MP4, MOV
- 動画解析: なし（ユーザーのコメントのみ記録）

---

## #振り返りチャンネル（後日の追記）

### 目的

- Obsidianでメモを読み返した後、追記したい情報を追加
- 後から気づいたこと、補足情報を記録

### 基本フロー

```
1. ユーザーが Obsidian でメモを読み返す
   「1/15のサーブのメモ、そういえば...」

2. #振り返り チャンネルへ移動

3. 音声メッセージを送信
   「1/15のサーブメモに追記。
    実は、その前日にコーチがトスについてアドバイスしてた」

4. Bot が該当メモを特定
   - 日付「1/15」を検索
   - キーワード「サーブ」を検索
   - 候補が複数なら選択肢を提示

5. 追記セクションを追加
   元のMarkdownに追記を追加
```

### 日付検出のロジック

```python
import re
from datetime import datetime, timedelta

def extract_date_from_text(text: str):
    """テキストから日付を抽出"""

    # 「YYYY/MM/DD」「YYYY-MM-DD」形式
    pattern1 = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
    match = re.search(pattern1, text)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))

    # 「MM/DD」形式（今年と仮定）
    pattern2 = r'(\d{1,2})[/-](\d{1,2})'
    match = re.search(pattern2, text)
    if match:
        month, day = match.groups()
        return datetime(datetime.now().year, int(month), int(day))

    # 相対的な表現
    if '昨日' in text:
        return datetime.now() - timedelta(days=1)
    if '一昨日' in text:
        return datetime.now() - timedelta(days=2)

    # 「〇日前」形式
    pattern3 = r'(\d+)日前'
    match = re.search(pattern3, text)
    if match:
        days_ago = int(match.group(1))
        return datetime.now() - timedelta(days=days_ago)

    return None
```

### 追記の実装

```python
async def append_to_memo(original_memo, append_text):
    """既存のメモに追記セクションを追加"""

    markdown_path = original_memo['file_path']
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    append_section = f"""

> [!tip] 振り返り・追記（{datetime.now().strftime('%Y-%m-%d %H:%M')}）
> {append_text}
"""

    updated_content = content + append_section

    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    await git_commit_and_push(f"追記: {original_memo['date']}")
```

---

## Discord DM対応（Bot停止時のバックアップ）

### ユースケース

- 練習中にBotが停止していた
- Raspberry Piの電源が落ちていた
- ネットワーク障害でBotがオフライン

### 基本フロー

```
1. Bot停止中、自分のDMに音声を送信
   メッセージに「壁打ち」などシーン名を記載

2. Bot復旧後、自動的に未処理DMをチェック

3. 未処理の音声メッセージを検出

4. 通常通り処理してObsidianに保存

5. ✅リアクションで処理済みマーク

6. 完了通知をDMに送信
```

### 実装コード

```python
@bot.event
async def on_ready():
    """Bot起動時の処理"""
    print(f'Bot起動: {bot.user}')
    await process_pending_dms()

async def process_pending_dms():
    """Bot停止中に送られたDMの音声メッセージを処理"""

    admin_user_id = int(os.getenv('ADMIN_USER_ID'))
    admin_user = await bot.fetch_user(admin_user_id)
    dm_channel = await admin_user.create_dm()

    pending_count = 0

    async for message in dm_channel.history(limit=50):
        # 処理済み（✅リアクション）をスキップ
        if any(r.emoji == '✅' for r in message.reactions):
            continue

        # 音声メッセージを処理
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('audio/'):
                    scene = extract_scene_from_text(message.content)
                    await process_voice_with_scene(message, attachment, scene)
                    await message.add_reaction('✅')
                    pending_count += 1

    if pending_count > 0:
        await dm_channel.send(f"Bot復旧後、未処理メモを {pending_count} 件処理しました ✅")
```

### 設定

`.env`ファイルに自分のDiscord User IDを追加：

```env
ADMIN_USER_ID=123456789
```

**User IDの確認方法:**
1. Discord設定 → 詳細設定 → 開発者モード をON
2. 自分のアイコンを右クリック → IDをコピー

---

## 次のドキュメント

- [processing.md](processing.md) - 処理機能
- [output.md](output.md) - 出力機能
