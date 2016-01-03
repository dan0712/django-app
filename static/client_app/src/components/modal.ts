/// <reference path='../libs/types/jquery/jquery.d.ts' />
/**
 * Created by cristian on 3/01/16.
 */

module App {
    "use strict";
    /*
     modal based in https://github.com/joaopereirawd/animatedModal.js

     Options
     ----------------------------------------------------------------------------------------
     Variable	        Default Value	            Options	Description
     ---------------------------------------------------------------------------------------
     modalTarget	    animatedModal		        Customize your target
     color	            #39BEB9	HEX, HSL, RGB, RBA	Define background color
     animatedIn	        zoomIn	                    Choose Here	Transition when the modal goes in
     animatedOut	    zoomOut	                    Choose Here	Transition when the modal goes out
     animationDuration	.6s	                        seconds	Animation duration
     overflow	        auto scroll; hidden; auto;	This makes your modal scrollable or not
     */

    export interface ModalOptions {
        position?:string;
        width?:string;
        height?:string;
        top?:string;
        left?:string;
        zIndexIn?:string;
        zIndexOut?:string;
        color?:string;
        opacityIn?:string;
        opacityOut?:string;
        animatedIn?:string;
        animatedOut?:string;
        animationDuration?:string;
        overflow?:string;
        // Callbacks
        beforeOpen?:Function;
        afterOpen?:Function;
        beforeClose?: Function;
        afterClose?: Function;
    }

    export class Modal {
        settings:ModalOptions;
        modal:JQuery;
        modalId:string;

        constructor(element:HTMLElement, options?:ModalOptions) {
            this.modal = jQuery(element);
            this.modalId = this.modal.attr("id");

            if ((!this.modalId) || (this.modalId = "")) {
                //add random id to the new modal
                this.modalId = "modal_" + generateRandomId();
                this.modal.attr("id", this.modalId);
            }

            //Defaults
            this.settings = jQuery.extend({
                modalTarget: 'animatedModal',
                position: 'fixed',
                width: '100%',
                height: '100%',
                top: '0px',
                left: '0px',
                zIndexIn: '9999',
                zIndexOut: '-9999',
                color: '#FFFFFF',
                opacityIn: '1',
                opacityOut: '0',
                animatedIn: 'zoomIn',
                animatedOut: 'zoomOut',
                animationDuration: '.6s',
                overflow: 'auto',
                // Callbacks
                beforeOpen: function () {
                },
                afterOpen: function () {
                },
                beforeClose: function () {
                },
                afterClose: function () {
                }
            }, options);

            // Default Classes
            this.modal.addClass('animated');
            this.modal.addClass(this.modalId+'-off');

            //Init styles
            var initStyles = {
                'position': this.settings.position,
                'width': this.settings.width,
                'height': this.settings.height,
                'top': this.settings.top,
                'left': this.settings.left,
                'background-color': this.settings.color,
                'overflow-y': this.settings.overflow,
                'z-index': this.settings.zIndexOut,
                'opacity': this.settings.opacityOut,
                '-webkit-animation-duration': this.settings.animationDuration,
                '-moz-animation-duration': this.settings.animationDuration,
                '-ms-animation-duration': this.settings.animationDuration,
                'animation-duration': this.settings.animationDuration
            };
            //Apply stles
            this.modal.css(initStyles);

            //listen close event
            var closebt = jQuery(this.modal.find('.closebt').first());
            closebt.on("click", ()=>{this.close()})

        }

        show():void {
            jQuery('body, html').css({'overflow': 'hidden'});

            if (this.modal.hasClass(this.modalId + '-off')) {
                this.modal.removeClass(this.settings.animatedOut);
                this.modal.removeClass(this.modalId + '-off');
                this.modal.addClass(this.modalId + '-on');
            }

            if (this.modal.hasClass(this.modalId + '-on')) {
                this.settings.beforeOpen();
                this.modal.css({'opacity': this.settings.opacityIn, 'z-index': this.settings.zIndexIn});
                this.modal.addClass(this.settings.animatedIn);
                this.modal.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
                    ()=>{this.afterOpen()});
            };


        }

        close():void {
            jQuery('body, html').css({'overflow': 'auto'});
            this.settings.beforeClose(); //beforeClose
            if (this.modal.hasClass(this.modalId + '-on')) {
                this.modal.removeClass(this.modalId + '-on');
                this.modal.addClass(this.modalId + '-off');
            }

            if (this.modal.hasClass(this.modalId + '-off')) {
                this.modal.removeClass(this.settings.animatedIn);
                this.modal.addClass(this.settings.animatedOut);
                this.modal.one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
                    ()=>{this.afterClose()});
            }

        }

        afterClose():void {
            this.modal.css({'z-index': this.settings.zIndexOut});
            this.settings.afterClose(); //afterClose
        }

        afterOpen():void {
            this.settings.afterOpen(); //afterOpen
        }

    }

    export function generateRandomId(length = 5): string {
        let s = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789=&$·#@/?+-*";
        return Array(length).join().split(',').map(function() {
            return s.charAt(Math.floor(Math.random() * s.length));
        }).join('');
    };

}
