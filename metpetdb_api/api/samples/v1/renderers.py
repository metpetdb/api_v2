from rest_framework_csv import renderers as r


class SampleCSVRenderer (r.CSVRenderer):

    def __init__(self):
        self.header = [
            'number',
            'rock_type',
            'description',
            'latitude',
            'longitude',
            'location_error',
            'country',
            'collector_name',
            'collection_date',
            'location_name',
            'minerals',
            ]
        self.labels = {
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
            'minerals': 'Mineral',
        }

        self.num_regions = 0
        self.num_meta_regions = 0
        self.num_refs = 0
        self.num_grades = 0
        self.minerals = set()
        self.fields = set()

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
                meta_region_headers = []
                for i in range(self.num_meta_regions):
                    meta_region_headers.append('metamorphic_regions.' + str(i))
                    labels[meta_region_headers[-1]] = 'Metamorphic Region'
                offset = 6 + self.num_regions
                header[offset:offset] = meta_region_headers
                ref_headers = []
                for i in range(self.num_refs):
                    ref_headers.append('references.' + str(i))
                    labels[ref_headers[-1]] = 'Reference'
                offset += 4 + self.num_meta_regions
                header[offset:offset] = ref_headers
                grade_headers = []
                for i in range(self.num_grades):
                    grade_headers.append('metamorphic_grades.' + str(i))
                    labels[grade_headers[-1]] = 'Metamorphic Grade'
                offset += self.num_refs
                header[offset:offset] = grade_headers
                mins = list(self.minerals)
                mins.sort()
                header.extend(mins)
                header = [x for x in header if (x in self.fields or x in self.minerals or x in region_headers or x in meta_region_headers or x in ref_headers or x in grade_headers)]

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
            self.fields |= item.keys()
            if (item.get('regions')):
                self.handle_regions(item)
            if (item.get('metamorphic_regions')):
                self.handle_meta_regions(item)
            if (item.get('minerals')):
                self.handle_minerals(item)
            if (item.get('references')):
                self.handle_references(item)
            if (item.get('metamorphic_grades')):
                self.handle_meta_grades(item)
            flat_item = self.flatten_item(item)
            yield flat_item

    def handle_minerals(self,item):
        for m in item['minerals']:
            item[m] = 'x'
            self.minerals.add(m)

    def handle_regions(self,item):
        regions = {r.title() for r in item['regions']}
        self.num_regions = max(self.num_regions,len(regions))

    def handle_meta_regions(self,item):
        meta_regions = {r.title() for r in item['metamorphic_regions']}
        self.num_meta_regions = max(self.num_meta_regions,len(meta_regions))

    def handle_references(self,item):
        refs = {r for r in item['references']}
        self.num_refs = max(self.num_refs, len(refs))

    def handle_meta_grades(self,item):
        grades = {g.title() for g in item['metamorphic_grades']}
        self.num_grades = max(self.num_grades, len(grades))