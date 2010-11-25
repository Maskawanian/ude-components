import sys,os
import gobject,pygtk,gtk
import Components.Client

class DemoClient(Components.Client.base):
	def prepare_new_widget(self):
		ret = gtk.Button("demo client")
		ret.connect("clicked",self.button_press)
		return ret
	
	def button_press(self,sender):
		print "click"
		pass
