"""
Templates for Uploading Files to MetPetDB

ChemicalAnalysesTemplate and SampleTemplate extend Template     
and initialize their own of the following types:
    
    Complex: types to be stored in a list  [<field>]
        e.g. comments
    
    Required: these fields must be in each entry [<field>]
        e.g. sample_number
    
    DB_Types: fields related to other db_objects [<field>]  
        e.g. subsample related through subsample_id

    Types: mapping of fields to expected types  {<field>: <expected_type>} 
        e.g. {"analyst": str}

Additionally, SampleTemplate has an additional type:
    
    Selected {<field>: []}: fields that should only be included if checked 

All other fields are assumed to be simple, i.e. directly mapped
    e.g. where_done = "Rensselaer Polytechnic Institute"

"""
import copy

# labels are case insensitive!
sample_label_mappings = {
    'sample number':'number',
    'rock type':'rock_type_name',
    'latitude':'latitude',
    'longitude':'longitude',
    'location error':'location_error',
    'collector':'collector_name',
    'date of collection':'collection_date',
    'present sample location':'location_name',
    'country':'country',
    # multi-fields 
    'comment':'description',
    'reference':'references',
    'region':'regions',
    'metamorphic region':'metamorphic_regions',
    'metamorphic grade':'metamorphic_grades'
}

chem_analysis_label_mappings = {
    'sample':'sample',
    'subsample':'subsample',
    'mineral':'mineral',
    'method':'analysis_method',
    'subsample type':'subsample_type',
    'reference':'reference',
    'point':'spot_id',
    'analytical facility':'where_done',
    'analysis date':'analysis_date',
    'analyst':'analyst',
    'reference x':'reference_x',
    'reference y':'reference_y',
    'stage x':'stage_x',
    'stage y':'stage_y',
    'total':'total',
    'comment':'description'
}


class Template:
    def __init__(self, c_types = [], required = [], db_types = [], types = {}): 
        self.complex_types = c_types
        self.required = required 
        self.db_types = db_types
        self.data = ''
        self.amounts = {'element', 'oxide'}
        self.types = types

    def check_line_len(self):
        data = self.data
        if len(data) == 0:
            raise Exception("empty file")

        for i in range(1,len(data)):
            if len(data[i]) != len(data[i-1]):
                raise Exception("inconsistent line length. Expected {0}, but was {1}".format(len(data[i-1]), len(data[i])))
    
    def check_required(self, row):
        header = [x for x in row[0]]
        for i in range(0,len(header)):
            header[i] = header[i].lower()
        missing ={}
        for i in range(0, len(self.required)):
            if self.required[i] not in header:
                missing[self.required[i]] = 'missing'
        return missing

    def check_type(self, curr_row):
        errors = {}
        header = list(map(lambda x: x.strip(), curr_row[0])) #strip blank spaces from headings
        for i in range(0,len(header)):
            if header[i] in self.types.keys():
                # try to convert the field to the required type  
                if not isinstance(curr_row[1][i], self.types[header[i]]):
                    try:
                        curr_row[1][i] = self.types[header[i]](curr_row[1][i])
                    except:
                        errors[header[i]] = '{0} expected'.format(self.types[header[i]].__name__)
        return errors

    def check_data(self,curr_row):        
        errors = {}
        self.check_line_len()
        
        req_resp = self.check_required(curr_row)
        if len(req_resp) > 0:
            errors.update(req_resp)
        
        type_resp = self.check_type(curr_row)
        if len(type_resp) > 0:
            errors.update(type_resp)
        return errors

    class TemplateResult:
        def __init__(self, r_template): 
            self.rep = r_template

        def set_field_simple(self, field, value): 
            self.rep[field] = value
        
        def set_field_complex(self, field, value):
            self.rep[field].append(value)

        def get_rep(self): return self.rep


    def parse(self, data):
        self.data = data
     
        header = data[0]
        meta_header = self.get_meta_header(header)
        self.check_amounts(header)

        result = []
        result_template = {}
        for heading in header:
            if self.is_complex(heading): result_template[heading] = []
            else: result_template[heading] = ''
        result_template['errors'] = ''
        
        for i in range(1, len(data)):
            tmp_result = self.TemplateResult(copy.deepcopy(result_template))
            curr_row = [header, data[i]]
            errors = self.check_data(curr_row)

            for j in range(0,len(data[i])):
                heading = header[j]
                              
                field = data[i][j]
                # print("{}: {}".format(heading,data[i][j]))
                if self.is_complex(heading):
                    tmp_result.set_field_complex(heading,field)
                else: tmp_result.set_field_simple(heading, field)
            
            tmp_result.set_field_simple('errors', errors)
            result.append(tmp_result.get_rep())
        return result, meta_header

    def is_complex(self, name): return name.lower() in self.complex_types
    def is_required(self, name): return name.lower() in self.required
    def is_db_type(self, name): return name in self.db_types

class ChemicalAnalysesTemplate(Template):
    def __init__(self):
        complex_types = ["comment","element","oxide"]
        required = ["sample","subsample","point","mineral","method","subsample type"]
        db_types = ["element", "oxide"]
        types = {"comment": str, "stage_x" : float, "stage_y" : float, "reference_x": float, "reference_y": float}
        Template.__init__(self, complex_types, required, db_types, types)

    def check_amounts(self,header):
        amounts = ['elements', 'oxides']
        if header[-1] in amounts:
            raise Exception('missing {0} amount'.format(header[-1]))
        
        for i in range(0,len(header)-1):
            if header[i] in amounts and header[i+1] != 'amount':
                raise Exception('missing {0} amount'.format(header[i]))

    def get_amount(self,data=[], i=0,j=0):
        return data[i][j+1]
    
    def get_meta_header(self,header):
        mappings = {}
        added = set() 
        meta_header = []
        itr = iter(header)
        for heading in itr:
            if heading not in added:
                if heading in mappings.keys():
                    meta_header.append((heading, mappings[heading]))
                    added.add(heading)
                else:
                    meta_header.append((heading, heading))
                    added.add(heading)
        return meta_header

class SampleTemplate(Template):
    
    def __init__(self):
        complex_types = ["comment", "reference", "region", "metamorphic region", "metamorphic grade"]
        required = ["sample number", "latitude", "longitude", "rock type"]
        types = {"comment": str, "latitude": float, 'longitude': float}
        db_types = ["minerals"]
        #selected_types = {'minerals': ['el1', 'el2', 'el3']}
        Template.__init__(self, complex_types, required, db_types, types)
   
    def check_amounts(self,header):
        pass

    def get_amount(self,data=[],i=0,j=0):
        return 0
    
    def get_meta_header(self,header):
        mappings = {}
        added = set()
        meta_header = []
        itr = iter(header)
        for heading in itr:
            # if heading.lower() == 'latitude':
            #     for i in range (0,2): heading = next(itr)
            #     meta_header.append((('latitude','longitude'),'Location'))
            if heading not in added:
                if heading.lower() in mappings.keys():
                    meta_header.append((heading.lower(),heading))
                    added.add(heading)
                else:
                    meta_header.append((heading, heading))
                    added.add(heading)
        # print("\nMETA-HEADER:")
        # print(meta_header)
        # print("\n\n")
        return meta_header
