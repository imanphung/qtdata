def init_lib_database():
    return 'init_lib_database'
    
#import random, os, sys, time
#import pandas as pd
#import numpy as np
#from datetime import datetime
#from selenium import webdriver
#from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.keys import Keys
#
#import utils    
#from lib import lib_sys
#
#
#
#option = Options()
#option.add_argument('--disable-infobars')
#option.add_argument('--disable-notifications') 
## option.add_argument('start-maximized')
#option.add_argument('--disable-extensions')
## Pass the argument 1 to allow and 2 to block
#option.add_experimental_option('prefs', {'profile.default_content_setting_values.notifications': 1})
#
#implicit_time = 10
#
#
#def send_linkedin(browser, linkedin, message, min_delay = 3):
#    browser.get(linkedin)
#    time.sleep(random.uniform(min_delay, min_delay + 3))
#    
#    #Customize message
#    name = browser.find_element_by_xpath('//li[@class="inline t-24 t-black t-normal break-words"]').text
#    message = message.replace('@name', name)
#    
#    checkProfileActions = browser.find_element_by_class_name('pv-s-profile-actions')
#    #If Message not locked
#    if 'pv-s-profile-actions--message' in checkProfileActions.get_attribute('class').split():
#        browser.find_element_by_class_name('pv-s-profile-actions--message').click()
#        browser.implicitly_wait(implicit_time)
#
#        actions = ActionChains(browser)
#        for part in message.split('\n'):
#            actions.send_keys(part)
#            actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
#                      
#        actions.perform()
#        time.sleep(1)
#
#        browser.find_element_by_class_name('msg-form__send-button').click()
#        
#        #If Follow is required
##        browser.find_element_by_class_name('pv-s-profile-actions--follow').click()
##        browser.implicitly_wait(implicit_time)
#
#        # Connect
#        # checkSentButton = browser.find_element_by_class_name('ml1')
#        # if 'artdeco-button--disabled' in checkSentButton.get_attribute('class').split():
#        #     browser.find_element_by_class_name('artdeco-modal__dismiss').click()
#        #     browser.find_element_by_class_name('pv-s-profile-actions--message').click()
##             browser.implicitly_wait(implicit_time)
#        #     if True == check_exists_class('msg-form__subject'):
#        #         browser.find_element_by_class_name('msg-form__subject').send_keys(subject)
#        #     if True == check_exists_class('msg-form__contenteditable'):
#        #         browser.find_element_by_class_name('msg-form__contenteditable').send_keys(message)
##             browser.implicitly_wait(implicit_time)
#        #     if True == check_exists_class('msg-form__send-button'):
#        #         browser.find_element_by_class_name('msg-form__send-button').click()
#        # else:
#        #     checkSentButton.click()
#            
#    # If Message is locked
#    else:
#        browser.find_element_by_class_name('pv-s-profile-actions__overflow-toggle').click()
#        browser.implicitly_wait(implicit_time)
#        
#        browser.find_element_by_class_name('pv-s-profile-actions--connect').click()
#        browser.implicitly_wait(implicit_time)
#        
#        browser.find_element_by_xpath("//button[contains(@aria-label, 'Add a note')]").click()
#        browser.implicitly_wait(implicit_time)
#        
#        actions = ActionChains(browser)
#        for part in message.split('\n'):
#            actions.send_keys(part)
#            actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
#                      
#        actions.perform()
#        time.sleep(1)
#        
#        browser.find_element_by_class_name('ml1').click()
#    
#    return name
#
#    
#df = pd.read_sql('select * from LINKEDIN_DB where rownum <= 10', utils.ENGINE)   
#    
#    
#def run_linkedin_message(min_delay = 3):
#    log = '' 
#    
#    path = lib_sys.get_filepath('xlsx')
#
#    if path is None or len(path) == 0:
#        return 'No file selected.'
#        
#    df_login = pd.read_excel(path, 'LOGIN')
#    df_message = pd.read_excel(path, 'MESSAGE')
#    df_data = pd.read_excel(path, 'DATA')
#    
#    #Init
#    linkedin_link = 'https://www.linkedin.com/uas/login'
#    username = df_login['USERNAME'][0]
#    password = df_login['PASSWORD'][0]
#    message = df_message['CONTENT'][0]
#
#    #Open link on chrome
#    if sys.platform == 'win32':
#        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
#    else:
#        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac
#
#    browser.get(linkedin_link)
#    browser.implicitly_wait(implicit_time)
#
#    #Access account
#    log += 'Login to Linkedin.\n'
#    try:
#        elementID = browser.find_element_by_id('username')
#        browser.implicitly_wait(implicit_time)
#        elementID.send_keys(username)
#        
#        elementID = browser.find_element_by_id('password')
#        browser.implicitly_wait(implicit_time)
#        elementID.send_keys(password)
#        
#        elementID.submit()
#        
#    except:
#        browser.quit()
#        log += 'Login failed!\n'
#        return log
#     
#    time.sleep(random.uniform(min_delay, min_delay + 3))
#    
#    log += 'Linkedin MessageBot: START\n'
#    for idx, row in df_data.iterrows():
#        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
#        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
#        
#        try:
#            linkedin = row['LINKEDIN']
#            status = row['STATUS']
#            
#            if status != 'sent':
#                name = send_linkedin(browser, linkedin, message, min_delay)
#                
#                df_data.loc[idx, 'NAME'] = name
#                df_data.loc[idx, 'STATUS'] = 'sent'
#                log += '{}: sent\n'.format(linkedin)
#                
#            #Sleep to make sure everything loads
#            time.sleep(random.uniform(min_delay, min_delay + 3))
#    
#        except Exception as e:
#            df_data.loc[idx, 'STATUS'] = e
#            log += '{}: error\n'.format(linkedin)
#            continue
#
#    browser.quit()
#    
#    #Update database
#    with pd.ExcelWriter(path) as writer:  
#        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
#        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
#        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
#    writer.close()
#
#    log += 'Linkedin MessageBot: DONE.\n'
#    
#    return log