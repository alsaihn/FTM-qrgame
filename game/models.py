from django.db import models
import datetime

class User(models.Model):
	registration_number = models.IntegerField(primary_key=True)
	status = models.CharField(max_length=10)
	image = models.CharField(max_length=20)
	last_checkin = models.DateTimeField()

	def __str__(self):
		return "%s - %s  (%s)" % (self.registration_number, self.status, self.image)
	
	def loginCount(self):
            return self.activitylog_set.filter(action_type="Checkin").count()


class Images(models.Model):
	src = models.CharField(max_length=120)
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name
		
		
class Group(models.Model):
	group_id = models.IntegerField(primary_key=True)
	group_name = models.CharField(max_length=100)
	group_total = models.IntegerField(default=0)
	
	def __str__(self):
		return self.group_name
		
		
class QrCode(models.Model):
	qr_id = models.IntegerField(primary_key=True)
	value = models.IntegerField(default=1)
	use_count = models.IntegerField(default=1)
	group = models.ForeignKey(Group)
	

class Panel(models.Model):
	panel_id = models.IntegerField(primary_key=True)
	panel_name = models.CharField(max_length=150)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	qr = models.ForeignKey(QrCode)

	def __str__(self):
		return self.room_name

	def in_play(self):
		now = datetime.datetime.now()
		return (self.end_time < now and now < self.start_time)


class ActivityLog(models.Model):
	user = models.ForeignKey(User)
	action_type = models.CharField(max_length=30)
	action = models.CharField(max_length=250)
	timestamp = models.DateTimeField()   

