/// <reference path='all.d.ts' />


module App{
    "use strict";
    var BetasmartzClientApp = angular.module('BetasmartzClientApp',
        ['ui.router',
         'ngAnimate',
         'restangular',
         'ngMaterial',
         'ngMessages',
         'angularModalService',
         'ngMask']);

    /*
        ============================================
                        Add controllers
        ==============================================
     */

    // progress bar
    BetasmartzClientApp.controller("GlobalProgressBarCtrl", Controllers.GlobalProgressBarCtrl);

    //account settings
    BetasmartzClientApp.controller("AccountSideNavCtrl", Controllers.AccountSettings.SideNavCtrl);
    BetasmartzClientApp.controller("AccountSettingsProfileCtrl", Controllers.AccountSettings.ProfileCtrl);
    BetasmartzClientApp.controller("AccountSettingsPersonalInfoModalCtrl", Controllers.AccountSettings.PersonalInfoModalCtrl);

    /*
        App Configuration
     */
    class AppConfig{
        constructor(private $stateProvider:angular.ui.IStateProvider,
                    private $urlRouterProvider:angular.ui.IUrlRouterProvider,
                    private $mdThemingProvider,
                    private RestangularProvider:restangular.IProvider){

            this.$urlRouterProvider.otherwise("/settings/profile");
            this.$stateProvider
              // --------------------
              // Account settings tab
              // ---------------------
              .state('settings', {
                  url: '/settings',
                  abstract: true,
                  templateUrl: '/static/client_app/public/views/account_settings/layout.html'
              })
              .state('settings.profile', {
                  url: '/profile',
                  views:{
                      'content':{
                          templateUrl: '/static/client_app/public/views/account_settings/profile.html',
                          controller:'AccountSettingsProfileCtrl'
                      }
                  }
              });

            // Theme
            $mdThemingProvider.theme('default').primaryPalette('green').accentPalette('teal');
            $mdThemingProvider.theme('backGreen').backgroundPalette('green').dark();
            $mdThemingProvider.theme('alternative').primaryPalette('lime');
            $mdThemingProvider.theme('dark').primaryPalette('grey').accentPalette('green').dark();



            // ==============================================
            //  global configuration restangular
            // ==============================================
            RestangularProvider.addResponseInterceptor(function(data, operation, what, url, response, deferred) {
                //When there is a new response decrease the number of current requests
                let currentRequests = new Observable<number>("currentRequests", 0);
                let currentRequestsLength = currentRequests.get();
                if(currentRequestsLength>0){
                    currentRequestsLength -= 1;
                }
                currentRequests.set(currentRequestsLength);

                return data;
            });

            RestangularProvider.addRequestInterceptor(function(element, operation, what, url) {
                //When there is a new request increase the number of current requests
                let currentRequests = new Observable<number>("currentRequests", 0);
                let currentRequestsLength = currentRequests.get();
                currentRequestsLength += 1;
                currentRequests.set(currentRequestsLength);

                return element;
            })


        }
    }

    //configure
    BetasmartzClientApp.config(["$stateProvider", "$urlRouterProvider", "$mdThemingProvider", "RestangularProvider",
        ($stateProvider, $urlRouterProvider, $mdThemingProvider, RestangularProvider) =>
        {
            return new AppConfig($stateProvider, $urlRouterProvider, $mdThemingProvider, RestangularProvider);
        }
    ]);

}

