__author__ = 'keroth'


import string
_base32_translate = string.maketrans(
    '0123456789ABCDEFGHKLMNPQRSTUWXYZIJOV',
    '0123456789ABCDEFGHIJKLMNOPQRSTUV110U'
)

_base32_alphabet='0123456789ABCDEFGHKLMNPQRSTUWXYZ'

def base32encode(number):
    """Converts an integer to a base36 string."""
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')

    base32 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(_base32_alphabet):
        return sign + _base32_alphabet[number]

    while number != 0:
        number, i = divmod(number, len(_base32_alphabet))
        base32 = _base32_alphabet[i] + base32

    return sign + base32

def base32decode(number):
    number = number.translate(_base32_translate)
    return int(number, 32)

