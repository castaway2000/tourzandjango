function initialize(){
    var input = document.getElementById('city_search_input');
    var options ={
        types: ['(cities)'],
        enablePoweredByContainer: false
    };
    var autocomplete = new google.maps.places.Autocomplete(input, options);
    console.log(1)
    google.maps.event.addListener(autocomplete, 'place_changed', function(){
        place = autocomplete.getPlace();
        document.getElementById('place_id').value = place.place_id;
        console.log("place_id: "+place.place_id);
        city_input = document.getElementById('city_search_input').value;
        console.log("full location: "+city_input);
        name_original = city_input.split(",")[0];
        console.log("name_original: "+name_original);
    })
}
google.maps.event.addDomListener(window, 'load', initialize);


$(document).ready(function(){
    $('#city_search_input').on("change", function(){
        if(! $(this).val()){
            $("#place_id").val("");
        }
    })
})
