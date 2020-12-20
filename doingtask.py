def ToDoItem(num, task):
    return [sg.Text(f'{num+1}. '), sg.CBox('',key= f'{num}'), sg.Text(f'{task}')]

def DoingItem(num, task):
    return [sg.Text(f'{num+1}. '), sg.Text(f'{task}'), sg.Button('Cancel',key= '-CANCEL-')]

def get_tasklist():
    
    #Comment next 2 lines or change the number if window size is too big/small
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 15))
    df = pd.read_sql("SELECT * FROM {} WHERE ASSIGNEE LIKE '{}' AND STATUS LIKE 'None'".format(utils.db_tasks, utils.username), utils.ENGINE)
    df.columns = [x.upper() for x in df.columns]
    layout = [ToDoItem(idx, df['TASK']) for idx, df in df.iterrows()] + [[sg.Button('Doing tasks', key= '-DOINGTASKS-'), sg.Button('Save', key= '-SAVE-'), sg.Button('Exit', key='-EXIT-')]]
    window = sg.Window(
        'New tasks',
        layout,
        disable_close = True,
        keep_on_top = True,
        finalize = True
    )
    while True:
        event, values = window.read(timeout = 500)
        # for idx, df in df.iterrows():
        #     if event == f'{idx}':

        if event == sg.TIMEOUT_KEY:
            continue    
        if event ==  '-SAVE-':
            for idx, df in df.iterrows():
                if values[f'{idx}'] == True:
                    df_doing_task = pd.DataFrame()
                    df_doing_task['ASSIGNER'] = [df['ASSIGNER']]
                    df_doing_task['ASSIGNEE'] = [df['ASSIGNEE']]
                    df_doing_task['TASK'] = [df['TASK']]
                    df_doing_task['DATE_MODIFIED'] = [datetime.now()]
                    df_doing_task['STATUS'] = ['doing']
                    utils.ENGINE.execute("delete from {} where to_char(ASSIGNEE) in '{}' and to_char(TASK) in '{}'".format(utils.db_tasks, utils.username, df['TASK']))
                    #Insert changed rows
                    df_doing_task.to_sql(utils.db_tasks, utils.ENGINE, if_exists = 'append', index = False)
                    break
            #window.FindElement(key).update(new_value)
        if event == '-EXIT-':
            window.Close()
            break
        if event == '-DOINGTASKS-':
            df_doing_task = pd.read_sql("SELECT * FROM QT_TASKS WHERE ASSIGNEE LIKE '{}' AND STATUS LIKE 'doing'".format(utils.username), utils.ENGINE)
            df_doing_task.columns = [x.upper() for x in df_doing_task.columns]
            layout = [DoingItem(idx, df_doing_task['TASK']) for idx, df_doing_task in df_doing_task.iterrows()] + [[sg.Button('Exit', key='-EXIT-')]]
        
            window_doing_task = sg.Window(
                'Doing tasks',
                layout,
                disable_close = True,
                keep_on_top = True,
                finalize = True
            )
            while True:
                event, values = window_doing_task.read(timeout = 500)
                if event == sg.TIMEOUT_KEY:
                    continue 
                if event == '-EXIT-':
                    window_doing_task.Close()
                    break
                if event == '-CANCEL-':
                    print(values[f'{idx}'])