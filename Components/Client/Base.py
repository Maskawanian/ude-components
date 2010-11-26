# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading
gobject.threads_init ()

prefix_glade_host = "/home/dan/Desktop/Programming/ude/ude-components/Host/"
path_python = "/usr/bin/python2"
path_host_script = "/home/dan/Desktop/Programming/ude/ude-components/Host/Host.py"

class Base(object):
	bus = None
	bus_name = None
	bus_obj = None
	
	widget = None # Widget that will be embeded.
	plug = None   
	
	__title = "untitled {0}".format(os.getpid())
	__proxy_icon_path = "/usr/share/ude/components/16x16doc.svg"
	
	def __init__(self,hostPID):
		#super(Base, self).__init__()
		print "init",hostPID
		dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
		self.bus = dbus.SessionBus()
		self.bus_name = dbus.service.BusName("org.ude.components.client_"+str(os.getpid()), self.bus)
		self.bus_obj = ComponentClientDBus(self.bus,'/org/ude/components/client',self)
		
		if hostPID == 0:
			fd = os.open(os.devnull, os.O_RDWR)
			env = os.environ.copy()
			env["GLADE_PREFIX"] = prefix_glade_host
			subprocess.Popen(['setsid',path_python,path_host_script,"-a",str(os.getpid())],env=env,stdout=fd,stderr=fd)
		else:
			print "connect to host"
			
			host_bus_name = "org.ude.components.host_"+str(hostPID)
			if False == self.bus.name_has_owner(host_bus_name):
				raise Exception("The bus `"+host_bus_name+"` does not exist.")
			
			remotehost = self.bus.get_object(host_bus_name,"/org/ude/components/host")
			remotehost.AddPID(os.getpid(),dbus_interface="org.ude.components.host",reply_handler=self.add_pid_reply,error_handler=self.add_pid_reply_error)
		pass
	
	def add_pid_reply(self): #stub
		pass
	
	def add_pid_reply_error(self,e):
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
	
	def prepare_new_widget(self):
		ret = gtk.Button("Default Widget")
		return ret
	
	def allow_close(self):
		print "allow_close()"
		return True
	
	def show_allow_close_prompt(self):
		print "show_allow_close_prompt()"
		pass
	
	def closed_by_host(self):
		print "closed_by_host()"
		gtk.main_quit()
		pass
	
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
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='b')
	def AllowClose(self):
		return self.realobj.allow_close()
	
	
	
	
	
	
	
	
	
	
	@dbus.service.method(dbus_interface='org.ude.components.client')
	def ShowAllowClosePrompt(self):
		self.realobj.show_allow_close_prompt()
	
	@dbus.service.method(dbus_interface='org.ude.components.client')
	def ClosedByHost(self):
		self.realobj.closed_by_host()
	
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







































