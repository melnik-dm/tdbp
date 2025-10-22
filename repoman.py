#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import json
from repo import Repo
from prov_git import RepoGit

class RepoMan:
  repos = dict()
  providers = {'git': RepoGit}

  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(RepoMan, cls).__new__(cls)
    return cls.instance

  def is_valid_prov(prov):
    if RepoMan.providers.get(prov) is not None:
      return True
    else:
      return False

  def has_repo(name):
    return True if RepoMan.repos.get(name) is not None else False

  def prov(name):
    with open(Repo._params(name) + Repo.FREPO(), 'r') as fd:
      settings = json.loads(fd.read())
      return RepoMan.providers[settings['provider']]

  def new(name, provider, desc):
    if RepoMan.has_repo(name):
      raise ValueError(name, "already exist")
    elif not RepoMan.is_valid_prov(provider):
      raise ValueError(provider, "invalid provider")
    else:
      repo = Repo(name)
      repo._Repo__create(provider, desc)
      return RepoMan.get(name)

  def get(name):
    try:
      obj = RepoMan.repos[name]
      #print('exist repo:', name)
    except:
      try:
        prov = RepoMan.prov(name)
        obj = prov(name)
      except:
        raise ValueError("bad repo '"+name+"'")
      else:
        RepoMan.repos[name] = obj;
      #print('new repo:', name)
    return obj
  
  def get_ready(name):
    repo = RepoMan.get(name)
    if not repo.ready():
      repo.ready_info()
      raise ValueError("Repo '"+repo.name()+"' not ready")
    return repo
  
  def walk():
    for d in os.listdir():
      if os.path.isdir(d):
        try:
          yield RepoMan.get(d)
        except ValueError:
          continue
          
  def walk_ready():
    for d in os.listdir():
      if os.path.isdir(d):
        try:
          yield RepoMan.get_ready(d)
        except ValueError:
          continue
