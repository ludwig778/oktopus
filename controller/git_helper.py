import os.path
from git import Repo

BASE_REPOS_PATH = os.path.abspath(os.path.join("/", "var", "opt", "git_repos"))

def manage_repo(url, repo, branch):
    print url, repo, branch
    if False:
        repo_folder = os.path.join(BASE_REPOS_PATH, repo, branch)
         
        if not os.path.exists(repo_folder):
            Repo.clone_from("git_url", repo_folder)
        else:
            repo = git.cmd.Git(repo_folder)
            repo.pull()