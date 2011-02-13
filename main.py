# -*- coding: utf-8 -*-

import sys
import util
from util import log
from util import log_exc
from server import Server


# Return codes:
ABEND = 1
GRACEFULLY = 0
USERQUIT = 2

#############################################
def main():
    print "--- Hardware Upgrade IRC Server project ---"

    if '--listen-outside' in sys.argv:
        srv = Server('', 6969) # Map either localhost and LAN 
    else:
        srv = Server('127.0.0.1', 6969) # Map in LAN
    
    if '--no-debug' in sys.argv:
        util.debug = False
    
    try:
        log('Server started...')
        srv.start()
    except KeyboardInterrupt:    # Sollevata quando si preme CTRL+C
        srv.stop()
        log("Server aborted due to CTRL-C signal")
        sys.exit(USERQUIT)
    except SystemExit: # Viene sollevata alla chiamata di sys.exit()
        log("Server ended")
        sys.exit(GRACEFULLY)
    except Exception as ex:
        log_exc("Server aborted due to exception: ", ex)
        srv.stop()
        sys.exit(ABEND)


#############################################
# Chiaramente da rimuovere
if __name__ == '__main__': main()
