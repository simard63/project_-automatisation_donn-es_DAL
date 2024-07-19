from datetime import datetime
import pandas as pd
import zipfile

def calculate_time_diff(row):
    """
    Calculate the amount of time the cows drank.
    Args:
    - row: Row in the dataset
    Returns:
    - Time in 00:00:00 format
    """
    # Get the date and time data from the row
    DStart = row["Date_debut"]
    HStart = row["Heure_debut"]
    DEnd = row["Date_fin"]
    HEnd = row["Heure_fin"]

    # Combine the date and time into a single datetime object
    start_datetime = datetime.strptime(DStart + " " + HStart, "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime(DEnd + " " + HEnd, "%Y-%m-%d %H:%M:%S")
    
    # Calculate the difference between start and end times
    time_difference = end_datetime - start_datetime
    
    # Format the time difference into hours, minutes, and seconds
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Return the formatted time difference as a string
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def generate_bande(date_str):
    """
    Generate the value for "bande" columns by period of time during the years.
    Args:
    - date_str: Date from the data file of cow's birth to know the "bande".
    Returns:
    - B2_XXXX or B1_XXXX
    """
    # Convert the date string to a datetime object
    date = pd.to_datetime(date_str)
    
    # Determine the "bande" based on the month of the date
    if date.month < 7:
        return f'B1_{date.year}'
    else:
        return f'B2_{date.year}'

def animal_caract(zip_filename, start_date, end_date):
    """
    Unzip raw data from the DAL to use file 00 and clean it.
    Args:
    - zip_filename: The path to the zip file.
    - start_date: Date of the first birth of cow's session.
    - end_date: Date of the last birth of cow's session.
    Returns:
    - Data files with ID of cows (urban, UEPAO, date of birth, lot, bande)
    """
    # Dictionary to rename columns
    rename_dict = {
        'tiere_id': 'URBAN_ID',
        'tier_nr': 'NUM',
        'geburtsdatum': 'Date_Naiss',
        'kurvennr': 'Courbe'
    }

    # Unzip the raw data from the DAL
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        with zipf.open('Export_instutut_export_nr_00.csv') as file:
            cows_id = pd.read_csv(file, delimiter=';')
                    
    # Rename columns according to the dictionary
    cows_id.rename(columns=rename_dict, inplace=True)
    # Keep only the renamed columns
    cows_id = cows_id[list(rename_dict.values())]

    # Convert start and end date strings to datetime.date
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Convert 'Date_Naiss' column to datetime.date
    cows_id['Date_Naiss'] = pd.to_datetime(cows_id['Date_Naiss'], dayfirst=True).dt.date

    # Filter rows based on start and end dates
    cows_id = cows_id[(cows_id['Date_Naiss'] >= start_date) & (cows_id['Date_Naiss'] <= end_date)]

    # Sort the DataFrame by 'Date_Naiss'
    cows_id = cows_id.sort_values(by='Date_Naiss', ascending=True)

    # Insert 'Bande' column based on 'Date_Naiss'
    cows_id.insert(3, 'Bande', cows_id['Date_Naiss'].apply(generate_bande))
    
    return cows_id

def animal_data(zip_filename):
    """
    Unzip raw data from the DAL to use file 03 and clean it.
    Args:
    - zip_filename: The path to the zip file.
    Returns:
    - Data files with drink measurements of cows
    """
    # Dictionary to rename columns

    # Unzip the raw data from the DAL
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        with zipf.open('Export_instutut_export_nr_03.csv') as file:
            cows_data = pd.read_csv(file, delimiter=';')
            
    try:
        rename_dict = {
        'tiere_id': 'URBAN_ID',
        'sollmenge_milch': 'Prog_lait',
        'verbrauch_milch': 'Conso_lait',
        'verbrauch_mat1': 'Conso_mat1',
        'verbrauch_mat2': 'Conso_mat2',
        'verbrauch_wasser': 'Conso_eau',
        'zeit_fuetterung_start_datum': 'Date_debut',
        'zeit_fuetterung_start_zeit': 'Heure_debut',
        'zeit_fuetterung_fertig_datum': 'Date_fin',
        'zeit_fuetterung_fertig_zeit': 'Heure_fin'
        }
        # Rename columns according to the dictionary and keep them
        cows_data.rename(columns=rename_dict, inplace=True)
        cows_data = cows_data[list(rename_dict.values())]
    except :
        rename_dict = {
        'tiere_id': 'URBAN_ID',
        'sollmenge_milch': 'Prog_lait',
        'verbrauch_milch': 'Conso_lait',
        'verbrauch_mat1': 'Conso_mat1',
        'verbrauch_mat2': 'Conso_mat2',
        'verbrauch_wasser': 'Conso_eau',
        'zeit_fuetterung_start': 'debut',
        'zeit_fuetterung_fertig': 'fin',
        }
        # Rename columns according to the dictionary and keep them
        cows_data.rename(columns=rename_dict, inplace=True)
        cows_data = cows_data[list(rename_dict.values())]
        
        cows_data['debut'] = pd.to_datetime(cows_data['debut'])
        cows_data['fin'] = pd.to_datetime(cows_data['fin'])
        cows_data['Date_debut'] = cows_data['debut'].dt.date.astype(str)
        cows_data['Date_fin'] = cows_data['fin'].dt.date.astype(str)
        cows_data['Heure_debut'] = cows_data['debut'].dt.strftime('%H:%M:%S')
        cows_data['Heure_fin'] = cows_data['fin'].dt.strftime('%H:%M:%S')
        
        cows_data.drop(columns=['debut', 'fin'], inplace=True)
        
    return cows_data

def data_global(zip_filename, start: str):
    """
    Extract and process global data from a zip file.
    Args:
    - zip_filename: Path to the zip file.
    - start: Start date as a string in the format "YYYY-MM-DD".
    Returns:
    - Filtered and sorted DataFrame.
    """

    # Unzip and read the raw data from the DAL
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        with zipf.open('Export_instutut_export_nr_01.csv') as file:
            data = pd.read_csv(file, delimiter=';')
    try:
        # Dictionary to rename columns
        rename_dict = {
            'tiere_id': 'URBAN_ID',
            'erste_erkennung_datum': 'DATE',
            'erste_erkennung_zeit': 'HEURE'
        }
        # Rename columns according to the dictionary
        data.rename(columns=rename_dict, inplace=True)
        # Keep only the renamed columns
        data = data[list(rename_dict.values())]
    except:
        # Dictionary to rename columns
        rename_dict = {
            'tiere_id': 'URBAN_ID',
            'erste_erkennung': 'debut'
        }
        # Rename columns according to the dictionary
        data.rename(columns=rename_dict, inplace=True)
        # Keep only the renamed columns
        data = data[list(rename_dict.values())]
        data['debut'] = pd.to_datetime(data['debut'])
        data['DATE'] = data['debut'].dt.date.astype(str)
        data['HEURE'] = data['debut'].dt.strftime('%H:%M:%S')
        
        data.drop(columns=['debut'], inplace=True)
        
    # Convert start date string to datetime.date
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    
    # Convert 'DATE' column to datetime.date
    data['DATE'] = pd.to_datetime(data['DATE'], dayfirst=True).dt.date

    # Filter rows based on start date
    filtered_data = data[(data['DATE'] >= start_date)]
    # Sort the DataFrame by 'URBAN_ID' and 'DATE'
    filtered_data = filtered_data.sort_values(by=['URBAN_ID', 'DATE'], ascending=True)
    # Reset the index of the DataFrame
    filtered_data.reset_index(drop=True, inplace=True)
    
    return filtered_data

def save_dataframe(df, chemin):
    """
    Save the DataFrame to a CSV file at the specified location.
    Args:
    - df (pandas.DataFrame): The DataFrame to save.
    - chemin (str): The full file path where the CSV should be saved, including the file name.
    Returns:
    - None
    """
    try:
        df.to_csv(chemin, index=False, sep=';')  # Use semicolon as separator
        print(f"DataFrame saved successfully to {chemin}")
    except PermissionError:
        print(f"Permission denied: You do not have permission to write to {chemin} (file might be open).")
    except Exception as e:
        print(f"Error saving file: {str(e)}")

def data_cleaned_without_week(df, nb):
    """
    Keep weeks composed of 7 days of data and remove cows not needed for the experiment.
    Args:
    - df: Data of the complete but uncleaned final DataFrame.
    - nb: Number of weeks threshold.
    Returns:
    - Final data to export without weeks with less than 7 days for the average.
    """
    # Filter cows with less than the required number of values (e.g., for 9 weeks, there must be more than 37 entries)
    df = df[(df.groupby('NUM')['NUM'].transform('count')) >= int(nb) * 7 * 3 / 5]

    # Initialize an empty DataFrame to store the complete data
    df_complet = pd.DataFrame(columns=df.columns)

    # Group by 'NUM'
    grouped = df.groupby('NUM')

    # Iterate through each group
    for num, group in grouped:
        # Check each unique week in the group
        for semaine in group['Sem'].unique():
            # Check the ages present in this week
            ages_presents = group[group['Sem'] == semaine]['JOUR'].unique()

            # Calculate the expected ages for a complete week
            if semaine == "s1":
                ages_attendus = range(3, int(semaine[1:]) * 7)
            else:
                ages_attendus = range((int(semaine[1:]) - 1) * 7, int(semaine[1:]) * 7)

            # Check if all expected ages are present
            if set(ages_attendus) == set(ages_presents):
                df_complet = pd.concat([df_complet, group[group['Sem'] == semaine]], ignore_index=True)
            else:
                # Uncomment the print statement if you want to see which weeks are ignored
                # print(f"Week {semaine} is not complete and will be ignored for NUM={num}.")
                pass
                
    return df_complet

def curve(zip_filename, start_date="2000-01-01", end_date="3000-01-01"):
    """
    Extract unique curve data from animal characteristics within a date range.
    Args:
    - zip_filename: Path to the zip file.
    - start_date: Start date as a string in the format "YYYY-MM-DD".
    - end_date: End date as a string in the format "YYYY-MM-DD".
    Returns:
    - List of unique curves.
    """
    data = animal_caract(zip_filename, start_date, end_date)
    data = data['Courbe']
    data = data.unique().tolist()
    
    return data

if __name__ == "__main__":
    
    zip_filename = r'..\data\2024_06_03__10_12_02_touch01__csv_export.zip'
    print(animal_data(zip_filename))
