import os, sys, time
import requests
from tornado import websocket, web, ioloop	

# Weather Underground API
apikey = '1473eef1c8584998'
features = ['conditions','astronomy']
pws_id = 'KNYASTOR5'
weather_url = 'http://api.wunderground.com/api/{}/{}/q/pws:{}.json'

def fetch_weather():
	current = time.strftime("%H:%M:%S")

	# Get the current conditions
	r = requests.get(weather_url.format(apikey, features[0], pws_id))
	temp = r.json()['current_observation']['temp_c']
	rh = r.json()['current_observation']['relative_humidity']
	
	# get sunset/sunrise times
	r = requests.get(weather_url.format(apikey, features[1], pws_id))	
	sunset = r.json()['moon_phase']['sunset']
	sunrise = r.json()['moon_phase']['sunrise']

	print "Current Time: {}".format(current)
	print "Current Conditions: {} - {}".format(temp, rh)
	print "Sunrise: {} - Sunset: {}".format(sunrise, sunset)

class Radio(object):
	'''Audio from Radio'''
	def __init__(self, station):
		self.status = 'running'
		self.station = station

		self._exec_command("service mpd start")
		self._exec_command("mpc clear")

		stream = self._fetch_stream(station)

		print "Playing stream: {}".format(stream)
		self._exec_command("mpc add {}".format(stream))		

	def play(self):
		'''Start Playing station'''
		self.status = 'playing'
		self._exec_command("mpc play")

	def stop(self):
		''' Stop playing the station'''
		self._exec_command("mpc stop")
		self.status = 'running'

	def _exec_command(self, cmd):
		result = ""
		p = os.popen(cmd)
		for line in p.readline().split('\n'):
			result = result + line
		
		return result	

	def _fetch_stream(self, url):
		#what we're looking for
		search='File1='
		r = requests.get(url)
		if r.status_code == 200:
			print r.text
			for line in r.text.splitlines():
				if search in line:
					return line.lstrip(search)	

class IndexHandler(web.RequestHandler):
	'''Handle requests on / '''
	def get(self):
		self.render("index.html")

class PlayHandler(web.RequestHandler):
	'''Handle requests on / '''
	@web.asynchronous
	def get(self):
		r = self.settings['radio']
		r.play()
		time.sleep(5)
		r.stop()
		self.finish()
		
class WeatherHandler(web.RequestHandler):
	@web.asynchronous
	def get(self):
		current = time.strftime("%H:%M:%S")

		# Get the current conditions
		r = requests.get(weather_url.format(apikey, features[0], pws_id))
		temp = r.json()['current_observation']['temp_c']
		rh = r.json()['current_observation']['relative_humidity']
		
		# get sunset/sunrise times
		r = requests.get(weather_url.format(apikey, features[1], pws_id))	
		sunset = r.json()['moon_phase']['sunset']
		sunrise = r.json()['moon_phase']['sunrise']

		print "Current Time: {}".format(current)
		print "Current Conditions: {} - {}".format(temp, rh)
		print "Sunrise: {} - Sunset: {}".format(sunrise, sunset)
		self.finish()
		
def main():
	stations = {
		'WNYC'      : 'http://www.wnyc.org/stream/wnyc-fm939/aac.pls',
	}	

	radio = Radio(stations['WNYC'])
	print "Status: {}".format(radio.status)

	settings = {
		"template_path": os.path.join(os.path.dirname(__file__), "templates"),
		"static_path": os.path.join(os.path.dirname(__file__), "static"),
		"radio" : radio,
		"debug" : True
	}

	app = web.Application(
		[
			(r'/', IndexHandler),
			(r'/play', PlayHandler),
			(r'/weather', WeatherHandler),
		], **settings
	)

	port = int(os.environ.get("PORT", 5000))
	print "Listening on port: %s"%(port)
	app.listen(port)
	ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()