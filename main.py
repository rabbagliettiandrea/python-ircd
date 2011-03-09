# -*- coding: utf-8 -*-

import sys

from argparse import ArgumentParser

from py_ircd import utils
from py_ircd.utils import print_log
from py_ircd.utils import print_exc
from py_ircd.server import Server
from py_ircd.const import constants


#############################################
def main():
    arg_parser = ArgumentParser(description=constants.SRV_NAME)
    arg_parser.add_argument('--debug', action='store_true', dest='debug',
                            default=False, help='Set on the print of verbose error message (default: off)')
    arg_parser.add_argument('--listen-outside', action='store_const', dest='hostaddr', 
                            const='', default='127.0.0.1', help='Listen outside localhost')
    arg_parser.add_argument('-P', '--port', dest='port', default=6667, type=int,
                            help='Listen to a different port (default: 6667)')
    
    arg_results = arg_parser.parse_args()
    print arg_results
    
    addr_tuple = (arg_results.hostaddr, arg_results.port)
    
    if arg_results.debug:
        utils.VERBOSITY_LEVEL = constants.VERBOSITY_DEBUG

    print("--- %s ---" % constants.SRV_NAME)
    print_log('Starting server...')
    
    srv = Server(arg_results.hostaddr, arg_results.port)
    
    try:
        srv.start()
    except KeyboardInterrupt:    # Sollevata quando si preme CTRL+C
        srv.stop()
        print_log("Server aborted due to CTRL-C signal")
        sys.exit(constants.USERQUIT)
    except SystemExit: # Viene sollevata alla chiamata di sys.exit()
        print_log("Server ended")
        sys.exit(constants.GRACEFULLY)
    except Exception as e:
        srv.stop()
        print_exc(msg="Server aborted due to an error")
        print_exc(exc=e)
        sys.exit(constants.ABEND)

#############################################
if __name__ == '__main__': 
    main()
