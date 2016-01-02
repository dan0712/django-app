/**
 * Common ubterface of objects that can be used in different controllers
 */
module App{


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
    }

    export class User{
        pk: number;
        first_name: string;
        middle_name: string;
        last_name: string;
        email: string;
        date_joined: string;
    }

    export  class RetireSmart {
        is_active: boolean;
    }

    export class PricingPlan{
        value: number;
    }

}