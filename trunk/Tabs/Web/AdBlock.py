import sys,os
import gobject,pygtk,gtk

#file:///usr/share/ude/components/spacer.gif
class AdBlock(object):
	__adblock_rules_uri = []
	__adblock_rules_uri_exceptions = []
	__adblock_rules_element = []
	__adblock_rules_element_exceptions = []
	
	
	def __init__(self):
		super(AdBlock, self).__init__()
	
	def add_file(self,path):
		f = open(path, 'r')
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
	
	def block(self,uri):
		for rule in self.__adblock_rules_uri:
			if self.uri_matches_rule(uri,rule):
				return True
		return False
	
	def uri_matches_rule(self,uri,rule):
		
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
