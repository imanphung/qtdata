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



parser = argparse.ArgumentParser('Tempo Popup')
parser.add_argument('-s', '--server-status', help = 'Server status', default = -1)
parser.add_argument('-t', '--total-time', help = 'Number of working hours to include', default = 1)
parser.add_argument('-n', '--popup-note', help = 'Run Tempo Note', default = 'off')
parser.add_argument('-m', '--popup-monitor', help = 'Run Tempo Monitor', default = 'off')
parser.add_argument('-style', '--style', help = "Display style: 'compact' or 'all'", default = 'all')

args = parser.parse_args()
total_secs = int(float(args.total_time) * 3600)
            

def encode_b64(image_pil):        
    if image_pil.mode != 'RGB':
        image_pil = image_pil.convert('RGB')
    buff = BytesIO()
    image_pil.save(buff, format = 'png')
    image_b64 = base64.b64encode(buff.getvalue()).decode('utf-8')

    return image_b64
    

def snapshot():
    # X1,Y1,X2,Y2
    X1 = 10
    Y1 = 290
    X2 = 710
    Y2 = 990

    #Grabbing images
    try:
        screen = ImageGrab.grab(bbox=(X1,Y1,X2,Y2))
        
        try:
            video_capture = cv2.VideoCapture(0)
            ret, frame = video_capture.read()
            video_capture.release()
            
            frame = frame[X1:X2, Y1:Y2]
            #Convert to PIL Image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
        except:
            frame = screen
        
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
    

def create_window_note():    
    sg.theme('TanBlue')
    
    #Comment next 2 lines or change the number if window size is too big/small
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 15))
        
    layout = [
        [sg.Text('Custom Status')],
        [sg.Text(key = '-TIME-', size = (20, 1))],
        [sg.Text('Outcome')],
        [sg.InputText(key = '-OUTCOME-')],
        [sg.Text('Next Activity')],
        [sg.InputText(key = '-NEXTACT-', focus = True)],
        [sg.Submit(key = '-SUBMIT-', bind_return_key = True)]
    ]
    
    window = sg.Window(
        'TempoNote 5000',
        layout,
        disable_close = True,
        keep_on_top = True,
        finalize = True
    )
    window.Element('-SUBMIT-').Update(visible = False)
    
    return window

    
def run_popup_note(total_secs, timer_popup, timer_exist, timer_monitor):
    #Init
    popup_start = time.time()
    monitor_start = time.time()
    timer_end = popup_start + total_secs
    popup_first_run = True
    
    frame_b64 = 'None'
    screen_b64 = 'None'
    while popup_start <= timer_end:
        try:
            #Capture image
#            if time.time() > monitor_start + timer_monitor or popup_first_run:
#                monitor_start = time.time()
#                frame_b64, screen_b64 = snapshot()
#
#                if int(args.server_status) == 0:
#                    df_monitor = pd.DataFrame([{
#                        'DATETIME': datetime.now(),
#                        'TIME': datetime.now().strftime('%H:%M:%S'),
#                        'NAME': utils.username,
#                        'WEBCAM': frame_b64,
#                        'SCREEN': screen_b64
#                    }])
#                    
#                    df_monitor.to_sql(utils.db_tempomonitor, utils.ENGINE, if_exists = 'append', index = False)
            
            #Create note
            if time.time() > popup_start + timer_popup or popup_first_run:
                window = create_window_note()
                popup_start = time.time()
                popup_first_run = False
                
                current_time = datetime.now().strftime('%H:%M:%S')
                window.Element('-TIME-').Update('Time: {}'.format(current_time))

                tp_act = 'None'
                tp_outcome = 'None'                
                while True:
                    event, values = window.read(timeout = 100)
                    if event == sg.TIMEOUT_KEY:
                        tp_act = values['-NEXTACT-']
                        tp_outcome = values['-OUTCOME-']
                        pass
                    
                    if time.time() > popup_start + timer_exist:
                        window.Hide()
                        window.Close()
                        break
                    
                    if tp_act is not None and len(tp_act) > 0 and event == '-SUBMIT-':
                        window.Hide()
                        window.Close()
                        break
    
                if int(args.server_status) == 0:
                    df_note = pd.DataFrame([{
                        'DATETIME': datetime.now(),
                        'TIME': current_time,
                        'NAME': utils.username,
                        'OUTCOME': tp_outcome,
                        'ACTIVITY': tp_act,
                        'WEBCAM': frame_b64,
                        'SCREEN': screen_b64
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
                        'ACTIVITY': tp_act,
                        'WEBCAM': frame_b64,
                        'SCREEN': screen_b64
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
        

def create_window_monitor():
    str_checkname = get_checkname()[0]
    list_checkname = str_checkname[1:-1].split(', ')
    check_user = []
    sg.theme('LightGreen')
    
    for i in range(len(list_checkname)):
        check_user.append([
            sg.Text(
                key = 'name{}'.format(i),
                size = (30, 1)
            )
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
    #Init
    sg.theme('LightGreen')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
    try:
        str_checkname = get_checkname()[0]
    except:
        sg.Popup('Error: list_checkname has no value.', title = 'Tempo Monitor', keep_on_top = True)
        
    window = create_window_monitor()
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

                    df = pd.read_sql("select * from {} where to_char(NAME) in {} and DATETIME in (select max(DATETIME) from {} group by to_char(NAME))"\
                        .format(utils.db_tempomonitor, str_checkname, utils.db_tempomonitor), utils.ENGINE)
                    df.columns = [x.upper() for x in df.columns]
                           
                    for i in df.index:
                        name = df['NAME'][i]
                        frame_b64 = df['WEBCAM'][i]
                        screen_b64 = df['SCREEN'][i]
                        frame = Image.open(BytesIO(base64.b64decode(frame_b64)))
                        screen = Image.open(BytesIO(base64.b64decode(screen_b64)))
                        
                        window.Element('name{}'.format(i)).Update(name)
                        window.Element('webcam{}'.format(i)).Update(data = ImageTk.PhotoImage(frame))
                        window.Element('screen{}'.format(i)).Update(data = ImageTk.PhotoImage(screen))
                    
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


if args.popup_note == 'on':
    run_popup_note(total_secs, utils.timer_popup, utils.timer_exist, utils.timer_monitor)

if args.popup_monitor == 'on':
    if args.style == 'compact':
        run_popup_monitor_compact()
    else:
        run_popup_monitor()