from sqlalchemy.engine import create_engine
import os, sys, subprocess
from datetime import datetime
import pandas as pd



#Database
db_temponote = 'qt_temponote'
db_tempomonitor = 'qt_tempomonitor'
db_memberinfo = 'qt_memberinfo'
db_weeklyreport = 'qt_weeklyreport'
db_functions = 'qt_functions'
db_tasks = 'qt_tasks'

#Tempo
timer_popup = 60 * 5
timer_exist = 60 * 4
timer_monitor = 10

monitor_style = 'all'

path_checkname = './modules/qt_tempo/list_checkname.txt'
path_media = os.getcwd() + '/modules/qt_bot/media/'
path_note = './modules/qt_tempo/notes/'
path_log = './log'

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
    engine = create_engine(engine_str, max_identifier_length = 128)
    
    return engine


def connect_jvnserver():
    DIALECT = 'oracle'
    SQL_DRIVER = 'cx_oracle'
    USERNAME = 'HRMS' #enter your username
    PASSWORD = 'qtdatA2020' #enter your password
#    HOST = '10.10.10.130' #enter the oracle db host url
    HOST = '14.161.28.178' #enter the oracle db host url
    PORT = 1521 #enter the oracle port number
    SERVICE = 'XE' #enter the oracle db service name
    engine_str = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + \
                           ':' + str(PORT) + '/' + SERVICE + '?encoding=UTF-8&nencoding=UTF-8'
    engine = create_engine(engine_str, max_identifier_length = 128)
    
    return engine

    
def load_userdata():        
    filesize = os.path.getsize('user.txt')
    if filesize == 0:
        user_data = open('user.txt', 'w')
        username = input('Enter your full name in UPPERCASE: ')
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
    
    df = pd.read_sql("select * from {} where FUNCTION like '{}'".format(db_functions, dependencies), ENGINE)
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
        

def init():
    #Check server connection
    try:
        ENGINE = connect_jvnserver()
        ENGINE.execute('select * from USERS')
        print('Connecting to JVN server.')
        print('-- START HRMSv2_Codebase --')
        server_status = 0
        
    except:
        try:
            ENGINE = connect_server()
            ENGINE.execute('select * from USERS')
            print('Connecting to qT server.')
            print('-- START HRMSv2_Codebase --')
            server_status = 0

        except:
            print('Error: Connection timed out!')
            print('-- START HRMSv2_Codebase offline --')
            ENGINE = 'No server'
            server_status = -1

    return ENGINE, server_status
    
#Main
ENGINE, server_status = init()
username = load_userdata()


  