from django.contrib.auth.signals import user_logged_in


def perform_some_action_on_login(sender, user, **kwargs):
    general_profile = user.generalprofile
    print("after login")

user_logged_in.connect(perform_some_action_on_login)