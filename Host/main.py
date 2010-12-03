# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
from TabbedHost import TabbedHost

app = None

def main():
	global app
	
	
	# Arguments
	parser = argparse.ArgumentParser(description='A multi-process tab server.')
	parser.add_argument('-a','--add',type=int,default=0,help="the PID that this host will add immediately")
	args = parser.parse_args()
	arg_add = args.add
	
	print "Host PID",os.getpid()
	
	app = TabbedHost(arg_add)
	gtk.main()
	pass

if __name__ == "__main__":
	main()
