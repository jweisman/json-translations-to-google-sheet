from github import Github, Auth
from params import GITHUB_REPO
from secret import GITHUB_TOKEN


# using an access token
auth = Auth.Token(GITHUB_TOKEN)

# Public Web Github
g = Github(auth=auth)

repo = g.get_repo(GITHUB_REPO)

def get_files(dir):
  return repo.get_contents(dir)
