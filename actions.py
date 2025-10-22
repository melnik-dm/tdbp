#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from act_error import *
from act_project import *
from act_repo import action_repo
from act_repo import action_repos
from act_union import action_union, action_unions
from act_link import action_link
from act_draft import action_draft, action_drafting
from act_stat import action_stat

import project
from version import __version__

def action_version(args):
  print("tdbp version "+__version__)

def action(args):
  if args.subcmd != 'version' and args.subcmd != 'init': 
    if not project.is_ready():
      raise ActionError("'" + os.getcwd() + "' is not a project or project created in incompatible version (" + project.version() + ")")
  
  if not hasattr(args, 'rtn'):
    raise ActionError("command without handler")

  args.rtn(args)    

