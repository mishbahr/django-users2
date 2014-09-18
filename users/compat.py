import base64
from binascii import Error as BinasciiError

try:
    from django.utils.http import urlsafe_base64_encode
except ImportError:
    def urlsafe_base64_encode(s):
        """
        Encodes a bytestring in base64 for use in URLs, stripping any trailing
        equal signs.
        """
        return base64.urlsafe_b64encode(s).rstrip(b'\n=')

try:
    from django.utils.http import urlsafe_base64_decode
except ImportError:
    def urlsafe_base64_decode(s):
        """
        Decodes a base64 encoded string, adding back any trailing equal signs that
        might have been stripped.
        """
        s = s.encode('utf-8')  # base64encode should only return ASCII.
        try:
            return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b'='))
        except (LookupError, BinasciiError) as e:
            raise ValueError(e)
