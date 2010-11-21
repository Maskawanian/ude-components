# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os,argparse
import gobject,pygtk,gtk,gio
import dbus,dbus.service,dbus.mainloop.glib
import subprocess,threading
import webkit
import sexy
import urllib,urlparse
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
	
	tlds = ["aero","asia","biz","cat","com","coop",\
		"edu","gov","info","int","jobs","mil","mobi",\
		"museum","name","net","org","pro","tel","travel",\
		"ac","ad","ae","af","ag","ai","al","am","an",\
		"ao","aq","ar","as","at","au","aw","ax","az",\
		"ba","bb","bd","be","bf","bg","bh","bi","bj",\
		"bm","bn","bo","br","bs","bt","bv","bw","by",\
		"bz","ca","cc","cd","cf","cg","ch","ci","ck",\
		"cl","cm","cn","co","cr","cu","cv","cx","cy",\
		"cz","de","dj","dk","dm","do","dz","ec","ee",\
		"eg","er","es","et","eu","fi","fj","fk","fm",\
		"fo","fr","ga","gb","gd","ge","gf","gg","gh",\
		"gi","gl","gm","gn","gp","gq","gr","gs","gt",\
		"gu","gw","gy","hk","hm","hn","hr","ht","hu",\
		"id","ie","il","im","in","io","iq","ir","is",\
		"it","je","jm","jo","jp","ke","kg","kh","ki",\
		"km","kn","kp","kr","kw","ky","kz","la","lb",\
		"lc","li","lk","lr","ls","lt","lu","lv","ly",\
		"ma","mc","md","me","mg","mh","mk","ml","mm",\
		"mn","mo","mp","mq","mr","ms","mt","mu","mv",\
		"mw","mx","my","mz","na","nc","ne","nf","ng",\
		"ni","nl","no","np","nr","nu","nz","om","pa",\
		"pe","pf","pg","ph","pk","pl","pm","pn","pr",\
		"ps","pt","pw","py","qa","re","ro","rs","ru",\
		"rw","sa","sb","sc","sd","se","sg","sh","si",\
		"sj","sk","sl","sm","sn","so","sr","st","su",\
		"sv","sy","sz","tc","td","tf","tg","th","tj",\
		"tk","tl","tm","tn","to","tp","tr","tt","tv",\
		"tw","tz","ua","ug","uk","us","uy","uz","va",\
		"vc","ve","vg","vi","vn","vu","wf","ws","ye",\
		"yt","yt","za","zm","zw","xn--fiqs8s","xn--fiqz9s",\
		"xn--wgbh1c","xn--j6w193g","xn--mgba3a4f16a",\
		"xn--mgbayh7gpa","xn--ygbi2ammx","xn--p1ai",\
		"xn--mgberp4a5d4ar","xn--fzc2c9e2c",\
		"xn--xkc2al3hye2a","xn--kprw13d","xn--kpry57d",\
		"xn--o3cw4h","xn--pgbs0dh","xn--mgbaam7a8h"]
	
	__adblock_rules_uri = []
	__adblock_rules_uri_exceptions = []
	__adblock_rules_element = []
	__adblock_rules_element_exceptions = []
	
	def __init__(self,hostPID):
		super(WebClient, self).__init__(hostPID)
		self.set_title("blank page")
		
		self.parse_adblock_fitlers()
		
		pass
	
	def parse_adblock_fitlers(self):
		f = open('/home/dan/Desktop/Programming/ude/ude-components/client/easylist.txt', 'r')
		for line in f:
			if line.find("!") != -1:
				# Comment
				pass
			elif line.find("##") != -1:
				if line.find("@@") != -1:
					self.__adblock_rules_element_exceptions.append(line.strip())
				else:
					self.__adblock_rules_element.append(line.strip())
			else:
				if line.find("@@") != -1:
					self.__adblock_rules_uri_exceptions.append(line.strip())
				else:
					self.__adblock_rules_uri.append(line.strip())
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
		im = gtk.image_new_from_file("/usr/share/ude/components/16x16doc.svg")
		self.__uri_entry = sexy.IconEntry()
		self.__uri_entry.set_icon(sexy.ICON_ENTRY_PRIMARY,im)
		self.__uri_entry.connect("activate",self.__uri_entry_activate)
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
		self.__wv.connect("resource-request-starting",self.__wv_resource_request_starting)
		
		sw = gtk.ScrolledWindow()
		sw.add(self.__wv)
		
		vbox.pack_start(self.toolbar,expand=False,fill=True)
		vbox.pack_start(sw,expand=True,fill=True)
		
		
		return vbox
	#http://www.google.ca/search?&q=pie
	def __uri_entry_activate(self,sender):
		text = self.__uri_entry.get_text().strip()
		if text == None or text == "": return
		
		
		validated_url = None
		
		scheme, netloc, path, params, query, fragment = urlparse.urlparse(text)
		if scheme == '':
			if netloc == '':
				if path == '':
					raise Exception("scheme netloc and path are all empty...")
				else:
					#
					#
					if path.startswith("www."):
						validated_url = "http://"+text
					else:
						for tld in self.tlds:
							if path.find("."+tld) != -1 and path.find(" ") == -1:
								validated_url = "http://"+text
						if None == validated_url:	
							validated_url = "http://www.google.ca/search?&q="+urllib.quote_plus(text)
			else:
				validated_url = "http://"+text
		else:
			validated_url = text
		
		self.__uri_entry.set_text(validated_url)
		self.__wv.load_uri(validated_url)
		
		window = self.__uri_entry.get_ancestor(gtk.Window.__gtype__)
		if None != window: window.set_focus(self.__wv)
		print "activate",text
		pass
	
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
				self.set_proxy_icon_path("/usr/share/ude/components/loading.gif")
			else:
				# Set the Icon used for the tab.
				path = None
				if None != self.__favicon_path:
					path = self.__favicon_path
				else:
					path = "/usr/share/ude/components/16x16doc.svg"
				self.set_proxy_icon_path(path)
				
				# Set the address bar's icon.
				i = self.__uri_entry.get_icon(sexy.ICON_ENTRY_PRIMARY)
				if path.endswith((".gif",".apng",".mng")):
					anim = gtk.gdk.PixbufAnimation(path)
					i.set_from_animation(anim)
				else:
					print "path",path
					pb = None
					try:
						pb = gtk.gdk.pixbuf_new_from_file_at_size(path,16,16)
					except:
						pb = gtk.gdk.pixbuf_new_from_file_at_size("/usr/share/ude/components/16x16doc.svg",16,16)
					i.set_from_pixbuf(pb)
					
				
				
		elif pspec.name == "title":
			title = self.__wv.get_property("title")
			self.set_title(title)
		elif pspec.name == "icon-uri":
			uri = self.__wv.get_property("icon-uri")
			filename, headers = urllib.urlretrieve(uri)
			self.__favicon_path = filename
		elif pspec.name in ["has-tooltip","has-focus","is-focus","parent","visible","style","window","events"]:
			pass
		else:
			print "unhandled",pspec.name
		
		# Update buttons.
		self.__back_button.set_sensitive(self.__wv.can_go_back())
		self.__forward_button.set_sensitive(self.__wv.can_go_forward())
	
	def __wv_load_error(self,sender,frame,arg,arg2):
		print "__wv_load_error",self,sender,frame,arg,arg2
	
	def __wv_resource_request_starting(self,webview,web_frame,web_resource,request,response):
		uri = request.get_uri()
		#scheme, netloc, path, params, query, fragment = urlparse.urlparse(uri)
		#scheme, netloc, path, params, query, fragment, username, password, hostname, port = \
		#	urlparse.urlparse(request.get_uri())
		
		for rule in self.__adblock_rules_uri:
			if self.__uri_matches_rule(uri,rule):
				request.set_uri("about:blank")
		
		
		
		
		
		#if netloc == "www.google-analytics.com":
		#	request.set_uri("about:blank")
		
		#file:///usr/share/ude/components/spacer.gif
		
		#print "__wv_resource_request_starting",scheme, netloc, path, params, query, fragment
		pass
	
	def __uri_matches_rule(self,uri,rule):
		
		#print "__uri_matches_rule",rule
		
		if rule.find("*") != -1 or rule.find("^") != -1 or rule.find("|") != -1 or rule.find("~") != -1:
			
			pass
		#elif regex:
		else:
			return self.__uri_matches_rule_simple(uri,rule)
		
		
		return False
	
	def __uri_matches_rule_simple(self,uri,rule):
		print rule
		return False
	
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
		
	def populate_popup(self, view, menu):
		pass
	
if __name__ == "__main__":
	main()






































