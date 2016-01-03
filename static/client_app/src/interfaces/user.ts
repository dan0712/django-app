/// <reference path='../all.d.ts' />

module App{

    /*
     *   ============================================================
     *                            User Api
     *   ============================================================
     */

    var userApi = `${apiEndpoint}/user/`;

    export class User{
        pk: number;
        first_name: string;
        middle_name: string;
        last_name: string;
        email: string;
        date_joined: string;
    }

    interface UserScope  extends ng.IScope {
        user: User;
    }

    /*
     * Contains commons function for manage user data
     */
    export class UserMixin {
        Restangular:restangular.IService;
        $scope:UserScope;

        /*
         Load user data (name, email, join date, etc) of the current client to the app
         */
        loadUser():void{
            var request:restangular.ICollectionPromise<User> = this.Restangular.all(userApi).getList<User>();
            request.then((users)=>{
                    this.$scope.user = users[0];
                }
            )
        }
    }


    export  class RetireSmart {
        is_active: boolean;
    }

    export class PricingPlan{
        value: number;
    }

}
