#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import repo_path

from colorama import Fore, Back, Style

from act_error import *
from repo import *
from repoman import RepoMan
from ci import *
from cid import ConfItemError, ConfItemId
from cit import ConfItemTrace

def action_link_add(cids_str):
  target_ci = ConfItem(cids_str[0])
  for cid_str in cids_str[1:]:
    ci = ConfItem(cid_str)
    target_ci.trace_add(ci)
  
def action_link_remove(cids_str):
  target_ci = ConfItem(cids_str[0])
  for cid_str in cids_str[1:]:
    ci = ConfItem(cid_str)
    target_ci.trace_rem(ci)

def action_link_clone(cids_str):
  target_ci = ConfItem(cids_str[0])
  for cid_str in cids_str[1:]:
    ci = ConfItem(cid_str)
    target_ci.trace_clone(ci)

def link_ralloced(cid_str):
  ci = ConfItem(cid_str)
  repo = ci.repo()
  path = ci.cid().rel_path()
  print()
  print(F"Reverse allocation for '{repo.name()}:{path}'")

  alloced = list()
  for file in repo.walk_traced(path):
    ci = ConfItem(file)
    for rci, direction in ci.trace_walk():
      if direction == 'b':
        alloced.append(rci.name())
  alloced.sort()
  print("\n".join(alloced))
    
# os.path.exists(path), os.path.isdir(path), os.path.isfile(path)
# TODO: проверить, что пришла именно директория; для файлов есть show
# TODO: поддержка union
def action_link_ralloced(cids_str):
  for cid_str in cids_str:
    link_ralloced(cid_str)
    
# TODO: добавить поддержку директорий: выводить для каждого файла
def action_link_show(cids_str):
  print()
  for cid_str in cids_str:
    ci = ConfItem(cid_str)
    print(Style.BRIGHT, ci.name(), Style.RESET_ALL, sep='')
    for rci, direction in ci.trace_walk():
      if direction == 'f':
        print("forward: ", end='')
      else:
        print("backward: ", end='')
      print(rci.name())
    print()
    
    
def action_link_reset(cids_str):
  for cid_str in cids_str:
    ci = ConfItem(cid_str)
    ci.trace_reset()

'''
def action_link_complete(completed_ci):
  for ci in completed_ci:
    cit = ConfItemTrace(ci.name())
    cit.complete(ci.rev(), True)

def action_link_uncomplete(uncompleted_ci):
  for ci in uncompleted_ci:
    cit = ConfItemTrace(ci.name())
    cit.complete(ci.rev(), False)
'''
def action_link_labels(cids_str):
  for cid_str in cids_str:
    print()
    ci = ConfItem(cid_str)
    labels = ci.labels()
    
    print(Style.BRIGHT, ci.name(), Style.RESET_ALL, sep='')
    for label in labels:
      print(label)

    print('(labels found: ' + str(len(labels)) + ')')

def action_link_resolve(cids_str):
  for cid_str in cids_str:
    cid = ConfItemId(cid_str)
    rev_id = cid.rev()
    ci = ConfItem(cid.name())
    rev_id = ci.last_rev_with_changes(rev_id)
    print(ci.name(), ':', cid.rev(), '->', rev_id)

def links_abs_to_rel(links):
  rel_links = list()
  for link in links:
    if os.path.isabs(link):
      for repo in RepoMan.walk():
        if repo.is_binded():
          path = repo.path().rstrip(repo_path.psep) + repo_path.psep
          if link.startswith(path):
            link = repo.name() + repo_path.psep + link.replace(path, '')
            break
      else:
        raise ValueError("can't recognize repo for link '"+link+"' that has absolute path")

    rel_links.append(link)
  return rel_links

def link_handle_and_route(links, link_action):
  links = links_abs_to_rel(links)
  if not links:
    raise
  
  link_action(links)
  
def action_link(args):
  if args.add:
    link_handle_and_route([args.add] + args.links, action_link_add)
  elif args.remove:
    link_handle_and_route([args.remove] + args.links, action_link_remove)
  elif args.clone:
    link_handle_and_route([args.clone] + args.links, action_link_clone)
  elif args.show:
    link_handle_and_route(args.links, action_link_show)
  elif args.ralloc:
    link_handle_and_route(args.links, action_link_ralloced)
  elif args.reset:
    link_handle_and_route(args.links, action_link_reset)
  elif args.complete:
    link_handle_and_route(args.links, action_link_complete)
  elif args.uncomplete:
    link_handle_and_route(args.links, action_link_uncomplete)
  elif args.labels:
    link_handle_and_route(args.links, action_link_labels)
  elif args.resolve:
    link_handle_and_route(args.links, action_link_resolve)
