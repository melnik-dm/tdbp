#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import shutil
from colorama import Fore, Back, Style

from repo import *
from repoman import RepoMan
from act_error import *
from ci import *
from cid import ConfItemError, ConfItemId
from cit import ConfItemTrace
from union import Unions
from act_label import *
from act_briefer import *

# TODO: подумать, где и как хранить сам адрес, где хранится репо, чтобы работать напрямую с ним, без reporef
# или чтобы сравнивать при reporef адрес привязываемого репо с тем, что задан

def action_repo_new(name, provider, desc):
  union = Unions().get(name)
  if union:
    raise ActionError("union name '"+name+"' is busy (probably already exists)")

  repo = RepoMan.new(name, provider, desc)
  Unions().new(name)

def repo_clear(repo):
  for file in repo.walk_traced():
    ci = ConfItem(file)
    ci.trace_reset()

def action_repo_delete(name):
  try:
    repo = RepoMan.get(name)
  except Exception as e:
    print(e)
  else:
    repo_clear(repo)

    Unions().delete(repo.name()) 

    repo.drop()
  # после предыдущих действий остается пустое дерево директорий
  # чтобы его удалить, можно воспользоваться функционалом shutil
  # однако безопаснее удалять через os.*
  #shutil.rmtree(repo.name())

def action_repo_clear(name):
  try:
    repo = RepoMan.get(name)
  except Exception as e:
    print(e)
  else:
    repo_clear(repo)

def action_repo_url(name):
  for url in RepoMan.get(name).urls():
    print(url)

def action_repo_ref(args):
  RepoMan.get(args.repo).bind(args.path)

def action_repo_unref(args):
  RepoMan.get(args.repo).unbind()
  
def action_repo_reref(args):
  RepoMan.get(args.repo).rebind(args.path)

def action_repo_desc(args):
  RepoMan.get(args.repo).desc_update(args.text)

def action_repo_bounds_add(args):
  RepoMan.get(args.repo).bounds.add(args.add)

def action_repo_bounds_remove(args):
  RepoMan.get(args.repo).bounds.remove(args.remove)

def action_repo_bounds_show(args):
  RepoMan.get(args.repo).bounds.show()

def action_repo_bounds_clear(args):
  RepoMan.get(args.repo).bounds.clear()

def action_repo_union_set(repo_name, union_name):
  if any(union_name == repo.name() for repo in RepoMan.walk()):
    raise ActionError("union-repo could be set only in 'reset' command")

  repo = RepoMan.get(repo_name)
  union = Unions().get(union_name)
  if not union:
    raise ActionError("union("+str(None != union)+") does not exist")

  repo.union_reset(union_name) 
  print("Repo '"+repo.name()+"' now in union '"+repo.union()+"':", union)

def action_repo_union_reset(repo_name):
  repo = RepoMan.get(repo_name)

  repo.union_reset()
  union = Unions()[repo.union()]
  print("Repo '"+repo.name()+"' now is union-repo:", union)

def action_repo_union_show(repo_name):
  repo = RepoMan.get(repo_name)
  union = Unions().get(repo.union())
  print("Repo '"+repo.name()+"' consists in union '"+str(repo.union())+"':", str(union))
  
# REV
  
def repo_rev(repo_name, rev_id = None):
  repo = RepoMan.get_ready(repo_name)
  if rev_id is None:
    rev_id = repo.rev_get() 
  rev = repo.rev_precise(rev_id)
  return rev, repo.is_rev_in_bounds(rev)
  
def repo_check_rev(repo_name, rev_id = None):
  try:
    rev, is_in_bounds = repo_rev(repo_name, rev_id)
  except Exception as e:
    print(Fore.RED, e, sep='')
  else:
    print(rev)
    if is_in_bounds:
      print(Fore.GREEN + "IN BOUNDS")
    else:
      print(Fore.YELLOW + "NOT IN BOUNDS")
  
def action_repo_rev_set(repo_name, rev):
  repo = RepoMan.get(repo_name)
  repo.rev_set(rev)
  repo_check_rev(repo_name)
  
def action_repo_rev_reset(repo_name):
  repo = RepoMan.get_ready(repo_name)
  repo.rev_reset()
  
def action_repo_rev_get(repo_name):
  repo_check_rev(repo_name)
    
def action_repo_rev_check(repo_name):
  repo_check_rev(repo_name)
    
def action_repo_rev_resolve(repo_name, rev_id):
  repo_check_rev(repo_name, rev_id)

def action_repo_diff(repo_name, rev):
  repo = RepoMan.get(repo_name)
  for file, status in repo.walk_changed(rev):
    ci = ConfItem(file)
    if status == 'D':
      print(Fore.RED, end='')
    elif status == 'A':
      print(Fore.GREEN, end='')
    elif status == 'M':
      print(Fore.YELLOW, end='')
    else:
      print(Fore.WHITE, end='')
    print(status, ci.cid(), sep='   ')
      
def action_repo_diff_draft(repo_name, rev):
  repo = RepoMan.get(repo_name)
  print('# A - added, D - deleted, M - modified')
  print('#')
  print("# don't forget to replace this command with 'repo rev --set <HEAD~1 (if CI and TD in same repo) or HEAD (otherwise)> "+repo_name+"'")
  print("repo rev --reset", repo_name)
  print()
  for file, status in repo.walk_changed(rev):
    ci = ConfItem(file)
    print('#', status)
    print("link --reset", ci.name())
    if ci.has_links():
      link_cmd = "link --add "
      link_cmd = link_cmd + ci.name()
      for link in ci.links():
        print(link_cmd, link.name())
    print()
    
