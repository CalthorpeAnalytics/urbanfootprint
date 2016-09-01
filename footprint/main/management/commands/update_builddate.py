
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

"""Replace any lines that want the date/branch/commit.

In the source file, just put a tag like auto-update-date: xxx.
For example, in JavaScript:

    var footer = 'UrbanFootprint rev. 2015.01.03-develop'; // auto-update-branch: 2015.01.03-develop

This will replace whatever comes after 'auto-update-branch' with the actual date+branch.

To get started with a new file, just use a dummy value:

    def footer():
        return 'Version XXX' # auto-update-branch: XXX

And run the script.
"""
import subprocess
from datetime import datetime
from tempfile import mkstemp
from os import remove, close
from shutil import move

from django.core.management import BaseCommand

SOURCE_FILES = [
    'sproutcore/apps/fp/views/left_sidebar_view.js',
]

class BadDataError(Exception):
    pass

def replace_date(filename, date, branch, commit):
    """In-place replacement, using a temporary file."""

    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(filename) as old_file:
            for lineno, line in enumerate(old_file):
                if 'auto-update-' not in line:
                    new_file.write(line)
                    continue

                update_pos = line.rindex('auto-update-')

                update_type, old_value = line[update_pos:].split(': ', 1)

                old_value = old_value.strip()
                if update_type == 'auto-update-date':
                    new_value = date
                elif update_type == 'auto-update-branch':
                    new_value = '%s-%s'  % (date, branch)
                elif update_type == 'auto-update-rev':
                    new_value = '%s-%s-%s' % (date, branch, commit)
                else:
                    raise BadDataError('%s:%s: Unknown update type "%s"' % (
                        filename, lineno, update_type))

                new_file.write(line.replace(old_value, new_value))

    close(fh)
    remove(filename)
    move(abs_path, filename)

class Command(BaseCommand):

    def handle(self, *args, **options):
        git_output = subprocess.check_output('git show --abbrev-commit HEAD'.split())

        for line in git_output.splitlines():
            if line.startswith('commit '):
                commit = line.split(' ', 1)[1]
                break

        else:
            raise BadDataError("Commit not found in git output:\n%s" % git_output)

        # Gets something like 'refs/heads/develop'
        branch = subprocess.check_output('git symbolic-ref HEAD'.split()).strip()

        # chop off tail, getting 'develop'
        branch = branch.rsplit('/', 1)[1]

        now = datetime.now().strftime('%Y.%m.%d')
        for filename in SOURCE_FILES:
            print "Updating %s..." % filename
            replace_date(filename, now, branch, commit)
