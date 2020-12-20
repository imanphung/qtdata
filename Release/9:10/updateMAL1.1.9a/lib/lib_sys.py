import PySimpleGUI as sg
import os, sys
import inspect, importlib
import pydoc
import pandas as pd
from datetime import datetime
import shutil

import utils



#List of libs
lib_global = ['lib_sys', 'lib_tempo', 'lib_bot', 'lib_hr']
sys_global = ['utils.py', 'codebase.py', 'popup_tempo.py', 'debugger.py', 'logger.py',
              'requirements.txt', 'mac_requirements.txt', 'README.rtf',
              'lib/__init__.py']


def hello(text = 'Hello, world!'):
    return text


def hi():
    return 'Hi there!'

              
def get_filepath(filename_extension = 'all'):
    try:
        if filename_extension == 'xlsx':
            path = sg.PopupGetFile(
                       'Choose File to Upload',
                       no_window = True,
                       default_extension = '.xlsx',
                       file_types = (('Excel Files', '*.xlsx'),)
                   )
        elif filename_extension == 'py':
            path = sg.PopupGetFile(
                       'Choose File to Upload',
                       no_window = True,
                       multiple_files = True,
                       default_extension = '.py',
                       file_types = (('Python Files', '*.py'),)
                   )
        else:
            if sys.platform == 'win32':
                path = sg.PopupGetFile(
                    'Choose File to Upload',
                    no_window = True,
                    multiple_files = True,
                    default_extension = '*.*',
                    file_types = (('ALL Files', '*.*'),)
                )
            else:
                path = sg.PopupGetFile(
                    'Choose File to Upload',
                    no_window = True,
                    multiple_files = True,
                    default_extension = '*.*',
                    file_types = (
                        ('RTF Files', '*.rtf'),
                        ('Text Files', '*.txt'),
                        ('Python Files', '*.py'),
                        ('Excel Files', '*.xlsx'),
                    )
                )
    except:
        path = None
    return path


def get_folderpath():
    try:
        path = sg.PopupGetFolder('Select a Destination', no_window = True)
    except:
        path = None
    return path


def list_function():
    all_functions = []
    package = 'lib'
    root = './{}'.format(package)
    
    for path, subdirs, files in os.walk(root):
        for fname in files:
            if fname.endswith('.py') and not fname.startswith('__'):
                obj = importlib.import_module('{}.{}'.format(package, fname.split('.')[0]))
                temp_func = inspect.getmembers(obj, inspect.isfunction)
                all_functions += [value[0] for id, value in enumerate(temp_func)]
    all_functions.sort()            
    return all_functions
    

