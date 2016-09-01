
# UrbanFootprint v1.5
# Copyright (C) 2016 Calthorpe Analytics
#
# This file is part of UrbanFootprint version 1.5
#
# UrbanFootprint is distributed under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation. This
# code is distributed WITHOUT ANY WARRANTY, without implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License v3 for more details; see <http://www.gnu.org/licenses/>.

from django.core.management import BaseCommand
from celery import current_app

__author__ = 'calthorpe_analytics'

class Command(BaseCommand):
    def handle(self, *args, **options):
        state = current_app.events.State()
        print 'Current Tasks: %s' % current_app.tasks.keys()

        def announce_succeeded_tasks(event):
            state.event(event)
            task_id = event['uuid']

            print('TASK SUCCEEDED: %s[%s] %s' % (
                event['name'], task_id, state[task_id].info(), ))

        def announce_failed_tasks(event):
            state.event(event)
            task_id = event['uuid']

            print('TASK FAILED: %s[%s] %s' % (
                event['name'], task_id, state[task_id].info(), ))

        def announce_dead_workers(event):
            state.event(event)
            hostname = event.get('hostname', None)

            print('Event type %s received' % event.get('type', 'undefined'))
            if hostname and not state.workers[hostname].alive:
                print('Worker %s missed heartbeats' % (hostname, ))



        with current_app.connection() as connection:
            recv = current_app.events.Receiver(connection, handlers={
                    'task-failed': announce_failed_tasks,
                    'task-succeeded': announce_succeeded_tasks,
                    'worker-heartbeat': announce_dead_workers,
            })
            recv.capture(limit=None, timeout=None, wakeup=True)
