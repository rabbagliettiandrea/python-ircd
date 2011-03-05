# -*- coding: utf-8 -*-

import sys

from argparse import ArgumentParser

from hwup_ircd import utils
from hwup_ircd.utils import print_log
from hwup_ircd.utils import print_exc
from hwup_ircd.server import Server
import argparse

# Return codes:
GRACEFULLY = 0
ABEND = 1
USERQUIT = 2

# Some consts:
SRV_NAME = "Yet another IRC Server project"

#############################################
def main():
    arg_parser = ArgumentParser(description=SRV_NAME)
    arg_parser.add_argument('--debug', action='store_true', dest='debug',
                            default='False', help='Set on the print of verbose error message (default: off)')
    arg_parser.add_argument('--listen-outside', action='store_const', dest='hostaddr', 
                            const='', default='127.0.0.1', help='Listen outside localhost')
    arg_parser.add_argument('-P', '--port', dest='port', default=6667, type=int,
                            help='Listen to a different port (default: 6667)')
    
    arg_results = arg_parser.parse_args()
    print arg_results
    
    utils.DEBUG = arg_results.debug

    print("--- %s ---" % SRV_NAME)
    print_log('Starting server...')
    
    srv = Server(arg_results.hostaddr, arg_results.port)
    
    try:
        srv.start()
    except KeyboardInterrupt:    # Sollevata quando si preme CTRL+C
        srv.stop()
        print_log("Server aborted due to CTRL-C signal")
        sys.exit(USERQUIT)
    except SystemExit: # Viene sollevata alla chiamata di sys.exit()
        print_log("Server ended")
        sys.exit(GRACEFULLY)
    except Exception as e:
        srv.stop()
        print_exc(msg="Server aborted due to an error")
        print_exc(exc=e)
        sys.exit(ABEND)

#############################################
if __name__ == '__main__': 
    main()
