#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from act_error import *
from prov import RepoError
import cmdp
from colorama import Fore, Back, Style
import colorama
import tmp

# TODO: сортировать записи в ConfItemTrace, чтобы ускорить поиск

# TODO: узнать есть ли анализатор https://www.python.org/dev/peps/pep-0484/

# TODO: добавить проверку корректности двухсторонней связи: наличие связи с обоих сторон, отсутствие пересечения связей одного уровня (bd_test)
# TODO: добавить проверку дублирования связей в ConfItemTrace (dup_test)
# TODO: добавить проверку соответствия ЕК репозиторию: наличие ЕК в заданной редакции, корректность хэша, попадание в bounds (resolve_test)
# TODO: добавить проверку пересечения уровней связей (чтобы ЕК не имела связей с ЕК того же уровня)

# TODO: добавить в td-файлы magic для проверки их корректности

# ПРОДУМАТЬ: Символы, доступные для использования в имени файла: @!#%^&~' 

def crash():
  tmp.clear()
  exit(1) # важно для вызывающей программы, чтобы определить корректность работы
  
def error(err, is_nonstop):
  print(Fore.RED + "Program error"+str(type(err))+": " + str(err))
  print()
  if not is_nonstop:
    crash()
      
def run(args, is_nonstop = True):
  try:
    cmdp.parse(args)
  except (ActionError, RepoError, ValueError, NotImplementedError) as err:
    error(err, is_nonstop)
  except KeyboardInterrupt:
    print(Fore.RED + "Program interrupted")
    crash()
  finally:
    print(Fore.RESET, Back.RESET, Style.RESET_ALL)

def input(args):
  cmdp.init(run)
  run(args, is_nonstop = False)
  tmp.clear()
      
def main(args = None):
  colorama.init()
  input(args)

if __name__ == '__main__':
  main()

