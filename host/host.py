# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import pygtk
pygtk.require('2.0')
import gobject
gobject.threads_init ()
import gtk,gio
gtk.gdk.threads_init()
import sys,os
import dbus
import dbus.service
import dbus.mainloop.glib
from hostclient import Client

app = None
bus = None

class App:
	builder = None
	window = None
	
	entry = None
	button = None
	notebook = None
	
	clients = []
	
	def __init__(self):
		glade_prefix = ""
		try:
			glade_prefix = os.environ["GLADE_PREFIX"]
		except KeyError:
			print "No Glade Environment"
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(glade_prefix+"host.glade")
		
		self.window = self.builder.get_object("window")
		
		self.entry = self.builder.get_object("entry")
		self.button = self.builder.get_object("button")
		self.notebook = self.builder.get_object("notebook")
		
		self.button.connect("clicked",self.do_add_pid_clicked)
		
		self.window.show_all()
		
		
		pass
	
	def do_add_pid_clicked(self,sender):
		print "do_add_pid_clicked"
		self.add_pid(int(self.entry.get_text()))
		pass
	
	
	def add_pid(self,pid):
		
		client = Client(bus,pid)
		xid = client.Prepare()
		
		socket = gtk.Socket()
		socket.show()
		
		self.notebook.append_page(socket,gtk.Label(str(pid)))
		
		# This must be called once the socket is on screen, not before.
		socket.add_id(xid)
		
		
		
		
		pass
	
	

class Example(dbus.service.Object):
	def __init__(self, bus, object_path):
		dbus.service.Object.__init__(self, bus, object_path)
	
	@dbus.service.method(dbus_interface='org.ude.components.host',in_signature='i')
	def Swallow(self, pid):
		app.add_pid(pid)
	
	#@dbus.service.method(dbus_interface='org.ude.components.host',in_signature='i')
	#def Expel(self, pid):
	#	print "Expel PID",pid
	#	pass

if __name__ == "__main__":
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SessionBus ()
	name = dbus.service.BusName("org.ude.components.host_"+str(os.getpid()), bus)
	object = Example(bus, '/org/ude/components/host')
	
	app = App()
	gtk.main()
