"""
Author: Adam Szablya
Date: November 26, 2018
Description: utility to schedule long process python scripts to follow up on events in the webapp
"""
# from emails.models import DripMailer, DripType, EmailMessage, EmailMessageType
from users.models import GeneralProfile
from guides.models import GuideProfile
from tourists.models import TouristProfile
from tours.models import ScheduledTour
from orders.models import Order, OrderStatus
from chats.models import Chat, ChatMessage
from utils.sending_emails import SendingEmail


import time
import datetime


"""utility functions"""


def notify(subject, message, user, email):
    sending = SendingEmail(None)
    sending.from_email = 'concierge@tourzan.com'
    sending.sending_email(to_user=user, to_email=email, subject=subject, message=message)


"""general and guide section"""


def schedules_about_to_expire():
    """one week before, reminder if already expired, run on cron"""
    #TODO: make this more robust and fire once and only once
    schedule = ScheduledTour.objects.all()
    for s in schedule:
        last_tour_date = s.tour.scheduledtour_set.filter(is_active=True).order_by("dt").reverse()[0].dt
        d = datetime.datetime.strptime(last_tour_date, "%Y-%m-%d")
        week = datetime.datetime.now()
        delta = d - week
        if delta.days == 7 or delta.days == 0:
            msg = 'Hello this is your <a href={}>Tourzan.com<a/> concierge service to remind you that your tour named '\
                  '{} has a schedule is expiring soon or has already expired. You can update your tours schedule '\
                  'by editing the schedule in your tours page from the guide profile on tourzan.com. ' \
                  'If you let the schedule expire we will automatically convert them to private tours where a ' \
                  'customer would need to request a time that works for both of you. '\
                  '<b\><b\>Thank you for your time<b\>The Tourzan.com team'\
                .format('https://www.tourzan.com', s.tour.name)
            notify(subject='Reminder that your scheduled tour is expiring', message=msg, user=s.tour.guide.user,
                   email=s.tour.guide.user.email)


def pending_order(order, timer=14400, day=0):
    """four horus and a one and two day follow up"""
    msg = 'Hello this is your %s concierge service to remind you that you have a pending order with %s. ' \
          'you can check in on your customer by going to your order ' \
          '<a href="%s/settings/guide/orders/?uuid=%s>by cliking here.</a>' \
          '<b\><b\>Thank you for your time<b\>The Tourzan.com team' % ('https://www.tourzan.com', order.tourist.user.generalprofile.get_name(), 'https://www.tourzan.com', order.uuid)
    if order.status_id == 1:
        time.sleep(timer)
        order = Order.objects.get(id=order.id)
        if order.status_id == 1:
            notify(subject='Reminder of your pending order with {}'.format(order.tourist.user.generalprofile.get_name()),
                   message=msg, user=order.guide.user, email=order.guide.user.email)
            day += 1
            timer = 86400
            if day <= 2:
                pending_order(order, timer, day)


def verified_reminder(timer=2592000):
    """once per month"""
    time.sleep(timer)
    not_verified = GeneralProfile.objects.filter(is_verified=False, user__guideprofile__isnull=False)
    for guide in not_verified:
        msg = 'Hello this is your <a href=%s>Tourzan.com<a/> concierge service to remind you that your account ' \
              'remains unverified %s. you can fix this by going to your guide profile and uploading the requisite ' \
              'documents under the Identity Verification tab on the left hand panel of your general profile settings' \
              'or <a href="%s/en/identity_verification/ID_uploading/">by cliking here.</a> if you need help resetting '\
              'your verification please reach out to us at contactus@tourzan.com' \
              '<b\><b\>Thank you for your time<b\>The Tourzan.com team' % (
              'https://www.tourzan.com', guide.user.generalprofile.get_name(), 'https://www.tourzan.com')
        notify(subject='Reminder to verify your identity on tourzan.com', message=msg, user=guide.userr,
               email=guide.user.email)


