#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from ci import ConfItem
#from repo import Repo
from repoman import RepoMan
from union import Unions

from export_csv import *
from export_html import *
from export_dipt import *
from export_if import *

# TODO: реализовать fwi и bwi (возможно и не нужно)
# TODO: добавить вывод repo.description для хранилища
# TODO: добавить вывод статистики

def direction_determine(ci, lci, forward_links, backward_links):
  if lci.level() < ci.level():
    backward_links.append(lci)
  elif lci.level() > ci.level():
    forward_links.append(lci)
  else:
    raise ValueError("ci '{ci}' has same level link '{link}'")

def export_ci(ci, method):
  forward_links = list()
  backward_links = list()
  is_completed = ci._td().trace().is_completed()
  for link in ci._td().links(): # links -> list(ConfItemId)
    lci = ConfItem(link.name())
    #assert link == lci.cid()
    #assert link.name() == lci.name()
    direction_determine(ci, lci, forward_links, backward_links)

  #assert ci.name() == ci.cid().name()
  method.body_entry(ci, is_completed, forward_links, backward_links)

def export_repo(repo, method, only_traced):
  walk = None
  if only_traced:
    walk = repo.walk_traced
  else:
    walk = repo.walk
    
  for file in walk():
    ci = ConfItem(file)
    export_ci(ci, method)

def export_union(export_method, direction, union_name, only_traced, with_contents, to):
  union_repos = [repo for repo in RepoMan.walk() if repo.union() == union_name]
  if len(union_repos) == 0:
    return
  
  method = export_method(to, union_name, direction, with_contents)
  method.header()
  caption = f'{union_name} ({[repo.name() for repo in union_repos]})'
  method.body_begin(caption)
  for repo in union_repos: 
    export_repo(repo, method, only_traced)
  method.body_end()
  method.footer()

def export(export_method, directions, target, only_traced, with_contents, to):
  if directions is None:
    directions = [TraceDir.__members__[x] for x in TraceDir.__members__]
    
  for direction in directions:
    if None == target:
      for union in Unions().walk():
        export_union(export_method, direction, union, only_traced, with_contents, to)
    else:
      if not Unions().get(target):
        raise ValueError(f"union '{target}' does not exist")
      export_union(export_method, direction, target, only_traced, with_contents, to)
    
  print(f"Successfully exported to '{to}'")
