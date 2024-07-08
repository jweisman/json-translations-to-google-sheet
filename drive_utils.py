from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import mimetypes, io
from googleapiclient.errors import HttpError

scope = ['https://www.googleapis.com/auth/drive']
service_account_json_key = './key.json'
credentials = service_account.Credentials.from_service_account_file(
                              filename=service_account_json_key, 
                              scopes=scope)
service = build('drive', 'v3', credentials=credentials)

DEFAULT_QUERY='trashed=false and name="{}"'
FILE_FIELDS = 'id, name, mimeType, size, modifiedTime, parents, webViewLink'

def guess_mimetype(filename):
  mimetypes.init()
  return mimetypes.guess_type(filename)[0]

def find_folder(name, parent_id=None):
  query = DEFAULT_QUERY.format(name) + ' and mimeType="application/vnd.google-apps.folder"'
  return find_single(query, parent_id=parent_id)

def find_file(name, parent_id=None):
  query = DEFAULT_QUERY.format(name)
  return find_single(query, parent_id=parent_id)

def find_files(query, parent_id=None):
  query = query + ' and trashed=false'
  if parent_id:
    query = query + ' and "{}" in parents'.format(parent_id)
  results = service.files().list(fields=f"nextPageToken, files({FILE_FIELDS})", q=query).execute()
  files = results.get('files', [])
  return files

def find_single(query, parent_id=None):
  if parent_id:
    query = query + ' and "{}" in parents'.format(parent_id)
  results = service.files().list(fields=f"nextPageToken, files({FILE_FIELDS})", q=query).execute()
  items = results.get('files', [])
  if len(items) > 0:
    return items[0]

def get_file(file_id):
  return service.files().get(fileId=file_id, fields=FILE_FIELDS).execute()

def create_folder(name, parent_id=None):
  file_metadata = {
    "name": name,
    "mimeType": "application/vnd.google-apps.folder",
    "parents": [parent_id]
  }
  try:
    file = service.files().create(body=file_metadata, fields="id").execute()
    return file
  except HttpError as error:
    print(f"An error occurred: {error}")
    return None
  
def get_or_create_folder(name, parent_id):
  folder = find_folder(name, parent_id=parent_id)
  if folder == None:
    folder = create_folder(name, parent_id=parent_id)
  return folder['id']
  
def create_or_replace_file(path_or_bytes, filename=None, parent_id=None, mimetype=None, target_mimetype=None):
  if filename == None and isinstance(path_or_bytes, str):
    filename = path_or_bytes.rpartition('/')[-1]

  if mimetype == None and filename != None:
      mimetype = guess_mimetype(filename)

  existing_file = find_file(filename, parent_id=parent_id)
  media = MediaIoBaseUpload(path_or_bytes, mimetype)
  print(f"Uploading {filename} to Drive")

  try:
    if existing_file != None:
      file = service.files().update(fileId=existing_file['id'], media_body=media, fields=FILE_FIELDS).execute()  
    else:
      file_metadata = {'name': filename, 'parents': [parent_id]}
      if target_mimetype: file_metadata['mimeType'] = target_mimetype
      file = service.files().create(body=file_metadata, media_body=media, fields=FILE_FIELDS).execute()  
    return file
  except HttpError as error:
    print(f"An error occurred: {error}")
    return None

def download_file(file_id):
  request = service.files().get_media(fileId=file_id)
  return download_request(request)

def export_file(file_id, mime_type):
  request = service.files().export_media(
      fileId=file_id, mimeType=mime_type
  )
  return download_request(request)

def download_request(request):
  try:
    # pylint: disable=maybe-no-member
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(f"Downloading from Drive ({int(status.progress() * 100)}%).")

  except HttpError as error:
    print(f"An error occurred: {error}")
    file = None

  return file.getvalue()