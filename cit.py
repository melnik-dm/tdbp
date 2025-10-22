#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from cid import ConfItemId, ConfItemError

'''
Текущий признак полноты покрытия предназначен только для одной ветви 
трассируемости. Таким образом, чтобы установить признак на обе ветви, 
необходимо создать два репозитория ссылающихся на один физический.
Например, для покрытия ТВУ в части реализации требуется отдельный
репозиторий проекта TDBP srs-impl, а для покрытия ТВУ в
части верификации также требуется отдельный репозиторий srs-ver.
Оба репозитория TDBP ссылаются на один репозиторий Git srs.
Если добавить группы и заменить текущий признак на имя группы, то возможно
использовать один репозиторий tdbp для одного репозитория git. 
ПРИМЕЧАНИЕ: под ветвями подразумевается разветвление процессов: разработка
и верификация.
'''
class Trace:
  def __init__(self):
    self._is_completed = False
    self._has_changed = False
    self._links = list() # list of ConfItemId

  def is_completed(self):
    return self._is_completed

  def complete(self, is_completed):
    self._is_completed = is_completed

  def has_changed(self):
    return self._has_changed
    
  def changed(self):
    self._has_changed = True

  def links(self):
    return self._links

  def is_empty(self):
    return False if self.links() else True

  def add(self, link):
    if link in self.links():
      raise ValueError("dup> " + str(link))
    else:
      self.links().append(link)
      self.changed()
    
  def rem(self, link):
    try:
      self.links().remove(link)
    except ValueError:
      raise ValueError("nop> " + str(link))
    else:
      self.changed()

  def clear(self):
    self.links().clear()
    self.changed()

'''
ConfItemTrace file structure (.td-file):

flags (completed, etc)
link1\n
link2\n
...
'''
class ConfItemTrace:
  def FEXT(): # FILE EXTENSION
    return '.td'

  # TODO: complete flag is '+' or word 'complete'?

  def __init__(self, ci_name, is_sandbox = False):
    self._is_sandbox = is_sandbox
    self._is_pure = True

    self._ci = ConfItemId(ci_name)
    self._path = ci_name + ConfItemTrace.FEXT()
    self._trace = Trace()
    
    self.load()

  def __del__(self):
    if not self._is_sandbox:
      self.save()

  def is_sandbox(self):
    return self._is_sandbox

  def is_pure(self):
    return self.trace().is_empty()
    
  def path(self):
    return self._path

  def trace(self):
    return self._trace

  def load(self):
    if (not (os.path.isfile(self.path())) or (0 == os.path.getsize(self.path()))):
      pass
    else:
      with open(self.path(), 'r') as fd: 
        flags = fd.readline() # TODO: обработать и сохранить флаги
        for line in fd:
          line = line.rstrip('\n' + ' ')
          if line:
            cid = ConfItemId(line)
            self.trace().links().append(cid)
        if not self.trace().is_empty():
          self._is_pure = False

  def save(self):
    if not self.trace().has_changed():
      return
      
    if self.is_sandbox():
      return
      
    os.makedirs(os.path.dirname(self.path()), exist_ok=True) # dirname возвращает пустую строку, если в path отсутствуют слэши, что не устраивает makedirs
    if self.trace().is_empty():
      if os.path.exists(self.path()):
        os.remove(self.path())
    else:
      with open(self.path(), 'w') as file:
        file.write('\n') # TODO: обработать и записать флаги
        line = '\n'.join(str(link) for link in self.trace().links())+'\n'
        file.write(line)

  def links(self):
    return self.trace().links().copy()

  # TODO: перенести в ConfItemId; либо в момент save сохранять только cid.name()
  def cid_truncate(self, cid):
    if cid.has_rev():
      print("warning: remove cid revision from '" + str(cid) + "'")
    return ConfItemId(cid.name())  

  def add(self, added_link):
    if not isinstance(added_link, ConfItemId):
      raise TypeError("link '"+added_link+"' of 'added_links' for 'add_all' is not ConfItemId")
    added_link = self.cid_truncate(added_link)
    self.trace().add(added_link)

  def rem(self, removed_link):
    if not isinstance(removed_link, ConfItemId):
      raise TypeError("link '"+link+"' of 'removed_links' for 'rem' is not ConfItemId")
    removed_link = self.cid_truncate(removed_link)
    self.trace().rem(removed_link)
    
  def clear(self):
    self.trace().clear()
    
  '''
  def complete(self, rev, is_completed = True):
    revlinks = self.get(rev)
    if revlinks is None:
      raise ValueError("missing revision '"+rev+"' in 'complete'")
    else:
      if revlinks.is_completed() != is_completed:
        revlinks.complete(is_completed)
        self._has_changed = True
  
  def dump(self, revlinks):
    rev = revlinks.revision()
    links = revlinks.links()
    completed = ConfItemTrace.CR() if revlinks.is_completed() else ''
    print(self._id_title(rev) + completed)
    if links:
      print('\n'.join(str(link) for link in links))
    print()

  def show(self, rev = ''):
    if not rev:
      for rl in self._data:
        self.dump(rl)    
    else:
      rl = self.get(rev)
      if rl is not None:
        self.dump(rl)
  '''
