from datetime import datetime
import pandas as pd
from utils import calculate_time_diff, data_global, animal_caract, animal_data

def par_passage(zip_filename, courbe, aliment, start_date="2000-01-01", end_date="3000-01-01"):
    """
    Create the first Excel data sheet with data for each passage of cows.
    Args:
    - zip_filename: Path to the zip file to extract data.
    - courbe: List of curves.
    - aliment: List of corresponding feeds.
    - start_date: Start date for the data extraction.
    - end_date: End date for the data extraction.
    Returns:
    - DataFrame containing all cow data with relevant details.
    """
    # Define the order of columns for the final DataFrame
    column_order = [
        "URBAN_ID", "NUM", "Bande", "Courbe", "ALIMENT", "Date_Naiss", "Age", "Semaine", "Sem",
        "Prog_lait", "Conso_lait", "Conso_mat1", "Conso_mat2", "Conso_eau",
        "Date_debut", "Heure_debut", "Date_fin", "Heure_fin", "Temps_buvee"
    ]

    # Create the cleaned ID data for each cow
    cows_id = animal_caract(zip_filename, start_date, end_date)

    # Create the cleaned drink data for each cow
    cows_data = animal_data(zip_filename)

    # Merge drink data with cow ID data
    final_df = cows_data.merge(cows_id[['URBAN_ID', 'Date_Naiss', 'Courbe', 'NUM', 'Bande']], on='URBAN_ID', how='left')

    # Remove rows where 'NUM' column has NaN values
    final_df = final_df.dropna(subset=['NUM'])

    # Initialize lists to store calculated values
    age = []
    semaine = []
    sem = []
    time_diff = []

    for index, row in final_df.iterrows():
        # Calculate age in days
        date1 = row["Date_Naiss"]
        date2 = datetime.strptime(row["Date_debut"], '%Y-%m-%d').date()
        difference = date2 - date1
        nombre_de_jours = difference.days

        # Append calculated values to the lists
        age.append(nombre_de_jours)
        semaine.append(round(age[-1] / 7, 1))
        sem.append("s" + str(int(semaine[-1] + 1)))
        time_diff.append(calculate_time_diff(row))

    # Assign the calculated values to the DataFrame
    final_df['Age'] = age
    final_df['Semaine'] = semaine
    final_df['Sem'] = sem
    final_df['Temps_buvee'] = time_diff
    
    final_df['ALIMENT'] = ""
    courbe_to_aliment = dict(zip(courbe, aliment))
    final_df['ALIMENT'] = final_df['Courbe'].map(courbe_to_aliment)

    # Convert 'NUM' from float to int
    final_df['NUM'] = final_df['NUM'].astype(int)

    # Sort the DataFrame by 'NUM', 'Semaine', and 'Heure_debut'
    final_df = final_df.sort_values(by=['NUM', 'Semaine', "Heure_debut"], ascending=[True, True, True])

    # Reorganize the columns according to the defined order
    final_df = final_df[column_order]

    # Reset the index of the DataFrame
    final_df.reset_index(drop=True, inplace=True)
    
    # Get the global data
    all = data_global(zip_filename, start_date)

    return final_df, all

