#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2020 neilk
#
# Based on the sample dimmer plugin

################################################################################
# Imports
################################################################################
import indigo
import requests
import json
import time
from datetime import datetime, timedelta, date
import pytz


################################################################################
# Globals
################################################################################


############################
# API Functions
#############################


def refresh_daily_solar_device(self, device):

	api_error = False
	resource_type = device.pluginProps['resource_ID']
	resource_ID = self.pluginPrefs[resource_type]
	url = "https://api.solcast.com.au/rooftop_sites/" + resource_ID + "/forecasts?format=json"

	payload = {}
	headers = {
		'Authorization': 'Basic '+device.pluginProps['API_key']
	}
	try:
		response = requests.get(url, headers=headers, data=payload)
		response.raise_for_status()
	except requests.exceptions.HTTPError as err:
		indigo.server.log("HTTP Error from Solcast API ")
		self.debugLog("Error is "+ str(err))
		api_error = True
	except Exception as err:
		indigo.server.log("Unknown/Other Error from Solcast API ")
		self.debugLog("Error is "+ str(err))
		api_error = True
	if api_error :
		indigo.server.log("Aborting update action for "+device.name)
		return
	response_json = response.json()

	device_states = []




	device_states.append({'key': 'raw_json', 'value': response_json})

	device.updateStatesOnServer(device_states)

	return





################################################################################
class Plugin(indigo.PluginBase):
	########################################
	# Class properties
	########################################

	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", False)
		self.deviceList = []

	########################################
	def deviceStartComm(self, device):
		self.debugLog("Starting device: " + device.name)
		device.stateListOrDisplayStateIdChanged()

		if device.id not in self.deviceList:
			self.update(device)
			self.deviceList.append(device.id)

	########################################
	def deviceStopComm(self, device):
		self.debugLog("Stopping device: " + device.name)
		if device.id in self.deviceList:
			self.deviceList.remove(device.id)

	########################################
	def runConcurrentThread(self):
		self.debugLog("Starting concurrent thread")
		try:
			pollingFreq = int(self.pluginPrefs['pollingFrequency'])
		except:
			pollingFreq = 15

		try:
			while True:

				self.sleep(1 * pollingFreq)
				for deviceId in self.deviceList:
					# call the update method with the device instance
					self.update(indigo.devices[deviceId])
		except self.StopThread:
			pass



	########################################
	def update(self, device):
		# # device.stateListOrDisplayStateIdChanged()
		local_day = datetime.datetime.now().date()
		#
		if str(local_day) != device.states["API_Today"]:
			device.setErrorStateOnServer('Forecast Expired')

		return

	########################################
	# UI Validate, Device Config
	########################################
	def validateDeviceConfigUi(self, valuesDict, typeId, device):

		return (True, valuesDict)

	########################################
	# UI Validate, Plugin Preferences
	########################################
	def validatePrefsConfigUi(self, valuesDict):

		return(True,valuesDict)




