# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
from Components import Client,Host
gobject.threads_init ()

from DemoClient import DemoClient

client = None
l = Client.logger

def main():
	global client
	
	# Arguments
	parser = argparse.ArgumentParser(description='A generic client example.')
	parser.add_argument('-o','--host',type=int,default=0,help="the PID that this client will embed itself into, if left out will spawn its own host")
	args = parser.parse_args()
	
	l.critical("===========================================================")
	l.critical("Client {0} - A generic client example. Started.".format(os.getpid()))
	l.critical("===========================================================")
	l.info("GLADE_PREFIX is {0}".format(Client.glade_prefix))
	
	client = DemoClient(args.host)
	gtk.main()
	pass	
	
if __name__ == "__main__":
	main()


