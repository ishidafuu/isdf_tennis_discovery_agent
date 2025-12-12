# Obsidianストレージ管理

## obsidian_manager.py

```python
import os
import yaml
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class ObsidianManager:
    """ObsidianのMarkdownファイルを読み書き・検索"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)

    async def save_memo(self, memo_data: dict, scene_type: str) -> str:
        """メモをObsidianに保存

        同日・同シーンの2回目以降は既存ファイルに追記する
        """

        # 1. UUIDを生成
        memo_id = str(uuid.uuid4())
        memo_data['id'] = memo_id

        # 2. ファイルパスを決定
        markdown_path = f"daily/{memo_data['date']}-{scene_type}.md"
        full_path = self.vault_path / markdown_path

        # 3. ディレクトリ作成
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 4. 既存ファイルの有無をチェック
        if full_path.exists():
            # 同日・同シーンの2回目以降 → 追記モード
            append_content = self._generate_append_section(memo_data, scene_type)
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write(append_content)
        else:
            # 新規作成
            markdown_content = self._generate_markdown(memo_data, scene_type)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

        return memo_id

    def _generate_append_section(self, memo_data: dict, scene_type: str) -> str:
        """同日2回目以降の追記セクションを生成"""
        timestamp = memo_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M'))

        append_section = f"""

---

## 追加メモ（{timestamp}）

{memo_data.get('raw_text', '')}

"""
        if memo_data.get('improvement'):
            append_section += f"**改善した点:** {memo_data['improvement']}\n\n"
        if memo_data.get('issue'):
            append_section += f"**課題:** {memo_data['issue']}\n\n"
        if memo_data.get('next_action'):
            append_section += f"**次回やること:** {memo_data['next_action']}\n"

        return append_section

    def _generate_markdown(self, memo_data: dict, scene_type: str) -> str:
        """Markdownコンテンツを生成"""
        from src.storage.markdown_templates import generate_markdown
        return generate_markdown(memo_data, scene_type)

    def read_memo(self, markdown_path: str) -> Optional[Dict]:
        """Markdownファイルから完全なメモを読み込む"""
        full_path = self.vault_path / markdown_path

        if not full_path.exists():
            return None

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # FrontmatterとBodyを分離
        frontmatter, body = self._parse_markdown(content)

        return {
            "frontmatter": frontmatter,
            "body": body,
            "full_content": content,
            "path": markdown_path
        }

    def _parse_markdown(self, content: str) -> tuple:
        """Markdownからfrontmatterと本文を抽出"""
        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError:
            frontmatter = {}

        body = parts[2].strip()

        return frontmatter, body

    async def search_by_date_and_scene(
        self,
        scene: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """日付とシーンでメモを検索"""
        results = []

        for markdown_file in sorted(self.vault_path.glob("daily/*.md"), reverse=True):
            # ファイル名から情報を抽出（例: 2025-01-27-壁打ち.md）
            filename = markdown_file.stem
            parts = filename.rsplit('-', 1)

            if len(parts) == 2:
                file_date, file_scene = parts
            else:
                continue

            # フィルタリング
            if scene and file_scene != scene:
                continue

            if start_date and file_date < start_date:
                continue

            if end_date and file_date > end_date:
                break

            # メモを読み込み
            memo = self.read_memo(f"daily/{markdown_file.name}")
            if memo:
                results.append(memo)

            if len(results) >= limit:
                break

        return results

    async def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """キーワードでメモを検索"""
        results = []

        for markdown_file in self.vault_path.rglob("*.md"):
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if keyword.lower() in content.lower():
                frontmatter, body = self._parse_markdown(content)
                results.append({
                    "path": str(markdown_file.relative_to(self.vault_path)),
                    "frontmatter": frontmatter,
                    "excerpt": self._extract_excerpt(body, keyword),
                })

            if len(results) >= limit:
                break

        return results

    def _extract_excerpt(self, text: str, keyword: str, context_chars: int = 100) -> str:
        """キーワード周辺のテキストを抽出"""
        lower_text = text.lower()
        lower_keyword = keyword.lower()

        idx = lower_text.find(lower_keyword)
        if idx == -1:
            return text[:context_chars] + "..."

        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keyword) + context_chars)

        excerpt = text[start:end]
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."

        return excerpt

    def get_latest_memo(self, scene_type: str = None) -> Optional[Dict]:
        """最新のメモを取得"""
        results = []

        for markdown_file in sorted(self.vault_path.glob("daily/*.md"), reverse=True):
            filename = markdown_file.stem

            if scene_type and scene_type not in filename:
                continue

            memo = self.read_memo(f"daily/{markdown_file.name}")
            if memo:
                return memo

        return None

    def get_memos_in_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """期間内のメモを取得"""
        results = []

        for markdown_file in self.vault_path.glob("daily/*.md"):
            filename = markdown_file.stem
            date_str = filename[:10]  # "2025-01-27"

            try:
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if start_date <= file_date <= end_date:
                    memo = self.read_memo(f"daily/{markdown_file.name}")
                    if memo:
                        memo['date'] = date_str
                        results.append(memo)
            except ValueError:
                continue

        return sorted(results, key=lambda x: x.get('date', ''))


async def save_media_memo(memo_data: dict, scene: str, media_type: str) -> str:
    """画像・動画メモを保存"""

    obsidian = ObsidianManager(os.getenv('OBSIDIAN_VAULT_PATH'))

    # 日付を追加
    memo_data['date'] = datetime.now().strftime('%Y-%m-%d')
    memo_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M')

    return await obsidian.save_memo(memo_data, scene)
```

