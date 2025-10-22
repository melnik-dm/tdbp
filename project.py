#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from version import __version__

def PRJ_FILE_NAME():
  return ".tdbp"

def PRJ_FILE_PATH():
  return os.getcwd() + "/"+PRJ_FILE_NAME()

def version():
  version = 'unknown version'
  if os.path.isfile(PRJ_FILE_PATH()):
    with open(PRJ_FILE_PATH(), 'r') as fd:
      version = fd.readline()
  return version

def is_compatible():
  return __version__.split('.')[0] == version().split('.')[0]

def test():
  # os.path.dirname(os.path.realpath(__file__)) - путь размещения утилиты (не нужен)
  if (not os.path.isfile(PRJ_FILE_PATH())):
    return False
  else:
    if not version():
      return False
    else:
      return True

def is_ready():
  if (not test() or not is_compatible()):
    return False
  return True

def init():
  if test():
    raise ValueError("try init already existing project '"+os.getcwd()+"'")

  with open(PRJ_FILE_PATH(), 'w') as fd:
    fd.write(__version__)
    pass
