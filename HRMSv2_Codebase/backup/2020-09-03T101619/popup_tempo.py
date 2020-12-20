import PySimpleGUI as sg
import pandas as pd
import os, sys
import traceback
import argparse
from datetime import datetime
import time
import pyscreenshot as ImageGrab
import cv2
import base64
from io import BytesIO
from PIL import Image, ImageTk
import json

import utils
from logger import log_temponote, log_tempomonitor
import pyautogui


parser = argparse.ArgumentParser('Tempo Popup')
parser.add_argument('-s', '--server-status', help = 'Server status', default = -1)
parser.add_argument('-t', '--total-time', help = 'Number of working hours to include', default = 1)
parser.add_argument('-c', '--capture-images', help = 'Capture images', default = 'off')
parser.add_argument('-n', '--popup-note', help = 'Run Tempo Note', default = 'off')
parser.add_argument('-m', '--popup-monitor', help = 'Run Tempo Monitor', default = 'off')
parser.add_argument('-style', '--style', help = "Display style: 'compact' or 'all'", default = 'all')

args = parser.parse_args()
total_secs = int(float(args.total_time) * 3600)
screen_size = pyautogui.size()
            

def encode_b64(image_pil):        
    if image_pil.mode != 'RGB':
        image_pil = image_pil.convert('RGB')
    buff = BytesIO()
    image_pil.save(buff, format = 'png')
    image_b64 = base64.b64encode(buff.getvalue()).decode('utf-8')

    return image_b64
    

def snapshot():
    X1 = 10
    Y1 = 290
    X2 = 710
    Y2 = 990

    #Grabbing images
    try:
        screen = ImageGrab.grab(bbox = (X1,Y1,X2,Y2))
        frame = screen
#        try:
#            video_capture = cv2.VideoCapture(0)
#            ret, frame = video_capture.read()
#            video_capture.release()
#            
#            frame = frame[X1:X2, Y1:Y2]
#            #Convert to PIL Image
#            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#            frame = Image.fromarray(frame)
#            
#        except:
#            frame = screen
        
        #Resize
        frame = frame.resize((100, 100), Image.ANTIALIAS)
        screen = screen.resize((100, 100), Image.ANTIALIAS)
        
        #Encode to string
        frame_b64 = encode_b64(frame)
        screen_b64 = encode_b64(screen)
        
    except:
        log_temponote.warning('Cannot capture images!')
        log_temponote.warning(traceback.format_exc())
        frame_b64 = 'None'
        screen_b64 = 'None'
        
    return frame_b64, screen_b64
    

def capture_images(total_secs, timer_monitor):
    monitor_start = time.time()
    timer_end = monitor_start + total_secs
    popup_first_run = True
    

    while monitor_start <= timer_end:
        try:
            #Capture image
            if time.time() > monitor_start + timer_monitor or popup_first_run:
                monitor_start = time.time()
                popup_first_run = False
                
                frame_b64, screen_b64 = snapshot()
        
                if int(args.server_status) == 0:
                    df_monitor = pd.DataFrame([{
                        'DATETIME': datetime.now(),
                        'TIME': datetime.now().strftime('%H:%M:%S'),
                        'NAME': utils.username,
                        'WEBCAM': frame_b64,
                        'SCREEN': screen_b64
                    }])
                    
                    df_monitor.to_sql(utils.db_tempomonitor, utils.ENGINE, if_exists = 'append', index = False)
                
        except:
            log_tempomonitor.warning(traceback.format_exc())
            pass
            
def create_window_note():
    sg.theme('TanBlue')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 15))
        
    layout = [
        [sg.Text('Custom Status')],
        [sg.Text(key = '-TIME-', size = (20, 1))],
        [sg.Text('Outcome', key = '-LABEL1-')],
        [sg.InputText(key = '-OUTCOME-')],
        [sg.Text('Next Activity', key = '-LABEL2-')],
        [sg.InputText(key = '-NEXTACT-', focus = True)],
        [sg.Text('Action', key = '-LABEL3-', visible = False)],
        [sg.InputText(key = '-ACTION-', visible = False)],
        [sg.Submit(key = '-SUBMIT-', bind_return_key = True)]
    ]
    
    window = sg.Window(
        'TempoNote 5000',
        layout,
        disable_close = True,
        keep_on_top = True,
        finalize = True,
        size=(screen_size[0],screen_size[1])
    )
    window.Element('-SUBMIT-').Update(visible = False)
    
    return window

    
