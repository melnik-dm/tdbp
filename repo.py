#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import fnmatch
import json
from cid import ConfItemId
from cit import ConfItemTrace
import tmp
from prov import RepoProvider, RepoError
from union import Unions
from repo_labels import RepoLabels
from repo_briefers import RepoBriefers
import project
import repo_path

'''
import contextlib
# сменит путь на path (если задан), выполнит do() и вернет путь на прежний
# with remember_cwd(path):
#   do()
@contextlib.contextmanager
def remember_cwd(newdir = None):
    curdir= os.getcwd()
    if newdir is not None:
      os.chdir(newdir)
    try: 
      yield
    finally: 
      os.chdir(curdir)
'''

# TODO: подумать, как убрать постоянный вызов _repo._sync_settings(); has_changes + sync в деструкторе?
# проверить, когда будет вызываться деструктор при переходе на RepoMan
class RepoBounds:
  def CFG_SECTION():
    return 'bounds'
  
  def __init__(self, repo):
    self._repo = repo

  def add(self, bound):
    if self._repo.is_exists():
      if bound in self._repo.settings['bounds']:
        print("ERROR: bound '" + bound + "' already exists")
      else:
        self._repo.settings['bounds'].append(bound)
        self._repo._sync_settings()

  def remove(self, bound):
    if self._repo.is_exists():
      if bound in self._repo.settings['bounds']:
        self._repo.settings['bounds'].remove(bound)
        self._repo._sync_settings()
      else:
        print("ERROR: bound does not exists: " + bound)

  def show(self):
    if self._repo.is_exists():
      print(self._repo.settings['bounds'])
      print('Total: ' + str(len(self._repo.settings['bounds'])))

  def clear(self):
    if self._repo.is_exists():
      self._repo.settings['bounds'] = []
      self._repo._sync_settings()

