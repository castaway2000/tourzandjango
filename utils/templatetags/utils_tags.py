from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.text import normalize_newlines
from urllib.parse import urlencode
from django import template
register = template.Library()
from tourzan.settings import MEDIA_URL


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.filter
def get_class(value):
    return value.__class__.__name__


@register.simple_tag(takes_context=True)
def get_sized_image(context, obj, default_size="large", image_base_field_name="image"):
    """
    This template tags assumes the same names of image fields on the objects to apply it:
    "image", "image_large", "image_medium", "image_small".

    image_base_field_name - name of the field for image without _size tag
    """
    request = context["request"]
    if hasattr(obj, image_base_field_name):
        img = getattr(obj, image_base_field_name)
        print(str(img))
        if len(str(img)) == 0 or str(img)[0] == '/':  # error with old default image and a leading /
            default_media = 'tours/small_size/default_tour_image.jpg'
            return "%s%s" % (MEDIA_URL, default_media)
        if request and request.user_agent.is_mobile:
            image_field_name = "%s_%s" % (image_base_field_name, "medium")
            if hasattr(obj, image_field_name):
                img = getattr(obj, image_field_name)
        else:
            image_field_name = "%s_%s" % (image_base_field_name, default_size)
            if hasattr(obj, image_field_name):
                img = getattr(obj, image_field_name)
        return "%s%s" % (MEDIA_URL, img)
    else:
        page = request.path.split('/')[2]
        default_media = 'tours/small_size/default_tour_image.jpg'
        media = "%s%s" % (MEDIA_URL, default_media)
        return media


@register.filter
def remove_newlines(text):
    """
    Removes all newline characters from a block of text.
    """
    # First normalize the newlines using Django's nifty utility
    normalized_text = normalize_newlines(text)
    # Then simply remove the newlines like so.
    return mark_safe(normalized_text.replace('\n', ' '))
remove_newlines.is_safe = True
remove_newlines = stringfilter(remove_newlines)
register.filter(remove_newlines)
