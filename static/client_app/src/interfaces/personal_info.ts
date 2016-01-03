/// <reference path='../all.d.ts' />

/**
 * Common interfaces of objects that can be used in different controllers
 */

module App{
    "use strict";

    /*
     *   ============================================================
     *                           Personal Info Api
     *   ============================================================
    */

    var personalInfoApi = `${apiEndpoint}/personal_info/`;

    export  class PersonalInfo{
        pk: number;
        address_line_1: string
        address_line_2: string;
        city: string;
        state: string;
        post_code: number;
        phone: number;
        employment_status: string;
        income: number;
        net_worth: number;
        create_date: string;
        states_codes: {db_value:string, name:string}[];
    }

    interface PersonalInfoScope  extends ng.IScope {
        personalInfo: PersonalInfo;
    }

    /*
     * Contains commons function for manage the personal info
     */
    export class PersonalInfoMixin {
        Restangular:restangular.IService;
        $scope:PersonalInfoScope;

        /*
         Load the personal info of the current client to the app
         */
        loadPersonalInfo():void{
            var request:restangular.ICollectionPromise<PersonalInfo> = this.Restangular.all(personalInfoApi).getList<PersonalInfo>();            request.then((info)=>{
                    this.$scope.personalInfo = info[0];
                }
            )
        }
    }



}