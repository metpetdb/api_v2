def chemical_analysis_query(params, qs):
    if params.get('minerals'):
        qs = qs.filter(mineral__name__in=params['minerals'].split(','))

    if params.get('elements'):
        elements = params['elements'].split(',')
        if params.get('elements_and') == 'True':
            for element in elements:
                qs = qs.extra(where=["""
                        EXISTS (
                            SELECT 0
                            FROM chemical_analysis_elements cae
                            INNER JOIN elements e
                            ON cae.element_id = e.id
                            WHERE chemical_analyses.id = cae.chemical_analysis_id
                            AND e.name = %s
                        )
                     """], params=[element])
        else:
            qs = qs.filter(elements__name__in=params['elements'].split(','))

    if params.get('oxides'):
        oxides = params['oxides'].split(',')
        if params.get('oxides_and') == 'True':
            for oxide in oxides:
                qs = qs.extra(where=["""
                        EXISTS (
                            SELECT 0
                            FROM chemical_analysis_oxides cao
                            INNER JOIN oxides o
                            ON cao.oxide_id = o.id
                            WHERE chemical_analyses.id = cao.chemical_analysis_id
                            AND o.species = %s
                        )
                     """], params=[oxide])
        else:
            qs = qs.filter(oxides__species__in=params['oxides'].split(','))

    if params.get('subsample_ids'):
        qs = qs.filter(subsample_id__in=params.get('subsample_ids').split(','))

    if params.get('public_data'):
        if params['public_data'] == 'True':
            qs = qs.filter(public_data=True)
        elif params['public_data'] == 'False':
            qs = qs.filter(public_data=False)

    return qs
