import glob
import os, time
import pandas as pd
import json
import datetime
from sqlalchemy.engine import create_engine
import gzip
import cx_Oracle
import numpy as np

#304701
#Server Info
# dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='XE')
# conn = cx_Oracle.connect(user='DEV', password='qtdata@2021', dsn=dsn_tns)
# engine = conn.cursor()
#Server Info
DIALECT = 'oracle'
SQL_DRIVER = 'cx_oracle'
USERNAME = 'DEV' #enter your username
PASSWORD = 'qtdata@2021' #enter your password
HOST = 'localhost' #enter the oracle db host url
PORT = 1521 #enter the oracle port number
SERVICE = 'XE' #enter the oracle db service name
engine_str = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + \
                       ':' + str(PORT) + '/' + SERVICE + '?encoding=UTF-8&nencoding=UTF-8'
engine = create_engine(engine_str, max_identifier_length = 128)
print('Connecting to server.')

dict_list = []
header_list = []
log = ''
linkedin_df = pd.read_csv('linkedin_data.csv')
linkedin_df['status'] = linkedin_df['status'].astype(str)

for index,row in linkedin_df.iterrows():
	filename = row['name']
	if index in range(82,93):
		print(filename)