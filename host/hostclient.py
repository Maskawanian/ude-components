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

class Client:
	bus = None
	remote = None
	
	def __init__(self,bus,pid):
		self.bus = bus
		self.remote = self.bus.get_object("org.ude.components.client_"+str(pid),"/org/ude/components/client")
		pass
	
	def Prepare(self):
		return self.remote.Prepare(dbus_interface="org.ude.components.client")
