import sys,os
import gobject,pygtk,gtk,gio
gobject.threads_init ()

class UnsavedChanges(object):
	def __init__(self):
		super(UnsavedChanges, self).__init__()
