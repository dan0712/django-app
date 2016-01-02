/// <reference path='../../libs/types/restangular/restangular.d.ts' />
/// <reference path='../../interfaces/client_profile.ts' />

module App.Controllers.AccountSettings{
    "use strict";
    interface ProfileScope extends ng.IScope {
        personalInfo : PersonalInfo;
        retireSmart: RetireSmart;
        user: User;
    }

    /*
        profile settings controller
        with this controller the user can change his personal info and delete the RetireSmart plan
    */
    export class ProfileCtrl{
        private profileApi:restangular.IElement;
        private userApi:restangular.IElement;
        private retireSmartApi:restangular.IElement;


        // $inject annotation.
		// It provides $injector with information about dependencies to be injected into constructor
		// it is better to have it close to the constructor, because the parameters must match in count and type.
		// See http://docs.angularjs.org/guide/di
        static $inject = [
            "$scope",
            "Restangular"
        ];


        constructor(private $scope:ProfileScope, private Restangular:restangular.IService){

            // Init apis
            this.profileApi = Restangular.all("/client/2.0/api/personal_info/");
            this.userApi = Restangular.all("/client/2.0/api/user/");

            //init personal info
            if(!this.$scope.personalInfo){
                this.loadPersonalInfo();
            }

            //init user
            if(!this.$scope.user){
                this.loadUser();
            }


        }
        /*
            Load user data (name, email, join date, etc)
         */
        loadUser():void{
            var request:restangular.ICollectionPromise<User> = this.userApi.getList<User>();
            request.then((users)=>{
                    this.$scope.user = users[0];
                }
            )

        }

        /*
            Load the personal info of the current client to the app
        */
        loadPersonalInfo():void{
            var request:restangular.ICollectionPromise<PersonalInfo> = this.profileApi.getList<PersonalInfo>();
            request.then((info)=>{
                this.$scope.personalInfo = info[0];
                }
            )
        }

        deleteRetireSmart():void{
            var request:Promise<void>  = null;
            if(!this.$scope.retireSmart){

            }
            else {
                //request = this.retireSmartApi.delete();
                //request.then(function() {
                //    this.$scope.todos = this.retireSmartApi.getList().$object;
                //})

            }

        }


    }

}