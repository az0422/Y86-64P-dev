# -*- encoding:UTF-8 -*-
import configparser
import os

# config reader
#
# 설정구성파일(.conf 또는 .config) 파일에서 설정 데이터를 읽어오는 모듈

class config():
	def __init__(self, path):
		# .conf or config
		self.configfile = path

		# extract file name
		temp = list(path)
		temp.reverse()

		temp = "".join(temp)

		ext, path = temp.split(".", maxsplit = 1)

		path = list(path)
		path.reverse()
		path = "".join(path)

		# .local file
		self.localconfig = path + ".local"
	
	# read
	def read(self):
		configdata = {}

		if os.path.isfile(self.localconfig):
			# read .local
			config = configparser.ConfigParser()
			config.read(self.localconfig, encoding = "UTF-8")

			config.sections()

			for section in list(config.keys()):
				configdata[section] = {}
				
				for key in config[section].keys():
					configdata[section][key] = config[section][key]
			
		else:
			# read .conf or .config
			config = configparser.ConfigParser()
			config.read(self.configfile, encoding = "UTF-8")
	
			config.sections()
	
			for section in list(config.keys()):
				configdata[section] = {}
	
				for key in config[section].keys():
					configdata[section][key] = config[section][key]
		
		return configdata
	