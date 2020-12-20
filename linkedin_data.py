import glob
import os
import pandas as pd
import json
import datetime
from sqlalchemy.engine import create_engine
import gzip
import cx_Oracle
import numpy as np

# Server Info
# dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='XE')
# conn = cx_Oracle.connect(user='DEV', password='qtdata@2021', dsn=dsn_tns)
# engine = conn.cursor()

list_filename = ['ds_dump_AS_1.jl.gz', 'ds_dump_AW_1.jl.gz']

#for y in glob.glob(os.path.join('*.gz')):
#    list_filename.append(y)
print(list_filename)

dict_list = []
header_list = []
log = ''
for filename in list_filename[:1]:
    try:
        #import json to dataframe
        start = datetime.datetime.now()
        f = gzip.open(filename, 'rt', encoding='utf-8')
        log += 'File name: ' + filename + '\n'
        rawdata = f.readlines()
        header_list += list(json.loads((rawdata[0])).keys())
        f.close()
        for i in rawdata:
            dict_list.append(json.loads(i))
        header_list = list(dict.fromkeys(header_list))
        upload_time = datetime.datetime.now()
        df = pd.DataFrame(dict_list, columns=header_list)
        finish = datetime.datetime.now()
        convert_time = (finish - start).total_seconds()
        log += 'Convert time: ' + str(convert_time) + '\n'
        
        #format values
        df.columns = [x.upper() for x in df.columns]
        df_report = pd.DataFrame()
        if 'FAMILY_NAME' in df.columns: df_report['FAMILY_NAME'] = df['FAMILY_NAME']
        else: df_report['FAMILY_NAME'] = np.nan
        if 'FULL_NAME' in df.columns: df_report['FULL_NAME'] = df['FULL_NAME']
        else: df_report['FULL_NAME'] = np.nan
        if 'GIVEN_NAME' in df.columns: df_report['GIVEN_NAME'] = df['GIVEN_NAME']
        else: df_report['GIVEN_NAME'] = np.nan
        if 'LOCALITY' in df.columns: df_report['LOCALITY'] = df['LOCALITY']
        else: df_report['LOCALITY'] = np.nan
        if 'URL' in df.columns: df_report['URL'] = df['URL']
        else: df_report['URL'] = np.nan
        if 'EDUCATION' in df.columns: df_report['EDUCATION'] = df['EDUCATION']
        else: df_report['EDUCATION'] = np.nan
        if 'INDUSTRY' in df.columns: df_report['INDUSTRY'] = df['INDUSTRY']
        else: df_report['INDUSTRY'] = np.nan
        if 'LAST_VISITED' in df.columns: df_report['LAST_VISITED'] = df['LAST_VISITED']
        else: df_report['LAST_VISITED'] = np.nan
        if 'NUM_CONNECTIONS' in df.columns: df_report['NUM_CONNECTIONS'] = df['NUM_CONNECTIONS']
        else: df_report['NUM_CONNECTIONS'] = np.nan
        if 'EXPERIENCE' in df.columns: df_report['EXPERIENCE'] = df['EXPERIENCE']
        else: df_report['EXPERIENCE'] = np.nan
        if 'HEADLINE' in df.columns: df_report['HEADLINE'] = df['HEADLINE']
        else: df_report['HEADLINE'] = np.nan
        if 'ALSO_VIEWED' in df.columns: df_report['ALSO_VIEWED'] = df['ALSO_VIEWED']
        else: df_report['ALSO_VIEWED'] = np.nan
        if 'IMAGE_URL' in df.columns: df_report['IMAGE_URL'] = df['IMAGE_URL']
        else: df_report['IMAGE_URL'] = np.nan
        if 'REDIRECT_URL' in df.columns: df_report['REDIRECT_URL'] = df['REDIRECT_URL']
        else: df_report['REDIRECT_URL'] = np.nan
        if 'CANONICAL_URL' in df.columns: df_report['CANONICAL_URL'] = df['CANONICAL_URL']
        else: df_report['CANONICAL_URL'] = np.nan
        if 'UNIQUE_ID' in df.columns: df_report['UNIQUE_ID'] = df['UNIQUE_ID']
        else: df_report['UNIQUE_ID'] = np.nan
        if '_KEY' in df.columns: df_report['KEY'] = df['_KEY']
        else: df_report['KEY'] = np.nan
        df_report = df_report.astype(str)
        df_report['DATE_UPLOADED'] = upload_time
        
        #push data into oracle
        log += 'Upload time: ' + str(upload_time) + '\n'
        rows = [tuple(x) for x in df_report[:1].values]
        # engine.executemany('INSERT INTO LINKEDIN_DB (FAMILY_NAME, FULL_NAME, GIVEN_NAME, URL,\
        #                                 EDUCATION, INDUSTRY, LAST_VISITED, NUM_CONNECTIONS,\
        #                                 EXPERIENCE, HEADLINE, ALSO_VIEWED, "IMAGE_URL",\
        #                                 REDIRECT_URL, CANONICAL_URL, UNIQUE_ID, KEY, DATE_UPLOADED)\
        #                                 VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17)',rows)
        
        # conn.commit()
        #df_report[:1].to_sql('LINKEDIN_DB', engine, if_exists='append', index = False)
        log += 'Upload successfully\n'
        # reset
        dict_list = []
        header_list = []
    except:
        log += 'Upload failed: ' + filename + '\n'
print(log)
with open("log.txt", "a") as logfile:
    logfile.write(log)
    logfile.close()
#conn.close()