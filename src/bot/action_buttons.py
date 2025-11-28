"""
Discordアクションボタン - メモ保存後のユーザーアクション選択UI
"""
import logging
from typing import Dict, Any, Optional, Literal

import discord
from discord.ui import Button, View


logger = logging.getLogger(__name__)


ActionResult = Literal["deep_dive", "compare", "finish", "timeout"]


class ActionButtonsView(View):
    """保存後のアクションボタン"""

    def __init__(
        self,
        memo_data: Dict[str, Any],
        timeout: float = 60.0,
        enable_deep_dive: bool = True,
        enable_compare: bool = True
    ):
        """
        Initialize ActionButtonsView.

        Args:
            memo_data: メモデータ（辞書形式）
            timeout: タイムアウト時間（秒）
            enable_deep_dive: 深堀ボタンを有効化
            enable_compare: 比較ボタンを有効化
        """
        super().__init__(timeout=timeout)
        self.memo_data = memo_data
        self.result: Optional[ActionResult] = None

        # 深堀ボタンが無効の場合は削除
        if not enable_deep_dive:
            self.remove_item(self.deep_dive_button)

        # 比較ボタンが無効の場合は削除
        if not enable_compare:
            self.remove_item(self.compare_button)

    @discord.ui.button(
        label="深堀り質問",
        style=discord.ButtonStyle.primary,
        emoji="🤔"
    )
    async def deep_dive_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        """深堀り質問ボタン"""
        logger.info(f"User {interaction.user.name} clicked 'deep_dive' button")
        self.result = "deep_dive"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(
        label="過去と比較",
        style=discord.ButtonStyle.secondary,
        emoji="📊"
    )
    async def compare_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        """過去と比較ボタン"""
        logger.info(f"User {interaction.user.name} clicked 'compare' button")
        self.result = "compare"
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(
        label="そのまま終了",
        style=discord.ButtonStyle.success,
        emoji="✅"
    )
    async def finish_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        """そのまま終了ボタン"""
        logger.info(f"User {interaction.user.name} clicked 'finish' button")
        self.result = "finish"
        await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        """タイムアウト時の処理"""
        logger.info("Action buttons timed out")
        self.result = "timeout"
        for item in self.children:
            item.disabled = True


async def send_with_action_buttons(
    channel: discord.TextChannel,
    content: str,
    memo_data: Dict[str, Any],
    timeout: float = 60.0,
    enable_deep_dive: bool = True,
    enable_compare: bool = True
) -> ActionResult:
    """
    アクションボタン付きでメッセージを送信し、ユーザーの選択を待つ

    Args:
        channel: 送信先チャンネル
        content: メッセージ内容
        memo_data: メモデータ
        timeout: タイムアウト時間（秒）
        enable_deep_dive: 深堀ボタンを有効化
        enable_compare: 比較ボタンを有効化

    Returns:
        ユーザーが選択したアクション ("deep_dive" | "compare" | "finish" | "timeout")
    """
    view = ActionButtonsView(
        memo_data=memo_data,
        timeout=timeout,
        enable_deep_dive=enable_deep_dive,
        enable_compare=enable_compare
    )

    message = await channel.send(content=content, view=view)

    logger.info(f"Sent action buttons, waiting for user interaction (timeout: {timeout}s)")

    # ボタン押下を待つ
    await view.wait()

    # ボタンを無効化
    for item in view.children:
        item.disabled = True

    try:
        await message.edit(view=view)
    except discord.errors.NotFound:
        logger.warning("Message was deleted before buttons could be disabled")

    result = view.result or "timeout"
    logger.info(f"User action: {result}")

    return result


class ConfirmButtonsView(View):
    """確認ダイアログ用のボタン（はい/いいえ）"""

    def __init__(self, timeout: float = 30.0):
        """
        Initialize ConfirmButtonsView.

        Args:
            timeout: タイムアウト時間（秒）
        """
        super().__init__(timeout=timeout)
        self.result: Optional[bool] = None

    @discord.ui.button(
        label="はい",
        style=discord.ButtonStyle.success,
        emoji="✅"
    )
    async def yes_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        """はいボタン"""
        logger.info(f"User {interaction.user.name} clicked 'yes'")
        self.result = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(
        label="いいえ",
        style=discord.ButtonStyle.danger,
        emoji="❌"
    )
    async def no_button(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        """いいえボタン"""
        logger.info(f"User {interaction.user.name} clicked 'no'")
        self.result = False
        await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        """タイムアウト時の処理"""
        logger.info("Confirm buttons timed out")
        self.result = False  # タイムアウト時はデフォルトで「いいえ」
        for item in self.children:
            item.disabled = True


async def confirm_dialog(
    channel: discord.TextChannel,
    question: str,
    timeout: float = 30.0
) -> bool:
    """
    確認ダイアログを表示し、ユーザーの回答を待つ

    Args:
        channel: 送信先チャンネル
        question: 質問内容
        timeout: タイムアウト時間（秒）

    Returns:
        「はい」の場合 True、「いいえ」またはタイムアウトの場合 False
    """
    view = ConfirmButtonsView(timeout=timeout)

    message = await channel.send(content=question, view=view)

    logger.info(f"Sent confirm dialog, waiting for user response (timeout: {timeout}s)")

    # ボタン押下を待つ
    await view.wait()

    # ボタンを無効化
    for item in view.children:
        item.disabled = True

    try:
        await message.edit(view=view)
    except discord.errors.NotFound:
        logger.warning("Message was deleted before buttons could be disabled")

    result = view.result if view.result is not None else False
    logger.info(f"User confirmed: {result}")

    return result