#def push_function(commit):
#    log = ''
#    list_filepath = list(get_filepath())
#    
#    if len(list_filepath) > 0:     
#        for filepath in list_filepath:
#            try:
#                #Detect libname
#                filename = os.path.basename(filepath).split('.')[0]
#                if filename in lib_global:
#                    libname = filename
#                else:
#                    libname = 'lib_custom'
#                    
#                text_file = open(filepath)
#                lines = text_file.readlines()
#                text_file.close()
#            
#                df_local = pd.DataFrame(columns = ['FUNCTION', 'CONTENT'])
#                idx = 0
#                
#                #Split function
#                func_content = []
#                for id, line in enumerate(lines):
#                    if line.find('def ') == 0:
#                        df_local.loc[idx, 'FUNCTION'] = line.split('def ', 1)[1].split('(')[0]
#                        idx += 1
#                        func_content.append(id - 1)
#                
#                sourcecode = ''
#                idx = 0
#                for id, line in enumerate(lines):
#                    if id not in func_content[1:]:
#                        sourcecode += line
#                    else:
#                        df_local.loc[idx, 'CONTENT'] = sourcecode
#                        idx += 1
#                        sourcecode = ''
#         
#                df_local.loc[idx, 'CONTENT'] = sourcecode
#                df_local['LIB'] = libname
#                df_local['NAME'] = utils.username
#                df_local['DATE_MODIFIED'] = datetime.now()
#                df_local['COMMIT'] = commit
#                
#                #Get list of local functions
#                list_func = "('{}')".format("', '".join(df_local['FUNCTION']))
#                
#                #Get functions from server
#                df_server = pd.read_sql("select * from {} where to_char(FUNCTION) in {} and LIB like '{}'"\
#                    .format(utils.db_function, list_func, libname), utils.ENGINE)
#                df_server.columns = [x.upper() for x in df_server.columns]
#
#                #Compare differences
#                run_diffcheck(df_local, df_server)
#                        
#                utils.ENGINE.execute(
#                    "delete from {} where to_char(FUNCTION) in {} and LIB like '{}'"\
#                    .format(utils.db_function, list_func, libname)
#                )
#                
#                df_local.to_sql(utils.db_function, utils.ENGINE, if_exists = 'append', index = False)
#                
#                log += "'{}': Functions uploaded successfully.\n".format(filename)
#          
#            except Exception as e:
#                print(e)
#                log += "'{}': Functions uploaded failed!\n".format(filename)
#                continue
#    else:
#        log += 'No file selected.'
#        
#    return log
#    
#
#def get_function(libname = None):
#    log = 'Backup files before updating.\n'
#    list_backup = sys_global + ['lib/{}.py'.format(i) for i in lib_global] + ['lib/lib_custom.py']
#    backup(list_backup)
#    
#    if libname is None:
#        df = pd.read_sql("select * from {} where LIB not like 'sys_file'".format(utils.db_function), utils.ENGINE)
#        df.columns = [x.upper() for x in df.columns]
#
#        lib_list = list(df['LIB'].unique())
#    else:
#        df = pd.read_sql("select * from {} where LIB like '{}'".format(utils.db_function, libname), utils.ENGINE)
#        df.columns = [x.upper() for x in df.columns]
#
#        lib_list = [libname]
#                  
#    for lib in lib_list:
#        try:
#            sourcecode = df.loc[df['LIB'] == lib, 'CONTENT']
#            if len(sourcecode) > 0:
#                file = open('./lib/{}.py'.format(lib), 'w+', encoding = 'utf-8')
#                #Add a new \n (line break) between value in Series
#                file.write('\n'.join(sourcecode))
#                file.close()
#                log += "'{}': Updates OK.\n".format(lib)
#            else:
#                log += "'{}': Library does not exist.\n".format(lib)
#          
#        except:
#            log += "'{}': Updates failed!\n".format(lib)
#            continue
#    
#    return log
#    
#
#def push_sysfile(commit, method = None):
#    log = ''
#
#    if method == 'all':
#        list_filename = sys_global
#    else:
#        list_filepath = list(get_filepath())
#        list_filename = [file.replace(utils.root +'/', '') for file in list_filepath]
#                         
#    if len(list_filename) > 0:                                       
#        for filename in list_filename:
#            try:
#                if filename in sys_global:
#                    text_file = open(utils.root +'/' + filename)
#                    lines = text_file.readlines()
#                    text_file.close()
#                
#                    sourcecode = ''.join(lines)
#                    df_local = pd.DataFrame()
#                    df_local['FUNCTION'] = [filename]
#                    df_local['CONTENT'] = sourcecode
#                    df_local['LIB'] = 'sys_file'
#                    df_local['NAME'] = utils.username
#                    df_local['DATE_MODIFIED'] = datetime.now()
#                    df_local['COMMIT'] = commit
#
#                    #Get functions from server
#                    df_server = pd.read_sql("select * from {} where FUNCTION like '{}' and LIB like 'sys_file'"\
#                        .format(utils.db_function, filename), utils.ENGINE) 
#                    df_server.columns = [x.upper() for x in df_server.columns]
#    
#                    #Compare differences
#                    run_diffcheck(df_local, df_server)
#                    
#                    #Insert to oracle server
#                    utils.ENGINE.execute(
#                        "delete from {} where FUNCTION like '{}' and LIB like 'sys_file'"\
#                        .format(utils.db_function, filename)
#                    )
#                        
#                    df_local.to_sql(utils.db_function, utils.ENGINE, if_exists = 'append', index = False)
#                    
#                    log += "'{}': File uploaded successfully.\n".format(filename)
#                
#                else:
#                    log += "'{}': Not a system file.\n".format(filename)
#          
#            except:
#                log += "'{}': File uploaded failed!\n".format(filename)
#                continue
#    else:
#        log += 'No file selected.'
#        
#    return log
#           
#
#def get_sysfile(sysfile = None):
#    log = 'Backup files before updating.\n'
#    list_backup = sys_global + ['lib/{}.py'.format(i) for i in lib_global] + ['lib/lib_custom.py']
#    backup(list_backup)
#    
#    if sysfile is None:
#        df = pd.read_sql("select * from {} where LIB like 'sys_file'".format(utils.db_function), utils.ENGINE)
#    else:
#        df = pd.read_sql(
#            "select * from {} where FUNCTION like '{}' and LIB like 'sys_file'"\
#            .format(utils.db_function, sysfile), utils.ENGINE
#        ) 
#    df.columns = [x.upper() for x in df.columns]
#    
#    for idx in df.index:
#        try:
#            sysfile = df.loc[idx, 'FUNCTION']
#            file = open('./{}'.format(sysfile), 'w+')
#            #Add a new \n (line break) between value in Series
#            file.write(df.loc[idx, 'CONTENT'])
#            file.close()
#            log += "'{}': Updates OK.\n".format(sysfile)
#          
#        except:
#            log += "'{}' Updates failed!\n".format(sysfile)
#            continue
#        
#    return log


