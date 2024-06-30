from io import BytesIO, StringIO
import pandas as pd

def merge_json_to_csv(files):
  merged_df = pd.DataFrame()

  for index, json_file in enumerate(files):
    # Load JSON file into a DataFrame
    df = pd.read_json(StringIO(json_file['contents']), typ='series').reset_index()
    df.columns = ['index', json_file['name'].replace('.json', '')]
    
    # Merge with the existing DataFrame
    if merged_df.empty:
      merged_df = df
    else:
      merged_df = pd.merge(merged_df, df, on='index', how='left')
    
  # Save the resulting DataFrame to a CSV file
  csv_buffer = BytesIO()
  merged_df.to_csv(csv_buffer, index=False)
  return csv_buffer

def split_csv_to_json_series(csv_file):
  # Read the CSV file into a DataFrame
  df = pd.read_csv(BytesIO(csv_file))
    
  # JSON Files
  json_files = []

  # Iterate over the columns (excluding the 'index' column)
  for column in df.columns[1:]:
    # Filter the DataFrame to include only rows where the column has a value
    filtered_df = df[['index', column]].dropna(subset=[column])
    
    # Convert the filtered DataFrame to a series
    series = filtered_df.set_index('index')[column]
    
    # Get bytes of file
    file = BytesIO()
    series.to_json(file, indent=4, force_ascii=False)

    # Add file to array
    json_files.append({ 'name': column + '.json', 'bytes': file})

  return json_files