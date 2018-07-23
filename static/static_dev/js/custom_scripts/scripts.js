if ($(".has-error").length>0){
    console.log(5);
     $('html, body').animate({scrollTop: ($(".has-error:last").parent("form").offset().top-100)}, 1);
}

$(document).ready(function(){

    function finalPriceCalculation(){
        if ($("#id_price")){
            price = $("#id_price").val();
            discount = $("#id_discount").val();
            final_price = price-discount;
            $("#price_final").text(final_price);
        }
    }
    finalPriceCalculation();
    $("#id_price, #id_discount").on("change", function(){
        finalPriceCalculation();
    });


    if($('.owl-carousel').length>0){
        $('.owl-carousel').owlCarousel({
            dots: false,
            autoplay: true,
            autoplayTimeout: 7000,
            nav: true,
            smartSpeed :900,
            navText : ["<i class='fa fa-2x fa-chevron-left'></i>","<i class='fa fa-2x fa-chevron-right'></i>"],
            center: true,
            items:1,
            loop:true,
            margin:10,
            responsive:{
                    1200:{items:1},
                    0: {
                        items: 1,
                        autoHeight: true,
                        mouseDrag: false,
                        touchDrag: true
                      },
                      768: {
                        items: 1,
                        autoHeight: true,
                        mouseDrag: false,
                        touchDrag: true
                      }
            }
        });
    }
    console.log("test");

    $(".book-scheduled-tour, .book-private-tour").on("click", function(e){
        e.preventDefault();
        scheduled_tour = $(this).data("scheduled_tour");
        $("#id_tour_scheduled").val(scheduled_tour);
        $("html, body").animate({ scrollTop: $("#tour_booking_form").offset().top }, 300);
    });

    //function showBookingButton(){
    //    var scroll = $(window).scrollTop();
    //    var width = $(window).width();
    //    console.log(222);
    //    console.log(scroll);
    //    guide_general_info_from_top = $('#guide_general_info').offset().top;
    //    booking_area_from_top = $('#booking_area').offset().top;
    //    console.log(guide_general_info_from_top);
    //    if (scroll >= guide_general_info_from_top && scroll <= booking_area_from_top && width>1200) {
    //        $('#booking_proposal').removeClass('hidden');
    //    } else  {
    //        $('#booking_proposal').addClass('hidden');
    //    }
    //}
    //
    //$(window).on('scroll', function(){
    //    if('#booking_proposal'){
    //        console.log("1111");
    //        showBookingButton();
    //    }
    //});
    //
    //$(window).resize(function () {
    //    showBookingButton();
    //});

    //there are at least 2 buttons with this class
    $('.btn-booking-proposal').on('click', function(e){
        e.preventDefault();
        var link = $(this).attr('href');
        $('html, body').animate({scrollTop: ($(link).offset().top-10)}, 500);
    });

    $('#scroll_top').on('click', function(e){
        e.preventDefault();
        var link = $(this).attr('href');
        $('html, body').animate({scrollTop: ($(link).offset().top)}, 500);
    });

    function updatingChosenHours(){
        var form = $('.schedule-form');
        hours = $('#booking_hours:not(.hidden) option:selected').val();
        if (!hours){
            var hours = form.find('#hours_nmb_container .btn-group-select-num label.active input').val();
        }

        $('#booking_hours option').attr('selected', false);
        $('#booking_hours option[value="'+hours+'"]').attr('selected','selected');
        $('#booking_hours').val(hours);

        return hours
    }

    function priceCalculation(){

        updatingChosenHours();
        if ($('#amount_container').hasClass('hidden')){
            $('#amount_container').removeClass('hidden');
        }
    }

    $(document).on('click', '.hours-nmb', function(){
        //$('#form_tour_scheduling .hours-nmb').removeClass('active');
        $(this).parent().find('.hours-nmb').removeClass('active');
        $(this).addClass('active');
        priceCalculation();
    });

    $(document).on('change', '#booking_hours', function(){
        priceCalculation();
    });


    function gettingFormData($form){
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function(n, i){
            //console.log(n['name']);
            //console.log(n['value']);
            //
            //indexed_array[n['name']] = n['value'];

            if (indexed_array[n['name']] ) {
                if ( typeof(indexed_array[n['name']]) === "string" ) {
                    indexed_array[n['name']] = [indexed_array[n['name']]];
                }
                indexed_array[n['name']].push(n['value']);
            } else {
                indexed_array[n['name']] = n['value'];
            }

        });

        return indexed_array;
    }

    function hidingNotification(){
         window.setTimeout(function() {
            $('.booking-result-message').addClass('hidden');
         }, 2500);
    }

    $('#form_guide_scheduling .submit-button, #form_tour_scheduling .submit-button').on('click', function(e){
        //var booked_hours = updatingChosenHours();
        //
        //if (booked_hours>0){
        //    $('.schedule-form').find('#booking_hours').val(booked_hours);
        //}

        e.preventDefault();
        time_slots_nmb = $('.time-slots-container .time-slot.chosen').length;
        $('.schedule-form').find('#booking_hours').val(time_slots_nmb);

        time_slots_chosen = [];
        $.each($('.time-slots-container .time-slot.chosen'), function(){
            time_slots_chosen.push($(this).data("guide_time_slot"));
        });

        minimum_hours = $('#minimum_hours').val();
        if (time_slots_chosen.length>0 && minimum_hours && time_slots_chosen.length<minimum_hours){
            $('#booking_form_error_container').html("<div class='text-black text-center text-error'>" +
                "Please select minimum "+minimum_hours+" hours.</div>")
        }else{
            $('#booking_hours').val(time_slots_chosen.length);

            if (time_slots_chosen.length>0){
                $('#time_slots_chosen').val(time_slots_chosen);
                $(this).closest('form').submit();
            }else {
                $('#booking_form_error_container').html("<div class='text-black text-center text-error'>Please select some time slot.</div>")
            }
        }

    });

    $(document).on('click', '.close-alert', function(){
        $(this).closest('.booking-result-message').addClass('hidden');
    });


    if ($('#amount_container').length > 0){
        priceCalculation();
    }

    $('.change-language-link').on('click', function (e) {
        e.preventDefault();
        url = $(this).attr("href");
        window.location.href = url;
    });

    function changingPaymentType(){
        var current_payment_type = $('#payment_type').val();
        if (current_payment_type == 1){
            $('#hourly_area').removeClass('hidden');
            $('#fixed_area').addClass('hidden');
        }else if (current_payment_type == 2){
            $('#hourly_area').addClass('hidden');
            $('#fixed_area').removeClass('hidden');
        }else{
            $('#hourly_area').addClass('hidden');
            $('#fixed_area').addClass('hidden');
        }
    }

    $(document).on('change', '#payment_type', function(){
        changingPaymentType();
    });

    changingPaymentType();


    $('#book_more').on('click', function(e){
        e.preventDefault();
        $('#booking_form_area').removeClass('hidden');
        if ($('#additional_services_select').length>0){
            $('#booking_form_area #additional_services_select').select2({
                placeholder: 'Select additional services'
            });
        }
    });


    $(".btn-order-review").magnificPopup({
            type: 'inline', // set source type (image default)
            removalDelay: 500, // delay removal by X to allow out-animation,
            midClick: true, // Allow opening popup on middle mouse click. Always set it to true if you don't provide alternative source in href
            callbacks: {
                //beforeOpen: function(e) {
                //  // Set Magnific Animation
                //  var Animation = "mfp-rotateLeft";
                //  this.st.mainClass = Animation;
                //
                //  // Inform content container there is an animation
                //  this.contentContainer.addClass('mfp-with-anim');
                //},

                open: function(){

                    var $triggerEl = $(this.st.el);
                    var order_id = $triggerEl.data("order_id");

                    var self = $.magnificPopup.instance;
                    self.contentContainer.find('#order_id').val(order_id)

                }
            }
    });

    $(document).on('change', '.service-name-checkbox', function() {
        var current_row = $(this).closest('tr');
        current_row.find('.service-price').toggleClass('hidden');
    });


    function togglingEditingPhoneStuff(){
        $('#submit_phone_btn').toggleClass('hidden');
        $('#validate_phone_btn').toggleClass('hidden');
        $('#sms_code_container').toggleClass('hidden')
    };

    $('#edit_phone').on('click', function(){
        togglingEditingPhoneStuff();
    });


    //$('#submit_phone_btn').on('click', function(e){
    //    e.preventDefault();
    //
    //    var phone = $('#phone').val();
    //    console.log(phone);
    //    console.log(phone.length);
    //    if (phone.length < 7){
    //        $('#phone_error_message').text("Enter valid phone");
    //        return false;
    //    }
    //
    //    data = {};
    //    var csrf_token = $('#csrf_getting_form [name="csrfmiddlewaretoken"]').val();
    //    data["csrfmiddlewaretoken"] = csrf_token;
    //    data["phone"] = phone;
    //
    //
    //    var url = $(this).data('link');
    //    $.ajax({
    //         url: url,
    //         type: 'POST',
    //         data: data,
    //         cache: true,
    //         success: function (data) {
    //             console.log(data);
    //             if(data.status=='success'){
    //                 togglingEditingPhoneStuff();
    //             };
    //         }
    //    })
    //});


    $('#is_company').on("change", function(){
        if ($(this).prop("checked")){
            $('#business_id_container').removeClass("hidden");
        }else{
            $('#business_id_container').addClass("hidden");
        }
    })

});

