import sys,os
import gobject,pygtk,gtk
import Components.Client

class DemoClient(Components.Client.Base):
	
	def __init__(self,hostPID):
		super(DemoClient, self).__init__(hostPID)
		self.set_save_status(Components.Client.SAVE_STATUS_NOT_SAVED)
		
	
	def prepare_new_widget(self):
		ret = gtk.Button("demo client")
		ret.connect("clicked",self.button_press)
		return ret
	
	def button_press(self,sender):
		print "click"
		self.set_save_status(Components.Client.SAVE_STATUS_SAVED)
		pass
