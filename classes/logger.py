# logger.py
# developer: @eggins
#!/usr/bin/env python3

import time, sys

class Logger:

	# initalise base file naming structure for the logger
	def __init__(self):
		self.fileName = "log.txt"

	# logging function to print colours easier
	def log(self, msg="", color="", file="", shown=True, showtime=True):

		# check colour variable and set text colour when printing
		if color.lower() == "error":
			textColour = "\033[91m"
		elif color.lower() == "success":
			textColour = "\033[92m"
		elif color.lower() == "info":
			textColour = "\033[96m"
		elif color.lower() == "pink":
			textColour = "\033[95m"
		elif color.lower() == "yellow":
			textColour = "\033[93m"
		elif color.lower() == "lightpurple":
			textColour = "\033[94m"
		elif color.lower() == "lightgray":
			textColour = "\033[97m"
		else:
			textColour = ""

		# set current time for printing in H:M:S msg
		currenttime = time.strftime("%H:%M:%S")

		# check if msg is to be shown to terminal
		if shown:
			if showtime == False:
				sys.stdout.write("%s %s %s\n" % (textColour, str(msg), "\033[00m"))
			else:
				sys.stdout.write("[%s]%s %s %s\n" % (currenttime, textColour, str(msg), "\033[00m"))
			sys.stdout.flush()

		if file:
			if file == self.fileName:
				with open(self.fileName, "a") as f:
					if showtime == False:
						f.write("{}\n".format(msg))
					else:
						f.write("[{}] {}\n".format(currenttime, msg))
			else:
				with open(file, "a") as f:
					if showtime == False:
						f.write("{}\n".format(msg))
					else:
						f.write("[{}] {}\n".format(currenttime, msg))
