import sys,os
import gobject,pygtk,gtk,gio
gobject.threads_init ()

class UnsavedChangesHandler(object):
	def __init__(self):
		super(UnsavedChangesHandler, self).__init__()
