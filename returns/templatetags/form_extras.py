from django import template

register = template.Library()

ACCESSIBILITY_FEATURES = [
    ('mechanical_ramp', 'Mechanical access ramp'),
    ('centre_door_ramps', 'Centre door ramps'),
    ('exterior_displays', 'Exterior backlit route displays'),
    ('interior_stop_displays', 'Interior stop displays'),
    ('audio_announcements', 'Automated audible stop announcements'),
    ('yellow_handrails', 'Yellow coloured handrails'),
    ('priority_seating', 'Priority seating'),
    ('contrasting_seat_covers', 'Contrasting seat covers'),
    ('induction_loop', 'Induction loop system'),
]


@register.filter
def get_field(form, field_name):
    return form[field_name]


@register.filter
def field_id(form, field_name):
    return form[field_name].id_for_label


@register.simple_tag
def accessibility_features():
    return ACCESSIBILITY_FEATURES