def run_popup_note(total_secs, timer_popup, timer_action, timer_exist):
    #Init
    popup_start = time.time()
    action_start = time.time()
    action_is_on = False
    timer_end = popup_start + total_secs
    popup_first_run = True
    
    while popup_start <= timer_end:
        try:
            #Create note
            if time.time() > popup_start + timer_popup or popup_first_run:
                window = create_window_note()
                popup_start = time.time()
                popup_first_run = False
                
                current_time = datetime.now().strftime('%H:%M:%S')
                window.Element('-TIME-').Update('Time: {}'.format(current_time))
                
                if time.time() > action_start + timer_action:
                    action_is_on = True
                    action_start = time.time()
                    window.Element('-LABEL1-').Update('Outcomes')
                    window.Element('-LABEL2-').Update('Activities')
                    window.Element('-LABEL3-').Update(visible = True)
                    window.Element('-ACTION-').Update(visible = True)

                tp_act = 'None'
                tp_outcome = 'None'
                tp_action = 'None'
                while True:
                    event, values = window.read(timeout = 100)
                    if event == sg.TIMEOUT_KEY:
                        tp_outcome = values['-OUTCOME-']
                        tp_act = values['-NEXTACT-']
                        if action_is_on:    
                            tp_action = values['-ACTION-']
                        pass
                    
                    if time.time() > popup_start + timer_exist:
                        window.Hide()
                        window.Close()
                        break
                    
                    if action_is_on:
                        if tp_act is not None and tp_outcome is not None and tp_action is not None \
                        and len(tp_act) > 0 and len(tp_outcome) > 0 and len(tp_action) > 0 \
                        and event == '-SUBMIT-':
                            window.Hide()
                            window.Close()
                            break
                    else:
                        if tp_act is not None and len(tp_act) > 0 and event == '-SUBMIT-':
                            window.Hide()
                            window.Close()
                            break
    
                if int(args.server_status) == 0:
                    if action_is_on:
                        df_action = pd.DataFrame([{
                            'DATETIME': datetime.now(),
                            'TIME': current_time,
                            'NAME': utils.username,
                            'ACTIVITIES': tp_act,
                            'OUTCOMES': tp_outcome,
                            'ACTION': tp_action,
                            'THUMBUP': ''
                        }])
    
                        df_action.to_sql(utils.db_action, utils.ENGINE, if_exists = 'append', index = False)
                        action_is_on = False
                        
                    else:
                        df_note = pd.DataFrame([{
                            'DATETIME': datetime.now(),
                            'TIME': current_time,
                            'NAME': utils.username,
                            'OUTCOME': tp_outcome,
                            'ACTIVITY': tp_act
                        }])
    
                        df_note.to_sql(utils.db_temponote, utils.ENGINE, if_exists = 'append', index = False)

                else:
                    file_path = utils.path_note + '{}_{}.json'.format(utils.username, utils.current_date.strftime('%d-%b-%y').upper())
                    if not os.path.exists(file_path):
                        with open(file_path, 'w+') as file:
                            json.dump([], file)
                    #Load json data        
                    with open(file_path, 'r') as file:
                        json_note = json.load(file)
                    
                    dict_note = {
                        'DATETIME': utils.current_date.strftime('%d-%b-%y').upper(),
                        'TIME': current_time,
                        'NAME': utils.username,
                        'OUTCOME': tp_outcome,
                        'ACTIVITY': tp_act
                    }
                            
                    #Write to note file
                    json_note.append(dict_note)
                    with open(file_path, 'w') as file:
                        json.dump(json_note, file)
                        
        except UnicodeDecodeError:
            pass     
        
        except KeyboardInterrupt:
            pass
                        
        except:
            log_temponote.warning(traceback.format_exc())
            window.Close()
            break


def get_checkname():
    file_path = utils.path_checkname
    if not os.path.exists(file_path):
        file = open(file_path, 'w+')
        file.close()
    
    file = open(file_path, 'r')
    list_checkname = file.readlines()
    file.close()
    
    return list_checkname

               
