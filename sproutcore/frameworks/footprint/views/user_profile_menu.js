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


Footprint.UserProfileMenu = SC.View.extend({
    childViews: ['userDisplay', 'userMenu'],
    userBinding: SC.Binding.oneWay('Footprint.userController.content.firstObject'),
    cursor: SC.Cursor.create({
                cursorStyle: SC.HAND_CURSOR,
            }),
    userTitle: function() {
        var first_name = this.getPath('user.first_name');
        var last_name = this.getPath('user.last_name');
        if (first_name) {
            if (last_name) {
                return '%@ %@'.fmt(first_name, last_name);
            }
            return first_name;
        }

        var email = this.getPath('user.email');
        if (email) {
            return email;
        }
        return this.getPath('user.username');
    }.property('user').cacheable(),

    items: [
        SC.Object.create({
            title: 'Manage Users',
            // Hack: Use a <a> link to avoid popup blockers, but otherwise structure ourselves like an SC.MenuItemView.
            exampleView: SC.View.extend({
                classNames: SC.MenuItemView.prototype.classNames,
                childViews: [SC.LinkView.extend({
                    classNames: ['menu-item'],
                    body: '<span class="value ellipsis">Manage Users</span>',
                    escapeHTML: false,
                    href: '/footprint/users',
                })],
            }),
        }),
        SC.Object.create({
            title: 'Documentation',
            // Hack: Use a <a> link to avoid popup blockers, but otherwise structure ourselves like an SC.MenuItemView.
            exampleView: SC.View.extend({
                classNames: SC.MenuItemView.prototype.classNames,
                childViews: [SC.LinkView.extend({
                    classNames: ['menu-item'],
                    body: '<span class="value ellipsis">Documentation</span>',
                    escapeHTML: false,
                    href: 'https://urbanfootprint-v1.readthedocs.io/',
                })],
            }),
        }),
        SC.Object.create({
            title: 'Report a bug..',
            // Hack: Use a <a> link to avoid popup blockers, but otherwise structure ourselves like an SC.MenuItemView.
            exampleView: SC.View.extend({
                classNames: SC.MenuItemView.prototype.classNames,
                childViews: [SC.LinkView.extend({
                    classNames: ['menu-item'],
                    body: '<span class="value ellipsis">Support</span>',
                    escapeHTML: false,
                    href: 'https://urbanfootprint-v1.readthedocs.io/en/latest/user_support/',
                })],
            }),
        }),
        SC.Object.create({
            title: 'Logout',
            action: 'doLogout',
        }),
    ],

    addAction: function() {
        // since this action is called by this view's children, the rest of the code references parentView
        // to get back to this view
        var menu = this.getPath('parentView.menu');
        if (!menu) {
            menu = SC.MenuPane.create(Footprint.MenuRenderMixin, {
                items: this.getPath('parentView.items'),
            });
            this.setPath('parentView.menu', menu);
        }
        menu.popup(this.get('parentView'));
    },

    userDisplay: SC.LabelView.extend({
        layout: { right: 30, width: 100, height: 24 },
        classNames: ['footprint-user-label'],
        value: '(none)',
        valueBinding: SC.Binding.oneWay('.parentView.userTitle'),
        click: null,
        clickBinding: SC.Binding.oneWay('.parentView.addAction'),
        cursor: null,
        cursorBinding: SC.Binding.oneWay('.parentView.cursor'),
    }),

    userMenu: SC.ImageButtonView.extend({
        layout: { width: 24, height: 24, right: 2, top: 0 },
        classNames: ['footprint-user-menu'],
        image: 'user-icon',
        title: '(no email)',
        titleBinding: SC.Binding.oneWay('.parentView.userTitle'),
        action: null,
        actionBinding: SC.Binding.oneWay('.parentView.addAction'),
        cursor: null,
        cursorBinding: SC.Binding.oneWay('.parentView.cursor'),
    }),

});
