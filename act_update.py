#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from repo import Repo
from repoman import RepoMan
from cid import ConfItemError, ConfItemId
from cit import ConfItemTrace
from ci import *
from act_error import *
from colorama import Fore, Back, Style

'''
фактически есть два отличающихся метода: revision и ci, все остальные 
основываются на ci (ci_list, repo, project).

присутствует два вида редакций:
rev_id - редакция директории, сюда же относится HEAD, тэги и тд; в этой редакции был изменен один из файлов внутри директории включая поддиректории
rev_id_spec - редакция файла; в этой редакции был изменен сам файл
'''

def update_draft(filename):
  with open(filename, 'a') as fd:
    cmd = os.sys.argv[1:]
    idx = cmd.index('--draft')
    del cmd[idx:idx+2]
    cmd_str = ' '.join(cmd) + os.linesep
    fd.write(cmd_str)

def update(ci, rev_id_spec, is_sandbox):
  if ci.has_links_for_rev(rev_id_spec):
    '''
    если у заданной редакции уже есть связи, значит она была обновлена ранее
    '''
    print(Fore.WHITE + "'"+str(ci.cid().new(rev_id_spec[:-30]))+"': not updated, already has links")
  else:
    last_rev = ci.last_rev_with_trace(rev_id_spec)
    if last_rev is None:
      '''
      отсутствуют предыдущие редакции для копирования связей
      '''
      print(Fore.WHITE + "'"+str(ci.cid().new(rev_id_spec[:-30]))+"': not updated, no prev data")
    else:
      try:
        if not is_sandbox:
          bd_clone(ci.cid().new(last_rev), list([ci.cid().new(rev_id_spec)]))
      except ConfItemError as err:
        raise ActionError("Clone error: " + err.message)
      else:
        print(Fore.GREEN + "'"+str(ci.cid().new(rev_id_spec[:-30]))+"': updated, from '"+str(ci.cid().new(last_rev[:-30]))+"'")

def revision_update(repo_name, rev_id, is_sandbox): # TODO: обновлять с учетом allow/deny?
  repo = RepoMan.get_ready(repo_name)

  rev_id_spec = repo.rev_resolve(rev_id)
  files = repo.rev_files(rev_id_spec)
  for file in files:
    ci = ConfItem(file)
    if repo.can_ci_contain_label(ci.cid()):
      labels = repo.ci_labels(ci.cid(), rev_id_spec)
      for label in labels:
        sub_ci = cid.sub(label)
        update(sub_ci, rev_id_spec, is_sandbox)
    update(ci, rev_id_spec, is_sandbox)

'''
Оставляет среди редакций ConfItemTrace только rev_id-редакцию и ее связи.
Отсекать связи можно будет при установке БВ ПО, чтобы уменьшить размер базы.
'''
def ci_trim(ci, rev_id_spec, is_sandbox):
  head_links, is_completed = None, False 
  if rev_id_spec is not None:
    head_links, is_completed = ci.links_for_rev(rev_id_spec)

  if head_links is not None:
    if ci.linked_revisions_count() > 1:
      if not is_sandbox:
        bd_reset(ci.cid())
        bd_add(ci.cid().new(rev_id_spec), head_links)
      print(Fore.GREEN + "'"+ci.cid().id()+"': trim '"+rev_id_spec[:-30]+"'")
    else:
      print(Fore.WHITE + "'"+ci.cid().id()+"': save")
  else:
    if not is_sandbox:
      bd_reset(ci.cid())
    print(Fore.RED + "'"+ci.cid().id()+"': drop")

def ci_update(ci, rev_id_spec, is_sandbox):
  if rev_id_spec is None:
    '''
    файл отсутствовал в заданной редакции и до нее
    '''
    cid = ci.cid()#.new(rev_id[:-30])
    print(Fore.RED + "'"+str(cid)+"': not updated, file doesn't exist in rev")
  else:
    update(ci, rev_id_spec, is_sandbox) 
   
def ci_list_update(ci_list, rev_id, is_need_trim, is_sandbox):
  for ci in ci_list:
    ci = ConfItem(ci)
    rev_id_spec = ci.last_rev_with_changes(rev_id, is_need_bounds_check=True) 
    if is_need_trim:
      ci_trim(ci, rev_id_spec, is_sandbox)
    else:
      ci_update(ci, rev_id_spec, is_sandbox)

def repo_update(repo_name, rev_id, is_need_trim, is_sandbox):
  repo = RepoMan.get_ready(repo_name)
  rev_id_spec = repo.rev_resolve(rev_id) 
  
  for ci in repo.walk_traced():
    ci = ConfItem(ci)
    rev_id_spec = ci.last_rev_with_changes(rev_id)
    if is_need_trim:
      ci_trim(ci, rev_id_spec, is_sandbox)
    else:
      ci_update(ci, rev_id_spec, is_sandbox)

def repo_list_update(repo_list, rev_id, is_need_trim, is_sandbox):
  for repo in repo_list:
    repo_update(repo, rev_id, is_need_trim, is_sandbox)

def prj_update(is_need_trim, is_sandbox):
    for repo in RepoMan.walk():
      repo_update(repo.name, 'HEAD', is_need_trim, is_sandbox)

def action_update(args):
  if args.draft is not None:
    args.sandbox = True

  if args.subcmd_update == 'revision':
    revision_update(args.repo, args.where, args.sandbox)

  elif args.subcmd_update == 'ci': 
    ci_list_update(args.ci, args.where, args.trim, args.sandbox)

  elif args.subcmd_update == 'repo': 
    repo_list_update(args.repo, args.where, args.trim, args.sandbox)

  elif args.subcmd_update == 'project':
    prj_update(args.trim, args.sandbox)

  if args.draft is not None:
    update_draft(args.draft)

  print(Fore.RESET, Back.RESET, Style.RESET_ALL, end='')

