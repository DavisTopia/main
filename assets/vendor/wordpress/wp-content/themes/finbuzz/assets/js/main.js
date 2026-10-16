jQuery(document).ready(function ($) {
    "use strict";
    var $grid;

    $('a[href=\\#]').on('click', function (e) {
        e.preventDefault();
    });
    /*ISOTOPE HTML END*/

    /* Theia Side Bar */
    if (typeof ($.fn.theiaStickySidebar) !== "undefined") {
        $('.has-sidebar .fixed-bar-coloum').theiaStickySidebar({'additionalMarginTop': 150});
        $('.shop-page .fixed-bar-coloum').theiaStickySidebar({'additionalMarginTop': 150});
    }

    /* Header Search */
    $('a[href="#header-search"]').on("click", function (event) {
        event.preventDefault();
        $("#header-search").addClass("open");
        $('#header-search > form > input[type="search"]').focus();
    });

    $("#header-search, #header-search button.close").on("click keyup", function (
        event
    ) {
        if (
            event.target === this ||
            event.target.className === "close" ||
            event.keyCode === 27
        ) {
            $(this).removeClass("open");
        }
    });

    /* Scroll to top */
    $('.scrollup').on('click', function () {
        $('html, body').animate({scrollTop: 0}, 800);
        return false;
    });

    $(window).on('scroll', function () {
        if ($(window).scrollTop() > 200) {
            $('.scrollup').addClass('back-top');
        } else {
            $('.scrollup').removeClass('back-top');
        }
    });

    /* Mobile menu */
    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 100) {
            $("body").addClass("not-top");
            $("body").removeClass("top");
        } else {
            $("body").addClass("top");
            $("body").removeClass("not-top");
        }
    });

    /* Search Box */
    $(".search-box-area").on('click', '.search-button, .search-close', function (event) {
        event.preventDefault();
        if ($('.search-text').hasClass('active')) {
            $('.search-text, .search-close').removeClass('active');
        } else {
            $('.search-text, .search-close').addClass('active');
        }
        return false;
    });


    $(".additional-menu-area").on('click', function () {    
        $("body").toggleClass("side-trigger-class");
    });

    var menuArea = $('.additional-menu-area');
    menuArea.on('click', '.side-menu-trigger', function (e) {
        e.preventDefault();
        var self = $(this);
        if (self.hasClass('side-menu-open')) {
            $('.sidenav').css('transform', 'translateX(0%)');
            if (!menuArea.find('> .rt-cover').length) {
                menuArea.append("<div class='rt-cover'></div>");
            }
            self.removeClass('side-menu-open').addClass('side-menu-close');
        }
    });

    function closeMenuArea() {
        var trigger = $('.side-menu-trigger', menuArea);
        trigger.removeClass('side-menu-close').addClass('side-menu-open');
        if (menuArea.find('> .rt-cover').length) {
            menuArea.find('> .rt-cover').remove();
        }
        $('.sidenav').css('transform', 'translateX(100%)');
    }

    menuArea.on('click', '.closebtn', function (e) {
        e.preventDefault();
        closeMenuArea();
    });

    $(document).on('click', '.rt-cover', function () {
        closeMenuArea();
    });

    /*-------------------------------------
    MeanMenu activation code
    --------------------------------------*/
    var a = $('.offscreen-navigation .menu');
    if (a.length) {
        $(".menu-item-has-children").append("<span></span>");
        $(".page_item_has_children").append("<span></span>");

        a.children("li").addClass("menu-item-parent");

        $('.menu-item-has-children > span').on('click', function () {
            var _self = $(this),
                sub_menu = _self.parent().find('>.sub-menu');
            if (_self.hasClass('open')) {
                sub_menu.slideUp();
                _self.removeClass('open');
            } else {
                sub_menu.slideDown();
                _self.addClass('open');
            }
        });
        $('.page_item_has_children > span').on('click', function () {
            var _self = $(this),
                sub_menu = _self.parent().find('>.children');
            if (_self.hasClass('open')) {
                sub_menu.slideUp();
                _self.removeClass('open');
            } else {
                sub_menu.slideDown();
                _self.addClass('open');
            }
        });
    }

    $('.mean-bar .sidebarBtn').on('click', function (e) {
        e.preventDefault();
        $('body').toggleClass('slidemenuon');
    });

    $(window).on("scroll", function () {
        if ($(".rt-header-style11").hasClass("sticky-on")) {
            let stickyPlaceHolder = $("#sticky-placeholder"),
                menu = $("#navbar-wrap"),
                menuH = menu.outerHeight(),
                topbarH = $("#topbar-wrap").outerHeight() || 0,
                targrtScroll = topbarH,
                header = $(".rt-header-style11");
            if ($(window).scrollTop() > targrtScroll) {
                header.addClass("sticky");
                stickyPlaceHolder.height(menuH);
            } else {
                header.removeClass("sticky");
                stickyPlaceHolder.height(0);
            }
        }
    });

    $(window).on("scroll", function () {
        if ($("#header-12").hasClass("header-area")) {
            let stickyPlaceHolder = $("#sticky-placeholder"),
                menu = $("#navbar-wrap"),
                menuH = menu.outerHeight(),
                topbarH = $("#topbar-wrap").outerHeight() || 0,
                targrtScroll = topbarH,
                header = $("#header-12");
            if ($(window).scrollTop() > targrtScroll) {
                header.addClass("sticky");
                stickyPlaceHolder.height(menuH);
            } else {
                header.removeClass("sticky");
                stickyPlaceHolder.height(0);
            }
        }
    });
    
    /*Header and mobile menu stick*/
    $(window).on('scroll', function () {
        if ($('body').hasClass('sticky-header')) {

            // Sticky header
            var stickyPlaceHolder = $("#rt-sticky-placeholder"),
                menu = $("#header-menu"),
                menuH = menu.outerHeight(),
                topHeaderH = $('#tophead').outerHeight() || 0,
                middleHeaderH = $('#middleHeader').outerHeight() || 0,
                targrtScroll = topHeaderH + middleHeaderH;
            if ($(window).scrollTop() > targrtScroll) {
                menu.addClass('rt-sticky');
                stickyPlaceHolder.height(menuH);
            } else {
                menu.removeClass('rt-sticky');
                stickyPlaceHolder.height(0);
            }

            // Sticky mobile header
            var stickyPlaceHolder = $("#mobile-sticky-placeholder"),
                menubar = $("#mobile-men-bar"),
                menubarH = menubar.outerHeight(),
                topHeaderH = $('#mobile-top-fix').outerHeight() || 0,
                total_height =topHeaderH;
            if ($(window).scrollTop() > total_height) {
                $("#meanmenu").addClass('mobile-sticky');
                stickyPlaceHolder.height(menubarH);
            } else {
                $("#meanmenu").removeClass('mobile-sticky');
                stickyPlaceHolder.height(0);
            }

        }
    });

    /*=============================
// video pop up 
===============================*/

    let videoPopUp = $(".play-btn");
    if (videoPopUp.length) {
        videoPopUp.magnificPopup({
            type: "iframe",
            iframe: {
                markup:
                    '<div class="mfp-iframe-scaler">' +
                    '<div class="mfp-close"></div>' +
                    '<iframe class="mfp-iframe" frameborder="0" allowfullscreen></iframe>' +
                    "</div>",
                patterns: {
                    youtube: {
                        index: "youtube.com/",
                        id: "v=",
                        src: "https://www.youtube.com/embed/%id%?autoplay=1",
                    },
                    vimeo: {
                        index: "vimeo.com/",
                        id: "/",
                        src: "//player.vimeo.com/video/%id%?autoplay=1",
                    },
                    gmaps: {
                        index: "//maps.google.",
                        src: "%id%&output=embed",
                    },
                },
                srcAction: "iframe_src",
            },
        });
    }

    /* Woocommerce Shop change view */
    $('#shop-view-mode li a').on('click', function () {
        $('body').removeClass('product-grid-view').removeClass('product-list-view');

        if ($(this).closest('li').hasClass('list-view-nav')) {
            $('body').addClass('product-list-view');
            Cookies.set('shopview', 'list');
        } else {
            $('body').addClass('product-grid-view');
            Cookies.remove('shopview');
        }
        return false;
    });

    // Popup - Used in video
    if (typeof $.fn.magnificPopup == 'function') {
        $('.rt-video-popup').magnificPopup({
            type: 'iframe',
            mainClass: 'mfp-fade',
            removalDelay: 160,
            preloader: false,
            fixedContentPos: false,
        });
    }
    if (typeof $.fn.magnificPopup == 'function') {
        if ($('.zoom-gallery').length) {
            $('.zoom-gallery').each(function () { // the containers for all your galleries
                $(this).magnificPopup({
                    delegate: 'a.finbuzz-popup-zoom', // the selector for gallery item
                    type: 'image',
                    gallery: {
                        enabled: true
                    }
                });
            });
        }
    }
     /* when product quantity changes, update quantity attribute on add-to-cart button */
     $("form.cart").on("change", "input.qty", function () {
        if (this.value === "0")
            this.value = "1";

        $(this.form).find("button[data-quantity]").data("quantity", this.value);
    });

    /* remove old "view cart" text, only need latest one thanks! */
    $(document.body).on("adding_to_cart", function () {
        $("a.added_to_cart").remove();
    });

    /*variable ajax cart end*/


    // Quantity
    $(document).on('click', '.quantity .input-group-btn .quantity-btn', function () {
        var $input = $(this).closest('.quantity').find('.input-text');

        if ($(this).hasClass('quantity-plus')) {
            $input.trigger('stepUp').trigger('change');
        }

        if ($(this).hasClass('quantity-minus')) {
            $input.trigger('stepDown').trigger('change');
        }
    });
    

    if( $('.header-shop-cart').length ){
        $( document ).on('click', '.remove-cart-item', function(){
          var product_id = $(this).attr("data-product_id");
          var loader_url = $(this).attr("data-url");
          var main_parent = $(this).parents('li.menu-item.dropdown');
          var parent_li = $(this).parents('li.cart-item');
          parent_li.find('.remove-item-overlay').css({'display':'block'});
          $.ajax({
            type: 'post',
            dataType: 'json',
            url: finbuzzObj.ajaxURL,
            data: { action: "neeon_product_remove",
                product_id: product_id
            },success: function(data){
              main_parent.html( data["mini_cart"] );
              $( document.body ).trigger( 'wc_fragment_refresh' );
            },error: function(xhr, status, error) {
              $('.header-shop-cart').children('ul.minicart').html('<li class="cart-item"><p class="cart-update-pbm text-center">'+ finbuzzObj.cart_update_pbm +'</p></li>');
            }
          });
          return false;
        });
    }
    // Wishlist
    $(document).on('click', '.rdtheme-wishlist-icon', function () {
        if ($(this).hasClass('rdtheme-add-to-wishlist') && typeof yith_wcwl_l10n != "undefined") {
            var $obj = $(this),
                productId = $obj.data('product-id'),
                afterTitle = $obj.data('title-after');
            var data = {
                'action': 'finbuzz_add_to_wishlist',
                'context': 'frontend',
                'nonce': $obj.data('nonce'),
                'add_to_wishlist': productId
            };

            $.ajax({
                url: yith_wcwl_l10n.ajax_url,
                type: 'POST',
                data: data,
                success: function success(data) {
                    if (data['result'] != 'error') {
                        $obj.removeClass('ajaxloading');
                        $obj.find('.wishlist-icon').removeClass('fa fa-heart').addClass('fas fa-heart').show();
                        $obj.removeClass('rdtheme-add-to-wishlist').addClass('rdtheme-remove-from-wishlist');
                        $obj.find('span').html(afterTitle);
                        $('body').trigger('rt_added_to_wishlist', [productId]);
                    } else {
                        console.log(data['message']);
                    }
                }
            });

            return false;
        }
    });
});

