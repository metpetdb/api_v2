def sample_qs_optimizer(params, qs):
    try:
        fields = params.get('fields').split(',')
        if 'rock_types' in fields:
            qs = qs.select_related('rock_type')
        if 'metamorphic_grades' in fields:
            qs = qs.prefetch_related('metamorphic_grades')
        if 'metamorphic_regions' in fields:
            qs = qs.prefetch_related('metamorphic_regions')
        if 'minerals' in fields:
            qs = qs.prefetch_related('samplemineral_set__mineral')
        if 'owner' in fields:
            qs = qs.prefetch_related('owner')
    except AttributeError:
        qs = qs.select_related('rock_type')
        qs = qs.prefetch_related('metamorphic_grades',
                                 'metamorphic_regions',
                                 'samplemineral_set__mineral',
                                 'owner')
    return qs
