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


// Modified based on http://broadcastingadam.com/2011/04/sproutcore_login_tutorial/
// The login page should only show up when the user hasn't logged in before. We'll store a cookie with the username and apiKey afterward
Footprint.loginPage = SC.Page.design({
    mainPane: SC.MainPane.design({
        childViews: 'loginContainerView'.w(),
        defaultResponder: 'Footprint.statechart',

        loginContainerView: SC.View.extend({
            layout: { width: 350, height: 600, centerX: 0, centerY: 0},

            childViews: 'loginForm ufLogoView clientLogoView logoView scagLogoView'.w(),

            ufLogoView: SC.ImageView.extend({
                classNames:'client-logo-image'.w(),
                useCanvas:NO,
                layout: {centerX: 0, top: 0, width:200, height:200},
                value:  sc_static('images/loading.png'),
            }),
            clientLogoView: SC.ImageView.extend({
                classNames:'client-logo-image'.w(),
                useCanvas: NO,
                layout: {centerX: 0, top: 210, width: 335, height: 105},
                value: sc_static('images/client_login_page_logo.png'),
            }),

            loginForm: SC.View.design({
                layout: {centerX: 0, top: 315, width: 320, height: 160 },
                childViews: 'email password loginButton'.w(),

                email: SC.TextFieldView.design({
                    layout: { width: 300, height: 30, top: 30, centerX: 0},
                    hint: 'Email address',
                    valueBinding: 'Footprint.loginController.email',
                    didCreateLayer: function() {
                        sc_super();
                        this.becomeFirstResponder();
                    },
                }),

                password: SC.TextFieldView.design({
                    layout: {  width: 300, height: 30, top: 80, centerX: 0 },
                    hint: 'Password',
                    type: 'password',
                    valueBinding: 'Footprint.loginController.password',
                }),

                loginButton: SC.ButtonView.design({
                    layout: { width: 100, height: 30, top: 120, centerX: 0 },
                    controlSize: SC.HUGE_CONTROL_SIZE,
                    isEnabledBinding: SC.Binding.and('Footprint.loginController.email', 'Footprint.loginController.password'),
                    title: 'Login',
                    action: 'doAuthenticate',
                    isDefault: YES,

                }),
            }),

            scagLogoView: SC.ImageView.extend({
                classNames:'logo-image'.w(),
                useCanvas:NO,
                layout: {centerX: 5, top: 505, width:210, height:37},
                value: sc_static('images/client_login_page_logo_lower.png'),
            }),

            logoView: SC.ImageView.extend({
                classNames:'logo-image'.w(),
                useCanvas:NO,
                layout: {centerX: 0, top: 548, width:200, height:35},
                cursor: SC.Cursor.create({
                    cursorStyle: SC.HAND_CURSOR,
                }),
                value: sc_static('images/Analytics_Logo_GreyLetters.png'),
                click: function() {
                    window.open('http://calthorpeanalytics.com/');
                    return YES;
                },
            }),
        }),
    }),
    loginBypassPane: SC.MainPane.extend({
        childViews: 'loadingView progressView'.w(),

        loadingView: SC.ImageView.extend({
            classNames:'loading-image'.w(),
            useCanvas:NO,
            layout: {centerX: 0, centerY:0, width:500, height:500},
            value: sc_static('images/loading.png'),
        }),
        progressView: SC.ProgressView.extend({
            layout: {centerX:.0001, centerY:0, width:.2, height:16, top:0.9},
            valueBinding:SC.Binding.oneWay('Footprint.loadingStatusController.content'),
            minimum:0,
            maximum:10,
        }),
    }),
});
