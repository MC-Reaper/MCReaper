# Module with lots of useful tools.
# Reaper Tools by Doz
# ---------------------------------------------------------------------------
# Modules
import random, datetime
# ---------------------------------------------------------------------------
# Humanize Time by Liudmil Mitev edited by makiolo.
def humanize_time(amount: int, units = 'seconds'):
    """
    Convert gibberish time values into human readable time.
    Usage: amount, the amount of time repersented by units.
           units, the unit to be used. Seconds is used by default.
    """

    def process_time(amount, units):

        INTERVALS = [   1, 60, 
                        60*60, 
                        60*60*24, 
                        60*60*24*7, 
                        60*60*24*7*4, 
                        60*60*24*7*4*12, 
                        60*60*24*7*4*12*100,
                        60*60*24*7*4*12*100*10]

        NAMES = [('second', 'seconds'),
                 ('minute', 'minutes'),
                 ('hour', 'hours'),
                 ('day', 'days'),
                 ('week', 'weeks'),
                 ('month', 'months'),
                 ('year', 'years'),
                 ('century', 'centuries'),
                 ('millennium', 'millennia')]

        result = []

        unit = list(map(lambda a: a[1], NAMES)).index(units)
        # Convert to seconds
        amount = amount * INTERVALS[unit]

        for i in range(len(NAMES)-1, -1, -1):
            a = amount // INTERVALS[i]
            if a > 0: 
                result.append( (a, NAMES[i][1 % a]) )
                amount -= a * INTERVALS[i]

        return result

    rd = process_time(int(amount), units)
    cont = 0
    for u in rd:
        if u[0] > 0:
            cont += 1

    buf = ''
    i = 0
    for u in rd:
        if u[0] > 0:
            buf += "%d %s" % (u[0], u[1])
            cont -= 1

        if i < (len(rd)-1):
            if cont > 1:
                buf += ", "
            else:
                buf += " and "

        i += 1

    return buf
# ---------------------------------------------------------------------------
# Date Diff by Doz
def datediff_humanize(old_time: datetime, new_time: datetime):
    """Get the difference of time in seconds then throw it to humanize_time"""
    timediff = new_time - old_time
    result = humanize_time(timediff.total_seconds())
    return result
# ---------------------------------------------------------------------------
# rtwdv by Doz
def rtwdv(txt, dic):
    """Replace words/letters in a string with values from a dict."""

    for a, b in dic.items():
        txt = txt.replace(a, b)

    return txt
# ---------------------------------------------------------------------------
# Simple hash generator by Doz
def rand_hash():
    """Returns a random hash"""
    
    ranbits_128 = random.getrandbits(128)
    return '%032x' % ranbits_128
# ---------------------------------------------------------------------------
