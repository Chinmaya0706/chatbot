# ssl_patch.py
import ssl
import urllib3
import requests
from requests.sessions import Session

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Disable global SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# -------- Patch requests methods (module-level) --------
def disable_ssl_for_requests_module():
    METHODS = ["get", "post", "put", "delete", "patch", "head", "options"]
    for method_name in METHODS:
        original_method = getattr(requests, method_name)

        def insecure_method(*args, original=original_method, **kwargs):
            kwargs["verify"] = False
            return original(*args, **kwargs)

        setattr(requests, method_name, insecure_method)

disable_ssl_for_requests_module()


# -------- Patch requests.Session --------
_original_session_request = Session.request

def insecure_session_request(self, method, url, **kwargs):
    kwargs["verify"] = False
    return _original_session_request(self, method, url, **kwargs)

Session.request = insecure_session_request

# import requests

# def disable_ssl_for_requests():
#     METHODS = ["get", "post", "put", "delete", "patch", "head", "options"]
#     for method_name in METHODS:
#         original_method = getattr(requests, method_name)

#         def insecure_method(*args, original=original_method, **kwargs):
#             kwargs["verify"] = False
#             return original(*args, **kwargs)

#         setattr(requests, method_name, insecure_method)

# disable_ssl_for_requests()