---

## git_manager.py

```python
import asyncio
import subprocess
import os

async def push_changes(commit_message: str):
    """変更をGitHubにプッシュ"""

    if os.getenv('GITHUB_PUSH_ENABLED', 'true').lower() != 'true':
        return  # プッシュ無効の場合は何もしない

    vault_path = os.getenv('OBSIDIAN_VAULT_PATH')

    try:
        # Git add
        subprocess.run(
            ['git', 'add', '.'],
            cwd=vault_path,
            check=True,
            capture_output=True
        )

        # Git commit
        subprocess.run(
            ['git', 'commit', '-m', commit_message],
            cwd=vault_path,
            check=True,
            capture_output=True
        )

        # Git push
        subprocess.run(
            ['git', 'push'],
            cwd=vault_path,
            check=True,
            capture_output=True
        )

    except subprocess.CalledProcessError as e:
        print(f"Git操作エラー: {e.stderr.decode() if e.stderr else str(e)}")
```

---

## 使用例

### メモの保存と読み込みフロー

```python
from src.storage.obsidian_manager import ObsidianManager

obsidian = ObsidianManager(os.getenv("OBSIDIAN_VAULT_PATH"))

# 1. メモを保存
memo_data = {
    "date": "2025-01-27",
    "timestamp": "2025-01-27 14:30",
    "scene": "壁打ち",
    "raw_text": "今日はサーブを重点的に練習した...",
    "tags": ["サーブ", "トス"],
    "important": False
}

memo_id = await obsidian.save_memo(memo_data, "壁打ち")
# → ファイル: daily/2025-01-27-壁打ち.md

# 2. 日付とシーンでメモを検索
memos = await obsidian.search_by_date_and_scene(
    scene="壁打ち",
    start_date="2025-01-20",
    limit=10
)

# 3. メモの内容を確認
for memo in memos:
    print(f"日付: {memo['frontmatter']['date']}")
    print(f"タグ: {memo['frontmatter']['tags']}")
    print(f"本文: {memo['body']}")
```

### キーワード検索の例

```python
# キーワードで検索
results = await obsidian.search_by_keyword("サーブ", limit=5)

for result in results:
    print(f"パス: {result['path']}")
    print(f"日付: {result['frontmatter']['date']}")
    print(f"抜粋: {result['excerpt']}")
```

---

## 次のドキュメント

- [security.md](security.md) - セキュリティ考慮事項
