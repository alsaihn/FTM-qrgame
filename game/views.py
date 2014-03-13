import random
import urllib2
import json
import pytz
import hashlib
from datetime import datetime, date
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms.extras.widgets import SelectDateWidget

from game.models import User, Room, Images, ActivityLog

# The number of seconds a user has to wait between checkins
USER_WAIT_TIME = 5 * 60

#[[ne], [sw]]  lat, lng
room_bounds = {
    'Ballroom': [[146.0,136.25],[22.25,136.25],[22.25,110.25],[146.0,110.0],[146.0,136.25]],
    "Dealer's Den A": [[96.25,136.0],[71.5,136.0],[71.5,110.25],[96.25,110.25],[96.25,136.0]],
    "Dealer's Den B": [[103,154.5],[80.5,154.5],[80.5,137.25],[103.0,137.25],[103,154.5]],
    "Artists' Alley": [[106,109.5],[21.25,109.5],[21.25,95.75],[106,95.75],[106,109.5]],
    'Registration': [[103.5,117.25],[97.0,117.25],[97.0,109.5],[103.5,109.5],[103.5,117.25]],
    'Portrait Studio': [[206.25,114.0],[193.5,114.0],[193.5,108.5],[206.25,108.5],[206.25,114.0]],
    'The Zoo': [[169.5,132.75],[148.75,132.75],[148.75,122.5],[169.5,122.5],[169.5,132.75]],
    'Video Games': [[205.75,103.5],[193.0,103.5],[193.0,95.5],[205.75,95.5],[205.75,103.5]],
    'Board Games': [[206.0,89.0],[193.0,89.0],[193.0,73.75],[206.0,73.75],[206.0,89.0]],
    'Panel 1': [[65.25,86.0],[52.5,86.0],[52.5,68.5],[65.25,68.5],[65.25,86.0]],
    'Medical': [[63.25,60.0],[55.75,60.0],[55.75,49.25],[63.25,49.25],[63.25,60.0]],
    'INTERNAL -- Operations': [[71.5,60.0],[63.75,60.0],[63.75,49.25],[71.5,49.25],[71.5,60.0]],
    'Panel 2': [[78.5,60.0],[],[71.75,49.25],[78.5,49.25],[78.5,60.0]],
    'Panel 3': [[86.0,60.0],[],[78.5,49.25],[86.0,49.25],[86.0,60.0]],
    'Panel 4': [[93.0,62.25],[],[85.75,49.25],[93.0,49.25],[93.0,62.25]],
    'The Headless Lounge': [[100.75,60.25],[93.0,60.25],[93.0,49.25],[100.75,49.25],[100.75,60.25]],
    'Hospitality Suite': [[198,68.25],[192.25,68.25],[192.25,57.5],[198,57.5],[198,68.25]]
}

def createGeoJson():
    geojson = {"type": "FeatureCollection",
        "features": []
    }
    room_list = Room.objects.all()
    for room in room_list:
        if room.room_name not in room_bounds:
            break
	coords = room_bounds[room.room_name]
        feature = {"type": "Feature",
		   "geometry": {
		      "type": "Polygon", "coordinates": [coords]
		    },
		    "properties": {"value": room.get_ratio()}
                  }
	geojson["features"].append(feature)

    return geojson

def index(request):
    room_list = Room.objects.all()
    geoJson = createGeoJson()
    context = {'room_list': room_list, 'geoJson': geoJson}
    return render(request, 'game/index.html', context)


#########################
# Log utilities

def logRegistration(user):
    saveLog(user, "Registration", "Success")

def logCheckin(user, roomid):
    saveLog(user, "Checkin", roomid)

def saveLog(user, action_type, action):    
    log_entry = ActivityLog()
    log_entry.user = user
    log_entry.action_type = action_type
    log_entry.action = action
    log_entry.timestamp = datetime.now()
    log_entry.save()

def get_statistics(request):
    users = User.objects.all()
    context = {'user_list': users}
    return render(request, 'game/statistics.html', context)


#########################
# User utilities

def getUserData(id):
    if User.objects.filter(registration_number=id).exists():
	return User.objects.get(registration_number=id)
    return None


def setLastCheckin(user, timestamp):
    user.last_checkin = timestamp
    user.save()

#########################
# User endpoints

def register_not_found(request):
    return render(request, 'game/notregistered.html', {})

def register(request, badge_number):
    response = urllib2.urlopen('https://reg.furthemore.org/Affiliation.ashx?id=' + badge_number + '&hex=true')
    data = json.load(response) 

    if data['FurTheMore']['Badge']['Affiliation'].lower() == 'none':
        return HttpResponseRedirect('/register/notfound/')

    if request.method == 'POST':
	form = RegisterForm(request.POST)
	form.inhash = data['FurTheMore']['Badge']['Birthdate']
        form.badge_number = badge_number
	if form.is_valid():

	    #todo: check birthdate
	    user = User()
	    user.registration_number = badge_number
            user.status = data['FurTheMore']['Badge']['Affiliation'].lower()
            user.image = form.cleaned_data['image']

            user.save()
            logRegistration(user)

            next = request.GET.get("next", "")

	    if next:
	            return HttpResponseRedirect(next)
            return HttpResponseRedirect('/')
    else:		
        form = RegisterForm()
    form_images = Images.objects.order_by("?")

    context = {'form': form, 'badge_number': badge_number, 'images': form_images}
    return render(request, 'game/register.html', context)


