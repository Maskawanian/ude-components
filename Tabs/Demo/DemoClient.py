import sys,os
import gobject,pygtk,gtk
import Components.Client

class DemoClient(Components.Client.Base):
	
	def __init__(self,hostPID):
		super(DemoClient, self).__init__(hostPID)
	
	def prepare_new_widget(self):
		ret = gtk.Button("demo client")
		ret.connect("clicked",self.button_press)
		return ret
	
	def button_press(self,sender):
		print "click"
		pass
	
	def save_status(self):
		print "save_status()"
		return Components.Client.SAVE_STATUS_NOT_SAVED
