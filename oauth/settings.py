AUTHORIZATION_URL = 'https://gymkhana.iitb.ac.in/sso/oauth/authorize/'

REDIRECT_URI = 'http://127.0.0.1:8000/oauth/callback/'

CLIENT_ID = 'ohRIIM0R1kEIxHOu67RgAvp3i2HkGEyYteQ40N1b'

CLIENT_SECRET = '9EU9GyaGNyuFh36Hqdv2mhN2bTgSoX6wPxCOHSt85F33a8qBZ6xDXkMcg6GWjXoAijgVOW0UFqfg2HR8JFAlNy6mCY' \
                'OJHVsKbZzIQIH8jIlJYT3LaFjMaev9A8prulMR'

SCOPE = '%20'.join([
    'profile', 'ldap', 'program'
])

SSO_TOKEN_URL = "https://gymkhana.iitb.ac.in/sso/oauth/token/"

SSO_PROFILE_URL = "https://gymkhana.iitb.ac.in/sso/user/api/user/" \
                  "?fields=first_name,last_name,roll_number,email,insti_address"
