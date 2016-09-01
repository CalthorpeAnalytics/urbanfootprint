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


/***
 * Shows a predicted scenario painting result
 * @type {void|*|Class|SC.RangeObserver}
 */
Footprint.NonEditableResultBottomInfoView = SC.View.extend({
    classNames: ['footprint-bottom-labelled-view'],
    childViews:'nameView contentView'.w(),
    status: null,
    title: null,
    value:null,
    titleLayout: null,
    contentLayout: null,
    isSeaGreen: NO,
    isYellow: NO,
    isDarkOrange: NO,
    isOrangeBrown: NO,
    isUmber: NO,
    isDarkPurple: NO,
    isRed: NO,
    isRose: NO,
    isBlue: NO,
    isLightPurple: NO,
    isGreyBlue: YES,

    builtFormSet: null,
    builtFormSetBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormSetsController.selection'),
    activeLayer: null,
    activeLayerBinding:  SC.Binding.oneWay('.parentView.activeLayer'),
    builtFormSelection: null,
    builtFormSelectionBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController*selection.firstObject'),
    builtFormStatus: null,
    builtFormStatusBinding: SC.Binding.oneWay('Footprint.urbanBuiltFormCategoriesTreeController*content.status'),
    allFeatures: null,
    allFeaturesBinding: SC.Binding.oneWay('.parentView.content'),
    allFeaturesStatus: null,
    allFeaturesStatusBinding: SC.Binding.oneWay('*allFeatures.status'),
    developmentPercent: null,
    developmentPercentBinding: SC.Binding.oneWay('Footprint.endStateDefaultsController*content.update.dev_pct'),
    densityPercent: null,
    densityPercentBinding: SC.Binding.oneWay('Footprint.endStateDefaultsController*content.update.density_pct'),
    grossNetPercent: null,
    grossNetPercentBinding: SC.Binding.oneWay('Footprint.endStateDefaultsController*content.update.gross_net_pct'),
    isClearBase: null,
    isClearBaseBinding: SC.Binding.oneWay('Footprint.endStateDefaultsController*content.update.clear_base_flag'),
    colorIsVisible: YES,
    isWhiteFont: NO,

    nameView:  SC.LabelView.extend({
        childViews: ['styleView', 'titleView'],
        classNames: ['footprint-bold-view'],
        classNameBindings: ['isSeaGreen: theme-title-white-lightseagreen',
            'isUmber: theme-title-white-umber', 'isDarkPurple: theme-title-white-darkpurple', 'isGreyBlue: theme-title-black-greyblue'],
        isGreyBlue: null,
        isGreyBlueBinding: '.parentView.isGreyBlue',
        isSeaGreen: null,
        isSeaGreenBinding: '.parentView.isSeaGreen',
        isYellow: null,
        isYellowBinding: '.parentView.isYellow',
        isDarkOrange: null,
        isDarkOrangeBinding: '.parentView.isDarkOrange',
        isOrangeBrown: null,
        isOrangeBrownBinding: '.parentView.isOrangeBrown',
        isUmber: null,
        isUmberBinding: '.parentView.isUmber',
        isDarkPurple: null,
        isDarkPurpleBinding: '.parentView.isDarkPurple',
        isRed: null,
        isRedBinding: '.parentView.isRed',
        isRose: null,
        isRoseBinding: '.parentView.isRose',
        isBlue: null,
        isBlueBinding: '.parentView.isBlue',
        isLightPurple: null,
        isLightPurpleBinding: '.parentView.isLightPurple',
        textAlign: SC.ALIGN_CENTER,
        title: null,
        titleBinding: SC.Binding.oneWay('.parentView.title'),
        layoutBinding: SC.Binding.oneWay('.parentView.titleViewLayout'),
        colorIsVisible: null,
        colorIsVisibleBinding: '.parentView.colorIsVisible',
        isWhiteFont: null,
        isWhiteFontBinding: SC.Binding.oneWay('.parentView.isWhiteFont'),

        titleView: SC.LabelView.extend({
            layout: {left: 0, right:0},
            classNames: ['footprint-bold-view', 'theme-title-black-transparent'],
            classNameBindings: ['isWhiteFont: theme-title-white'],
            textAlign: SC.ALIGN_CENTER,
            valueBinding: SC.Binding.oneWay('.parentView.title'),
            isWhiteFont: null,
            isWhiteFontBinding: SC.Binding.oneWay('.parentView.isWhiteFont')
        }),

        styleView: SC.LabelView.extend({
            classNames: ['footprint-bold-view'],
            classNameBindings: ['isYellow: theme-title-black-yellow',
                'isDarkOrange: theme-title-black-darkorange', 'isOrangeBrown: theme-title-black-orangebrown',
                'isRed: theme-title-white-red', 'isRose: theme-title-white-rose', 'isBlue: theme-title-white-blue',
                'isLightPurple: theme-title-black-lightpurple'],
            isVisibleBinding: '.parentView.colorIsVisible',
            isYellow: null,
            isYellowBinding: '.parentView.isYellow',
            isDarkOrange: null,
            isDarkOrangeBinding: '.parentView.isDarkOrange',
            isOrangeBrown: null,
            isOrangeBrownBinding: '.parentView.isOrangeBrown',
            isRed: null,
            isRedBinding: '.parentView.isRed',
            isRose: null,
            isRoseBinding: '.parentView.isRose',
            isBlue: null,
            isBlueBinding: '.parentView.isBlue',
            isLightPurple: null,
            isLightPurpleBinding: '.parentView.isLightPurple',
            layout: {left:1, width: 14, bottom: 1, top: 1}
        })
    }),
    contentView: SC.LabelView.extend({
        classNames: ['footprint-noneditable-result--content-view'],
        textAlign: SC.ALIGN_CENTER,
        valueBinding: SC.Binding.oneWay('.parentView.value'),
        layoutBinding: SC.Binding.oneWay('.parentView.contentLayout')
    })
});
