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
	
	__glade_prefix = ""
	__glade_builder = gtk.Builder()
	
	__outerbox = None
	__tb = None
	__tb_back = None
	__tb_forward = None
	__tb_reload = None
	__tb_stop = None
	__tb_address = None
	__tb_address_entry = None
	__tb_address_entry_image = None
	
	__wv = None
	__wv_sw = None
	
	__favicon_path = None
	
	def __init__(self,hostPID):
		super(WebClient, self).__init__(hostPID)
		
		try:
			self.__glade_prefix = os.environ["GLADE_PREFIX"]
		except KeyError:
			print "No Glade Environment"
		
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
		
		self.__glade_builder = gtk.Builder()
		self.__glade_builder.add_from_file(self.__glade_prefix+"webclient.glade")
		
		self.__outerbox = self.__glade_builder.get_object("outerbox")
		self.__tb = self.__glade_builder.get_object("toolbar")
		
		self.__tb_back = gtk.ToolButton(gtk.STOCK_GO_BACK)
		self.__tb_back.connect("clicked",self.__tb_back_clicked)
		self.__tb.insert(self.__tb_back,-1)
		
		self.__tb_forward = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
		self.__tb_forward.connect("clicked",self.__tb_forward_clicked)
		self.__tb.insert(self.__tb_forward,-1)
		
		self.__tb_reload = gtk.ToolButton(gtk.STOCK_REFRESH)
		self.__tb_reload.connect("clicked",self.__tb_reload_clicked)
		self.__tb.insert(self.__tb_reload,-1)
		
		self.__tb_stop = gtk.ToolButton(gtk.STOCK_STOP)
		self.__tb_stop.connect("clicked",self.__tb_stop_clicked)
		self.__tb.insert(self.__tb_stop,-1)
		
		self.__tb_address = gtk.ToolItem()
		self.__tb_address.set_expand(True)
		self.__tb_address_entry = sexy.IconEntry()
		self.__tb_address_entry_image = gtk.image_new_from_file("/usr/share/ude/components/16x16doc.svg")
		self.__tb_address_entry.set_icon(sexy.ICON_ENTRY_PRIMARY,self.__tb_address_entry_image)
		self.__tb_address_entry.connect("activate",self.__tb_address_entry_activate)
		self.__tb_address.add(self.__tb_address_entry)
		self.__tb.insert(self.__tb_address,-1)
		
		self.__wv = WebViewTab()
		self.__wv.connect("notify::uri",self.__wv_notify_uri)
		self.__wv.connect("notify::progress",self.__wv_notify_progress)
		self.__wv.connect("notify::load-status",self.__wv_notify_load_status)
		self.__wv.connect("notify::title",self.__wv_notify_title)
		self.__wv.connect("notify::icon-uri",self.__wv_notify_icon_uri)
		
		self.__wv.connect("load-error",self.__wv_load_error)
		self.__wv.connect("resource-request-starting",self.__wv_resource_request_starting)
		
		
		__wv_sw = gtk.ScrolledWindow()
		__wv_sw.add(self.__wv)
		self.__outerbox.pack_start(__wv_sw,expand=True,fill=True)
		
		return self.__outerbox
	
	def __tb_address_entry_activate(self,sender):
		text = self.__tb_address_entry.get_text().strip()
		if text == None or text == "": return
		
		validated_url = None
		
		scheme, netloc, path, params, query, fragment = urlparse.urlparse(text)
		if scheme == '':
			if netloc == '':
				if path == '':
					raise Exception("scheme netloc and path are all empty...")
				else:
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
		
		self.__tb_address_entry.set_text(validated_url)
		self.__wv.load_uri(validated_url)
		
		window = self.__tb_address_entry.get_ancestor(gtk.Window.__gtype__)
		if None != window: window.set_focus(self.__wv)
		pass
	
	def __tb_back_clicked(self,sender):
		self.__wv.go_back()
	
	def __tb_forward_clicked(self,sender):
		self.__wv.go_forward()
	
	def __tb_reload_clicked(self,sender):
		self.__wv.reload()
	
	def __tb_stop_clicked(self,sender):
		self.__wv.stop_loading()
	
	def __wv_notify_uri(self,sender,arg):
		self.__tb_address_entry.set_text(self.__wv.get_main_frame().get_uri())
	
	def __wv_notify_progress(self,sender,arg):
		print "progress",self.__wv.get_property("progress")
	
	def __wv_notify_load_status(self,sender,arg):
		status = self.__wv.get_property("load-status")
		print "load status",status
		self.__tb_reload.set_sensitive(status == webkit.LOAD_FINISHED)
		self.__tb_stop.set_sensitive(status != webkit.LOAD_FINISHED)
		
		# if we are not loading we delete the favicon, this may be a good idea to cache later.
		if status != webkit.LOAD_FINISHED and status != webkit.LOAD_FIRST_VISUALLY_NON_EMPTY_LAYOUT:
			if self.__favicon_path != None:
				os.remove(self.__favicon_path)
				self.__favicon_path = None
		
		if status != webkit.LOAD_FINISHED:
			self.set_proxy_icon_path("/usr/share/ude/components/loading.gif")
			self.set_proxy_icon_path("/usr/share/ude/components/16x16doc.svg")
		else:
			# Set the Icon used for the tab.
			path = None
			if None != self.__favicon_path:
				path = self.__favicon_path
			else:
				path = "/usr/share/ude/components/16x16doc.svg"
			self.set_proxy_icon_path(path)
			
			anim = gtk.gdk.PixbufAnimation(path)
			
			pb = gtk.gdk.pixbuf_new_from_file_at_size(path,16,16)
			self.__tb_address_entry_image.set_from_pixbuf(pb)
		
		# Update buttons.
		self.__tb_back.set_sensitive(self.__wv.can_go_back())
		self.__tb_forward.set_sensitive(self.__wv.can_go_forward())
	
	def __wv_notify_title(self,sender,arg):
		title = self.__wv.get_property("title")
		self.set_title(title)
	
	def __wv_notify_icon_uri(self,sender,arg):
		uri = self.__wv.get_property("icon-uri")
		filename, headers = urllib.urlretrieve(uri)
		self.__favicon_path = filename
	
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
		#print rule
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






































