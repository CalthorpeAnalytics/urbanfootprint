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

sc_require('views/style_render_mixin');

Footprint.ListItemView = SC.ListItemView.extend(Footprint.StyleRenderMixin, {
    classNames: ['footprint-list-item'],
    displayProperties:['layerVisible'],
    contentValueKey: 'title',
    contentCheckboxKey: 'layerVisible',
    styleClass: 'footprint-legend-medium-color',
    labelStyleClass: 'footprint-legend-item-style-label-view',
    labelLayerClassNoToggle: 'footprint-legend-item-layer-label-no-toggle-view',
    labelLayerClassToggle: 'footprint-legend-item-layer-label-toggle-view',
    labelAttributeClassNoToggle: 'footprint-legend-item-attribute-label-no-toggle-view',
    labelAttributeClassToggle: 'footprint-legend-item-attribute-label-toggle-view',
    selectedObject: null,
    selectedObjectBinding: SC.Binding.oneWay('.parentView*selection.firstObject'),

    /***
     * This should be overridden in the subclass to do specific rendering at certain tree
     * levels by inspecting the current content. By default this just calls renderLabel
     * @param content
     * @param context
     * @param key
     * @param value
     * @param working
     */
    renderForTreeLevel: function (content, context, key, value, working) {
        value = (key && content) ? (content.get ? content.get(key) : content[key]) : content;
        if (value && SC.typeOf(value) !== SC.T_STRING) value = value.toString();
        this.renderLabel(working, value);
    },

    isSelectedObserver: function () {
        if (this.get('selectedObject') && this.get('content')) {
            if (this.getPath('selectedObject.id') === this.getPath('content.id')) {
                this.set('isSelected', YES);
                this.get('content').set(this.get('contentCheckboxKey'), YES);

            } else {
                this.set('isSelected', NO);
            }
        }
    }.observes('.selectedObject'),

    style: function () {
        if (this.get('content') && this.getPath('content.style')) {
            return this.getPath('content.style');
        }
    }.property('content').cacheable(),


    render: function (context, firstTime) {
        var content = this.get('content'),
            del = this.displayDelegate,
            level = this.get('outlineLevel'),
            indent = this.get('outlineIndent'),
            key, value, working, classArray = [];

        //make all style example views be unable to be selected
        if (content.get('isStyle') || (content.get('isAttribute'))) {
            this.set('isSelected', NO);
        }
        // add alternating row classes
        classArray.push((this.get('contentIndex') % 2 === 0) ? 'even' : 'odd');
        context.setClass('disabled', !this.get('isEnabled'));
        context.setClass('drop-target', this.get('isDropTarget'));

        // outline level wrapper
        working = context.begin('div').addClass('sc-outline');
        if (level >= 0 && indent > 0) working.addStyle('left', indent * (level + 1));

        // handle disclosure triangle
        value = this.get('disclosureState');
        if (value !== SC.LEAF_NODE) {
            this.renderDisclosure(working, value);
            classArray.push('has-disclosure');
        } else if (this._disclosureRenderSource) {
            // If previously rendered a disclosure, clean up.
            context.removeClass('has-disclosure');
            this._disclosureRenderSource.destroy();
            this._disclosureRenderSource = this._disclosureRenderDelegate = null;
        }
        // handle checkbox - render of child content is a layer
        key = this.getDelegateProperty('contentCheckboxKey', del);
        if (key) {
            value = content ? (content.get ? content.get(key) : content[key]) : NO;
            if (value !== null && content.get('hasCheckBox')) {
                this.renderCheckbox(working, value);
                classArray.push('has-checkbox');
            } else if (this._checkboxRenderSource) {
                // If previously rendered a checkbox, clean up.
                context.removeClass('has-checkbox');
                this._checkboxRenderSource.destroy();

                this._checkboxRenderSource = this._checkboxRenderDelegate = null;
            }
        }
        // handle label -- always invoke - logic handles whether the example view will be render with CSS styling
        // for layer views or style views
        key = this.getDelegateProperty('contentValueKey', del);
        value = this.renderForTreeLevel(content, context, key, value, working);
        context.addClass(classArray);
        context = working.end();
    },
});
