from numpy import nan
import pandas as pd
import zipfile
from datetime import datetime

def calculate_time_diff(cows_data , i):
    """
    calculate the amount of time the cows drank.
    args:
    - cows_data: data cleaned up to calculated the amount of time they drank.
    - i: row in the data set
    returns:
    - time in 00:00:00 format
    """
    #get the date/hours data of cows_data
    DStart = cows_data.loc[i,"Date_debut"]
    HStart = cows_data.loc[i,"Heure_debut"]
    DEnd = cows_data.loc[i,"Date_fin"]
    HEnd = cows_data.loc[i,"Heure_fin"]

    # combine the date and time into datetime
    start_datetime = datetime.strptime(DStart + " " + HStart, "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime(DEnd + " " + HEnd, "%Y-%m-%d %H:%M:%S")
    
    time_difference = end_datetime - start_datetime
    
    # format the time difference
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def generate_bande(date_str):
    """
    generate the value for "bande" columns by periode of time during the years
    args:
    - date_str: date from the data file of cow's birth to know the "bande".
    returns:
    - B2_XXXX or B1_XXXX
    """
    bande1_debut = (1, 1) #1st january
    bande1_fin = (6, 30)# 30th june

    bande2_debut = (7, 1)# 1st jully
    bande2_fin = (12, 31)# 31th decembre
    date = pd.to_datetime(date_str)
    mois_jour = (date.month, date.day)
    if bande1_debut <= mois_jour <= bande1_fin:
        return f'B2_{date.year}'
    elif bande2_debut <= mois_jour <= bande2_fin:
        return f'B1_{date.year}'

def animal_caract(zip_filename,start: str, end: str):
    """
    unzip brut data from the DAL to use file 00 and clean it.
    we clean the data by only keep the cows of the session giving by the start and end variables and sort them 
    to have the first part of DAL's data traitement.
    args:
    - zip_filename: the pass to the zip file.
    - start: date of the first birth of cow's session.
    - end: date of the last birth of cow's session.
    returns:
    - data files with id of cows( urban, UEPAO, date of birth, lot, bande)
    """
    
    rename_dict = {
    'tiere_id': 'URBAN_ID',
    'tier_nr': 'NUM',
    'geburtsdatum': 'Date_Naiss'
    }

    # unzip of DAL's brut data
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        with zipf.open('Export_instutut_export_nr_00.csv') as file:
            cows_id = pd.read_csv(file, delimiter=';')
    # rename columns we need
    cows_id.rename(columns=rename_dict, inplace=True)
    # only keep renamed columns
    cows_id = cows_id[list(rename_dict.values())]

    # convert start and end date strings to datetime.date
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    
    # convert 'Date_Naiss' column to datetime.date
    cows_id['Date_Naiss'] = pd.to_datetime(cows_id['Date_Naiss'], dayfirst=True).dt.date

    # filter rows in the DataFrame based on start and end dates
    filtered_cows_id = cows_id[(cows_id['Date_Naiss'] >= start_date) & (cows_id['Date_Naiss'] <= end_date)]

    # sort the DataFrame by 'Date_Naiss'
    filtered_cows_id = filtered_cows_id.sort_values(by='Date_Naiss', ascending=True)

    # fill Bande
    filtered_cows_id.insert(3, 'Bande', filtered_cows_id['Date_Naiss'].apply(generate_bande))

    return filtered_cows_id

def animal_data(zip_filename):
  """
  unzip brut data from the DAL to use file 03 and clean it.
  we clean the data by only keep data we need.
  args:
  - zip_filename: the pass to the zip file.
  returns:
  - data files with drink esurement of cows( )
  """

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

  # unzip of DAL's brut data
  with zipfile.ZipFile(zip_filename, 'r') as zipf:
      with zipf.open('Export_instutut_export_nr_03.csv') as file:
          cows_data = pd.read_csv(file, delimiter=';')

  # rename columns we need and keep them
  cows_data.rename(columns=rename_dict, inplace=True)
  cows_data = cows_data[list(rename_dict.values())]

  return cows_data

def pbp_data(zip_filename,start_date, end_date):# data for sigpa and other
    """
    make the first exel data sheet with data  for each passage of cows
    args:
    - zip_filename: path for the zip_file to extrac data.
    - start_date: date for the first birth of the set
    - end_date: date for the last birth of the set
    returns:
    - data set of all the cow with all the data
    """
    column_order = [
    "URBAN_ID", "NUM", "Bande", "Date_Naiss", "Age", "Semaine", "Sem",
    "Prog_lait", "Conso_lait", "Conso_mat1", "Conso_mat2", "Conso_eau",
    "Date_debut", "Heure_debut", "Date_fin", "Heure_fin", "Temps_buvee"
    ]

    # make the clean id data for each cows
    cows_id = animal_caract(zip_filename,start_date, end_date)
    #print("cows id:")
    #print(cows_id)

    # make the clean drink data for each cows
    cows_data = animal_data(zip_filename)
    #print("cows data:")
    #print(cows_data)

    # make the final sheet pass by pass
    merged_df = cows_data.merge(cows_id[['URBAN_ID', 'Date_Naiss', 'NUM', 'Bande']], on='URBAN_ID', how='left')

    #if columns is missing just fill it with none
    for col in column_order:
        if col not in merged_df.columns:
            merged_df[col] = None
    # reorganize the columns
    final_df = merged_df[column_order]
    # delete all the ligns were there is nan in columns NUM
    final_df = final_df.dropna(subset=['NUM'])
    # reset the index of the ligns
    final_df.reset_index(drop=True, inplace=True)
    # create the list of value to add them in cows_data
    age = []
    semaine = []
    sem = []
    time_diff = []

    for i in range(len(final_df)):
        # transform date into number of days 
        date_str1 = str(final_df.loc[i, "Date_Naiss"])
        date_str2 = final_df.loc[i, "Date_debut"]
        date1 = datetime.strptime(date_str1, '%Y-%m-%d')
        date2 = datetime.strptime(date_str2, '%Y-%m-%d')
        difference = date2 - date1
        nombre_de_jours = difference.days

        # list about the number of days/weeks since the cows were born
        age = age + [nombre_de_jours]
        semaine = semaine + [round(age[i]/7,1)]
        sem = sem + ["s"+str(int(semaine[i]+1))]
        # time the cows drank milk
        time_diff = time_diff + [calculate_time_diff(final_df , i)]

    # replace columns by the value
    final_df.loc[:, 'Age'] = age
    final_df.loc[:, 'Semaine'] = semaine
    final_df.loc[:, 'Sem'] = sem
    final_df.loc[:, 'Temps_buvee'] = time_diff

    # transforme NUM float into NUM int
    final_df['NUM'] = final_df['NUM'].astype(int)

    # sort the ligns by NUM then Semaine then Heure_debut
    final_df = final_df.sort_values(by=['NUM', 'Semaine',"Heure_debut"], ascending=[True, True, True])

    # reset the index of the ligns
    final_df.reset_index(drop=True, inplace=True)
    return final_df

def data_cleaned_without_week(df,list):
    """
    Garde la semaine composée de 7 jours de données
    et supprime les vaches que nous ne voulons pas pour l'expérience.
    args:
    - df: données du dataframe final complet mais non nettoyé.
    returns:
    - données finales à exporter sans semaine avec moins de 7 jours pour la moyenne
    """

    # Filtrer les vaches si elles ont moins de 100 valeurs
    df = df[(df.groupby('URBAN_ID')['URBAN_ID'].transform('count')) >= 190]

    # Initialiser un DataFrame vide pour stocker les données complètes
    df_complet = pd.DataFrame(columns=df.columns)

    # Groupement par NUM
    grouped = df.groupby('NUM')

    # Parcourir chaque groupe
    for num, group in grouped:
        # Vérifier chaque semaine unique dans le groupe
        for semaine in group['Sem'].unique():
            # Vérifier les âges présents dans cette semaine
            ages_presents = group[group['Sem'] == semaine]['Age'].unique()

            # Calculer les âges attendus pour une semaine complète
            if semaine == "s1":
                ages_attendus = range(3, int(semaine[1:]) * 7)
            else:
                ages_attendus = range((int(semaine[1:]) - 1) * 7, int(semaine[1:]) * 7)

            # Vérifier si tous les âges attendus sont présents
            if set(ages_attendus) == set(ages_presents):
                df_complet = pd.concat([df_complet, group[group['Sem'] == semaine]], ignore_index=True)
            else:
                #print(f"Semaine {semaine} n'est pas complète et sera ignorée pour NUM={num}.")
                pass
    df_complet = df_complet[list]
    return df_complet

def data_cleaned_with_week(df,list):# data for experiment with week error
    """
    delete cows we don't want for experiment
    args:
    - df: data of final_dataframe complet but not clean.
    returns:
    - final data to export them  with all the data week complete or not
    """
    # delete cows value if there is less than 100 value
    df = df[(df.groupby('URBAN_ID')['URBAN_ID'].transform('count')) >= 190]
    df = df[list]
    return df
    
def save_dataframe(df, chemin):# save csv in the path atribute
    """
    Sauvegarde le DataFrame dans un fichier CSV à l'emplacement spécifié.
    args:
    - df (pandas.DataFrame): Le DataFrame à sauvegarder.
    - chemin (str): Le chemin complet du fichier où sauvegarder le fichier CSV, y compris le nom du fichier.
    returns:
    - None
    """
    
    try:
        df.to_csv(chemin, index=False, sep=';')  # Utilisation du point-virgule comme séparateur
        print(f"DataFrame saved successfully to {chemin}")
    except PermissionError:
        print(f"Permission denied: You do not have permission to write to {chemin} le fichier dois etre ouvert.")
    except Exception as e:
        print(f"Error saving file: {str(e)}")

if __name__=="__main__":
    zip_filename = r'..\data\2024_06_03__10_12_02_touch01__csv_export.zip'  # file of DAL's data
    start_date = "2023-09-15"
    end_date = "2024-03-30"
    list1 = [
    "URBAN_ID", "NUM", "Bande", "Date_Naiss", "Age", "Semaine", "Sem",
    "Prog_lait", "Conso_lait", "Conso_mat1", "Conso_mat2", "Conso_eau",
    "Date_debut", "Heure_debut", "Date_fin", "Heure_fin", "Temps_buvee"
    ]
    data = pbp_data(zip_filename,start_date, end_date)
    data = data_cleaned_without_week(data,list1)
    print(data)
    save_dataframe(data,r"V1\data\pass_by_pass.csv")
