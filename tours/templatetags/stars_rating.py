from django import template
import math

register = template.Library()


"""
This custom template tag is needed for rendering "stars" rating based on decimal number of rating.
It should be placed within ul tag in a template with additional |s template tag.
For example like this:
<ul class="icon-group booking-item-rating-stars">
    {{ tour.rating|rendering_stars|safe }}
</ul>
"""
@register.filter(name='rendering_stars') #can be without extra name parameter and ()
def rendering_stars(value):

    rating_decimal_part, rating_main_part = math.modf(value)
    rating_main_part = int(rating_main_part)+1#to include last digit in loop (range(1, 3) will show only 1, 2)
    range_rating = range(1, rating_main_part)

    #possible values for stars are "empty", "semi-full", "full"
    star_max_nmb = 5
    stars = ["empty"]*star_max_nmb#populates the same element n times

    #i - starts with 1, counter start with 0 and it is used to reach 0-indexed element of the list
    counter = 0
    for i in range_rating:
        stars[counter] = "full"

        if i >= star_max_nmb:
            break
        else:
            counter+=1


    # adding semi-full star if there is decimal part in rating and
    # last i value of loop above is less than star_max_nmb.
    # This approach is needed for ratings > 5 (what is possible in testing server)
    if rating_decimal_part > 0 and i < star_max_nmb:
        stars[counter] = "semi-full"

    stars_tags = str()
    for star in stars:
        if star == "empty":
            stars_tags += '<li><i class="fa fa-star-o"></i></li>'
        elif star == "semi-full":
            stars_tags += '<li><i class="fa fa-star-half-empty"></i></li>'
        elif star == "full":
            stars_tags += '<li><i class="fa fa-star"></i></li>'

    return stars_tags