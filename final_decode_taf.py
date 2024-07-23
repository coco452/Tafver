import re
from datetime import datetime, timedelta
import itertools
import pandas as pd
import numpy as np

cloud = ['FEW','SCT','BKN','OVC','CB','TCU']

def extract_metada(taf):
    sep_taf = taf.split()
    special = ['AMD' , 'COR']

    if sep_taf[1] in special:
        airport = sep_taf[2]
        date_validity = sep_taf[4]
        wind = sep_taf[5]
        visibility = 9999 if sep_taf[6]=='CAVOK' else sep_taf[6]
    else:
        airport = sep_taf[1]
        date_validity = sep_taf[3]
        wind = sep_taf[4]
        visibility = 9999 if sep_taf[5]=='CAVOK' else sep_taf[5]
   
    return airport , date_validity , wind, visibility

taf_data = "TAF AMD SADF 231140Z 2312/2412 02005KT 0300 FG OVC002 TX20/2318Z TN14/2410Z TEMPO 2312/2314 0100 FG OVC001 BECMG 2314/2316 8000 BKN010 BECMG 2321/2323 09010KT 5000 BR BKN008 BECMG 2403/2405 0800 FG OVC004"

airport , date_validity , wind , visibility = extract_metada(taf_data)

start_day = date_validity[:2]
start_hour = date_validity[2:4]
end_day = date_validity[5:7]
end_hour = date_validity[7:9]

def generate_datetime_list(start, end):
    start_day = int(start[:2])
    start_hour = int(start[2:])
    end_day = int(end[:2])
    end_hour = int(end[2:])
    
    month = datetime.now().month
    year = datetime.now().year
    
    start_date = datetime(year, month, start_day, start_hour)
    end_date = datetime(year, month, end_day, end_hour)
    
    if end_day < start_day:
        end_date = end_date.replace(month=month + 1)
    
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(hours=1)
    
    return date_list

date_list = generate_datetime_list(start_day+start_hour, end_day+end_hour)

rows = list(range(25))
df = pd.DataFrame(None, index=rows, columns=['Airport', 'Date', 'Wind_dir', 'Wind_int', 'Visibility', 'Phen', 'Cloud_cover_1', 'Cloud_height_1', 'Cloud_cover_2', 'Cloud_height_2', 'Cloud_cover_3', 'Cloud_height_3'])
df.loc[:,'Airport']= airport
df.loc[:,'Date']= date_list[:]
df.loc[:,'Wind_dir'] = wind[:3]
df.loc[:,'Wind_int'] = wind[3:5]
df.loc[:,'Visibility'] = visibility

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

IDX_TX=index_tx(taf_split)[0]
taf_ini = taf_split[:IDX_TX[0]]

idx_wind = [i for i, x in enumerate(taf_ini) if x.endswith('KT')]
taf_mid = taf_ini[idx_wind[0]:]

idx_cloud = [i for i, x in enumerate(taf_mid) if x.startswith(('SCT','FEW','BKN','OVC'))]
print(idx_cloud)
def index_tx(taf_split):
    idx_tx = [i for i, x in enumerate(taf_split) if x.startswith('TX')]
    idx_tn = [i for i, x in enumerate(taf_split) if x.startswith('TN')]
    return idx_tx, idx_tn

IDX_TX = index_tx(taf_split)[0]
taf_ini = taf_split[:IDX_TX[0]]

idx_wind = [i for i, x in enumerate(taf_ini) if x.endswith('KT')]
taf_mid = taf_ini[idx_wind[0]:]

idx_cloud = [i for i, x in enumerate(taf_mid) if x.startswith(('SCT','FEW','BKN','OVC'))]

idx_phen = [i for i, x in enumerate(taf_mid) if any(sub in x for sub in ('RA', 'BR', 'FG', 'DZ', 'SH', 'SN', 'BL', 'DU', 'VC', 'MI','NSW'))]
if idx_phen:
    phen = taf_mid[idx_phen[0]]
    df.loc[:, 'Phen'] = phen

