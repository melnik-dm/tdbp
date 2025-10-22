#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import tempfile

__tmp_path__ = tempfile.gettempdir() + "/tdbp/"

def clear():
  if os.path.exists(__tmp_path__):
    shutil.rmtree(__tmp_path__)
