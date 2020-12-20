from datetime import datetime
import sys
import os

ISO_DATETIME_FORMAT_FSAFE = "%Y%m%dT%H%M%S"
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ISO_DATE_FORMAT = "%Y-%m-%d"

def on_windows():
  return os.name in ['nt']

def on_linux():
  return os.name in ['posix']

def makedirs(path = None):
  if (path == None):
    raise Exception("No path specified")

  if not (os.path.exists(path)):
    os.makedirs(path)

def files(path):
  return [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]

def file_exists(path):
  return os.path.isfile(path)

def file_size(path):
  if not (file_exists(path)):
    raise Exception("Could not find file: '%s'" % path)

  return os.stat(path).st_size

def maindir_realpath():
  dirname = os.path.split(os.path.realpath(sys.argv[0]))[0]
  if (dirname[-1] != os.sep):
    dirname += os.sep
  return dirname

def maindir_abspath():
  dirname = os.path.split(os.path.realpath(sys.argv[0]))[0]
  if (dirname[-1] != os.sep):
    dirname += os.sep
  return dirname

def now_string(date_format="%Y-%m-%dT%H:%M:%S"):
  now = datetime.now()
  return now.strftime(date_format)