# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from PIL import Image
from StringIO import StringIO
import requests
import os
import sys
from tourzan.settings import FROM_EMAIL
from emails.models import EmailMessage as OwnEmailMessage


class SendingEmail(object):
    from_email = FROM_EMAIL
    reply_to_emails = [from_email]
    target_emails = []
    bcc_emails = [from_email]

    def __init__(self, data):
        data = data
        self.data = data
        self.order = data.get("order")

        if self.order:
            self.email_for_order()


    def sending_email(self):
        print "enter to sending email"

        for index, email in enumerate(self.bcc_emails):
            print email
            print index

            user = self.users[index]

            vars = {
                'message': self.message,
                'user': user
            }

            print ("before sending emails")
            message = get_template('emails/notification_email.html').render(vars)


            msg = EmailMessage(
                            self.subject, self.message, from_email=self.from_email,
                            to=self.target_emails, bcc=self.bcc_emails, reply_to=self.reply_to_emails
                            )
            msg.content_subtype = 'html'
            msg.mixed_subtype = 'related'
            msg.send()

            email_message = OwnEmailMessage.objects.create(type_id=self.email_type, email=email,
                                                           order=self.order, user=user)
            print ('Email was sent successfully!')


    def email_for_order(self):
        print "email type one"
        self.email_type = 1 #order info

        order = self.order
        tour = order.tour
        if tour:
            order_naming = '"%s"' % order.tour.name
        else:
            order_naming = 'with %s' % order.guide.name

        if order.status.id == 1:# pending
            self.subject = 'Tour %s was created' % order_naming
        elif order.status.id == 2:# agreed
            self.subject = 'Tour %s was aggreed!' % order_naming
        elif order.status.id == 3: # cancelled by tourist
            self.subject = 'Tour %s was cancelled by %s!' % (order_naming, order.tourist.user.username)

        elif order.status.id == 4: # completed
            self.subject = 'Tour %s was completed!' % order_naming
        elif order.status.id == 5: # waiting for payment
            self.subject = 'Tour %s is waiting for payment!' % order_naming
        elif order.status.id == 6: # cancelled by guide
            self.subject = 'Tour %s was cancelled by %s!' % (order_naming, order.guide.user.username)

        self.message = self.subject

        self.users = [order.guide.user]
        self.bcc_emails = [order.guide.user.email]

        self.sending_email()
