#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.util
import os
import inspect

# TODO: кешировать загруженные бриферы

class RepoBriefers:
  def CFG_SECTION():
    return 'briefers'

  def __init__(self, repo):
    self._repo = repo

  # загружает класс Briefer из модуля, расположенного по пути mod_path
  def _load_handler(self, mod_path, opts = None):
    def _load_module(mod_path):
      try:
        spec = importlib.util.spec_from_file_location('briefer', mod_path)
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

    def _get_handler(mod, opts):
      try:
        # class
        briefer_attr = getattr(mod, 'Briefer', None)
        assert briefer_attr is not None
        # ctor
        ctor_attr = getattr(briefer_attr, '__init__', None)
        assert ctor_attr is not None
        ctor_inspect = inspect.getargspec(ctor_attr)
        assert len(ctor_inspect.args) == 2      
        # method
        parse_attr = getattr(briefer_attr, 'parse', None)
        assert parse_attr is not None
        parse_inspect = inspect.getargspec(parse_attr)
        assert len(parse_inspect.args) == 3
        #print(ctor_inspect)
        #print(parse_inspect)
        #print()      
        briefer = mod.Briefer(opts)
        return briefer
      except:
        raise ValueError("bad briefer")

    '''
    попытка подключить модуль, который располагается где-то в системе.
    то есть 'mod_path' - это относительный или абсолютный путь до файла.
    если указан не абсолютный путь (/home/user/.../), то isfile принимает путь,
    как путь относительно директории запуска.
    '''
    if os.path.sep in mod_path:
      if not os.path.isfile(mod_path):
        raise ValueError(f"handler could not be found '{mod_path}'")
      return _get_handler(_load_module(mod_path), opts)

    '''
    попытка подключить модуль, который должен располагаться в директории запуска
    tdbp.
    то есть 'mod_path' - это имя файла, располагающегося в одной директории с
    проектом tdbp.
    '''
    if os.path.isfile(mod_path):
      return _get_handler(_load_module(mod_path), opts)
      
    '''
    попытка подключить модуль, который должен располагаться вместе с tdbp.
    то есть 'mod_path' - это имя файла, располагающегося в одной директории с
    'tdbp.py'.
    '''
    try:
      if mod_path.endswith('.py'):
        mod_path = mod_path[:-3]
      return _get_handler(__import__(mod_path), opts)
    except (ModuleNotFoundError) as err:
      raise ValueError(str(err))

  def has_handler(self, ext):
    if ext in self._repo.settings[RepoBriefers.CFG_SECTION()]:
      return True
    else:
      return False
      
  def get(self, ext):
    cfg = self._repo.settings[RepoBriefers.CFG_SECTION()][ext]
    return self._load_handler(cfg['path'], cfg['args'])

  def find_suitable(self, filename):
    if not self._repo.settings[RepoBriefers.CFG_SECTION()]:
      return None
      
    # удаление директорий из имени
    filename_pos = filename.rfind('/')
    if filename_pos != -1:
      filename = filename[filename_pos:]
    
    # обработка вложенных (нескольких) расширений
    while '.' in filename:
      filename = '.'.join(filename.split('.')[1:])

      ext = '.' + filename
      if ext in self._repo.settings[RepoBriefers.CFG_SECTION()]:
        handler = self.get(ext)
      else:
        handler = None

      if handler:
        return handler

    return None

  def add(self, ext, mod_path, args):
    if self._load_handler(mod_path):
      self._repo.settings[RepoBriefers.CFG_SECTION()][ext] = {'path': mod_path, 'args': args}
      self._repo._sync_settings()

  def remove(self, ext):
    if ext in self._repo.settings[RepoBriefers.CFG_SECTION()]:
      del(self._repo.settings[RepoBriefers.CFG_SECTION()][ext])
      self._repo._sync_settings()
    else:
      raise ValueError(f'Repo \'{self._repo.name()}\' does not have a briefer for \'{ext}\'')

  def clear(self):
    self._repo.settings[RepoBriefers.CFG_SECTION()] = {}
    self._repo._sync_settings()
