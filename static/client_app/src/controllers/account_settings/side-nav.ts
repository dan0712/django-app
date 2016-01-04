/**
 * Created by cristian on 4/01/16.
 */
/// <reference path='../../all.d.ts' />

module App.Controllers.AccountSettings{
    "use strict";

    interface SideNavScope extends ng.IScope {
        isOpen : boolean;
    }

    /*
        controll the side nav on account settings page
     */
    export class SideNavCtrl{
        static $inject = [
            "$scope",
        ];

        constructor(public $scope:SideNavScope){
            //init
            this.$scope.isOpen = true;

        }


    }
}