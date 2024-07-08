import webbrowser, argparse
from df_utils import merge_json_to_csv, split_csv_to_json_series
from drive_utils import create_or_replace_file, find_file, export_file, get_or_create_folder, find_files, download_file, get_file
from github_utils import get_files
from params import DRIVE_FOLDER, GITHUB_TRANSLATIONS_DIR, LANGUAGES

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

def upload_csv(json_source):
  if json_source == 'drive':
    # Find files in Drive
    json_files = find_files('name contains ".json"', get_or_create_folder(INPUT_FOLDER_NAME, DRIVE_FOLDER))
    # Convert to list
    json_files = list(map(lambda file: {'name': file['name'], 'contents': download_file(file['id']).decode()}, json_files))
  else:
    # Get files from Github
    json_files = get_files(GITHUB_TRANSLATIONS_DIR)
    # Filter for desired languages
    json_files = [file for file in json_files if file.name in map(lambda x: x + '.json', LANGUAGES)]
    # Convert to list
    json_files = list(map(lambda file: {'name': file.name, 'contents': file.decoded_content.decode()}, json_files))

  # English needs to be first to join left
  json_files = sort_files(json_files, ENGLISH_FILE_NAME)
  # Join to CSV
  csv = merge_json_to_csv(json_files)
  # Upload and convert to Google sheet
  file = create_or_replace_file(csv, parent_id=DRIVE_FOLDER, mimetype='text/csv', target_mimetype='application/vnd.google-apps.spreadsheet', filename=CSV_NAME)
  webbrowser.open(file.get('webViewLink'))

def update_jsons():
  # Get Sheet as CSV
  csv_file = export_file(find_file(CSV_NAME, parent_id=DRIVE_FOLDER)['id'], 'text/csv')
  # Convert to JSON files
  json_files = split_csv_to_json_series(csv_file)
  # Upload to Drive
  folder_id = get_or_create_folder(OUTPUT_FOLDER_NAME, DRIVE_FOLDER)
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
    upload_csv(args.json_source)
  else:
    update_jsons()
