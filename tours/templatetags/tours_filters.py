from django import template
import math
import time
from django.template.defaulttags import GroupedResult

register = template.Library()

@register.filter(name='add_all_days')
def add_all_days(value):
    existing_days = dict()
    for index, item in enumerate(value):
        weekday = item.grouper
        existing_days[weekday] = index
    final_list = list()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for weekday in weekdays:
        if not weekday in existing_days:
            final_list.append(GroupedResult(grouper=weekday, list=[]))
        else:
            index = existing_days[weekday]
            current_item = value[index]
            final_list.append(current_item)

    return final_list