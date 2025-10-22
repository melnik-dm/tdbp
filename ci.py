#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from repo import Repo 
from repoman import RepoMan
from union import *
from cid import ConfItemId, ConfItemError
from cit import ConfItemTrace

class ConfItem:
  def __init__(self, raw_id, is_sandbox = False):
    self._cid = None
    self._repo = None
    self._cit = None
    self._level = None
    self._is_sandbox = is_sandbox
    
    self._cid = ConfItemId(raw_id) # TODO: добавить отбрасывание редакции?
    self._repo = RepoMan.get_ready(self._cid.repo())

  def repo(self):
    return self._repo

  '''
  может оказаться, что доступ к TD из CI не нужен, но нужны другие возможности CI
  '''
  def _td(self):
    if self._cit is None:
      self._cit = ConfItemTrace(self._cid.name(), self.is_sandbox())
    return self._cit

  def is_sandbox(self):
    return self._is_sandbox

  def name(self):
    return self._cid.name()

  def cid(self):
    '''
    if rev_id:
      resolved_rev_id = self.last_rev_with_changes(rev_id, True)
      if resolved_rev_id is None:
        raise ValueError("CI '"+ self._cid.name() +"' doesn't exist in '"+ rev_id +"'")
      return self._cid.new(resolved_rev_id)
    else:
      return self._cid
    '''
    return self._cid
    
  def sub(self, label):
    '''
    if rev_id:
      ci = ConfItem(self.cid().sub(label).name())
      resolved_rev_id = ci.last_rev_with_changes(rev_id, True)
      if resolved_rev_id is None:
        raise ValueError("CI '"+ ci.cid().name() +"' doesn't exist in '"+ rev_id +"'")
      return ci.cid().new(resolved_rev_id)
    else:
      return self._cid.sub(label)
    '''
    return self._cid.sub(label)
    
  def labels(self):
    labels = self._repo.file_labels(self._cid.rel_path())
    return labels
    
  def level(self):
    return self._repo.level()

  def contents(self, rev_id = None):
    return self._repo.file_contents(self._cid.rel_path(), rev_id)

  def brief_contents(self, rev_id = None):
    return self._repo.file_brief_contents(self._cid.rel_path(), ci.cid().label(), rev_id)

  '''
  путь до временного файла с содержимым ЕК в заданной редакции
  '''
  def contents_tmpfile_path(self, rev_id = None):
    return self._repo.file_extract(self._cid.rel_path(), rev_id)

  '''
  проверка наличия присутствия в заданной редакции (именно присутствия, а не
  изменения)
  '''
  def is_in_rev(self, rev_id = None):
    if self._cid.label():
      return self._repo.is_file_label_valid(self._cid.rel_path(), self._cid.label(), rev_id)
    else:
      return self._repo.is_file_in_rev(self._cid.rel_path(), rev_id)

  '''
  поиск последней редакции, в которой изменялся файл, начиная с from_rev_id
  '''
  def last_rev_with_changes(self, from_rev_id, is_need_bounds_check = False):
    if not from_rev_id:
      raise ValueError("empty from_rev_id")
  
    if is_need_bounds_check:
      # TODO: rev_id далее не используется
      rev_id = self._repo.rev_resolve(from_rev_id)
        
    label_exist = True
    if self._cid.label():
      label_exist = self._repo.is_file_label_valid(self._cid.rel_path(), self._cid.label(), from_rev_id)
      
    if not label_exist:
      return None
    else:
      return self._repo.rev_precise(from_rev_id, self._cid.rel_path())
    
  def has_links(self):
    return not self._td().is_pure()
    
  def links(self):
    for link in self._td().links():
      yield link
    
  def trace_add(self, ci):
    if not isinstance(ci, ConfItem):
      raise TypeError("added CI is not ConfItem")
  
    if self.level() == ci.level():
      raise ValueError("added CI '"+ci.cid().id()+"' has same level")
  
    if not self.is_in_rev():
      raise ValueError("target CI '"+self.cid().id()+"' not exist in repo")
      
    if not ci.is_in_rev():
      raise ValueError("added CI '"+ci.cid().id()+"' not exist in repo")
  
    # TODO: подумать над добавлением проверки allow/deny
  
    self._td().add(ci.cid())
    ci._td().add(self.cid())
    
  def trace_rem(self, ci):
    if not isinstance(ci, ConfItem):
      raise TypeError("removed CI is not ConfItem")

    self._td().rem(ci.cid())
    ci._td().rem(self.cid())
      
  def trace_clone(self, cloned_ci):
    if not isinstance(cloned_ci, ConfItem):
      raise TypeError("cloned CI is not ConfItem")
  
    if self._td().is_pure():
      raise ValueError("CI has no traces, can't clone")
  
    if not cloned_ci._td().is_pure():
      raise ConfItemError("CI '"+str(cloned_ci.cid())+"' already has trace, can't clone")
      
    added_links = self._td().links()
    for link in added_links:
      cloned_ci.trace_add(ConfItem(link.name()))
  
  def trace_reset(self):
    # проверять существование CI в хранилище не нужно
    if not self._td().is_pure():
      affected_links = self._td().links()
      self._td().clear()
      
      for link in affected_links:
        affected_cit = ConfItemTrace(link.name(), self.is_sandbox())
        affected_cit.rem(self.cid())

  def trace_walk(self):
    # TODO: подумать над применением enum вместо f/b
    for link in self._td().links():
      rci = ConfItem(link.name())
      if rci.level() > self.level():
        direction = 'f'
      else:
        direction = 'b'
      yield rci, direction

  '''
  TODO: работа с метками (label) требует уточнения
  сейчас все функции, определяющие редакцию для ЕК смотрят на сам файл, но не на
  его метку. таким образом, если файл изменился, но метка в нем не изменилась
  или вовсе была удалена, то это никак не отобразится.
  is_changed_in_rev, last_rev_with_changes
  '''
  '''
  def is_changed_in_rev(self, rev_id):
    label_exist = True
    if self._cid.label():
      label_exist = self._repo.is_ci_label_valid(self._cid.new(rev_id))
    return self._repo.is_file_changed_in_rev(self._cid.rel_path(), rev_id) and label_exist

  '''

