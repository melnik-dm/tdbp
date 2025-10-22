#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from repo import *
from repoman import RepoMan
from act_error import *
from repo_briefers import RepoBriefers

def action_briefers_add(args):
  repo = RepoMan.get_ready(args.repo)
  ext = args.add
  if not args.handler:
    raise ActionError("missing 'handler' argument")
  else:
    repo.briefers.add(ext, args.handler, args.args)
  print(f"'{ext}' briefer was added to repo '{repo.name()}'")

def action_briefers_remove(args):
  repo = RepoMan.get_ready(args.repo)
  ext = args.remove
  repo.briefers.remove(ext)
  print(f"'{ext}' briefer was removed from repo '{repo.name()}'")

def action_briefers_show(args):
  count = 0
  repo = RepoMan.get_ready(args.repo)
  for ext in repo.settings['briefers']:
    print(f"'{ext}': '{repo.settings['briefers'][ext]}'")
    count += 1
  print()
  print(f'total: {count}')

def action_briefers_clear(args):
  repo = RepoMan.get_ready(args.repo)
  repo.briefers.clear()
  print(f"All briefers was removed from repo '{repo.name()}'")

  
