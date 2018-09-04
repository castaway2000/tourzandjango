ACCOUNT_ADAPTER = 'users.adapter_allAuth.MyAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapter_allAuth.MySocialAccountAdapter'
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTOMATICALLY_CONNECT = True
PRESERVE_USERNAME_CASING = True
ACCOUNT_FORMS = {
    "signup": "users.forms.CustomSignupForm",
}

ACCOUNT_AUTHENTICATION_METHOD = "username_email"

ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email', 'public_profile'],
        'METHOD': 'oauth2',
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'verified',
            'locale',
            'timezone',
            'link',
            'gender',
            'likes',      #This is the one you want
            'friends',
        ],

        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': False,
        'VERSION': 'v2.4'
    }
}
