import re
from datetime import datetime, timedelta
import itertools
import pandas as pd
import numpy as np

def extract_metada(taf):
    sep_taf = taf.split()
    len_taf = len(sep_taf)

    type_message = sep_taf[0]
    special = ['AMD' , 'COR', 'CAVOK']

    if sep_taf[1] in special:
        airport = sep_taf[2]
        date_validity = sep_taf[4]
        wind = sep_taf[5]
        visibility = 9999
    else:
        airport = sep_taf[1]
        date_validity = sep_taf[3]
        wind = sep_taf[4]
        visibility[5]
    return airport , date_validity , wind, visibility
taf_data = "TAF COR SABE 041700Z 0418/0518 30005KT 9999 SCT010 OVC030 TX04/0418Z TNM06/0511Z BECMG 0420/0422 36005KT 9999 NSW SCT030 OVC060 BECMG 0512/0514 VRB05KT 9999 SHSN BKN025 OVC050"

airport , date_validity , wind ,visibility = extract_metada(taf_data)

start_day = date_validity[:2]
start_hour = date_validity[2:4]

end_day = date_validity[5:7]
end_hour = date_validity[7:9]

print(start_day,start_hour,end_day,end_hour)

def generate_datetime_list(start, end):
    # Extract month and day from start and end
    start_day = int(start[:2])
    start_hour = int(start[2:])
    end_day = int(end[:2])
    end_hour = int(end[2:])
    
    # Assume both dates are in the same month
    month = datetime.now().month
    year = datetime.now().year
    
    # Define the start and end datetime objects
    start_date = datetime(year, month, start_day, start_hour)
    end_date = datetime(year, month, end_day, end_hour)
    
    # Handle month wrapping (e.g., end date in the next month)
    if end_day < start_day:
        end_date = end_date.replace(month=month + 1)
    
    # Create a list to store the datetime objects
    date_list = []

    # Generate the list of datetime objects incrementing by one hour
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(hours=1)

    # Print the results

    for date in date_list:
        print(date.strftime('%d%H'))
    return date_list

date_list = generate_datetime_list(start_day+start_hour,end_day+end_hour)
print(date_list)
rows = list(range(25))
df = pd.DataFrame(np.nan, index = rows, columns= ['Airport', 'Date', 'Wind_dir','Wind_int', 'Visibility', 'Phen', 'Cloud_cover_1', 'Cloud_height_1','Cloud_cover_2', 'Cloud_height_2','Cloud_cover_3', 'Cloud_height_3'])
df['Airport'][:]=airport
df['Date'][:] = date_list[:]
df['Wind_dir'][:] = wind[:3]
df['Wind_int'][:] = wind[3:5]
print(df)
taf_split = taf_data.split()

def index_tx(taf_split):
    # Encuentra los índices donde comienza con TX y TN
    # Esta función solamente funciona si el taf ya se encuentra convertido en una lista

    idx_tx = [i for i, x in enumerate(taf_split) if x.startswith('TX')]
    idx_tn = [i for i, x in enumerate(taf_split) if x.startswith('TN')]
    return idx_tx , idx_tn

def index_changes(taf_split):
    # Encuentra los índices donde comienza con BECMG
    # Esta función solamente funciona si el taf ya se encuentra convertido en una lista

    idx_becmg = [i for i, x in enumerate(taf_split) if x.startswith('BECMG')]
    idx_tempo = [i for i, x in enumerate(taf_split) if x.startswith('TEMPO')]
    idx_prob = [i for i, x in enumerate(taf_split) if x.startswith('PROB')]
    idx_changes = idx_becmg + idx_tempo + idx_prob 
    idx_changes.sort()
    return idx_changes, idx_becmg , idx_tempo , idx_prob


idx_becmg = [i for i, x in enumerate(taf_split) if x.startswith('BECMG')]
idx_tempo = [i for i, x in enumerate(taf_split) if x.startswith('TEMPO')]
print(len(idx_tempo))
print(len(idx_becmg))
list_idx_changes = idx_becmg+idx_tempo
list_idx_changes.sort()

taf_change = taf_split[list_idx_changes[0]+1:list_idx_changes[1]-1]
idx_wind = [i for i, x in enumerate(taf_change) if x.endswith('KT')]
idx_cloud = [i for i, x in enumerate(taf_change) if x.startswith(('SCT','FEW','BKN','OVC'))]
visibility = [element for element in taf_change if len(element) == 4 and element.isdigit()]

date_change = taf_change[0]
wind = taf_change[idx_wind[0]]
cloud_cover = taf_change[idx_cloud[0]]
print(cloud_cover)
start_day = date_change[:2]
start_hour = date_change[2:4]

date_list = generate_datetime_list(start_day+start_hour,end_day+end_hour)
start_idx = (df['Date'] < date_list[0]).sum()
df['Wind_dir'][start_idx+1:24] = wind[:3]
df['Wind_int'][start_idx+1:24] = wind[3:5]

df['Cloud_cover_1'][start_idx+1:24] = cloud_cover[:3]
df['Cloud_height_1'][start_idx+1:24] = cloud_cover[3:]
df['Visibility'][start_idx+1:24] = visibility[0]

#print(start_day,start_hour,end_day,end_hour)
print(df)

#HASTA AHORA FECHAS Y AEROPUERTO#