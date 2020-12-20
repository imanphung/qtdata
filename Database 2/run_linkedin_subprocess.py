import subprocess
import time

try:
   # wait=False
#   print(command + ' ' + ' '.join(list(args)))
    sp1 = subprocess.Popen(
        'python ./linkedin_data_v1.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)      
    sp2 = subprocess.Popen(
        'python ./linkedin_data_v2.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp3 = subprocess.Popen(
        'python ./linkedin_data_v3.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp4 = subprocess.Popen(
        'python ./linkedin_data_v4.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp5 = subprocess.Popen(
        'python ./linkedin_data_v5.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp6 = subprocess.Popen(
        'python ./linkedin_data_v6.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)     
    sp7 = subprocess.Popen(
        'python ./linkedin_data_v7.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp8 = subprocess.Popen(
        'python ./linkedin_data_v8.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp9 = subprocess.Popen(
        'python ./linkedin_data_v9.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    time.sleep(10)
    sp10 = subprocess.Popen(
        'python ./linkedin_data_v10.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    # if wait:      
    #     out, err = sp1.communicate()      
    #     if out:      
    #         print(out.decode('utf-8'))      
    #     if err:      
    #         print(err.decode('utf-8'))
            
except Exception as e:
    print(e)
    pass