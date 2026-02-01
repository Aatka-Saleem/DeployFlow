"""
GitHub Repository Fetcher
Fetches repository information from GitHub API without authentication
"""

import requests
import base64
from typing import Dict, Optional, List


class GitHubFetcher:
    """Fetches repository data from GitHub public API"""

    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }

    def parse_github_url(self, url: str) -> tuple:
        """
        Parse GitHub URL to extract owner and repo name

        Args:
            url: GitHub URL (e.g., https://github.com/owner/repo)

        Returns:
            Tuple of (owner, repo_name)
        """
        url = url.strip()

        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]

        # Remove ".git" properly (FIXED)
        if url.endswith(".git"):
            url = url[:-4]

        # Remove GitHub base URL
        url = url.replace("https://github.com/", "").replace("http://github.com/", "")

        parts = url.split("/")

        if len(parts) >= 2:
            return parts[0], parts[1]

        raise ValueError(f"Invalid GitHub URL: {url}")

    def fetch_repository_info(self, owner: str, repo: str) -> Dict:
        """
        Fetch repository metadata
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repository info: {e}")
            return {}

    def fetch_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """
        Fetch content of a specific file
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "content" in data:
                content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
                return content

            return None

        except Exception as e:
            print(f"Could not fetch {path}: {e}")
            return None

    def fetch_repository_tree(self, owner: str, repo: str) -> List[str]:
        """
        Fetch list of files in repository
        """
        # Try main first
        branches_to_try = ["main", "master"]

        for branch in branches_to_try:
            url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"

            try:
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 404:
                    continue

                response.raise_for_status()
                data = response.json()

                tree = data.get("tree", [])
                files = [item["path"] for item in tree if item.get("type") == "blob"]
                return files

            except Exception:
                continue

        print("Error fetching repository tree: Could not find main/master branch tree")
        return []

    def analyze_repository(self, github_url: str) -> str:
        """
        Analyze a GitHub repository and create a description for the agents
        """
        try:
            owner, repo = self.parse_github_url(github_url)

            print(f"📡 Fetching repository: {owner}/{repo}")

            repo_info = self.fetch_repository_info(owner, repo)

            if not repo_info:
                return f"Error: Could not fetch repository information from {github_url}"

            files = self.fetch_repository_tree(owner, repo)

            language = repo_info.get("language", "Unknown")
            description = repo_info.get("description", "No description")

            requirements_txt = None
            package_json = None
            pom_xml = None

            if "requirements.txt" in files:
                requirements_txt = self.fetch_file_content(owner, repo, "requirements.txt")

            if "package.json" in files:
                package_json = self.fetch_file_content(owner, repo, "package.json")

            if "pom.xml" in files:
                pom_xml = self.fetch_file_content(owner, repo, "pom.xml")

            analysis = f"""
Repository: {repo_info.get('name', repo)}
URL: {github_url}
Description: {description}
Primary Language: {language}
Stars: {repo_info.get('stargazers_count', 0)}
Forks: {repo_info.get('forks_count', 0)}

Files Detected:
{chr(10).join(['- ' + f for f in files[:20]])}
{'... and more' if len(files) > 20 else ''}

"""

            if requirements_txt:
                analysis += f"\nrequirements.txt content:\n{requirements_txt[:500]}\n"

            if package_json:
                analysis += f"\npackage.json content:\n{package_json[:500]}\n"

            if pom_xml:
                analysis += f"\npom.xml content:\n{pom_xml[:500]}\n"

            common_files = []
            for file_name in ["app.py", "main.py", "server.js", "index.js", "Application.java"]:
                if file_name in files:
                    common_files.append(file_name)

            if common_files:
                analysis += f"\nMain application files: {', '.join(common_files)}\n"

            print("✅ Successfully analyzed repository!")
            return analysis

        except ValueError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error analyzing repository: {str(e)}"


# Main function for testing
if __name__ == "__main__":
    fetcher = GitHubFetcher()

    test_url = "https://github.com/Aatka-Saleem/fitness_testing.git"

    print("Testing GitHub Fetcher:")
    print("=" * 70)

    result = fetcher.analyze_repository(test_url)
    print(result)
