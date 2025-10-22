#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from act_error import *
import project
from union import Unions
import export

def action_new_project(args):
  project.init()
  print("Successfully initialized")

def action_export_to(union, format, directions, only_traced, with_contents, to):
  export.export(format, directions, union, only_traced, with_contents, to)

def action_export(args):
  action_export_to(args.target, args.format, args.directions, args.only_traced, args.with_contents, args.to)
