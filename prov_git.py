#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pygit2
import repo_path
from time import time, ctime
from repo import Repo
from prov import RepoProvider, RepoError
from packaging.version import Version

if Version(pygit2.__version__) < Version("1.15.0"):
  GIT_OBJ_TAG = pygit2.GIT_OBJ_TAG
  GIT_OBJ_COMMIT = pygit2.GIT_OBJ_COMMIT
else:
  GIT_OBJ_TAG = pygit2.GIT_OBJECT_TAG
  GIT_OBJ_COMMIT = pygit2.GIT_OBJECT_COMMIT

class RepoGit(Repo):
  def __init__(self, name):
    self._desc = None
    Repo.__init__(self, name)

  def provname(self):
    return 'Git'

  def is_connected(self):
    return (not (self._desc == None))

  def connect(self, path):
    try:
      self._desc = pygit2.Repository(path)
    except pygit2.GitError as err:
      raise ValueError(err)

  def disconnect(self):
    del self._desc
    self._desc = None

  def urls(self):
    if not self.is_connected():
      raise RepoError(self, "Repo not connected")
  
    for remote in self._desc.remotes:
      yield str(remote.name + ' ' + remote.url) #print(remote.name, remote.url)

  def describe(self, rev):
    return self._desc.describe(committish=rev)

  def _revparse(self, rev):
    try:
      obj = self._desc.revparse_single(rev)
    except:
      raise RepoError(self, f"Bad revision '{rev}'")
    else:
      return obj

  '''
  Проверяет наличие объекта path для редакции, на которую указывает rev.
  Под объектом подразумевается директория или файл.
  Поиск осуществляется среди всех файлов (не только тех, что были изменены
  в редакции)
  '''
  def _has_path_in_rev(self, path, rev_id):
    has_path = False
    rev = self._revparse(rev_id)
    if rev.type == GIT_OBJ_TAG:
      raise ValueError("passed tag, not commit")
    try:
      obj = rev.tree[path]
    except:
      has_path = False
    else:
      has_path = True
    return has_path

  def is_file_in_rev(self, path, rev_id):
    if rev_id is None:
      rev_id = self.settings['revision']
    return self._has_path_in_rev(path, rev_id)

  '''
  Проверяет наличие объекта path для редакции, на которую указывает rev.
  Под объектом подразумевается директория или файл.
  Поиск осуществляется только среди объектов, измененных в этой редакции.
  Поиск осуществляется для всех родителей редакции rev.
  '''
  def _has_path_in_diff(self, rev, path):
    has_path = False
    commit = rev
    if len(commit.parents):
      for parent in commit.parents:
        diff = self._desc.diff(parent, commit)
        for e in diff:
          if e.delta.new_file.path.startswith(path): # if path == e.delta.new_file.path: 
            has_path = True
            break
          else:
            continue
          break;
    else:
      try:
        obj = commit.tree[path]
      except:
        has_path = False
      else:
        has_path = True
    return has_path

  def is_file_changed_in_rev(self, path, rev_id):
    is_changed = False
    rev = self._revparse(rev_id)
    if rev.type == GIT_OBJ_COMMIT:
      is_changed = self._has_path_in_diff(rev, path)
    else:
      raise TypeError("passed not commit")

    return is_changed

  def is_rev_exists(self, rev_id = None):
    if rev_id is None:
      rev_id = self.settings['revision']
    try:
      self._revparse(rev_id)
      return True
    except:
      return False
          
  def is_rev_in_bounds(self, rev_id = None):
    if rev_id is None:
      rev_id = self.settings['revision']
  
    if not self.is_rev_exists(rev_id):
      return False
  
    bounds = self.settings['bounds']
    
    is_in_bounds = True
    if bounds:
      rev_id = rev_id.strip(' \n').rstrip(' \n')
      if not list(set(bounds) & set(self._desc.branches.with_commit(rev_id))):
        is_in_bounds = False
    return is_in_bounds

  '''
  Получение идентификатора комита, в котором изменялся файл filename, начиная с
  редакции from_rev. Используется для конвертирования тэгов, коротких хэшей, 
  хэшей всего репозитория, указателя HEAD в полный хэш для конкретного файла или
  директории.
  Аналог git rev-list -1 <from_rev> <path>

  https://stackoverflow.com/questions/13293052/pygit2-blob-history
  '''
  # TODO: выбрать сортировку (https://git-scm.com/docs/git-log) GIT_SORT_: NONE, TIME, REVERSE, TOPOLOGICAL
  # TODO: достаточно долгая операция
  def _commit_with_file_change(self, from_commit, filename):
    last_commit = None
    last_oid = None
    for commit in self._desc.walk(from_commit.oid, pygit2.GIT_SORT_NONE): # перебор всех комитов в хронологическом порядке, начиная с самого нового
      #print(commit.oid, ':', commit.message) # commit.oid - это хэш комита
      try:
        oid = commit.tree[filename].oid
      except: # filename отсутствует (в комите commit.oid)
        break # файл отсутствует в стартовом комите, либо найден комит создания файла
      else: # filename присутствует (в комите commit.oid)
        has_changed = (oid != last_oid and last_commit)
        if has_changed:
          break
        last_oid = oid

      last_commit = commit

    return str(last_commit.oid) if last_commit else None  

  def rev_precise(self, rev_id, path = None):
    obj = self._revparse(rev_id)
    if obj.type == GIT_OBJ_TAG:
      obj = self._revparse(str(obj.target))
      
    if path is not None:
      return self._commit_with_file_change(obj, path)
    else:
      return str(obj.oid)

  def file_extract(self, rel_path, rev_id = None):
    if rev_id is None:
      rev_id = self.rev_get()
    data = self._revparse(rev_id).tree[rel_path].data
    return RepoProvider.save_to_file(self, data)

  def rev_files(self, rev):
    files = list()
    commit = self._revparse(rev)
    if len(commit.parents):
      for parent in commit.parents:
        diff = self._desc.diff(parent, commit)
        for e in diff:
          files.append(e.delta.new_file.path)
    files = [str(self.name() + repo_path.psep + file) for file in files]
    return files

  # TODO: добавить обработку rename (сейчас при rename флаги D и A, хотя должен быть R?)
  def walk_diff(self, from_rev, to_rev):
    cfrom = self.rev_precise(from_rev)
    cto = self.rev_precise(to_rev)
    diff = self._desc.diff(cfrom, cto)
    for e in diff:
      file = self.name() + '/' + e.delta.new_file.path
      # TODO: https://libgit2.org/libgit2/#v0.18.0/type/git_delta_t
      # https://github.com/libgit2/libgit2/blob/v0.18.0/include/git2/diff.h#L163-173
      # https://www.pygit2.org/diff.html
      #e.delta.status
      #e.delta.status_char()
      yield file, e.delta.status_char()

  def rev_info(self, rev, with_files = False):
    commit = self._revparse(rev)
    print(rev, ctime(commit.commit_time))
    print("Author: " + commit.author.name, ctime(commit.author.time))
    print("Committer: " + commit.committer.name, ctime(commit.committer.time))
    if with_files:
      files = self.rev_files(rev)
      print(files)
    print()

  def rev_pick_last(self, commit_ids, relative_commit_id = None):
    last_commit = None
    relative_commit = None
    if relative_commit_id:
      relative_commit = self._revparse(relative_commit_id)
    for cid in commit_ids:
      commit = self._revparse(cid)
      if (not relative_commit or relative_commit.commit_time > commit.commit_time):
        if (not last_commit or commit.commit_time > last_commit.commit_time):
          last_commit = commit
    return str(last_commit.oid) if last_commit else None
    
  def walk_rev(self, rev_id):
    if not self.is_connected():
      raise RepoError(self, "Repo not connected")
  
    def parse_tree(tree, path = self.name()):
      for obj in tree:
        if obj.type_str == 'tree':
          yield from parse_tree(list(obj), path + '/' + obj.name)
        elif obj.type_str == 'blob':
          yield (path + '/' + obj.name)
        else:
          continue#raise TypeError(obj.type_str)
  
    obj = self._revparse(rev_id)
    if obj.type == GIT_OBJ_TAG:
      obj = self._revparse(str(obj.target))
    for file in parse_tree(obj.tree):
      yield file
    
  
  '''
  #Печать дерева файлов комита
  #commit = repo.revparse_single(rev)
  #git_tree_print(commit.tree)
  def git_tree_print(tree, path = '.'):
    for obj in tree:
      if obj.type_str == 'tree':
        RepoGit.git_tree_print(list(obj), path + '/' + obj.name)
      else:
        print(path + '/' + obj.name)
  '''
    
  '''
  
  # _commit_with_file_change: поддержка изменений filemode
    last_commit = None
    last_blob = None
    for commit in self._desc.walk(from_commit.oid, pygit2.GIT_SORT_NONE): # перебор всех комитов в хронологическом порядке, начиная с самого нового
      #print(commit.oid, ':', commit.message) # commit.oid - это хэш комита
      try:
        blob = commit.tree[filename]
      except: # filename отсутствует (в комите commit.oid)
        break # файл отсутствует в стартовом комите, либо найден комит создания файла
      else: # filename присутствует (в комите commit.oid)
        has_changed = (last_commit != None and (blob.oid != last_blob.oid or blob.filemode != last_blob.filemode))
        if has_changed:
          break
        last_blob = blob

      last_commit = commit

    return str(last_commit.oid) if last_commit else None
    '''
