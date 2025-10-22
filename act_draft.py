#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import draft

def action_draft(args):
  if args.test:
    draft.test(args.draft, args.rerun, args.nonstop, is_need_remove = False)
  elif args.apply:
    draft.replay(args.draft, args.rerun, args.nonstop, is_need_remove = False)
  elif args.use:
    draft.replay(args.draft, args.rerun, args.nonstop, is_need_remove = True)
    
def action_drafting(args):
  draft.drafting(args.cmddraft, args.rerun, args.draft)

