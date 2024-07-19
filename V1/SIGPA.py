import zipfile
import pandas as pd
from datetime import datetime, timedelta
from data_pass_by_pass import pbp_data,save_dataframe

def data_accepted(zip_filename,start_date, end_date):

    colonnes_a_garder = ['URBAN_ID','NUM', 'Date_debut', 'Heure_debut','TYPE', 'Conso_lait']
    rename_dict = {
        'NUM': 'ANIMAL',
        'Date_debut': 'DATE',
        'Heure_debut': 'HEURE',
        'Conso_lait': 'QUANTITE'
    }
    
    # extract the complete data
    data = pbp_data(zip_filename,start_date, end_date)
    # create missing columns
    data['TYPE'] = 'Offert'
    # keep data we need
    data = data[colonnes_a_garder]
    # round consomation data
    data['Conso_lait'] = data['Conso_lait'].astype(float).round(2)
    # rename columns we need
    data.rename(columns=rename_dict, inplace=True)
    data = data.sort_values(by='URBAN_ID', ascending=True)
    # reset the index of the ligns
    data.reset_index(drop=True, inplace=True)
    return data

def data_global(zip_filename,start: str):
    rename_dict = {
    'tiere_id': 'URBAN_ID',
    'erste_erkennung_datum': 'DATE',
    'erste_erkennung_zeit': 'HEURE'
    }

    # unzip of DAL's brut data
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        with zipf.open('Export_instutut_export_nr_01.csv') as file:
            data = pd.read_csv(file, delimiter=';')
    # rename columns we need
    data.rename(columns=rename_dict, inplace=True)
    # only keep renamed columns
    data = data[list(rename_dict.values())]

    # convert start and end date strings to datetime.date
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    
    # convert 'Date_Naiss' column to datetime.date
    data['DATE'] = pd.to_datetime(data['DATE'], dayfirst=True).dt.date

    # filter rows in the DataFrame based on start and end dates
    filtered_data = data[(data['DATE'] >= start_date)]
    filtered_data = filtered_data.sort_values(by=['URBAN_ID','DATE'], ascending=True)
    # reset the index of the ligns
    filtered_data.reset_index(drop=True, inplace=True)
    return filtered_data

def data_for_sigpa(zip_filename,start_date, end_date,aliment,Farming):
    colonnes_a_garder = ['ANIMAL', 'ALIMENT', 'DATE', 'HEURE', 'TYPE', 'QUANTITE']
    # collect data accepted and all the passage of cow
    data_accept = data_accepted(zip_filename,start_date, end_date)
    data = data_global(zip_filename,start_date)
    # put the animal number in all the data
    data = pd.merge(data, data_accept[['URBAN_ID', 'ANIMAL']], on='URBAN_ID', how='left')
    #clear duplicate ligns due to merge
    data = data.drop_duplicates()
    # reset the index of the ligns
    data.reset_index(drop=True, inplace=True)
    # clear ligns with nan in animal columns
    data = data.dropna(subset=['ANIMAL'])
    # put columns HEURE and DATE to the same format by replacing 24H by 00H and transforme it to datetime
    data['HEURE'] = data['HEURE'].replace('24:00:00', '00:00:00')
    data_accept['HEURE'] = data_accept['HEURE'].replace('24:00:00', '00:00:00')
    data['DATE'] = pd.to_datetime(data['DATE'])
    data_accept['DATE'] = pd.to_datetime(data_accept['DATE'])
    data['HEURE'] = pd.to_datetime(data['HEURE'], format='%H:%M:%S').dt.time
    data_accept['HEURE'] = pd.to_datetime(data_accept['HEURE'], format='%H:%M:%S').dt.time
    # put the Offert and QUANTITE on the ligns where it's the same date in the two files
    data = pd.merge(data, data_accept[['URBAN_ID', 'DATE', 'HEURE', 'TYPE', 'QUANTITE']], 
                       on=['URBAN_ID', 'DATE', 'HEURE'], how='left')
    # fill nan part of TYPE columns by REFUS
    data['TYPE'] = data['TYPE'].fillna('Refus')
    # fill nan part of QUANTITE columns by 0
    data['QUANTITE'] = data['QUANTITE'].fillna('')
    #create the column ALIMENT
    data['ALIMENT'] = aliment
    # put animal numbers to integer
    data['ANIMAL'] = data['ANIMAL'].astype(int)
    data['ANIMAL'] = data['ANIMAL'].apply(lambda x: Farming + str(x))
    #keep columns we want
    data = data[colonnes_a_garder]
    
    # classifie the data
    data = data.sort_values(by=['ANIMAL','DATE','HEURE'], ascending=True)
    # convert DATE column to 'dd/hh/yyyy' format
    data['DATE'] = data['DATE'].dt.strftime('%d/%m/%Y')
    # convert HEURE column to 'hh:mm' format
    data['HEURE'] = data['HEURE'].apply(lambda x: x.strftime('%H:%M'))
    # reset the index of the ligns
    data.reset_index(drop=True, inplace=True)
    
    return data
"""
#to automize data transformation but this take all the data and the dal keep all data from the begining
def autorun(zip_filename,extract_path,name):
    start_date="2000-01-01"

    # add 10 years
    day = datetime.today() + timedelta(days=365*10)

    # convert to format yyyy-mm-dd
    day = day.strftime('%Y-%m-%d')
    data = data_for_sigpa(zip_filename,start_date, day,"PAO-2021-001-COC","FR371783")
    save_dataframe(data,extract_path+"\ " + name)
 """   
if __name__=="__main__":
    zip_filename = r'..\data\2024_06_03__10_12_02_touch01__csv_export.zip'  # file of DAL's data
    start_date = "2023-09-15"
    end_date = "2024-03-30"
    aliment = "PAO-2021-001-COC"
    #data=data_global(zip_filename,start_date)
    data = data_for_sigpa(zip_filename,start_date, end_date,aliment,"FR371783")
    print(data)
    save_dataframe(data,r"V1\data\sigpa.csv")