if not idx_cloud:
    df.loc[:,'Cloud_cover_1'] = "NSC"
    df.loc[:,'Cloud_height_1'] = None
    df.loc[:,'Cloud_cover_2'] = "NSC"
    df.loc[:,'Cloud_height_2'] = None
    df.loc[:,'Cloud_cover_3'] = "NSC"
    df.loc[:,'Cloud_height_3'] = None
else:
    for idx in range(len(idx_cloud)):
        cloud_cover = taf_mid[idx_cloud[idx]]
        df.loc[:,f'Cloud_cover_{idx+1}'] = cloud_cover[:3]
        df.loc[:,f'Cloud_height_{idx+1}'] = cloud_cover[3:]

def index_changes(taf_split):
    idx_becmg = [i for i, x in enumerate(taf_split) if x.startswith('BECMG')]
    idx_tempo = [i for i, x in enumerate(taf_split) if x.startswith('TEMPO')]
    idx_prob = [i for i, x in enumerate(taf_split) if x.startswith('PROB')]
    idx_changes = idx_becmg + idx_tempo + idx_prob 
    idx_changes.sort()
    return idx_changes, idx_becmg, idx_tempo, idx_prob

def update_taf(taf_change, df, end_day, end_hour):
    print(f'Processing change: {taf_change}')
    date_change = taf_change[0]
    start_day = date_change[:2]
    start_hour = date_change[2:4]

    date_list = generate_datetime_list(start_day + start_hour, end_day + end_hour)
    start_idx = (df['Date'] < date_list[0]).sum()

    idx_wind = [i for i, x in enumerate(taf_change) if x.endswith('KT')]
    if idx_wind:
        wind = taf_change[idx_wind[0]]
        df.loc[start_idx+1:, 'Wind_dir'] = wind[:3]
        df.loc[start_idx+1:, 'Wind_int'] = wind[3:5]
   
    idx_cloud = [i for i, x in enumerate(taf_change) if x.startswith(('SCT','FEW','BKN','OVC'))]
    print(f'Cloud indices: {idx_cloud}')
    if idx_cloud:
        for idx in range(len(idx_cloud)):
            cloud_cover = taf_change[idx_cloud[idx]]
            df.loc[start_idx+1:, f'Cloud_cover_{idx+1}'] = cloud_cover[:3]
            df.loc[start_idx+1:, f'Cloud_height_{idx+1}'] = cloud_cover[3:]

    idx_phen = [i for i, x in enumerate(taf_change) if any(sub in x for sub in ('RA', 'BR', 'FG', 'DZ', 'SH', 'SN', 'BL', 'DU', 'VC', 'MI','NSW'))]
    if idx_phen:
        phen = taf_change[idx_phen[0]]
        df.loc[start_idx+1:, 'Phen'] = phen

    visibility = [element for element in taf_change if len(element) == 4 and element.isdigit()]
    if visibility:
        df.loc[start_idx+1:, 'Visibility'] = visibility[0]
    
    idx_cavok = [i for i, x in enumerate(taf_change) if 'CAVOK' in x]
    if idx_cavok:
        df.loc[start_idx+1:, 'Visibility'] = 9999
        df.loc[start_idx+1:, 'Phen'] = 'NSW'
        df.loc[start_idx+1:, 'Cloud_cover_1'] = 'NSC'
        df.loc[start_idx+1:, 'Cloud_height_1'] = None
        df.loc[start_idx+1:, 'Cloud_cover_2'] = 'NSC'
        df.loc[start_idx+1:, 'Cloud_height_2'] = None
        df.loc[start_idx+1:, 'Cloud_cover_3'] = 'NSC'
        df.loc[start_idx+1:, 'Cloud_height_3'] = None

    return df

idx_changes, idx_becmg, idx_tempo, idx_prob = index_changes(taf_split)

for k in range(len(idx_becmg)):
    if k != len(idx_becmg) - 1:
        taf_change = taf_split[idx_becmg[k] + 1 : idx_becmg[k + 1]]
    else:
        taf_change = taf_split[idx_becmg[k] + 1 :]
    df = update_taf(taf_change, df, end_day, end_hour)

print(df)
