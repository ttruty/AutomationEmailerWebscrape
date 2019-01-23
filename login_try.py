##import requests
##
##payload = {'inUserName': 'USERNAME/EMAIL', 'inUserPass': 'PASSWORD'}
##url = 'https://radc.rush.edu/radc/schedule/Weekly'
##requests.post(url, data=payload)

##import requests
##
### Fill in your details here to be posted to the login form.
##payload = {
##    'username': 'ttruty',
##    'password': 'pk97nw',
##    'submit' : 'Login'
##}
##
### Use 'with' to ensure the session context is closed after use.
##with requests.Session() as s:
##    p = s.post('https://radc.rush.edu/radc/schedule/Weekly', data=payload)
##    # print the html returned or something more intelligent to see if it's a successful login page.
##    print(p.text)
##
##    # An authorised request.
##    r = s.get('https://radc.rush.edu/radc/schedule/Weekly')
##    print(r.text)
##        # etc...

def login_gui():
    username = input('username: ')
    password = input('password: ')
    return username, password

us, pw = login_gui()