def add_checkname(name):
    file_path = utils.path_checkname
    str_checkname = None
    if not os.path.exists(file_path):
        file = open(file_path, 'w+')
        file.close()
        
    file = open(file_path, 'r')
    list_checkname = file.readlines()
    file.close()
    
    if len(list_checkname) > 0:
        if list_checkname[0].find("'{}'".format(name)) == -1:
            str_checkname = list_checkname[0][:-1] + ", '{}')".format(name)
    else:
        str_checkname = "('{}')".format(name)
    
    if str_checkname is not None:                  
        with open(file_path, 'w') as file:
            file.write(str_checkname)
        file.close()             
    
        return str_checkname
    else:
        return list_checkname[0]


def remove_checkname(name):
    file_path = utils.path_checkname
    str_checkname = None
    if not os.path.exists(file_path):
        file = open(file_path, 'w+')
        file.close()
        
    file = open(file_path, 'r')
    list_checkname = file.readlines()
    file.close()
    
    if len(list_checkname) > 0:
        str_checkname = list_checkname[0].replace(", '{}'".format(name), '') #first of list
        str_checkname = str_checkname.replace("'{}', ".format(name), '') #middle or last in list
        str_checkname = str_checkname.replace("('{}')".format(name), '') #only name in list
        
        with open(file_path, 'w') as file:
            file.write(str_checkname)
        file.close()
        
        return str_checkname
        
    else:
        return 'list_checkname is empty.'
                    
                    
def create_window_monitor_compact():
    sg.theme('LightGreen')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
        
    layout = [
        [sg.Text(key = '-NAME-', size = (30, 1))],
        [sg.Image(key = '-WEBCAM-'), sg.Image(key = '-SCREEN-')]
    ]
    
    window = sg.Window(
        'TempoMonitor',
        layout,
        location = (sg.Window.get_screen_size()[0] - 245, 0),
        keep_on_top = True,
        grab_anywhere = True,
        finalize = True
    )
    return window
        
        
def run_popup_monitor_compact():
    #Init
    window = create_window_monitor_compact()
    monitor_start = time.time()
    timer_monitor = utils.timer_monitor
    popup_first_run = True

    while True:
        try:
            event, values = window.read(timeout = 100)
            if event == sg.TIMEOUT_KEY:
                if time.time() > monitor_start + timer_monitor or popup_first_run:
                    monitor_start = time.time()
                    popup_first_run = False
                    
                    df = pd.read_sql("select * from {} where DATETIME = (select max(DATETIME) from {})"\
                        .format(utils.db_tempomonitor, utils.db_tempomonitor), utils.ENGINE) 
                    df.columns = [x.upper() for x in df.columns]
                    
                    if len(df) > 0 and df['SCREEN'][0] is not None:
                        name = df['NAME'][0]
                        frame_b64 = df['WEBCAM'][0]
                        screen_b64 = df['SCREEN'][0]
                        frame = Image.open(BytesIO(base64.b64decode(frame_b64)))
                        screen = Image.open(BytesIO(base64.b64decode(screen_b64)))
                        
                        window.Element('-NAME-').Update(name)
                        window.Element('-WEBCAM-').Update(data = ImageTk.PhotoImage(frame))
                        window.Element('-SCREEN-').Update(data = ImageTk.PhotoImage(screen))
                    
                continue
                    
            if event == sg.WIN_CLOSED:
                window.Close()
                break
                
        except UnicodeDecodeError:
            pass     
        
        except KeyboardInterrupt:
            pass
        
        except:
            log_tempomonitor.warning(traceback.format_exc())
            window.Close()
            break
        

def create_window_monitor(str_checkname):
    sg.theme('LightGreen')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
        
    list_checkname = str_checkname[1:-1].split(', ')
    check_user = []
    
    for i in range(len(list_checkname)):
        check_user.append([
            sg.Text(key = 'name{}'.format(i), size = (25, 1))
        ])
            
        check_user.append([
            sg.Text('Task:', size = (5, 1)),
            sg.Text(key = 'doing_task{}'.format(i), size = (20, 1))
        ])
        
        check_user.append([
            sg.Text('Note:', size = (5, 1)),
            sg.Text(key = 'current_note{}'.format(i), size = (20, 1))
        ])
        
        check_user.append([
            sg.Image(key = 'webcam{}'.format(i)),
            sg.Image(key = 'screen{}'.format(i))
        ])
        
    layout = [
        *check_user
    ]
    
    window = sg.Window(
        'TempoMonitor',
        layout,
        location = (sg.Window.get_screen_size()[0] - 245, 0),
        keep_on_top = True,
        finalize = True
    )
    return window


