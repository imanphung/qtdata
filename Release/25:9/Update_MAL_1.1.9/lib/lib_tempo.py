import PySimpleGUI as sg
import pandas as pd
import sys
import traceback
from datetime import datetime
    
import utils
from lib import lib_sys
from logger import log_debugger


def add_task(project, task, content, name_assignee, team, start_date, end_date):
    try:
        df = pd.DataFrame(
            columns = ['DATE_MODIFIED', 'PROJECT', 'TASK', 'CONTENT', 'STATUS',
                'ASSIGNER', 'ASSIGNEE', 'TEAM', 'ISSUE', 'SOLUTION', 
                'SUPERVISOR_COMMENT', 'START_DATE', 'END_DATE', 'NOTE']
        )
        
        # Replacing data at each cell of the new row
        df['DATE_MODIFIED'] = [datetime.now()]
        df['PROJECT'] = project    
        df['TASK'] = task        
        df['CONTENT'] = content
        df['STATUS'] = 'Open'
        
        df['ASSIGNER'] = utils.username
        df['ASSIGNEE'] = name_assignee
        df['TEAM'] = team
        df['ISSUE'] = 'None'
        df['SOLUTION'] = 'None'
        
        df['SUPERVISOR_COMMENT'] = 'None'
        df['START_DATE'] = datetime.strptime(start_date, '%d-%b-%y')
        df['END_DATE'] = datetime.strptime(start_date, '%d-%b-%y')
        df['NOTE'] = 'None'
            
        df.to_sql(utils.db_task, utils.ENGINE, if_exists = 'append', index = False)
        return 'Add task successfully.'
        
    except Exception as e:
        return 'Add task failed!'


def make_table_task(name):
    df = pd.read_sql(
        "select * from {} where ASSIGNEE like '{}'".format(utils.db_task, name), utils.ENGINE)
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
    
    
def get_task(name = utils.username):
    df_task = make_table_task(name)
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
                
                utils.ENGINE.execute("delete from {} where ASSIGNEE like '{}'".format(utils.db_task, name))
                df_task.to_sql(utils.db_task, utils.ENGINE, if_exists = 'append', index = False)
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
                return 'Done'
            
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
        
        
def create_window_recommendations():
    sg.theme('TanBlue')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 15))
        
    layout = [
        [sg.Text('3 Recommendations')],
        [sg.Multiline(key = '-RECOMMENDATION-', size = (45, 10))],
        [sg.Submit(key = '-SUBMIT-')]
    ]
    
    window = sg.Window(
        'Recommendations List',
        layout,
        keep_on_top = True,
        finalize = True
    )
    
    return window

def add_recommendations():
    window = create_window_recommendations()

    while True:
        try:
            event, values = window.read(timeout = 100)
            if event == sg.TIMEOUT_KEY:
                tp_recommendation = values['-RECOMMENDATION-']
                pass
            if len(tp_recommendation.replace('\n','')) > 0 and event == '-SUBMIT-':
                if int(utils.server_status) == 0:
                    df_todo = pd.DataFrame([{
                        'DATETIME': datetime.now(),
                        'TIME': datetime.now().strftime('%H:%M:%S'),
                        'NAME': utils.username,
                        'RECOMMENDATION': tp_recommendation,
                    }])
                    print(df_todo)
                    df_todo.to_sql(utils.db_recommendation, utils.ENGINE, if_exists = 'append', index = False)
                    
                window.Hide()
                window.Close()
                return 'Done'
            
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