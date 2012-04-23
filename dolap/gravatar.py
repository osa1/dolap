import urllib
import hashlib

def create_gravatar_link(email, size=30):
    default = "/media/default_gravatar.jpg"

    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
    return gravatar_url
