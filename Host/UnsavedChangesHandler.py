import sys,os
import gobject,pygtk,gtk,gio,pango
from Components import Client
gobject.threads_init ()

class UnsavedChangesHandler(object):
	glade_prefix = ""
	builder = None
	window = None
	
	clients_denying_close = None
	
	button_save_all = None
	button_cancel = None
	button_dont_save = None
	
	delegate = None
	
	def __init__(self,clients_denying_close,delegate):
		super(UnsavedChangesHandler, self).__init__()
		try:
			self.glade_prefix = os.environ["GLADE_PREFIX"]
		except KeyError:
			print "No Glade Environment"
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(self.glade_prefix+"UnsavedChangesHandler.glade")
		self.window = self.builder.get_object("window")
		self.button_save_all = self.builder.get_object("buttonSaveAll") 
		self.button_cancel = self.builder.get_object("buttonCancel") 
		self.button_dont_save = self.builder.get_object("buttonDontSave") 
		self.vbox = self.builder.get_object("vbox") 
		
		self.clients_denying_close = clients_denying_close
		self.delegate = delegate
		
		self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
		self.window.set_deletable(False)
		self.window.set_resizable(False)
		self.window.set_title("Save Changes?")
		#self.window.set_decorated(False)
		
		for client in self.clients_denying_close:
			
			
			# We need to make a manual save row for the client.
			client.__unsaved_hbox = gtk.HBox(spacing=10)
			client.__unsaved_image = gtk.image_new_from_stock("gtk-save",gtk.ICON_SIZE_BUTTON)
			client.__unsaved_label = gtk.Label("NO LABEL SET")
			client.__unsaved_label.set_justify(gtk.JUSTIFY_LEFT)
			client.__unsaved_label.set_alignment(0,0.5)
			client.__unsaved_label.set_ellipsize(pango.ELLIPSIZE_END)
			client.__unsaved_label.set_line_wrap(False)
			client.__unsaved_label.set_selectable(True)
			client.__unsaved_button_dontsave = gtk.Button("Don't Save")
			client.__unsaved_button_dontsave.connect("clicked",self.__cb_dont_save_specific_client,client)
			client.__unsaved_button_dontsave.set_size_request(100,-1)
			client.__unsaved_button_save = gtk.Button("Save")
			client.__unsaved_button_save.connect("clicked",self.__cb_save_specific_client,client)
			client.__unsaved_button_save.set_size_request(100,-1)
			client.__unsaved_hbox.pack_start(client.__unsaved_image,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_label)
			client.__unsaved_hbox.pack_start(client.__unsaved_button_dontsave,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_button_save,expand=False)
			self.vbox.pack_start(client.__unsaved_hbox,expand=False)
			
			description = client.GetDescription()
			client.__unsaved_label.set_markup(description)
			
		self.button_save_all.connect("clicked",self.__cb_save_all)
		self.button_cancel.connect("clicked",self.__cb_cancel)
		self.button_dont_save.connect("clicked",self.__cb_dont_save_all)
	
	def show(self,parent):
		self.window.set_modal(True)
		self.window.set_transient_for(parent)
		self.window.show_all()
		pass
	
	def save_specific_client(self,client):
		print "save_specific_client",client
		pass
	
	def dont_save_specific_client(self,client):
		print "dont_save_specific_client",client
		pass
	
	def save_all(self):
		print "save_all"
		pass
	
	def dont_save_all(self):
		print "dont_save_all"
		pass
	
	def cancel(self):
		self.window.hide()
		self.delegate.update_unsaved_changes_handler(0)
	
	def __cb_save_specific_client(self,sender,client):
		self.save_specific_client(client)
		
	def __cb_dont_save_specific_client(self,sender,client):
		self.dont_save_specific_client(client)
	
	def __cb_save_all(self,sender):
		self.save_all()
	
	def __cb_dont_save_all(self,sender):
		self.dont_save_all()
	
	def __cb_cancel(self,sender):
		self.cancel()
	
	def __cb_window_delete_event(self,sender,event):
		self.cancel()
		return True # Stop Delete
	
	def update_save_status(self,client,status):
		print "update_save_status",client,status
		pass
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
