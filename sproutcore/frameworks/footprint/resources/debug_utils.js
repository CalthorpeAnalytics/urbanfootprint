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


// TODO these should be mixed into SC.Observable
/***
 * short-cut to getPath
 * @param obj
 * @param path
 * @returns {*}
 */
function g(obj, path) {
    return obj.getPath(path);
}
/***
 * short-cut to status
 * @param obj
 * @param path
 * @returns {*}
 */
function s(obj, path) {
    return path ? obj.getPath(path + '.status') : obj.get('status');
}
/***
 * short-cut to constructor
 * @param obj
 * @param path
 * @returns {*}
 */
function c(obj, path) {
    return path ? obj.getPath(path + '.constructor') : obj.get('constructor');
}
/***
 * short-cut to firstObject.toString()
 * @param obj
 * @param path
 * @returns {*}
 */
function f(obj, path) {
    return (path ? obj.getPath(path + '.firstObject') : obj.get('firstObject')).toString();
}
/***
 * short-cut to firstObject.constructor
 * @param obj
 * @param path
 * @returns {*}
 */
function fc(obj, path) {
    return (path ? obj.getPath(path + '.firstObject.constuctor') : obj.getPath('firstObject.constructor'));
}
/***
 * short-cut to length
 * @param obj
 * @param path
 * @returns {*}
 */
function l(obj, path) {
    return path ? obj.getPath(path + '.length') : obj.get('length');
}

function ts(obj, path) {
    return path ? obj.getPath(path).toString() : obj.toString();
}

function a(record, path) {
    return path ? record.getPath(path + '.attributes') : record.get('attributes')
}
