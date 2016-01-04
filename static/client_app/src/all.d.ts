/// <reference path='libs/types/jquery/jquery.d.ts' />
/// <reference path='libs/types/angularjs/angular.d.ts' />
/// <reference path='libs/types/angular-ui-router/angular-ui-router.d.ts' />
/// <reference path='libs/types/restangular/restangular.d.ts' />


/*
    Components
 */
/// <reference path='components/observable.ts' />
/// <reference path='components/modal.ts' />

/*
    interfaces
 */
/// <reference path='interfaces/endpoint.ts' />
/// <reference path='interfaces/personal_info.ts' />
/// <reference path='interfaces/user.ts' />
/*
    Controllers
 */
/// <reference path='controllers/account_settings/profile.ts' />
/// <reference path='controllers/account_settings/side-nav.ts' />
/// <reference path='controllers/global_progress_bar.ts' />


declare function applyMixins(derivedCtor: any, baseCtors: any[]):void;

interface Window{
    $AppObservables: {[observName: string] : App.Observable<any>};
}