# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

import sys,os
import gobject,pygtk,gtk
import webkit

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
