import random, os, sys, time
import pandas as pd
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import utils    
from lib import lib_sys



option = Options()
option.add_argument('--disable-infobars')
option.add_argument('--disable-notifications') 
# option.add_argument('start-maximized')
option.add_argument('--disable-extensions')
# Pass the argument 1 to allow and 2 to block
option.add_experimental_option('prefs', {'profile.default_content_setting_values.notifications': 1})

implicit_time = 10
  
    
def send_facebook_classic(browser, facebook, message, images, min_delay = 3):
    browser.get(facebook)
    time.sleep(random.uniform(min_delay, min_delay + 3))
        
    #Customize message
    name = browser.find_element_by_name('q').get_attribute('value')
    message = message.replace('@name', name)
    
    #Add friend
    elementID = browser.find_element_by_class_name('_42ft._4jy0.FriendRequestAdd.addButton._4jy4._517h._9c6')
    if elementID.is_displayed():
        elementID.click()
        time.sleep(2)
    
    #Get Facebook ID
    facebook_id = facebook.split('.com/',1)[1]
    if '?id=' in facebook_id:
        facebook_id = facebook_id.split('?id=',1)[1]

    browser.find_element_by_xpath('//a[@href="/messages/t/'+ facebook_id +'/"]').click()
    browser.implicitly_wait(implicit_time)
    
    #Attach images    
    for img in images:
        elementID = browser.find_element_by_xpath('//input[@name="attachment[]"]')
        elementID.send_keys(utils.path_media + img)
        time.sleep(1)
    
    actions = ActionChains(browser)
    for part in message.split('\n'):
        actions.send_keys(part)
        actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
                  
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    
    ActionChains(browser).send_keys(Keys.ESCAPE).perform()
    
    return name


def send_facebook(browser, facebook, message, images, min_delay = 3):
    browser.get(facebook)
    time.sleep(random.uniform(min_delay, min_delay + 3))
        
    #Customize message
    name = browser.find_element_by_xpath('//h1[@dir="auto"]').text
    message = message.replace('@name', name)
    
    #Add friend
    elementID = browser.find_element_by_xpath('//div[@class="k4urcfbm"]/div')
    if elementID.is_displayed():
        elementID.click()
        time.sleep(2)
    
    browser.find_element_by_xpath('//div[@class="h676nmdw"]/div/span/div').click()
    browser.implicitly_wait(implicit_time)
    
    #Attach images    
    for img in images:
        elementID = browser.find_element_by_xpath('//input[@class="mkhogb32"]')
        elementID.send_keys(utils.path_media + img)
        time.sleep(1)
    
    actions = ActionChains(browser)
    for part in message.split('\n'):
        actions.send_keys(part)
        actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
                  
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    
    ActionChains(browser).send_keys(Keys.ESCAPE).perform()
    
    return name
    
    
def run_facebook_message(layout = 'new', min_delay = 3):
    log = '' 
     
    path = lib_sys.get_filepath('xlsx')

    if path is None or len(path) == 0:
        return 'No file selected.'
        
    df_login = pd.read_excel(path, 'LOGIN')
    df_message = pd.read_excel(path, 'MESSAGE')
    df_data = pd.read_excel(path, 'DATA')
    
    #Init
    facebook_link = 'https://www.facebook.com/login'
    username = df_login['USERNAME'][0]
    password = df_login['PASSWORD'][0]
    message = df_message['CONTENT'][0]
    try:
        images = df_message['IMAGE'][0].split(', ')
    except:
        images = []
    
    #Open link on chrome
    if sys.platform == 'win32':
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
    else:
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac

    browser.get(facebook_link)
    browser.implicitly_wait(implicit_time)

    #Access account
    log += 'Login to Facebook.\n'
    try:
        elementID = browser.find_element_by_id('email')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(username)
        
        elementID = browser.find_element_by_id('pass')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(password)
        
        elementID.submit()
        
    except:
        browser.quit()
        log += 'Login failed!\n'
        return log
        
    time.sleep(random.uniform(min_delay, min_delay + 3))

    log += 'Facebook MessageBot: START\n'
    for idx, row in df_data.iterrows():
        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
        
        try:
            facebook = row['FACEBOOK']
            status = row['STATUS']
            
            if status != 'sent': 
                if layout == 'new':
                    name = send_facebook(browser, facebook, message, images, min_delay)
                else:
                    name = send_facebook_classic(browser, facebook, message, images, min_delay)
                
                df_data.loc[idx, 'NAME'] = name
                df_data.loc[idx, 'STATUS'] = 'sent'
                log += '{}: sent\n'.format(facebook)
                
            #Sleep to make sure everything loads
            time.sleep(random.uniform(min_delay + 3, min_delay + 7))
    
        except Exception as e:
            df_data.loc[idx, 'STATUS'] = e
            log += '{}: error\n'.format(facebook)
            continue

    browser.quit()
    
    #Update database
    with pd.ExcelWriter(path) as writer:  
        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
    writer.close()
    
    log += 'Facebook MessageBot: DONE.\n'
    
    return log    


