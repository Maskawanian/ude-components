# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading
import webkit
import sexy
gobject.threads_init ()

from ComponentClient import ComponentClient

client = None

def main():
	global client
	
	# Arguments
	parser = argparse.ArgumentParser(description='A generic client example.')
	parser.add_argument('-o','--host',type=int,default=0,help="the PID that this client will embed itself into, if left out will spawn its own host")
	args = parser.parse_args()
	
	# DBus
	print "Client PID",os.getpid()
	
	client = WebClient(args.host)
	gtk.main()
	pass

class WebClient(ComponentClient):
	__toolbar = None
	__wv = None
	
	def prepare_new_widget(self):
		self.toolbar = gtk.Toolbar()
		
		tb = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_GO_BACK,2)
		tb.set_icon_widget(im)
		self.toolbar.insert(tb,-1)
		
		tb = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD,2)
		tb.set_icon_widget(im)
		self.toolbar.insert(tb,-1)
		
		tb = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_REFRESH,2)
		tb.set_icon_widget(im)
		self.toolbar.insert(tb,-1)
		
		tb = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_STOP,2)
		tb.set_icon_widget(im)
		self.toolbar.insert(tb,-1)
		
		tb = gtk.ToolItem()
		tb.set_expand(True)
		im = gtk.image_new_from_file("16x16doc.svg")
		e = sexy.IconEntry()
		e.set_icon(sexy.ICON_ENTRY_PRIMARY,im)
		tb.add(e)
		self.toolbar.insert(tb,-1)
		
		tb = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_ABOUT,2)
		tb.set_icon_widget(im)
		self.toolbar.insert(tb,-1)
		
		tb = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_PROPERTIES,2)
		tb.set_icon_widget(im)
		self.toolbar.insert(tb,-1)
		
		vbox = gtk.VBox()
		self.__wv = WebViewTab()
		sw = gtk.ScrolledWindow()
		sw.add(self.__wv)
		
		vbox.pack_start(self.toolbar,expand=False,fill=True)
		vbox.pack_start(sw,expand=True,fill=True)
		
		
		return vbox

class WebViewTab(webkit.WebView):
	settings = None
	
	def __init__(self):
		webkit.WebView.__init__(self)
		
		self.settings = self.get_settings()
		self.settings.set_property("enable-developer-extras", True)
		
		# scale other content besides from text as well
		self.set_full_content_zoom(True)
		
		# make sure the items will be added in the end
		# hence the reason for the connect_after
		self.connect_after("populate-popup", self.populate_popup)
		
		self.load_uri("http://www.google.com")
	
	def populate_popup(self, view, menu):
		pass
	
if __name__ == "__main__":
	main()






