//function Load
function finbuzz_content_load_scripts() {
    var $ = jQuery;
    //Preloader

    $('#preloader').fadeOut('slow', function () {
        $(this).remove();
    });


     /*-------------------------------------
    Slick Slider
    -------------------------------------*/
    $('.slick-carousel').each(function() {
        $('.slick-carousel').not('.slick-initialized').slick();
    });

    /*---------------------------------------
      Background Parallax
      --------------------------------------- */
      if ($(".rt-parallax-bg-yes").length) {
        $(".rt-parallax-bg-yes").each(function () {
            var speed = $(this).data('speed');
            $(this).parallaxie({
                speed: speed ? speed : 0.5,
                offset: 0,
            });
        })
    }

    //button hover

    $(".button-arrow").hover(function () {
        $(".button-arrow").removeClass("active");
        $(this).addClass("active");
    });

    /*===================================
	// Main Banner
    =====================================*/
    $('.main-banner-slider').each(function() {
            var $this = $(this);
            var settings = $(this).data('options');
            var autoplayconditon = settings['auto'];
            var $pagination = $this.find('.swiper-pagination')[0];
            var $next = $this.find('.swiper-button-next')[0];
            var $prev = $this.find('.swiper-button-prev')[0];
        var mainSlider = new Swiper(this, {
            slidesPerView: 1,
            loop: settings['loop'],
            slideToClickedSlide: true,
            effect: "fade",
            autoplay:autoplayconditon ? {delay:settings['autoplay']['delay']}:false,
            speed:settings['speed'],
            navigation: {
            nextEl: $next,
            prevEl: $prev,
            },
            pagination: {
                el: $pagination,
                type: 'bullets',
                clickable:'true',
            },
            on: {
                slideChange: function () {
                    $('.rt-video-popup').magnificPopup({
                        type: 'iframe',
                        mainClass: 'mfp-fade',
                        removalDelay: 160,
                        preloader: false,
                        fixedContentPos: false,
                    });
                },
            },
        });
        mainSlider.init();

    });

    /*===================================
	// Main Banner
    =====================================*/
    $('.main-banner-slider3').each(function() {
        var $this = $(this);
        var settings = $(this).data('options');
        var autoplayconditon = settings['auto'];
        var $next = $this.find('.swiper-button-next')[0];
        var $prev = $this.find('.swiper-button-prev')[0];
        var mainSlider3 = new Swiper(this, {
            slidesPerView: 1,
            loop: settings['loop'],
            slideToClickedSlide: true,
            autoplay:autoplayconditon,
            autoplayTimeout:settings['autoplay']['delay'],
            speed:settings['speed'],
            navigation: {
                nextEl: $next,
                prevEl: $prev,
            },
        });
    mainSlider3.init();

    });


    //Horizontal Thumbnail slider 

    $('.finbuzz-horizontal-slider').each(function(){
        var slider_wrap = $(this);
        var $pagination = slider_wrap.find('.swiper-pagination')[0];
        var $next = slider_wrap.find('.swiper-button-next')[0];
        var $prev = slider_wrap.find('.swiper-button-prev')[0];
        var target_thumb_slider = slider_wrap.find('.horizontal-thumb-slider');
        var thumb_slider = null;
        if(target_thumb_slider.length){
            var settings = target_thumb_slider.data('xld');
            var autoplayconditon= settings['auto'];
            thumb_slider = new Swiper(target_thumb_slider[0],
                {
                autoplay:   autoplayconditon,
                autoplayTimeout: settings['autoplay']['delay'],
                speed: settings['speed'],
                loop:  settings['loop'],
                spaceBetween:  settings['spaceBetween'],
                breakpoints: {
                    0: {
                        slidesPerView: settings['breakpoints']['0']['slidesPerView'],
                    },
                    576: {
                        slidesPerView: settings['breakpoints']['576']['slidesPerView'],
                    },
                    768: {
                        slidesPerView: settings['breakpoints']['768']['slidesPerView'],
                    },
                    992: {
                        slidesPerView: settings['breakpoints']['992']['slidesPerView'],
                    },
                    1200: {
                        slidesPerView:  settings['breakpoints']['1200']['slidesPerView'],
                    },            
                },
                pagination: {
                    el: $pagination,
                    type: "progressbar",
                },
                
            });
        }

        var target_slider = slider_wrap.find('.horizontal-slider');
        if(target_slider.length){
            var settings = target_slider.data('xld');
            new Swiper(target_slider[0], {
                autoplay:  settings && settings['auto'],
                autoplayTimeout: settings['autoplay']['delay'],
                speed: settings && settings['speed'],
                loop:  settings && settings['loop'],
                effect: settings && settings['effect'],
                thumbs: {
                  swiper: thumb_slider,
                },
                navigation: {
                    nextEl: $next,
                    prevEl: $prev,
                },
            });
        }
    });

    /*===================================
	 // Section background image
	====================================*/
    imageFunction();

    function imageFunction() {
        $("[data-bg-image]").each(function () {
        let img = $(this).data("bg-image");
        $(this).css({
            backgroundImage: "url(" + img + ")",
        });
        });
    }



    /*=================================
   // counter up
   ==================================*/

   let counter=true;
   $(".counter-appear").appear();
   $(".counter-appear").on("appear", function () {
    if (counter) {
        // Only number counter
            $(".counterUp").each(function () {
                var $this = $(this);
                let duration=$(this).data('duration');
                jQuery({
                    Counter: 0,
                }).animate(
                    {
                    Counter: $this.attr("data-counter"),
                    },
                    {
                    duration: duration,
                    easing: "swing",
                    step: function () {
                        var num = Math.ceil(this.Counter).toString();
                        if (Number(num) > 99999) {
                        while (/(\d+)(\d{3})/.test(num)) {
                            num = num.replace(/(\d+)(\d{3})/, "");
                        }
                        }
                        $this.html(num);
                    },
                    }
                );
            });

            // pie chart
        $(".chart-bar").each(function(){
            let circleSettings=$(this).data('circle-options');
            $(this).easyPieChart({
                barColor: circleSettings.fg_color,
                trackColor: circleSettings.bg_color,
                scaleColor: false,
                lineWidth: circleSettings.circle_border_size,
                size: circleSettings.circle_size,
                lineCap: "square",
                animate: circleSettings.animation_speed,
            });
        });
        counter = false;
        }
   });

    //initialize swiper when document ready
    $('.rt-swiper-container').each(function () {
        var swiper = $(this),
            autoplay = swiper.data('autoplay'),
            autoplayDelay = swiper.data('autoplay-timeout') || '',
            speed = swiper.data('speed') || '',
            loop = swiper.data('loop') || true,
            slidesPerView = swiper.data('slides-per-view') || 1,
            spaceBetween = swiper.data('space-between'),
            centeredSlides = swiper.data('centered-slides'),
            rXsmall = swiper.data("r-x-small"),
            rSmall = swiper.data("r-small"),
            rMedium = swiper.data("r-medium"),
            rLarge = swiper.data("r-large"),
            rXlarge = swiper.data("r-x-large");
        var $swiper = new Swiper('.rt-swiper-container', {
            // Optional parameters
            autoplay: autoplay ? {delay:autoplayDelay} : false,
            speed: speed ? speed : 2000,
            loop: loop ? true : false,
            slidesPerView: slidesPerView ? slidesPerView : 1,
            spaceBetween: spaceBetween ? spaceBetween : 10,
            centeredSlides: centeredSlides ? true : false,
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            breakpoints: {
                0: {
                    slidesPerView: rXsmall ? rXsmall : 1,
                },
                576: {
                    slidesPerView: rSmall ? rSmall : 2,
                },
                768: {
                    slidesPerView: rMedium ? rMedium : 3,
                },
                992: {
                    slidesPerView: rLarge ? rLarge : 4,
                },
                1200: {
                    slidesPerView: rXlarge ? rXlarge : 1,
                }
            }
        });
    });

    $('.rt-related-slider').each(function() {
        var $this = $(this);
        var settings = $this.data('xld');
        var autoplayconditon= settings['auto'];
        var $pagination = $this.find('.swiper-pagination')[0];
        var $next = $this.find('.swiper-button-next')[0];
        var $prev = $this.find('.swiper-button-prev')[0];
        var swiper = new Swiper( this, {
                autoplay:   autoplayconditon,
                autoplayTimeout: settings['autoplay']['delay'],
                speed: settings['speed'],
                loop:  settings['loop'],
                pauseOnMouseEnter :true,
                slidesPerView: settings['slidesPerView'],
                spaceBetween:  settings['spaceBetween'],
                centeredSlides:  settings['centeredSlides'],
                slidesPerGroup: settings['slidesPerGroup'] ? settings['slidesPerGroup']:1,
                pagination: {
                    el: $pagination,
                    clickable: true,
                    type: 'bullets',
                },
                navigation: {
                    nextEl: $next,
                    prevEl: $prev,
                },
                breakpoints: {
                0: {
                    slidesPerView: settings['breakpoints']['0']['slidesPerView'],
                },
                576: {
                    slidesPerView: settings['breakpoints']['576']['slidesPerView'],
                },
                768: {
                    slidesPerView: settings['breakpoints']['768']['slidesPerView'],
                },
                992: {
                    slidesPerView: settings['breakpoints']['992']['slidesPerView'],
                },
                1200: {
                    slidesPerView:  settings['breakpoints']['1200']['slidesPerView'],
                },
                1600: {
                    slidesPerView: settings['breakpoints']['1600']['slidesPerView'],
                },
            },
        });
        swiper.init();
    });

    //portfolio 9 slider coverflow effect
    $('.portfolio-coverflow-slider').each(function() {
        var $this = $(this);
        var settings = $this.data('xld');
        var autoplayconditon= settings['auto'];
        let portfolioSlider2 = new Swiper(".portfolio-coverflow-slider", {
            autoplay:   autoplayconditon,
            autoplayTimeout: settings['autoplay']['delay'],
            speed: settings['speed'],
            loop:  settings['loop'],
            spaceBetween: 1,
            slidesPerView: 4,
            centeredSlides: true,
            roundLengths: true,
            loopAdditionalSlides: 0,
            breakpoints: {
                0: {
                    slidesPerView: settings['breakpoints']['0']['slidesPerView'],
                },
                768: {
                    //slidesPerView: 1.5,
                    slidesPerView: settings['breakpoints']['768']['slidesPerView'],
                },
                992: {
                    //slidesPerView: 2,
                    slidesPerView: settings['breakpoints']['992']['slidesPerView'],
                },
                1200: {
                    //slidesPerView: 3.1,
                    slidesPerView:  settings['breakpoints']['1200']['slidesPerView'],
                },
            },
        });
    });

    //mousewheel slider
    $('.rt-mousewheel-slider').each(function() {
        var swiper = new Swiper('.rt-mousewheel-slider', {
            slidesPerView: 1,
            mousewheel: true,
            breakpoints: {
                0: {
                    slidesPerView: 1,
                    direction: 'horizontal',
                },
                768: {
                    slidesPerView: 1,
                    direction: 'horizontal',
                },
                992: {
                    slidesPerView: 1,
                    direction: 'horizontal',
                },
                1200: {
                    slidesPerView: 1,
                    direction: 'vertical',
                },
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
        });
    });

    //coverflow effect slider 2
    $('.rt-coverflow-slider2').each(function() {
        var $this = $(this);
        var settings = $this.data('xld');
        var autoplayconditon= settings['auto'];
        let rt_coverflow_slider2 = new Swiper(".rt-coverflow-slider2", {
            loop:  settings['loop'],
            centeredSlides:  settings['centeredSlides'],
            slidesPerView: 'auto',
            spaceBetween:  settings['spaceBetween'],
            autoHeight: true,
            autoplay:   autoplayconditon,
            autoplayTimeout: settings['autoplay']['delay'],
            speed: settings['speed'],
            pagination: {
                el: ".swiper-pagination",
                type: "bullets",
                clickable: "true",
            },
            breakpoints: {
                0: {
                    slidesPerView: 1,
                },
                768: {
                    slidesPerView: settings['breakpoints']['768']['slidesPerView'],
                },
                992: {
                    slidesPerView: settings['breakpoints']['992']['slidesPerView'],
                },
                1200: {
                    slidesPerView:  settings['breakpoints']['1200']['slidesPerView'],
                },
                1600: {
                    slidesPerView: settings['breakpoints']['1600']['slidesPerView'],
                },
            },
        });
    });


    //tab



    // pricing swithces
    var pricingWrapper = $(".pricing-wrapper");
    if (pricingWrapper) {
        $(".pricing-wrapper").each(function () {
            $(".pricing-switch-container").on("click", function () {
                $(".pricing-switch")
                .parents(".price-switch-box")
                .toggleClass("price-switch-box--active"),
                $(".pricing-switch").toggleClass("pricing-switch-active"),
                $(".price-box").toggleClass("price-box-show price-box-hide");
            });
        });
    }

    let testimonialSlider5 = new Swiper(".rt-fin-testimonial-slider-wrap", {
        loop: true,
        spaceBetween : 24,
        // autoplay: {
        // delay: 5000,
        // speed: 800,
        // },
      
        breakpoints: {
        0: {
          slidesPerView: 1,
        },
        768: {
          slidesPerView: 1,
        },
        992: {
          slidesPerView: 1,
        },
        1200: {
          slidesPerView: 1,
        },
        },
        navigation: {
          nextEl: ".swiper-button-next",
          prevEl: ".swiper-button-prev",
        },
      });

    /*-------------------------------------
	  Intersection Observer
	  -------------------------------------*/
	  if (!!window.IntersectionObserver) {
		let observer = new IntersectionObserver((entries, observer) => {
		  entries.forEach(entry => {
			if (entry.isIntersecting) {
			  entry.target.classList.add("active-animation");
			  observer.unobserve(entry.target);
			}
		  });
		}, {
		  rootMargin: "0px 0px -100px 0px"
		});
		document.querySelectorAll('.has-animation').forEach(block => {
		  observer.observe(block)
		});
	  } else {
		document.querySelectorAll('.has-animation').forEach(block => {
		  block.classList.remove('has-animation')
		});
	  }

    /*-------------------------------------
        Masonry
    -------------------------------------*/

    var galleryIsoContainer = $(".rt-portfolio-masonary");
    if (galleryIsoContainer.length) {
        var imageGallerIso = galleryIsoContainer.imagesLoaded(function () {
            imageGallerIso.isotope({
                itemSelector: ".rt-portfolio-item",
                percentPosition: true,
                isAnimated: true,
                masonry: {
                    columnWidth: ".rt-portfolio-item",
                },
                animationOptions: {
                    duration: 700,
                    easing: 'linear',
                        queue: false
                }
            });
        });
    }

    /* Wow Js Init */
    var wow = new WOW({
        boxClass: 'wow',
        animateClass: 'animated',
        offset: 0,
        mobile: false,
        live: true,
        scrollContainer: null,
    });

    new WOW().init();

    /**Load More Portfolio Button */
    var page = 2;
    $('#loadMore').click(function(){
        let main = $(this).data('port-items');
        var $container = jQuery('.portfolio-items');
        $.ajax({
            type : "post",
            url : finbuzzObj.ajaxURL,
            data : {
                action: "loadmore_ajax",
                postitem : main['item'],
                postcat:main['cat'],
                colclass:main['col_class'],
                excerptDisplay:main['excerpt_display'],
                excerptCount:main['excerpt_count'],
                portSerDisplay:main['port_serial_dis'],
                titleCount:main['title_count'],
                catDisplay:main['cat_display'],
                readMore:main['read_more_btn_dis'],
                pageNumber: page
            },
            success    : function(html){
                var $data = jQuery(html);
                if ($data.length) {
                  $container.append( html );
                    jQuery('#loadMore').removeClass('loading-lazy');
                } else {
                  jQuery("#loadMore").html("No More Portfolio");
                  jQuery('#loadMore').removeClass('loading-lazy');
                }
                setTimeout( function() {
                  revealPosts();
                }, 500);
            },

         });
         page++;

    });

    function revealPosts(){
        var posts = $('.single-grid-item:not(.reveal)');
        var i = 0;
        setInterval( function(){
          if ( i >= posts.length) return false;
          var el = posts[i];
          $(el).addClass('reveal');
          i++
        }, 100);
    }


}

(function ($) {
    "use strict";

    // Window Load+Resize
    $(window).on('load resize', function () {

        // Define the maximum height for mobile menu
        var wHeight = $(window).height();
        wHeight = wHeight - 50;
        $('.mean-nav > ul').css('max-height', wHeight + 'px');

    });

    // Elementor Frontend Load
    $(window).on('elementor/frontend/init', function () {
        if (elementorFrontend.isEditMode()) {
            elementorFrontend.hooks.addAction('frontend/element_ready/widget', function () {
                finbuzz_content_load_scripts();
            });
        }
    });

    // Window Load
    $(window).on('load', function () {
        finbuzz_content_load_scripts();
    });

})(jQuery);
