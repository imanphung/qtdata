import PySimpleGUI as sg
import os, sys
import subprocess, psutil, signal

import utils
    


def launcher():
    #Init
    version = 'v1.1.8'
    
    temponote_off = True
    tempomonitor_off = True
    list_debugger_pid = []
    
    sg.theme('TanBlue')
    
    #Comment next 2 lines or change the number if window size is too big/small
    if sys.platform != 'win32':
        sg.set_options(font = ('Helvetica', 13))
    
    layout = [
        [sg.Text('>> MI AN LIEN <<', font = ('Helvetica', 20, 'bold'))],
        [sg.Text('{}'.format(version), font = ('Helvetica', 13))],
        [sg.Text('Hello, {}!'.format(utils.username), font = ('Helvetica', 15), text_color = 'red')],
        [sg.Text('Input your working time (in hrs)')],
        [sg.InputText(key = '-WORKINGTIME-', default_text = '1', size = (15, 1), justification = 'center')],
        [sg.Text('')],
        [
            sg.Button(key = '-START-', button_text = 'Start'),
            sg.Button(key = '-TEMPONOTE-', button_text = 'Start TempoNote'),
            sg.Button(key = '-DEBUGGER-', button_text = 'Ask Noawan'),
            sg.Button(key = '-TEMPOMONITOR-', button_text = 'Start TempoMonitor')
        ],
        [sg.Text('')],
    ]
        
    win_main = sg.Window(
        'HRMSv2 Codebase',
        layout,
        element_justification = 'center',
        keep_on_top = True,
        finalize = True
    )
    
    while True:
        try:
            event, values = win_main.read(timeout = 100)
            if event == sg.TIMEOUT_KEY:
                pass
            
            if event == '-START-':
                win_main.Element('-WORKINGTIME-').Update(text_color = '#8A8A84', disabled = True)
                if temponote_off is True:
                    event = '-TEMPONOTE-'
                    
            if event == '-DEBUGGER-':
                #Start new temponote process
                debugger_pid = execute_command(
                    'Debugger',                    
                    'python', './debugger.py', '-s {}'.format(utils.server_status)
                )
                list_debugger_pid.append(debugger_pid)

            if event == '-TEMPONOTE-':
                temponote_off = not temponote_off
                win_main.Element('-TEMPONOTE-').Update(
                    ('Stop TempoNote', 'Start TempoNote')[temponote_off],
                    button_color = (('#FFFFFF', ('red', '#063289')[temponote_off]))
                )
                                    
                #Start new temponote process
                if temponote_off is False:
                    total_time = values['-WORKINGTIME-']
                    temponote_pid = execute_command(
                        'TempoNote',                                
                        'python', './popup_tempo.py', '-n on',
                        '-s {}'.format(utils.server_status), '-t {}'.format(total_time)
                    )
                    capimgs_pid = execute_command(
                        'Capture Images',                                
                        'python', './popup_tempo.py', '-c on',
                        '-s {}'.format(utils.server_status), '-t {}'.format(total_time)
                    )
                else:
                    #Kill current temponote and capimgs process if it is running
                    kill_processtree('Capture Images', capimgs_pid)
                    kill_processtree('TempoNote', temponote_pid)
                    
            if event == '-TEMPOMONITOR-':
                tempomonitor_off = not tempomonitor_off
                win_main.Element('-TEMPOMONITOR-').Update(
                    ('Stop TempoMonitor', 'Start TempoMonitor')[tempomonitor_off],
                    button_color = (('#FFFFFF', ('red', '#063289')[tempomonitor_off]))
                )
                                    
                #Start new tempomonitor process
                if tempomonitor_off is False:
                    tempomonitor_pid = execute_command(
                        'TempoMonitor',                                   
                        'python', './popup_tempo.py', '-m on',
                        '-s {}'.format(utils.server_status), '-style {}'.format(utils.monitor_style)
                    )
                else:
                    #Kill current tempomonitor process if it is running
                    kill_processtree('TempoMonitor', tempomonitor_pid)
            
            if event == sg.WIN_CLOSED:
                #Kill all debugger process in list
                if len(list_debugger_pid) > 0:
                    for pid in list_debugger_pid:
                        kill_processtree('Debugger', pid)
                
                if temponote_off is False:
                    kill_processtree('Capture Images', capimgs_pid)
                    kill_processtree('TempoNote', temponote_pid)
                    
                if tempomonitor_off is False:
                    kill_processtree('TempoMonitor', tempomonitor_pid)
    
                print('-- STOP HRMSv2_Codebase --')
                win_main.Close()
                break
                
        except Exception as e:
            print(e)
            
            if len(list_debugger_pid) > 0:
                for pid in list_debugger_pid:
                    kill_processtree('Debugger', pid)
            
            if temponote_off is False:
                kill_processtree('Capture Images', capimgs_pid)
                kill_processtree('TempoNote', temponote_pid)
                
            if tempomonitor_off is False:
                kill_processtree('TempoMonitor', tempomonitor_pid)
                
            print('-- STOP HRMSv2_Codebase --')     
            win_main.Close()

    
def execute_command(display_name, command, *args, communicate = False):      
    try:
#        print(command + ' ' + ' '.join(list(args)))
        p = psutil.Popen(
            command + ' ' + ' '.join(list(args)),
            shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
        )      

        if communicate:      
            out, err = p.communicate()      
            if out:      
                print(out.decode('utf-8'))      
            if err:      
                print(err.decode('utf-8'))
                
        print('{} start: {}'.format(display_name, p.pid))
        
    except Exception as e:
        print(e)
        pass
    
    return p.pid
    

def kill_processtree(display_name, pid, sig = signal.SIGTERM, include_parent = True, timeout = None, on_terminate = None):
    """
    Kill a process tree (including grandchildren) with signal "sig".
    "on_terminate", if specified, is a callabck function which is called as soon as a child terminates.
    """
    try:
        if pid == os.getpid():
            raise RuntimeError("I refuse to kill myself")
        parent = psutil.Process(pid)
        children = parent.children(recursive = True)
        if include_parent:
            children.append(parent)
        for p in children:
            p.send_signal(sig)
        
        print('{} kill: {}'.format(display_name, pid))
        
    except Exception as e:
        print(e)
        pass
        
    
if __name__ == '__main__':
    launcher()
    
    
    
    
    