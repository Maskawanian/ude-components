# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
from hostclient import Client

app = None
bus = None
arg_add = None

def main():
	global app
	global bus
	global arg_add
	
	# Arguments
	parser = argparse.ArgumentParser(description='A multi-process tab server.')
	parser.add_argument('-a','--add',type=int,default=0,help="the PID that this host will add immediately")
	args = parser.parse_args()
	arg_add = args.add
	print arg_add
	
	# DBus
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SessionBus ()
	name = dbus.service.BusName("org.ude.components.host_"+str(os.getpid()), bus)
	dbusobj = Example(bus, '/org/ude/components/host')
	
	print "Host PID",os.getpid()
	
	
	app = App()
	gtk.main()
	pass

class App:
	glade_prefix = ""
	
	builder = None
	window = None
	
	entry = None
	button = None
	
	notebook = None
	embed = None
	
	clients = []
	
	def __init__(self):
		try:
			self.glade_prefix = os.environ["GLADE_PREFIX"]
		except KeyError:
			print "No Glade Environment"
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(self.glade_prefix+"host.glade")
		
		self.window = self.builder.get_object("window")
		
		self.entry = self.builder.get_object("entry")
		self.button = self.builder.get_object("button")
		self.notebook = self.builder.get_object("notebook")
		
		self.window.connect("delete-event",self.do_window_delete_event)
		self.button.connect("clicked",self.do_add_pid_clicked)
		
		self.window.show_all()
		
		if arg_add != 0:
			self.add_pid(arg_add)
		pass
	
	def do_window_delete_event(self,sender,event):
		gtk.main_quit()
		return False
		#return True # Stop Delete
	
	def do_add_pid_clicked(self,sender):
		self.add_pid(int(self.entry.get_text()))
	
	def add_pid(self,pid):
		client = Client(bus,pid)
		self.clients.append(client)
		
		hbox = gtk.HBox(spacing=5)
		hbox.pack_start(client.image,expand=False,fill=False)
		hbox.pack_start(client.label,expand=True,fill=True)
		hbox.pack_start(client.closebutton,expand=False,fill=False)
		hbox.show_all()
		
		self.notebook.append_page(client.widget,hbox)
	
	def remove_pid(self,pid):
		i = 0
		for client in self.clients:
			self.notebook.remove_page(self.notebook.page_num(client.widget))
			del client

class Example(dbus.service.Object):
	def __init__(self, bus, object_path):
		dbus.service.Object.__init__(self, bus, object_path)
	
	@dbus.service.method(dbus_interface='org.ude.components.host',in_signature='i')
	def AddPID(self, pid):
		app.add_pid(pid)
	
	@dbus.service.method(dbus_interface='org.ude.components.host',in_signature='i')
	def RemovePID(self, pid):
		app.remove_pid(pid)
	
if __name__ == "__main__":
	main()
