import pandas as pd
from datetime import datetime

import utils
from lib import lib_sys



def get_memberinfo(status = 'all'):    
    try:
        if status in ['in', 'out', 'dealing', 'temp']:
             df = pd.read_sql("select * from {} where STATUS like '{}'".format(utils.db_memberinfo, status), utils.ENGINE)
        else:
            df = pd.read_sql("select * from {}".format(utils.db_memberinfo), utils.ENGINE)
            
        df.columns = [x.upper() for x in df.columns]
    except:
        return "Members' Info downloaded failed!"
        
    path = lib_sys.get_folderpath()
    df.to_excel(path + '/{}_{}_{}.xlsx'.format(utils.db_memberinfo, status, datetime.now().strftime('%y%m%d_%H%M%S')), index = False)
    
    return "Members' Info downloaded successfully."


def get_memberinfo_byname(name):
    try:
        df = pd.read_sql("select * from {} where NAME like '{}'".format(utils.db_memberinfo, name), utils.ENGINE)
        df.columns = [x.upper() for x in df.columns]
    except:
        return "'{}': Get information failed!".format(name)
        
    return df

    

def push_memberinfo():
    log = ''
    
    path = lib_sys.get_filepath('xlsx')
    if path is None or len(path) == 0:
        return 'No file selected.'
        
    df = pd.read_excel(path)
    df.columns = [x.upper() for x in df.columns]
    df['DATE_MODIFIED'] = datetime.now()
    df['NAME_MODIFIED'] = utils.username

    try:
        for col in df.columns:
            #Convert to datetime
            if col == 'TIMESTAMP'or col == 'STARTDATE' or col == 'OUTDATE' or col == 'DATE_MODIFIED':
                if df[col].dtypes == 'float':
                    df[col] = pd.to_datetime(df[col])
                    
                if df[col].dtypes != 'datetime64[ns]':
                    log += 'Correct type of column {} as yyyy-mm-dd\n'.format(col)
            else:
                #Convert to string
                df[col] = df[col].astype(str)
        
        if log == '':
            listname = "('{}')".format("', '".join(df['NAME']))
            utils.ENGINE.execute('delete from {} where to_char(NAME) in {}'.format(utils.db_memberinfo, listname))

            #Insert changed rows
            df.to_sql(utils.db_memberinfo, utils.ENGINE, if_exists = 'append', index = False)
            log += "Members' Info uploaded successfully."
        return log
        
    except:
        return "Members' Info uploaded failed!"
    
