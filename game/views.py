import random
import urllib2
import json
import pytz
import hashlib
from datetime import datetime, date
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms.extras.widgets import SelectDateWidget

from game.models import *

# The number of seconds a user has to wait between checkins
USER_WAIT_TIME = 5 * 60



def index(request):
    context = {}
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
# Group utilities

def getGroupData(id):
    if Group.objects.filter(group_id=id).exists():
		return Group.objects.get(group_id=id)
    return None
    
def getQrData(id):
    if QrCode.objects.filter(qr_id=id).exists():
		return QrCode.objects.get(qr_id=id)
    return None
    


#########################
# Group endpoints


def grouplist(request):
    group_list = Group.objects.all()
    context = {'group_list': group_list}
    return render(request, 'game/roomlist.html', context)
    
def groupdata(request, group_id):
    group_data = getGroupData(group_id)
    if not group_data:
        return HttpResponseRedirect('/group/notfound/')
    
    user_list = User.objects.filter(status=group_data.group_name.lower())
    context = {'group': group_data, 'user_list': user_list}
    return render(request, 'game/groupdata.html', context)
    
def group_not_found(request):
    return render(request, 'game/notinplay.html', {})


#########################
# Qr endpoints

def qr_not_found(request):
    return render(request, 'game/notinplay.html', {})

def qr_wait(request, user_id):
    user_data = getUserData(user_id)
    wait_time, seconds = divmod(USER_WAIT_TIME, 60)
    return render(request, 'game/wait.html', {'wait_time': wait_time, 'user_time': user_data.last_checkin})

def qrcheckin(request, qr_id):
	qr_data = getQrData(qr_id)
	if not qr_data:
		return HttpResponseRedirect('/qr/notfound/')

	if request.method == 'POST':
		form = CheckinForm(request.POST)
		if form.is_valid():

			user_data = getUserData(form.cleaned_data["badge_number"])
			if not user_data:
				return HttpResponseRedirect('/register/%s/?next=/qr/%s/checkin/%s/' % (form.cleaned_data["badge_number"], qr_id, form.cleaned_data["badge_number"]))
	    
			return HttpResponseRedirect('/qr/%s/checkin/%s/' % (qr_id, user_data.registration_number))
	else:
		form = CheckinForm()

	context = {'qr': qr_data, 'form': form}
	return render(request, 'game/roomcheckin.html', context)

def qrcheckin_validate(request, room_id, user_id):
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
    

def qrcheckin_done(request, room_id):
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

	return cleaned_data	
	

class CheckinForm(forms.Form):
    badge_number = forms.IntegerField()


class ValidationForm(forms.Form):
    image = forms.CharField(widget=forms.HiddenInput())
