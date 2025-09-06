import os
import pandas as pd
from tqdm import tqdm
import re
from datetime import datetime


def clean_header_and_drop_unuse_row(tmp_df):
    """Cleans the header of a single DataFrame."""
    tmp_df.columns = tmp_df.iloc[0]
    tmp_df = tmp_df[1:].reset_index(drop=True)
    if 'Date' in tmp_df.columns:
        tmp_df = tmp_df[~pd.isna(tmp_df['Date'])]
    return tmp_df

def preprocess_convert_datatype_with_date(tmp_df, filename):
    """Adds a proper datetime index and converts data to numeric."""
    match = re.search(r"(\d{2})-(\d{4})", filename)
    if not match:
        raise ValueError(f"Cannot extract date from filename: {filename}")
    start_month, start_year = map(int, match.groups())
    date_range = pd.date_range(start=datetime(start_year, start_month, 1), periods=len(tmp_df), freq='D')
    tmp_df['Date'] = date_range
    time_cols = [col for col in tmp_df.columns if col != "Date"]
    tmp_df[time_cols] = tmp_df[time_cols].apply(pd.to_numeric, errors='coerce')
    return tmp_df

def load_and_preprocess_data():
    """Main function to load, clean, and prepare the dataset."""
    # download_data()
    
    # Process Excel files to cleaned CSVs
    cleaned_data_dir = "cleaned_data"
    os.makedirs(cleaned_data_dir, exist_ok=True)
    for subdir, _, files in tqdm(os.walk('Load-data'), desc="Cleaning Excel files"):
        for file in files:
            if file.endswith(".xlsx"):
                try:
                    rel_path = os.path.relpath(subdir, 'Load-data')
                    output_subdir = os.path.join(cleaned_data_dir, rel_path)
                    os.makedirs(output_subdir, exist_ok=True)
                    
                    df = pd.read_excel(os.path.join(subdir, file))
                    df = clean_header_and_drop_unuse_row(df)
                    df.to_csv(os.path.join(output_subdir, file.replace('.xlsx', '.csv')), index=False)
                except Exception as e:
                    print(f"Skipping file {file} due to error: {e}")

    # Process cleaned CSVs to preprocessed CSVs
    preprocessed_data_dir = "preprocessed_data"
    os.makedirs(preprocessed_data_dir, exist_ok=True)
    for subdir, _, files in tqdm(os.walk(cleaned_data_dir), desc="Preprocessing CSV files"):
         for file in files:
            if file.endswith(".csv"):
                rel_path = os.path.relpath(subdir, cleaned_data_dir)
                output_subdir = os.path.join(preprocessed_data_dir, rel_path)
                os.makedirs(output_subdir, exist_ok=True)
                
                df = pd.read_csv(os.path.join(subdir, file))
                df = preprocess_convert_datatype_with_date(df, file)
                df.insert(0, 'station_name', rel_path)
                df.to_csv(os.path.join(output_subdir, file), index=False)
    
    # Concatenate all data
    all_data = [pd.read_csv(os.path.join(subdir, file)) for subdir, _, files in os.walk(preprocessed_data_dir) for file in files if file.endswith(".csv")]
    all_data_df = pd.concat(all_data, ignore_index=True)
    
    # Melt to long format
    time_columns = [col for col in all_data_df.columns if re.match(r"^\d{1,2}:\d{2}$", str(col))]
    long_df = all_data_df.melt(id_vars=['station_name', 'Date'], value_vars=time_columns, var_name='Time', value_name='Electricity(kW)')
    long_df['Date'] = pd.to_datetime(long_df['Date'].astype(str) + ' ' + long_df['Time'])
    long_df.drop(columns=['Time'], inplace=True)
    long_df.sort_values(by=['station_name', 'Date'], inplace=True)
    
    # Final cleaning
    long_df = long_df[long_df['station_name'] != 'Data_อาคารวิทยนิเวศน์'].copy()
    long_df.loc[long_df['Electricity(kW)'] < 0, 'Electricity(kW)'] = 0
    long_df['Electricity(kW)'].fillna(method='ffill', inplace=True)
    long_df.dropna(inplace=True)

    # Split data
    train_list, test_list = [], []
    for _, station_df in long_df.groupby('station_name'):
        train_end = int(len(station_df) * 0.8)
        train_list.append(station_df.iloc[:train_end])
        test_list.append(station_df.iloc[train_end:])
        
    return pd.concat(train_list), pd.concat(test_list)