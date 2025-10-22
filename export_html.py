#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from repoman import RepoMan
from export_if import TraceExport, TraceDir

class TraceExportHtml(TraceExport):
  def __init__(self, to, name, direction, with_contents):
    self._direction = direction
    TraceExport.__init__(self, to, name, 'html', direction, with_contents)

  def header(self):
    out = ''
    out = out + '<html>\n'
    out = out + '<head>\n'
    out = out + '<style>\n'
    out = out + 'caption {\n'
    out = out + '  padding: 10px;\n'
    out = out + '}\n'
    out = out + ':target {\n'
    out = out + '  background-color: #ffa;\n'
    out = out + '}\n'
    out = out + 'table {\n'
    out = out + '    table-layout: fixed;\n'
    out = out + '    word-wrap: break-word;\n'
    out = out + '    border-collapse: collapse;\n'
    out = out + '    border: 2px solid rgb(200, 200, 200);\n'
    out = out + '    letter-spacing: 1px;\n'
    out = out + '    font-family: sans-serif;\n'
    out = out + '    font-size: .8rem;\n'
    out = out + '}\n'
    out = out + 'tr:nth-child(even) td {\n'
    out = out + '    background-color: white;\n'
    out = out + '}\n'
    out = out + 'tr:nth-child(odd) td {\n'
    out = out + '    background-color: rgb(250, 250, 250);\n'
    out = out + '}\n'
    out = out + 'A:hover { color: black; background: #ffa; }\n'
    out = out + 'A:link { color: black;text-decoration: none; }\n'
    out = out + 'A:visited { color: black;text-decoration: none; }\n'
    out = out + 'A:active { color: black;text-decoration: none; }\n'
    out = out + '</style>\n'
    out = out + '</head>\n'
    out = out + '<body>\n'
    #out = out + '<script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>'
    #out = out + '<table class="sortable">'
    self.out(out)

  def footer(self):
    out = ''
    out = out + '</body></html>\n'
    self.out(out)

  def body_begin(self, caption):
    out = ''
    out = out + '<table border="1" cellspacing="2" cellpadding="6" width="100%">\n'
    out = out + '<caption>'+caption+'</caption>\n'
    out = out + '<thead>\n'
    out = out + '<tr style="background-color: #DBECFF;">\n'
    
    if self._direction == TraceDir.bd:
      out = out + '<th>Backward (Up)</th>\n'
      out = out + '<th>Target</th>\n'
      out = out + '<th>Forward (Down)</th>\n'
    elif self._direction == TraceDir.fw:
      out = out + '<th>Target</th>\n'
      out = out + '<th>Forward (Down)</th>\n'
    elif self._direction == TraceDir.bw:
      out = out + '<th>Target</th>\n'
      out = out + '<th>Backward (Up)</th>\n'
    else:
      raise ValueError("bad contents '{self._direction}'")    
    
    out = out + '</tr>\n'
    out = out + '</thead>\n<tbody>\n'
    self.out(out)
    
  def _contents(self, ci):
    if self.with_contents():
      try:
        return f'<br>{ci.brief_contents()}<br>'
      except:
        return "<br>CAN'T GET CONTENTS"
    else:
      return ''
    
  def body_entry(self, target, has_mark, forward, backward):
    font_color = "#22801C" if has_mark else "black"
    id = f'<td><font color="{font_color}"><a name="{target.name()}">{target.name()}</a>{self._contents(target)}</font></td>\n'
    if self._direction == TraceDir.bd:
      bw = '<td>'+'<br><br>'.join(f'<a href="{x.repo().union()}.bd.tdbp.html#{x.name()}">{x.name()}</a>{self._contents(x)}' for x in backward)+'</td>\n'
      fw = '<td>'+'<br><br>'.join(f'<a href="{x.repo().union()}.bd.tdbp.html#{x.name()}">{x.name()}</a>{self._contents(x)}' for x in forward)+'</td>\n' 
      entry = '<tr>\n' + bw + id + fw + '</tr>\n'
    elif self._direction == TraceDir.fw:
      fw = '<td>'+'<br><br>'.join(f'<a href="{x.repo().union()}.bw.tdbp.html#{x.name()}">{x.name()}</a>{self._contents(x)}' for x in forward)+'</td>\n' 
      entry = '<tr>\n' + id + fw + '</tr>\n'
    elif self._direction == TraceDir.bw:
      bw = '<td>'+'<br><br>'.join(f'<a href="{x.repo().union()}.fw.tdbp.html#{x.name()}">{x.name()}</a>{self._contents(x)}' for x in backward)+'</td>\n'
      entry = '<tr>\n' + id + bw + '</tr>\n'
    else:
      raise ValueError("bad contents '{self._direction}'")    
    self.out(entry)

  def body_end(self):
    out = ''
    out = out + '</tbody></table>\n'
    self.out(out)

