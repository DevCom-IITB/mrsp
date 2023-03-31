from decouple import config

AUTHORIZATION_URL = 'https://gymkhana.iitb.ac.in/sso/oauth/authorize/'

REDIRECT_URI = config('REDIRECT_URI')

CLIENT_ID = config('CLIENT_ID')

CLIENT_SECRET = config("CLIENT_SECRET")

SCOPE = '%20'.join([
    'profile', 'ldap', 'program'
])

SSO_TOKEN_URL = "https://gymkhana.iitb.ac.in/sso/oauth/token/"

SSO_PROFILE_URL = "https://gymkhana.iitb.ac.in/sso/user/api/user/" \
                  "?fields=first_name,last_name,roll_number,email,insti_address"
