# -*- coding: utf-8 -*-
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from tourzan.settings import FROM_EMAIL
from emails.models import EmailMessage as OwnEmailMessage
from emails.models import EmailMessageType
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class SendingEmail(object):

    current_site = Site.objects.get_current()
    domain = current_site.domain

    from_email = FROM_EMAIL
    reply_to_emails = [from_email]
    bcc_emails = [from_email]
    order = None
    chat = None

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
        kwargs = {"type_id":self.email_type_id, "email": ''.join(to_email), "user": to_user}
        if self.order:
            kwargs["order_id"] = self.order.id
        if hasattr(self, "chat_message"):
            kwargs["chat_message"] = self.chat_message
        OwnEmailMessage.objects.create(**kwargs)
        # print ('Email was sent successfully!')


    def email_for_order(self):
        self.email_type_id = 1 #order info
        order = self.order
        tour = order.tour if order.tour_id else None

        subject_tourist = None
        subject_guide = None

        if order.status_id in [2, 3, 4, 5, 6]:
            if tour:
                order_naming = '"%s"' % order.tour.name
            else:
                order_naming = 'with %s' % order.guide.user.generalprofile.first_name

            # cancelled by - for guide it is order.guide.user.generalprofile.first_name, but for tourists it us order.tourist.user.username
            if order.status_id == 1:
                subject_guide = 'You have new order for "%s" from %s!' % (order_naming, order.tourist.user.generalprofile.get_name())
                message_guide = 'New order for %s was created by %s. Click <a href="%s/settings/guide/orders/?uuid=%s" target="_blank">here</a> to review it.' % (order_naming, order.tourist.user.generalprofile.get_name(), self.domain, order.uuid)

            elif order.status_id == 2:# agreed
                subject_tourist = 'Tour %s was confirmed by guide!' % order_naming
                message_tourist = 'Tour %s was confirmed by guide! To review it and proceed with checkout click <a href="%s/live-chat/%s" target="_blank">here</a>' % (order_naming, self.domain, order.chat.uuid)

            elif order.status_id == 3: # cancelled by tourist
                subject_tourist = 'You cancelled a tour %s!' % order_naming
                message_tourist = 'You cancelled a tour %s!' % order_naming
                subject_guide = 'Order %s was cancelled by tourist! If you feel this is an error please reach out to your customer.' % (order_naming)
                message_guide = 'Order <a href="%s/settings/guide/orders/?uuid=%s" target="_blank">%s</a> was cancelled by tourist. ' \
                                'If you feel this an error please reach out to your customer <a href="%s/live-chat/%s" target="_blank">here</a>.' % (self.domain, order.uuid, order_naming, self.domain, order.chat.uuid)

            elif order.status_id == 6: # cancelled by guide
                subject_tourist = 'A tour %s was cancelled by guide!' % (order_naming)
                message_tourist = 'Order %s was cancelled by guide. If you feel this is an error please reach out to your guide <a href="%s/live-chat/%s" target="_blank">here</a>.' % (order_naming, self.domain, order.chat.uuid)
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
                        '<a href="https://www.tourzan.com/order_completing_page/%s/" target="_blank">here</a>' % (order_naming, order.uuid)

                subject_guide = 'Order #%s was completed!' % order.uuid
                if self.is_guide_saving:
                    message_guide = 'Order <a href="https://www.tourzan.com/settings/guide/orders/?uuid=%s" target="_blank">#%s</a> was completed!' % (order.uuid, order.uuid)
                else:
                    message_guide = 'Order <a href="https://www.tourzan.com/settings/guide/orders/?uuid=%s" target="_blank">#%s</a> was completed! Please review your experience ' \
                       '<a href="https://www.tourzan.com/order_completing_page/%s/" target="_blank">here</a>' % (order.uuid, order.uuid, order.uuid)

            elif order.status_id == 5: # payment reserved
                subject_tourist = 'A payment for your tour %s was reserved!' % (order_naming)
                message_tourist = 'A payment for your tour %s was reserved!' % (order_naming)

                subject_guide = 'A payment for your tour %s was reserved!' % (order_naming)
                message_guide = 'A payment for your tour %s was reserved! Click <a href="https://www.tourzan.com/settings/guide/orders/?uuid=%s" target="_blank">here</a> for details' % (order_naming, order.uuid)


            #sending email to guide
            if subject_guide:
                to_user = order.guide.user
                to_email = [order.guide.user.email]
                self.sending_email(to_user, to_email, subject=subject_guide, message=message_guide, template_location="emails/order_related_email_guides.html")

            #sending email to tourist
            if subject_tourist:
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
                  "You can now enter your <a href='https://www.tourzan.com/guide/payouts/'>payout preferences</a> \n\n" \
                  "Have a great day.\n" \
                  "<br><br>The Tourzan Team</p>"
        to_user = User.objects.get(id=user_id)
        to_email = [to_user.email]
        self.sending_email(to_user, to_email, subject, message)


    def send_new_message_email(self):
        email_type, created = EmailMessageType.objects.get_or_create(name='Chat')
        self.email_type_id = email_type.id

        chat_message = self.data.get("chat_message")
        chat = chat_message.chat

        self.chat_message = chat_message
        message = chat_message.message
        user_from = self.data.get("user_from")
        user_to = self.data.get("user_to")

        user_from_name = user_from.generalprofile.get_name()

        subject = "Notification about new message on tourzan.com from %s" % user_from_name
        message = "<p>You have received a new message from %s.</p>" \
                  "<p><b>Message: </b>%s</p>\n" \
                  "<p>Go by this <a href='https://www.tourzan.com/chats/chat_uuid/%s/' target='_blank'>link</a> for response. \n\n</p>" \
                  "<p>Have a great day.\n" \
                  "<br><br>The Tourzan Team</p>" % (user_from_name, message, chat.uuid)

        if user_to:
            to_email = [user_to.email]
            self.sending_email(user_to, to_email, subject, message)

    def email_for_express_signup(self):
        """
        Sending of the email with a link to fully complete express signup process later
        """
        user = self.data.get("user")
        email_type, created = EmailMessageType.objects.get_or_create(name='Welcome email for express singup')
        self.email_type_id = email_type.id
        domain = Site.objects.get_current().domain
        subject = "Tourzan Welcome Email"
        message = "You have initiated booking a tour without user sign up on www.tourzan.com. \n" \
                  "To complete full signup process your email please use " \
                  "<a href='%s/express-signup-completing/%s' target='_blank'>this link</a> \n\n" \
                  "Have a great day.\n" \
                  "<br><br>The Tourzan Team</p>" % (domain, user.generalprofile.uuid)  # 'www.tourzan.com', user.generalprofile.uuid)
        to_user = user
        to_email = [to_user.email]
        self.sending_email(to_user, to_email, subject, message)


