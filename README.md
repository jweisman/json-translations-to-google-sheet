# JSON Translation Files to Google Sheet

## Instructions
1. Set up Python environment
   * Make sure [Python is installed](https://cloud.google.com/python/docs/setup)
   * Install requirements: `pip install -r requirements.txt`
2. Update parameters in `params.py`
3. Download credential key file for a [GCP Service Account](https://medium.com/@matheodaly.md/create-a-google-cloud-platform-service-account-in-3-steps-7e92d8298800) and save it as `key.json`
4. Ensure the service account has access to the folder in Google Drive
5. Create a [Github token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with access to the desired repository
6. Add secret.py file with the following parameters. 
```
GITHUB_TOKEN = 'token'
```
7. Run `python main.py csv` to download the JSON files and create a Google Sheet. Run `python main.py json` to parse the updated Sheet into JSON files. By default JSON files are retrieved from Github. To retrieve them from Google Drive, use `python main.py --j drive csv`
