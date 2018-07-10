from rest_framework_csv import renderers as r


class SampleCSVRenderer (r.CSVRenderer):
    header = ['number',
            'rock_type',
            'description',
            'latitude',
            'longitude',
            'location_error',
            'country',
            'collector_name',
            'collection_date',
            'location_name',
            # 'references.0',
            # 'metamorphic_grades.0',
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
        'location_error': 'Location Error', 
        'country': 'Country', 
        'collector_name': 'Collector', 
        'collection_date': 'Date of Collection', 
        'location_name': 'Present Sample Location', 
        # 'references.0': 'Reference', 
        # 'metamorphic_grades.0': 'Metamorphic Grade', 
        'minerals': 'Mineral',
        # 'Subsamples': 'Number of Subsamples',
        # 'Chemical_Analyses': 'Number of Chemical Analyses'
    }

    num_regions = 0
    num_refs = 0
    num_grades = 0

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
                region_headers = []
                for i in range(self.num_regions):
                    region_headers.append('regions.' + str(i))
                    labels[region_headers[-1]] = 'Region'
                header[6:6] = region_headers
                ref_headers = []
                for i in range(self.num_refs):
                    ref_headers.append('references.' + str(i))
                    labels[ref_headers[-1]] = 'Reference'
                offset = 10 + self.num_regions
                header[offset:offset] = ref_headers
                grade_headers = []
                for i in range(self.num_grades):
                    grade_headers.append('metamorphic_grades.' + str(i))
                    labels[grade_headers[-1]] = 'Metamorphic Grade'
                offset += self.num_refs
                header[offset:offset] = grade_headers


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
            self.handle_regions(item)
            self.handle_minerals(item)
            self.handle_references(item)
            self.handle_meta_grades(item)
            # print(item)
            flat_item = self.flatten_item(item)
            # print(flat_item)
            yield flat_item

    def handle_minerals(self,item):
        for m in item['minerals']:
            item[m] = 'x'
            if m not in self.header:
                self.header.append(m)

    def handle_regions(self,item):
        regions = set()
        for r in item['regions']:
            regions.add(r.title())
        for r in item['metamorphic_regions']:
            regions.add(r.title())
        self.num_regions = max(self.num_regions,len(regions))

    def handle_references(self,item):
        refs = set()
        for r in item['references']:
            refs.add(r)
        self.num_refs = max(self.num_refs, len(refs))

    def handle_meta_grades(self,item):
        grades = set()
        for g in item['metamorphic_grades']:
            grades.add(g.title())
        self.num_grades = max(self.num_grades, len(grades))

    def flatten_item(self, item):
        if isinstance(item, list):
            flat_item = self.flatten_list(item)
        elif isinstance(item, dict):
            flat_item = self.flatten_dict(item)
        else:
            flat_item = {'': item}

        return flat_item
