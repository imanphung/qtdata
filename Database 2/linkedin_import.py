import glob
import os
import pandas as pd
import json
import time

from sqlalchemy.engine import create_engine
import gzip



#Server info
DIALECT = 'oracle'
SQL_DRIVER = 'cx_oracle'
USERNAME = 'DEV' #enter your username
PASSWORD = 'qtdata@2021' #enter your password
HOST = '118.69.32.128' #enter the oracle db host url
PORT = 1521 #enter the oracle port number
SERVICE = 'XE' #enter the oracle db service name
ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + \
                       ':' + str(PORT) + '/?service_name=' + SERVICE

print("SERVER INFO __ %s " % (ENGINE_PATH_WIN_AUTH)) 
engine = create_engine(ENGINE_PATH_WIN_AUTH, max_identifier_length = 128)
# con = engine.connect()

print('START IMPORTING DATABASE')
start_time = time.time()

#Get list of filenames
path = input("Please enter a path:\n")
#path = os.getcwd()
list_filename = []

for x in os.walk(path):
    for y in glob.glob(os.path.join(x[0], '*.gz')):
        list_filename.append(y)

#Convert .gz to dataframe        
header_list = ['path']
db_name = 'LINKEDIN_DB'

for filename in list_filename:
    start_filename = time.time()
    print("IMPORTING __ %s \n" % (filename))
    dict_list = []
    error_df = pd.DataFrame()

    f = gzip.open(filename, 'rt', encoding='utf-8')
    rawdata = f.readlines()
    header_list += list(json.loads((rawdata[0])).keys())
    f.close()
    
    for i in rawdata:
        dict_list.append(json.loads(i))
        
    header_list = list(dict.fromkeys(header_list))
    df = pd.DataFrame(dict_list, columns=header_list)
    df['path'] = filename

#a = [df[col].str.find("\u2019").any() for col in df.columns]
#b = df.education.str.find("\xe19")

    #Run with linkedin data
    for col in df.columns:
        try:
            if isinstance(df[col][0], str):
                df[col] = df[col].str.encode('utf-8')
            else:
                df[col] = df[col].astype(str)
#                df[col] = df[col].str.replace("\u2019", "'")
        except Exception as e:
            print(e, col)
            continue
    
    for index, row in df.iterrows():
        try:
            pd.DataFrame([row]).to_sql(db_name, engine, if_exists='append', index = False)
#            print('Row %s is imported' % (index))
        except Exception as e:
            print('IMPORTING ERROR __ ROW %s __ %s \n' % (index, e))
            error_df = error_df.append(row, sort = False)
            continue
    
    print('RUNNING TIME FOR DATABASE %s __ %s: %s seconds \n' % (db_name, filename, time.time() - start_filename))
    
    if len(error_df) > 0:
        error_path = path + '/error_data/{}.csv'.format(os.path.basename(filename).split('.')[0])
        error_df.to_csv(error_path)
        print('EXPORTING ERROR DATBASE __ %s \n' % (error_path))
    
print("--- TOTAL TIME RUN ALL %s seconds ---" % (time.time() - start_time))

#engine.execute('select * from {}'.format(db_name)).fetchall()
#engine.execute('drop table {}'.format(db_name))