def action_repo_ls(repo_name):
  repo = RepoMan.get(repo_name)
  total = 0
  for file in repo.walk():
    total = total + 1
    ci = ConfItem(file)
    if ci.has_links():
      print(Fore.GREEN, ci.name())
    else:
      print(Fore.RESET, ci.name())
  print(Fore.RESET)
  print('Total:', total)
    
# TODO: возможно стоит это сделать вариантом экспорта
# TODO: также нужна поддержка для объединений
def action_repo_draft(repo_name):
  repo = RepoMan.get_ready(repo_name)
  filename = repo.name()+'.draft'
  with open(filename, 'w') as fd:
    line = str()
    line = '# Repo URLs: '
    fd.write(line)
    for url in repo.urls():
      line = url + ';'
      fd.write(line)
    fd.write('\n\n')
    line = "repo rev --set " + repo.rev_get() + " " + repo_name
    fd.write(line)
    fd.write('\n\n')
    for file in repo.walk_traced():
      ci = ConfItem(file)
      line = "link --reset " + ci.name()
      fd.write(line)
      fd.write('\n')
      link_cmd = "link --add " + ci.name()
      for link in ci.links():
        line = link_cmd + ' ' + link.name()
        fd.write(line)
        fd.write('\n')
      fd.write('\n')
  print(f"Successfully drafted to '{filename}'".format(filename))

def repo_info(repo):
    print(repo.name())
    if repo.is_exists():
      print(f'  provider: {repo.provname()}')
      print(f'  desc: {repo.description()}')
      print(f'  union: {repo.union()}')
    if repo.ready():  
      print(f'  level: {repo.level()}')
      for url in repo.urls():
        print('  url: ', url, ';', sep='')
      print(f'  ref: {repo.path()}')
      not_in_repo = ''
      if not repo.is_rev_exists():
        not_in_repo = '(not in repo) '
      print(f'  revision: {not_in_repo}{repo.rev_get()}')
      print(f'  version: {repo.version()}')
      if repo.is_rev_in_bounds():
        print('  in bounds')
      else:
        print('  not in bounds')
      if 0 != len(repo.settings['label_handlers']):
        print('  labels: ', end='')
        for ext in repo.settings['label_handlers']:
          print(f"{ext} ({repo.settings['label_handlers'][ext]}); ", end='')
        print()
      if 0 != len(repo.settings['briefers']):
        print('  briefers: ', end='')
        for ext in repo.settings['briefers']:
          print(f"{ext} ({repo.settings['briefers'][ext]}); ", end='')
        print()
    else:
      print(Fore.RED, ' not ready:', end='')
      if not repo.is_exists(): print(Fore.RED, 'exist', end='')
      if not repo.is_binded(): print(Fore.RED, 'bind', end='')
      if not repo.has_rev(): print(Fore.RED, 'rev', end='')
      if not repo.is_connected(): print(Fore.RED, 'connect', end='')
      print()
    print(Fore.RESET)

def action_repo_info(repo_name):
  repo = RepoMan.get(repo_name)
  repo_info(repo)

def action_repos(args):
  for repo in RepoMan.walk():
    repo_info(repo)

def action_repo(args):
    args.repo = args.repo.rstrip('/')
    repo_name = args.repo

    if args.subcmd_repo == 'new':
      action_repo_new(args.repo, args.provider, args.desc)

    elif args.subcmd_repo == 'delete':
      action_repo_delete(args.repo)

    elif args.subcmd_repo == 'clear':
      action_repo_clear(args.repo)
      
    elif args.subcmd_repo == 'url':
      action_repo_url(args.repo)

    elif args.subcmd_repo == 'ref':
      action_repo_ref(args)
      
    elif args.subcmd_repo == 'reref':
      action_repo_reref(args)
      
    elif args.subcmd_repo == 'unref':
      action_repo_unref(args)

    elif args.subcmd_repo == 'desc':
      action_repo_desc(args)    

    elif args.subcmd_repo == 'draft':
      action_repo_draft(args.repo)  

    elif args.subcmd_repo == 'bounds':
      if args.add:
        action_repo_bounds_add(args)
      elif args.remove:
        action_repo_bounds_remove(args)
      elif args.show:
        action_repo_bounds_show(args)
      elif args.clear:
        action_repo_bounds_clear(args)

    elif args.subcmd_repo == 'labels':
      if args.add:
        action_label_add(args)
      elif args.remove:
        action_label_remove(args)
      elif args.show:
        action_label_show(args)
      elif args.clear:
        action_label_clear(args)
      elif args.policy:
        action_label_policy(args)

    elif args.subcmd_repo == 'briefers':
      if args.add:
        action_briefers_add(args)
      elif args.remove:
        action_briefers_remove(args)
      elif args.show:
        action_briefers_show(args)
      elif args.clear:
        action_briefers_clear(args)

    elif args.subcmd_repo == 'union':
      if args.set:
        action_repo_union_set(args.repo, args.set)
      elif args.reset:
        action_repo_union_reset(args.repo)
      elif args.show:
        action_repo_union_show(args.repo)

    elif args.subcmd_repo == 'rev':
      if args.set:
        action_repo_rev_set(repo_name, args.set)
      if args.reset:
        action_repo_rev_reset(repo_name)
      if args.get:
        action_repo_rev_get(repo_name)
      if args.check:
        action_repo_rev_check(repo_name)
      if args.resolve:
        action_repo_rev_resolve(repo_name, args.resolve)
        
    elif args.subcmd_repo == 'diff':
      if args.draft:
        action_repo_diff_draft(repo_name, args.rev)
      else:
        action_repo_diff(repo_name, args.rev)
        
    elif args.subcmd_repo == 'ls':
      action_repo_ls(repo_name)

    elif args.subcmd_repo == 'info':
      action_repo_info(repo_name)

