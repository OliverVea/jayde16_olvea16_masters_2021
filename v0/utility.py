_utility_verbose_options_status=True
_utility_verbose_options_error=True
_utility_verbose_options_timestamp=True
_utility_verbose_options_tag_whitelist=[]
_utility_verbose_options_tag_blacklist=[]

import datetime
from colorsys import hsv_to_rgb

# status, error, tag_whitelist, tag_blacklist, timestamp
def set_verbose(**args):
    global _utility_verbose_options_status, _utility_verbose_options_error, _utility_verbose_options_timestamp, _utility_verbose_options_tag_whitelist, _utility_verbose_options_tag_blacklist
    for key, val in zip(args.keys(), args.values()):
        if key == 'status': _utility_verbose_options_status = val
        if key == 'error': _utility_verbose_options_error = val
        if key == 'tag_whitelist': _utility_verbose_options_tag_whitelist = val
        if key == 'tag_blacklist': _utility_verbose_options_tag_blacklist = val
        if key == 'timestamp': _utility_verbose_options_timestamp = val

def _get_timestamp(b):
    if b:
        return datetime.datetime.now().strftime('%H:%M:%S')
    return ''

def prints(s, tag=None):
    if not _utility_verbose_options_status:
        return

    if (len(_utility_verbose_options_tag_whitelist) > 0 and not tag in _utility_verbose_options_tag_whitelist) or tag in _utility_verbose_options_tag_blacklist:
        return

    message = ['[STATUS]']

    if _utility_verbose_options_timestamp:
        message.append(datetime.datetime.now().strftime('%H:%M:%S'))
    
    message.append(s)

    print(' '.join(message))

def printe(s, tag=None):
    if not _utility_verbose_options_error:
        return

    if (len(_utility_verbose_options_tag_whitelist) > 0 and not tag in _utility_verbose_options_tag_whitelist) or tag in _utility_verbose_options_tag_blacklist:
        return

    message = ['[ERROR]']

    if _utility_verbose_options_timestamp:
        message.append(datetime.datetime.now().strftime('%H:%M:%S'))
    
    message.append(s)

    print(' '.join(message))

def shortstring(s, maxlen):
    if len(s) > maxlen:
        return s[:maxlen] + '...'
    return s

def uniform_colors(n):
    return ['#' + "".join("%02X" % round(i*255) for i in hsv_to_rgb(j/n, 1, 1)) for j in range(n)]