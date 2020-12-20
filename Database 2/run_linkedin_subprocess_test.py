import subprocess

try:
   # wait=False
#   print(command + ' ' + ' '.join(list(args)))
    sp1 = subprocess.Popen(
        'python ./linkedin_data_v1_test.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )      
    sp2 = subprocess.Popen(
        'python ./linkedin_data_v2_test.py',
        shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    )
    # sp3 = subprocess.Popen(
    #     'python ./linkedin_data_v3.py',
    #     shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    # )
    # sp4 = subprocess.Popen(
    #     'python ./linkedin_data_v4.py',
    #     shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    # )
    # sp5 = subprocess.Popen(
    #     'python ./linkedin_data_v5.py',
    #     shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE
    # )
    # if wait:      
    #     out, err = sp1.communicate()      
    #     if out:      
    #         print(out.decode('utf-8'))      
    #     if err:      
    #         print(err.decode('utf-8'))
            
except Exception as e:
    print(e)
    pass