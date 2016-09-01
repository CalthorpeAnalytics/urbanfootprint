
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


# http://stackoverflow.com/questions/196960/can-you-list-the-keyword-arguments-a-python-function-receives
# >>> import inspect
# >>> def func(a,b,c=42, *args, **kwargs): pass
# >>> inspect.getargspec(func)
# (['a', 'b', 'c'], 'args', 'kwargs', (42,))
# If you want to know if its callable with a particular set of args, you need the args without a default already specified. These can be got by:
import inspect
from footprint.main.lib.functions import map_to_dict


def get_valued_arg_dict(func):
    """
        Returns the args with values specified.
    :param func:
    :return:
    """
    args, varargs, varkw, defaults = inspect.getargspec(func)
    reversed_defaults = reversed(defaults)
    return map_to_dict(lambda default_value: [args.pop(), default_value], reversed_defaults)

def get_required_args(func):
    args, varargs, varkw, defaults = inspect.getargspec(func)
    if defaults:
        args = args[:-len(defaults)]
    return args   # *args and **kwargs are not required, so ignore them.

#Then a function to tell what you are missing from your particular dict is:
def missing_args(func, argdict):
    return set(get_required_args(func)).difference(argdict)

#Similarly, to check for invalid args, use:
def invalid_args(func, argdict):
    args, varargs, varkw, defaults = inspect.getargspec(func)
    if varkw: return set()  # All accepted
    return set(argdict) - set(args)

#And so a full test if it is callable is :
def is_callable_with_args(func, argdict):
    return not missing_args(func, argdict) and not invalid_args(func, argdict)