def bank_account_reminder(order):
    """once after a booking and 4 days after scheduled date"""
    msg = 'Hello this is your <a href=%s>Tourzan.com<a/> concierge service to remind you to keep your ' \
          'payout method up to date in order to ensure a promp and on-time payout. As a reminder we payout on the ' \
          '1st and the 15th of the month following a five day grace period. If you require setting up or editing ' \
          'your payout preference please <a href=%s>click here to update it.' \
          '<br/>' \
          'please reach out to us at contactus@tourzan.com if you have any questions.' \
          '<b\><b\>Thank you for your time<b\>The Tourzan.com team' % ('https://www.tourzan.com',
                                                                       'https://www.tourzan.com/en/guide/payouts/')
    if order.status_id == 4:
        notify(subject='Reminder to keep your payout preferences updated', message=msg, user=order.guide.userr,
               email=order.guide.user.email)
    elif order.status_id == 5:
        today = datetime.datetime.now().timestamp()
        booked = datetime.datetime(order.date_booked_for).timestamp()
        delta = booked + 345600 - today
        time.sleep(delta)
        notify(subject='Reminder to keep your payout preferences updated', message=msg, user=order.guide.userr,
               email=order.guide.user.email)


def new_messages():
    """4 hours and 1 day"""
    return True


def incomplete_profile():
    """once one week post profile setup"""
    return True


"""Tourist section"""


def upcoming_trip():
    """one week and two days in advance to remind both the guide and the tourist"""
    today = datetime.datetime.now()
    orders = Order.objects.filter(status__in=[2, 5, 9], date_booked_for__gt=today)
    for order in orders:
        d = datetime.datetime.strptime(order.date_booked_for, "%Y-%m-%d")
        delta = d - today
        if delta.days == 7:
            msg = 'Hello %s this is your <a href=%s>Tourzan.com<a/> concierge service to remind you of your upcoming ' \
                  'reservation with %s in the next 7 days please make sure you have make all the proper arrangements ' \
                  'with your Tourzan guide <b\><b\>Thank you for your time<b\>The Tourzan.com team' \
                  % (order.tourist.user.generalprofile.get_name(), 'https://www.tourzan.com', order.guide.name)
            notify(subject='Reminder of your upcoming tour', message=msg, user=order.tourist.user,
                   email=order.tourist.user.email)
            msg = 'Hello %s this is your <a href=%s>Tourzan.com<a/> concierge service to remind you of your upcoming ' \
                  'booking with %s in the next 7 days please make sure you have make all the proper arrangements ' \
                  'with your customer <b\><b\>Thank you for your time<b\>The Tourzan.com team' \
                  % (order.guide.user.generalprofile.get_name(), 'https://www.tourzan.com', order.tourist.user.generalprofile.get_name())
            notify(subject='Reminder of your upcoming booking', message=msg, user=order.tourist.user,
                   email=order.tourist.user.email)
        elif delta.days == 14:
            msg = 'Hello %s this is your <a href=%s>Tourzan.com<a/> concierge service to remind you of your upcoming ' \
                  'reservation with %s in the next 14 days please make sure you have make all the proper arrangements ' \
                  'with your Tourzan guide <b\><b\>Thank you for your time<b\>The Tourzan.com team' \
                  % (order.tourist.user.generalprofile.get_name(), 'https://www.tourzan.com', order.guide.name)
            notify(subject='Reminder of your upcoming tour', message=msg, user=order.tourist.user,
                   email=order.tourist.user.email)
            msg = 'Hello %s this is your <a href=%s>Tourzan.com<a/> concierge service to remind you of your upcoming ' \
                  'booking with %s in the next 14 days please make sure you have make all the proper arrangements ' \
                  'with your customer <b\><b\>Thank you for your time<b\>The Tourzan.com team' \
                  % (order.guide.user.generalprofile.get_name(), 'https://www.tourzan.com', order.tourist.user.generalprofile.get_name())
            notify(subject='Reminder of your upcoming booking', message=msg, user=order.tourist.user,
                   email=order.tourist.user.email)


def guide_reply(chat):
    """once one day later"""


    return True


def non_payment(order, timer=14400, day=0):
    """ agreed state
        4 hours, 1 day, 2 days.
    """
    msg = 'Hello this is your <a href=%s>Tourzan.com</a> concierge service to remind you that you have an order ' \
          'that needs finalizing. The guide has agreed to your request and to finalize you will need to pay for ' \
          'your order before services can be rendered. Please review your order ' \
          '<a href="%s/settings/guide/orders/?uuid=%s>by cliking here.</a>' \
          '<b\><b\>Thank you for your time<b\>The Tourzan.com team'\
          % ('https://www.tourzan.com', 'https://www.tourzan.com', order.uuid)
    if order.status_id == 2:
        time.sleep(timer)
        order = Order.objects.get(id=order.id)
        if order.status_id == 2:
            notify(subject='Reminder to pay for your tourzan order.', message=msg, user=order.guide.user,
                   email=order.guide.user.email)
            day += 1
            timer = 86400
            if day <= 2:
                pending_order(order, timer, day)