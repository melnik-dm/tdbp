#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from enum import IntEnum
from act_error import *
from repo import Repo
from repoman import RepoMan
from ci import *
from cid import ConfItemError, ConfItemId
from cit import ConfItemTrace
from colorama import Fore, Back, Style

'''
TODO: посчитать связи
- прямые (вниз)
- если прямые отсутствуют, значит непокрытые
- обратные (вверх)
- если обратные отсутствуют, значит производные

также оценить признак complete: 
- связи присутствуют, но не установлен complete
- связи присутствуют и установлен complete

помимо этого решить что делать с:
- системными требованиями (всегда производные) и исходным кодом (всегда без прямой связи)
- с файлами, содержащими внутренние метки (сам файл, как правило, не трассируется - трассируются только сами метки, а значит файл всегда без прямой связи)
- похожая ситуация с директориями, которые сейчас просто не учитываются (вероятно нужно запретить их связывать вообще)
'''

class StatContents(IntEnum):
  DERIVATIVES = 1 << 0
  UNIMPLEMENTED = 1 << 1
  UNCOMPLETED = 1 << 2
  ALL = (1 << 3) - 1
  
def is_trace_exist(ci_name):
  has_fw = False
  has_bw = False
  ci = ConfItem(ci_name)
  if ci.has_links(): # у CI есть связи 
    # TODO: проверить complete
    for link in ci.links():
      if has_fw and has_bw:
        break
      lci = ConfItem(link.id())
      if ci.level() < lci.level():
        has_fw = True
      else:
        has_bw = True
  else: # у CI нет связей
    # производное и нереализованное
    # TODO: нужно также оценивать, есть ли уровень ниже, это важно для ИК, который ниже не может быть протрассирован
    # или для ТНУ, которые неявно трассируются на ИК. если это не учесть, то ТНУ или ИК будут производными, хотя это не так
    # возможно следует отслеживать complete, который будет учитываться даже при отсутствии связей вниз
    has_fw = False
    has_bw = False
  return has_fw, has_bw

def repo_walk_trace(repo):
  for file in repo.walk():
    has_fw, has_bw = is_trace_exist(file)
    yield file, has_fw, has_bw

def info(title, total, n):
  print(Fore.WHITE, title + ': ', str(round(n / total * 100, 1)) + '%', '(' + str(n), '/', str(total) + ')')

def show_stat(total, unimpl, derivative, contents):
  if total:
    if (contents & StatContents.DERIVATIVES):
      info('Derivatives', total, derivative)   
    if (contents & StatContents.UNIMPLEMENTED):
      info('Unimplemented', total, unimpl)      
  else:
    print(Fore.WHITE, 'none') 
      
def stat(repo, contents):
  print(Fore.WHITE)
  print("Stat for '"+repo.name()+"'")

  total = 0
  unimpl = 0
  derivative = 0  
  for file, has_fw, has_bw in repo_walk_trace(repo):
    total = total + 1
    if (contents & StatContents.UNIMPLEMENTED) and (not has_fw):
      print(Fore.RED, 'i', file)
      unimpl = unimpl + 1

    if (contents & StatContents.DERIVATIVES) and (not has_bw):
      print(Fore.YELLOW, 'd', file)
      derivative = derivative + 1

  show_stat(total, unimpl, derivative, contents);
    
  return total, unimpl, derivative

def action_stat(args):
  #print(args)

  if args.contents is None:
    contents = StatContents.ALL
  else:
    contents = int(0)
    for type in args.contents:
      contents = contents | type
  
  if args.target is None:
    for repo in RepoMan.walk():
      stat(repo, contents)
  else:
    args.target = args.target.rstrip('/')
    
    union_repos = [repo for repo in RepoMan.walk() if repo.union() == args.target]
    if len(union_repos) == 0:
      # target оказался хранилищем
      stat(RepoMan.get_ready(args.target), contents)
    else:
      # target оказался объединением
      total = 0
      unimpl = 0
      derivative = 0  
      for repo in union_repos: 
        repo_total, repo_unimpl, repo_derivative = stat(RepoMan.get_ready(repo.name()), contents)
        total = total + repo_total
        unimpl = unimpl + repo_unimpl
        derivative = derivative + repo_derivative
      print()
      print("Stat for '"+args.target+"'")
      show_stat(total, unimpl, derivative, contents)

