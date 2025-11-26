"""
GitHub synchronization for Obsidian vault.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from github import Github, GithubException, InputGitTreeElement
from github.Repository import Repository

from src.models.session import PracticeSession
from src.storage.markdown_builder import MarkdownBuilder

# Load environment variables
load_dotenv()


class GitHubSync:
    """Sync practice session markdown files to GitHub repository."""

    def __init__(
        self,
        repo_name: Optional[str] = None,
        token: Optional[str] = None,
        base_path: Optional[str] = None
    ):
        """
        Initialize GitHub sync client.

        Args:
            repo_name: Repository name (format: "username/repo-name")
            token: GitHub personal access token
            base_path: Base directory path in repository (e.g., "sessions")
        """
        self.repo_name = repo_name or os.getenv("GITHUB_REPO")
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_path = base_path or os.getenv("OBSIDIAN_PATH", "sessions")

        if not self.repo_name:
            raise ValueError("GITHUB_REPO not found in environment variables")
        if not self.token:
            raise ValueError("GITHUB_TOKEN not found in environment variables")

        # Initialize GitHub client
        self.github = Github(self.token)
        self.repo: Repository = self.github.get_repo(self.repo_name)

        print(f"🔗 Connected to GitHub repository: {self.repo_name}")

    def push_session(
        self,
        session: PracticeSession,
        commit_message: Optional[str] = None
    ) -> str:
        """
        Push practice session to GitHub repository.

        Args:
            session: PracticeSession object
            commit_message: Custom commit message. If None, auto-generated.

        Returns:
            URL of the created/updated file

        Raises:
            GithubException: If push fails
        """
        # Build markdown content
        builder = MarkdownBuilder()
        markdown_content = builder.build(session)

        # Generate file path
        file_path = builder.get_relative_path_for_session(session, self.base_path)

        # Generate commit message
        if commit_message is None:
            date_str = session.date.strftime("%Y-%m-%d")
            commit_message = f"Add practice session: {date_str}"

        # Push to GitHub
        print(f"📤 Pushing to GitHub: {file_path}")
        file_url = self._push_file(
            file_path=file_path,
            content=markdown_content,
            commit_message=commit_message
        )

        print(f"✅ Successfully pushed to GitHub: {file_url}")
        return file_url

    def _push_file(
        self,
        file_path: str,
        content: str,
        commit_message: str
    ) -> str:
        """
        Push or update a file in the repository.

        Args:
            file_path: Relative path in repository
            content: File content
            commit_message: Commit message

        Returns:
            URL of the file in GitHub
        """
        try:
            # Check if file exists
            try:
                existing_file = self.repo.get_contents(file_path)
                # File exists, update it
                result = self.repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha
                )
                print(f"📝 Updated existing file: {file_path}")
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    result = self.repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content
                    )
                    print(f"✨ Created new file: {file_path}")
                else:
                    raise

            return result["content"].html_url

        except GithubException as e:
            raise Exception(f"Failed to push to GitHub: {e.data.get('message', str(e))}")

    def get_latest_session(self) -> Optional[str]:
        """
        Get the latest practice session file path from repository.

        Returns:
            File path of the latest session, or None if no sessions found
        """
        try:
            contents = self.repo.get_contents(self.base_path)
            if not contents:
                return None

            # Find all markdown files
            md_files = []
            for content in contents:
                if content.type == "dir":
                    # Recursively search subdirectories
                    self._find_markdown_files(content.path, md_files)
                elif content.name.endswith(".md"):
                    md_files.append(content.path)

            if not md_files:
                return None

            # Sort by name (assumes date-based naming) and return latest
            md_files.sort(reverse=True)
            return md_files[0]

        except GithubException:
            return None

    def _find_markdown_files(self, directory: str, md_files: list):
        """Recursively find markdown files in directory."""
        try:
            contents = self.repo.get_contents(directory)
            for content in contents:
                if content.type == "dir":
                    self._find_markdown_files(content.path, md_files)
                elif content.name.endswith(".md"):
                    md_files.append(content.path)
        except GithubException:
            pass

    def check_connection(self) -> bool:
        """
        Check if connection to GitHub repository is working.

        Returns:
            True if connection is successful
        """
        try:
            self.repo.get_branch("main")
            print(f"✅ GitHub connection OK: {self.repo_name}")
            return True
        except GithubException as e:
            print(f"❌ GitHub connection failed: {e.data.get('message', str(e))}")
            return False
