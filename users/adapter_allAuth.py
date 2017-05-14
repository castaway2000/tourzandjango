from django.conf import settings
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


from allauth.utils import (import_attribute,
                     email_address_exists,
                     valid_email_or_none,
                     serialize_instance,
                     deserialize_instance)

from allauth.account.utils import user_email, user_username, user_field
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account import app_settings as account_settings
from allauth.socialaccount import app_settings
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives, EmailMessage


class MyAccountAdapter(DefaultAccountAdapter):

    def format_email_subject(self, subject):
        print ("CUSTOM")
        prefix = settings.EMAIL_SUBJECT_PREFIX
        print (prefix + force_text(subject))
        return force_text(subject)

    def render_mail(self, template_prefix, email, context):
        """
        Renders an e-mail to `email`.  `template_prefix` identifies the
        e-mail that is to be sent, e.g. "account/email/email_confirmation"
        """
        subject = render_to_string('{0}_subject.txt'.format(template_prefix),
                                   context)
        # remove superfluous line breaks
        subject = " ".join(subject.splitlines()).strip()
        subject = self.format_email_subject(subject)

        from_email = "%s <%s>" % ("Social Share Me", self.get_from_email())
        print ("render email")
        print (subject)

        bodies = {}
        for ext in ['html', 'txt']:
            try:
                template_name = '{0}_message.{1}'.format(template_prefix, ext)
                bodies[ext] = render_to_string(template_name,
                                               context).strip()
            except TemplateDoesNotExist:
                if ext == 'txt' and not bodies:
                    # We need at least one body
                    raise
        if 'txt' in bodies:
            msg = EmailMultiAlternatives(subject,
                                         bodies['txt'],
                                         from_email,
                                         [email])
            if 'html' in bodies:
                msg.attach_alternative(bodies['html'], 'text/html')
        else:
            msg = EmailMessage(subject,
                               bodies['html'],
                               from_email,
                               [email])
            msg.content_subtype = 'html'  # Main content is now text/html
        return msg


class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_auto_signup_allowed(self, request, sociallogin):
        # If email is specified, check for duplicate and if so, no auto signup.
        auto_signup = app_settings.AUTO_SIGNUP
        if auto_signup:
            email = user_email(sociallogin.user)
            # Let's check if auto_signup is really possible...
            if email:
                if account_settings.UNIQUE_EMAIL:
                    if email_address_exists(email):
                        # Oops, another user already has this address.
                        # We cannot simply connect this social account
                        # to the existing user. Reason is that the
                        # email adress may not be verified, meaning,
                        # the user may be a hacker that has added your
                        # email address to their account in the hope
                        # that you fall in their trap.  We cannot
                        # check on 'email_address.verified' either,
                        # because 'email_address' is not guaranteed to
                        # be verified.

                        """
                        Commented out
                        """
                        #auto_signup = False

                        # FIXME: We redirect to signup form -- user will
                        # see email address conflict only after posting
                        # whereas we detected it here already.
            elif app_settings.EMAIL_REQUIRED:
                # Nope, email is required and we don't have it yet...
                auto_signup = False
        return auto_signup

    def pre_social_login(self, request, sociallogin):
        print ("entered to presocial")
        # """
        # Invoked just after a user successfully authenticates via a
        # social provider, but before the login is actually processed
        # (and before the pre_social_login signal is emitted).
        #
        # We're trying to solve different use cases:
        # - social account already exists, just go on
        # - social account has no email or email is unknown, just go on
        # - social account's email exists, link social account to existing user
        # """
        #
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            print 1
            return

        # # some social logins don't have an email address, e.g. facebook accounts
        # # with mobile numbers only, but allauth takes care of this case so just
        # # ignore it
        if 'email' not in sociallogin.account.extra_data:
            print 2
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases


        try:
            print 3
            email = sociallogin.account.extra_data['email'].lower()
            print email
            # email_address = EmailAddress.objects.get(email__iexact=email)
            user = User.objects.get(email__iexact=email)

        # if it does not, let allauth take care of this new social account
        except EmailAddress.DoesNotExist:
            print 4
            return

        # if it does, connect this new social login to the existing user
        # user = email_address.user #it is commented because above EmailAddress is replaced with User model

        sociallogin.connect(request, user)

