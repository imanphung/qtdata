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
import imageio
from io import BytesIO
from PIL import Image, ImageTk, ImageSequence
import json
import utils
from logger import log_temponote, log_tempomonitor



parser = argparse.ArgumentParser('Tempo Popup')
parser.add_argument('-s', '--server-status', help = 'Server status', default = -1)
parser.add_argument('-t', '--total-time', help = 'Number of working hours to include', default = 1)
parser.add_argument('-c', '--capture-images', help = 'Capture images', default = 'off')
parser.add_argument('-n', '--popup-note', help = 'Run Tempo Note', default = 'off')
parser.add_argument('-m', '--popup-monitor', help = 'Run Tempo Monitor', default = 'off')
parser.add_argument('-style', '--style', help = "Display style: 'compact' or 'all'", default = 'all')

args = parser.parse_args()
total_secs = int(float(args.total_time))
            

def encode_b64(image_pil):        
    if image_pil.mode != 'RGB':
        image_pil = image_pil.convert('RGB')
    buff = BytesIO()
    image_pil.save(buff, format = 'png')
    image_b64 = base64.b64encode(buff.getvalue()).decode('utf-8')

    return image_b64
    

def snapshot():

    #Grabbing images
    try:
        screen = ImageGrab.grab()
        frame = screen
        try:
            if sys.platform == 'win32':
                video_capture = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
            else:
                video_capture = cv2.VideoCapture(0)
                # video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                # video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                
            ret, frame = video_capture.read()
            time.sleep(1)
            video_capture.release()

            #Convert to PIL Image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            
        except:
            frame = screen
        
        #Resize
        #frame = frame.resize((1440, 900), Image.ANTIALIAS)
        #screen = screen.resize((1440, 900), Image.ANTIALIAS)
        #Encode to string
        frame_b64 = encode_b64(frame)
        screen_b64 = encode_b64(screen)
        
    except:
        log_temponote.warning('Cannot capture images!')
        log_temponote.warning(traceback.format_exc())
        frame_b64 = 'None'
        screen_b64 = 'None'
        
    return frame_b64, screen_b64
    

def capture_images(total_secs, timer_monitor, timer_thumbsup):
    monitor_start = time.time()
    thumbsup_start = time.time()
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
                #server off
                elif int(args.server_status) == -1:
                    date = datetime.now().strftime("%Y-%m-%d")
                    path = utils.path_output + '{}_{}/'.format(date, utils.username)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    date_position = (10,40)
                    with imageio.get_writer( path +'webcams_screens.gif', mode='I', fps=5) as writer_screen:
                        screen = imageio.imread(base64.b64decode(screen_b64))
                        webcam = imageio.imread(base64.b64decode(frame_b64))
                        #crop webcame to overlay a webcame image on a screen image
                        crop_webcam = webcam[100:800, 350:1050]
                        crop_webcam = cv2.resize(crop_webcam, (300, 300))
                        x_offset=y_offset=0
                        screen[y_offset:y_offset+crop_webcam.shape[0], x_offset:x_offset+crop_webcam.shape[1]] = crop_webcam
                        #concat_image = cv2.hconcat([ crop_webcam,crop_webcam])
                        cv2.putText(
                          screen, #numpy array on which text is written
                          "{}".format(date), #text
                          date_position, #position at which writing has to start
                          cv2.FONT_HERSHEY_SIMPLEX, #font family
                          1.3, #font size
                          (0,0,255), 3
                          )
                    #Image.save(path +'webcams_screens.gif', save_all=True, append_images=screen)
                        writer_screen.append_data(screen)
                    writer_screen.close()
                    
#            if time.time() > thumbsup_start + timer_thumbsup:
#                thumbsup_start = time.time()
#                run_popup_action()
                
        except:
            log_tempomonitor.warning(traceback.format_exc())
            pass
        
        
