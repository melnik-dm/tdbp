#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.util
import os

# TODO: закешировать загруженные label handler

class RepoLabels:
  def CFG_SECTION():
    return 'label_handlers'

  def __init__(self, repo):
    self._repo = repo

  # загружает класс Label из модуля, расположенного по пути mod_path
  def _load_handler(self, mod_path):
    def _load_module(mod_path):
      try:
        spec = importlib.util.spec_from_file_location('label', mod_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
      except (FileNotFoundError) as err:
        raise ValueError(f"{str(err)} [{mod_path}]")

    def _has_method(obj, name):
      meth = getattr(obj, name, None)
      if meth:
        return callable(meth)
      else:
        return False

    def _get_handler(mod):
      try:
        label = mod.Label()
        if not (_has_method(label, 'probe') and _has_method(label, 'scan')):
          raise Exception()
        return label
      except:
        raise ValueError("bad label handler")

    '''
    попытка подключить модуль, который располагается где-то в системе.
    то есть 'mod_path' - это относительный или абсолютный путь до файла.
    если указан не абсолютный путь (/home/user/.../), то isfile принимает путь,
    как путь относительно директории запуска.
    '''
    if os.path.sep in mod_path:
      if not os.path.isfile(mod_path):
        raise ValueError(f"handler could not be found '{mod_path}'")
      return _get_handler(_load_module(mod_path))

    '''
    попытка подключить модуль, который должен располагаться в директории запуска
    tdbp.
    то есть 'mod_path' - это имя файла, располагающегося в одной директории с
    проектом tdbp.
    '''
    if os.path.isfile(mod_path):
      return _get_handler(_load_module(mod_path))
      
    '''
    попытка подключить модуль, который должен располагаться вместе с tdbp.
    то есть 'mod_path' - это имя файла, располагающегося в одной директории с
    'tdbp.py'.
    '''
    try:
      if mod_path.endswith('.py'):
        mod_path = mod_path[:-3]
      return _get_handler(__import__(mod_path))
    except (ModuleNotFoundError) as err:
      raise ValueError(str(err))

  def find_label_handler(self, filename):
    if not self._repo.settings[RepoLabels.CFG_SECTION()]:
      return None
      
    # удаление директорий из имени
    filename_pos = filename.rfind('/')
    if filename_pos != -1:
      filename = filename[filename_pos:]
    
    # обработка вложенных (нескольких) расширений
    while '.' in filename:
      filename = '.'.join(filename.split('.')[1:])

      ext = '.' + filename
      if ext in self._repo.settings[RepoLabels.CFG_SECTION()]:
        handler = self._load_handler(self._repo.settings[RepoLabels.CFG_SECTION()][ext])
      else:
        handler = None

      if handler:
        return handler

    return None

  def set_handler(self, ext, mod_path):
    if self._load_handler(mod_path):
      self._repo.settings[RepoLabels.CFG_SECTION()][ext] = mod_path
      self._repo._sync_settings()

  def del_handler(self, ext):
    if ext in self._repo.settings[RepoLabels.CFG_SECTION()]:
      del(self._repo.settings[RepoLabels.CFG_SECTION()][ext])
      self._repo._sync_settings()
    else:
      raise ValueError(f'Repo \'{self._repo.name()}\' does not have a label handler for \'{ext}\'')

  def clear_handlers(self):
    self._repo.settings[RepoLabels.CFG_SECTION()] = {}
    self._repo._sync_settings()
