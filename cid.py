#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import repo_path

class ConfItemError(Exception):
  def __init__(self, message):
    self.message = message

class ConfItemId:
  # <CI_NAME>#<LABEL>@<CI_REVISION>

  def RT(): # REVISION TAG
    return '@'
  
  def LT(): # LABEL TAG
    return '#'

  def ANY_REV(): # для связывания ЕК без редакции (или любой редакции) предусмотрена специальная редакция
    return '*'

  def is_id_has_rev(ci_id):
    return (not ci_id.endswith(ConfItemId.RT()) and (ConfItemId.RT() in ci_id))

  def make_id(name, rev):
    return (name+ConfItemId.RT()+rev)

  def __repr__(self):
    return self.id()

  def __str__(self):
    return self.id()

  def __eq__(self, other): # unhashable, otherwise need __hash__ method
    if not isinstance(other, ConfItemId):
      return NotImplemented
    return self.id() == other.id()    

  def __init__(self, ci_id):
    self._name = ''
    self._path = ''
    self._label = ''
    self._rev = ''
    self._id = ''
    self._repo = None

    if not ci_id:
      raise ValueError("'ci_id' for 'CI' is empty")

    # Windows
    #if os.sep == '\\': ci_id = ci_id.replace('\\', repo_path.psep)
    #if ci_id.startswith('./') or ci_id.startswith('.\\'): ci_id = ci_id[2:]

    if not repo_path.psep in ci_id:
      raise ValueError("no repo in ci_id '"+ci_id+"' specified")
    self._repo = ci_id.split(repo_path.psep)[0]

    ci_id = ci_id.strip()
    ci_id = ci_id.split(ConfItemId.RT())

    if (len(ci_id) >= 1):
      if not ci_id[0]:
        raise ValueError("'ci_id' has empty name for 'CI'")
      else:
        self._name = ci_id[0]

    if (2 == len(ci_id)):
      self._rev = ci_id[1]

    if self.has_rev():
      self._id = self.id(self._rev)
    else:
      self._id = self.name()

    path_label = self.name().split(ConfItemId.LT(), 1)
    self._path = path_label[0]
    if len(path_label) > 1:
      self._label = path_label[1]

  def new(self, rev):
    return ConfItemId(self.id(rev))

  def sub(self, label, rev = ''):
    if self.has_label():
      raise ValueError(self.name(), "already has label")
    if not rev: rev = self.rev()
    return ConfItemId(ConfItemId.make_id(self.name() + ConfItemId.LT() + label, rev))

  '''
  path, label, rev (could be custom)
  '''
  def id(self, rev = ''): 
    if not rev:
      return self._id
    else:
      return ConfItemId.make_id(self._name, rev)

  '''
  path, rev (could be custom) (without label)
  '''
  def id_wo_label(self, rev = ''):
    if not rev:
      return self._id
    else:
      return ConfItemId.make_id(self._path, rev)

  '''
  path and label (without rev)
  '''
  def name(self):
    return self._name

  '''
  path (without label and rev)
  '''
  def path(self):
    return self._path

  '''
  path without repo prefix (without label and rev) 
  '''
  def rel_path(self):
    return self._path.split(repo_path.psep, 1)[1]

  def extension(self):
    dir = self.path().rfind('/')
    assert dir != -1
    ext = self.path().find('.', dir)
    # or dir+1 == ext - ? .bashrc
    if ext == -1 or len(self.path())-1 == ext:
      return ''
    else:
      return self.path()[ext+1:]

  def repo(self):
    return self._repo

  def label(self):
    return self._label

  def has_label(self):
    return True if self.label() else False

  def rev(self):
    return self._rev

  def has_rev(self):
    if self._rev: return True
    else: return False

  def has_any_rev(self):
    if (ConfItemId.ANY_REV() == self.rev()):
      return True
    else:
      return False