def par_jour(grouped, all, COURBE, conso_lait, visites):
    """
    Aggregate data on a per-day basis.
    Args:
    - grouped: DataFrame containing grouped data.
    - all: DataFrame containing all data.
    - COURBE: List of curves.
    - conso_lait: List of theoretical milk consumption values.
    - visites: List of theoretical visit counts.
    Returns:
    - Aggregated DataFrame with daily data.
    """
    # Define columns to keep
    keep_columns = ['NUM', 'Bande', 'ALIMENT', 'JOUR', 'Sem', 'Conso_lait', 'Conso_lait_theorique',
                    'Ecart_conso_lait', 'Temps_buvee_total', 'Nombre_de_visites', 'Visites_theoriques',
                    'Ecart_visites', 'Nb_sans_droit']

    # Convert 'Temps_buvee' to timedelta
    grouped['Temps_buvee'] = pd.to_timedelta(grouped['Temps_buvee'])

    # Aggregate data by 'URBAN_ID', 'NUM', 'Courbe', 'ALIMENT', 'Bande', 'Date_debut', 'Age', and 'Sem'
    counts = grouped
    grouped = grouped.groupby(['URBAN_ID', 'NUM', 'Courbe', 'ALIMENT', 'Bande', 'Date_debut', 'Age', 'Sem']).agg({
        'Conso_lait': 'sum',
        'Temps_buvee': 'sum'
    }).reset_index()

    # Count the number of visits
    counts = counts.groupby(['NUM', 'Age']).size().reset_index(name='count')
    grouped = pd.merge(grouped, counts, on=['NUM', 'Age'], how='left').rename(columns={'count': 'Nombre_de_visites'})

    # Function to extract the week index from 'Sem'
    def get_week_index(sem):
        return int(sem[1:]) - 1  # Extract the index (s1 -> 0, s2 -> 1, etc.)

    # Fill 'Conso_lait_theorique' and 'Visites_theoriques' columns
    for i, courbe in enumerate(COURBE):
        mask = grouped["Courbe"] == courbe
        for index, row in grouped[mask].iterrows():
            week_index = get_week_index(row["Sem"])
            if week_index < len(conso_lait[i]) and week_index < len(visites[i]):
                grouped.at[index, "Conso_lait_theorique"] = conso_lait[i][week_index]
                grouped.at[index, "Visites_theoriques"] = visites[i][week_index]

    # Calculate differences between theoretical and actual values
    grouped['Ecart_conso_lait'] = grouped['Conso_lait_theorique'] - grouped['Conso_lait']
    grouped['Ecart_visites'] = grouped['Nombre_de_visites'] - grouped['Visites_theoriques']

    # Format 'Temps_buvee' to HH:MM:SS
    grouped['Temps_buvee'] = grouped['Temps_buvee'].apply(lambda x: '{:02}:{:02}:{:02}'.format(
        int(x.total_seconds() // 3600), int((x.total_seconds() // 60) % 60), int(x.total_seconds() % 60)))
    
    # Round numeric values to three decimal places
    grouped['Conso_lait_theorique'] = grouped['Conso_lait_theorique'].astype(float).round(3)
    grouped['Ecart_conso_lait'] = grouped['Ecart_conso_lait'].astype(float).round(3)
    grouped['Ecart_visites'] = grouped['Ecart_visites'].astype(int).round(2)
    grouped['Conso_lait'] = grouped['Conso_lait'].astype(float).round(3)

    # Rename 'Age' to 'JOUR' and 'Temps_buvee' to 'Temps_buvee_total'
    grouped = grouped.rename(columns={'Age': 'JOUR', 'Temps_buvee': 'Temps_buvee_total'})

    # Process the 'all' DataFrame for refusals
    all['DATE'] = pd.to_datetime(all['DATE'])
    all = all.groupby(['URBAN_ID', 'DATE']).size().reset_index(name='Nb_sans_droit')
    grouped = grouped.rename(columns={'Date_debut': 'DATE'})
    grouped['DATE'] = pd.to_datetime(grouped['DATE'])
    grouped = pd.merge(grouped, all, on=['DATE', 'URBAN_ID'], how='left')
    grouped['Nb_sans_droit'] = grouped['Nb_sans_droit'] - grouped['Nombre_de_visites']

    # Keep only specified columns
    grouped = grouped[keep_columns]
    
    return grouped

if __name__ == "__main__":
    zip_filename = r'donnees\2024_06_03__10_12_02_touch01__csv_export.zip'
    start_date = "2023-09-15"
    end_date = "2024-03-30"
    Courbe = [6, 5, 1]
    aliment = ['pao 001', 'pao 002', 'pao 003']
    
    conso_lait = [
        [4, 5, 6, 7, 7, 7, 6, 5, 2.5],
        [40, 50, 60, 70, 70, 70, 60, 50, 20.5],
        [400, 500, 600, 700, 700, 700, 600, 500, 200.5]
    ]
    visites = [
        [4, 4, 4, 4, 4, 4, 4, 3, 1],
        [40, 40, 40, 40, 40, 40, 40, 30, 10],
        [400, 400, 400, 400, 400, 400, 400, 300, 100]
    ]
    data,all_data = par_passage(zip_filename,Courbe,aliment, start_date, end_date)
    print("data par passage\n",data)
    data = par_jour(data,all_data,Courbe, conso_lait, visites)
    print("data par day\n",data)
    #save_dataframe(data,r"DAL\V3\test.csv")
    pass
