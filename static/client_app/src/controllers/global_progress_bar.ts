/// <reference path='../all.d.ts' />

module App.Controllers{
     "use strict";

     interface GlobalProgressBarScope extends ng.IScope {
        currentRequests : boolean;
     }

    /*
        Control when to show the global progressbar
     */
    export class GlobalProgressBarCtrl{

        // $inject annotation.
		// It provides $injector with information about dependencies to be injected into constructor
		// it is better to have it close to the constructor, because the parameters must match in count and type.

        static $inject = [
            "$scope",
        ];

        constructor(public $scope:GlobalProgressBarScope){

            // init
            if(!this.$scope.currentRequests){
                this.$scope.currentRequests = false;
            }

            // listen the global observable
            let currentRequests = new Observable<number>("currentRequests", 0);
            let unSubscribe = currentRequests.subscribe(()=>{
                this.$scope.currentRequests = currentRequests.get()>0;
            });
            //unbind
            this.$scope.$on("$destroy", (event:ng.IAngularEvent)=>{unSubscribe()});

        }


    }

}