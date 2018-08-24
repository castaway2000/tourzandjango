if ($("#city_search_input").length > 0 && !$("#search_form").length > 0) {
    function initialize() {
        var input = document.getElementById('city_search_input');
        var options = {
            types: ['(cities)'],
            enablePoweredByContainer: false
        };
        var autocomplete = new google.maps.places.Autocomplete(input, options);
        console.log(1);
        google.maps.event.addListener(autocomplete, 'place_changed', function () {
            place = autocomplete.getPlace();
            document.getElementById('place_id').value = place.place_id;
            console.log("place_id: " + place.place_id);
            city_input = document.getElementById('city_search_input').value;
            console.log("full location: " + city_input);
            name_original = city_input.split(",")[0];
            console.log("name_original: " + name_original);
            if (name_original) {
                $.ajax({
                    url: "/en/ajax/rate_agregate/",
                    data: {
                        'location': name_original
                    },
                    dataType: 'json',
                    success: function (res) {
                        console.log(res.rates.rate__avg);
                        if ($("#average-rate")){
                            if (res.rates.rate__avg !== null) {
                                document.getElementById("average-rate").innerText = 'The average rate in your area is: $' + Math.round(res.rates.rate__avg) + ' per hour';
                            } else {
                                document.getElementById("average-rate").innerText = '';
                            }
                        }
                    }
                })
            }
        })
    }

    google.maps.event.addDomListener(window, 'load', initialize);
    $(document).ready(function () {
        $('#city_search_input').on("change", function () {
            if (!$(this).val()) {
                $("#place_id").val("");
            }
        })
    });
}
else {
    console.log('country');
    function initialize() {
        if ($("#location_search_input").length > 0) {
            var search_input = $("#location_search_input");
            var input = document.getElementById('location_search_input');
            var options = {
                types: ['(regions)'],
                enablePoweredByContainer: false
            };
        } else {
            var search_input = $("#city_search_input");
            var input = document.getElementById('city_search_input');
            var options = {
                types: ['(cities)'],
                enablePoweredByContainer: false
            };
        }

        var autocomplete = new google.maps.places.Autocomplete(input, options);
        google.maps.event.addListener(autocomplete, 'place_changed', function () {
            place = autocomplete.getPlace();
            document.getElementById('place_id').value = place.place_id;
            console.log("place_id: " + place.place_id);
            location_input = input.value;
            console.log("full location: " + location_input);
            name_original = location_input.split(",")[0];
            console.log("name_original: " + name_original);
            console.log(place);
            if (name_original) {
                $.ajax({
                    url: "/en/ajax/rate_agregate/",
                    data: {'location': name_original},
                    dataType: 'json',
                    success: function (res) {
                        console.log(res.rates.rate__avg);
                        if ($("#average-rate")){
                           if (res.rates.rate__avg !== null) {
                                document.getElementById("average-rate").innerText = 'The average rate in your area is: $'
                                    + Math.round(res.rates.rate__avg) + ' per hour';
                            }
                            else {
                                document.getElementById("average-rate").innerText = '';
                            }
                        }
                    }
                })
            }
            if ("address_components" in place) {
                var place_types = place["address_components"][0]["types"];
                console.log(place_types);
                console.log($.inArray("country", place_types));
                if ($.inArray("country", place_types) != -1) {
                    $("#is_country").prop("checked", true);
                } else {
                    $("#is_country").prop("checked", false);
                }
            } else {
                $("#is_country").prop("checked", false);
            }
            search_input.focus();
            console.log("finish");
            $("#search_form").submit();
        })
    }

    google.maps.event.addDomListener(window, 'load', initialize);

    $(document).ready(function () {
        console.log('doc ready');
        if ($("#location_search_input").length > 0) {
            var search_input = $("#location_search_input")
        } else {
            var search_input = $("#city_search_input");
        }
        search_input.on("change", function () {
            console.log('onchange');
            if (!$(this).val()) {
                $("#place_id").val("");
            }
        })
    });
}