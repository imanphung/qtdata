def hello(text = 'Hello, world!'):
    return text


def hi():
    return 'Hi there!'


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