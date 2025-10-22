# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later
import xml.etree.ElementTree as ET
import markdown

class Briefer:
  def __init__(self, opts):
    self.opts = opts

  def parse(self, path, label):
    if self.opts:
      tag = self.opts
    else:
      tag = 'text'
    tree = ET.parse(path)
    root = tree.getroot()
    text = root.find(tag).text
    if text.startswith('\n'):
      text = text[1:]
    if text.endswith('\n'):
      text = text[:-1]
    return markdown.markdown(text)
    
    #with open(path, 'r') as fd:
    #  data = fd.read()
    #  return data
