import json

from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import Polygon, GEOSException
from django.db.models import Q, F


def sample_query(user, params, qs):
    
    if isinstance(user, AnonymousUser):
        qs = qs.filter(public_data=True)
    else:
        qs = qs.filter(Q(owner=user) | Q(public_data=True))

    if params.get('provenance'):
        if params['provenance']=="Public":
            qs = qs.filter(Q(public_data=True))
        elif params['provenance'] == "Private":
            qs = qs.filter(Q(public_data=False))


    if params.get('ids'):
        qs = qs.filter(pk__in=params['ids'].split(','))

    if params.get('collectors'):
        qs = qs.filter(collector_name__in=params['collectors'].split(','))

    if params.get('numbers'):
        qs = qs.filter(number__in=params['numbers'].split(','))

    if params.get('countries'):
        qs = qs.filter(country__in=params['countries'].split(','))

    if params.get('location_bbox'):
        bbox  = Polygon.from_bbox(params['location_bbox'].split(','))
        qs = qs.filter(location_coords__contained=bbox)

    if params.get('polygon_coords'):
        try:
            polygon = Polygon((json.loads(params['polygon_coords'])))
        except GEOSException:
            raise ValueError("Invalid polygon coordinates. Please check if "
                             "the points form a closed linestring or not.")
        qs = qs.filter(location_coords__contained=polygon)

    if params.get('metamorphic_grades'):
        metamorphic_grades = params['metamorphic_grades'].split(',')
        qs = qs.filter(metamorphic_grades__name__in=metamorphic_grades)

    if params.get('metamorphic_regions'):
        metamorphic_regions = params['metamorphic_regions'].split(',')
        qs =qs.filter(metamorphic_regions__name__in=metamorphic_regions)

    if params.get('minerals'):
        minerals = params['minerals'].split(',')
        if params.get('minerals_and') == 'True':
            for mineral in minerals:
                qs = qs.extra(where=["""
                        EXISTS (
                            SELECT 0
                            FROM sample_minerals sm
                            INNER JOIN minerals m
                            ON sm.mineral_id = m.id
                            WHERE samples.id = sm.sample_id
                            AND m.name = %s
                        )
                     """], params=[mineral])
        else:
            qs = qs.filter(minerals__name__in=minerals)

    if params.get('owners'):
        qs = qs.filter(owner__name__in=params['owners'].split(','))

    if params.get('emails'):
        qs = qs.filter(owner__email__in=params['emails'].split(','))

    if params.get('references'):
        qs = qs.filter(references__name__in=params['references'].split(','))

    if params.get('regions'):
        qs = qs.filter(regions__overlap=params['regions'].split(','))

    if params.get('rock_types'):
        qs = qs.filter(rock_type__name__in=params['rock_types'].split(','))

    if params.get('start_date'):
        qs = qs.filter(collection_date__gt=params['start_date'])

    if params.get('end_date'):
        qs = qs.filter(collection_date__lt=params['end_date'])

    if params.get('sesar_number'):
        qs = qs.filter(sesar_number__in=params['sesar_number'].split(','))

    if params.get('ordering'):
        qs = qs.order_by(params['ordering'])

    return qs
