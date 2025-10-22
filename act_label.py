#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

from repo import *
from repoman import RepoMan
from act_error import *

def action_label_add(args):
  repo = RepoMan.get_ready(args.repo)
  ext = args.add
  if not args.handler:
    raise ActionError("missing 'handler' argument")
  else:
    repo.labels.set_handler(ext, args.handler)
  print(f"'{ext}' label handler was added to repo '{repo.name()}'")

def action_label_remove(args):
  repo = RepoMan.get_ready(args.repo)
  ext = args.remove
  repo.labels.del_handler(ext)
  print(f"'{ext}' label handler was removed from repo '{repo.name()}'")

def action_label_show(args):
  count = 0
  repo = RepoMan.get_ready(args.repo)
  for ext in repo.settings['label_handlers']:
    print(f"'{ext}': '{repo.settings['label_handlers'][ext]}'")
    count += 1
  print()
  print(f'total: {count}')

def action_label_clear(args):
  repo = RepoMan.get_ready(args.repo)
  repo.labels.clear_handlers()
  print(f"All label handlers was removed from repo '{repo.name()}'")

'''
TODO: Политики обработки внутренних меток (если к расширению ЕК привязан обработчик внутренних меток)
1. все метки, которые есть в ЕК, должны быть протрассированы
2. может быть протрассирована хотя бы одна из меток, которые есть в ЕК, остальные непротрассированные метки будут считаться протрассированными автоматически (как будто они протрассированы на одну из реально протрассированных меток) 

- можно ли трассировать файл целиком не указывая конкретных меток? как это будет происходить: будут создаваться связи для каждой метки файла?  
- где должны учитываться политики? в stat, export
- что делать, если "вверх" трассировки нет (реальной нет, есть автоматическая), но вниз - есть? 
- политика №2 распротраняется в обе стороны или только вверх? скорее только вверх
- применять политику можно прям в Repo.walk() - выдавать только нужные метки, а можно в stat и export отдельно
- скорее всего, лучше выбрать одинаковое поведение с директориями
'''
def action_label_policy(args):
  repo = RepoMan.get_ready(args.repo)
  repo.labels_policy_update(args.policy)
  print(f'The labels policy update for repo \'{repo.name()}\' was successful')
  
