#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from enum import IntEnum

class TraceDir(IntEnum):
  bw = 1
#  bwi = 2
  fw = 3
#  fwi = 4
  bd = 5

class TraceExport:
  def __init__(self, to, name, form, direction, with_contents):
    dirname = to
    self._with_contents = with_contents
    self._filename = dirname + '/' + name + '.' + direction.name + '.' + 'tdbp' + '.' + form
    os.makedirs(os.path.dirname(self._filename), exist_ok=True)
    self._fd = open(self._filename, 'w')

  def __del__(self):
    if self._fd:
      self._fd.close()
    
  def with_contents(self):
    return self._with_contents
    
  def filename(self):
    return self._filename

  def out(self, data):
    if data:
      self._fd.write(data)
    
  def header(self):
    return ''

  def footer(self):
    return ''

  def body_begin(self, caption):
    return ''

  def body_entry(self, target, has_mark, forward, backward):
    return ''

  def body_end(self):
    return ''

