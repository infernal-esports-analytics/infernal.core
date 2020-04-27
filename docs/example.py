"""

Ideal Usage:

from infernal import core, drake
# core -->  All the methods to interact with the riot API directly
# drake --> All the "resource" type methods and the extensions and QoL 
#               Improvements ontop of the LoL api


# To interact with the API directly:
# 1. From core, initialize a session
session = core.sesion.Session()

# or
session = core.session.default() #this is the default session if non is specified

# 2. From a session, create a service
mastery = session.service('mastery')

# if you don't use a session, it automatically grabs the default
league = core.service('mastery')








"""