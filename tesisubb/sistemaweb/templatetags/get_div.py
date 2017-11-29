from django import template
from django.template.defaultfilters import stringfilter

register = template.Library ()


@register.filter (name='get_div')
def get_div(len1,len2):
    if len1 > len2:
        if len1 == 1:
            return 184
        else:
            if len1 == 2:
                return 206
            else:
                if len1 == 3:
                    return 228
                else:
                    if len1 == 4:
                        return 250
                    else:
                        if len1 == 5:
                            return 272
    else:
        if len2 == 1:
            return 184
        else:
            if len2 == 2:
                return 206
            else:
                if len2 == 3:
                    return 228
                else:
                    if len2 == 4:
                        return 250
                    else:
                        if len2 == 5:
                            return 272



