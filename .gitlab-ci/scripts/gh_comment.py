#!/usr/bin/env python3

"""Post a comment on the GitHub pull request matching this GitLab pipeline's branch."""
import argparse
import json
import os
import urllib.parse
import urllib.request


class GithubComment:
    def __init__(self, token, repo, branch, job_url=""):
        """repo is owner/repo; branch is the GitLab pipeline branch."""
        self.token = token
        self.repo = repo
        self.branch = branch
        self.job_url = job_url

    def _api(self, path, data=None):
        request = urllib.request.Request(
            f"https://api.github.com/repos/{self.repo}/{path}",
            data=data,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def find_pr_number(self):
        """Number of the open GitHub PR whose head is this pipeline's branch."""
        owner = self.repo.split("/")[0]
        head = urllib.parse.quote(f"{owner}:{self.branch}")
        prs = self._api(f"pulls?state=open&head={head}")
        if not prs:
            raise SystemExit(f"No open PR for branch {self.branch} in {self.repo}")
        return prs[0]["number"]

    def comment(self):
        body = "Test run finished.\n\n"
        if self.job_url:
            body += f"Artifacts: {self.job_url}/artifacts/browse/results/"
        print("Posting comment...")
        self._api(f"issues/{self.find_pr_number()}/comments", json.dumps({"body": body}).encode())


def main():
    env = os.environ.get
    branch = env("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME") or env("CI_COMMIT_BRANCH")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=env("REPO"), required="REPO" not in os.environ, help="owner/repo [env REPO]")
    parser.add_argument("--branch", default=branch, required=branch is None, help="GitLab branch [env CI_MERGE_REQUEST_SOURCE_BRANCH_NAME or CI_COMMIT_BRANCH]")
    parser.add_argument("--job-url", default=env("CI_JOB_URL", ""), help="[env CI_JOB_URL]")
    args = parser.parse_args()
    GithubComment(os.environ["TOKEN"], args.repo, args.branch, args.job_url).comment()


if __name__ == "__main__":
    main()
