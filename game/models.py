from django.db import models

class User(models.Model):
	registration_number = models.IntegerField(primary_key=True)
	status = models.CharField(max_length=10)
	image = models.CharField(max_length=20)
        last_checkin = models.DateTimeField()

	def __str__(self):
		return "%s - %s  (%s)" % (self.registration_number, self.status, self.image)


class Images(models.Model):
	src = models.CharField(max_length=120)
	name = models.CharField(max_length=30)

	def __str__(self):
		return self.name

class Room(models.Model):
	room_id = models.IntegerField(primary_key=True)
	room_name = models.CharField(max_length=150)
	pirate_total = models.IntegerField(default=0)
	ninja_total = models.IntegerField(default=0)
	in_play = models.BooleanField(default=False)

	def __str__(self):
		return "%s (pirates: %s, ninjas: %s)" % (self.room_name, self.pirate_total, self.ninja_total)

	def get_ratio(self):
		if self.pirate_total < self.ninja_total*2:
                        return -2
		if self.pirate_total < self.ninja_total:
			return -1
		if self.pirate_total == self.ninja_total:
			return 0 
		if self.pirate_total > self.ninja_total:
			return 1
		if self.pirate_total*2 > self.ninja_total:
			return 2

class ActivityLog(models.Model):
	user = models.ForeignKey(User)
	action_type = models.CharField(max_length=30)
	action = models.CharField(max_length=250)
        timestamp = models.DateTimeField()   
