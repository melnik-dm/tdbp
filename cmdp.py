#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 MELNIK DENIS
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

import export
import act_stat
from actions import * 

argparser = None

def init(run_rtn):
  global argparser
  argparser = argparse.ArgumentParser(description='Управление базой данных трассировок. Для создания и настройки проекта предусмотрены команды init и repo; для управления связями базы данных - link.')
  subcmd = argparser.add_subparsers(dest='subcmd')
  #argparser.add_argument('-v', '--version', action='store_true', required=False, help='Просмотр версии')
  subcmd.required = True

  # VERSION
  subcmd_version_parser = subcmd.add_parser('version', help='Версия утилиты')
  subcmd_version_parser.set_defaults(rtn=action_version)

  # INIT
  subcmd_init_parser = subcmd.add_parser('init', help='Инициализация проекта в текущей директории')
  subcmd_init_parser.set_defaults(rtn=action_new_project)

  # REPO
  subcmd_unions_parser = subcmd.add_parser('repos', help='Список хранилищ проекта')
  subcmd_unions_parser.set_defaults(rtn=action_repos)
  
  subcmd_repo_parser = subcmd.add_parser('repo', help='Управление хранилищами проекта')
  subcmd_repo_parser.set_defaults(rtn=action_repo)

  subcmd_repo = subcmd_repo_parser.add_subparsers(dest='subcmd_repo')
  subcmd_repo.required = True

  # REPO NEW
  subcmd_repo_new_parser = subcmd_repo.add_parser('new', help='Добавление хранилища')

  subcmd_repo_new_parser.add_argument('repo', action='store', help='Имя создаваемого хранилища; используется как префикс пути при работе со связями')
  subcmd_repo_new_parser.add_argument('--provider', action='store', required=True, help='Тип хранилища: git, svn и тд')
  subcmd_repo_new_parser.add_argument('--desc', action='store', required=True, help='Описание хранилища; подойдет любая информация, которая поможет идентифицировать хранилище и выполнить установку связи на рабочем месте, например, адрес хранилища в сети')

  # REPO DELETE
  subcmd_repo_delete_parser = subcmd_repo.add_parser('delete', help='Удаление хранилища')
  subcmd_repo_delete_parser.add_argument('repo', action='store', help='Имя удаляемого хранилища; используется как префикс пути при работе со связями')

  # REPO CLEAR
  subcmd_repo_clear_parser = subcmd_repo.add_parser('clear', help='Очистка хранилища')
  subcmd_repo_clear_parser.add_argument('repo', action='store', help='Имя очищаемого хранилища; используется как префикс пути при работе со связями')

  # REPO REF
  subcmd_repo_ref_parser = subcmd_repo.add_parser('ref', help='Установка связи между хранилищем и его расположением на диске')

  subcmd_repo_ref_parser.add_argument('repo', action='store', help='Имя хранилища, для которого устанавливается ссылка')
  subcmd_repo_ref_parser.add_argument('--path', action='store', required=True, help='Путь до хранилища на диске')

  # REPO UNREF
  subcmd_repo_unref_parser = subcmd_repo.add_parser('unref', help='Сброс связи между хранилищем и его расположением на диске')

  subcmd_repo_unref_parser.add_argument('repo', action='store', help='Имя хранилища, для которого сбрасывается ссылка')

  # REPO REREF
  subcmd_repo_reref_parser = subcmd_repo.add_parser('reref', help='Переустановка связи между хранилищем и его расположением на диске')

  subcmd_repo_reref_parser.add_argument('repo', action='store', help='Имя хранилища, для которого устанавливается ссылка')
  subcmd_repo_reref_parser.add_argument('--path', action='store', required=True, help='Путь до хранилища на диске')

  # REPO URL
  subcmd_repo_url_parser = subcmd_repo.add_parser('url', help='Адреса хранилища')
  subcmd_repo_url_parser.add_argument('repo', action='store', help='Имя хранилища')

  # REPO DRAFT
  subcmd_repo_draft_parser = subcmd_repo.add_parser('draft', help='Черновик на основе связей хранилища')
  subcmd_repo_draft_parser.add_argument('repo', action='store', help='Имя хранилища')

  # REPO DESC
  subcmd_repo_desc_parser = subcmd_repo.add_parser('desc', help='Обновление описания')

  subcmd_repo_desc_parser.add_argument('repo', action='store', help='Имя хранилища')
  subcmd_repo_desc_parser.add_argument('--text', action='store', required=True, help='Новое описание')
  
  # REPO BOUNDS
  subcmd_repo_bounds_parser = subcmd_repo.add_parser('bounds', help='Установка границ (ветвей) для используемых редакций в рамках работы с хранилищем')

  bounds_group = subcmd_repo_bounds_parser.add_mutually_exclusive_group(required=True)

  bounds_group.add_argument('--add', action='store', metavar='bound', help='Добавление границы хранилища')
  bounds_group.add_argument('--remove', action='store', metavar='bound', help='Удаление конкретной границы хранилища')
  bounds_group.add_argument('--show', action='store_true', help='Просмотр всех границ хранилища')
  bounds_group.add_argument('--clear', action='store_true', help='Удаление всех границ хранилища')

  subcmd_repo_bounds_parser.add_argument('repo', action='store', help='Имя хранилища')

  # REPO UNION
  subcmd_repo_union_parser = subcmd_repo.add_parser('union', help='Включение хранилища в объединение')

  runion_group = subcmd_repo_union_parser.add_mutually_exclusive_group(required=True)

  runion_group.add_argument('--set', action='store', metavar='union', help='Добавление хранилища в объединение')
  runion_group.add_argument('--reset', action='store_true', help='Выход из объединения')
  runion_group.add_argument('--show', action='store_true', help='Просмотр информации об объединении хранилища')

  subcmd_repo_union_parser.add_argument('repo', action='store', help='Имя хранилища')  

  # REPO REVISION
  subcmd_repo_rev_parser = subcmd_repo.add_parser('rev', help='Настройка редакции хранилища')
  
  rrev_group = subcmd_repo_rev_parser.add_mutually_exclusive_group(required=True)
  
  rrev_group.add_argument('--set', action='store', metavar='rev', help='Установка редакции хранилища')
  rrev_group.add_argument('--reset', action='store_true', help='Сброс редакции хранилища')
  rrev_group.add_argument('--get', action='store_true', help='Получение редакции хранилища')
  rrev_group.add_argument('--check', action='store_true', help='Проверка редакции хранилища')
  rrev_group.add_argument('--resolve', action='store', help='Разрешение редакции хранилища')
  
  subcmd_repo_rev_parser.add_argument('repo', action='store', help='Имя хранилища')  

  # REPO DIFF
  subcmd_repo_rev_parser = subcmd_repo.add_parser('diff', help='Просмотр измененных данных', description="Просмотр изменений, затрагивающих протрассированные ЕК")

  subcmd_repo_rev_parser.add_argument('--rev', action='store', required=True, metavar='rev', help='Редакция')  
  subcmd_repo_rev_parser.add_argument('--as-draft', action='store_true', required=False, dest='draft', help='Создание черновика, на основе изменений, затрагивающих протрассированные ЕК')
  
  subcmd_repo_rev_parser.add_argument('repo', action='store', help='Имя хранилища')  
  
  # REPO LS
  subcmd_repo_rev_parser = subcmd_repo.add_parser('ls', help='Список ЕК хранилища', description="Просмотр списка ЕК хранилища с учетом фильтров")

  subcmd_repo_rev_parser.add_argument('repo', action='store', help='Имя хранилища')  
  
  # REPO INFO
  subcmd_repo_rev_parser = subcmd_repo.add_parser('info', help='Информация о хранилище', description="Просмотр параметров хранилища")

  subcmd_repo_rev_parser.add_argument('repo', action='store', help='Имя хранилища')
  
  # UNION
  subcmd_unions_parser = subcmd.add_parser('unions', help='Список объединений')
  subcmd_unions_parser.set_defaults(rtn=action_unions)

  subcmd_union_parser = subcmd.add_parser('union', help='Управление объединениями', description='Объединения служат для представления нескольких хранилищ как единое целое. Объединениям назначаются уровни. Уровни соответствуют уровням декомпозиции артефактов. Чем ниже значение уровня, тем более абстрактные артефакты содержатся в хранилище, чем выше - тем более декомпозированные. Например, если рассматривать ТВУ и ТНУ, то ТВУ абстрактный артефакт, а ТНУ - декомпозированный; таким образом, ТВУ будет иметь значение уровня ниже, чем ТНУ.')
  subcmd_union_parser.set_defaults(rtn=action_union)

  union_group = subcmd_union_parser.add_mutually_exclusive_group(required=True)

  union_group.add_argument('--new',
    action='store_true',
    help='Создание объединения')
  union_group.add_argument('--delete',
    action='store_true',
    help='Удаление объединения')
  union_group.add_argument('--level',
    metavar='level', action='store',
    help='Изменение уровня объединения')
  union_group.add_argument('--info',
    action='store_true',
    help='Информация об объединении')

  subcmd_union_parser.add_argument('union', metavar='union', action='store', nargs=1)

  # REPO LABELS
  subcmd_repo_label_parser = subcmd_repo.add_parser('labels', help='Управление обработчиками внутренних меток файлов хранилища')

  label_group = subcmd_repo_label_parser.add_mutually_exclusive_group(required=True)

  label_group.add_argument('--add', action='store', metavar='label', help='Добавление обработчика внутренних меток для файлов с заданным расширением (например, .req.pdf)')
  label_group.add_argument('--remove', action='store', metavar='label', help='Удаление обработчика внутренних меток для файлов с заданным расширением')
  label_group.add_argument('--show', action='store_true', help='Отображение всех обработчиков хранилища')
  label_group.add_argument('--clear', action='store_true', help='Удаление всех обработчиков хранилища')
  label_group.add_argument('--policy', action='store', choices=['ALL', 'TRACED'], help='Политика обработки меток')

  subcmd_repo_label_parser.add_argument('--handler', action='store', help='Путь до скрипта-обработчика (py) внутренних меток')
  subcmd_repo_label_parser.add_argument('repo', action='store', help='Имя хранилища')

  # REPO BRIEFERS
  subcmd_repo_briefers_parser = subcmd_repo.add_parser('briefers', help='Управление обработчиками краткого содержимого файла')

  briefers_group = subcmd_repo_briefers_parser.add_mutually_exclusive_group(required=True)

  briefers_group.add_argument('--add', action='store', metavar='label', help='Добавление обработчика краткого содержимого файлов с заданным расширением (например, .req.pdf)')
  briefers_group.add_argument('--remove', action='store', metavar='label', help='Удаление обработчика краткого содержимого файлов с заданным расширением')
  briefers_group.add_argument('--show', action='store_true', help='Отображение всех обработчиков хранилища')
  briefers_group.add_argument('--clear', action='store_true', help='Удаление всех обработчиков хранилища')

  subcmd_repo_briefers_parser.add_argument('--handler', action='store', help='Путь до скрипта-обработчика (py) краткого содержимого')
  subcmd_repo_briefers_parser.add_argument('--args', action='store', help='Аргументы, которые будут передавать скрипту-обработчику')
  subcmd_repo_briefers_parser.add_argument('repo', action='store', help='Имя хранилища')

  # LINK
  subcmd_link_parser = subcmd.add_parser('link', help='Управление связями')
  subcmd_link_parser.set_defaults(rtn=action_link)

  link_group = subcmd_link_parser.add_mutually_exclusive_group(required=True)

  link_group.add_argument('--add',
    metavar='target_ci', action='store',
    help='Добавление связей')
  link_group.add_argument('--remove',
    metavar='target_ci', action='store',
    help='Удаление связей')
  link_group.add_argument('--clone',
    metavar='target_ci', action='store',
    help='Клонирование связей (клоны не должны иметь связей)')
  link_group.add_argument('--show',
    action='store_true', help='Поиск и вывод связей')
  link_group.add_argument('--ralloc',
    action='store_true', help='Обратное распределение связей')
  link_group.add_argument('--reset',
    action='store_true', help='Очистка связей всех редакций')
  link_group.add_argument('--resolve',
    action='store_true', help='Разрешение связей')
  link_group.add_argument('--complete',
    action='store_true', help='Установка признака завершенности связей')
  link_group.add_argument('--uncomplete',
    action='store_true', help='Снятие признака завершенности связей')
  link_group.add_argument('--labels',
    action='store_true', help='Вывод меток для всех переданных CI')

  subcmd_link_parser.add_argument('links', metavar='link_ci', action='store', nargs='+')

  # DRAFT
  subcmd_draft_parser = subcmd.add_parser('draft', help='Обработка черновиков')
  subcmd_draft_parser.set_defaults(rtn=action_draft,rerun=run_rtn)

  draft_group = subcmd_draft_parser.add_mutually_exclusive_group(required=True)

  draft_group.add_argument('--test',
    action='store_true',
    help='Проверка черновика в песочнице')
  draft_group.add_argument('--apply',
    action='store_true',
    help='Применение черновика')
  draft_group.add_argument('--use',
    action='store_true',
    help='Использование черновика (применяет и удаляет файл черновика)')

  subcmd_draft_parser.add_argument('--nonstop',
    action='store_true',
    help='Не останавливаться при ошибках')

  subcmd_draft_parser.add_argument('draft', action='store',  nargs='+')

  # DRAFTING

  subcmd_drafting_parser = subcmd.add_parser('drafting', description='Составление черновиков: drafting [--draft <filename>] "cmd ..."')
  subcmd_drafting_parser.set_defaults(rtn=action_drafting,rerun=run_rtn)
  
  subcmd_drafting_parser.add_argument('--draft', action='store', help='Имя файла черновика')
  
  subcmd_drafting_parser.add_argument('cmddraft', action='store', help='Команда', nargs='?')

  # EXPORT

  subcmd_export_parser = subcmd.add_parser('export', help='Экспорт проекта')
  subcmd_export_parser.set_defaults(rtn=action_export)
  subcmd_export_parser.add_argument('target', metavar='union', action='store', nargs='?', default=None)
  
  subcmd_export_parser.add_argument('--traced', dest='only_traced', action='store_true', default=False,
    help='Не отображать ЕК без связи')

  subcmd_export_parser.add_argument('--contents', dest='with_contents', action='store_true', default=False,
    help='Выгрузить содержимое ЕК')

  subcmd_export_parser.add_argument('--to', action='store', default='__export', help='Путь до директории экспорта')

  export_format = subcmd_export_parser.add_mutually_exclusive_group(required=True)
  export_format.add_argument('--html', dest='format', action='store_const', const=export.TraceExportHtml,
    help='Формат HTML')
  export_format.add_argument('--csv', dest='format', action='store_const', const=export.TraceExportCsv,
    help='Формат CSV')
  export_format.add_argument('--dipt', dest='format', action='store_const', const=export.TraceExportDipt,
    help='Формат DIP-table')
  
  export_direction = subcmd_export_parser.add_argument_group()
  export_direction.add_argument('--bd', dest='directions', action='append_const', const=export.TraceDir.bd, default=None,
    help='В объеме двусторонних связей: (backward, target, forward)')
  export_direction.add_argument('--fw', dest='directions', action='append_const', const=export.TraceDir.fw,
    help='В объеме прямых связей: (target, forward)')
  export_direction.add_argument('--bw', dest='directions', action='append_const', const=export.TraceDir.bw,
    help='В объеме обратных связей: (target, backward)')
  #export_direction.add_argument('--fwi', dest='directions', action='append_const', const=export.TraceDir.fwi,
  #  help='В объеме прямых связей (с инверсией): (forward, target)')
  #export_direction.add_argument('--bwi', dest='directions', action='append_const', const=export.TraceDir.bwi,
  #  help='В объеме обратных связей (с инверсией): (backward, target)')

  # STAT
  subcmd_stat_parser = subcmd.add_parser('stat', help='Сбор статистики')
  subcmd_stat_parser.set_defaults(rtn=action_stat)
  subcmd_stat_parser.add_argument('target', metavar='repo', action='store', nargs='?', default=None)

  subcmd_stat_parser.add_argument('-a', dest='contents', action='append_const', const=act_stat.StatContents.ALL,
    help='Все ЕК')
  subcmd_stat_parser.add_argument('-d', dest='contents', action='append_const', const=act_stat.StatContents.DERIVATIVES,
    help='Только производные (отсутствует обратная/вверх связь) ЕК')
  subcmd_stat_parser.add_argument('-i', dest='contents', action='append_const', const=act_stat.StatContents.UNIMPLEMENTED,
    help='Только нереализованные (отсутствует прямая/вниз связь)')
  subcmd_stat_parser.add_argument('-c', dest='contents', action='append_const', const=act_stat.StatContents.UNCOMPLETED,
    help='Только незавершенные (неполный набор связей)')

def parse(args):
  global argparser
  cmd = argparser.parse_args(args)
  action(cmd)