def run_popup_monitor():        
    try:
        str_checkname = get_checkname()[0]
    except:
        sg.Popup('Error: list_checkname has no value.', title = 'Tempo Monitor', keep_on_top = True)
        
    window = create_window_monitor(str_checkname)
    monitor_start = time.time()
    timer_monitor = utils.timer_monitor
    popup_first_run = True

    while True:
        try:
            event, values = window.read(timeout = 100)
            if event == sg.TIMEOUT_KEY:
                if time.time() > monitor_start + timer_monitor or popup_first_run:
                    monitor_start = time.time()
                    popup_first_run = False

                    #Monitor images
                    df_monitor = pd.read_sql(
                        "select * from {} where to_char(NAME) in {} "\
                        "and DATETIME in (select max(DATETIME) from {} group by to_char(NAME))"\
                        .format(utils.db_tempomonitor, str_checkname, utils.db_tempomonitor), utils.ENGINE)
                    df_monitor.columns = [x.upper() for x in df_monitor.columns]
                                  
                    #Current Task
                    df_task = pd.read_sql(
                        "select * from {} where to_char(ASSIGNEE) in {} and STATUS like 'In Progress'"\
                        .format(utils.db_tasks, str_checkname), utils.ENGINE)
                    df_task.columns = [x.upper() for x in df_task.columns]
                                   
                    #Current Note    
                    df_note = pd.read_sql(
                        "select * from {} where to_char(NAME) in {} "\
                        "and DATETIME in (select max(DATETIME) from {} group by to_char(NAME))"\
                        .format(utils.db_temponote, str_checkname, utils.db_temponote), utils.ENGINE)
                    df_note.columns = [x.upper() for x in df_note.columns]
                    df_note = df_note[['NAME', 'ACTIVITY', 'OUTCOME']]
                                             
                    df = pd.merge(df_monitor, df_task, how = 'outer', left_on = 'NAME', right_on = 'ASSIGNEE')
                    df = pd.merge(df, df_note, how = 'outer', on = 'NAME')
                    
                    for i in df.index:
                        name = df['NAME'][i]
                        doing_task = df['TASK'][i]
                        task_content = 'Project: {}\n'\
                            'Content: {}\n'\
                            'Date: {}\n'\
                            'Assigner: {}\n'\
                            'Issue: {}\n'\
                            'Solution: {}\n'\
                            .format(df['PROJECT'][i], df['CONTENT'][i], df['DATE_MODIFIED'][i], \
                                df['ASSIGNER'][i], df['ISSUE'][i], df['SOLUTION'][i])
                        current_note = df['ACTIVITY'][i]
                        if current_note is None:
                            current_note = ''

                        window.Element('name{}'.format(i)).Update(name)
                        window.Element('doing_task{}'.format(i)).Update(doing_task)
                        window.Element('doing_task{}'.format(i)).set_tooltip(task_content)
                        window.Element('current_note{}'.format(i)).Update(current_note)
                        try:
                            frame_b64 = df['WEBCAM'][i]
                            screen_b64 = df['SCREEN'][i]
                            frame = Image.open(BytesIO(base64.b64decode(frame_b64)))
                            screen = Image.open(BytesIO(base64.b64decode(screen_b64)))

                            window.Element('webcam{}'.format(i)).Update(data = ImageTk.PhotoImage(frame))
                            window.Element('screen{}'.format(i)).Update(data = ImageTk.PhotoImage(screen))
                            
                        except:
                            continue
                    
                continue
                    
            if event == sg.WIN_CLOSED:
                window.Close()
                break
                
        except UnicodeDecodeError:
            pass     
        
        except KeyboardInterrupt:
            pass
        
        except:
            log_tempomonitor.warning(traceback.format_exc())
            window.Close()
            break
        
if args.capture_images == 'on':
    capture_images(total_secs, utils.timer_monitor)

if args.popup_note == 'on':
    run_popup_note(total_secs, utils.timer_popup, utils.timer_action, utils.timer_exist)

if args.popup_monitor == 'on':
    if args.style == 'compact':
        run_popup_monitor_compact()
    else:
        run_popup_monitor()