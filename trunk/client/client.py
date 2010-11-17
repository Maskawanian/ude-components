# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading
gobject.threads_init ()

app = None
dbusobj = None
bus = None
arg_host = None
prefix_glade_host = "/home/dan/Desktop/Programming/ude/ude-components/host/"
path_python = "/usr/bin/python2"
path_host_script = "/home/dan/Desktop/Programming/ude/ude-components/host/host.py"

def main():
	global app
	global dbusobj
	global bus
	global arg_host
	
	# Arguments
	parser = argparse.ArgumentParser(description='A generic client example.')
	parser.add_argument('-o','--host',type=int,default=0,help="the PID that this client will embed itself into, if left out will spawn its own host")
	args = parser.parse_args()
	arg_host = args.host
	print args
	
	# DBus
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SessionBus()
	name = dbus.service.BusName("org.ude.components.client_"+str(os.getpid()), bus)
	dbusobj = Example(bus,'/org/ude/components/client')
	
	print "Client PID",os.getpid()
	
	app = App()
	gtk.main()
	pass

class App:
	widget = None # Widget that will be embeded.
	plug = None   
	
	def __init__(self):
		if arg_host == 0:
			fd = os.open(os.devnull, os.O_RDWR)
			env = os.environ.copy()
			env["GLADE_PREFIX"] = prefix_glade_host
			subprocess.Popen(['setsid',path_python,path_host_script,"-a",str(os.getpid())],env=env,stdout=fd,stderr=fd)
		else:
			print "connect to host"
			remotehost = bus.get_object("org.ude.components.client_"+str(arg_host),"/org/ude/components/client")
			
			
			
		pass
	
	def prepare(self):
		'''
		Prepare a widget for embedding. If it is already embeded this will break the widget free.
		'''
		
		newplug = gtk.Plug(0)
		
		if None == self.widget:
			self.widget = gtk.Button("button")
			self.widget.connect("clicked",self.button_press)
			
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
	
	def button_press(self,sender):
		#self.prepare()
		pass
	
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
		return "untitled {0}".format(os.getpid())
	
	def get_proxy_icon_path(self):
		return "/home/dan/Desktop/Programming/ude/ude-components/client/16x16doc.svg"
		
	
class Example(dbus.service.Object):
	def __init__(self, bus, object_path):
		dbus.service.Object.__init__(self, bus, object_path)
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='i')
	def Prepare(self):
		return app.prepare()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='b')
	def AllowClose(self):
		return app.allow_close()
	
	@dbus.service.method(dbus_interface='org.ude.components.client')
	def ShowAllowClosePrompt(self):
		app.show_allow_close_prompt()
	
	@dbus.service.method(dbus_interface='org.ude.components.client')
	def ClosedByHost(self):
		app.closed_by_host()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='s')
	def GetTitle(self):
		return app.get_title()
	
	@dbus.service.method(dbus_interface='org.ude.components.client', out_signature='s')
	def GetProxyIconPath(self):
		return app.get_proxy_icon_path()
	
	@dbus.service.signal(dbus_interface='org.ude.components.client', signature='s')
	def TitleChanged(self, title):
		pass
	
	@dbus.service.signal(dbus_interface='org.ude.components.client', signature='s')
	def ProxyIconChanged(self, path):
		pass

if __name__ == "__main__":
	main()


