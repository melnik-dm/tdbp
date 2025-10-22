# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later
from pyclibrary import CParser
import markdown

class Briefer:
  def __init__(self, opts):
    pass
    
  def parse(self, path, label):
    headers = []
    headers.append(path) # список путей заголовочных C-файлов
    func_str = ""
    if not path:
      print("C headers list is empty")
    else:
      parser = CParser(headers)
      func_list = parser.defs['functions'].keys()
      func_str = "<br>".join(func_list)

    #return markdown.markdown(func_str)
    return func_str # строка из имен функций, разделенных символом новой строки

