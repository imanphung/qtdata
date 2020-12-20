import sys, io, string, datetime, re, time, asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from skpy import Skype, SkypeMsg, SkypeGroupChat, SkypeChats, SkypeChat
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

def convert_to_array(input_str):
    return input_str.strip('][').split(',')

def connect_skype(username, password):
    
    path_skype_secret = './modules/client_secret.json'
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(path_skype_secret, scope)
    client = gspread.authorize(creds)
    # connect to Skype
    sk = Skype(username, password)
    #SKYPE = sk.conn.liveLogin(username, password)
    print('Connecting to skype.')
    return sk

def add_remove_skype_members():   
    log = '' 
    path = './modules/skype.xlsx'
    df_login = pd.read_excel(path, 'login')
    df_login.columns = [x.upper() for x in df_login.columns]
    
    #Connect skype
    SKYPE = connect_skype(df_login['USERNAME'][0], df_login['PASSWORD'][0])

    df_members_info = pd.read_excel(path, 'members_info')
    df_members_info.columns = [x.upper() for x in df_members_info.columns]
    df_groups_info = pd.read_excel(path, 'groups')
    df_groups_info.columns = [x.upper() for x in df_groups_info.columns]
    df_configs_info = pd.read_excel(path, 'configs')
    df_configs_info.columns = [x.upper() for x in df_configs_info.columns]

    for idx, member_info in df_members_info.iterrows():
        if member_info['STATUS'] != 'done':
            #get member info
            team_member = member_info['TEAM']
            action = member_info['ACTION'].upper()
            list_idx_config = convert_to_array(member_info['IDX_CONFIG'])
            list_group = []
            flag = True
            error = ''
            
            #get list groups in list configs
            for idx_config in list_idx_config:
                for _,config_info in df_configs_info.iterrows():
                    if config_info['IDX'] == int(idx_config):
                        list_idx_group = convert_to_array(config_info['IDX_GROUP'])
                        [list_group.append(x) for x in list_idx_group]
            
            #connect groups
            for idx_group in list_group:
                for _, group_info in df_groups_info.iterrows():
                    if group_info['IDX'] == int(idx_group):
                        # get group id
                        ch = SKYPE.chats
                        group_id = ch.urlToIds(group_info['GROUP_LINK'])
                        skc = SkypeChats(SKYPE)
                        group_chat = skc.chat(group_id['id'])
                        
                        #add member to this group
                        if action == 'ADD':
                            try:
                                #add member with user role
                                group_chat.addMember(member_info['SKYPE_ID'], False)
                                log += '{}: added to {}\n'.format(member_info['NAME'], group_info['NAME'])
                            except:
                                flag = False
                                error += str(group_info['IDX']) + ','
                                log += '{}: error add to {}\n'.format(member_info['NAME'], group_info['NAME'])
                        
                        #remove member from this group
                        elif action == 'REMOVE':
                            try:
                                #remove member
                                group_chat.removeMember(member_info['SKYPE_ID'])
                                log += '{}: removed from {}\n'.format(member_info['NAME'], group_info['NAME'])
                        
                            except:
                                flag = False
                                error += str(group_info['IDX']) + ','
                                log += '{}: error remove from {}\n'.format(member_info['NAME'], group_info['NAME'])
                
                        else:
                            log += 'No action'
        
            if flag == True:
                df_members_info.loc[idx, 'STATUS'] = 'done'
            else:
                df_members_info.loc[idx, 'STATUS'] = 'error from: ' + error

        #Update database
    with pd.ExcelWriter(path) as writer:
        df_login.to_excel(writer, sheet_name = 'login', index = False)
        df_groups_info.to_excel(writer, sheet_name = 'groups', index = False)
        df_configs_info.to_excel(writer, sheet_name = 'configs', index = False)
        df_members_info.to_excel(writer, sheet_name = 'members_info', index = False)
    writer.close()

