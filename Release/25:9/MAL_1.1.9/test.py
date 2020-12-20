#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 22:02:41 2020

@author: phungan
"""

                    date = datetime.now()
                    path = utils.path_output + '{}_{}/'.format(date.strftime("%Y-%m-%d").upper(), utils.username)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    date_position = (20,50)
                    with imageio.get_writer( path +'webcams_screens.gif', mode='I', fps=5) as writer_screen:
                        screen = imageio.imread(base64.b64decode(screen_b64))
                        webcam = imageio.imread(base64.b64decode(frame_b64))
                        crop_webcam = webcam[100:800, 400:1100]
                        crop_webcam = crop_webcam.resize((1440, 900), Image.ANTIALIAS)
                        concat_image = cv2.hconcat([ crop_webcam,crop_webcam])
                        cv2.putText(
                          concat_image, #numpy array on which text is written
                          "{}".format(date.strftime("%Y-%m-%d %H:%M:%S").upper()), #text
                          date_position, #position at which writing has to start
                          cv2.FONT_HERSHEY_SIMPLEX, #font family
                          2, #font size
                          (0,0,255), 3
                          )
                        
                        writer_screen.append_data(concat_image)
                    writer_screen.close()
                    
                    
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
                video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                
            ret, frame = video_capture.read()
            time.sleep(1)
            video_capture.release()

            #Convert to PIL Image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            
        except:
            frame = screen
        
        #Resize
        frame = frame.resize((1440, 900), Image.ANTIALIAS)
        screen = screen.resize((1440, 900), Image.ANTIALIAS)
        #Encode to string
        frame_b64 = encode_b64(frame)
        screen_b64 = encode_b64(screen)
        
    except:
        log_temponote.warning('Cannot capture images!')
        log_temponote.warning(traceback.format_exc())
        frame_b64 = 'None'
        screen_b64 = 'None'
        
    return frame_b64, screen_b64
    

                    with imageio.get_writer( path +'webcams_screens.gif', mode='I', fps=5) as writer_screen:
                        screen = imageio.imread(base64.b64decode(screen_b64))
                        webcam = imageio.imread(base64.b64decode(frame_b64))
                        concat_image = cv2.hconcat([ webcam,screen])
                        cv2.putText(
                          concat_image, #numpy array on which text is written
                          "{}".format(date.strftime("%Y-%m-%d %H:%M:%S").upper()), #text
                          date_position, #position at which writing has to start
                          cv2.FONT_HERSHEY_SIMPLEX, #font family
                          2, #font size
                          (0,0,255), 2
                          )
                        writer_screen.append_data(concat_image)
                    writer_screen.close()