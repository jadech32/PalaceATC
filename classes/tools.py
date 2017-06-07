# developer: @eggins
#!/usr/bin/env python3

import sys, os, os.path, json, requests, colorama, cfscrape


sys.path.append('../')

from classes.logger import Logger
log = Logger().log

class Tools:
	def __init__(self):
		self.tools = "tools"

	def load(self, filePath):
		if not os.path.exists(filePath):
			log("%s - file not found!" % filePath, "error")
			exit()
		else:
			while True:
				with open(filePath) as jsonObj:
					jsonFile = json.load(jsonObj)
					if jsonFile:
						#log("%s has been loaded." % (filePath), "info")
						return jsonFile
						break
					else:
						log("Fatal error while trying to load %s file." % filePath, "error")
						exit()
