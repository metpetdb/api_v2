from django.contrib.gis.geos import Polygon


def sample_query(params, qs):

    if params.get('collectors'):
        qs = qs.filter(collector_name__in=params['collectors'].split(','))

    if params.get('numbers'):
        qs = qs.filter(number__in=params['numbers'].split(','))

    if params.get('countries'):
        qs = qs.filter(country__in=params['countries'].split(','))

    if params.get('location_bbox'):
        bbox  = Polygon.from_bbox(params['location_bbox'].split(','))
        qs = qs.filter(location_coords__contained=bbox)

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
        qs = qs.filter(user__name__in=params['owners'].split(','))

    if params.get('references'):
        qs = qs.filter(references__overlap=params['references'].split(','))

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

    if params.get('public_data'):
        if params['public_data'] == 'True':
            qs = qs.filter(public_data=True)
        elif params['public_data'] == 'False':
            qs = qs.filter(public_data=False)

    return qs
