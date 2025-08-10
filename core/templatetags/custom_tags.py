from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    if user is None:
        return False
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()