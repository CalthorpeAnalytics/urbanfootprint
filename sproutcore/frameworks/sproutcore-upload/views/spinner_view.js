/*-------------------------------------------------------------------------------------------------
 - Project:   sproutcore-upload                                                                   -
 - Copyright: ©2013 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/


/*-------------------------------------------------------------------------------------------------
 - Project:   Matygo Internal SproutCore                                                          -
 - Copyright: ©2012 Matygo Educational Incorporated operating as Learndot                         -
 - Author:    Joe Gaudet (joe@learndot.com) and contributors (see contributors.txt)               -
 - License:   Licensed under MIT license (see license.js)                                         -
 -------------------------------------------------------------------------------------------------*/

SC.SpinnerView = SC.View.extend({
    classNames: 'sc-spinner-view-container contain dark rounded',

    layout: {
        height: 60,
        width: 60,
        centerX: 0,
        centerY: 0
    },

    childViews: [ 'spinner' ],

    spinner: SC.View.extend({
        classNames: 'sc-spinner-view spin',
        currentNumber: 1,
        maxNumber: 12,
        interval: 83,
        timer: null,

        layout: {
            height: 42,
            width: 42,
            centerX: 0,
            centerY: 0
        },

        isVisibleDidChange: function () {
            if (this.get('isVisible')) {
                this.animate();
            }
        }.observes('.parentView.isVisible'),

        animate: function () {
            var self = this;
            var animation = function (time) {
                if (self.getPath('parentView.isVisible')) {
                    window.requestAnimationFrame(animation);
                }

                if (Math.round(time) % 2 === 0) {
                    self.nextSlice(self);
                }
            };
            window.requestAnimationFrame(animation);
        },

        nextSlice: function (target) {
            var current = target.get('currentNumber');
            var max = target.get('maxNumber');

            // add new class && remove old class
            var numberToAdd = (current + 1) % max;
            target.$().addClass('spin-' + (numberToAdd + 1)).removeClass('spin-' + (current + 1));

            // set new current
            target.currentNumber = numberToAdd;
        }
    })
});
