#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from act_error import *
from repo import *
from repoman import RepoMan
from union import Unions

def action_union_new(union_name):
  Unions().new(union_name)
  print("Create new union '"+union_name+"'")

# TODO: функция может перепривязывать все репо удаляемого объединения к другому заданному объединению, если оно задано (можно сделать отдельную команду)
def action_union_delete(union_name):
  union = Unions().get(union_name)
  if not union:
    raise ActionError("union '"+union_name+"' does not exist")

  if any(union_name == repo.name() for repo in RepoMan.walk()): 
    raise ActionError("union-repo could be deleted only with repo")

  for repo in RepoMan.walk():
    if union_name == repo.union():
      repo.union_reset()
  Unions().delete(union_name)
      
def action_union_level(union_name, level):
  unions = Unions()
  unions.change_level(union_name, level)
  print("Set union '"+union_name+"' to '"+level+"'")

def action_union_info(union_name):
  union = Unions().get(union_name)
  if not union:
    raise ActionError(f"union '{union_name}' does not exist")

  print(union_name)
  print(f'  level: {union["level"]}')
  print('  repos: ', end='')

  for repo in RepoMan.walk():
    if union_name == repo.union():
      print(f"'{repo.name()}';", end=' ')
  print()
  
def action_union(args):
  if args.new:
    action_union_new(args.union[0])
  elif args.delete:
    action_union_delete(args.union[0])
  elif args.level:
    action_union_level(args.union[0], args.level)
  elif args.info:
    action_union_info(args.union[0])

def action_unions(args):
  unions = Unions()
  for union in unions.walk():
    action_union_info(union)
    print()