def send_linkedin(browser, linkedin, message, min_delay = 3):
    browser.get(linkedin)
    time.sleep(random.uniform(min_delay, min_delay + 3))
    
    #Customize message
    name = browser.find_element_by_xpath('//li[@class="inline t-24 t-black t-normal break-words"]').text
    message = message.replace('@name', name)
    
    checkProfileActions = browser.find_element_by_class_name('pv-s-profile-actions')
    #If Message not locked
    if 'pv-s-profile-actions--message' in checkProfileActions.get_attribute('class').split():
        browser.find_element_by_class_name('pv-s-profile-actions--message').click()
        browser.implicitly_wait(implicit_time)

        actions = ActionChains(browser)
        for part in message.split('\n'):
            actions.send_keys(part)
            actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
                      
        actions.perform()
        time.sleep(1)

        browser.find_element_by_class_name('msg-form__send-button').click()
        
        #If Follow is required
#        browser.find_element_by_class_name('pv-s-profile-actions--follow').click()
#        browser.implicitly_wait(implicit_time)

        # Connect
        # checkSentButton = browser.find_element_by_class_name('ml1')
        # if 'artdeco-button--disabled' in checkSentButton.get_attribute('class').split():
        #     browser.find_element_by_class_name('artdeco-modal__dismiss').click()
        #     browser.find_element_by_class_name('pv-s-profile-actions--message').click()
#             browser.implicitly_wait(implicit_time)
        #     if True == check_exists_class('msg-form__subject'):
        #         browser.find_element_by_class_name('msg-form__subject').send_keys(subject)
        #     if True == check_exists_class('msg-form__contenteditable'):
        #         browser.find_element_by_class_name('msg-form__contenteditable').send_keys(message)
#             browser.implicitly_wait(implicit_time)
        #     if True == check_exists_class('msg-form__send-button'):
        #         browser.find_element_by_class_name('msg-form__send-button').click()
        # else:
        #     checkSentButton.click()
            
    # If Message is locked
    else:
        browser.find_element_by_class_name('pv-s-profile-actions__overflow-toggle').click()
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_class_name('pv-s-profile-actions--connect').click()
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_xpath("//button[contains(@aria-label, 'Add a note')]").click()
        browser.implicitly_wait(implicit_time)
        
        actions = ActionChains(browser)
        for part in message.split('\n'):
            actions.send_keys(part)
            actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
                      
        actions.perform()
        time.sleep(1)
        
        browser.find_element_by_class_name('ml1').click()
    
    return name

