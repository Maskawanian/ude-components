# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os
import gobject,pygtk,gtk,gio
gobject.threads_init ()
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
	
	title = None
	proxy_icon_path = None
	
	def __init__(self,bus,pid):
		try:
			self.glade_prefix = os.environ["GLADE_PREFIX"]
		except KeyError:
			print "No Glade Environment"
		
		self.bus = bus
		self.remote = self.bus.get_object("org.ude.components.client_"+str(pid),"/org/ude/components/client")
		self.remote.connect_to_signal("TitleChanged",self.__TitleChanged_cb)
		self.remote.connect_to_signal("ProxyIconChanged",self.__ProxyIconChanged_cb)
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(self.glade_prefix+"HostClient.glade")
		
		self.widget = gtk.VBox()
		self.widget.add_events(gtk.gdk.STRUCTURE_MASK)
		self.widget.connect("map",self.__widget_map)
		
		self.image = gtk.Image()
		self.image.set_size_request(16,16)
		path = self.GetProxyIconPath()
		self.__ProxyIconChanged_cb(path)
		
		self.label = gtk.Label()
		self.__TitleChanged_cb(self.GetTitle())
		
		img = gtk.Image()
		img.set_size_request(12,12)
		img.set_from_file("/usr/share/ude/components/12x12close.svg")
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
	
	def SaveStatus(self):
		try:
			return self.remote.SaveStatus(dbus_interface="org.ude.components.client")
		except:
			return 0
	
	def GetDescription(self):
		try:
			return self.remote.GetDescription(dbus_interface="org.ude.components.client")
		except:
			return "No Description"
	
	def ClosedByHost(self):
		try:
			self.remote.ClosedByHost(dbus_interface="org.ude.components.client")
		except:
			pass
	
	def GetTitle(self):
		try:
			self.title = self.remote.GetTitle(dbus_interface="org.ude.components.client")
			return self.title
		except:
			return ""
	
	def __TitleChanged_cb(self,title):
		self.title = title
		self.label.set_text(self.title)
	
	def GetProxyIconPath(self):
		try:
			return self.remote.GetProxyIconPath(dbus_interface="org.ude.components.client")
		except:
			return ""
	
	def __ProxyIconChanged_cb(self,path):
		self.proxy_icon_path = path
		if self.proxy_icon_path.endswith((".gif",".apng",".mng")):
			anim = gtk.gdk.PixbufAnimation(self.proxy_icon_path)
			self.image.set_from_animation(anim)
		else:
			pb = None
			try:
				pb = gtk.gdk.pixbuf_new_from_file_at_size(self.proxy_icon_path,16,16)
			except:
				pb = gtk.gdk.pixbuf_new_from_file_at_size("/usr/share/ude/components/16x16doc.svg",16,16)
			self.image.set_from_pixbuf(pb)
		pass



































