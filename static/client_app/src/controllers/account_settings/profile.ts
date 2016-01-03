/// <reference path='../../interfaces/user.ts' />
/// <reference path='../../interfaces/personal_info.ts' />
/// <reference path='../../all.d.ts' />

module App.Controllers.AccountSettings{
    "use strict";

    interface ProfileScope extends ng.IScope {
        personalInfo : PersonalInfo;
        retireSmart: RetireSmart;
        user: User;
        profile: ProfileCtrl;
    }

    /*
        profile settings controller
        with this controller the user can change his personal info and delete the RetireSmart plan
    */
    export class ProfileCtrl implements PersonalInfoMixin, UserMixin{

        //personal info methods
        loadPersonalInfo:()=>void;

        //user methods
        loadUser:()=>void;


        // $inject annotation.
		// It provides $injector with information about dependencies to be injected into constructor
		// it is better to have it close to the constructor, because the parameters must match in count and type.

        static $inject = [
            "$scope",
            "Restangular",
            "ModalService"
        ];

        constructor(public $scope:ProfileScope, public Restangular:restangular.IService, public ModalService){

            //init personal info
            if(!this.$scope.personalInfo){
                this.loadPersonalInfo();
            }

            //init user
            if(!this.$scope.user){
                this.loadUser();
            }

            //add instance methods
            this.$scope.profile = this;

        }

        /*
         * launch profile information edit modal
         */
        showPersonalInfoEditModal():void{
            // Just provide a template url, a controller and call 'showModal'.
            this.ModalService.showModal({
                templateUrl: "/static/client_app/public/views/account_settings/personal_info_modal.html",
                controller: "AccountSettingsPersonalInfoModalCtrl"
            }).then(function(modal) {
                // load new modal
                var modalObject = new Modal(modal.element, {animationDuration:'.5s',
                    animatedIn:'bounceInUp', animatedOut:'bounceOutDown'});
                modalObject.show();

            });

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

    applyMixins(ProfileCtrl, [PersonalInfoMixin, UserMixin]);

    /*
                                    PersonalInfoModalCtrl
                                    ----------------------

       this controller allow save personal info data from a modal
     */

    interface PersonalInfoModalScope extends ng.IScope{
        personalInfo:PersonalInfo;
        modal: PersonalInfoModalCtrl;

    }
    export class PersonalInfoModalCtrl implements  PersonalInfoMixin{

        //personal info methods
        loadPersonalInfo:()=>void;

        static $inject = [
            "$scope",
            "Restangular",
            "ModalService",
            "close"
        ];

        constructor(public $scope:PersonalInfoModalScope, public Restangular:restangular.IService,
                    public ModalService, public close){

            //init personal info
            if(!this.$scope.personalInfo){
                this.loadPersonalInfo();
            }

            this.$scope.modal  = this;


        }

        dismiss():void{
            //close, but give 500ms for animation
            this.close(null, 500);
        }

    }
    applyMixins(PersonalInfoModalCtrl, [PersonalInfoMixin]);


}