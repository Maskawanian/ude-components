import sys,os
import gobject,pygtk,gtk
import Components.Client

class DemoClient(Components.Client.Base):
	allow_close = False
	
	def __init__(self,hostPID):
		super(DemoClient, self).__init__(hostPID)
	
	def prepare_new_widget(self):
		ret = gtk.Button("demo client")
		ret.connect("clicked",self.button_press)
		return ret
	
	def button_press(self,sender):
		print "click"
		allow_close = True
		pass
	
	def allow_close(self):
		return allow_close