def run_linkedin_message(min_delay = 3):
    log = '' 
    
    path = lib_sys.get_filepath('xlsx')

    if path is None or len(path) == 0:
        return 'No file selected.'
        
    df_login = pd.read_excel(path, 'LOGIN')
    df_message = pd.read_excel(path, 'MESSAGE')
    df_data = pd.read_excel(path, 'DATA')
    
    #Init
    linkedin_link = 'https://www.linkedin.com/uas/login'
    username = df_login['USERNAME'][0]
    password = df_login['PASSWORD'][0]
    message = df_message['CONTENT'][0]

    #Open link on chrome
    if sys.platform == 'win32':
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
    else:
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac

    browser.get(linkedin_link)
    browser.implicitly_wait(implicit_time)

    #Access account
    log += 'Login to Linkedin.\n'
    try:
        elementID = browser.find_element_by_id('username')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(username)
        
        elementID = browser.find_element_by_id('password')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(password)
        
        elementID.submit()
        
    except:
        browser.quit()
        log += 'Login failed!\n'
        return log
     
    time.sleep(random.uniform(min_delay, min_delay + 3))
    
    log += 'Linkedin MessageBot: START\n'
    for idx, row in df_data.iterrows():
        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
        
        try:
            linkedin = row['LINKEDIN']
            status = row['STATUS']
            
            if status != 'sent':
                name = send_linkedin(browser, linkedin, message, min_delay)
                
                df_data.loc[idx, 'NAME'] = name
                df_data.loc[idx, 'STATUS'] = 'sent'
                log += '{}: sent\n'.format(linkedin)
                
            #Sleep to make sure everything loads
            time.sleep(random.uniform(min_delay + 3, min_delay + 7))
    
        except Exception as e:
            df_data.loc[idx, 'STATUS'] = e
            log += '{}: error\n'.format(linkedin)
            continue

    browser.quit()
    
    #Update database
    with pd.ExcelWriter(path) as writer:  
        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
    writer.close()

    log += 'Linkedin MessageBot: DONE.\n'
    
    return log
    

def send_gmail(browser, email, subject, message, min_delay = 3):
    browser.find_element_by_class_name('aic').click()
    browser.implicitly_wait(implicit_time)
    
    browser.find_element_by_xpath('//textarea[@rows="1"]').send_keys(email)
    browser.implicitly_wait(implicit_time)
    
    browser.find_element_by_xpath('//input[@name="subjectbox"]').send_keys(subject)
    browser.implicitly_wait(implicit_time)
    try:
        browser.find_element_by_xpath('//div[@aria-label="Message Body"]').send_keys(message)
        time.sleep(2)
        
        browser.find_element_by_xpath("//div[text()='Send']").click()
    except:
        browser.find_element_by_xpath('//div[@aria-label="Nội dung thư"]').send_keys(message)        
        time.sleep(2)
        
        browser.find_element_by_xpath("//div[text()='Gửi']").click()


def run_gmail_message(min_delay = 3):
    log = ''
    
    path = lib_sys.get_filepath('xlsx')

    if path is None or len(path) == 0:
        return 'No file selected.'
        
    df_login = pd.read_excel(path, 'LOGIN')
    df_message = pd.read_excel(path, 'MESSAGE')
    df_data = pd.read_excel(path, 'DATA')
    
    #Init
    stackOverflow_link = 'https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27'
    gmail_link = 'https://mail.google.com/mail/'
    username = df_login['USERNAME'][0]
    password = df_login['PASSWORD'][0]
    subject = df_message['SUBJECT'][0]
    message = df_message['CONTENT'][0]

    #Open link on chrome
    if sys.platform == 'win32':
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
    else:
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac

    #Access account
    log += 'Login to Gmail.\n'
    try:
        browser.get(stackOverflow_link)
        time.sleep(random.uniform(min_delay, min_delay + 4))
    
        browser.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()
        time.sleep(random.uniform(min_delay, min_delay + 2))
        
        browser.find_element_by_xpath('//input[@type="email"]').send_keys(username)
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_id('identifierNext').click()
        time.sleep(random.uniform(min_delay, min_delay + 2))
        
        browser.find_element_by_xpath('//input[@type="password"]').send_keys(password)
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_id('passwordNext').click()
        time.sleep(random.uniform(min_delay, min_delay + 2))
        
        browser.get(gmail_link)
        
    except:
        browser.quit()
        log += 'Login failed!\n'
        return log
        
    time.sleep(random.uniform(min_delay, min_delay + 3))
    #browser.find_element_by_xpath("//div[@data-tooltip='Sent']").click()
    
    log += 'Gmail MessageBot: START\n'
    for idx, row in df_data.iterrows():
        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
        
        try:
            email = row['EMAIL']
            status = row['STATUS']

            if status != 'sent':
                #Customize message
                name = str(row['NAME'])
                if name == 'nan':
                    subject = subject.replace('@subject', '')
                    message = message.replace('@name', '')
                else:
                    subject = subject.replace('@subject', name)
                    message = message.replace('@name', name)
                
                send_gmail(browser, email, subject, message, min_delay)
                
                df_data.loc[idx, 'STATUS'] = 'sent'
                log += '{}: sent\n'.format(email)
                
            #Sleep to make sure everything loads
            time.sleep(random.uniform(min_delay + 3, min_delay + 7))
                      
        except Exception as e:
            df_data.loc[idx, 'STATUS'] = e
            log += '{}: error\n'.format(email)
            continue

    browser.quit()
    
    #Update database
    with pd.ExcelWriter(path) as writer:  
        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
    writer.close()

    log += 'Gmail MessageBot: DONE.\n'
    
    return log
    

