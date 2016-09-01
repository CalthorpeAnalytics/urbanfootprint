
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

__author__ = 'calthorpe_analytics'


class Token(object):
    """
        A tree structure based on Sproutcore's SC.Query Token Tree, although not at all dependent on Sproutcore.
        This supports a tree specification for any query condition, no matter how embedded the condition is or if
        it uses functions
    """

    # The left side of an equation or inequality This can be a simple Token with only a tokenType and tokenValue
    # or can be a complex token with a leftSide and rightSide. The possible embedding is of course infinite
    leftSide = None
    # The right side of an equation or inequality This can be a simple Token with only a tokenType and tokenValue
    # or can be a complex token with a leftSide and rightSide. The possible embedding is of course infinite
    rightSide = None
    # The type of the tokenValue. These are very granular. They basically are just the word description, whereas
    # the tokenValue is the actual symbol. Therse are often the same thing
    # So far we have PROPERTY, NUMBER, <, >, =, !=, AND, OR from Sproutcore, and we'll add them
    # for geometry operations
    tokenType = None
    # The actually value described by tokenType. Often the same symbol as the type, but in the case of PROPERTY
    # or NUMBER this would be the actual value
    tokenValue = None
    # This is not part of Sproutcore. To handle functions we need to be able to specify parameters and recurse.
    # So these can be simple Tokens that are tokenType and tokenValue or they be more complex Tokens
    # that embed more functions
    parameters = None

    def __init__(self, **kwargs):
        self.init_args(**kwargs)

    def init_args(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
