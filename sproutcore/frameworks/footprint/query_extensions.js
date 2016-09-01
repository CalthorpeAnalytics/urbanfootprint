/*
 * UrbanFootprint v1.5
 * Copyright (C) 2016 Calthorpe Analytics
 *
 * This file is part of UrbanFootprint version 1.5
 *
 * UrbanFootprint is distributed under the terms of the GNU General
 * Public License version 3, as published by the Free Software Foundation. This
 * code is distributed WITHOUT ANY WARRANTY, without implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 * Public License v3 for more details; see <http://www.gnu.org/licenses/>.
 */


Footprint.queryLanguage = SC.clone(SC.Query.create().queryLanguage)
Footprint.queryLanguage.WHERE_COUNT = { reservedWord: YES, rightType: 'BOOLEAN', evalType: 'PRIMITIVE' }
Footprint.queryLanguage.WHERE_AVG = { reservedWord: YES, rightType: 'BOOLEAN', evalType: 'PRIMITIVE' }
Footprint.queryLanguage.WHERE_SUM = { reservedWord: YES, rightType: 'BOOLEAN', evalType: 'PRIMITIVE' }
// t = q.tokenizeString("COUNT(poster=5)", q.queryLanguage)
// tr = q.buildTokenTree(t, q.queryLanguage)
Footprint.queryLanguage.COUNT = { reservedWord: YES, rightType: 'PRIMITIVE', evalType: 'PRIMITIVE' }
Footprint.queryLanguage.AVG = { reservedWord: YES, rightType: 'PRIMITIVE', evalType: 'PRIMITIVE' }
Footprint.queryLanguage.SUM = { reservedWord: YES, rightType: 'PRIMITIVE', evalType: 'PRIMITIVE' }
Footprint.queryLanguage.MAX = { reservedWord: YES, rightType: 'PRIMITIVE', evalType: 'PRIMITIVE' }
Footprint.queryLanguage.MIN = { reservedWord: YES, rightType: 'PRIMITIVE', evalType: 'PRIMITIVE' }

Footprint.queryLanguage.AREA = { reservedWord: YES, rightType: 'PRIMITIVE', evalType: 'PRIMITIVE' }

// Basic query handling. This will be improved
/***
 * Parses a SproutCore formatted query string returning a toke tree if successful, otherwise throws
 * @param queryString
 * @param requireQueryType Default null.
 *   If 'equation' requires that the queryString be an equation, not just a value. (e.g. 'foo = 1', not 'foo')
 *   If 'aggregate' requires an aggregate function, such as 'SUM(foo)'
 * @returns {Object}
 */
Footprint.processQuery = function(queryString, requireQueryType) {
    var queryFactory = SC.Query.create();
    var tokenList = queryFactory.tokenizeString(queryString, Footprint.queryLanguage);
    if (tokenList.error)
        throw tokenList.error;
    try {
        var tree = queryFactory.buildTokenTree(tokenList, Footprint.queryLanguage);
        if (requireQueryType == 'equation')
            if (!(tree['tokenType'] && tree['tokenValue'] && tree['leftSide'] && tree['rightSide']))
                tree.error = new Error("Expected aggregate function");
        if (requireQueryType == 'aggregate')
            if (!(tree['tokenType'] && tree['tokenValue'] && tree['rightSide']))
                tree.error = new Error("Expected aggregate function");
        return tree;
    }
    catch(e) {
        logWarning("Unexpected buildTokenTree failure for %@".fmt(queryString))
        return null;
    }
}

/***
 * Returns the single clause or the rightSide clause of the desired position
 * @param tokenTree: The tokenTree to parse
 * @param tokenTypes: The permitted token types for the sought clause
 * @param position: The position of the clause. 0 would be the main clause and
 * -1 would be the right-most rightSide clause (or main clause if no rightSide clause exists)
 */
function rightSideClause(tokenTree, tokenTypes, position) {
    var rightSideClauses = [];
    var rightSideClause = tokenTree;
    var pos = 0;
    while (rightSideClause && pos != position) {
        rightSideClauses.push(rightSideClause);
        pos++;
        if (rightSideClause['rightSide'])
            rightSideClause = rightSideClause['rightSide'];
        else
            break
    }
    // If position is negative take a slice of the array. If >= 0 we already have the right value
    rightSideClause = position < 0 ? rightSideClauses.slice(position)[0] : rightSideClause;

    // If no tokenTypes right the right-most clause
    if (!tokenTypes)
        return rightSideClause;
    // Find the last clause with one of the tokenTypes
    if (rightSideClause && tokenTypes.contains(rightSideClause['tokenType']))
        return rightSideClause;
    return null;
}
