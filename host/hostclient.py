# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os
import gobject,pygtk,gtk,gio
gobject.threads_init ()
gtk.gdk.threads_init()
import dbus,dbus.service,dbus.mainloop.glib

class Client:
	glade_prefix = ""
	
	bus = None
	remote = None
	
	builder = None
	widget = None
	image = None
	label = None
	closebutton = None
	socket = None
	crashbox = None
	
	has_remote = False
	
	def __init__(self,bus,pid):
		try:
			self.glade_prefix = os.environ["GLADE_PREFIX"]
		except KeyError:
			print "No Glade Environment"
		
		self.bus = bus
		self.remote = self.bus.get_object("org.ude.components.client_"+str(pid),"/org/ude/components/client")
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(self.glade_prefix+"hostclient.glade")
		
		self.widget = gtk.VBox()
		self.widget.add_events(gtk.gdk.STRUCTURE_MASK)
		self.widget.connect("map",self.__widget_map)
		
		self.image = gtk.Image()
		self.image.set_size_request(16,16)
		self.image.set_from_file(self.GetProxyIconPath())
		
		self.label = gtk.Label()
		self.label.set_text(self.GetTitle())
		
		img = gtk.Image()
		img.set_size_request(12,12)
		img.set_from_file("/home/dan/Desktop/Programming/ude/ude-components/host/12x12close.svg")
		self.closebutton = gtk.ToolButton(img)
		
		
		self.socket = gtk.Socket()
		self.socket.connect("plug-removed",self.__plug_removed)
		
		self.crashbox = self.builder.get_object("crashbox")
		
		self.widget.pack_start(self.socket)
		self.widget.show_all()
		pass
	
	def __widget_map(self,sender):
		if self.has_remote == False:
			print "map event"
			self.socket.add_id(self.Prepare())
			self.has_remote = True
		return False
	
	def __plug_removed(self,sender):
		self.has_remote = False
		self.widget.pack_start(self.crashbox)
		self.widget.show_all()
		print "plug-removed"
		return False
	
	def Prepare(self):
		try:
			return self.remote.Prepare(dbus_interface="org.ude.components.client")
		except:
			return None
	
	def AllowClose(self):
		try:
			return self.remote.AllowClose(dbus_interface="org.ude.components.client")
		except:
			return True
	
	def ShowAllowClosePrompt(self):
		try:
			self.remote.ShowAllowClosePrompt(dbus_interface="org.ude.components.client")
		except:
			pass
	
	def ClosedByHost(self):
		try:
			self.remote.ClosedByHost(dbus_interface="org.ude.components.client")
		except:
			pass
	
	def GetTitle(self):
		try:
			return self.remote.GetTitle(dbus_interface="org.ude.components.client")
		except:
			return ""
	
	def GetProxyIconPath(self):
		try:
			return self.remote.GetProxyIconPath(dbus_interface="org.ude.components.client")
		except:
			return ""



































