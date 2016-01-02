/// <reference path='libs/types/angularjs/angular.d.ts' />
/// <reference path='libs/types/angular-ui-router/angular-ui-router.d.ts' />
/// <reference path='controllers/account_settings/profile.ts' />

module App{
    "use strict";
    var BetasmartzClientApp = angular.module('BetasmartzClientApp', ['ui.router', 'restangular']);

    //Add controllers
    BetasmartzClientApp.controller("AccountSettingsProfileCtrl", Controllers.AccountSettings.ProfileCtrl);

    /*
        App Configuration
     */
    class AppConfig{
        constructor(private $stateProvider:angular.ui.IStateProvider,
                    private $urlRouterProvider:angular.ui.IUrlRouterProvider){

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

        }
    }

    //configure
    BetasmartzClientApp.config(["$stateProvider", "$urlRouterProvider",
        ($stateProvider, $urlRouterProvider) =>
        {
            return new AppConfig($stateProvider, $urlRouterProvider);
        }
    ]);

}