#def create_window_action(df):
#    thumbsup_img = utils.path_icon + 'thumbsup.gif'
#    thumbsup_sound = utils.path_sound + 'thumbsup.wav'
#    wave_thumbsup = sa.WaveObject.from_wave_file(thumbsup_sound)
#    play_thumbsup = wave_thumbsup.play()
#    play_thumbsup.wait_done()
#    
#    sg.theme('TanBlue')
#    if sys.platform != 'win32':
#        sg.set_options(font = ('Helvetica', 13))
#        
#    layout = [ 
#        [sg.Text('{}'.format(df['NAME'][0]))],
#        [sg.Multiline(default_text = df['ACTION'][0], size = (60, 3))],  
#        [sg.Button(key = '-THUMBSUP-',
#            border_width = 0, button_color = (sg.theme_background_color(), sg.theme_background_color()),
#            image_filename = thumbsup_img, image_size = (46, 46))]
#    ]
#    
#    window = sg.Window(
#        'Conclusion and Action',
#        layout,
#        location = (sg.Window.get_screen_size()[0]/2 - 220, 100),
#        element_justification = 'center',
#        disable_close = True,
#        keep_on_top = True,
#        finalize = True
#    )
#    
#    return window
#
#    
#def run_popup_action():
#    df = pd.read_sql("select * from {} where THUMBSUP not like '%{}%'".format(utils.db_action, utils.username), utils.ENGINE)
#    df.columns = [x.upper() for x in df.columns]
#    df = df.sort_values('DATETIME', ascending = True).reset_index(drop = True).loc[0].to_frame().T
#
#    thumbsup_user = df['THUMBSUP'][0]
#
#    window = create_window_action(df)
#    
#    while True:
#        try:
#            event, values = window.read(timeout = 100)
#            if event == '-THUMBSUP-':
#                df['THUMBSUP'] = thumbsup_user + ', ' + utils.username
#                
#                utils.ENGINE.execute("delete from {} where DATETIME like '{}' and TIME like '{}' and NAME like '{}'"\
#                    .format(utils.db_action, df['DATETIME'][0].strftime('%d-%b-%y').upper(), \
#                    df['TIME'][0],  df['NAME'][0]))
#                
#                df.to_sql(utils.db_action, utils.ENGINE, if_exists = 'append', index = False)
#                window.Hide()
#                window.Close()
#                break
#            
#        except UnicodeDecodeError:
#            pass     
#        
#        except KeyboardInterrupt:
#            pass
#                        
#        except:
#            log_temponote.warning(traceback.format_exc())
#            window.Close()
#            break
   
            
def create_window_note():
    sg.theme('TanBlue')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 15))
        
    history = []
    for i in range(10):
        history.append([
        sg.Text( key = '-OUTTIME-{}'.format(i),size = (8, 1),background_color = 'white',font = ('Helvetica',10,'bold')),
        sg.Text(key = '-OUTNEXTACT-{}'.format(i),size = (25, 1),background_color = 'white', font = ('Helvetica',10,'bold'))
        ])    
            
    layout = [
        [sg.Text('Tử tế + Chia sẻ + Nghiêm túc + Cầu tiến',text_color='red',font = ('Helvetica',16,'bold'))],
        [sg.Text('History',text_color='black', font = ('Helvetica',16,'bold'))],
        [sg.Column(history,background_color = 'white', vertical_scroll_only = True, scrollable = True)],
        [sg.Text('Note',text_color='black',font = ('Helvetica',16,'bold'))],
        [sg.Text(key = '-TIME-', size = (20, 1))],
        [sg.Text('Outcome', key = '-LABEL1-', size = (10, 1))],
        [sg.InputText(key = '-OUTCOME-',  focus = True)],
        [sg.Text('Next Activity', key = '-LABEL2-')],
        [sg.InputText(key = '-NEXTACT-')],
        [sg.Text('Recommendation & Action', key = '-LABEL3-', visible = False)],
        [sg.InputText(key = '-ACTION-', visible = False)],
        [sg.Submit(key = '-SUBMIT-', bind_return_key = True)]
    ]
    
    window = sg.Window(
        'TempoNote 5000',
        layout,
        disable_close = True,
        keep_on_top = True,
        finalize = True,
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
    
    prev_act = ''
    prev_outcome = ''
    prev_action = ''
    while popup_start <= timer_end:
        try:
            #Create note
            if time.time() > popup_start + timer_popup or popup_first_run:
                window = create_window_note()
                popup_start = time.time()
                popup_first_run = False
                df_history = pd.read_sql("select NEXTACT, TIME from ( select * from {} order by DATETIME DESC ) where rownum < 11 and NAME like '{}'".format(utils.db_temponote,utils.username), utils.ENGINE)
                for i in df_history.index:
                    time_now = df_history['time'][i]
                    nextact_now = df_history['nextact'][i]
                    window.Element('-OUTTIME-{}'.format(i)).Update('{} :'.format(time_now))
                    window.Element('-OUTNEXTACT-{}'.format(i)).Update('{}'.format(nextact_now))
                    
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
                            if prev_act != tp_act and prev_outcome != tp_outcome and prev_action != tp_action:
                                prev_act = tp_act
                                prev_action = tp_action
                                prev_outcome = tp_outcome
                                window.Hide()
                                window.Close()
                                break
                            else:
                                sg.popup('Notification', 'Action is duplicated. Please enter a new one.',keep_on_top = True)
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
                            'THUMBSUP': utils.username
                        }])
    
                        df_action.to_sql(utils.db_action, utils.ENGINE, if_exists = 'append', index = False)
                        action_is_on = False
                        
                    else:
                        df_note = pd.DataFrame([{
                            'DATETIME': datetime.now(),
                            'TIME': current_time,
                            'NAME': utils.username,
                            'OUTCOME': tp_outcome,
                            'NEXTACT': tp_act
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
                        'NEXTACT': tp_act
                    }
                            
                    #Write to note file
                    json_note.append(dict_note)
                    with open(file_path, 'w') as file:
                        json.dump(json_note, file)
                time.sleep(timer_popup-120)
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
    level_result = utils.check_my_level(name)
    if level_result == 0:
        return "You are not allowed to check on this member"
    else:
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
        

def create_window_monitor(str_checkname, my_level):
    sg.theme('LightGreen')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
        
    list_checkname = str_checkname[1:-1].split(', ')
    check_user = []
    index = len(list_checkname)
    for i in range(index):
        check_user.append([
            sg.Graph(canvas_size=(12, 12), graph_bottom_left=(0, 0), graph_top_right=(12, 10),\
                     enable_events=True, key='circle-icon{}'.format(i)),
            sg.Text(key = 'name{}'.format(i), size = (52, 1))
        ])
            
        check_user.append([
            sg.Text('Task:', size = (5, 1)),
            sg.Text(key = 'doing_task{}'.format(i), size = (45, 1))
        ])
        
        check_user.append([
            sg.Text('Note:', size = (5, 1)),
            sg.Text(key = 'current_note{}'.format(i), size = (45, 1))
        ])
        
        check_user.append([
            sg.Image(key = 'webcam{}'.format(i), size = (200, 200)),
            sg.Image(key = 'screen{}'.format(i), size = (200, 200))
        ])
        k = len(check_user)//12
    n = k+i-1
    s = []
    a = (len(check_user)//4)%3
    for j in range(0,n,4):
        t=j*3
        for k in range(t,t+4):
            s.append(check_user[k]+check_user[k+4]+check_user[k+8])
    if a == 1 and index > 2:
        for i in range(len(check_user)-4,len(check_user)):
            s.append(check_user[i])
    elif a == 2 and index > 2:
        for i in range(len(check_user)-8,len(check_user)-4):
            s.append(check_user[i]+check_user[i+4])
    if my_level == 1 and len(list_checkname) >= 3:
        layout = [[sg.Column(s, vertical_scroll_only = True, size = (1450,850), scrollable = True)]]    
        window = sg.Window(
        'TempoMonitor',
        layout,
        keep_on_top = True,
        finalize = True
        ).Finalize()
        window.Maximize()
    else:
        if len(list_checkname) >= 2:
            layout = [[sg.Column(check_user,size = (480,290), vertical_scroll_only = True, scrollable = True)]]    
        else:
            layout = check_user
            
        window = sg.Window(
        'TempoMonitor',
        layout,
        location = (sg.Window.get_screen_size()[0] - 480, 0),
        keep_on_top = True,
        finalize = True,
        size = (480,290)
        )
    return window


def run_team_popup():
   
    sg.theme('LightGreen')
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
    layout=[
        [sg.Text('')],
        [
            sg.Button(key ='-TECH-',button_text = 'Technology'),
            sg.Button(key ='-HR-',button_text = 'HumanResource'),
            sg.Button(key ='-LAW-',button_text = 'Law'),
            sg.Button(key ='-DESIGN-',button_text = 'Design'),
            sg.Button(key ='-ONLINEBUSINESS-',button_text = 'OnlineBusiness'),
            sg.Button(key ='-OPERATION-',button_text = 'Operation'),
            sg.Button(key ='-PROJECT-',button_text = 'Project'),
            sg.Button(key ='-SALE-',button_text = 'Sale'),
            sg.Button(key ='-BOD-',button_text = 'BOD'),
            sg.Button(key ='-ACCOUNTING-',button_text = 'Accounting'),
            sg.Button(key ='-INTERNALLAW-',button_text = 'Internallaw'),
            sg.Button(key ='-AU-',button_text = 'AU'),
            sg.Button(key ='-ARRANGER-',button_text = 'Arranger'),            
            sg.Button(key ='-EXECUTION-',button_text = 'Execution'),
            sg.Button(key ='-INTERN-',button_text = 'Intern'),
            sg.Button(key ='-START-',button_text = 'Start')
        ],
        [sg.Text('')],
    ]
          
    window = sg.Window(
        'Check Team',
        layout,
        element_justification = 'center',
        keep_on_top = True,
        finalize = True
    )
    while True:
        try:
            event, values = window.read(timeout = 100)
            if event == sg.TIMEOUT_KEY:
                pass
            if event == '-TECH-':
                get_code('qt-Technology')
                window.Element('-TECH-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-LAW-':
                get_code('qt-Law')
                window.Element('-LAW-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-DESIGN-':
                get_code('qt-Design') 
                window.Element('-DESIGN-').Update(button_color = ('#FFFFFF', ('red')))                               
            if event == '-HR-':
                get_code('qt-HumanResource') 
                window.Element('-HR-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-ONLINEBUSINESS-':
                get_code('qt-OnlineBusiness')
                window.Element('-ONLINEBUSINESS-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-OPERATION-':
                get_code('qt-Operation')
                window.Element('-OPERATION-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-PROJECT-':
                get_code('qt-Project')
                window.Element('-PROJECT-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-SALE-':
                get_code('qt-Sale')
                window.Element('-SALE-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-BOD-':
                get_code('qt-BOD')
                window.Element('-BOD-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-ACCOUNTING-':
                get_code('qt-Accounting')
                window.Element('-ACCOUNTING-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-AU-':
                get_code('qt-AU')
                window.Element('-AU-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-ARRANGER-':
                get_code('qt-Arranger')
                window.Element('-ARRANGER-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-INTERN-':
                get_code('qt-Technology-Intern')
                window.Element('-INTERN-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-EXECUTION-':
                get_code('qt-Execution')
                window.Element('-EXECUTION-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-INTERNALLAW-':
                get_code('qt-InternalLaw')
                window.Element('-INTERNALLAW-').Update(button_color = ('#FFFFFF', ('red')))
            if event == '-START-':
                run_popup_monitor()
                window.Element('-TECH-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-LAW-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-DESIGN-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-HR-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-ONLINEBUSINESS-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-OPERATION-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-PROJECT-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-SALE-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-BOD-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-ACCOUNTING-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-AU-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-ARRANGER-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-INTERN-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-EXECUTION-').Update(button_color = ('#FFFFFF', ('#658268')))
                window.Element('-INTERNALLAW-').Update(button_color = ('#FFFFFF', ('#658268')))

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

def run_popup_monitor():        
    try:
        #str_checkname = get_checkname()[0]
        str_checkname = ['tech04.qtdata_Thomas']
    except:
        #sg.Popup('Error: list_checkname has no value.', title = 'Tempo Monitor', keep_on_top = True)
        add_checkname(utils.username)
        str_checkname = get_checkname()[0]
    my_level = pd.read_sql("select CLASS from {} where code like '{}'"\
                     .format(utils.db_memberinfo,utils.username), utils.ENGINE)['class'][0]
    window = create_window_monitor(str_checkname, my_level)
    monitor_start = time.time()
    timer_monitor = utils.timer_monitor
    popup_first_run = True
    #check online
    df_online = pd.read_sql(
        "select * from {} where to_char(NAME) in {} "\
        "and DATETIME in (select max(DATETIME) from {} group by to_char(NAME))"\
        .format(utils.db_tempomonitor, str_checkname, utils.db_tempomonitor), utils.ENGINE)
    df_online.columns = [x.upper() for x in df_online.columns]
    df_online.sort_values(by='DATETIME', inplace=True, ascending=True)
    df_online.drop_duplicates(subset=['NAME'],keep='last',inplace=True)
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
                    df_monitor.sort_values(by='DATETIME', inplace=True, ascending=True)
                    df_monitor.drop_duplicates(subset=['NAME'],keep='last',inplace=True)

                    #Current Task
                    df_task = pd.read_sql(
                        "select * from {} where to_char(ASSIGNEE) in {} and STATUS like 'In Progress'"\
                        .format(utils.db_task, str_checkname), utils.ENGINE)
                    df_task.columns = [x.upper() for x in df_task.columns]
                                   
                    #Current Note    
                    df_note = pd.read_sql(
                        "select * from {} where to_char(NAME) in {} "\
                        "and DATETIME in (select max(DATETIME) from {} group by to_char(NAME))"\
                        .format(utils.db_temponote, str_checkname, utils.db_temponote), utils.ENGINE)
                    df_note.columns = [x.upper() for x in df_note.columns]
                    df_note.sort_values(by='DATETIME', inplace=True, ascending=True)
                    df_note.drop_duplicates(subset=['NAME'],keep='last',inplace=True)
                    df_note = df_note[['NAME', 'NEXTACT', 'OUTCOME']]
                                             
                    df = pd.merge(df_monitor, df_task, how = 'outer', left_on = 'NAME', right_on = 'ASSIGNEE')
                    df = pd.merge(df, df_note, how = 'outer', on = 'NAME')
                    df.replace([None], 'None', inplace = True)
                    df = df.sort_values(by=['NAME'])
                   
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
                        current_note = df['NEXTACT'][i]

                        try:
                            window.Element('name{}'.format(i)).Update(name)
                            window.Element('doing_task{}'.format(i)).Update(doing_task)
                            window.Element('doing_task{}'.format(i)).set_tooltip(task_content)
                            window.Element('current_note{}'.format(i)).Update(current_note)
                            circle = window['circle-icon{}'.format(i)]         # type: sg.Graph
                            if df['TIME'][i] == df_online['TIME'][i]:
                                circle.draw_circle((6, 5), 5, fill_color='gray', line_color='gray')
                            else:
                                circle.draw_circle((6, 5), 5, fill_color='green', line_color='green')
                                df_online = df_monitor
                        except:
                            pass
                        
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
      
#select follow team get to list_checkname.txt
def get_code(name):
    file_path = utils.path_checkname
    df = pd.read_sql(" SELECT CODE FROM {} WHERE  DEPARTMENT  LIKE '{}'".format(utils.db_memberinfo, name), utils.ENGINE)
    file = open(file_path,"r+")
    file.truncate(0)
    file.close()
    arr_name = []
    check_name = open(file_path,'w')
    for i in df.index:
        arr_name.append(df['code'][i])
    arr_name = "', '".join(arr_name)    
    arr_name = "('{}')".format(arr_name)
    check_name.write(arr_name)
    check_name.close()          
    return arr_name


if args.capture_images == 'on':
    capture_images(total_secs, utils.timer_monitor, utils.timer_thumbsup)

if args.popup_note == 'on':
    run_popup_note(total_secs, utils.timer_popup, utils.timer_action, utils.timer_exist)

if args.popup_monitor == 'on':
    my_level = pd.read_sql("select CLASS from {} where code like '{}'"\
                     .format(utils.db_memberinfo,utils.username), utils.ENGINE)['class'][0]
    if args.style == 'compact':
        run_popup_monitor_compact()
    if my_level == 1 and args.style == 'all' :
        run_team_popup()
    else:
        run_popup_monitor()    