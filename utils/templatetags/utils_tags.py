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
    if hasattr(obj, image_base_field_name):
        request = context["request"]
        img = getattr(obj, image_base_field_name)
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
        return None
