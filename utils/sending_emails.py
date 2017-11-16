# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from tourzan.settings import FROM_EMAIL
from emails.models import EmailMessage as OwnEmailMessage
from emails.models import EmailMessageType
from django.contrib.auth.models import User


class SendingEmail(object):
    from_email = FROM_EMAIL
    reply_to_emails = [from_email]
    bcc_emails = [from_email]

    def __init__(self, data):
        data = data
        self.data = data
        self.order = data.get("order")

        if self.order:
            self.email_for_order()


    def sending_email(self, to_user, to_email, subject, message):
        vars = {
            'message': message,
            'user': to_user
        }

        print ("before sending emails")
        message = get_template('emails/notification_email.html').render(vars)

        print(self.from_email)
        print(to_email)
        print(self.bcc_emails)
        print(self.reply_to_emails)
        msg = EmailMessage(
                        subject, message, from_email=self.from_email,
                        to=to_email, bcc=self.bcc_emails, reply_to=self.reply_to_emails
                        )
        print("after message")
        msg.content_subtype = 'html'
        msg.mixed_subtype = 'related'
        msg.send()
        print("send")

        kwargs = dict()
        kwargs = {"type_id":self.email_type_id, "email": to_email, "user": to_user}
        if self.order:
            kwargs["order_id"] = self.order.id
        OwnEmailMessage.objects.create(**kwargs)
        print ('Email was sent successfully!')


    def email_for_order(self):
        self.email_type_id = 1 #order info
        order = self.order
        tour = order.tour if order.tour_id else None
        # print (tour)
        order_msg = '\n\nto manage your customers please visit '
        orders_link = '<a href="https://www.tourzan.com/en/settings/guide/orders/">your orders page.</a>'

        if tour:
            order_naming = '"%s"' % order.tour.name
        else:
            order_naming = 'with %s' % order.guide.name

        if order.status.id == 1:# pending
            self.subject = 'Tour %s was created' % order_naming
            self.message = 'Tour %s was created' % order_naming
        elif order.status.id == 2:# agreed
            self.subject = 'Tour %s was aggreed!' % order_naming
            self.message = 'Tour %s was aggreed!' % order_naming
        elif order.status.id == 3: # cancelled by tourist
            self.subject = 'Tour %s was cancelled!' % order_naming
            self.message = 'Tour %s was cancelled by %s! If you feel this an error please reach out to your customer' \
                           'by going to %s' % (order_naming, order.tourist.user.username, orders_link)

        elif order.status.id == 4: # completed
            self.subject = 'Tour %s was completed!'
            self.subject = 'Tour %s was completed! Please review your experience at %s' % (order_naming, orders_link)
        elif order.status.id == 5: # waiting for payment
            self.subject = 'Tour %s is waiting for payment! %s' % (order_naming, order_msg+orders_link)
            self.message = 'Tour %s is waiting for payment! %s' % (order_naming, order_msg+orders_link)
        elif order.status.id == 6: # cancelled by guide
            self.subject = 'Tour %s was cancelled'
            self.message = 'Tour %s was cancelled by %s! %s' % (order_naming, order.guide.user.username,
                                                                order_msg+orders_link)

        subject = self.subject
        message = self.message

        #sending to guide
        to_user = order.guide.user
        to_email = [order.guide.user.email]
        self.sending_email(to_user, to_email, subject, message)

        #sending to user
        to_user = order.tourist.user
        to_email = [order.tourist.user.email] if order.tourist.user.email else [FROM_EMAIL]
        self.sending_email(to_user, to_email, subject, message)


    def email_for_partners(self):
        api_token = self.data.get("api_token")
        user_id = self.data.get("user_id")

        email_type, created = EmailMessageType.objects.get_or_create(name="API Partner Welcome Email")
        self.email_type_id = email_type.id
        subject = "Receiving API token from Tourzan"
        message = "<p> We have received your application for getting our API access.</p>" \
                  "<p>It has been successfully approved.</p>" \
                  "<p> Here is your API token for tourzan.com: %s</p>" % api_token
        to_user = User.objects.get(id=user_id)
        to_email = [to_user.email]
        print("to email is tuple")
        self.sending_email(to_user, to_email, subject, message)

    def email_for_verficiation(self):
        user_id = self.data.get("user_id")
        subject = "Tourzan Verification Completed"
        message = "<p>Tourzan.com has completed your identity verification check. " \
                  "You can now enter your <a hfre='https://www.tourzan.com/en/guide/payouts/'>payout prefrences</a> " \
                  "and set your <a href='https://www.tourzan.com/en/calendar/'>calendar</a> " \
                  "so that tourists can hire you.\n\n" \
                  "Have a great day.\n" \
                  "-The Tourzan Team"
        to_user = User.objects.get(id=user_id)
        to_email = [to_user.email]
        self.sending_email(to_user, to_email, subject, message)