async def main():
    # use creds to create a client to interact with the Google Drive API
    path = './modules/skype.xlsx'
    df_login = pd.read_excel(path, 'login')
    df_login.columns = [x.upper() for x in df_login.columns]
    
    #Connect skype
    SKYPE, CLIENT = connect_skype(df_login['USERNAME'][0], df_login['PASSWORD'][0])
    mysuser = SKYPE.user
    ch=SKYPE.chats
    df_members_info = pd.read_excel(path, 'members_info')
    df_members_info.columns = [x.upper() for x in df_members_info.columns]
    df_groups_info = pd.read_excel(path, 'groups')
    df_groups_info.columns = [x.upper() for x in df_groups_info.columns]
    df_configs_info = pd.read_excel(path, 'configs')
    df_configs_info.columns = [x.upper() for x in df_configs_info.columns]

    list_group_link = df_groups_info['GROUP_LINK']
    # Call back to handle message in all groups
    while True:
        for group_link in list_group_link[0:5]:
            await async_group_message(CLIENT, ch, group_link)
        time.sleep(300)

def update_task(userID, task, worksheet):
    # Find user
    user = worksheet.find(userID)
    column = int(user.col) -1
    old_task = worksheet.cell(4, column).value #Get old task
    if old_task == '':
        new_task = "'+ " + task
    else:
        new_task = old_task + chr(10) + "+ " + task
    print(userID)
    print(new_task)
    find_assign_task = worksheet.update_cell(4, column, new_task) # Update using cell

async def async_group_message(client, ch, group_link):
    groupid= ch.urlToIds(group_link)
    print(groupid["id"])
    ch2= ch.chat(groupid["id"])
    while True:
        now =datetime.datetime.utcnow()
        fiveminute= now - datetime.timedelta(minutes=5) # time to get task
        Mess= ch2.getMsgs() # Get 8 mess
        for j in Mess:
            if j.time >= fiveminute:    # in last 5 minute
                if j.content.find('#') == 0:  #task
                    print(j.content)
                    tasks = filter_task(j)
                    print(tasks)
                    if tasks == 0 : # Error syntax
                        print('error')
                        # alert_skype(j.user.name ch, False)

                    else:
                        #Find a workbook and open sheet by name
                        dt = datetime.datetime.today()
                        sheet_name = str(dt.day) + '/' + str(dt.month)
                        worksheet = client.open("Tempo 5000").worksheet(sheet_name)
                        #Update task for members on worksheet
                        for task in tasks:
                            update_task(task['userID'], task['task_content'], worksheet)
                            alert_skype(j.user.name, task['userID'], task['task_content'], ch, True)
                            print('Sent task to: ', task['userID'])
                else:
                    continue
        break

def filter_task(j):
    task_total = []
    task_key='# <at id="8:'
    hashtag_key = '<at id="8:'
    content = j.content
    while True:
        if content.find(task_key) != -1:
            start = content.find(task_key) + len(task_key)
            end = content.find('">')
            userID = content[start:end] # Find user id
            content = content[end + 2:] # Update content
            start = content.find('</at>') + 5 # Find task content of UserID above

            #Multi-task
            if content.find(hashtag_key) != -1:
                end = content.find(hashtag_key)
                task_content = content[start:end]
                if (task_content != ' '):
                    task_content += ' ' + str(j.time)

                #create tasks
                new_task = {
                    "userID" : userID,
                    "task_content" : task_content
                }

                if len(task_total) != 0 and task_total[-1]['task_content'] == ' ': #Task common 
                    task_total[-1]['task_content'] = task_content #Update taskcontent for member before
                    if new_task in task_total: #Syntax error
                        return 0
                task_total.append(new_task) # add task
                content = content[end:]
                task_key = hashtag_key #Update key

            # One task
            else:
                task_content = content[start:] + ' ' + str(j.time)
                new_task = {
                    "userID" : userID,
                    "task_content" : task_content
                }
                task_total.append(new_task)
                content=''

        # elif content.find('#') == 0: #Syntax error
        #   return 0
        else:
            return task_total

def alert_skype(leaderName,userID,Task, ch, status, user=None, time=None, content=None):
    idSkype='8:'+userID
    ch1= ch.chat(idSkype) # connect to chat using id
    now =datetime.datetime.now()

    #Alert to member
    if status == True:
        alert = 'You have a new Task from ' + SkypeMsg.bold(str(leaderName)) + chr(10) + SkypeMsg.bold(str(Task))
        ch1.sendMsg(alert, rich=True)
    #Alert to leader
    else:
        alert = SkypeMsg.quote(user, ch1, time1,content1)  + chr(10) + 'syntax error'
        ch1.sendMsg(alert, rich=True)

if __name__ == '__main__':
    #asyncio.run(main())
    add_remove_skype_members()