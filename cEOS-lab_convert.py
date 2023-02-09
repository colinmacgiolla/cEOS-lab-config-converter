#!/bin/python
# Copyright (c) 2022 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,  this list of conditions and the following disclaimer in the documentation 
#   and/or other materials provided with the distribution.
# * Neither the name of the Arista nor the names of its contributors may be used to endorse or promote products derived from this software without 
#   specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

import os, sys, ssl, argparse
from jsonrpclib import Server
import string, random
from getpass import getpass
import argparse

# Stop the nags over self-signed certificates
import urllib3
urllib3.disable_warnings()


# Allow unverified contexts for newer python, where it is required
if ((sys.version_info.major == 3) or
    (sys.version_info.major == 2 and sys.version_info.minor == 7 and sys.version_info.micro >= 5)):
    ssl._create_default_https_context = ssl._create_unverified_context


test_upload = False

def generate_uuid(length=8):
    '''
    generate_uuid - generate a relatively short ID to use for config sessions
    '''
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, length=length))


def main():
    parser = argparse.ArgumentParser(prog='cEOS-lab Config Converter',
      description='This script strips any config lines that would cause issues in cEOS-lab simulation environments')

    parser.add_argument('-i','--input', default='input', help="Input directory - all files in this directory are parsed")
    parser.add_argument('-o','--output', default='output', help="Output directory - the adjusted files are outputted here")
    args = parser.parse_args()

    filtered = []


    for filename in os.listdir(args.input):
        host = filename.split('.')[0]
        with open(os.path.join(args.input, filename), 'r') as f:
            data = f.read()

            for line in data.split('\n'):
                # MTU != 1500 breaks things in odd ways
                if 'mtu' in line:
                    leading = len(line) - len(line.lstrip())
                    filtered.append( " " * leading + "mtu 1500")

                # cEOS-lab is using Management0
                elif 'Management1' in line:
                    filtered.append( line.replace('Management1','Management0') )

                # BGP knobs that require real hardware
                elif 'update wait-install' in line or 'update wait-for-convergence' in line:
                    pass

                elif 'storm-control' in line:
                    pass

                else:
                    filtered.append(line)

        
        if test_upload:
            username = 'admin'
            password = 'Arista12345'
            port = '443'

            url = 'https://{}:{}@{}:{}/command-api'.format(username, password, host, port)
            eos = Server(url)

            session = generate_uuid()

            cmds = []
            cmds.append('enable')
            cmds.append('configure session %s' % session)
            cmds.append('rollback clean-config')
            cmds.append(filtered)
            cmds.append('show session-config diffs')
            cmds.append('abort')
            response = eos.runCmds(1,cmds,)


     
        with open(os.path.join(args.output, filename), 'w') as f:
            for line in filtered:
                f.write(f'{line}\n')
        filtered.clear()



    return 0


if __name__ == "__main__":
    main()