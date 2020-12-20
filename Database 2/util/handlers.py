from __future__ import print_function
from datetime import datetime
import sys, traceback

class ExceptionHandler:
  def __init__(self, exception):
    self.exception = exception
    self.exception_string = self.format()
    self.now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

  def format(self):
    ret = ''
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback, None)
    header = ('Exception: %s' % type(self.exception).__name__)

    ret += '\n' + header + '\n'
    ret += 'Time: %s\n' % datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    ret += 'Traceback:\n'
    for i,el in enumerate(tb):
      el_string = ''.ljust(i) + '--> "%s":%s in %s' % (el[0], el[1], el[2])
      if ('<' not in el_string):
        el_string += '()'
      ret += el_string + '\n'

    last_string = '\n'.ljust(i + 5) + '%s' % tb[-1][3]
    ret += last_string + '\n'
    try:
      ret += ('\nError: \n%s' % exc_value)
    except:
      pass

    return ret

  def __repr__(self):
    return self.exception_string

  def __str__(self):
    return self.exception_string