#########################
# Room utilities

def getRoomData(id):
    if Room.objects.filter(room_id=id).exists():
	return Room.objects.get(room_id=id)
    return None


#########################
# Room endpoints


def roomlist(request):
    room_list = Room.objects.all()
    context = {'room_list': room_list}
    return render(request, 'game/roomlist.html', context)
    
def roomdata(request, room_id):
    room_data = getRoomData(room_id)
    if not room_data:
        return HttpResponseRedirect('/room/notfound/')
    
    context = {'room': room_data}
    return render(request, 'game/roomdata.html', context)
    

def room_not_found(request):
    return render(request, 'game/notinplay.html', {})

def room_wait(request, user_id):
    user_data = getUserData(user_id)
    wait_time, seconds = divmod(USER_WAIT_TIME, 60)
    return render(request, 'game/wait.html', {'wait_time': wait_time, 'user_time': user_data.last_checkin})

def roomcheckin(request, room_id):
    room_data = getRoomData(room_id)
    if not room_data:
        return HttpResponseRedirect('/room/notfound/')
    
    if not room_data.in_play:
        return HttpResponseRedirect('/room/notfound/')

    if request.method == 'POST':
	form = CheckinForm(request.POST)
        if form.is_valid():

            user_data = getUserData(form.cleaned_data["badge_number"])
            if not user_data:
		return HttpResponseRedirect('/register/%s/?next=/room/%s/checkin/%s/' % (form.cleaned_data["badge_number"], room_id, form.cleaned_data["badge_number"]))
	    
            return HttpResponseRedirect('/room/%s/checkin/%s/' % (room_id, user_data.registration_number))
    else:
	form = CheckinForm()

    context = {'room': room_data, 'form': form}
    return render(request, 'game/roomcheckin.html', context)

def roomcheckin_validate(request, room_id, user_id):
    room_data = getRoomData(room_id)
    if not room_data:
        return HttpResponseRedirect('/room/notfound/')

    user_data = getUserData(user_id)
    if not user_data:
	return HttpResponseRedirect('/register/%s/?next=/room/%s/checkin/%s/' % (user_id, room_id, user_id))

    if request.method == 'POST':
	form = ValidationForm(request.POST)
        if form.is_valid():

	    if form.cleaned_data["image"] == user_data.image:        

                if user_data.last_checkin:
                    elapsed_time = datetime.now(pytz.timezone('US/Eastern')) - user_data.last_checkin
                    if elapsed_time.total_seconds() < USER_WAIT_TIME:
                        return HttpResponseRedirect('/room/wait/%s/' % user_id)


                if user_data.status == "ninja":
                    room_data.ninja_total = room_data.ninja_total + 1
                else:
                    room_data.pirate_total = room_data.pirate_total + 1

                room_data.save()
		timestamp = datetime.now()
		setLastCheckin(user_data, timestamp)
		logCheckin(user_data, room_id)

                return HttpResponseRedirect('/room/%s/checkin/done/' % room_id)
	    else:
		return HttpResponseRedirect('/room/%s/checkin/' % room_id)
    else:
	form = ValidationForm()

    user_image = Images.objects.get(name=user_data.image)
    images = list(Images.objects.exclude(name=user_data.image).order_by("?"))[:4]
    random_idx = random.randint(0,4)
    images.insert(random_idx, user_image)

    context = {'room': room_data, 'user_id': user_id, 'images': images, 'form': form}
    return render(request, 'game/roomcheckin_validate.html', context)
    

def roomcheckin_done(request, room_id):
    room_data = getRoomData(room_id)
    if not room_data:
        return HttpResponseRedirect('/room/notfound/')

    context = {'room': room_data}
    return render(request, 'game/roomcheckindone.html', context)
    

#########################
# Forms  

from django import forms

years_list = [x for x in range(1920, date.today().year + 1)]
years_list.reverse()
BIRTH_YEARS = tuple(years_list)

class RegisterForm(forms.Form):
    birthdate = forms.DateField(widget=SelectDateWidget(years=BIRTH_YEARS))
    image = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        salt_hash = hashlib.md5()
        salt_hash.update(self.badge_number)
        salt_hash.update("45F0BD1EFDCB4C69951102912B483123")

        birthdate = datetime.strftime(cleaned_data.get("birthdate"), '%Y%m%d')
        pass_hash = hashlib.md5()
        pass_hash.update(birthdate)
        pass_hash.update(salt_hash.digest())
        hash = pass_hash.hexdigest()

	#if self.inhash != hash:
	#    raise forms.ValidationError("Birthdate must match your registration records. %s - %s ,  %s" % (self.inhash, hash, birthdate))

	return cleaned_data	
	

class CheckinForm(forms.Form):
    badge_number = forms.IntegerField()


class ValidationForm(forms.Form):
    image = forms.CharField(widget=forms.HiddenInput())
