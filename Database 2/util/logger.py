from __future__ import print_function
from datetime import datetime
from util import systools
from util.handlers import ExceptionHandler
import inspect
import shutil
import sys
import os

class __COLORS:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

__LOG_VERBOSITY   = "info"
__PRINT_VERBOSITY = "warning"
__SHOW_INSPECTION = True

__DO_LOG = False
__SHOW_COLORS = False

__LOGDIR = None
__LOG_FILE_NAME = "latest.txt"

__VERBOSITY_LEVELS = ["silent","error","warning","info","debug"]
__VERBOSITY_MAPPING = {
  "silent"  :__VERBOSITY_LEVELS[:1],
  "error"   :__VERBOSITY_LEVELS[:2],
  "warning" :__VERBOSITY_LEVELS[:3],
  "info"    :__VERBOSITY_LEVELS[:4],
  "debug"   :__VERBOSITY_LEVELS[:5]
  }

__MAX_LOG_SIZE = 160000000 # bytes (160 megabytes)

__PREFIX = [""] # add the prefix information to message

def log_dir_was_setup():
  global __LOGDIR
  if __LOGDIR is None:
    return False
  else:
    return True

def append_prefix(new_prefix):
  global __PREFIX
  __PREFIX.append(new_prefix)

def pop_prefix():
  global __PREFIX
  __PREFIX.pop()

def __add_prefix_to_message(message):
  return u'%s %s' % (" ".join(__PREFIX), message)


def enable_inspection():
  global __SHOW_INSPECTION
  __SHOW_INSPECTION = True

def disable_inspection():
  global __SHOW_INSPECTION
  __SHOW_INSPECTION = False

def enable_colors():
  if (systools.on_windows()):
    return

  global __SHOW_COLORS
  __SHOW_COLORS = True

def disable_colors():
  global __SHOW_COLORS
  __SHOW_COLORS = False

def enable_logging():
  global __DO_LOG
  __DO_LOG = True

def disable_logging():
  global __DO_LOG
  __DO_LOG = False

def set_print_verbosity(v):
  global __PRINT_VERBOSITY
  if (isinstance(v,basestring)):
    __PRINT_VERBOSITY = v
  else:
    __PRINT_VERBOSITY = __VERBOSITY_LEVELS[v]

def set_log_verbosity(v):
  global __LOG_VERBOSITY
  if (isinstance(v,basestring)):
    __LOG_VERBOSITY = v
  else:
    __LOG_VERBOSITY = __VERBOSITY_LEVELS[v]

def set_logdir(path):
  global __LOGDIR
  if not (os.path.exists(path)):
    systools.makedirs(path)

  if (path[-1] != os.sep):
    path += os.sep

  __LOGDIR = path

def set_log_name(file_name):
  global  __LOG_FILE_NAME
  __LOG_FILE_NAME = file_name


def __format_message(message):
  if (isinstance(message, ExceptionHandler)):
    message = u'%s' % str(message)
  message = message.replace('\n', '\n    |')
  return message

def __caller_string():
  if (not __SHOW_INSPECTION):
    return " "

  caller = inspect.getouterframes(inspect.currentframe(), 2)[-1][1]
  s = ' %s ' % caller
  return s

def print_message(message, verbosity_level):
  if (verbosity_level not in __VERBOSITY_MAPPING[__PRINT_VERBOSITY]):
    return
  print(message)

def log_message(message, verbosity_level):
  if not (__DO_LOG):
    return

  if (verbosity_level not in __VERBOSITY_MAPPING[__LOG_VERBOSITY]):
    return

  global __LOGDIR
  if (__LOGDIR == None):
    __LOGDIR = systools.maindir_realpath() + "logs" + os.sep

  systools.makedirs(__LOGDIR)
  logfile_path = __LOGDIR + __LOG_FILE_NAME

  if (systools.file_exists(logfile_path)):
    if (systools.file_size(logfile_path) > __MAX_LOG_SIZE):
      destfile = __LOGDIR + ("%s.txt" % systools.now_string(systools.ISO_DATETIME_FORMAT_FSAFE))
      shutil.copy(logfile_path, destfile)
      logfile = open(logfile_path, 'w')
    else:
      logfile = open(logfile_path, 'a')
  else:
    logfile = open(logfile_path, 'w')
  print(message, file=logfile)
  logfile.close()

def debug(message):
  message = __format_message(message)
  message = __add_prefix_to_message(message)

  os = "[%s%sDEBUG] %s" % (systools.now_string(), __caller_string(), message)
  ls = os

  print_message(os, "debug")
  log_message(ls, "debug")

def info(message):
  message = __format_message(message)
  message = __add_prefix_to_message(message)

  os = "[%s%sINFO] %s" % (systools.now_string(), __caller_string(), message)
  ls = os
  print_message(os, "info")
  log_message(ls, "info")

def success(message):
  message = __format_message(message)
  message = __add_prefix_to_message(message)

  sc = __COLORS.GREEN if (__SHOW_COLORS) else ''
  ec = __COLORS.ENDC if (__SHOW_COLORS) else ''

  os = "%s[%s%sSUCCESS] %s%s" % (sc, systools.now_string(), __caller_string(), message, ec)
  ls = "[%s%sSUCCESS] %s" % (systools.now_string(), __caller_string(), message)

  print_message(os, "info")
  log_message(ls, "info")

def warning(message):
  message = __format_message(message)
  message = __add_prefix_to_message(message)

  sc = __COLORS.YELLOW if (__SHOW_COLORS) else ''
  ec = __COLORS.ENDC if (__SHOW_COLORS) else ''

  os = "%s[%s%sWARNING] %s%s" % (sc, systools.now_string(), __caller_string(), message, ec)
  ls = "[%s%sWARNING] %s" % (systools.now_string(), __caller_string(), message)

  print_message(os, "warning")
  log_message(ls, "warning")

def error(message):
  message = __format_message(message)
  message = __add_prefix_to_message(message)

  sc = __COLORS.RED if (__SHOW_COLORS) else ''
  ec = __COLORS.ENDC if (__SHOW_COLORS) else ''

  os = "%s[%s%sERROR] %s%s" % (sc, systools.now_string(), __caller_string(), message, ec)
  ls = "[%s%sERROR] %s" % (systools.now_string(), __caller_string(), message)

  print_message(os, "error")
  log_message(ls, "error")

def fail(message):
  message = __format_message(message)

  sc = __COLORS.RED if (__SHOW_COLORS) else ''
  ec = __COLORS.ENDC if (__SHOW_COLORS) else ''

  os = "%s[%s%sFAIL] %s%s" % (sc, systools.now_string(), __caller_string(), message, ec)
  ls = "[%s%sFAIL] %s" % (systools.now_string(), __caller_string(), message)

  print_message(os, "error")
  log_message(ls, "error")

def progress(i, total, mod=100):
  if (i % 100 == 0):
    percent_complete = (1 - (total - float(i))/total) * 100.0
    info("Percent complete {0:.1f}%".format(percent_complete))