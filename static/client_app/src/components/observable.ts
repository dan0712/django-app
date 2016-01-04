/**
 * Created by cristian on 3/01/16.
 */
/// <reference path='../all.d.ts' />

module App{
    export class Observable<T>{
        private __listeners: Function[];
        private __value: T;
        private __primeObject:Observable<T>;

        constructor(private name:string, initialValue:T){

            // init observables
            this.__listeners = [];
            window.$AppObservables = (window.$AppObservables || (window.$AppObservables = {}));
            // create observable variable
            window.$AppObservables[this.name] = (window.$AppObservables[this.name] || (window.$AppObservables[this.name] = this));
            this.__primeObject = window.$AppObservables[this.name];
            // init state in case that the observable don't exists already
            if(this.__primeObject==this){
                this.__value = initialValue;
            }
        }


        /*
            Subscribe a new function to the listeners callback, return the function for remove the listener
            @param listener: the callback function
            @return: unbind function
         */
        subscribe(listener: Function): Function {
            // in case that is the same object
            if(this.__primeObject==this){

                this.__listeners.push(listener);
                // unbind function
                return () => {
                    this.__listeners.splice(this.__listeners.indexOf(listener), 1);
                };
            }
            else{
                return this.__primeObject.subscribe(listener);
            }


        }

        // call all the listeners
        private __callListeners():void{
            for (let listener of this.__listeners) {
                listener();
            }
        }
        /*
            set new value
        */
        set(value:T): void{
            // console.log(this.name, value);
            // in case that is the same object
            if(this.__primeObject==this) {
                this.__value = value;
                this.__callListeners()
            }
            else{
                this.__primeObject.set(value);
            }
        }

        /*
            get current value
         */
        get():T{
            // in case that is the same object
            if(this.__primeObject==this) {
                return this.__value;
            }
            else{
                return this.__primeObject.get();
            }

        }
    }
}