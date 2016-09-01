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

/*eslint-env mocha*/
/*global start,stop*/

/**
 * This is a wrapper around a SproutCore test that needs to call
 * start() and stop(), to match Mocha-style async tests.
*
 * To use, just wrap the test function with this.

 * Replace this:
 *
 *     test('some event fires', function() {
 *         doSomething();
 *         stop(1000);
 *         setTimeout(function() {
 *             start();
 *             equals(newValue, expectedValue);
 *         });
 *     });
 *
 * With this:
 *
 *     test('some event fires', AsyncTest(function(done) {
 *         doSomething();
 *         setTimeout(function() {
 *             equals(newValue, expectedValue);
 *             done();
 *         });
 *     });
 *
 * @param {Function} fn testing function.
 * @param {Number} timeoutMs Test timeout in ms (defaults to 10s)
 */
function AsyncTest(fn, timeoutMs) {
    timeoutMs = timeoutMs || 10000;
    function runTest() {
        stop(timeoutMs);
        fn(start);
    }

    return runTest;
}
