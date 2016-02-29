import pexpect
import time
COMMAND_WAIT_TIME = 2
PEXPECT_TIME_OUT = 2

class switch_controller:

    def __init__(self):
        pass

    def send_commands(self, switch_ip, switch_user, switch_password, switch_hostname, switch_commands):
        ssh_pexpect = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null admin@' + switch_ip)
        # Waits a second to give the connection time to print the following questions
        time.sleep(COMMAND_WAIT_TIME)
        try:
            # Answers to the question Are you sure you want to continue connecting (yes/no)?
            ssh_pexpect.sendline('yes')
            ssh_pexpect.expect('Password: ', PEXPECT_TIME_OUT)
            ssh_pexpect.sendline(switch_password)
            ssh_pexpect.expect(switch_hostname + '# ', PEXPECT_TIME_OUT)
            ssh_pexpect.sendline('configure terminal')
            ssh_pexpect.expect('\r\n', PEXPECT_TIME_OUT)
            ssh_pexpect.expect('Enter configuration commands, one per line.  End with CNTL/Z.', PEXPECT_TIME_OUT)
            ssh_pexpect.expect('\r\n', PEXPECT_TIME_OUT)
            ssh_pexpect.expect('\r', PEXPECT_TIME_OUT)
        except:
            raise
        finally:
            ssh_pexpect.close()