def send_hubspot(browser, email, subject, message, alias_number = 1, min_delay = 3):
    browser.find_element_by_xpath('//button[@data-test-id="compose-email-button"]').click()
    time.sleep(random.uniform(min_delay, min_delay + 2))
    
    element = browser.find_element_by_xpath('//span[contains(@class, "Select-multi-value-wrapper")]/div[2]/input')
    browser.implicitly_wait(implicit_time)
    element.send_keys(email)
    time.sleep(2)
    
    element.send_keys(Keys.ENTER)
    time.sleep(random.uniform(min_delay, min_delay + 2))
    
    try:
        browser.find_element_by_xpath('//span[@data-selenium-test="communicator-from-address"]/small/button').send_keys(Keys.ENTER)
        time.sleep(2)
        browser.find_element_by_xpath('//ul[@class="private-typeahead-results"]/li[{}]/span/button'.format(alias_number)).click()
        time.sleep(1)
    except:
       pass
        
    browser.find_element_by_xpath('//input[@data-selenium-test="email-subject-input"]').send_keys(subject)
    browser.implicitly_wait(implicit_time)
    
    browser.find_element_by_xpath(
        '//div[contains(@class, "rich-text-editor-input")]/div/div[1]/div/div/div/div/div'
    ).send_keys(message)
    time.sleep(2)
    
    browser.find_element_by_xpath('//button[contains(@data-selenium-test, "rich-text-editor-controls__save-btn")]').click()
    

def run_hubspot_message(alias_number = 1, min_delay = 3):
    log = ''
    
    path = lib_sys.get_filepath('xlsx')

    if path is None or len(path) == 0:
        return 'No file selected.'
        
    df_login = pd.read_excel(path, 'LOGIN')
    df_message = pd.read_excel(path, 'MESSAGE')
    df_data = pd.read_excel(path, 'DATA')
    
    #Init
    hubspot_link = 'https://app.hubspot.com/live-messages/'
    username = df_login['USERNAME'][0]
    password = df_login['PASSWORD'][0]
    subject = df_message['SUBJECT'][0]
    message = df_message['CONTENT'][0]

    #Open link on chrome
    if sys.platform == 'win32':
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
    else:
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac

    #Access account
    log += 'Login to Hubspot.\n'
    try:
        browser.get(hubspot_link)
        browser.implicitly_wait(implicit_time)
    
        browser.find_element_by_id('username').send_keys(username)
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_id('password').send_keys(password)
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(random.uniform(min_delay, min_delay + 3))
        
        browser.find_element_by_class_name('CollapsableSidebarHeaderDeadZone-p4vqop-0').click()
        
    except:
        browser.quit()
        log += 'Login failed!\n'
        return log
        
    time.sleep(random.uniform(min_delay, min_delay + 3))
    #browser.find_element_by_xpath("//div[@data-tooltip='Sent']").click()
    
    log += 'Hubspot MessageBot: START\n'
    
    for idx, row in df_data.iterrows():
        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
        
        try:
            email = row['EMAIL']
            status = row['STATUS']

            if status != 'sent':
                #Customize message
                name = row['NAME']
                if np.isnan(name):
                    subject = subject.replace('@subject', '')
                    message = message.replace('@name', '')
                else:
                    subject = subject.replace('@subject', name)
                    message = message.replace('@name', name)
                
                send_hubspot(browser, email, subject, message, alias_number, min_delay)
                
                df_data.loc[idx, 'STATUS'] = 'sent'
                log += '{}: sent\n'.format(email)
                
            #Sleep to make sure everything loads
            time.sleep(random.uniform(min_delay + 3, min_delay + 7))
                
        except Exception as e:
            df_data.loc[idx, 'STATUS'] = e
            log += '{}: error\n'.format(email)
            continue

    browser.quit()
    
    #Update database
    with pd.ExcelWriter(path) as writer:  
        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
    writer.close()

    log += 'Hubspot MessageBot: DONE.\n'
    
    return log
    
    
