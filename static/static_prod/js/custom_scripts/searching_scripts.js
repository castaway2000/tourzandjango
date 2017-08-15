
if (jQuery) {
    var city_search_url = $('#city_input').data("search_url");
    $('#city_input').select2({
        ajax: {
            url: city_search_url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },
            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used

                params.page = params.page || 1;

                return {
                    results: data.items,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },

        minimumInputLength: 1
    });

    var guide_search_url = $('#guide_input').data("search_url");
    $('#guide_input').select2({
        ajax: {
            url: guide_search_url,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },
            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used

                params.page = params.page || 1;

                return {
                    results: data.items,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },

        minimumInputLength: 1
    });


    if ($('#language_input')) {
        var guide_search_url = $('#language_input').data("search_url");
        $('#language_input').select2({
            ajax: {
                url: guide_search_url,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page
                    };
                },
                processResults: function (data, params) {
                    // parse the results into the format expected by Select2
                    // since we are using custom formatting functions we do not need to
                    // alter the remote JSON data, except to indicate that infinite
                    // scrolling can be used

                    params.page = params.page || 1;

                    return {
                        results: data.items,
                        pagination: {
                            more: (params.page * 30) < data.total_count
                        }
                    };
                },
                cache: true
            },

            minimumInputLength: 1
        });
    }

    if ($('#interest_input')) {
        var interest_search_url = $('#interest_input').data("search_url");
        $('#interest_input').select2({
            tags: true,
            tokenSeparators: [',', ' '],

            ajax: {
                url: interest_search_url,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page
                    };
                },
                processResults: function (data, params) {
                    // parse the results into the format expected by Select2
                    // since we are using custom formatting functions we do not need to
                    // alter the remote JSON data, except to indicate that infinite
                    // scrolling can be used

                    params.page = params.page || 1;

                    return {
                        results: data.items,
                        pagination: {
                            more: (params.page * 30) < data.total_count
                        }
                    };
                },
                cache: true
            },

            minimumInputLength: 1
        });
    };

    if ($('#service_input')) {
        $('#service_input').select2({
            tags: true
        });
    };
    //if ($('#service_input')) {
    //    var service_search_url = $('#service_input').data("search_url");
    //    $('#service_input').select2({
    //        tags: true,
    //        tokenSeparators: [',', ' '],
    //
    //        ajax: {
    //            url: service_search_url,
    //            dataType: 'json',
    //            delay: 250,
    //            data: function (params) {
    //                return {
    //                    q: params.term, // search term
    //                    page: params.page
    //                };
    //            },
    //            processResults: function (data, params) {
    //                // parse the results into the format expected by Select2
    //                // since we are using custom formatting functions we do not need to
    //                // alter the remote JSON data, except to indicate that infinite
    //                // scrolling can be used
    //
    //                params.page = params.page || 1;
    //
    //                return {
    //                    results: data.items,
    //                    pagination: {
    //                        more: (params.page * 30) < data.total_count
    //                    }
    //                };
    //            },
    //            cache: true
    //        },
    //
    //        minimumInputLength: 1
    //    });
    //};

    if ($('#language_native')) {
        var language_search_url = $('#language_native').data("search_url");
        $('#language_native').select2({

            ajax: {
                url: language_search_url,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page
                    };
                },
                processResults: function (data, params) {
                    // parse the results into the format expected by Select2
                    // since we are using custom formatting functions we do not need to
                    // alter the remote JSON data, except to indicate that infinite
                    // scrolling can be used

                    params.page = params.page || 1;

                    return {
                        results: data.items,
                        pagination: {
                            more: (params.page * 30) < data.total_count
                        }
                    };
                },
                cache: true
            },

            minimumInputLength: 1
        });

        $('#language_second').select2({

            ajax: {
                url: language_search_url,
                dataType: 'json',
                delay: 250,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page
                    };
                },
                processResults: function (data, params) {
                    // parse the results into the format expected by Select2
                    // since we are using custom formatting functions we do not need to
                    // alter the remote JSON data, except to indicate that infinite
                    // scrolling can be used

                    params.page = params.page || 1;

                    return {
                        results: data.items,
                        pagination: {
                            more: (params.page * 30) < data.total_count
                        }
                    };
                },
                cache: true
            },

            minimumInputLength: 1
        });
    }

    if ($('#status_input')){
        $('#status_input').select2({
            placeholder: function(){
                $(this).data('placeholder');
            }
        })
    }
}

$(document).ready(function(){
    $('#sorting_area a').on('click', function(){
        var order_value = $(this).data('order_value');
        var current_url = window.location.href;
        var is_get_params = current_url.indexOf('?') != -1;

        //assigning ordering value to the hidden field on filters panel
        $('#order_results_input').val(order_value);
        $('#filtering_form').submit();
    });

});