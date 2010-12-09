# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse,time
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading

import Components.Client
import Components.Host

gobject.threads_init ()

class Base(object):
	bus = None
	bus_name = None
	bus_obj = None
	
	widget = None # Widget that will be embeded.
	plug = None   
	
	__title = "untitled {0}".format(os.getpid())
	__proxy_icon_path = Components.MEDIA_PATH_PREFIX+"16x16doc.svg"
	__save_status = 0 # We can't use Components.Client.SAVE_STATUS_SAVED for some reason.
	
	def __init__(self,hostPID):
		super(Base, self).__init__()
		
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()
		self.bus_name = dbus.service.BusName(Components.Client.BUS_INTERFACE_NAME+"_"+str(os.getpid()), self.bus)
		self.bus_obj = ComponentClientDBus(self.bus,Components.Client.BUS_OBJECT_PATH,self)
		
		if hostPID == 0:
			#fd = os.open(os.devnull, os.O_RDWR)
			env = os.environ.copy()
			env["GLADE_PREFIX"] = Components.Host.GLADE_PREFIX
			#subprocess.Popen(['setsid',path_python,path_host_script,"-a",str(os.getpid())],env=env,stdout=fd,stderr=fd)
			subprocess.Popen(['setsid',Components.PYTHON2_PATH,Components.Host.MAIN_TABBED,"-a",str(os.getpid())],env=env)
		else:
			print "connect to host"
			
			host_bus_name = Components.Host.BUS_INTERFACE_NAME+"_"+str(hostPID)
			if False == self.bus.name_has_owner(host_bus_name):
				raise Exception("The bus `"+host_bus_name+"` does not exist.")
			
			remotehost = self.bus.get_object(host_bus_name,Components.Host.BUS_OBJECT_PATH)
			remotehost.AddPID(os.getpid(),dbus_interface=Components.Host.BUS_INTERFACE_NAME,reply_handler=self.__cb_add_pid,error_handler=self.__cb_add_pid_e)
		pass
	
	def __cb_add_pid(self): #stub
		pass
	def __cb_add_pid_e(self,e):
		raise Exception("Error when communicating with the host: {0}".format(e))
	
	def prepare(self):
		'''
		Prepare a widget for embedding. If it is already embeded this will break the widget free.
		'''
		
		newplug = gtk.Plug(0)
		
		if None == self.widget:
			self.widget = self.prepare_new_widget()
			newplug.add(self.widget)
		else:
			if None != self.widget.get_parent():
				self.widget.reparent(newplug)
			else:
				newplug.add(self.widget)
		
		if None != self.plug:
			del self.plug
		self.plug = newplug
		
		self.plug.show_all()
		
		print "Prepare ID=",self.plug.get_id()
		
		return self.plug.get_id()
	
	def save(self):
		self.set_save_status(3) # Saving
		time.sleep(1)
		self.set_save_status(0) # Saved
		pass
	
	def prepare_new_widget(self):
		ret = gtk.Button("Default Widget")
		return ret
	
	def notify_closed_by_host(self):
		print "closed_by_host()"
		gtk.main_quit()
		pass
	
	def get_save_status(self):
		print "save_status()"
		return self.__save_status
	
	def set_save_status(self,status):
		self.__save_status = status
		self.bus_obj.SaveStatusChanged(self.__save_status)
	
	def get_description(self):
		return "PID {0}".format(os.getpid())

	
	def get_title(self):
		return self.__title
	
	def set_title(self,title):
		if None != title:
			self.__title = title
			self.bus_obj.TitleChanged(self.__title)
	
	def get_proxy_icon_path(self):
		return self.__proxy_icon_path
	
	def set_proxy_icon_path(self,path):
		self.__proxy_icon_path = path
		self.bus_obj.ProxyIconChanged(self.__proxy_icon_path)
		
	
class ComponentClientDBus(dbus.service.Object):
	realobj = None
	
	def __init__(self, bus, object_path, realobj):
		dbus.service.Object.__init__(self, bus, object_path)
		self.realobj = realobj
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='i')
	def Prepare(self):
		return self.realobj.prepare()
	
	@dbus.service.method(dbus_interface='org.ude.components.client')
	def Save(self):
		self.realobj.save()
	
	@dbus.service.method(dbus_interface='org.ude.components.client')
	def NotifyClosedByHost(self):
		self.realobj.notify_closed_by_host()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='i')
	def GetSaveStatus(self):
		return self.realobj.get_save_status()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='s')
	def GetDescription(self):
		return self.realobj.get_description()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='s')
	def GetTitle(self):
		return self.realobj.get_title()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='s')
	def GetProxyIconPath(self):
		return self.realobj.get_proxy_icon_path()
	
	@dbus.service.signal(dbus_interface='org.ude.components.client', signature='s')
	def TitleChanged(self, title):
		pass
	
	@dbus.service.signal(dbus_interface='org.ude.components.client', signature='s')
	def ProxyIconChanged(self, path):
		pass
	
	@dbus.service.signal(dbus_interface='org.ude.components.client', signature='i')
	def SaveStatusChanged(self, save_status):
		pass
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	







































