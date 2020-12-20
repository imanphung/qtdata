from sqlalchemy.engine import create_engine
import os, sys, subprocess
from datetime import datetime
import pandas as pd
import shutil
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pygsheets


#Database
company = 'qt'
db_temponote = company + '_temponote'
db_tempomonitor = company + '_tempomonitor'
db_memberinfo = company + '_memberinfo'
db_weeklyreport = company + '_weeklyreport'
db_function = company + '_function'
db_task = company + '_task'
db_action = company + '_action'
db_todo = company + '_todo'
db_department = company + '_department'
db_file = company + '_file'
db_recommendation = company + '_recommendation'
#Tempo
timer_popup = 60*5
timer_action = 60*60
timer_exist = 60*2
timer_monitor = 30
timer_thumbsup = 60*4

monitor_style = 'all'

path_checkname = './modules/tempo/list_checkname.txt'
path_media = os.getcwd() + '/modules/bot/media/'
path_note = './modules/tempo/notes/'
path_log = './log/'
path_backup = './backup/'
path_icon = './config/icon/'
path_sound = './config/sound/'
path_config = './config/'
path_output = './ouput/'

#Init
current_date = datetime.now().date()
current_week = datetime.now().isocalendar()[1]
root = os.getcwd()

#Make dirs
if not os.path.exists(path_media):
    os.makedirs(path_media)

if not os.path.exists(path_note):
    os.makedirs(path_note)

if not os.path.exists(path_log):
    os.makedirs(path_log)
    
    
def connect_server():
    #Server Info
    DIALECT = 'oracle'
    SQL_DRIVER = 'cx_oracle'
    USERNAME = 'DEV' #enter your username
    PASSWORD = 'qtdatA2020' #enter your password
    HOST = '118.69.32.128' #enter the oracle db host url
    PORT = 1521 #enter the oracle port number
    SERVICE = 'ORCLCDB' #enter the oracle db service name
    engine_str = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + \
                           ':' + str(PORT) + '/' + SERVICE + '?encoding=UTF-8&nencoding=UTF-8'
    engine = create_engine(engine_str, max_identifier_length = 128, pool_use_lifo = True, pool_pre_ping = True)
    
    return engine


def connect_jvnserver():
    DIALECT = 'oracle'
    SQL_DRIVER = 'cx_oracle'
    USERNAME = 'HRMSv2' #enter your username
    PASSWORD = 'qtdatA2020' #enter your password
#    HOST = '10.10.10.130' #enter the oracle db host url
    HOST = '14.161.28.178' #enter the oracle db host url
    PORT = 1521 #enter the oracle port number
    SERVICE = 'XE' #enter the oracle db service name
    engine_str = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + \
                           ':' + str(PORT) + '/' + SERVICE + '?encoding=UTF-8&nencoding=UTF-8'
    engine = create_engine(engine_str, max_identifier_length = 128, pool_use_lifo = True, pool_pre_ping = True)
    
    return engine

    
def load_userdata():        
    filesize = os.path.getsize('user.txt')
    if filesize == 0:
        user_data = open('user.txt', 'w')
        username = input('Enter your CODE: ')
        username = username.replace('\n', '')
        user_data.write(username)
        user_data.close()

    else:
        user_data = open('user.txt', 'r')
        username = user_data.readline()
        username = username.replace('\n', '')
        user_data.close()
        
    return username


def install_missingmodules():
    print('Checking for missing modules.')
    
    if sys.platform != 'win32':
        dependencies = 'mac_requirements.txt'
    else:
        dependencies = 'requirements.txt'
    
    file = open(dependencies, 'r')
    lines = file.readlines()
    file.close()
    local_modules = [s.replace('\n', '') for s in lines]
    
    df = pd.read_sql("select * from {} where FUNCTION like '{}'".format(db_function, dependencies), ENGINE)
    df.columns = [x.upper() for x in df.columns]
    server_modules = df['CONTENT'][0]
    server_modules = server_modules.split('\n')
    
    new_modules =  list(set(server_modules) - set(local_modules))
    
    for mod in new_modules:          
        try:
            # implement pip as a subprocess:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '{}'.format(mod)])
            file = open(dependencies, 'a')
            file.write('\n' + mod)
            file.close()
            print("'{}': Module installs successfully.".format(mod))
            
        except Exception as e:
            print("'{}': Module installs failed.\n{}".format(mod, e))
            continue
        

def init(username):
    #Check server connection
    try:
        ENGINE = connect_server()
        folder_id = ENGINE.execute("select FOLDER_ID from {} where CODE like '{}'"
            .format(db_memberinfo, username)).fetchall()[0][0]
        print('Connecting to qT server.')
        print('-- START HRMSv2_Codebase --')
        server_status = 1
        
        # print('Error: Connection timed out!')
        # print('-- START HRMSv2_Codebase offline --')
        # ENGINE = 'No server'
        # server_status = -1
        # folder_id = 'None'
        
    except:
        try:
            ENGINE = connect_jvnserver()
            folder_id = ENGINE.execute("select FOLDER_ID from {} where CODE like '{}'"\
                .format(db_memberinfo, username)).fetchall()[0][0]
            print('Connecting to JVN server.')
            print('-- START HRMSv2_Codebase --')
            server_status = 1
        except:
            print('Working offline!')
            print('-- START HRMSv2_Codebase offline --')
            ENGINE = 'No server'
            server_status = -1
            folder_id = 'None'

    return ENGINE, server_status, folder_id

    
def delete_oldbackup():
    list_folder = []

    for folder in os.listdir(path_backup):
        try:
            folder_time = datetime.strptime(folder,'%Y-%m-%dT%H%M%S')
            list_folder.append(folder_time)
            
        except:
            continue
        
    list_folder.sort()
    for i in list_folder[:-1]: #Keep latest backup
        if i.isocalendar()[1] < current_week - 1:
            deleted_folder = path_backup + '{}'.format(i.strftime('%Y-%m-%dT%H%M%S'))
            shutil.rmtree(deleted_folder, ignore_errors = True)
                 

def get_credentials():
    creds = None
    # If modifying these scopes, delete the file token.pickle.'
    SCOPES = ['https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets',
    ]
    
    try:
        if os.path.exists(path_config + 'token.pickle'):
            with open('./config/token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                
            else:
                flow = InstalledAppFlow.from_client_secrets_file(path_config + 'credentials.json', SCOPES)
                creds = flow.run_local_server(port = 0)
                
            # Save the credentials for the next run
            with open(path_config + 'token.pickle', 'wb') as token:
                pickle.dump(creds, token)
                
        return creds
        
    except Exception:
        return Exception

def check_my_level(name):
    level_checked = pd.read_sql("select CLASS from {} where CODE like '{}'"\
                 .format(db_memberinfo, name), ENGINE)['class'][0]
    my_level = pd.read_sql("select CLASS from {} where CODE like '{}'"\
                     .format(db_memberinfo, username), ENGINE)['class'][0]
    if int(my_level) > int(level_checked):
        return 0
    return 1

# drive_service = build('drive', 'v3', credentials = get_credentials())
# ss_service = build('sheets', 'v4', credentials = get_credentials())
# gc = pygsheets.authorize(custom_credentials = get_credentials())
                     
#Main
username = load_userdata()
ENGINE, server_status, folder_id = init(username)
delete_oldbackup()

  