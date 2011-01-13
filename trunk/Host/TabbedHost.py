# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
from HostClient import HostClient
from UnsavedChangesHandler import UnsavedChangesHandler
from ComponentHostDBus import ComponentHostDBus
from Components import Client,Host
import logging

l = Host.logger

class TabbedHost(object):
	bus = None
	bus_name = None
	bus_service_name = None
	bus_obj = None
	
	builder = None
	window = None
	
	notebook = None
	embed = None
	
	clients = []
	
	def __init__(self,add_pid):
		super(TabbedHost, self).__init__()
		assert add_pid >= 0
		
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()
		self.bus_name = Host.BUS_INTERFACE_NAME+"_"+str(os.getpid())
		self.bus_service_name = dbus.service.BusName(self.bus_name, self.bus)
		self.bus_obj = ComponentHostDBus(self.bus, Host.BUS_OBJECT_PATH, self)
		
		assert self.bus != None
		assert self.bus_name != None
		assert self.bus_service_name != None
		assert self.bus_obj != None
		
		self.builder = gtk.Builder()
		path = Host.GLADE_PREFIX+"TabbedHost.glade"
		assert os.path.exists(path)
		self.builder.add_from_file(path)
		
		self.window = self.builder.get_object("window")
		self.notebook = self.builder.get_object("notebook")
		
		assert self.window != None
		assert self.notebook != None
		
		self.window.connect("delete-event",self.__window_delete_event_cb)
		self.window.show_all()
		
		if add_pid > 0:
			self.add_pid(add_pid)
		pass
	
	__uch = None
	def __window_delete_event_cb(self,sender,event):
		"""
		When the user tries to close the window we may cancel their action and prompt 
		them if they want to save, or at least inform them when they can't save things.
		"""
		assert None == self.__uch
		assert None != self.clients
		
		unsaved_clients = []
		
		# Check for any clients that can't just be closed.
		for client in self.clients:
			d = client.GetSaveStatus()
			if d != Client.SAVE_STATUS_SAVED:
				unsaved_clients.append(client)
		
		if len(unsaved_clients)>0:
			l.info("{0} unsaved clients, prompting user if we should save them.".format(len(unsaved_clients)))
			self.__uch = UnsavedChangesHandler(unsaved_clients,self)
			self.__uch.show(self.window)
			return True # Stop Delete
		
		# Tell all the clients to quit.
		for client in self.clients:
			l.info("Notifying {0} to close.".format(client))
			client.NotifyClosedByHost()
		
		gtk.main_quit()
		
		return False
	
	def unsaved_changes_handler_cb(self,resolution):
		"""
		Called by UnsavedChangesHandler when it has closed. 
		We either don't do anything or quit based on that.
		"""
		assert None != self.__uch
		assert None != self.clients
		assert resolution in UnsavedChangesHandler.RETURN_RANGE
		
		self.__uch = None
		
		if resolution == UnsavedChangesHandler.RETURN_SAVED_ALL:
			for client in self.clients:
				client.NotifyClosedByHost() # Tell the client to quit.
			gtk.main_quit()
	
	def update_client_status(self,client,status):
		"""
		Called when we get status updates from the clients. This 
		is just passed to the UnsavedChangesHandler if it exists.
		"""
		assert None != client
		assert status in Client.SAVE_STATUS_RANGE
		
		if self.__uch:
			self.__uch.update_client_status(client,status)
	
	def add_pid(self,pid):
		"""
		Attempt to add this PID.
		"""
		assert 0 < pid
		assert None != self.bus
		assert None != self.clients
		assert None != self.notebook
		assert self.bus.name_has_owner(Client.BUS_INTERFACE_NAME_PID_FORMAT.format(pid)), "PID provided was not located on DBus."
		
		client = HostClient(self.bus,pid,self)
		
		assert None != client
		assert None != client.image
		assert None != client.label
		assert None != client.closebutton
		assert None != client.widget
		
		self.clients.append(client)
		
		hbox = gtk.HBox(spacing=5)
		hbox.pack_start(client.image,expand=False,fill=False)
		hbox.pack_start(client.label,expand=True,fill=True)
		hbox.pack_start(client.closebutton,expand=False,fill=False)
		hbox.show_all()
		
		self.notebook.append_page(client.widget,hbox)
	
	def remove_pid(self,pid):
		"""
		Attempt to remove this PID.
		"""
		assert 0 < pid
		assert None != self.clients
		assert None != self.notebook
		
		for client in self.clients:
			w = client.widget
			assert None != w
			
			self.notebook.remove_page(self.notebook.page_num(w))
			del client



















































