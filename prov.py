#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4
import tmp
import os

class RepoError(Exception):
  def __init__(self, repo, message):
    super().__init__(f"{message} [{repo.name()}]")

  #def __str__(self):
  #  return self.message

class RepoProvider:
  def provname(self):
    raise NotImplementedError()
    
  def connect(self, path):
    raise NotImplementedError()

  def disconnect(self):
    raise NotImplementedError()

  def is_connected(self):
    raise NotImplementedError()
    
  def urls(self):
    raise NotImplementedError()    

  def describe(self, rev):
    raise NotImplementedError()

  def is_rev_exists(self, rev_id):
    raise NotImplementedError()

  '''
  проверка наличия редакции в рамках заданных границ 
  (редакция находится в одной из разрешенных веток)
  '''
  def is_rev_in_bounds(self, rev, bounds):
    raise NotImplementedError()

  '''
  получение редакции, в которой изменялся path (или весь репо), 
  начиная от редакции rev_id;
  преобразование версии (короткий хэш, тэг и тд) в полную редакцию (хэш 40 символов)
  '''
  def rev_precise(self, rev_id, path = None):
    raise NotImplementedError()

  '''
  список файлов, которые были изменены в редакции
  '''
  def rev_files(self, rev_id):
    raise NotImplementedError()
  
  def rev_info(self, rev_id, with_files = False):
    raise NotImplementedError()
    
  '''
  выбрать из набора редакций rev_ids хронологически последнюю, но не позже 
  редакции relative_rev_id, если она задана.
  '''
  def rev_pick_last(self, rev_ids, relative_rev_id = None):
    raise NotImplementedError()

  def is_file_changed_in_rev(self, path, rev):
    raise NotImplementedError()

  '''
  проверка наличия присутствия в заданной редакции (именно присутствия, а не
  изменения)
  '''
  def is_file_in_rev(self, path, rev_id):
    raise NotImplementedError()

  def file_extract(self, rel_path, rev_id):
    raise NotImplementedError()

  def save_to_file(self, data):
    if not data:
      raise ValueError("No data to save")

    tmpfile_path = tmp.__tmp_path__ + 'prov/p-' + str(uuid4()) + '.dat'
    os.makedirs(os.path.dirname(tmpfile_path), exist_ok=True)
    try:
      with open(tmpfile_path, 'wb') as f:
        f.write(data)
    except:
      raise RepoError(self, f"failed to write temporary file '{tmpfile_path}'")
    return tmpfile_path 

  def rev_resolve(self, rev_id): # TODO: rename
    try:
      rev_id = self.rev_precise(rev_id)
    except:
      raise ValueError("Revision '"+rev_id+"' not exist")
      
    if not self.is_rev_in_bounds(rev_id):
      raise ValueError("Revision '"+rev_id+"' not in bounds")
      
    return rev_id
    
  def walk_rev(self, rev_id):
    raise NotImplementedError()
    
  def walk_diff(self, from_rev, to_rev):
    raise NotImplementedError()