def post_facebookgroup_classic(browser, facebook_group, subject, message, images, min_delay = 3):
    browser.get(facebook_group)
    time.sleep(random.uniform(min_delay + 3, min_delay + 7))
    
    #Customize message
    name = browser.find_element_by_name('q').get_attribute('value')
    
    browser.find_element_by_class_name('fbReactComposerAttachmentSelector_STATUS').click()
    time.sleep(2)

    #Attach images
    for img in images:
        elementID = browser.find_element_by_xpath('//input[@type="file"]')
        elementID.send_keys(utils.path_media + img)
        time.sleep(1)
    time.sleep(random.uniform(min_delay, min_delay + 3))
    
    browser.find_element_by_class_name('_5rpb').click()
    browser.implicitly_wait(implicit_time)
    
    actions = ActionChains(browser)
    for part in message.split('\n'):
        actions.send_keys(part)
        actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
        
    actions.perform()
    time.sleep(1)

    try: #Sell group
        browser.find_element_by_class_name('fbReactComposerAttachmentSelector_SELL').click()
        time.sleep(1)
        
        browser.find_element_by_xpath('//input[@class="_58al" and @maxlength="100"]').send_keys(subject)
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_xpath('//input[@class="_58al" and @maxlength="20"]').send_keys('0')
        time.sleep(2)
        
#        elementID = browser.find_element_by_xpath('//input[@class="_58al" and @role="combobox"]')
#        elementID.click()
#        browser.implicitly_wait(implicit_time)
#        
#        elementID.send_keys('Hồ Chí Minh City')
#        time.sleep(1)
#        
#        elementID.send_keys(Keys.ENTER)
#        browser.implicitly_wait(implicit_time)

        next_button = browser.find_element_by_xpath('//*[@class="_332r"]')
        browser.implicitly_wait(implicit_time)
        clickable = False
        while not clickable:
            cursor = next_button.find_element_by_tag_name('span').value_of_css_property('cursor')
            if cursor != 'default':
                clickable = True
            break
        
        next_button.click()
        time.sleep(2)
        
        #Uncheck Marketplace
        elementID = browser.find_element_by_xpath('//div[@aria-disabled="false"]')
        if elementID.get_attribute('aria-checked') == 'true':
            elementID.click()
        time.sleep(1)
        
    except: #Discuss group
        pass
    
    post_button = browser.find_element_by_xpath('//*[@class="_332r"]')
    browser.implicitly_wait(implicit_time)
    clickable = False
    while not clickable:
        cursor = post_button.find_element_by_tag_name('span').value_of_css_property('cursor')
        if cursor != 'default':
            clickable = True
        break

    post_button.click()
    
    return name


