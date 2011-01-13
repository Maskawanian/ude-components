# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os
import gobject,pygtk,gtk,gio
gobject.threads_init ()
import dbus,dbus.service,dbus.mainloop.glib
import Components
from Components import Client,Host
import logging
from logging import debug,info,warning,error,critical,log,exception

l = Host.logger

class HostClient(object):
	bus = None
	remote = None
	delegate = None
	
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
	
	def __init__(self,bus,pid,delegate):
		assert None != bus
		assert None != delegate
		assert 0 < pid
		assert bus.name_has_owner(Client.BUS_INTERFACE_NAME_PID_FORMAT.format(pid)), "PID provided was not located on DBus."
		
		super(HostClient, self).__init__()
		
		self.delegate = delegate
		self.bus = bus
		
		self.remote = self.bus.get_object(Client.BUS_INTERFACE_NAME_PID_FORMAT.format(pid),Client.BUS_OBJECT_PATH)
		assert None != self.remote
		
		self.remote.connect_to_signal("TitleChanged",self.__cb_title_changed)
		self.remote.connect_to_signal("ProxyIconChanged",self.__cb_proxy_icon_changed)
		self.remote.connect_to_signal("SaveStatusChanged",self.__cb_save_status_changed)
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(Host.GLADE_PREFIX+"HostClient.glade")
		assert None != self.builder
		
		self.widget = gtk.VBox()
		self.widget.add_events(gtk.gdk.STRUCTURE_MASK)
		self.widget.connect("map",self.__widget_map)
		assert None != self.widget
		
		self.image = gtk.Image()
		self.image.set_size_request(16,16)
		assert None != self.image
		
		self.label = gtk.Label()
		assert None != self.label
		
		img = gtk.Image()
		img.set_size_request(12,12)
		img.set_from_file(Components.MEDIA_PATH_PREFIX+"12x12close.svg")
		assert None != img
		
		self.closebutton = gtk.ToolButton(img)
		assert None != self.closebutton
		
		self.socket = gtk.Socket()
		self.socket.connect("plug-removed",self.__plug_removed)
		assert None != self.socket
		
		self.crashbox = self.builder.get_object("crashbox")
		assert None != self.crashbox
		
		self.widget.pack_start(self.socket)
		
		# Update with initial values.
		initial_path = self.GetProxyIconPath()
		assert None != initial_path
		
		initial_title = self.GetTitle()
		assert None != initial_title
		
		initial_ss = self.GetSaveStatus()
		assert initial_ss in Client.SAVE_STATUS_RANGE
		
		self.__cb_proxy_icon_changed(initial_path)
		self.__cb_title_changed(initial_title)
		self.__cb_save_status_changed(initial_ss)
		
		self.widget.show_all()
		pass
	
	def __widget_map(self,sender):
		"""
		The host window has to be mapped before we can add an xembed window to it.
		"""
		if self.has_remote == False:
			plug_id = self.Prepare()
			assert 0 < plug_id
			
			l.info("Insert new remote xid of {0}.".format(plug_id))
			
			self.socket.add_id(plug_id)
			self.has_remote = True
		
		assert self.has_remote
		
		return False
	
	def __plug_removed(self,sender):
		"""
		When the remote widget disconnects for any reason we display the crash box. 
		If the disconnect is for a valid reason, then tab will also be removed, 
		this will happen fast enough that no one will see the crash box.
		"""
		
		assert None != self.widget
		assert None != self.crashbox
		
		self.has_remote = False
		
		self.widget.pack_start(self.crashbox)
		self.widget.show_all()
		
		l.info("Remote xid disconnected.")
		
		return False
	
	def Prepare(self):
		"""
		Synchronously tell the remote side to prepare a window for embedding and return its XID.
		"""
		try:
			return self.remote.Prepare(dbus_interface=Client.BUS_INTERFACE_NAME)
		except:
			return None
	
	def Save(self):
		"""
		Asynchronously tell the remote side to save.
		"""
		try:
			self.remote.Save(dbus_interface=Client.BUS_INTERFACE_NAME,
							 reply_handler=self.__cb_save_stub,
							 error_handler=self.__cb_save_stub_e)
		except:
			pass
	def __cb_save_stub(self):
		pass
	def __cb_save_stub_e(self):
		pass
	
	def GetSaveStatus(self):
		"""
		Synchronously get the save status from the remote side.
		"""
		try:
			return self.remote.GetSaveStatus(dbus_interface=Client.BUS_INTERFACE_NAME)
		except:
			return Client.SAVE_STATUS_SAVED
	
	def GetDescription(self):
		"""
		Synchronously get the description from the remote side.
		"""
		try:
			return self.remote.GetDescription(dbus_interface=Client.BUS_INTERFACE_NAME)
		except:
			return "No Description"
	
	def NotifyClosedByHost(self):
		"""
		Asynchronously notify the other side to close.
		"""
		self.remote.NotifyClosedByHost(dbus_interface=Client.BUS_INTERFACE_NAME,
									   reply_handler=self.__cb_closed_by_host_stub,
									   error_handler=self.__cb_closed_by_host_stub_e)
	def __cb_closed_by_host_stub(self):
		pass
	def __cb_closed_by_host_stub_e(self,error):
		pass
	
	def GetTitle(self):
		"""
		Synchronously get the title from the remote side.
		"""
		try:
			self.title = self.remote.GetTitle(dbus_interface=Client.BUS_INTERFACE_NAME)
			return self.title
		except:
			return ""
	
	def GetProxyIconPath(self):
		"""
		Synchronously get the proxy icon path from the remote side.
		"""
		try:
			return self.remote.GetProxyIconPath(dbus_interface=Client.BUS_INTERFACE_NAME)
		except:
			return ""
	
	def __cb_title_changed(self,title):
		"""
		Remote title changed.
		"""
		
		assert None != title
		assert None != self.label
		
		self.title = title
		self.label.set_text(self.title)
		pass
	
	def __cb_proxy_icon_changed(self,path):
		"""
		Remote proxy icon changed.
		"""
		self.proxy_icon_path = path
		
		assert None != self.proxy_icon_path
		assert None != self.image
		
		if self.proxy_icon_path.endswith((".gif",".apng",".mng")):
			anim = gtk.gdk.PixbufAnimation(self.proxy_icon_path)
			assert None != anim
			self.image.set_from_animation(anim)
		else:
			pb = None
			try:
				pb = gtk.gdk.pixbuf_new_from_file_at_size(self.proxy_icon_path,16,16)
			except:
				pb = gtk.gdk.pixbuf_new_from_file_at_size(Components.MEDIA_PATH_PREFIX+"16x16doc.svg",16,16)
			assert None != pb
			self.image.set_from_pixbuf(pb)
		pass
	
	def __cb_save_status_changed(self,status):
		"""
		Remote save status changed.
		"""
		assert None != self.delegate
		assert status in Client.SAVE_STATUS_RANGE
		
		self.delegate.update_client_status(self,status)
		pass



















































