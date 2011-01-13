# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
from Components import Client,Host
from TabbedHost import TabbedHost
import logging

app = None
l = Host.logger

def main():
	global app
	
	# Arguments
	parser = argparse.ArgumentParser(description='A multi-process tab server.')
	parser.add_argument('-a','--add',type=int,default=0,help="the PID that this host will add immediately")
	args = parser.parse_args()
	arg_add = args.add
	
	l.critical("===========================================================")
	l.critical("Host {0} - A multi-process tab server. Started.".format(os.getpid()))
	l.critical("===========================================================")
	l.info("GLADE_PREFIX is {0}".format(Host.glade_prefix))
	
	app = TabbedHost(arg_add)
	gtk.main()
	pass

if __name__ == "__main__":
	main()