def post_facebookgroup(browser, facebook_group, subject, message, images, min_delay = 3):
    browser.get(facebook_group)
    time.sleep(random.uniform(min_delay + 3, min_delay + 7))
    
    #Customize message
    name = browser.find_element_by_xpath('//h2[@dir="auto"]').text
    
    try: #Sell group
        browser.find_element_by_xpath('//div[(@aria-label="Sell Something" or @aria-label="Bán gì đó") and @role="button"]').click()
        time.sleep(2)
        
        #Attach images           
        elementID = browser.find_element_by_xpath('//input[@class="mkhogb32"]')
        browser.implicitly_wait(implicit_time)
        
        elementID.send_keys(utils.path_media + images[0])
        time.sleep(random.uniform(min_delay, min_delay + 3))
        
        browser.find_element_by_xpath('//div[@class="j83agx80 k4urcfbm"]/div/input').send_keys(subject)
        browser.implicitly_wait(implicit_time)
        
        browser.find_element_by_xpath('//input[@dir="auto" and @autocomplete="off"]').send_keys('0')
        time.sleep(2)

        browser.find_element_by_xpath('//textarea[@dir="auto"]').click()
        browser.implicitly_wait(implicit_time)
                
        actions = ActionChains(browser)
        for part in message.split('\n'):
            actions.send_keys(part)
            actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
            
        actions.perform()
        time.sleep(1)
        
        next_button = browser.find_element_by_xpath('//div[(@aria-label="Next" or @aria-label="Tiếp") and @role="button"]')
        browser.implicitly_wait(implicit_time)
        
        clickable = False
        while not clickable:
            cursor = next_button.value_of_css_property('cursor')
            if cursor != 'not-allowed':
                clickable = True
            break

        next_button.click()
        time.sleep(2)
        
        #Uncheck Marketplace
        try:
            browser.find_element_by_class_name('hu5pjgll.op6gxeva.sp_v8yz2528JQj.sx_3bb65f').click()
        except:
            pass
        time.sleep(1)
    
    except: #Discuss group
        browser.find_element_by_xpath('//span[text() = "Discussion" or text() = "Thảo luận"]').click()
        time.sleep(2)
        
        #Attach images
        elementID = browser.find_element_by_xpath('//input[@class="mkhogb32"]')
        browser.implicitly_wait(implicit_time)
        
        elementID.send_keys(utils.path_media + images[0])
        time.sleep(random.uniform(min_delay, min_delay + 3))
        
        actions = ActionChains(browser)
        for part in message.split('\n'):
            actions.send_keys(part)
            actions.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER)
            
        actions.perform()
        time.sleep(1)
        
    post_button = browser.find_element_by_xpath('//div[(@aria-label="Post" or @aria-label="Đăng") and @role="button"]')
    browser.implicitly_wait(implicit_time)
    
    clickable = False
    while not clickable:
        cursor = post_button.value_of_css_property('cursor')
        if cursor != 'not-allowed':
            clickable = True
        break

    post_button.click()
    
    return name

    
def run_facebook_grouppost(layout = 'new', min_delay = 3):
    log = '' 
     
    path = lib_sys.get_filepath('xlsx')

    if path is None or len(path) == 0:
        log += 'No file selected.'
        return log
        
    df_login = pd.read_excel(path, 'LOGIN')
    df_message = pd.read_excel(path, 'MESSAGE')
    df_data = pd.read_excel(path, 'DATA')
    
    #Init
    facebook_link = 'https://www.facebook.com/login'
    username = df_login['USERNAME'][0]
    password = df_login['PASSWORD'][0]
    subject = df_message['SUBJECT'][0]
    message = df_message['CONTENT'][0]
    try:
        images = df_message['IMAGE'][0].split(', ')
    except:
        images = []

    #Open link on chrome
    if sys.platform == 'win32':
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
    else:
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac

    browser.get(facebook_link)
    browser.implicitly_wait(implicit_time)

    #Access account
    log += 'Login to Facebook.\n'
    try:
        elementID = browser.find_element_by_id('email')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(username)
        
        elementID = browser.find_element_by_id('pass')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(password)
        
        elementID.submit()
        
    except:
        browser.quit()
        log += 'Login failed!\n'
        return log
        
    time.sleep(random.uniform(min_delay, min_delay + 3))

    log += 'Facebook MessageBot: START\n'
    for idx, row in df_data.iterrows():
        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
        
        try:
            facebook_group = row['FACEBOOK_GROUP']
            status = row['STATUS']
            
            if status != 'sent':
                if layout == 'new':
                    name = post_facebookgroup(browser, facebook_group, subject, message, images, min_delay)
                else:
                    name = post_facebookgroup_classic(browser, facebook_group, subject, message, images, min_delay)
                
                df_data.loc[idx, 'NAME'] = name
                df_data.loc[idx, 'STATUS'] = 'sent'
                log += '{}: sent\n'.format(facebook_group)
                
            #Sleep to make sure everything loads
            time.sleep(random.uniform(min_delay + 3, min_delay + 7))
    
        except Exception as e:
            df_data.loc[idx, 'STATUS'] = e
            log += '{}: error\n'.format(facebook_group)
            continue

    browser.quit()
    
    #Update database
    with pd.ExcelWriter(path) as writer:  
        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
    writer.close()
    
    log += 'Facebook GroupBot: DONE.\n'
    
    return log 
    