$('.datepicker').datepicker();
$('.datepicker-date').datepicker();

//$('.datepicker.today-date').datepicker('setDate', 'today');
//

window.setTimeout(function() {
  $(".alert:not(.booking-result-message)").fadeTo(100, 0).slideUp(100, function(){
    $(this).addClass('hidden');
  });
}, 2500);


$(document).ready(function(){
    $(document).on('click', '#toggle_left_menu', function(e) {
         if($.cookie("left_menu_hided") == 1) {
             $.cookie("left_menu_hided", 0, {path: '/'});
         }
         else{
            $.cookie("left_menu_hided", 1, {path: '/'});
        }
        hidingLeftMenu()
    });


});

function hidingLeftMenu(){
    if ($.cookie("left_menu_hided") == 1) {
        $('.booking-filters-container').addClass("closed");
    }else{
        $('.booking-filters-container').removeClass("closed");
    }
}
hidingLeftMenu();


//sticking leftbar on scroll

$(window).scroll(function () {
    var scroll = $(window).scrollTop();
    var width = $(window).width();
    elementsResizing()
});

function elementsResizing(){
    var scroll = $(window).scrollTop();
    var width = $(window).width();
    if (scroll >= 130 && width>990) {
        $('.booking-filters-container').addClass('sticky-top');
    } else  {
        $('.booking-filters-container').removeClass('sticky-top');
    };
    if (width>990){
        $('.booking-filters-container').removeClass("closed");
    }
};

$(window).resize(function () {
    elementsResizing();
});