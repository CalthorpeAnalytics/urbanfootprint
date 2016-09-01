
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

import logging

from footprint.main.utils.utils import execute_with_stdin

logger = logging.getLogger(__name__)


class CommandExecution:

    def __init__(self, logger):
        logger = logger

    def _exec(self, command, stdin):
        logger.info("Running %s" % command)
        out_and_err_tuple = execute_with_stdin(command, stdin)
        # Just log errors, since the output seems to include the output of the piped command too
        if out_and_err_tuple.stdout:
            logger.info(out_and_err_tuple.stdout.bytes)
        if out_and_err_tuple.stderr:
            logger.warn(out_and_err_tuple.stderr.bytes)
        for returncode in out_and_err_tuple.returncodes:
            if returncode:
                raise Exception('command failed: ' % command)
        return out_and_err_tuple

    def run(self, commands, stdin=None):
        return self._exec(commands, stdin)
