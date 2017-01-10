import os.path
from git import Repo

BASE_REPOS_PATH = os.path.abspath(os.path.join("/", "var", "opt", "git_repos"))

def manage_repo(url, repo, branch):
    print url, repo, branch
    checkout_to = branch
    if False:
        if branch not in ["master", "preprod"]:
            branch = "test"
        repo_folder = os.path.join(BASE_REPOS_PATH, repo, branch)
         
        if not os.path.exists(repo_folder):
            Repo.clone_from("git_url", repo_folder)
            repo = Git(repo_folder)
        else:
            repo = Git(repo_folder)
            repo.pull()
        repo.checkout(checkout_to)