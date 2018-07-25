import os
import datetime
import logging
from crontab import CronTab

class Scheduler(object):
	def __init__(self):
		self.cron = CronTab(user=True)

	def schedule_alarm(self, hour, minute):

		# -- Remove any existing alarms
		self.cron.remove_all(comment="alarm")
		
		# -- Create new job
		current_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
		
		job = self.cron.new(command='python '+current_dir+'/npr_radio.py', comment="alarm")

		# -- Finally, add the new job to the crontab
		job.minute.on(minute)
		job.hour.on(hour)

		self.cron.write()

	def get_current_alarms(self):
		jobs = self.cron.find_comment("alarm")

		if not jobs:
			return False

		alarms = []
		for job in jobs:
			alarms.append("%s:%s" % (str(job.hour).zfill(2), str(job.minute).zfill(2)))

		return alarms

	def clear_alarm(self):
		logging.warning('clear_alarm')
		# -- Remove any existing alarms
		self.cron.remove_all(comment="alarm")
		self.cron.write()