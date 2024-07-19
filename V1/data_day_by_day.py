import pandas as pd
from data_pass_by_pass import pbp_data,save_dataframe
from SIGPA import data_global


def data_dbd(df, conso_lait, visites,list):
    # Convert str to time
    df['Temps_buvee'] = pd.to_timedelta(df['Temps_buvee'])
    # Group by 'NUM', 'Bande', 'Age', 'Sem' and sum 'Conso_lait' and 'Temps_buvee'
    grouped = df.groupby(['URBAN_ID','NUM', 'Bande','Date_debut', 'Age', 'Sem']).agg({
        'Conso_lait': 'sum',
        'Temps_buvee': 'sum'
    }).reset_index()

    # Theoretical values provided by the user
    grouped['Conso_lait_theorique'] = float('nan')
    
    # Fill the 'Conso_lait_theorique' column with values from conso_lait
    for i in range(len(conso_lait)):
        sem_label = f's{i+1}'
        grouped.loc[grouped['Sem'] == sem_label, 'Conso_lait_theorique'] = conso_lait[i]
    
    grouped['Visites_theoriques'] = float('nan')
    
    # Fill the 'Visites_theoriques' column with values from visites
    for i in range(len(visites)):
        sem_label = f's{i+1}'
        grouped.loc[grouped['Sem'] == sem_label, 'Visites_theoriques'] = visites[i]

    # Count the number of times the cows go to the DAL and can drink
    counts = df.groupby(['NUM', 'Age']).size().reset_index(name='count')
    grouped = pd.merge(grouped, counts, on=['NUM', 'Age'], how='left').rename(columns={'count': 'Nombre_de_visites'})
    
    # Difference between theoretical values and actual data
    grouped['Ecart_conso_lait'] = grouped['Conso_lait_theorique'] - grouped['Conso_lait']
    grouped['Ecart_visites'] = grouped['Nombre_de_visites'] - grouped['Visites_theoriques']
    
    # Format the sum result of 'Temps_buvee'
    grouped['Temps_buvee_total'] = grouped['Temps_buvee'].apply(lambda x: '{:02}:{:02}:{:02}'.format(int(x.total_seconds() // 3600), int((x.total_seconds() // 60) % 60), int(x.total_seconds() % 60)))
    # Keep and order the necessary columns
    grouped = grouped[['URBAN_ID','NUM', 'Bande','Date_debut', 'Age', 'Sem', 'Conso_lait', 'Conso_lait_theorique', 'Ecart_conso_lait', 'Temps_buvee_total', 'Nombre_de_visites', 'Visites_theoriques', 'Ecart_visites']]
    
    # Rename 'Age' column to 'JOUR'
    grouped = grouped.rename(columns={'Age': 'JOUR'})
    # get the number of denied passage besause of no right
    total = data_global(zip_filename,start_date)
    total['DATE'] = pd.to_datetime(total['DATE'])
    total = total.groupby(['URBAN_ID', 'DATE']).size().reset_index(name='Nb_Reffus')
    grouped = grouped.rename(columns={'Date_debut': 'DATE'})
    grouped['DATE'] = pd.to_datetime(grouped['DATE'])
    grouped = pd.merge(grouped, total, on=['DATE', 'URBAN_ID'], how='left')
    grouped['Nb_Reffus']=grouped['Nb_Reffus']-grouped['Nombre_de_visites']
    print(grouped)
    # Round numeric values to two decimal places
    grouped['Conso_lait_theorique'] = grouped['Conso_lait_theorique'].astype(float).round(2)
    grouped['Ecart_conso_lait'] = grouped['Ecart_conso_lait'].astype(float).round(2)
    grouped['Ecart_visites'] = grouped['Ecart_visites'].astype(int).round(2)
    grouped['Conso_lait'] = grouped['Conso_lait'].astype(float).round(2)
    grouped = grouped[list]
    return grouped

if __name__=="__main__":
    zip_filename = r'..\data\2024_06_03__10_12_02_touch01__csv_export.zip'  # file of DAL's data
    start_date = "2023-09-15"
    end_date = "2024-03-30"
    nb_week = 9
    conso_lait = [4, 5, 6, 7, 7, 7, 6, 5, 2.5]
    visites = [4,4,4,4,4,4,4,3,1]
    list=["URBAN_ID","NUM", "Bande","DATE", "JOUR", "Sem", "Conso_lait", "Conso_lait_theorique",
               "Ecart_conso_lait", "Temps_buvee_total", "Nombre_de_visites",
               "Visites_theoriques", "Ecart_visites","Nb_Reffus"]
    df = pbp_data(zip_filename,start_date, end_date)
    data = data_dbd(df,conso_lait, visites,list)
    print(data)
    save_dataframe(data,r"V1\data\day_by_day.csv")