def run_facebook_groupschedule(layout, min_delay = 3):
    log = '' 
     
    path = lib_sys.get_filepath('xlsx')

    if path is None or len(path) == 0:
        log += 'No file selected.'
        return log
        
    df_login = pd.read_excel(path, 'LOGIN')
    df_message = pd.read_excel(path, 'MESSAGE')
    df_data = pd.read_excel(path, 'DATA')
    
    #Init
    facebook_link = 'https://www.facebook.com/login'
    username = df_login['USERNAME'][0]
    password = df_login['PASSWORD'][0]

    #Get all subjects, contents and list of images
    df_subject = df_message['SUBJECT']
    df_content = df_message['CONTENT']
    try:
        df_images = df_message['IMAGE']
    except:
        df_images = pd.DataFrame()

    #Open link on chrome
    if sys.platform == 'win32':
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver.exe') #windows
    else:
        browser = webdriver.Chrome(options = option, executable_path = './modules/qt_bot/driver/chromedriver') #mac

    browser.get(facebook_link)
    browser.implicitly_wait(implicit_time)

    #Access account
    log += 'Login to Facebook.\n'
    try:
        elementID = browser.find_element_by_id('email')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(username)
        
        elementID = browser.find_element_by_id('pass')
        browser.implicitly_wait(implicit_time)
        elementID.send_keys(password)
        
        elementID.submit()
        
    except:
        browser.quit()
        log += 'Login failed!\n'
        return log
        
    time.sleep(random.uniform(min_delay, min_delay + 3))

    log += 'Facebook MessageBot: START\n'
    
    len_message = len(df_message)
    ii = 0
    for idx, row in df_data.iterrows():
        df_data.loc[idx, 'NAME_MODIFIED'] = utils.username
        df_data.loc[idx, 'DATE_MODIFIED'] = datetime.now()
        
        subject = df_subject[ii]
        message = df_content[ii]
        images = df_images[ii].split(', ')
        ii += 1
        if ii == len_message: #reset to first content
            ii = 0
            
        try:
            facebook_group = row['FACEBOOK_GROUP']
            status = row['STATUS']
            
            if status != 'sent':                
                if layout == 'new':
                    name = post_facebookgroup(browser, facebook_group, subject, message, images, min_delay)
                else:
                    name = post_facebookgroup_classic(browser, facebook_group, subject, message, images, min_delay)
                
                df_data.loc[idx, 'NAME'] = name
                df_data.loc[idx, 'STATUS'] = 'sent'
                log += '{}: sent\n'.format(facebook_group)
                
            #Sleep to make sure everything loads
            time.sleep(random.uniform(min_delay + 3, min_delay + 7))
    
        except Exception as e:
            df_data.loc[idx, 'STATUS'] = e
            log += '{}: error\n'.format(facebook_group)
            continue

    browser.quit()
    
    #Switch content
    df_message = df_message.apply(np.roll, shift = 1)
    
    #Update database
    with pd.ExcelWriter(path) as writer:  
        df_login.to_excel(writer, sheet_name = 'LOGIN', index = False)
        df_message.to_excel(writer, sheet_name = 'MESSAGE', index = False)
        df_data.to_excel(writer, sheet_name = 'DATA', index = False)
    writer.close()
    
    log += 'Facebook GroupBot: DONE.\n'
    
    return log     
    
    