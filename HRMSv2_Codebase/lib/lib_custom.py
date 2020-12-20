def read_file_googlesheet(SAMPLE_SPREADSHEET_ID,SAMPLE_RANGE_NAME):
    #pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    import pickle
    import os.path
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [0])
    headers = values.pop(0)
    
    return values, headers

def get_todo_list_in_tempo5000(username):
    import datetime
    import pandas as pd
    #get current day (type 22/7)
    dt = datetime.datetime.today()
    current_date = str(dt.day) + "/" + str(dt.month)
    values, headers = read_file_googlesheet("1gzbkiGtn3FhcfY3xiThQli8TXazrdCQ-1a3MUIVpz5Q", current_date)
    i = 0
    for val in headers:
        val = str(val)
        if not val and i == 0:
            headers[i] = "TIME"
        if not val and i > 0:
            headers[i] = headers[i-1]
        if headers[-1] == val:  
            last_arr = [val, val, val]
            headers = headers + last_arr
        i += 1
    df = pd.DataFrame(values, columns = headers)
    df_todo = df[username].iloc[2]
    return df_todo.iloc[2]


def get_all_image_working(name):
    import pandas as pd
    import utils
    import PySimpleGUI as sg
    import base64
    import imageio

    def decode_b64():
        print('error')
    
    name = name.upper()
    df_gif_working = pd.read_sql("select * from {} where NAME like '{}'".format(utils.db_image_working, name), utils.ENGINE)
    with imageio.get_writer('{}_screens.gif'.format(name), mode='I', fps=5) as writer_screen:
        for filename in df_gif_working['screen']:
            image = imageio.imread(decode_b64(filename))
            writer_screen.append_data(image)
    with imageio.get_writer('{}_webcam.gif'.format(name), mode='I', fps=5) as writer_webcam:
        for filename in df_gif_working['webcam']:
            image = imageio.imread(decode_b64(filename))
            writer_webcam.append_data(image)
    with open("{}_screens.gif".format(name), "rb") as image_file:
        encoded_screen = base64.b64encode(image_file.read())
    with open("{}_webcam.gif".format(name), "rb") as image_file:
        encoded_webcam = base64.b64encode(image_file.read())

    layout = [[sg.Text('Screens', font='ANY 15')],
              [sg.Image(data=encoded_screen, key='_IMAGE_SC_')],
              [sg.Text('Webcams', font='ANY 15')],
              [sg.Image(data=encoded_screen, key='_IMAGE_WC_')],
              [sg.Button('Cancel')]
              ]
    window = sg.Window('My new window').Layout(layout)
    while True:  # Event Loop
        event, values = window.Read(timeout=25)
        if event in (None, 'Exit', 'Cancel'):
            break
        window.Element('_IMAGE_SC_').UpdateAnimation(encoded_screen, time_between_frames=280)
        window.Element('_IMAGE_WC_').UpdateAnimation(encoded_webcam, time_between_frames=280) 
        

