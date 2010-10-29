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

app = None
dbusobj = None

class App:
	widget = None # Widget that will be embeded.
	plug = None   
	
	def __init__(self):
		pass
	
	def prepare(self):
		'''
		Prepare a widget for embedding. If it is already embeded this will break the widget free.
		'''
		
		newplug = gtk.Plug(0)
		newplug.show()
		
		if None == self.widget:
			self.widget = gtk.Button("button")
			self.widget.connect("clicked",self.button_press)
			self.widget.show()
			
			newplug.add(self.widget)
		else:
			if None != self.widget.get_parent():
				self.widget.reparent(newplug)
			else:
				newplug.add(self.widget)
		
		if None != self.plug:
			del self.plug
		self.plug = newplug
		
		print "Prepare ID=",self.plug.get_id()
		
		return self.plug.get_id()
	
	def button_press(self,sender):
		#self.prepare()
		pass
	
	
class Example(dbus.service.Object):
	def __init__(self, bus, object_path):
		dbus.service.Object.__init__(self, bus, object_path)
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='i')
	def Prepare(self):
		return app.prepare()
	
if __name__ == "__main__":
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	system_bus = dbus.SessionBus ()
	name = dbus.service.BusName("org.ude.components.client_"+str(os.getpid()), system_bus)
	dbusobj = Example(system_bus, '/org/ude/components/client')
	
	app = App()
	gtk.main()


