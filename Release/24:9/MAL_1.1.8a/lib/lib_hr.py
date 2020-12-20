import PySimpleGUI as sg
from datetime import datetime
import os
import pandas as pd
from PIL import Image
import io
import base64
import time
import imageio
import cv2
import utils
from lib import lib_sys
        

def create_department():
    mal_id = utils.ENGINE.execute("select ID from {} where DEPARTMENT like '{}'"\
            .format(utils.db_department, utils.company + '-MAL')).fetchall()[0][0]
    df = pd.read_sql('select * from {}'.format(utils.db_department), utils.ENGINE)
    df.columns = [x.upper() for x in df.columns]

    for idx, dept_name in enumerate(df['DEPARTMENT']):
        if df.loc[idx, 'ID'] == 'None':
            file_metadata = {
                'name': dept_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [mal_id]
            }
            dept_id = utils.drive_service.files().create(body = file_metadata, fields = 'id').execute()['id']
            df['ID'].iloc[idx] = dept_id

    df.to_sql(utils.db_department, utils.ENGINE, if_exists = 'replace', index = False)


def create_workingspace_by_email(email, alias, dept_id):
    '''
    Create workingspace '<emailID>_<Alias>'.
    Add permission to edit.
    '''
    emailID = email.split('@')[0]

    #Create folder
    file_metadata = {
        'name': emailID + "_" + alias,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [dept_id]
        }
    folder_id = utils.drive_service.files().create(body = file_metadata, fields = 'id').execute()['id']

    #Create notes
    file_document_metadata = {
        'mimeType': 'application/vnd.google-apps.document',
        'name': emailID + "_" + alias + '_notes',
        'parents': [folder_id]
    }
    utils.drive_service.files().create(body = file_document_metadata).execute()['id']

    #Create sheets
    file_spreadsheet_metadata = {
        'mimeType': 'application/vnd.google-apps.spreadsheet',
        'name': emailID + "_" + alias + '_sheets',
        'parents': [folder_id]
    }
    utils.drive_service.files().create(body = file_spreadsheet_metadata).execute()['id']
    
    #Update id in member info
    utils.ENGINE.execute("update {} set FOLDER_ID = '{}' where EMAIL like '{}'".format(utils.db_memberinfo, folder_id, email))
    
    #Add permission
    workingspace_permission = {
        'emailAddress': email,
        'type': 'user',
        'role': 'writer'
    }
    utils.drive_service.permissions().create(fileId = folder_id, body = workingspace_permission).execute()


def create_workingspace():
    #Get members info
    df_info = pd.read_sql('select * from {}'.format(utils.db_memberinfo), utils.ENGINE)
    df_info.columns = [x.upper() for x in df_info.columns]
    #Get dept id
    df_dept = pd.read_sql('select * from {}'.format(utils.db_department), utils.ENGINE)
    df_dept.columns = [x.upper() for x in df_dept.columns]
                       
    for idx, email in enumerate(df_info['EMAIL']):
        if email != 'None' and df_info.loc[idx, 'FOLDER_ID'] == 'None':
            try:
                dept_name = df_info.loc[idx, 'DEPARTMENT']
                dept_id = df_dept.loc[df_dept['DEPARTMENT'] == dept_name, 'ID'].values[0]
                dept_permission = {
                    'emailAddress': email,
                    'type': 'user',
                    'role': 'reader'
                }
                utils.drive_service.permissions().create(fileId = dept_id, body = dept_permission).execute()

                alias = df_info.loc[idx, 'ALIAS']
                create_workingspace_by_email(email, alias, dept_id)
                
            except: 
                print(email)

