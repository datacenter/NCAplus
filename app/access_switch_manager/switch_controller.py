"""
Main point of entry for the web application

"""

import pexpect
import time
import os

__author__ = 'Santiago Flores Kanter (sfloresk@cisco.com)'

COMMAND_WAIT_TIME = 1
PEXPECT_TIME_OUT = 3


class switch_controller:

    def __init__(self):
        pass

    def send_commands(self, switch_ip, switch_user, switch_login_password,
                      switch_enable_password, switch_hostname, switch_commands):
        log_file_w = open("access-switch.log", "w")
        ssh_pexpect = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null ' + switch_user + '@' + switch_ip)
        # Waits a second to give the connection time to print the following questions
        time.sleep(COMMAND_WAIT_TIME)
        try:
            # Answers to the question Are you sure you want to continue connecting (yes/no)?
            ssh_pexpect.sendline('yes')
            ssh_pexpect.expect('Password: ', PEXPECT_TIME_OUT)
            ssh_pexpect.sendline(switch_login_password)
            ssh_pexpect.expect(switch_hostname + '>', PEXPECT_TIME_OUT)
            ssh_pexpect.sendline('enable')
            try:
                ssh_pexpect.expect('Password: ', PEXPECT_TIME_OUT)
                ssh_pexpect.sendline(switch_enable_password)
            except pexpect.TIMEOUT:
                ssh_pexpect.expect(switch_hostname + '#', PEXPECT_TIME_OUT)
            ssh_pexpect.logfile = log_file_w
            for command in switch_commands:
                ssh_pexpect.sendline(command)
                time.sleep(COMMAND_WAIT_TIME)
                ssh_pexpect.expect('\r\n', PEXPECT_TIME_OUT)
            log_file_r = open("access-switch.log", "r")
            result = ''
            for string in log_file_r.readlines():
                result += string
            return result
        except:
            raise
        finally:
            ssh_pexpect.close()
            os.remove('access-switch.log')
