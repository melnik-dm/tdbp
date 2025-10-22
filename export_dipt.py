#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from repoman import RepoMan
from export_if import TraceExport, TraceDir

class TraceExportDipt(TraceExport):
  def __init__(self, to, name, direction, with_contents):
    self._direction = direction
    TraceExport.__init__(self, to, name, 'table', direction, with_contents)

  def header(self):
    out = ''
    self.out(out)

  def footer(self):
    out = ''
    self.out(out)

  def body_begin(self, caption):
    out = ''
    out = out + '<table border="1" cellspacing="2" cellpadding="6" width="100%">\n'
    out = out + '<thead>\n'
    out = out + '<tr>\n'
    
    if self._direction == TraceDir.bd:
      out = out + '<th>Backward (Up)</th>\n'
      out = out + '<th>Target</th>\n'
      out = out + '<th>Forward (Down)</th>\n'
    elif self._direction == TraceDir.fw:
      out = out + '<th>Идентификатор ВУ</th>\n'
      out = out + '<th>Идентификатор НУ</th>\n'
    elif self._direction == TraceDir.bw:
      out = out + '<th>Идентификатор НУ</th>\n'
      out = out + '<th>Идентификатор ВУ</th>\n'
    else:
      raise ValueError("bad contents '{self._direction}'")    
    
    out = out + '</tr>\n'
    out = out + '</thead>\n<tbody>\n'
    self.out(out)
    
  def body_entry(self, target, has_mark, forward, backward):
    id = f'<td>{target.name()}</td>\n'
    if self._direction == TraceDir.bd:
      entry=''
    elif self._direction == TraceDir.fw:
      fw = '<td>'+'<br><br>'.join(f'{x.name()}' for x in forward)+'</td>\n' 
      entry = '<tr>\n' + id + fw + '</tr>\n'
    elif self._direction == TraceDir.bw:
      bw = '<td>'+'<br><br>'.join(f'{x.name()}' for x in backward)+'</td>\n'
      entry = '<tr>\n' + id + bw + '</tr>\n'
    else:
      raise ValueError("bad contents '{self._direction}'")    
    self.out(entry)

  def body_end(self):
    out = ''
    out = out + '</tbody></table>\n'
    self.out(out)