'''
TODO: рассмотреть возможность добавления алиасов к поддиректориям 
репозитория (сейчас только корневая директория)

TODO: пронаследовать Repo от RepoLabels и RepoBounds? могут быть пересечения по именам методов? почитать про множественное наследование
'''
class Repo(RepoProvider):
  def FREPO():
    return '.repo'

  def FREPOREF():
    return '.reporef'

  def FREPOALLOW():
    return '.repoallow'

  def FREPODENY():
    return '.repodeny'

  def __init__(self, name):
    self._name = name
    self.def_settings = { \
      RepoBounds.CFG_SECTION(): [], \
      'union': self.name(), \
      RepoLabels.CFG_SECTION(): {}, \
      'label_policy': "ALL", \
      RepoBriefers.CFG_SECTION(): {} \
      }
    self.settings = {}
    self._path = None
    self.bounds = RepoBounds(self)
    self.labels = RepoLabels(self)
    self.briefers = RepoBriefers(self)
    self._allow = list()
    self._deny = list()
    self._level = None

    if self.is_exists():
      self._load_settings()

    if self.is_binded():
      self._load_ref()
      try:
        self.connect(self.path())
      except:
        print("Can't connect to repo '" + self.name() + "' ["+self.path()+"]")

  def name(self):
    return self._name

  def path(self):
    return self._path

  def description(self):
    return self.settings['desc']

  # в текущем варианте репо просто хранит идентификатор объединения, ничего не зная о самом объединении, в частности, не зная о его корректности
  def union(self):
    return self.settings.get('union')

  def union_reset(self, new_union = None): 
    if not new_union:
      new_union = self.name()
    self.settings['union'] = new_union
    self._sync_settings()

  def desc_update(self, desc):
    self.settings['desc'] = desc
    self._sync_settings()    

  def _params(name):
    return name + '/' + project.PRJ_FILE_NAME() + '/'

  def drop(self):
    try:
      os.remove(self._handle())
      os.remove(self._allow_handle())
      os.remove(self._deny_handle())
      os.remove(self._ref_handle())
    except:
      pass
    os.rmdir(Repo._params(self.name()))

  def _handle(self):
    return Repo._params(self.name()) + Repo.FREPO()

  def _ref_handle(self):
    return Repo._params(self.name()) + Repo.FREPOREF()

  def _allow_handle(self):
    return Repo._params(self.name()) + Repo.FREPOALLOW()

  def _deny_handle(self):
    return Repo._params(self.name()) + Repo.FREPODENY()

  def is_exists(self):
    return os.path.isfile(self._handle())

  def is_binded(self):
    return os.path.isfile(self._ref_handle())

  def has_rev(self):
    if self.settings.get('revision') is not None:
      return True
    else:
      return False

  def rev_get(self):
    return self.settings['revision']

  def rev_set(self, rev):
    if not self.is_connected():
      raise RepoError(self, "Repo not connected")
  
    rev = self.rev_precise(rev)
    self.settings['revision'] = rev
    self._sync_settings()
    
  def rev_reset(self):
    del self.settings['revision']
    self._sync_settings()

  def version(self):
    try:
      ver = self.describe(self.rev_get())
    except:
      ver = 'null'
    return ver

  def ready(self):
    return (self.is_exists() and self.is_binded() and self.is_connected() and self.has_rev())
    
  def ready_info(self):
    print("Exists ("+str(self.is_exists())+")")
    print("Binded ("+str(self.is_binded())+")")
    print("Revision set ("+str(self.has_rev())+")")
    print("Connected ("+str(self.is_connected())+")")

  def _load_patterns(file):
    patterns = list()
    with open(file, 'r') as fd:
      for line in fd: 
        line = line.rstrip(os.linesep + ' ')
        if line:
          patterns.append(line)
    return patterns

  def _load_settings(self):
    with open(self._handle(), 'r') as fd:
      settings = json.loads(fd.read())
      self.settings = {**self.def_settings, **settings}
        
    try:
      self._allow = Repo._load_patterns(self._allow_handle())
      self._deny = Repo._load_patterns(self._deny_handle())
    except FileNotFoundError:
      pass

  def _sync_settings(self):
    os.makedirs(os.path.dirname(self._handle()), exist_ok=True)
    with open(self._handle(), 'w') as fd:
      fd.write(json.dumps(self.settings, indent=2, separators=(", ", ": ")) + '\n')

  def _load_ref(self):
    with open(self._ref_handle(), 'r') as fd:
      self._path = fd.readlines()[0].rstrip('\n/')
      #print(self.path(), os.path.abspath(self.path()))

  def _save_ref(self, path):
    with open(self._ref_handle(), 'w') as fd:
      fd.write(path)

  def _drop_ref(self):
    os.remove(self._ref_handle())
    self._path = None

  def _save_def_patterns(self):
    with open(self._allow_handle(), 'w') as fd:
      fd.write('*')
      
    with open(self._deny_handle(), 'w') as fd:
      pass

  def __create(self, provider, description):
    self.settings = self.def_settings.copy()
    self.settings['provider'] = provider
    self.settings['desc'] = description
    self.settings['union'] = self.name()

    try:
      self._sync_settings()
      self._save_def_patterns()
      print("New repo '" + self.name() + "'")
    except:
      self.settings = None
      raise

  def bind(self, path):
    if not self.is_exists():
      raise RepoError(self, "Repo does not exists")

    if self.is_binded():
      raise RepoError(self, "Repo already binded")

    expanded_path = os.path.expanduser(path)

    self.connect(expanded_path)
    self._save_ref(expanded_path)
    self._load_ref()
    print("New reporef '" + self.name() + "': " + self.path())

  def unbind(self):
    if not self.is_exists():
      raise RepoError(self, "Repo does not exists")
  
    if not self.is_binded():
      raise RepoError(self, "Repo not bound yet")
      
    if self.is_connected():
      self.disconnect()
    
    self._drop_ref()

  def rebind(self, path):
    self.unbind() 
    self.bind(path)

  def allow(self):
    return self._allow

  def deny(self):
    return self._deny

  def level(self):
    if self._level is None:
      self._level = int(Unions()[self.union()]['level']) 
    return self._level

  def labels_policy(self):
    return self.settings['label_policy']
    
  def labels_policy_update(self, policy):
    self.settings['label_policy'] = policy
    self._sync_settings()

  # сейчас: если файл поддерживает метки, то сам файл не выдается; 
  def labels_expand(self, files, rev_id):
    sub_files = list()
    remain_files = list()
    for file in files:
      if self.can_file_contain_labels(file):
        cid = ConfItemId(file)
        labels = self.file_labels(cid.rel_path(), rev_id)
        for label in labels:
          file = cid.sub(label).name()
          sub_files.append(file)
      else:
        remain_files.append(file)  
    return remain_files, sub_files

  def pattern_filter(self, files):
    # если хотя бы один паттерн подходит, то файл исключается
    for pattern in self.deny():
      files = [file for file in files if not fnmatch.fnmatch(file, pattern)]
    # если хотя бы один паттерн подходит, то файл остается
    filtered_files = list()
    for file in files:
      for pattern in self.allow():
        if fnmatch.fnmatch(file, pattern):
          filtered_files.append(file)
          break  
    return filtered_files

  def subfiles_policy_filter(self, subfiles):
    if self.labels_policy() == "TRACED":
      filtered_subfiles = list()
      for file in subfiles:
        if os.path.exists(file + ConfItemTrace.FEXT()):
          filtered_subfiles.append(file)
      return filtered_subfiles
    else:
      return subfiles

  def walk(self):
    for file in self.walk_rev(self.rev_get()):#os.walk(self.path()):
      files = list([file])
      files = self.pattern_filter(files)
      files, subfiles = self.labels_expand(files, self.rev_get())
      if subfiles: 
        subfiles = self.pattern_filter(subfiles)
        subfiles = self.subfiles_policy_filter(subfiles)
      for file in files:
        yield file
      for file in subfiles:
        yield file

  def walk_traced(self, path=''):
    if path:
      path = self.name()+repo_path.psep+path
    else:
      path = self.name()
    for root, dirs, files in os.walk(path):
      for file in files: 
        FEXT = ConfItemTrace.FEXT()
        if file.endswith(FEXT):
          yield repo_path.psep.join(root.split(repo_path.psep))+repo_path.psep+file[:-len(FEXT)]

  # TODO: добавить обработку (expand old_rev, new_rev) файлов с метками
  def walk_changed(self, new_rev):
    for file, status in self.walk_diff(self.rev_get(), new_rev):
      #yield file, status
      files = list([file])
      files = self.pattern_filter(files)
      for file in files:
        yield file, status

  # LABELS

  def is_file_label_valid(self, rel_filepath, label, rev_id = None):
    if rev_id is None:
      rev_id = self.rev_get()

    if not self.can_file_contain_labels(rel_filepath):
      raise ValueError("'" + rel_filepath +"' can't contain labels")

    labels = self.file_labels(rel_filepath, rev_id)
    if label in labels:
      return True
    else:
      return False

  def can_file_contain_labels(self, rel_filepath):
    handler = self.labels.find_label_handler(rel_filepath)
    if handler is not None:
      return True
    else:
      return False
    
  def file_labels(self, rel_filepath, rev_id = None):
    if rev_id is None:
      rev_id = self.rev_get()
  
    labels = list()
    tmp_labels_path = tmp.__tmp_path__ + 'labelscache/' + ConfItemId(self.name() + '/' + rel_filepath).id(rev_id)
    if os.path.exists(tmp_labels_path):
      with open(tmp_labels_path, 'r') as fd:
        for line in fd: 
          labels.append(line.rstrip(os.linesep + ' '))
    else:
      handler = self.labels.find_label_handler(rel_filepath)
      if handler is not None:
        tmpfile_path = self.file_extract(rel_filepath, rev_id)
        if not tmpfile_path:
          raise RepoError(self, "label scanning couldn't be completed")
          
        labels = handler.scan(tmpfile_path)
        os.makedirs(os.path.dirname(tmp_labels_path), exist_ok=True)
        with open(tmp_labels_path, 'w') as fd: 
          for label in labels:
            fd.write(label)
            fd.write(os.linesep)
          
    return labels
    
  def file_contents(self, rel_filepath, rev_id = None):
    tmp_filepath = self.file_extract(rel_filepath, rev_id)
    with open(tmp_filepath, 'r') as fd:
      data = fd.read()
      return data
        
  def file_brief_contents(self, rel_filepath, label, rev_id = None):
    handler = self.briefers.find_suitable(rel_filepath)
    if not handler:
      return ''
      
    tmp_filepath = self.file_extract(rel_filepath, rev_id)
    brief = handler.parse(tmp_filepath, label)

    return brief

