from rest_framework_csv import renderers as r


class SampleCSVRenderer (r.CSVRenderer):
    header = ['number',
            'rock_type',
            'description',
            'longitude',
            'latitude',
            'regions',
            # 'metamorphic_regions',
            'country',
            'collector_name',
            'collection_date',
            'location_name',
            'references',
            'metamorphic_grades',
            'minerals',
            # 'igsn',
            # 'subsample_ids',
            # 'chemical_analyses_ids',
            ]
    labels = {
        'number': 'Sample', 
        'rock_type': 'Rock Type', 
        'description': 'Comment', 
        'latitude': 'Latitude', 
        'longitude': 'Longitude', 
        # 'Location_Error': 'Location Error',
        'regions': 'Region', 
        'metamorphic_regions': 'Region',
        'country': 'Country', 
        'collector_name': 'Collector', 
        'collection_date': 'Date of Collection', 
        'location_name': 'Present Sample Location', 
        'references': 'Reference', 
        'metamorphic_grades': 'Metamorphic Grade', 
        'minerals': 'Mineral',
        # 'Subsamples': 'Number of Subsamples',
        # 'Chemical_Analyses': 'Number of Chemical Analyses'
    }

    def tablize(self, data, header=None, labels=None):
        if data:
            data = self.flatten_data(data)

            # materialize the generator so that it grabs all the
            # minerals in this sample set... figure out a better way
            # to do this (or just make it so that we're not working
            # with a generator in the first place? this looks silly)
            if 'minerals' in header:
                data = tuple(data)
                header.remove('minerals')

            if labels:
                yield [labels.get(x,x) for x in header]
            else:
                yield header

            for item in data:
                # print(item)
                row = [item.get(key,None) for key in header]
                yield row

        elif header:
            if labels:
                yield [labels.get(x,x) for x in header]
            else:
                yield header
        else:
            pass

    def flatten_data(self,data):
        for item in data:
            self.handle_minerals(item)
            self.handle_regions(item)
            # print(item)
            flat_item = self.flatten_item(item)
            # print(flat_item)
            yield flat_item

    def handle_minerals(self,item):
        for m in item['minerals']:
            item[m] = 'x'
            if m not in self.header:
                self.header.append(m)

    def handle_regions(self, item):
        regions = []
        item['regions'].extend(item['metamorphic_regions'])
        for r in item['regions']:
            regions.append(r.title())
        item['regions'] = list(set(regions))

    def flatten_item(self, item):
        if isinstance(item, list):
            flat_item = self.flatten_list(item)
        elif isinstance(item, dict):
            flat_item = self.flatten_dict(item)
        else:
            flat_item = {'': item}

        return flat_item

    def flatten_list(self, l):
        flat_list = {'': ', '.join(l)}
        return flat_list