#http://eyana.me/list-gdrive-folders-python/
def list_spreadsheet_by_folderid(folder_id):
    results = utils.drive_service.files().list(q = "mimeType='application/vnd.google-apps.spreadsheet' and parents in '"\
        + folder_id + "' and trashed = false", fields = "nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    
    return items

    
def list_folder_by_folderid(folder_id):
    results = utils.drive_service.files().list(q = "mimeType='application/vnd.google-apps.folder' and parents in '"\
        + folder_id + "' and trashed = false", fields = "nextPageToken, files(id, name)", pageSize = 400).execute()
    items = results.get('files', [])
        
    return items
    
    
def create_window_browser(items):
    treedata = sg.TreeData()      
    for idx, value in enumerate(items):    
        treedata.Insert('', value['name'], value['name'], values = value['id'])
    
    layout = [
        [sg.Text('Select File')],
        [sg.Tree(data = treedata, headings = ['ID'], auto_size_columns = True,
            num_rows = 20, col0_width = 30, key = '-TREE-', show_expanded = False)],
        [sg.Button('Choose')]
    ]

    window = sg.Window(
        'File Browser',
        layout,
        keep_on_top = True
    )
    
#    print(window.Element('-TREE-').TreeData.tree_dict[values['-TREE-'][0]].values)
    return window

    
def read_spreadsheet(spreadsheet_id):
    if spreadsheet_id == 'None':
        path = lib_sys.get_filepath('xlsx')
        if path is None or len(path) == 0:
            return 'No file selected.'
        
        df = pd.read_excel(path, sheetname = None)
        
        return df
    else:
        sh = utils.gc.open_by_key(spreadsheet_id)
        
        return sh


def get_memberinfo(status = 'all'):
    try:
        if status in ['in', 'temp', 'pending', 'out']:
             df = pd.read_sql("select * from {} where STATUS like '{}'".format(utils.db_memberinfo, status), utils.ENGINE)
        else:
            df = pd.read_sql("select * from {}".format(utils.db_memberinfo), utils.ENGINE)
        df.columns = [x.upper() for x in df.columns]
                      
        memberinfo_id = utils.ENGINE.execute("select ID from {} where FILENAME like '{}'"\
            .format(utils.db_file, utils.company + '-Memberinfo')).fetchall()[0][0]
        sh = utils.gc.open_by_key(memberinfo_id)
        wks = sh[0]
        wks.clear()
        wks.set_dataframe(df, 'A1')
        
        return "Members' Info downloaded successfully."
        
    except:
        return "Members' Info downloaded failed!"
    
    
def push_memberinfo():
    try:
        memberinfo_id = utils.ENGINE.execute("select ID from {} where FILENAME like '{}'"\
            .format(utils.db_file, utils.company + '-Memberinfo')).fetchall()[0][0]
        sh = utils.gc.open_by_key(memberinfo_id)
        wks = sh[0]
        df = wks.get_as_df()
        df.columns = [x.upper() for x in df.columns]
                      
        df['DATE_MODIFIED'] = datetime.now()
        df['NAME_MODIFIED'] = utils.username
        df['STARTDATE'] = pd.to_datetime(df['STARTDATE'])
        df['OUTDATE'] = pd.to_datetime(df['OUTDATE'])
                 
        df.to_sql(utils.db_memberinfo, utils.ENGINE, if_exists = 'replace', index = False)    
    
        return "Members' Info uploaded successfully."
        
    except:
        return "Members' Info uploaded failed!"

def get_dailyreport(username = utils.username, date = utils.current_date.strftime('%Y-%m-%d')):
    level_result = utils.check_my_level(username)
    if level_result == 0:
        return "You are not allowed to check on this member"
    else:
        date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%y').upper()
        path = utils.path_output + '{}_{}/'.format(date, username)
        if not os.path.exists(path):
            os.makedirs(path)
            
        df_note = pd.read_sql("select * from {} where NAME like '{}' and DATETIME like '{}'"\
            .format(utils.db_temponote, username, date), utils.ENGINE)
        df_note.columns = [x.upper() for x in df_note.columns]
        df_note.sort_values(by='DATETIME', inplace=True, ascending=True)
        df_note = df_note[['DATETIME', 'TIME', 'NAME', 'OUTCOME', 'NEXTACT']]
    
        df_action = pd.read_sql("select * from {} where NAME like '{}' and DATETIME like '{}'"\
            .format(utils.db_action, username, date), utils.ENGINE)
        df_action.columns = [x.upper() for x in df_action.columns]
        df_action.sort_values(by='DATETIME', inplace=True, ascending=True)
        df_action['NUMLIKE'] = df_action['THUMBSUP'].str.split(', ').apply(len)
        df_action = df_action[['DATETIME', 'TIME', 'NAME', 'ACTION', 'ACTIVITIES', 'OUTCOMES', 'THUMBSUP', 'NUMLIKE']]
        
    
        df_todo = pd.read_sql("select * from {} where NAME like '{}' and DATETIME like '{}'"\
            .format(utils.db_todo, username, date), utils.ENGINE)
        df_todo.columns = [x.upper() for x in df_todo.columns]
        df_todo['NUMTODO'] = df_todo['TODO'].str.rstrip().str.split('\n').apply(len)
        df_todo = df_todo[['DATETIME', 'TIME', 'NAME', 'OUTCOMES', 'TODO', 'NUMTODO']]
    
        #Note summary
        note_duplicate, note_empty, note_nonsense, note_stat = summarize_tempo(df_note, 'NEXTACT', 5)
            
        #Action summary
        action_duplicate, action_empty, action_nonsense, action_stat = summarize_tempo(df_action, 'ACTION', 10)
        activity_duplicate, activity_empty, activity_nonsense, activity_stat = summarize_tempo(df_action, 'ACTIVITIES', 10)
        outcome_duplicate, outcome_empty, outcome_nonsense, outcome_stat = summarize_tempo(df_action, 'OUTCOMES', 10)
        
        #Duplicate details
        act_stat = pd.concat([action_stat, activity_stat, outcome_stat], axis = 1)
        act_duplicate = pd.concat([action_duplicate, activity_duplicate, outcome_duplicate], axis = 1)
    
        writer = pd.ExcelWriter(
            path + 'dailyreview_{}.xlsx'.format(datetime.now().strftime('%H%M%S'))
        )
        row_start = 0
        col_start = 0
        df_todo.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
        row_start += len(df_todo) + 2
        df_action.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
        row_start += len(df_action) + 2
        df_note.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
    
        row_start = 0
        col_start = 10
        note_stat.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
        row_start += len(note_stat) + 2
        note_duplicate.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
        row_start += len(note_duplicate) + 2
        act_stat.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
        row_start += len(act_stat) + 2
        act_duplicate.to_excel(writer, sheet_name = username, startrow = row_start, startcol = col_start, index = False)
        
        writer.save()
    
        return 'View in output directory'


def get_image(username = utils.username, date = utils.current_date.strftime('%Y-%m-%d')):
    level_result = utils.check_my_level(username)
    if level_result == 0:
        return "You are not allowed to check on this member"
    else:
        date = datetime.strptime(date, '%Y-%m-%d').strftime('%d-%b-%y').upper()
        path = utils.path_output + '{}_{}/'.format(date, username)
        if not os.path.exists(path):
            os.makedirs(path)
        
        df = pd.read_sql("select * from {} where NAME like '{}' and DATETIME like '{}'"\
                 .format(utils.db_tempomonitor, username, date), utils.ENGINE)
        df.columns = [x.upper() for x in df.columns]
        df.sort_values(by='DATETIME', inplace=True, ascending=True)
        #    if len(df) > num_image:
        #        df = df.sample(num_image).sort_values('DATETIME')
        #    for idx in df.index:
        #        frame = Image.open(io.BytesIO(base64.b64decode(df.loc[idx,'WEBCAM'])))
        #        frame.save(
        #            path + '{}_webcam.png'.format(df.loc[idx,'TIME'].replace(':', ''))
        #        )
        #        
        #        screen = Image.open(io.BytesIO(base64.b64decode(df.loc[idx,'SCREEN'])))
        #        screen.save(
        #            path + '{}_screen.png'.format(df.loc[idx,'TIME'].replace(':', ''))
        #        )
        date_position = (20,10)
        with imageio.get_writer( path +'webcams_screens.gif', mode='I', fps=5) as writer_screen:
            for idx, row in df.iterrows():
                screen = imageio.imread(base64.b64decode(row['SCREEN']))
                webcam = imageio.imread(base64.b64decode(row['WEBCAM']))
                concat_image = cv2.hconcat([webcam,screen])
                cv2.putText(
                 concat_image, #numpy array on which text is written
                 "{}".format(row['DATETIME']), #text
                 date_position, #position at which writing has to start
                 cv2.FONT_HERSHEY_SIMPLEX, #font family
                 0.4, #font size
                 (0,0,255)
                 )
                writer_screen.append_data(concat_image)
        writer_screen.close()
        
        return 'View in output directory'

def summarize_tempo(df, column_name, nonsense_value):
    try:
        df_duplicate = df.pivot_table(index = [column_name], aggfunc = 'size')
        df_duplicate = pd.DataFrame(df_duplicate[df_duplicate >= 2])
        df_duplicate.columns = ['{}_Duplicate'.format(column_name)]
        df_duplicate.reset_index(inplace = True)
    except:
        df_duplicate = pd.DataFrame(columns = [
            '{}'.format(column_name),     
            '{}_Duplicate'.format(column_name)
        ])
    
    df[column_name] = df[column_name].str.strip()
    df_empty = df[(df[column_name].isna()) | (df[column_name] == '')]

    df_nonsense = df[df[column_name].str.len() <= nonsense_value]
    
    df_stat = pd.DataFrame()
    df_stat['{}_Duplicate'.format(column_name)] = [len(df_duplicate)]
    df_stat['{}_Empty'.format(column_name)] = len(df_empty)
    df_stat['{}_NonSense'.format(column_name)] = len(df_nonsense)
    
    return df_duplicate, df_empty, df_nonsense, df_stat


def get_time_use(name = None):   
#    trường hợp 1
    if name is not None:
        df = pd.read_sql("SELECT qt_temponote.name,qt_memberinfo.code,qt_temponote.datetime \
        FROM {} INNER JOIN {} on to_char(qt_memberinfo.code) = to_char(qt_temponote.name)\
        where DATETIME in (select min(DATETIME) from {} where name like '{}')"\
        .format(utils.db_memberinfo,utils.db_temponote,utils.db_temponote,name),utils.ENGINE)
        
#    trường hợp 2
    if name is None:
        df = pd.read_sql("SELECT SUBQUERY.NAME code,{}.NAME name,\
        (SELECT min(DATETIME) FROM {} WHERE NAME LIKE SUBQUERY.NAME )DATETIME\
        FROM (SELECT DISTINCT to_char(NAME)NAME FROM {}) SUBQUERY\
        join {} on to_char({}.code) = SUBQUERY.NAME"\
        .format(utils.db_memberinfo,utils.db_temponote,utils.db_temponote,utils.db_memberinfo,utils.db_memberinfo),utils.ENGINE)
    
    df.to_excel('the-first-user-MAL.xlsx',index=False)
    os.system("start EXCEL.EXE the-first-user-MAL.xlsx")
               
    return 'Done'
#def get_weekly_report():
#    end_datetime = datetime.now().strftime('%Y-%m-%d ')
#    conver_end_datetime = time.mktime(time.strptime(end_datetime, '%Y-%m-%d '))
#    conver_start_datetime = conver_end_datetime - 60*60*24*7
#    start_datetime = datetime.fromtimestamp(conver_start_datetime).strftime('%Y-%m-%d ')
#                
#    df_tempo = pd.read_sql("SELECT  activity, outcome, datetime   FROM {} WHERE DATETIME BETWEEN TO_DATE {} AND TO_DATE {} AND NAME like '{}' ORDER BY datetime  "\
#        .format(utils.db_temponote,(start_datetime,'YYYY-MM-DD'),(end_datetime,'YYYY-MM-DD '),utils.username),utils.ENGINE)
#
#
#    df_todo = pd.read_sql("SELECT  todo, outcomes, datetime   FROM {} WHERE DATETIME BETWEEN TO_DATE {} AND TO_DATE {} AND NAME like '{}' ORDER BY datetime  "\
#        .format(utils.db_todo,(start_datetime,'YYYY-MM-DD '),(end_datetime,'YYYY-MM-DD '),utils.username),utils.ENGINE)
#
#
#    df_action = pd.read_sql("SELECT  action, datetime   FROM {} WHERE DATETIME BETWEEN TO_DATE {} AND TO_DATE {} AND NAME like '{}' ORDER BY datetime  "\
#        .format(utils.db_action,(start_datetime,'YYYY-MM-DD '),(end_datetime,'YYYY-MM-DD'),utils.username),utils.ENGINE)
#
#
#    writer = pd.ExcelWriter('action_weekly.xlsx', engine='xlsxwriter',datetime_format = 'YYYY-MM-DD')
#    df_tempo.to_excel(writer, sheet_name='Temponote')
#    df_action.to_excel(writer, sheet_name='Action')
#    df_todo.to_excel(writer, sheet_name='TODO')
#    writer.save()
#
#
#
#    print('Get Action successfully!!. Please check your folder and review before update to server')
#
#
#
#    os.system("start EXCEL.EXE action_weekly.xlsx")
    # #while time.time() <= timer_run:
    #     #if time.time() > time_review + timer:
    #         #try:
    #     time.sleep(60*5)
    #     df_review = pd.read_excel('action.xlsx')

    #     df_review.to_sql(utils.db_weekendreview, utils.ENGINE, if_exists = 'append', index = False)
    #     #print(df_review)
    #     print('Update successfully!!')