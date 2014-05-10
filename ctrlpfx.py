#!/usr/bin/python

import sys
import os

import resource
import time
import logging
import logging.handlers
from optparse import OptionParser

HOMEASN = 47065
#PREFIXES = range(236, 238)

MUX2IP = { # {{{
		'GATECH': '10.200.224.1',
		'WISC': '10.200.225.1',
		'CLEMSON': '10.200.226.1',
		'PRINCE': '10.200.227.1',
		'UW': '10.200.228.1',
		'AMSIX': '10.200.229.1',
		'ISI': '10.200.230.1'
} # }}}

def announce(prefix, mux, homeasn=HOMEASN): # {{{
        #print prefix
	print "MUX -- >"+mux
	#prefix=int(prefix)
        #print homeasn
        mux = mux.upper()
	assert mux in MUX2IP
        #assert prefix in PREFIXES
        assert isinstance(homeasn, int)
        # tstamp = int(time.time())
        # poison_string = str(poisonv)
        prepend_string = str(homeasn)
        # prepend_string = '%s %d' % (poison_string, homeasn)
        cmd = 'vtysh -d bgpd -c "config terminal" '
        cmd += '-c "route-map %s permit %s" ' % (mux, prefix)
        #cmd += '-c "set as-path prepend %s"' % prepend_string
        reliable_exec(cmd, 3)
        _prefix_up(prefix, mux, prepend_string)
        # logging.info('ctrlpfx %d 184.164.%d.0/24 %s %s %s', tstamp,
        #               prefix, mux, 'announced', prepend_string)
	soft_reset(mux)
# }}}
def poison(prefix, mux, poisonv, homeasn=HOMEASN): # {{{
	mux = mux.upper()
	prefix=int(prefix)
	print "MUX --> "+mux	
	assert mux in MUX2IP
	#assert prefix in PREFIXES
	#poisonv =poisonv+" " +str(homeasn)
	#assert isinstance(poisonv, announce.Announce)
	assert isinstance(homeasn, int)
	# tstamp = int(time.time())
	# poison_string = str(poisonv)
	prepend_string = poisonv
	# prepend_string = '%s %d' % (poison_string, homeasn)
	cmd = 'vtysh -d bgpd -c "config terminal" '
	cmd += '-c "route-map %s permit %d" ' % (mux, prefix)
	cmd += '-c "set as-path prepend %s"' % prepend_string
	reliable_exec(cmd, 3)
	_prefix_up(prefix, mux, prepend_string)
	soft_reset(mux)
	# logging.info('ctrlpfx %d 184.164.%d.0/24 %s %s %s', tstamp,
	# 		prefix, mux, 'announced', prepend_string)
# }}}


def unpoison(prefix, mux): # {{{
	mux = mux.upper()
	prefix=int(prefix)
	assert mux in MUX2IP
	#assert prefix in PREFIXES
	# tstamp = int(time.time())
	_reset_route_map(prefix, mux)
	_prefix_up(prefix, mux, 'noprepend')
	soft_reset(mux)
	# logging.info('ctrlpfx %d 184.164.%d.0/24 %s %s %s', tstamp,
	# 		prefix, mux, 'announced', 'no-prepend')
# }}}


def withdraw(prefix, mux): # {{{
	mux = mux.upper()
	prefix=int(prefix)
	assert mux in MUX2IP
	#assert prefix in PREFIXES
	_reset_route_map(prefix, mux)
	# tstamp = int(time.time())
	logging.info('prefix down %d %s', prefix, mux)
	cmd = 'vtysh -d bgpd -c "config terminal" '
	cmd += '-c "route-map %s permit %d" ' % (mux, prefix)
	cmd += '-c "match ip address prefix-list NONET"'
	reliable_exec(cmd, 3)
	soft_reset(mux)
	# logging.info('ctrlpfx %d 184.164.%d.0/24 %s %s %s', tstamp,
	# 		prefix, mux, 'withdrawn', 'no-prepend')
# }}}


def soft_reset(mux): # {{{
	mux = mux.upper()
	assert mux in MUX2IP
	neighbor = MUX2IP[mux]
	# tstamp = int(time.time())
	# logging.info('soft_reset %s %s', mux, tstamp)
	cmd = 'vtysh -d bgpd -c "clear ip bgp %s soft out"' % neighbor
	reliable_exec(cmd, 3)
# }}}


def reliable_exec(cmd, maxerrors, wait_time=60): # {{{
	# logging.info(cmd)
	errors = 0
	r = os.system(cmd)
	while r != 0:
		errors += 1
		if errors > maxerrors:
			logging.info('tried running %s (%d times) but failed', cmd,
					maxerrors)
			assert False
		time.sleep(wait_time)
		r = os.system(cmd)
# }}}


def deploy(prefix, pfxannounce):#{{{
	logging.info('deploying %s', str(pfxannounce))
	for mux, ace in pfxannounce.items():
		if announce.WITHDRAWN in ace.status:
			withdraw(prefix, mux)
		elif announce.NOPREPEND in ace.status:
			unpoison(prefix, mux)
		else:
			poison(prefix, mux, ace)
		soft_reset(mux)
#}}}


def _prefix_up(prefix, mux, message): # {{{
	logging.info('prefix up %d %s %s', prefix, mux, message)
	cmd = 'vtysh -d bgpd -c "config terminal" '
	cmd += '-c "route-map %s permit %d" ' % (mux, prefix)
	cmd += '-c "match ip address prefix-list NET-%s"' % prefix
	reliable_exec(cmd, 3)
# }}}


def _reset_route_map(prefix, mux): # {{{
	# logging.info('resetting route-map %s permit %d', mux, prefix)
	cmd = 'vtysh -d bgpd -c "config terminal" '
	cmd += '-c "route-map %s permit %d" ' % (mux, prefix)
	cmd += '-c "set as-path prepend 1" '
	cmd += '-c "no set as-path prepend"'
	reliable_exec(cmd, 3)
# }}}

