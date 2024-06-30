from github import Github, Auth
from params import GITHUB_REPO
from secret import GITHUB_TOKEN


# using an access token
auth = Auth.Token(GITHUB_TOKEN)

# Public Web Github
g = Github(auth=auth)

# Github Enterprise with custom hostname
#g = Github(auth=auth, base_url="https://{hostname}/api/v3")

repo = g.get_repo(GITHUB_REPO)

def get_files(dir):
  return repo.get_contents(dir)
  #for content_file in contents:
  #  print(content_file)
  #  print(content_file.decoded_content.decode())
    #print(help(content_file))