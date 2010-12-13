# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib

class ComponentHostDBus(dbus.service.Object):
	realobj = None
	
	def __init__(self, bus, object_path, realobj):
		dbus.service.Object.__init__(self, bus, object_path)
		self.realobj = realobj
	
	@dbus.service.method(dbus_interface='org.ude.components.host',in_signature='i')
	def AddPID(self, pid):
		self.realobj.add_pid(pid)
	
	@dbus.service.method(dbus_interface='org.ude.components.host',in_signature='i')
	def RemovePID(self, pid):
		self.realobj.remove_pid(pid)