def get_credentials():
    import pickle
    import os.path
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    creds = None
    # If modifying these scopes, delete the file token.pickle.'
    SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets'  ]
    try:
        if os.path.exists('./config/token.pickle'):
            with open('./config/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './config/screds.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('./config/token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds
    except Exception:
        return Exception


def export_temponote():
    import pickle
    import os.path
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import webbrowser
    import pandas as pd
    import utils
    import numpy as np
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets']
    try:
        if os.path.exists('./config/token.pickle'):
            with open('./config/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './config/screds.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('./config/token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        #service sheet
        googlesheet_service = build('sheets', 'v4', credentials=creds)
        
        df = pd.read_sql("SELECT name, datetime, time, activity, outcome FROM {} ORDER BY to_char(name), datetime".format(utils.db_temponote), utils.ENGINE)
        #df_name = df.groupby('name').agg({'activity':lambda x: list(x),'outcome':lambda y: list(y)})
        df['time'] = df['time'].astype(str)    
        df['datetime'] = df['datetime'].astype(str)    
        df.replace(np.nan, '', inplace=True)
        df.columns = [x.upper() for x in df.columns]
        #craeate new sheet
        sheet_temponotes = googlesheet_service.spreadsheets().create(body={ 'properties': {'title': 'All temponote'}}).execute()
        #export data df to sheet
        googlesheet_service.spreadsheets().values().append(
            spreadsheetId=sheet_temponotes['spreadsheetId'],
            valueInputOption='RAW',
            range='A1:A1',
            body=dict(
                majorDimension='ROWS',
                values=df.T.reset_index().T.values.tolist())
        ).execute()
        #open in browser
        url ='https://docs.google.com/spreadsheets/d/{}/edit#gid=0'.format(sheet_temponotes['spreadsheetId'])
        return webbrowser.open(url)
    except:
        return "Fails"
def action_thumbup():
    import PySimpleGUI as sg 
    import utils
    import sys
    import pandas as pd
    import time
    from datetime import datetime
    from playsound import playsound
    def create_window_action():
        sg.theme('Tanblue')
    
    
        if sys.platform != 'win32':
            sg.set_options(font = ('Helvetica', 13))
        text = [ 
                [sg.Text(key = '-NAME-',size=(18,1), text_color = 'red')],
                [sg.Text(key = '-OUTPUT-',size=(20,10))],          
            ]
        layout = [
            
            [sg.Column(text,size=(200,150), vertical_scroll_only=True, visible=True, scrollable = True)],
            [sg.Button(key = '-THUMBUP-',border_width = 0,button_color =('#C0FFEE','#C0FFEE'),image_filename = 'thumbup/iconthumbup.png',image_size=(50, 35))]
        ]
    
        window = sg.Window(
            'Action Popup',
            layout,
            disable_close = True,
            keep_on_top = True,
            finalize = True,
            location = (sg.Window.get_screen_size()[0] - 245, 0)
        )   
        return window
        
    def run_action_thumbup():   
        popup_first_run = True
        popup_start = time.time()
        while True:
            if time.time() > popup_start + utils.timer_thumbup or popup_first_run:
    
                popup_start = time.time()
                end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                conver_end_datetime = time.mktime(time.strptime(end_datetime, '%Y-%m-%d %H:%M:%S'))
                conver_start_datetime = conver_end_datetime - 60*60
                start_datetime = datetime.fromtimestamp(conver_start_datetime).strftime('%Y-%m-%d %H:%M:%S')
                
                df = pd.read_sql("select * from {} where DATETIME BETWEEN TO_DATE {} AND TO_DATE {}"\
                .format(utils.db_testaction,(start_datetime,'YYYY-MM-DD HH24:MI:SS'),(end_datetime,'YYYY-MM-DD HH24:MI:SS')),utils.ENGINE)
    
                df.columns = [x.upper() for x in df.columns]
                              
                for idx, row in df.iterrows():  
                    
                    list_user_thumbup = str(df['THUMBUP'][idx])
                    list_user_thumbup = list_user_thumbup.split(',')
                    
                    if not utils.username in list_user_thumbup:
                        window = create_window_action()
                        playsound('thumbup/thumbup.mp3')
                        while True:
                            
                            event, values = window.read(timeout = 100)
                            action = df['ACTION'][idx]
                            name = df['NAME'][idx]
                            window['-NAME-'].update('{}'.format(name)) 
                            window['-OUTPUT-'].update('{}'.format(action))
    
                            if event == '-THUMBUP-':
    #                            playsound('thumbup/thumbup_exits.mp3')
                                popup_first_run = False
                                
                                df_thumbup = pd.DataFrame(columns = ['action','activities','datetime','name', 'outcomes', 'thumbup', 'time'])
                                df_thumbup.loc[idx,'action'] =  df['ACTION'][idx]
                                df_thumbup.loc[idx,'activities'] =  df['ACTIVITIES'][idx]
                                df_thumbup.loc[idx,'datetime'] =  df['DATETIME'][idx]
                                df_thumbup.loc[idx,'name'] =  df['NAME'][idx]
                                df_thumbup.loc[idx,'outcomes'] =  df['OUTCOMES'][idx]
    
                                if df['THUMBUP'][idx] == None:
                                    df_thumbup.loc[idx,'thumbup'] = utils.username
                                else: 
                                    df_thumbup.loc[idx,'thumbup'] =  df['THUMBUP'][idx]+','+ utils.username
    
                                df_thumbup.loc[idx,'time'] =  df['TIME'][idx]
                                format_date = df['DATETIME'][idx].strftime('%Y-%m-%d %H:%M:%S')
                                utils.ENGINE.execute("delete from {} where THUMBUP like '{}' AND DATETIME like TO_DATE {} "\
                                 .format(utils.db_testaction, df['THUMBUP'][idx], (format_date,'YYYY-MM-DD HH24:MI:SS')))
    #                            df.to_excel('t1.xlsx', index = False)
                                df_thumbup.to_sql(utils.db_testaction, utils.ENGINE, if_exists = 'append', index = False)
                                
                                window.Close()
                                time.sleep(15)
                                break
                    else:
                       popup_first_run = False
    #     
    #def test():
    #    df_thumbup = pd.DataFrame(columns = ['action','activities','datetime','name', 'outcomes', 'thumbup', 'time'])
    #    df_thumbup.loc[0,'action'] =  'thong bao20'
    #    df_thumbup.loc[0,'activities'] =  'thong bao'
    #    df_thumbup.loc[0,'datetime'] =  datetime.now()
    #    df_thumbup.loc[0,'name'] =  'tech02_Nathan'
    #    df_thumbup.loc[0,'outcomes'] =  'thong bao'
    #    df_thumbup.loc[0,'thumbup'] = 'tech04_Thomas'
    #    df_thumbup.loc[0,'time'] =  datetime.now().strftime('%H:%M:%S')
    #    df_thumbup.to_sql(utils.db_testaction, utils.ENGINE, if_exists = 'append', index = False)
    if __name__ == "__main__":
        run_action_thumbup()
    #    test()
def Tech10_Yamar():
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
    parser.add_argument('-c', '--capture-images', help = 'Capture images', default = 'off')
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
        X1 = 10
        Y1 = 290
        X2 = 710
        Y2 = 990
    
        #Grabbing images
        try:
            screen = ImageGrab.grab(bbox=(X1,Y1,X2,Y2))
        
            video_capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)
            try:
                ret, frame = video_capture.read()
                frame = frame[X1:X2, Y1:Y2]
                #Convert to PIL Image
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = Image.fromarray(frame)
            except:
                frame = screen
                log_temponote.warning(traceback.format_exc())
                pass
            
            video_capture.release()
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
        
        count = 0
        while monitor_start <= timer_end:
            try:
                #Capture image
                if time.time() > monitor_start + timer_monitor or popup_first_run:
                    monitor_start = time.time()
                    popup_first_run = False
                    count += 1
                    log_temponote.warning(count)
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
            finalize = True
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
                sg.Text(key = 'current_note{}'.format(i), size = (20, 2))
            ])
            
            check_user.append([
                sg.Image(key = 'webcam{}'.format(i),size = (None, 100)),
                sg.Image(key = 'screen{}'.format(i),size = (None, 100))
            ])
        
            #Táº¡o thanh scroll khi display khi cÃ³ 3 member trÃªn tempomonitor 
        if len(list_checkname) >= 3:
            layout = [[sg.Column(check_user, size=(250,260), vertical_scroll_only=True, visible=True, scrollable = True)]]
        else:
            layout = check_user
            
    #    layout = [
    #        *check_user
    #    ]
        
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