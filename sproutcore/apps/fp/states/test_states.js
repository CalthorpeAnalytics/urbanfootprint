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


sc_require('views/main_pane');
sc_require('states/logging_in_state');

if (!Footprint.DO_STATE_TESTS) {
    Footprint.TestState = SC.State;
    Footprint.TestAppState = SC.State;
}
else {
Footprint.TestState = SC.State.extend({
    initialSubstate: 'loadingState',

    // Override this with the needed dependencies
    loadingState: Footprint.LoadingConcurrentDependenciesState,

    readyState: SC.State.extend({
        substatesAreConcurrent: YES,
        modalState:SC.State.plugin('Footprint.CrudState'),

        enterState: function() {
            Footprint.mainPage.get('mainPane').append();
        },
        exitState: function() {
            Footprint.mainPage.get('mainPane').remove();
        }
    })

});

Footprint.TestAppState = SC.State.extend({

    initialSubstate:'readyState',
    readyState: SC.State,

    // Test to make sure that the Footprint.LabelSelectView functions (test it on BuiltForm)
    testLabelSelectViewState: Footprint.TestState.extend({
        loadingState: Footprint.LoadingConcurrentDependenciesState.extend({
            didLoadConcurrentDependencies: function() {
                Footprint.statechart.gotoState('%@.readyState'.fmt(this.getPath('parentState.name')));
            },
            loadingBuiltFormSetsState: SC.State.plugin('Footprint.LoadingBuiltFormSetsState'),
            loadingBuiltFormTagsState:SC.State.plugin('Footprint.LoadingBuiltFormTagsState')
        })
    }),

    // Test to make sure that the Footprint.EditButtonView menu works (test it on BuiltForm)
    testActionMenuState: Footprint.TestState.extend({
        loadingState: Footprint.LoadingConcurrentDependenciesState.extend({
            didLoadConcurrentDependencies: function() {
                Footprint.statechart.gotoState('%@.readyState'.fmt(this.getPath('parentState.name')));
            },
            loadingBuiltFormSetsState: SC.State.plugin('Footprint.LoadingBuiltFormSetsState'),
            loadingBuiltFormTagsState:SC.State.plugin('Footprint.LoadingBuiltFormTagsState')
        })
    }),

    // Test to make sure that Scenario cloning works
    testScenarioClone: Footprint.TestState.extend({
        loadingState: Footprint.LoadingConcurrentDependenciesState.extend({
            didLoadConcurrentDependencies: function() {
                Footprint.statechart.gotoState('%@.readyState'.fmt(this.getPath('parentState.name')));
            },

            loadingCategoriesState: SC.State.plugin('Footprint.LoadingCategoriesState')
        })
    }),

    testScenario: Footprint.TestState.extend({

    })
});

Footprint.testController = SC.ObjectController.create({
    content: ['testLabelSelectViewState']
});
Footprint.MainPane.reopen({
    childViews: 'testTitle projectSectionView leftlogoView rightlogoView accountView splitView'.w(),

    testTitle: SC.LabelView.extend({
        classNames: ['footprint-test-title'],
        layout: {left:0.7, width:0.2, height:24},
        valueBinding:SC.Binding.oneWay('Footprint.testController.content').transform(function(value) {
            if (value)
                return 'Running Test: %@'.fmt(value);
        })
    })
});

Footprint.LoggingInState.reopen({
    didCompleteLogin: function() {
        this.gotoState('testLabelSelectViewState');
    }
});
}
