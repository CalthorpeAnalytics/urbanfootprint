#
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
#
# This script, when used with reduce.py, analyzes logging output generated during footprint_init and
# calulates the total number of occurences of unique log messages and the total amount of time spent
# between a log message and the next.

# Logs from production runs of footprint_init can be found here:
#     https://drive.google.com/open?id=0B-Bwr3ZNiaMbNE5SWUptUzhaZkE

# Usage:
#     footprint/tools/analyze_logs.sh <log_file> <output_file>

# Output is total duration (in seconds), total count, log message (tab separated). Example output for
# build-production-1455086133.log (top 4 lines):

#     11083.467   185 Getting/Creating LayerSelection instances for Layer of DbEntity Key: Bike Lane of The SCAG Region
#     11046.72    185 Getting/Creating LayerSelection instances for Layer of DbEntity Key: Sea Level Rise of The SCAG Region
#     10963.335   184 Getting/Creating LayerSelection instances for Layer of DbEntity Key: Farmland of The SCAG Region
#     10957.349   184 Getting/Creating LayerSelection instances for Layer of DbEntity Key: Census Tracts of The SCAG Region

cat $1 | python footprint/scripts/log_parsing/map.py | sort | python footprint/scripts/log_parsing/reduce.py | sort -nr > $2
