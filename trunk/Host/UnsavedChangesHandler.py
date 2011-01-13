import sys,os
import gobject,pygtk,gtk,gio,pango
from Components import Client,Host
import logging
gobject.threads_init ()

l = Host.logger

# TODO! Add a customized display if all the tabs are Client.SAVE_STATUS_UNSAVABLE

class UnsavedChangesHandler(object):
	builder = None
	window = None
	
	clients_denying_close = None
	
	button_save_all = None
	button_cancel = None
	button_dont_save = None
	
	delegate = None
	
	def __init__(self,clients_denying_close,delegate):
		"""
		Displays a window allowing the user to choose which tabs are saved, or if all of them are.
		- clients_denying_close must have at least one item within it to ask the user.
		- delegate must be not null, it must also respond to the following:
		  - unsaved_changes_handler_cb(resolution)
		"""
		assert None != clients_denying_close
		assert len(clients_denying_close) > 0
		assert None != delegate
		
		super(UnsavedChangesHandler, self).__init__()
		
		self.builder = gtk.Builder()
		self.builder.add_from_file(Host.glade_prefix+"UnsavedChangesHandler.glade")
		self.window = self.builder.get_object("window")
		self.button_save_all = self.builder.get_object("buttonSaveAll") 
		self.button_cancel = self.builder.get_object("buttonCancel") 
		self.button_dont_save = self.builder.get_object("buttonDontSave") 
		self.vbox = self.builder.get_object("vbox")
		
		assert None != self.builder
		assert None != self.window
		assert None != self.button_save_all
		assert None != self.button_cancel
		assert None != self.button_dont_save
		assert None != self.vbox
		
		self.__clients_denying_close = clients_denying_close
		self.delegate = delegate
		
		self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
		self.window.set_deletable(False)
		self.window.set_title("Save Changes?")
		
		for client in self.__clients_denying_close:
			
			# We need to make a manual save row for the client.
			client.__unsaved_hbox = gtk.HBox(spacing=10)
			assert None != client.__unsaved_hbox
			
			client.__unsaved_spinner = gtk.Spinner()
			client.__unsaved_spinner.start()
			client.__unsaved_spinner.set_size_request(22,22)
			assert None != client.__unsaved_spinner
			
			client.__unsaved_image_save = gtk.image_new_from_stock(gtk.STOCK_FLOPPY,gtk.ICON_SIZE_BUTTON)
			client.__unsaved_image_save.set_size_request(22,22)
			assert None != client.__unsaved_image_save
			
			client.__unsaved_image_saved = gtk.image_new_from_stock(gtk.STOCK_APPLY,gtk.ICON_SIZE_BUTTON)
			client.__unsaved_image_saved.set_size_request(22,22)
			assert None != client.__unsaved_image_saved
			
			client.__unsaved_image_no_save = gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING,gtk.ICON_SIZE_BUTTON)
			client.__unsaved_image_no_save.set_size_request(22,22)
			assert None != client.__unsaved_image_no_save
			
			client.__unsaved_label = gtk.Label("NO LABEL SET")
			client.__unsaved_label.set_justify(gtk.JUSTIFY_LEFT)
			client.__unsaved_label.set_alignment(0,0.5)
			client.__unsaved_label.set_ellipsize(pango.ELLIPSIZE_END)
			client.__unsaved_label.set_line_wrap(False)
			client.__unsaved_label.set_selectable(True)
			assert None != client.__unsaved_label
			
			client.__unsaved_button_dontsave = gtk.Button("Don't Save")
			client.__unsaved_button_dontsave.connect("clicked",self.__cb_dont_save_specific_client,client)
			client.__unsaved_button_dontsave.set_size_request(100,-1)
			assert None != client.__unsaved_button_dontsave
			
			client.__unsaved_button_save = gtk.Button("Save")
			client.__unsaved_button_save.connect("clicked",self.__cb_save_specific_client,client)
			client.__unsaved_button_save.set_size_request(100,-1)
			assert None != client.__unsaved_button_save
			
			client.__unsaved_button_save_as = gtk.Button("Save As...")
			#client.__unsaved_button_save_as.connect("clicked",self.__cb_saveas_specific_client,client)
			client.__unsaved_button_save_as.set_size_request(100,-1)
			assert None != client.__unsaved_button_save_as
			
			client.__unsaved_button_cant_save = gtk.Button("Not Savable")
			client.__unsaved_button_cant_save.set_size_request(210,-1)
			client.__unsaved_button_cant_save.set_sensitive(False)
			assert None != client.__unsaved_button_cant_save
			
			client.__unsaved_hbox.pack_start(client.__unsaved_spinner,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_image_save,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_image_saved,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_image_no_save,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_label)
			client.__unsaved_hbox.pack_start(client.__unsaved_button_dontsave,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_button_save,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_button_save_as,expand=False)
			client.__unsaved_hbox.pack_start(client.__unsaved_button_cant_save,expand=False)
			self.vbox.pack_start(client.__unsaved_hbox,expand=False)
			
			description = client.GetDescription()
			assert None != description
			
			description = description.replace("&","&amp;")
			assert None != description
			
			client.__unsaved_label.set_markup(description)
			
			client.__unsaved_hbox.show()
			client.__unsaved_label.show()
			
			self.__update_client_status_visibility(client)
			
		self.button_save_all.connect("clicked",self.__cb_save_all)
		self.button_cancel.connect("clicked",self.__cb_cancel)
		self.button_dont_save.connect("clicked",self.__cb_dont_save_all)
	
	def __update_client_status_visibility(self,client,status=None):
		"""
		Manages the row for the specific client provided. Shows 
		and/or hides things based upon the status argument. If the
		status argument is not provided the client is queried for its
		current status.
		"""
		assert None != client
		assert None != client.__unsaved_hbox
		assert None != client.__unsaved_spinner
		assert None != client.__unsaved_image_save
		assert None != client.__unsaved_image_saved
		assert None != client.__unsaved_image_no_save
		assert None != client.__unsaved_label
		assert None != client.__unsaved_button_dontsave
		assert None != client.__unsaved_button_save
		assert None != client.__unsaved_button_save_as
		assert None != client.__unsaved_button_cant_save
		
		if status==None:
			status = client.GetSaveStatus()
		
		if status == Client.SAVE_STATUS_NOT_SAVED_NEED_PATH:
			client.__unsaved_image_save.show()
			client.__unsaved_spinner.hide()
			client.__unsaved_image_no_save.hide()
			client.__unsaved_button_dontsave.show()
			client.__unsaved_button_dontsave.set_sensitive(True)
			client.__unsaved_button_save_as.show()
			client.__unsaved_button_save_as.set_sensitive(True)
			client.__unsaved_button_cant_save.hide()
		elif status == Client.SAVE_STATUS_NOT_SAVED:
			client.__unsaved_image_save.show()
			client.__unsaved_spinner.hide()
			client.__unsaved_image_no_save.hide()
			client.__unsaved_button_dontsave.show()
			client.__unsaved_button_dontsave.set_sensitive(True)
			client.__unsaved_button_save.show()
			client.__unsaved_button_save.set_sensitive(True)
			client.__unsaved_button_cant_save.hide()
		elif status == Client.SAVE_STATUS_SAVING:
			client.__unsaved_spinner.show()
			client.__unsaved_image_no_save.hide()
			client.__unsaved_image_save.hide()
			client.__unsaved_button_dontsave.hide()
			client.__unsaved_button_save.hide()
			client.__unsaved_button_dontsave.set_sensitive(False)
			client.__unsaved_button_save.set_sensitive(False)
			client.__unsaved_button_save_as.set_sensitive(False)
			client.__unsaved_button_cant_save.hide()
		elif status == Client.SAVE_STATUS_SAVED:
			client.__unsaved_image_saved.show()
			client.__unsaved_spinner.hide()
			client.__unsaved_image_no_save.hide()
			client.__unsaved_image_save.hide()
			client.__unsaved_button_dontsave.hide()
			client.__unsaved_button_save.hide()
			client.__unsaved_button_cant_save.hide()
		elif status == Client.SAVE_STATUS_UNSAVABLE:
			client.__unsaved_image_no_save.show()
			client.__unsaved_button_cant_save.show()
	
	def show(self,parent):
		"""
		Show the unsaved changes handler. Requires a transient parent window. 
		This would normally be the host window. This handler will be modal 
		for the entire host widnow. 
		"""
		assert None != parent
		assert None != self.window
		assert None != self.__clients_denying_close
		
		self.window.set_modal(True)
		self.window.set_transient_for(parent)
		self.window.show()
		
		# Remove unsavable items from self.__clients_denying_close 
		# so they don't deny close. This has to be done after 
		# showing so that they are visable in the list none the less.
		new_arr = []
		for client in self.__clients_denying_close:
			status = client.GetSaveStatus()
			if status != Client.SAVE_STATUS_UNSAVABLE:
				new_arr.append(client)
		
		self.__clients_denying_close = new_arr
	
	def save_specific_client(self,client):
		"""
		Tell the provided <client> to save itself.
		"""
		assert None != client
		
		client.Save()
	
	def dont_save_specific_client(self,client):
		"""
		Mark <client> as not requiring saving. The user will still have 
		the option to manually choose to save it however by clicking save.
		"""
		assert None != client
		assert None != client.__unsaved_button_dontsave
		assert None != self.__clients_denying_close
		assert None != self.window
		assert None != self.delegate
		
		# Remove this client from the list so that it no longer denies close.
		if client in self.__clients_denying_close:
			self.__clients_denying_close.remove(client)
		
		client.__unsaved_button_dontsave.set_sensitive(False)
		
		# If there are no more tabs denying close, then return that everything has been "saved".
		if len(self.__clients_denying_close) == 0:
			self.window.hide()
			self.delegate.unsaved_changes_handler_cb(UnsavedChangesHandler.RETURN_SAVED_ALL)
	
	def save_all(self):
		"""
		Iterate though all clients currently denying close and save them.
		WARNING: If the user previously chose "Don't Save" that client WILL
		NOT BE SAVED!!!
		"""
		assert None != self.__clients_denying_close
		
		for client in self.__clients_denying_close:
			client.Save()
	
	def dont_save_all(self):
		"""
		Tell the delegate that everything has been saved. Of course 
		it hasn't, but that is what the user chose.
		"""
		assert None != self.window
		assert None != self.delegate
		
		self.window.hide()
		self.delegate.unsaved_changes_handler_cb(UnsavedChangesHandler.RETURN_SAVED_ALL)
	
	def cancel(self):
		"""
		Just close the unsaved changes window.
		"""
		assert None != self.window
		assert None != self.delegate
		
		self.window.hide()
		self.delegate.unsaved_changes_handler_cb(UnsavedChangesHandler.RETURN_CANCEL)
	
	#
	# BUTTON EVENT CALLBACKS
	#
	def __cb_save_specific_client(self,sender,client):
		assert None != client
		self.save_specific_client(client)
		
	def __cb_dont_save_specific_client(self,sender,client):
		assert None != client
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
	
	#
	# REMOTE NOTIFICATIONS
	#
	def update_client_status(self,client,status):
		"""
		Called to update the status. Used to update the display once the client has finished saving.
		"""
		assert None != client
		assert None != self.__clients_denying_close
		assert None != self.window
		assert None != self.delegate
		assert status in Client.SAVE_STATUS_RANGE
		
		self.__update_client_status_visibility(client,status)
		
		if status == Client.SAVE_STATUS_SAVED:
			self.__clients_denying_close.remove(client)
		
		#print "update_client_status",client,status
		if len(self.__clients_denying_close) == 0:
			self.window.hide()
			self.delegate.unsaved_changes_handler_cb(UnsavedChangesHandler.RETURN_SAVED_ALL)

	
UnsavedChangesHandler.RETURN_CANCEL = 0
UnsavedChangesHandler.RETURN_SAVED_ALL = 1
UnsavedChangesHandler.RETURN_RANGE = range(UnsavedChangesHandler.RETURN_CANCEL,UnsavedChangesHandler.RETURN_SAVED_ALL+1)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
