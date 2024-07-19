import pandas as pd
from Data import par_jour, par_passage
from utils import data_cleaned_without_week, save_dataframe

def sicpa(df, farm):
    """
    Process the DataFrame for SICPA export with specific formatting and renaming.
    
    Args:
    - df (pandas.DataFrame): The input DataFrame with raw data.
    - farm (str): The prefix to prepend to the animal numbers.

    Returns:
    - pandas.DataFrame: The processed DataFrame ready for SICPA export.
    """
    
    # Dictionary to rename columns as required for SICPA export
    rename_dict = {
        'NUM': 'ANIMAL',           # Renames 'NUM' to 'ANIMAL'
        'Temps_buvee': 'DUREE',    # Renames 'Temps_buvee' to 'DUREE'
        'Conso_lait': 'QUANTITE',  # Renames 'Conso_lait' to 'QUANTITE'
        'Prog_lait': 'CONSIGNE'    # Renames 'Prog_lait' to 'CONSIGNE'
        # Columns 'DISTRIBUTEUR', 'ALIMENT', 'ENTREE' will be added later
    }
    
    # Rename columns in the DataFrame based on rename_dict
    df.rename(columns=rename_dict, inplace=True)
    
    # Add a constant value 'DAL' to the 'DISTRIBUTEUR' column
    df['DISTRIBUTEUR'] = 'PAO_BOV_DAL_001'
    
    # Combine 'Date_debut' and 'Heure_debut' into a single 'ENTREE' column
    df['ENTREE'] = df['Date_debut'] + ' ' + df['Heure_debut']
    
    # Convert the combined 'ENTREE' column to datetime format and then to string
    df['ENTREE'] = pd.to_datetime(df['ENTREE'], format='%Y-%m-%d %H:%M:%S')
    df['ENTREE'] = df['ENTREE'].dt.strftime('%d/%m/%Y %H:%M:%S')
    
    # Modify 'ANIMAL' numbers: prepend the farm prefix and convert to string
    df['ANIMAL'] = df['ANIMAL'].apply(lambda x: farm + str(x))
    df['DUREE'] = df['DUREE'].apply(lambda x: '{:02}:{:02}:{:02}'.format(
        int(x.total_seconds() // 3600), int((x.total_seconds() // 60) % 60), int(x.total_seconds() % 60)))
    # Define the columns to keep in the final DataFrame
    keep_columns = ['DISTRIBUTEUR', 'ANIMAL', 'ALIMENT', 'ENTREE', 'DUREE', 'QUANTITE', 'CONSIGNE']
    
    # Reorganize the DataFrame to only include the columns in keep_columns
    df = df[keep_columns]
    
    return df

def sem_comp_jour(df, nb):
    """
    Clean the DataFrame to retain only weeks with at least `nb` days of data.

    Args:
    - df (pandas.DataFrame): The initial DataFrame containing daily data.
    - nb (int): The number of weeks required to keep in the DataFrame.

    Returns:
    - pandas.DataFrame: The cleaned DataFrame with only the specified weeks of data.
    """
    # Clean the DataFrame to remove weeks with less than the required number of days
    df = data_cleaned_without_week(df, nb)
    return df

if __name__ == "__main__":
    # Path to the ZIP file containing raw data
    zip_filename = r'data\2024_06_03__10_12_02_touch01__csv_export.zip'
    
    # Define the start and end dates for the data extraction
    start_date = "2023-09-15"
    end_date = "2024-03-30"
    
    # List of curves and corresponding feed types
    Courbe = [6, 5, 1]
    aliment = ['pao 001', 'pao 002', 'pao 003']
    
    # Theoretical milk consumption values and visit counts by week
    conso_lait = [
        [4, 5, 6, 7, 7, 7, 6, 5, 2.5],     # Consumption for curve 6
        [40, 50, 60, 70, 70, 70, 60, 50, 20.5],  # Consumption for curve 5
        [400, 500, 600, 700, 700, 700, 600, 500, 200.5]  # Consumption for curve 1
    ]
    
    visites = [
        [4, 4, 4, 4, 4, 4, 4, 3, 1],      # Visits for curve 6
        [40, 40, 40, 40, 40, 40, 40, 30, 10],  # Visits for curve 5
        [400, 400, 400, 400, 400, 400, 400, 300, 100]  # Visits for curve 1
    ]
    
    # Minimum number of weeks required for the analysis
    nb = 9
    
    # Farm prefix for SICPA data
    farm = "FR371783"
    
    # Extract and process data for each passage
    data, all_data = par_passage(zip_filename, Courbe, aliment, start_date, end_date)
    print("data par passage\n", data)
    
    # Save the passage data to a CSV file
    save_dataframe(data, r"data\DB_PAO.csv")

    # Process the data for each day
    data_day = par_jour(data, all_data, Courbe, conso_lait, visites)
    print("data par day\n", data_day)
    
    # Save the daily data to a CSV file
    save_dataframe(data_day, r"data\Statistiques.csv")

    # Prepare the data for SICPA export
    Sicpa = sicpa(data, farm)
    print("data for sicpa:\n", Sicpa)
    
    # Save the SICPA data to a CSV file
    save_dataframe(Sicpa, r"data\SICPA.csv")

    # Clean the daily data to retain only the required weeks
    complet = sem_comp_jour(data_day, nb)
    print("data exp sans semaine:\n", complet)
    
    # Save the cleaned data to a CSV file
    save_dataframe(complet, r"data\Semaines_completes.csv")
