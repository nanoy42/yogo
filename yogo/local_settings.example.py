import ldap
from django_auth_ldap.config import LDAPSearch

AUTH_LDAP_SERVER_URI = ""
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch("", ldap.SCOPE_SUBTREE, "")

