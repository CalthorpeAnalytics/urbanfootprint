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

sc_require('views/section_toolbars/edit_button_view');
sc_require('views/user_profile_menu');


Footprint.HeaderBarView = SC.View.extend({
    classNames: ['footprint-project-section-view', 'toolbar'],
    childViews: ['hamburgerView','clientView', 'clientLogoView', 'projectView',
                 'userProfileView'],

    hamburgerView: SC.ImageButtonView.extend({
        image: 'hamburger-icon',
        layout: {left: 15, width: 24, height: 24, top: 5},
        itemTitleKey: 'title',
        itemValueKey: 'value',
        isEnabledKey: 'isEnabled',
        visibleValue: null,
        menu: null,
        isDataManager: null,
        isDataManagerBinding: SC.Binding.oneWay('Footprint.scenarioActiveController*configEntityDelegate.isDataManager'),
        scenario: null,
        scenarioBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.content'),
        scenarioStatus: null,
        scenarioStatusBinding: SC.Binding.oneWay('Footprint.scenarioActiveController.status'),

        // The following configuration values are copied into all menu items
        menuConfiguration: {
            action: 'doOpenTopSection',
            width: '40',
            topSectionIsHidden: null,
            topSectionIsHiddenBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.topSectionIsVisible').not(),

            // The value of the current top section
            topSectionContentValue: null,
            topSectionContentValueBinding: SC.Binding.oneWay('Footprint.topSectionVisibleViewController.content'),

            // Indicates that this isn't the current section
            isNotSelected: function() {
                return this.get('value') != this.get('topSectionContentValue');
            }.property('topSectionContentValue', 'value').cacheable(),

            isEnabledBinding: SC.Binding.or('.topSectionIsHidden', '.isNotSelected'),
        },

        /***
         * Returns the scenarios view or data manager view, depending on the isDataManager flag
         */
        mainViewConfiguration: function() {
            return !this.get('isDataManager') ?
                SC.Object.create({
                    icon: sc_static('images/chart_icon16.png'),
                    view: 'Footprint.ManageScenarioTopSectionView',
                    value: 'scenarios',
                    title: 'Scenario Info',
                    toolTip: 'Choose from available scenarios',
                }, this.get('menuConfiguration')):
                SC.Object.create({
                    icon: sc_static('images/chart_icon16.png'),
                    view: 'Footprint.DataManagementTopSectionView',
                    value: 'projectInfo',
                    title: 'Project Info',
                    toolTip: 'Overview of the project',
                }, this.get('menuConfiguration'));
        }.property('isDataManager').cacheable(),

        items: function() {
            // Clear the menu whenever we rerequest the items
            this.set('menu', null);
            return [
                // The scenarios view or data manager view
                this.get('mainViewConfiguration'),

                // Query view
                SC.Object.create({
                    icon: sc_static('images/query_icon16.png'),
                    view: 'Footprint.QueryTopSectionView',
                    value: 'query',
                    title: 'Data Explorer',
                    action: 'doOpenTopSection',
                    disallowedBehaviors: ['behavior__remote_imagery'],
                }, this.get('menuConfiguration')),

                // Only show the approval/merge tool if this is a data manager site
                // And the user has permission to approve/merge
                this.get('isDataManager') && (this.getPath('scenario.permissions') || []).contains('merge') ?
                    SC.Object.create({
                        icon: sc_static('images/approval_icon16.png'),
                        view: 'Footprint.ApprovalTopSectionView',
                        value: 'approval',
                        title: 'Approve and Merge',
                        action: 'doOpenTopSection',
                        disallowedBehaviors: ['behavior__remote_imagery', 'behavior__base_master_scenario'],
                        allowedBehaviors: ['behavior__editable_feature'],
                        requiredPermissions: ['approve']
                    }, this.get('menuConfiguration')) : null

            ].compact();
        }.property('mainViewConfiguration', 'scenario', 'scenarioStatus').property(),

        /**
         * Creates or reveals the menu
         */
        action: function () {
            var menu = this.get('menu');
            if (!menu) {
                menu = SC.MenuPane.create(Footprint.MenuRenderMixin, {
                    anchor: this,
                    items: this.get('items'),
                    itemTitleKey:this.get('itemTitleKey'),
                    itemValueKey:this.get('itemValueKey'),
                });
                this.set('menu', menu);
            }
            menu.popup(this);
        },
    }),

    projectView: SC.View.extend({
        layout: { width: 310, left: 45 },
        contentBinding: SC.Binding.oneWay('Footprint.projectsController.arrangedObjects'),
        selectionBinding: 'Footprint.projectsController.selection',
        childViews: ['projectLabelView', 'projectSelectView'],

        projectLabelView: SC.LabelView.extend({
            classNames: ['footprint-10font-title-view'],
            layout: {width: 65, height: 16, left: 10,  centerY: 0},
            value: 'Active Project: ',
        }),

        projectSelectView: Footprint.FootprintSelectView.extend({
            layout: { left: 80, right: 10, height: 24, centerY: 0},
            contentController: Footprint.projectsController,
            itemTitleKey: 'name',
            _reloadWithProjectKey: function(projectKey, replace) {
                var url = window.location.pathname;
                var params = window.location.search;
                var paramObj = {};
                if (params && params[0] === '?') {
                    params = params.split('?')[1];
                    params.split('&').forEach(function(kv) {
                        kv = kv.split('=', 2);
                        paramObj[kv[0]] = paramObj[kv[1]];
                    });
                }
                paramObj.project = projectKey;
                var fullUrl = url + '?' + $.param(paramObj);
                Footprint.developerModeController.navigateTo(fullUrl, projectKey, replace);
            },
            valueObserver: function(context, key, value) {
                var urlProjectKey = Footprint.developerModeController.get('project');
                if (urlProjectKey != this.getPath('value.key')) {
                    // We replace the current url (rather than navigating to it) if the
                    // current project wasn't specified. This prevents an initial reload on
                    // startup if the url doesn't contain ?project=xxx.
                    this._reloadWithProjectKey(this.getPath('value.key'), !urlProjectKey);
                }
            }.observes('value'),
        }),
    }),

    clientView: SC.View.extend({
        layout: { left:.4, right:.4 },
        childViews: ['titleView'],
        titleView: SC.LabelView.create({
            layout: {left:.02, right: 0.02, height: 24, centerY: 0 },
            classNames: 'footprint-right-logo-title-view',
            value: 'UrbanFootprint Scenario Planning Model',
            textAlign: SC.ALIGN_CENTER,
        }),
    }),

    clientLogoView: SC.ImageView.extend({
        layout: { width: 145, right: 154, height: 33, centerY: 0 },
        scale: SC.BEST_FIT,
        useCanvas: NO,
        valueBinding: SC.Binding.oneWay('Footprint.regionActiveController*clientPath.logoPath'),
    }),

    userProfileView: Footprint.UserProfileMenu.extend({
        layout: { width: 140, right: 10, height: 22, centerY: 0, border: 1 },
    }),
});
