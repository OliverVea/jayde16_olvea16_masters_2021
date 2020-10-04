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

def _print(message_type, message_content, message_tag):
    if (len(_utility_verbose_options_tag_whitelist) > 0 and not message_tag in _utility_verbose_options_tag_whitelist) or message_tag in _utility_verbose_options_tag_blacklist:
        return

    message_tag = str(message_tag)

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')

    to_print = f'[{message_type.upper()}] ({message_tag}): {message_content}'
    if _utility_verbose_options_timestamp:
        to_print = f'{timestamp} [{message_type.upper()}] ({message_tag}): {message_content}'
    print(to_print)

    with open('log.txt', 'a+') as f:
        f.write(';'.join([timestamp, message_type, message_tag, message_content]) + '\n')

def prints(s, tag=None):
    if not _utility_verbose_options_status:
        return

    _print('status', s, tag)

def printe(s, tag=None):
    if not _utility_verbose_options_error:
        return

    _print('error', s, tag)

def shortstring(s, maxlen):
    if len(s) > maxlen:
        return s[:maxlen] + '...'
    return s

def uniform_colors(n):
    return ['#' + "".join("%02X" % round(i*255) for i in hsv_to_rgb(j/n, 1, 1)) for j in range(n)]

with open('log.txt', 'a+') as f:
    f.write('\n---\n\n')