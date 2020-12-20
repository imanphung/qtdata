import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('118.69.32.128', port = 22, username='qtdatavn', password='qtdata@2020')
stdin, stdout, stderr = ssh.exec_command('ls -l')
out = stdout.read()
print(out.decode())