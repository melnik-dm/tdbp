#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import contextlib
from distutils.dir_util import copy_tree, remove_tree
import shutil
from colorama import Fore, Back, Style

import tmp
from repoman import RepoMan

# TODO: подумать над режимом работы "черновик", когда все команды, без использования drafting, будут попадать в черновик
# например, после вызова repo "diff --as-draft" включать режим, а после "draft --use" - отключать.
# нужно решить, как и где хранить признак работы режима (.repo, аналог .reporef).
# нужно решить, как выбирать имя черновика (автоматически или вручную)
# пока включен режим выводить об этом информацию при каждом запуске программы 

# TODO: возможно стоит перенести в другое место, например, в project
# relocate all project's repos that has relative ref-path
def project_relocate(origin_path):
  for repo in RepoMan.walk():
    if repo.is_binded():
      if not os.path.isabs(repo.path()):
        print("Relocate repo '"+repo.name()+"'")
        repo.rebind(origin_path + '/' + repo.path())
        print()
        
@contextlib.contextmanager
def remember_cwd(sandbox_path):
  origin_path= os.getcwd()
  os.makedirs(os.path.dirname(sandbox_path), exist_ok=True)
  copy_tree(origin_path, sandbox_path)
  os.chdir(sandbox_path)
  project_relocate(origin_path)
  try: 
    yield
  finally: 
    os.chdir(origin_path)
    #remove_tree(sandbox_path) #tmp и так очищается при завершении работы программы

# TODO: придумать расширение для черновика (например, tdbd - trace data base draft)
def replay(drafts, run_rtn, is_nonstop, is_need_remove):
  for filename in drafts:
    with open(filename, 'r') as fd:
      print(Style.BRIGHT + "DRAFT:", filename)
      print()
      for nr, line in enumerate(fd):
        line = line.strip(' ')
        line = line.rstrip(os.linesep).rstrip(' ')
        if not line:
          continue
        if line.startswith('#'): # comments
          continue
        args = line.split(' ')
        print(Style.BRIGHT + str(nr+1)+':', ' '.join(args), Style.RESET_ALL) 
        run_rtn(args, is_nonstop)
    if is_need_remove: 
      os.remove(filename)
    
def test(drafts, run_rtn, is_nonstop, is_need_remove):
  with remember_cwd(tmp.__tmp_path__ + '/draft/'):
    replay(drafts, run_rtn, is_nonstop, is_need_remove)
            
def drafting(cmd, run_rtn, draft):
  with remember_cwd(tmp.__tmp_path__ + '/drafting/'):
    args = cmd.split(' ')
    print(' '.join(args))
    run_rtn(args)
  if draft:
    with open(draft, 'a') as fd:
      fd.write(cmd + '\n')

