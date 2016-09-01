
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

from footprint.main.lib.functions import unique, first, to_list

__author__ = 'calthorpe_analytics'

def get_subclasses(classes, level=0):
    """
        Return the list of all subclasses given class (or list of classes) has.
        Inspired by this question:
        http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python
    """
    # for convenience, only one class can can be accepted as argument
    # converting to list if this is the case
    if not isinstance(classes, list):
        classes = [classes]

    if level < len(classes):
        classes += classes[level].__subclasses__()
        return get_subclasses(classes, level+1)
    else:
        return classes

def best_matching_subclass(c, matching_lambas):
    """
        Recursively find the subclasses matching the lambdas.
        The first lambda is the most important. The first subclass to match it will return.
        The subsequent lambdas are sought if the first fails to match anything
    :param c:
    :param matching_lambas:
    :return:
    """
    for matching_lambda in matching_lambas:
        subclass = match_subclasses(c, matching_lambda, first_only=True)
        if subclass:
            return subclass
    return None

def match_subclasses(c, matching_lambda=lambda x: True, first_only=False):
    """
        Recursively find the subclasses matching lambda
    :param c: starting class
    :param matching_lambda: filter function that takes each subclass and returns true or false. Unmatched classes
    are still recursed beforehand. Defaults to returning all.
    :param first_only: Default False. Stop after the first match and return one result
    :return: A single result or None if first_only is True. Otherwise 0 or more results in an array
    """
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        subclasses.extend(get_subclasses(d))
    unique_subclasses = unique(subclasses)
    return first(matching_lambda, unique_subclasses) if first_only else \
        filter(matching_lambda, unique_subclasses)

def receiver_subclasses(signal, sender, dispatch_uid_prefix, **kwargs):
    """
    A decorator for connecting receivers and all receiver's subclasses to signals. Used by passing in the
    signal and keyword arguments to connect::

        @receiver_subclasses(post_save, sender=MyModel)
        def signal_receiver(sender, **kwargs)G:
            ...
    """
    def _decorator(func):
        all_senders = get_subclasses(sender)
        for snd in all_senders:
            signal.connect(func, sender=snd, dispatch_uid=dispatch_uid_prefix+'_'+snd.__name__, **kwargs)
        return func
    return _decorator

def connect_subclasses(func, signal, sender, dispatch_uid_prefix, **kwargs):
    all_senders = get_subclasses(sender)
    for snd in all_senders:
        signal.connect(func, sender=snd, dispatch_uid=dispatch_uid_prefix+'_'+snd.__name__, **kwargs)

def best_matching_subclass(
        cls,
        matching_lambda=lambda x: True,
        limited_subclasses=None,
        return_base_unless_match=False,
        ascend_cls_until=None
    ):
    """
        Find the best matching subclass according to the matching_lambda.
        This works by breadth-first. It searches immediate sublasses,
        and upon finding a match recurses on that subclass. If no match
        is found at a certain level it returns the match at the level above
    :param cls:
    :param matching_lambda: filter function that takes each subclass and returns true or false.
    :param limited_subclasses: If specified limits the search to the given subclasses.
    These subclasses are used recursively as well
    :param return_base_unless_match: Default false. Return the c if no match is found.
    :param ascend_cls_until: Default None. If set to a class, if no match is found for cls,
    recurse on cls.__base__ until a match or cls.__base__ equals the class specified here.
    Example. If cls is GlobalConfig and ascend_cls_until=FootprintModel, the method looks
    for a subclass with cls==GlobalConfig. If that fails as cls==ConfigEntity. If that fails
    then cls==FootprintModel so we give up and return None or if return_base_unless_match is True
    then we return ConfigEntity (which is probably useless)
    :return: The first match or None (or c if return_base_unless_match is True)
    """
    subclasses = filter(lambda limited_subclass: issubclass(limited_subclass, cls), limited_subclasses) if \
        limited_subclasses else \
        cls.__subclasses__()
    match = first(matching_lambda, unique(subclasses))
    if match:
        # If we have a match recurse on the match to try to find an even better match
        # specify return_base_unless_match since we already succeed at matching for this iteration
        return best_matching_subclass(match, matching_lambda, limited_subclasses, return_base_unless_match=True)
    elif ascend_cls_until and cls.__base__ != ascend_cls_until:
        # No match but recurse on cls.__base__ to find a more general match unless we reach the 'until' cls
        return best_matching_subclass(cls.__base__, matching_lambda, limited_subclasses, return_base_unless_match, ascend_cls_until)
    # Give up and return the current c or None
    return (cls if return_base_unless_match else None)
