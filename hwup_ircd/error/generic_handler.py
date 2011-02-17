# -*- coding: utf-8 -*-

from hwup_ircd.util import log_exc

#############################################
def handleException(e):
    log_exc('Exception:', e)