def whatis(module):
    return pydoc.render_doc(module, 'help(%s)', renderer = pydoc.plaintext)
        

def backup(list_files):
    backup_folder = utils.path_backup + '{}'.format(datetime.now().strftime('%Y-%m-%dT%H%M%S'))
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    for file in list_files:
        shutil.copy2(file, backup_folder)


def rollback():
    backup_folder = get_folderpath()
    list_path = [os.path.join(backup_folder, f) for f in os.listdir(backup_folder)]

    for file in list_path:
        if os.path.basename(file) == '__init__.py':
            shutil.copy2(file, './lib/')
        else:
             shutil.copy2(file, './')
        

def create_window_diffcheck(func_content, log_diff):
    sg.theme('TanBlue')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
    
    layout = [
        [
            sg.Text("Function: {}".format(func_content['FUNCTION'][0])),
            sg.Text("Date Modified: {}".format(func_content['DATE_MODIFIED'][0]))
        ],
        [
            sg.Text("Lib: {}".format(func_content['LIB'][0])),
            sg.Text("Author: {}".format(func_content['NAME'][0])),
            sg.Text("Commit: {}".format(func_content['COMMIT'][0]))
        ],
        [sg.Multiline(default_text = log_diff, size = (70, 20))],
        [sg.Button('Replace'), sg.Button('Cancel')]
    ]
    window = sg.Window(
        '{}: Changes to be commited'.format(func_content['FUNCTION'][0]),
        layout,
        resizable = True,
        keep_on_top = True,
        finalize = True
    )
        
    return window
    

def run_diffcheck(df_local, df_server):
    import difflib
    
    df_diff = df_server.merge(df_local, on = 'FUNCTION', how = 'outer')

    for i in df_diff.index:
        try:
            lines1 = df_diff.loc[i, 'CONTENT_x'].splitlines()
            lines2 = df_diff.loc[i, 'CONTENT_y'].splitlines()
        except:
            continue
        
        log_diff = ''
        for line in difflib.unified_diff(lines1, lines2, fromfile = 'local', tofile = 'server', lineterm = ''):
            log_diff += line + '\n'
    
        func_name = df_diff.loc[i, 'FUNCTION']
        func_content = df_server[df_server['FUNCTION'] == func_name].reset_index(drop = True)
            
        if log_diff == '':
            df_local.loc[df_local['FUNCTION'] == func_name, 'NAME'] = func_content['NAME'].values
            df_local.loc[df_local['FUNCTION'] == func_name, 'DATE_MODIFIED'] = func_content['DATE_MODIFIED'].values
            df_local.loc[df_local['FUNCTION'] == func_name, 'COMMIT'] = func_content['COMMIT'].values

        else:
            win_alert = create_window_diffcheck(func_content, log_diff)
    
            while True:
                event, values = win_alert.read()
                if event == 'Replace':
                    win_alert.Close()
                    break
                
                if event == sg.WIN_CLOSED or event == 'Cancel':
                    df_local.loc[df_local['FUNCTION'] == func_name, 'CONTENT'] = func_content['CONTENT'].values
                    df_local.loc[df_local['FUNCTION'] == func_name, 'NAME'] = func_content['NAME'].values
                    df_local.loc[df_local['FUNCTION'] == func_name, 'DATE_MODIFIED'] = func_content['DATE_MODIFIED'].values
                    df_local.loc[df_local['FUNCTION'] == func_name, 'COMMIT'] = func_content['COMMIT'].values
                    win_alert.Close()
                    break


                