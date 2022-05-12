import os
import sys
import time
import subprocess as sp
from crontab import CronTab
from .utils import get_config
from datetime import datetime
from twisted.internet import reactor, threads


class Scheduler:
    def __init__(self, verbose=False):
        self.v = verbose
        config = get_config('scheduler')
        tasks = config['tasks']
        child_init_options = {
            'pid': None,
            'base_task': None,
            'started': None,
            'stopped': None,
            'rc': 0,
        }
        self.waiter = None
        self.popen_childs = {}
        self.childs = {child['name']: {
            **child_init_options,
            'command': child['command'],
            'can_verbose': child['can_verbose']
        } for child in tasks if 'command' in child}
        self.subtasks = {child['name']: child['subtasks'] for child in tasks if 'subtasks' in child}
        self.delays = {}
        self.delayed_calls = {}
        self.schedules = {child['name']: child['schedule'] for child in tasks if 'schedule' in child}
        for task in self.schedules:
            self.delays[task] = CronTab(self.schedules[task])
            self.delayed_calls[task] = reactor.callLater(self.delays[task].next(default_utc=True), self.__start_task, task)

    def __get_popen_command(self, task):
        command = self.childs[task]['command'].format(**{'path': f'{os.getenv("project_path")}/src'}).split(' ')
        if self.v and self.childs[task]['can_verbose']:
            command.push('-v')
        return command

    def __start_task(self, task, base_task=None):
        if base_task is None:
            self.delayed_calls[task] = reactor.callLater(
                self.delays[task].next(default_utc=True),
                self.__start_task,
                task,
            )

        if self.__is_started_task(task):
            print(f'error: task {task} already started', file=sys.stderr)

        if task in self.subtasks:
            base_task = task
            task = self.subtasks[task][0]

        self.popen_childs[task] = sp.Popen(self.__get_popen_command(task))
        self.childs[task] = {
            'pid': self.popen_childs[task].pid,
            'base_task': base_task,
            'started': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stopped': None,
            'rc': None,
        }
        print(f'task {task} started with pid {self.popen_childs[task].pid}')
        self.__wait_poll(task)

    def __is_started_task(self, task):
        if task in self.subtasks:
            return any(child['rc'] is None for key, child in self.childs.items() if key in self.subtasks[task])
        return self.childs[task]['rc'] is None

    def __wait_poll(self, task):
        self.waiter = threads.deferToThread(self.__waiter)
        self.waiter.addCallbacks(self.__poll, self.__error_back, callbackArgs=(task,))

    def __waiter(self):
        time.sleep(3)
        self.waiter = None

    def __error_back(self, failure):
        print(f'error in awaiting task: {failure}', file=sys.stderr)

    def __poll(self, result, task):
        if result is not None:
            return
        rc = self.popen_childs[task].poll()
        if rc is None:
            self.__wait_poll(task)
        else:
            self.popen_childs[task] = None
            self.childs[task]['stopped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.childs[task]['rc'] = rc
            print(f'task {task} stopped with rc {rc}')
            if self.childs[task]['base_task'] is not None:
                self.__start_next_subtask(task)

    def __start_next_subtask(self, task):
        subtasks = self.subtasks[self.childs[task]['base_task']]
        task_index = subtasks.index(task)
        if task_index < (len(subtasks) - 1):
            self.__start_task(subtasks[task_index + 1], self.childs[task]['base_task'])
        self.childs[task]['base_task'] = None

    def run(self):
        print('scheduler started...')
        for task in self.schedules:
            print(f'{task} task start in: {round(self.delays[task].next(default_utc=True))} seconds')
        reactor.run()
