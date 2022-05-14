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
import datetime
import json


################################################################################
# Globals
################################################################################




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

	############################
	# Action Method
	#############################

	def refresh_daily_solar_device(self,pluginAction, device):

		api_error = False
		local_day = datetime.datetime.now().date()
		tomorrow = datetime.date.today() + datetime.timedelta(days=1)


		resource_ID = device.pluginProps['resource_ID']
		url = "https://api.solcast.com.au/rooftop_sites/" + resource_ID + "/forecasts?format=json"
		self.debugLog("API call is "+url)
		payload = {}
		headers = {
			'Authorization': 'Basic ' + device.pluginProps['API_key']
		}
		self.debugLog("Headers : "+str(headers))
		try:
			response = requests.get(url, headers=headers, data=payload)
			response.raise_for_status()
		except requests.exceptions.HTTPError as err:
			indigo.server.log("HTTP Error from Solcast API ")
			self.debugLog("Error is " + str(err))
			api_error = True
		except Exception as err:
			indigo.server.log("Unknown/Other Error from Solcast API ")
			self.debugLog("Error is " + str(err))
			api_error = True
		if api_error:
			indigo.server.log("Aborting update action for " + device.name)
			return
		forecast_json = response.json()
		device_states = []
		#forecast_json = json.loads(device.states['raw_json'])
		length = len(forecast_json['forecasts'])
		i = 0
		pv_estimate = 0
		pv_estimate10 = 10
		pv_estimate90 = 0
		while i < length:
			period_end = forecast_json['forecasts'][i]['period_end']
			if str(tomorrow) in period_end:
				pv_estimate = pv_estimate + forecast_json['forecasts'][i]['pv_estimate']
				pv_estimate10 = pv_estimate10 + forecast_json['forecasts'][i]['pv_estimate10']
				pv_estimate90 = pv_estimate90 + forecast_json['forecasts'][i]['pv_estimate90']

				self.debugLog(str(pv_estimate) + " " + str(pv_estimate10) + " " + str(pv_estimate90))
			i += 1
		# if str(local_day +datetime.timedelta(days=1)) in forecast_json[forecasts]['period_end']:
		device_states.append({'key': 'solar_forecast','value': pv_estimate })
		device_states.append({'key': 'solar_forecast10','value': pv_estimate10 })
		device_states.append({'key': 'solar_forecast90','value': pv_estimate90 })

		device_states.append({'key': 'raw_json', 'value': json.dumps(forecast_json)})
		device_states.append({'key': 'API_Today', 'value': str(local_day)})
		device.updateStatesOnServer(device_states)

		return






