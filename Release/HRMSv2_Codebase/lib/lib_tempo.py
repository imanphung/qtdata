import PySimpleGUI as sg
import pandas as pd
from datetime import datetime
    
import utils
from lib import lib_sys



def push_weeklyreport():
    path = lib_sys.get_filepath('xlsx')
    if path is None or len(path) == 0:
        return 'Weekly report uploaded failed!'
        
    df_report = pd.read_excel(path)
    df_report.columns = [x.upper() for x in df_report.columns]
    df_report['NAME'] = utils.username
    df_report['WEEK'] = utils.current_week
    df_report['DATE_MODIFIED'] = datetime.now()
#    df_report = df_report[['WEEK', 'NAME', 'ACTIVITIES', 'OUTCOMES', 'TODO', 'BIGACTION', 'DATE_MODIFIED']]
    
    utils.ENGINE.execute("delete from {} where NAME like '{}' and WEEK like {}".format(\
                        utils.db_weeklyreport, utils.username, utils.current_week))

    #Insert changed rows
    df_report.to_sql(utils.db_weeklyreport, utils.ENGINE, if_exists = 'append', index = False)
    
    return 'Weekly report uploaded successfully.'
    

def get_weeklyreport(name = 'all'):
    try:
        if name == 'all':
            df = pd.read_sql("select * from {}".format(utils.db_weeklyreport), utils.ENGINE)
            df.columns = [x.upper() for x in df.columns]
        
            path = sg.PopupGetFile(
                       'Save As',
                       no_window = True,
                       save_as = True,
                       default_extension = '.xlsx',
                       file_types = (('Excel Files', '*.xlsx'),)
                   )
            
            df.to_excel(path, index = False)
            return 'Weekly report downloaded successfully.'

    except:
        return 'Weekly report downloaded failed!'
        

def add_task(task, name_assignee):
    try:
        df_task = pd.DataFrame(columns = ['ASSIGNER','ASSIGNEE','TASK','DATE_MODIFIED', 'SUPERVISOR_COMMENT'])
        
        # Replacing data at each cell of the new row
        df_task['ASSIGNER'] = [utils.username]
        df_task['ASSIGNEE'] = name_assignee    
        df_task['TASK'] = task
        df_task['SUPERVISOR_COMMENT'] = ''
        df_task['DATE_MODIFIED'] = datetime.now()
            
        df_task.to_sql(utils.db_tasks, utils.ENGINE, if_exists = 'append', index = False)
        return 'Add task successfully.'
        
    except Exception as e:
        return 'Add task failed!'


def push_note():
    import os
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    
    #Connect GoogleDrive
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile('./config/mycreds.txt')
    
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
        
    gauth.SaveCredentialsFile('./config/mycreds.txt')
    drive = GoogleDrive(gauth)
    
    #Upload to Folder in GoogleDrive
    folder_id = '17uxf0cRba4JSpiWJgJ1Urr_u5NFpg7nS'
    filename = '{}_{}.json'.format(utils.username, utils.current_date.strftime('%d-%b-%y').upper())
    file_path = './modules/qt_tempo/' + filename
    file_id = None
    
    if os.path.exists(file_path):
        file_list = drive.ListFile({'q':"'{}'  in parents and trashed = False".format(folder_id)}).GetList()
        for x in range(len(file_list)):
            if file_list[x]['title'] == filename:
                file_id = file_list[x]['id']
                break
            
        if file_id:
            file = drive.CreateFile({
                'id': file_id,
                'title': filename
            })
            file.SetContentFile(file_path)
            file.Upload()
        else:
            file = drive.CreateFile({
                'parents': [{'id': folder_id}],
                'title': filename
            })
            file.SetContentFile(file_path)
            file.Upload()

            
            
  