/*

	Main.js

	01. Menu toggle
	02. Top bar height effect
	03. Home content slider
	04. Home background slider
	05. Home background and content slider
	06. Quote slider
	07. Image slider
	08. Services slider
	09. Employee slider
	10. Work slider
	11. Footer promo
	12. Contact form
	13. Scrollto
	14. Magnific popup
	15. Equal height
	16. fitVids

*/

jQuery('document').ready(function($){
    setTimeout(function() {
        $('.owl-prev').html('<i class="fa fa-angle-left"></i>');
        $('.owl-next').html('<i class="fa fa-angle-right"></i>');
    }, 10);
    
    $('.nt-nt_accordions-wrap .tab').click(function() {
        t = $(this);
        
        setTimeout(function() {
            $('html, body').animate({
               scrollTop: t.offset().top - 120
            }, 1000);
        }, 200);
    });
});


jQuery(document).ready(function($) {

    var carouselIds = new Array();

    $(".owl-carousel").each(function() {
        carouselIds.push($(this).attr("id"));
    });

    for (var i in carouselIds) {
        var params = {};
        var datas = $(document.getElementById(carouselIds[i])).data();
        for (var paramName in datas) {
            var data = $(document.getElementById(carouselIds[i])).data(paramName);
            if (data !== "") {
                // If it's an array (contains comma) parse the string to array
                if(String(data).indexOf(",") > -1) {
                    data = data.split(",");
                }

                // New random param not available in Owl Carousel
                if(paramName == "random") {
                    params[owlCarouselParamName("beforeInit")] = function(elem) {
                        random(elem);
                    };
                } else {
                    params[owlCarouselParamName(paramName)] = data;
                }
            }
        }

        $(document.getElementById(carouselIds[i])).owlCarousel(params);
    }

    /**
     * Sort random function
     * @param {Selector} owlSelector Owl Carousel selector
     */
    function random(owlSelector){
        owlSelector.children().sort(function(){
            return Math.round(Math.random()) - 0.5;
        }).each(function(){
            $(this).appendTo(owlSelector);
        });
    }

});

/**
 * Fix Owl Carousel parameter name case.
 * @param {String} paramName Parameter name
 * @returns {String} Fixed parameter name
 */
function owlCarouselParamName(paramName) {

    var parameterArray = {
        ADDCLASSACTIVE: "addClassActive",
        AFTERACTION: "afterAction",
        AFTERINIT: "afterInit",
        AFTERLAZYLOAD: "afterLazyLoad",
        AFTERMOVE: "afterMove",
        AFTERUPDATE: "afterUpdate",
        AUTOHEIGHT: "autoHeight",
        AUTOPLAY: "autoPlay",
        BASECLASS: "baseClass",
        BEFOREINIT: "beforeInit",
        BEFOREMOVE: "beforeMove",
        BEFOREUPDATE: "beforeUpdate",
        DRAGBEFOREANIMFINISH: "dragBeforeAnimFinish",
        ITEMS: "items",
        ITEMSCUSTOM: "itemsCustom",
        ITEMSDESKTOP: "itemsDesktop",
        ITEMSDESKTOSMALL: "itemsDesktopSmall",
        ITEMSMOBILE: "itemsMobile",
        ITEMSSCALEUP: "itemsScaleUp",
        ITEMSTABLET: "itemsTablet",
        ITEMSTABLETSMALL: "itemsTabletSmall",
        JSONPATH: "jsonPath",
        JSONSUCCESS: "jsonSuccess",
        LAZYLOAD: "lazyLoad",
        LAZYFOLLOW: "lazyFollow",
        LAZYEFFECT: "lazyEffect",
        MOUSEDRAG: "mouseDrag",
        NAVIGATION: "navigation",
        NAVIGATIONTEXT: "navigationText",
        PAGINATION: "pagination",
        PAGINATIONNUMBERS: "paginationNumbers",
        PAGINATIONSPEED: "paginationSpeed",
        RESPONSIVE: "responsive",
        RESPONSIVEBASEWIDTH: "responsiveBaseWidth",
        RESPONSIVEREFRESHRATE: "responsiveRefreshRate",
        REWINDNAV: "rewindNav",
        REWINDSPEED: "rewindSpeed",
        SCROLLPERPAGE: "scrollPerPage",
        SINGLEITEM: "singleItem",
        SLIDESPEED: "slideSpeed",
        STARTDRAGGING: "startDragging",
        STOPONHOVER: "stopOnHover",
        THEME: "theme",
        TOUCHDRAG: "touchDrag",
        TRANSITIONSTYLE: "transitionStyle",
    };

    return parameterArray[paramName.toUpperCase()];
}



