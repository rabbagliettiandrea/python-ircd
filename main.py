# -*- coding: utf-8 -*-

import sys
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

    try:
        print '-L- Server started...   '
        srv.start()
    except KeyboardInterrupt:    # Sollevata quando si preme CTRL+C
        srv.stop()
        print "-L-Server aborted due to CTRL-C signal"
        sys.exit(USERQUIT)
    except SystemExit: # Viene sollevata alla chiamata di sys.exit()
        print "-L- Server ended"
        sys.exit(GRACEFULLY)
    except Exception as ex:
        print "-L- Server aborted due to exception:", ex
        srv.stop()
        sys.exit(ABEND)


#############################################
# Chiaramente da rimuovere
if __name__ == '__main__': main()
