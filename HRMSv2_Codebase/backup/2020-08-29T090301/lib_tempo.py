def add_todo():
    window = create_window_todo()

    while True:
        try:
            event, values = window.read(timeout = 100)
            if event == sg.TIMEOUT_KEY:
                tp_outcomes = values['-OUTCOMES-']
                tp_todo = values['-TODO-']
                pass

            if len(tp_outcomes.replace('\n','')) > 0 and len(tp_todo.replace('\n','')) > 0 and event == '-SUBMIT-':
                if int(utils.server_status) == 0:
                    df_todo = pd.DataFrame([{
                        'DATETIME': datetime.now(),
                        'TIME': datetime.now().strftime('%H:%M:%S'),
                        'NAME': utils.username,
                        'OUTCOMES': tp_outcomes,
                        'TODO': tp_todo
                    }])
                    print(df_todo)
                    df_todo.to_sql(utils.db_todo, utils.ENGINE, if_exists = 'append', index = False)
                    
                window.Hide()
                window.Close()
                break
            
            if event == sg.WIN_CLOSED:
                window.Close()
                break
    
        except UnicodeDecodeError:
            pass     
        
        except KeyboardInterrupt:
            pass
                        
        except:
            log_debugger.warning(traceback.format_exc())
            window.Close()
            break
import PySimpleGUI as sg
import pandas as pd
import sys
import traceback
from datetime import datetime
    
import utils
from lib import lib_sys
from logger import log_debugger



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
                        

def add_task(project, task, content, name_assignee):
    try:
        df = pd.DataFrame(
            columns = ['ASSIGNER', 'ASSIGNEE', 'PROJECT', 'TASK', 'CONTENT', 'STATUS',
                       'DATE_MODIFIED', 'ISSUE', 'SOLUTION', 'SUPERVISOR_COMMENT', 'TOTAL_TIME'])
        
        # Replacing data at each cell of the new row
        df['ASSIGNER'] = [utils.username]
        df['ASSIGNEE'] = name_assignee
        df['PROJECT'] = project    
        df['TASK'] = task        
        df['CONTENT'] = content
        df['STATUS'] = 'Open'
        
        df['DATE_MODIFIED'] = datetime.now()
        df['ISSUE'] = 'None'
        df['SOLUTION'] = 'None'
        df['SUPERVISOR_COMMENT'] = 'None'
        df['TOTAL_TIME'] = 0
            
        df.to_sql(utils.db_tasks, utils.ENGINE, if_exists = 'append', index = False)
        return 'Add task successfully.'
        
    except Exception as e:
        return 'Add task failed!'


def make_table(name):
    df = pd.read_sql(
        "select * from {} where ASSIGNEE like '{}'".format(utils.db_tasks, name), utils.ENGINE)
    df.columns = [x.upper() for x in df.columns]
    
    return df


def create_window_task(data, header):
    sg.theme('LightGreen')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))      
    
    layout = [
        [sg.Table(
            key = '-TABLE-',
            values = data,
            headings = header,
            max_col_width = 25,
            auto_size_columns = True,
            display_row_numbers = True,
            justification = 'right',
            num_rows = 10,
            alternating_row_color = 'white',
            row_height = 35
        )],
        [
            sg.Button('Choose'),
            sg.Button('Modify')
        ]
    ]
    
    window = sg.Window(
        'List of Tasks',
        layout,
        keep_on_top = True
    )

    return window
    

def get_listtask(name = utils.username):
    df_task = make_table(name)
    data = df_task.values.tolist()
    header = df_task.columns.tolist()
    window = create_window_task(data, header)
    task = ''
    
    while True:
        try:
            event, values = window.read()        
            if event == 'Choose':
                task_index = values.get('-TABLE-')[0]
                df_task.loc[df_task['STATUS'] == 'In Progress', 'STATUS'] = 'Pending'
                df_task.loc[task_index, 'STATUS'] = 'In Progress'
                
                utils.ENGINE.execute("delete from {} where ASSIGNEE like '{}'".format(utils.db_tasks, name))
                df_task.to_sql(utils.db_tasks, utils.ENGINE, if_exists = 'append', index = False)
                task = df_task.loc[task_index, 'TASK']
                
                window.Close()
                
            elif event == 'Modify':
                print(event, values)
                
            if event == sg.WIN_CLOSED:
                window.close()
                break
            
        except UnicodeDecodeError:
            pass     
        
        except KeyboardInterrupt:
            pass
        
        except:
            log_debugger.warning(traceback.format_exc())
            window.Close()
            break
    
    return "'{}': Task is selected.".format(task)
        

def create_window_todo():
    sg.theme('TanBlue')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 15))
        
    layout = [
        [sg.Text('Today Outcomes')],
        [sg.Multiline(key = '-OUTCOMES-', size = (45, 5))],
        [sg.Text('To Do')],
        [sg.Multiline(key = '-TODO-', size = (45, 5))],
        [sg.Submit(key = '-SUBMIT-')]
    ]
    
    window = sg.Window(
        'To Do List',
        layout,
        keep_on_top = True,
        finalize = True
    )
    
    return window
    
