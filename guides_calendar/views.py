from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
# from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import JsonResponse
import calendar
import json
import datetime


def guide_calendar(request, guide_username=None):
    page = "calendar"
    user = request.user
    if guide_username:
        guide = GuideProfile.objects.get(user__username=guide_username)
    else:
        try:
            GuideProfile.objects.get(user=user)
            if request.session.get("current_role") != "guide":
                messages.error(request, _('Please switch to a guide profile!'))
                return HttpResponseRedirect(reverse("home"))
        except:#no guide profile
            messages.error(request, _('Please sign up as a guide!'))
            return HttpResponseRedirect(reverse("home"))

    guide_calendar_items = CalendarItemGuide.objects.filter(guide__user=user).exclude(calendar_item__isnull=True)
    guide_calendar_items_dict=dict()
    for item in guide_calendar_items:
        try:
            guide_calendar_items_dict[item.calendar_item.id] = item.status.name
        except:
            pass

    if not request.GET.get("date_start") or not request.GET.get("date_end"):
        date_start = datetime.datetime.today()
        timedelta_days_nmb = 9 #10 days range by default
        date_end = date_start+datetime.timedelta(days=timedelta_days_nmb)
    else:
        date_start = datetime.datetime.strptime(request.GET.get("date_start"), '%m.%d.%Y')
        date_end = datetime.datetime.strptime(request.GET.get("date_end"), '%m.%d.%Y')

    calendar_items = list(CalendarItem.objects.filter(date__gte=date_start, date__lte=date_end).values())

    for calendar_item in calendar_items:
        if calendar_item["id"] in guide_calendar_items_dict:
            calendar_item["status"] = guide_calendar_items_dict[calendar_item["id"]]
    hours_list = range(0, 24)
    return render(request, 'guides_calendar/calendar.html', locals())


@login_required()
def updating_calendar(request):
    print("updating_calendar")
    response_data = dict()
    user = request.user
    if request.POST:
        data = request.POST
        print(data)
        calendar_item_id = data.get("calendar_item_id")
        new_status = data.get("new_status")
        new_status = CalendarItemStatus.objects.get(name=new_status)

        current_role = request.session.get("current_role")
        if current_role != "guide" and new_status!="booked":
            response_data["result"] = _("You have no permissions for this action!")
        elif current_role == "guide":
            if new_status == "booked":
                response_data["result"] = _("You have no permission for booking")
            else:
                guide = GuideProfile.objects.get(user=user)
                CalendarItemGuide.objects.update_or_create(calendar_item_id=calendar_item_id, guide=guide,
                                                           defaults={"status": new_status})
                response_data["result"] = _("Time slots were successfully updated!")
    return JsonResponse(response_data)


def weekly_schedule(request):
    print(calendar.day_name[0])
    page = "calendar"
    user = request.user
    try:
        guide = GuideProfile.objects.get(user=user)
        if request.session.get("current_role") != "guide":
            messages.error(request, _('Please switch to a guide profile!'))
            return HttpResponseRedirect(reverse("home"))
    except:#no guide profile
        messages.error(request, _('Please sign up as a guide!'))
        return HttpResponseRedirect(reverse("home"))

    hours_list = range(0, 24)
    weekdays = list(calendar.day_name)
    schedule_template = ScheduleTemplateItem.objects.filter(guide=guide, status_id=2)#available
    available_calendar_items = ["%s-%s" % (item.day, item.hour) for item in schedule_template]
    available_calendar_items_json = json.dumps(available_calendar_items)

    if request.POST:
        print("POSTTTTTT")
        current_dt = datetime.datetime.now().date()
        calendar_items = CalendarItem.objects.filter(date__gte=current_dt)

        #applying of new available items
        for calendar_item in calendar_items:
            weekday_nmb = calendar_item.date.weekday()
            hour = calendar_item.time_from.hour
            day_hour = "%s-%s" % (weekday_nmb, hour)
            if day_hour in available_calendar_items:
                guide = GuideProfile.objects.get(user=user)

                #get or update functionality, but without applying for booked items
                try:
                    calendar_item_guide = CalendarItemGuide.objects.get(calendar_item_id=calendar_item.id, guide=guide)
                    if calendar_item_guide.status_id == 3: #unavailable
                        calendar_item_guide.status_id = 2 #available
                        calendar_item_guide.save(force_update=True)
                except:
                    CalendarItemGuide.objects.create(calendar_item_id=calendar_item.id, guide=guide, status_id=2)

        #changing status for previously available items, which now are converted to unavailable
        calendar_items_guide = CalendarItemGuide.objects.filter(guide=guide, status_id=2) #available
        print(calendar_items_guide)
        for calendar_item_guide in calendar_items_guide:
            weekday_nmb = calendar_item_guide.calendar_item.date.weekday()
            hour = calendar_item_guide.calendar_item.time_from.hour
            day_hour = "%s-%s" % (weekday_nmb, hour)

            if not day_hour in available_calendar_items:
                print("not in")
                calendar_item_guide.status_id = 3#unavailable
                calendar_item_guide.save(force_update=True)
        messages.success(request, _('Applied!'))
    return render(request, 'guides_calendar/weekly_schedule.html', locals())


def updating_schedule_template(request):
    print("updating_schedule_template")
    response_data = dict()
    user = request.user
    if request.POST:
        data = request.POST
        print(data)

        #days-hour splitting
        day_hour = data.get("day_hour").split("-")
        day = day_hour[0]
        hour = day_hour[1]

        new_status = data.get("new_status")
        new_status = CalendarItemStatus.objects.get(name=new_status)
        current_role = request.session.get("current_role")
        if current_role != "guide":
            response_data["result"] = _("You have no permissions for this action!")
        elif current_role == "guide":
            guide = GuideProfile.objects.get(user=user)
            ScheduleTemplateItem.objects.update_or_create(guide=guide, day=day, hour=hour,
                                                       defaults={"status": new_status})
            response_data["result"] = _("Time slots were successfully updated!")
    return JsonResponse(response_data)


def available_date_timeslots(request):
    response_data = dict()
    if request.POST:
        data = request.POST
        guide_id = data.get("guide_id")
        calendar_date = datetime.datetime.strptime(data.get("booking_date"), '%m.%d.%Y')
        available_time_slots = list(CalendarItemGuide.objects.filter(guide_id=guide_id, status_id=2, calendar_item__date=calendar_date)\
                                    .values("calendar_item_id", "calendar_item__time_from", "calendar_item__time_to"))
        response_data["available_time_slots"] = available_time_slots
    return JsonResponse(response_data)