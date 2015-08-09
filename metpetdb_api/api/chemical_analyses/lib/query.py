def chemical_analysis_query(params, qs):
    if params.get('minerals'):
        qs = qs.filter(minerals__name__in=params['minerals'].split(','))

    if params.get('elements'):
        qs = qs.filter(elements__name__in=params['elements'].split(','))

    if params.get('oxides'):
        qs = qs.filter(oxides__species__in=params['oxides'].split(','))

    if params.get('public_data'):
        if params['public_data'] == 'True':
            qs = qs.filter(public_data=True)
        elif params['public_data'] == 'False':
            qs = qs.filter(public_data=False)

    return qs
