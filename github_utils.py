from github import Github, Auth

class GithubUtils:

  def __init__(self, repo, secret):
    auth = Auth.Token(secret)
    self.g = Github(auth=auth)
    self.repo = repo

  def get_files(self, dir):
    repo = self.g.get_repo(self.repo)
    print(f"Retrieving {self.repo}/{dir} from Github.")
    return repo.get_contents(dir)
