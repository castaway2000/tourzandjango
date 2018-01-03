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
        self.is_guide_saving = data.get("is_guide_saving")


    def sending_email(self, to_user, to_email, subject, message, template_location=None):
        vars = {
            'message': message,
            'user': to_user
        }
        if template_location:
            message = get_template(template_location).render(vars)
        else:
            message = get_template('emails/notification_email.html').render(vars)

        msg = EmailMessage(
                        subject, message, from_email=self.from_email,
                        to=to_email, bcc=self.bcc_emails, reply_to=self.reply_to_emails
                        )
        msg.content_subtype = 'html'
        msg.mixed_subtype = 'related'
        msg.send()

        kwargs = dict()
        kwargs = {"type_id":self.email_type_id, "email": to_email, "user": to_user}
        if self.order:
            kwargs["order_id"] = self.order.id
        OwnEmailMessage.objects.create(**kwargs)
        # print ('Email was sent successfully!')


    def email_for_order(self):
        self.email_type_id = 1 #order info
        order = self.order
        tour = order.tour if order.tour_id else None

        if order.status_id in [2, 3, 4, 5, 6]:
            if tour:
                order_naming = '"%s"' % order.tour.name
            else:
                order_naming = 'with %s' % order.guide.user.generalprofile.first_name

            # cancelled by - for guide it is order.guide.user.generalprofile.first_name, but for tourists it us order.tourist.user.username
            if order.status_id == 2:# agreed
                subject_tourist = 'Tour %s was confirmed by guide!' % order_naming
                message_tourist = 'Tour %s was confirmed by guide!' % order_naming
                subject_guide = 'Order #%s was confirmed by tourist!' % order.id
                message_guide = 'Order <a href="https://www.tourzan.com/settings/guide/orders/?id=%s" target="_blank">#%s</a> was confirmed by tourist' % (order.id, order.id)

            elif order.status_id == 3: # cancelled by tourist
                subject_tourist = 'You cancelled a tour %s!' % order_naming
                message_tourist = 'You cancelled a tour %s!' % order_naming
                subject_guide = 'Order #%s was cancelled by %s! If you feel this is an error please reach out to your customer.' % (order.id, order.tourist.user.username)
                message_guide = 'Order <a href="https://www.tourzan.com/settings/guide/orders/?id=%s" target="_blank">#%s</a> was cancelled by %s. If you feel this an error please reach out to your customer' % (order.id, order.id, order.tourist.user.username)

            elif order.status_id == 6: # cancelled by guide
                subject_tourist = 'A tour %s was cancelled by %s!' % (order_naming, order.guide.user.generalprofile.first_name)
                message_tourist = 'Order %s was cancelled by %s. If you feel this is an error please reach out to your guide.' % (order.id, order.guide.user.generalprofile.first_name)
                subject_guide = 'You cancelled the order #%s!' % order.id
                message_guide = 'You cancelled the order <a href="https://www.tourzan.com/settings/guide/orders/?id=%s" target="_blank">#%s</a>!' % (order.id, order.id)

            elif order.status_id == 4: # completed
                subject_tourist = 'Tour %s was completed!' % order_naming

                #those one (guide or tourist), who saves an order setting "completed" status write a feedback at the same time
                #so the idea is avoid sending him a message with asking to "review his experience"
                if not self.is_guide_saving:
                    message_tourist = 'Tour %s was completed!' % (order_naming)
                else:
                    message_tourist = 'Tour %s was completed! Please review your experience ' \
                        '<a href="https://www.tourzan.com/order_completing_page/%s/" target="_blank">here</a>' % (order_naming, order.id)

                subject_guide = 'Order #%s was completed!' % order.id
                if self.is_guide_saving:
                    message_guide = 'Order <a href="https://www.tourzan.com/settings/guide/orders/?id=%s" target="_blank">#%s</a> was completed!' % (order.id, order.id)
                else:
                    message_guide = 'Order <a href="https://www.tourzan.com/settings/guide/orders/?id=%s" target="_blank">#%s</a> was completed! Please review your experience ' \
                       '<a href="https://www.tourzan.com/order_completing_page/%s/" target="_blank">here</a>' % (order.id, order.id, order.id)

            elif order.status_id == 5: # payment reserved
                subject_tourist = 'A payment for your tour %s was reserved!' % (order_naming)
                message_tourist = 'A payment for your tour %s was reserved!' % (order_naming)

                subject_guide = 'You have received a new order #%s!' % (order.id)
                message_guide = 'You have received a new order <a href="https://www.tourzan.com/settings/guide/orders/?id=%s" target="_blank">#%s</a>!' % (order.id, order.id)


            #sending email to guide
            to_user = order.guide.user
            to_email = [order.guide.user.email]
            self.sending_email(to_user, to_email, subject=subject_guide, message=message_guide, template_location="emails/order_related_email_guides.html")

            #sending email to tourist
            to_user = order.tourist.user
            to_email = [order.tourist.user.email] if order.tourist.user.email else [FROM_EMAIL]
            self.sending_email(to_user, to_email, subject=subject_tourist, message=message_tourist, template_location="emails/order_related_email_tourists.html")


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
        email_type, created = EmailMessageType.objects.get_or_create(name='Verification Notification Email')
        self.email_type_id = email_type.id
        subject = "Tourzan Verification Completed"
        message = "<p>Tourzan.com has completed your identity verification check. " \
                  "You can now enter your <a href='https://www.tourzan.com/guide/payouts/'>payout preferences</a> " \
                  "and set your <a href='https://www.tourzan.com/en/calendar/'>calendar</a> " \
                  "so that tourists can hire you.\n\n" \
                  "Have a great day.\n" \
                  "-The Tourzan Team"
        to_user = User.objects.get(id=user_id)
        to_email = [to_user.email]
        self.sending_email(to_user, to_email, subject, message)
