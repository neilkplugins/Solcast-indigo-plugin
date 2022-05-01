# Solcast-indigo-plugin
An Indigo Plugin for the Solcast Solar forecasting API

This is a very basic Indigo plugin that collects forecast solar generation data from www.solcast.au for a predefined rooftop solar generation array and it return the total forecast energy generation for that site tomorrow.

This version has very limited functionality and has no configuration validation etc.

Usage:

Create an account on www.solcast.au which is free for private residential solar generation sites (rooftop sites)

Add your rooftop site providing the location (lat/long) and the details about the array (direction, roof pitch, etc)

This will generate a resource_ID for your location, and you will also need your API key (from the account settings)

In the plugin:

Create a Solcast device, type "PV Solar Generation Forecast"

In the device settings, add the Resource_ID for your site and your API Key (in this version these are not validated or tested so paste carefully)

The device does not automatically update other than to "expire" the forecast when it is out of date as a free Solcast account has a very limited number of daily API calls (20 per day)

To refresh the device with the forecast for tomorrow you need to create an action group to run the action "Refresh Solar PV Forecast (Solcast Controls)"

This will make the API call and aggegrate the forecast for tomorrow and populate the device state with the total solar_forecast energy for the day in kW

It does the same for the solar_forecast10 and solar_forecast90 device states that are daily totals for the 10th and 90th percentile forecasts. See the solcast site for more details
