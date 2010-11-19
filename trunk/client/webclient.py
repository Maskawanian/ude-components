# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading
import webkit
import sexy
import urllib
gobject.threads_init ()

# Fix missing variables in pywebkit.
webkit.LOAD_PROVISIONAL = 0
webkit.LOAD_COMMITTED = 1
webkit.LOAD_FINISHED = 2
webkit.LOAD_FIRST_VISUALLY_NON_EMPTY_LAYOUT = 3
webkit.LOAD_FAILED = 4

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
	__back_button = None
	__forward_button = None
	__reload_button = None
	__stop_button = None
	__uri_entry = None
	__favicon_path = None
	
	def __init__(self,hostPID):
		super(WebClient, self).__init__(hostPID)
		self.set_title("blank page")
		
		pass
	
	def prepare_new_widget(self):
		self.toolbar = gtk.Toolbar()
		
		self.__back_button = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_GO_BACK,2)
		self.__back_button.set_icon_widget(im)
		self.__back_button.connect("clicked",self.__tb_back_button_clicked)
		self.toolbar.insert(self.__back_button,-1)
		
		self.__forward_button = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_GO_FORWARD,2)
		self.__forward_button.set_icon_widget(im)
		self.__forward_button.connect("clicked",self.__tb_forward_button_clicked)
		self.toolbar.insert(self.__forward_button,-1)
		
		self.__reload_button = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_REFRESH,2)
		self.__reload_button.set_icon_widget(im)
		self.__reload_button.connect("clicked",self.__tb_reload_button_clicked)
		self.toolbar.insert(self.__reload_button,-1)
		
		self.__stop_button = gtk.ToolButton()
		im = gtk.image_new_from_stock(gtk.STOCK_STOP,2)
		self.__stop_button.set_icon_widget(im)
		self.__stop_button.connect("clicked",self.__tb_stop_button_clicked)
		self.toolbar.insert(self.__stop_button,-1)
		
		tb = gtk.ToolItem()
		tb.set_expand(True)
		im = gtk.image_new_from_file("16x16doc.svg")
		self.__uri_entry = sexy.IconEntry()
		self.__uri_entry.set_icon(sexy.ICON_ENTRY_PRIMARY,im)
		tb.add(self.__uri_entry)
		self.toolbar.insert(tb,-1)
		
		#tb = gtk.ToolButton()
		#im = gtk.image_new_from_stock(gtk.STOCK_ABOUT,2)
		#tb.set_icon_widget(im)
		#self.toolbar.insert(tb,-1)
		
		#tb = gtk.ToolButton()
		#im = gtk.image_new_from_stock(gtk.STOCK_PROPERTIES,2)
		#tb.set_icon_widget(im)
		#self.toolbar.insert(tb,-1)
		
		vbox = gtk.VBox()
		self.__wv = WebViewTab()
		self.__wv.connect("notify",self.__wv_notify)
		self.__wv.connect("load-error",self.__wv_load_error)
		
		sw = gtk.ScrolledWindow()
		sw.add(self.__wv)
		
		vbox.pack_start(self.toolbar,expand=False,fill=True)
		vbox.pack_start(sw,expand=True,fill=True)
		
		
		return vbox
	
	def __tb_back_button_clicked(self,sender):
		self.__wv.go_back()
	
	def __tb_forward_button_clicked(self,sender):
		self.__wv.go_forward()
	
	def __tb_reload_button_clicked(self,sender):
		self.__wv.reload()
	
	def __tb_stop_button_clicked(self,sender):
		self.__wv.stop_loading()
	
	
	def __wv_notify(self,sender,pspec):
		if pspec.name == "uri":
			#print self.__wv.get_property("load-status")
			self.__uri_entry.set_text(self.__wv.get_main_frame().get_uri())
		elif pspec.name == "progress":
			print "progress",self.__wv.get_property("progress")
		elif pspec.name == "load-status":
			status = self.__wv.get_property("load-status")
			print "load status",status
			self.__reload_button.set_sensitive(status == webkit.LOAD_FINISHED)
			self.__stop_button.set_sensitive(status != webkit.LOAD_FINISHED)
			
			# if we are not loading we delete the favicon, this may be a good idea to cache later.
			if status != webkit.LOAD_FINISHED and status != webkit.LOAD_FIRST_VISUALLY_NON_EMPTY_LAYOUT:
				if self.__favicon_path != None:
					os.remove(self.__favicon_path)
					self.__favicon_path = None
			
			if status != webkit.LOAD_FINISHED:
				self.set_proxy_icon_path("/home/dan/Desktop/Programming/ude/ude-components/loader.gif")
			else:
				# Set the Icon used for the tab.
				path = None
				if None != self.__favicon_path:
					path = self.__favicon_path
				else:
					path = "/home/dan/Desktop/Programming/ude/ude-components/client/16x16doc.svg"
				self.set_proxy_icon_path(path)
				
				# Set the address bar's icon.
				i = self.__uri_entry.get_icon(sexy.ICON_ENTRY_PRIMARY)
				if path.endswith((".gif",".apng",".mng")):
					anim = gtk.gdk.PixbufAnimation(path)
					i.set_from_animation(anim)
				else:
					pb = gtk.gdk.pixbuf_new_from_file_at_size(path,16,16)
					i.set_from_pixbuf(pb)
				
				
		elif pspec.name == "title":
			title = self.__wv.get_property("title")
			self.set_title(title)
		elif pspec.name == "icon-uri":
			uri = self.__wv.get_property("icon-uri")
			
			filename, headers = urllib.urlretrieve(uri)
			self.__favicon_path = filename
			
			
			
			
			
			
			
			
			
			
			print "icon-uri",uri,"__favicon_path",self.__favicon_path
		elif pspec.name in ["has-tooltip","has-focus","is-focus","parent","visible","style","window","events"]:
			pass
		else:
			print "unhandled",pspec.name
		
		# Update buttons.
		self.__back_button.set_sensitive(self.__wv.can_go_back())
		self.__forward_button.set_sensitive(self.__wv.can_go_forward())
	
	def __wv_load_error(self,sender,frame,arg,arg2):
		print "__wv_load_error",self,sender,frame,arg,arg2
	
	
class WebViewTab(webkit.WebView):
	settings = None
	
	def __init__(self):
		webkit.WebView.__init__(self)
		
		self.settings = self.get_settings()
		#self.settings.set_property("enable-developer-extras", True)
		
		# scale other content besides from text as well
		self.set_full_content_zoom(True)
		self.set_highlight_text_matches(True)
		
		
		#self.set_view_source_mode(True)
		
		# make sure the items will be added in the end
		# hence the reason for the connect_after
		self.connect_after("populate-popup", self.populate_popup)
		
		self.load_uri("http://www.google.com")
		#self.load_uri("http://tsunami/tmp")
		
	def populate_popup(self, view, menu):
		pass
	
if __name__ == "__main__":
	main()






































