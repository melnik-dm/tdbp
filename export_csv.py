#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from export_if import TraceExport, TraceDir

class TraceExportCsv(TraceExport):
  def __init__(self, to, name, direction, with_contents):
    self._direction = direction
    TraceExport.__init__(self, to, name, 'csv', direction, with_contents)

  def header(self):
    return ''

  def footer(self):
    return ''

  # TODO: вывести caption
  def body_begin(self, caption):
    return ''

  def _ci_str(self, ci):
    if self.with_contents():
      return f'{ci.name()}\n{ci.brief_contents()}\n'
    else:
      return f'{ci.name()}'

  def _delimiter(self):
    return ','

  # TODO: вывести has_mark
  def body_entry(self, target, has_mark, forward, backward):
    t = f'"{self._ci_str(target)}"'
    if self._direction == TraceDir.bd:
      bw = '"' + '\n'.join(self._ci_str(x) for x in backward) + '",'
      fw = f'{self._delimiter()}"' + '\n'.join(self._ci_str(x) for x in forward) + '"'
      self.out(bw + t + fw + os.linesep)
    elif self._direction == TraceDir.fw:
      fw = f'{self._delimiter()}"' + '\n'.join(self._ci_str(x) for x in forward) + '"'
      self.out(t + fw + os.linesep)
    elif self._direction == TraceDir.bw:
      bw = f'{self._delimiter()}"' + '\n'.join(self._ci_str(x) for x in backward) + '"'
      self.out(t + bw + os.linesep)
    else:
      raise ValueError("bad contents '{self._direction}'")

  def body_end(self):
    return ''
