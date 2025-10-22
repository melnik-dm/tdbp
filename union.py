#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import json

class Unions:
  def FUNIONS():
    return ".unions"

  def __init__(self):
    self._data = {}
    self.load()

  def __del__(self):
    self.save()

  def __repr__(self):
    return self._data

  def __str__(self):
    return str(self._data)

  def __getitem__(self, key):
    return self._data[key]

  def walk(self):
    for union in self._data:
      yield union

  def load(self):
    try:
      with open(Unions.FUNIONS(), 'r') as fd:
        self._data = json.loads(fd.read())
    except:
      pass

  def save(self):
    with open(Unions.FUNIONS(), 'w') as fd:
      fd.write(json.dumps(self._data, indent=2, separators=(", ", ": ")) + '\n')

  def _change_level(self, name, level):
    level = int(level)
    is_level_not_uniq = any(level == self._data[name]['level'] for name in self._data)
    if is_level_not_uniq:
      raise ValueError("'"+name+"' level '"+str(level)+"' is not uniq")
    else:
      self._data[name] = {"level": level}

  def new(self, name, level = None):
    if self._data.get(name):
      raise ValueError("union '"+name+"' already exists")
    else:
      if not level:
        level = 0
        for u in self._data:
          if level < self._data[u]['level']:
            level = self._data[u]['level']
        else:
          level = level + 1
      self._change_level(name, level)

  def get(self, name):
    return self._data.get(name)

  def delete(self, name):
    if not self._data.get(name):
      raise ValueError("can't delete '"+name+"', not exists")
    else:
      del self._data[name]

  def change_level(self, name, level):
    if not self._data.get(name):
      raise ValueError("can't change level for '"+name+"', not exists")
    else:
      self._change_level(name, level)

  def swap_levels(self, name1, name2):
    union1 = self._data.get(name1)
    union2 = self._data.get(name2)
    if not union1 or not union2:
      raise ValueError("can't swap union1("+(None == union1)+"), union2("+(None == union2)+")")
    else:
      tmp = union1['level']
      union1['level'] = union2['level']
      union2['level'] = tmp
