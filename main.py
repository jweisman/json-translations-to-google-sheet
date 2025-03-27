import webbrowser, argparse, os
from df_utils import merge_json_to_csv, split_csv_to_json_series
from drive_utils import * 
from github_utils import GithubUtils
from secret import GITHUB_TOKEN
from params import DRIVE_FOLDER, LANGUAGES, GITHUB_REPOS

CSV_NAME = 'translations'
OUTPUT_FOLDER_NAME = 'output'
INPUT_FOLDER_NAME = 'input'
ENGLISH_FILE_NAME = 'en.json'

def sort_files(files, file_name):
  index = list(map(lambda f: f['name'], files)).index(file_name) 
  first_object = files[index]
  if index:
    del(files[index])
    files.insert(0, first_object)
  return files

def create_csv_file(json_files, file_name):
  # English needs to be first to join left
  json_files = sort_files(json_files, ENGLISH_FILE_NAME)
  # Join to CSV
  csv = merge_json_to_csv(json_files)
  # Upload and convert to Google sheet
  file = create_or_replace_file(csv, parent_id=DRIVE_FOLDER, mimetype='text/csv', target_mimetype='application/vnd.google-apps.spreadsheet', filename=file_name)
  webbrowser.open(file.get('webViewLink'))

def create_csv(json_source):
  if json_source == 'drive':
    # Find files in Drive
    json_files = find_files('name contains ".json"', get_or_create_folder(INPUT_FOLDER_NAME, DRIVE_FOLDER))
    # Convert to list
    json_files = list(map(lambda file: {'name': file['name'], 'contents': download_file(file['id']).decode()}, json_files))
    create_csv_file(json_files, CSV_NAME)
  else:
    for repo in GITHUB_REPOS:
      repo_name, repo_dir = repo
      gh = GithubUtils(repo_name, GITHUB_TOKEN)
      # Get files from Github
      json_files = gh.get_files(repo_dir)
      # Filter for desired languages
      json_files = [file for file in json_files if file.name in map(lambda x: x + '.json', LANGUAGES)]
      # Convert to list
      json_files = list(map(lambda file: {'name': file.name, 'contents': file.decoded_content.decode()}, json_files))
      create_csv_file(json_files, f"{os.path.basename(repo_name)}-{CSV_NAME}")

def update_jsons():
  files = find_files(f"mimeType='{MimeTypes.SHEETS}'", parent_id=DRIVE_FOLDER)
  output_folder_id = get_or_create_folder(OUTPUT_FOLDER_NAME, DRIVE_FOLDER)
  for file in files:
    # Get Sheet as CSV
    csv_file = export_file(file['id'], 'text/csv')
    # Convert to JSON files
    json_files = split_csv_to_json_series(csv_file)
    # Upload to Drive
    folder_id = get_or_create_folder(file['name'], output_folder_id)
    for file in json_files:
      file = create_or_replace_file(file['bytes'], filename=file['name'], parent_id=folder_id)
    # Navigate to folder
    folder = get_file(file['parents'][0])
    webbrowser.open(folder.get('webViewLink'))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Parses translation JSON files into CSV, and back.')
  parser.add_argument('action', choices=['csv', 'json'])
  parser.add_argument('--j', dest='json_source', help='JSON source (default: github)', choices=['drive', 'github'], default='github')
  args = parser.parse_args()
  if args.action == 'csv':
    create_csv(args.json_source)
  else:
    update_jsons()
