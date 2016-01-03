/// <reference path='all.d.ts' />

module App{
    "use strict";
    var BetasmartzClientApp = angular.module('BetasmartzClientApp',
        ['ui.router',
         'restangular',
         'ngMaterial',
         'angularModalService',
         'ngMask']);

    //Add controllers
    BetasmartzClientApp.controller("AccountSettingsProfileCtrl", Controllers.AccountSettings.ProfileCtrl);
    BetasmartzClientApp.controller("AccountSettingsPersonalInfoModalCtrl", Controllers.AccountSettings.PersonalInfoModalCtrl);

    /*
        App Configuration
     */
    class AppConfig{
        constructor(private $stateProvider:angular.ui.IStateProvider,
                    private $urlRouterProvider:angular.ui.IUrlRouterProvider, private $mdThemingProvider){

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

        }
    }

    //configure
    BetasmartzClientApp.config(["$stateProvider", "$urlRouterProvider", "$mdThemingProvider",
        ($stateProvider, $urlRouterProvider, $mdThemingProvider) =>
        {
            return new AppConfig($stateProvider, $urlRouterProvider, $mdThemingProvider);
        }
    ]);

}

