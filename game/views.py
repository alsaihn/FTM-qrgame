import random
import urllib2
import json
import pytz
from datetime import datetime
from django.http import HttpResponseRedirect
from django.shortcuts import render

from game.models import User, Room, Images

# The number of seconds a user has to wait between checkins
USER_WAIT_TIME = 5 * 60

def index(request):
    room_list = Room.objects.all()
    context = {'room_list': room_list}
    return render(request, 'game/index.html', context)

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
    response = urllib2.urlopen('https://reg.furthemore.org/Affiliation.ashx?id=' + badge_number)
    data = json.load(response) 

    if 'Error' in data['FurTheMore']:
        return HttpResponseRedirect('/register/notfound/')

    if request.method == 'POST':
	form = RegisterForm(request.POST)
	if form.is_valid():

	    #todo: check birthdate
	    user = User()
	    user.registration_number = badge_number
            user.status = data['FurTheMore']['Badge']['Affiliation'].lower()
            user.image = form.cleaned_data['image']

            user.save()

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

class RegisterForm(forms.Form):
    birthdate = forms.DateField()
    image = forms.CharField(widget=forms.HiddenInput())

class CheckinForm(forms.Form):
    badge_number = forms.IntegerField()


class ValidationForm(forms.Form):
    image = forms.CharField(widget=forms.HiddenInput())