(function(){
	"use strict";

	/* ==================== 01. Menu toggle ==================== */
	$(function(){
		$('#toggle').click(function (e){
			e.stopPropagation();
		});
		$('html').click(function (e){
			if (!$('.toggle').is($(e.target))){
				$('#toggle').prop("checked", false);
			}
		});
	});

/* Minified js in demo only */
$(window).bind("scroll",function(){if($(this).scrollTop()>100){$(".top-bar").removeClass("tb-large").addClass("tb-small")}else{$(".top-bar").removeClass("tb-small").addClass("tb-large")}});$(".home-c-slider").bxSlider({mode:"horizontal",pager:false,controls:true,nextText:'<i class="bs-right fa fa-angle-right"></i>',prevText:'<i class="bs-left fa fa-angle-left"></i>'});$(".home-bg-slider").bxSlider({mode:"fade",auto:true,speed:1e3,pager:false,controls:false,nextText:'<i class="bs-right fa fa-angle-right"></i>',prevText:'<i class="bs-left fa fa-angle-left"></i>'});$(".home-bgc-slider").bxSlider({mode:"fade",pager:true,controls:true,nextText:'<i class="bs-right fa fa-angle-right"></i>',prevText:'<i class="bs-left fa fa-angle-left"></i>'});$(".quote-slider").bxSlider({mode:"horizontal",controls:false,adaptiveHeight:true});$(".img-slider").bxSlider({mode:"fade",pager:true,controls:true,nextText:'<i class="bs-right fa fa-angle-right"></i>',prevText:'<i class="bs-left fa fa-angle-left"></i>'});$(function(){var e=$(".services-slider");e.owlCarousel({pagination:false,navigation:false,items:4,itemsDesktop:[1e3,3],itemsTablet:[600,2],itemsMobile:[321,1]});$(".serv-next").click(function(){e.trigger("owl.next")});$(".serv-prev").click(function(){e.trigger("owl.prev")})});$(function(){var e=$(".employee-slider");e.owlCarousel({pagination:false,navigation:false,items:4,itemsDesktop:[1e3,3],itemsTablet:[600,2],itemsMobile:[321,1]});$(".emp-next").click(function(){e.trigger("owl.next")});$(".emp-prev").click(function(){e.trigger("owl.prev")})});$(function(){var e=$(".work-slider");e.owlCarousel({pagination:false,navigation:false,items:3,itemsDesktop:[1e3,3],itemsTablet:[600,2],itemsMobile:[321,1]});$(".work-next").click(function(){e.trigger("owl.next")});$(".work-prev").click(function(){e.trigger("owl.prev")})});$(".promo-control").click(function(){$(".footer-promo").slideToggle(500);if($(".footer-promo").is(":visible")){$("html, body").animate({scrollTop:$(".footer-promo").offset().top},500)}});$(function(){$("#contactform").submit(function(){var e=$(this).attr("action");$("#message").slideUp(300,function(){$("#message").hide();$("#submit").after('<img src="../images/status.gif" class="loader">').attr("disabled","disabled");$.post(e,{name:$("#name").val(),email:$("#email").val(),phone:$("#phone").val(),subject:$("#subject").val(),comments:$("#comments").val(),verify:$("#verify").val()},function(e){document.getElementById("message").innerHTML=e;$("#message").slideDown(300);$("#contactform img.loader").fadeOut(300,function(){$(this).remove()});$("#submit").removeAttr("disabled");if(e.match("success")!=null)$("#contactform").slideUp(300)})});return false})});$(function(){$(".scrollto").bind("click.scrollto",function(e){e.preventDefault();var t=this.hash,n=$(t);$("html, body").stop().animate({scrollTop:n.offset().top-0},900,"swing",function(){window.location.hash=t})})});$(".popup").magnificPopup({type:"image",fixedContentPos:false,fixedBgPos:false,removalDelay:300,mainClass:"mfp-fade"});$(".popup-youtube, .popup-vimeo, .popup-gmaps").magnificPopup({disableOn:700,type:"iframe",fixedContentPos:false,fixedBgPos:false,removalDelay:300,mainClass:"mfp-fade",preloader:false});$(".popup-gallery").magnificPopup({type:"image",gallery:{enabled:true},fixedContentPos:false,fixedBgPos:false,removalDelay:300,mainClass:"mfp-fade"});$(document).ready(function(){$(".equal").children(".col").equalizeHeight();$(window).resize(function(){$(".equal").children(".col").equalizeHeight()})});$(".responsive-video").fitVids()

})(jQuery);