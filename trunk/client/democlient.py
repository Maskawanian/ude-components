# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading
gobject.threads_init ()

from ComponentClient import ComponentClient

client = None

def main():
	global client
	
	# Arguments
	parser = argparse.ArgumentParser(description='A generic client example.')
	parser.add_argument('-o','--host',type=int,default=0,help="the PID that this client will embed itself into, if left out will spawn its own host")
	args = parser.parse_args()
	
	# DBus
	print "Client PID",os.getpid()
	
	client = DemoClient(args.host)
	gtk.main()
	pass

class DemoClient(ComponentClient):
	def prepare_new_widget(self):
		ret = gtk.Button("demo client")
		ret.connect("clicked",self.button_press)
		return ret
	
	def button_press(self,sender):
		print "click"
		pass
	
	
if __name__ == "__main__":
	main()


