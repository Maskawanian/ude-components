# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk
from Components import Client,Host
gobject.threads_init ()

from WebClient import WebClient

client = None
l = Client.logger

def main():
	global client
	
	# Arguments
	parser = argparse.ArgumentParser(description='A multi-process tabbed web browser.')
	parser.add_argument('-o','--host',type=int,default=0,help="the PID that this client will embed itself into, if left out will spawn its own host")
	args = parser.parse_args()
	
	l.critical("===========================================================")
	l.critical("Client {0} - A multi-process tabbed web browser. Started.".format(os.getpid()))
	l.critical("===========================================================")
	
	client = WebClient(args.host)
	gtk.main()
	l.info("Client {0} closing cleanly.".format(os.getpid()))
	pass
	

	
if __name__ == "__main__":
	main()






































