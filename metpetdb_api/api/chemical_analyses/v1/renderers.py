from rest_framework_csv import renderers as r

class ChemicalAnalysisCSVRenderer (r.CSVRenderer):

	def __init__(self):
		self.header = [
			'sample',
			'subsample',
			'spot_id',
			'mineral',
			'analysis_method',
			'subsample_type',
			'where_done',
			'analysis_date',
			'analyst',
			'reference',
			# 'reference_image'
			'reference_x',
			'reference_y',
			'elements',
			# 'oxides',
			'total',
			'stage_x', 
			'stage_y',
			'description',
			]
		self.labels = {
			'sample':'Sample',
			'subsample':'Subsample',
			'mineral':'Mineral',
			'analysis_method':'Method',
			'subsample_type':'Subsample Type',
			'reference':'Reference',
			'spot_id':'Point',
			'where_done':'Analytical Facility',
			'analysis_date':'Analysis Date',
			'analyst':'Analyst',
			'reference_x':'Reference X',
			'reference_y':'Reference Y',
			'stage_x':'Stage X', 
			'stage_y':'Stage Y',
			'description':'Comment',
			# 'elements',
			# 'oxides',
			'total':'Total',
			}

		self.num_elements = 0
		self.num_oxides = 0
		self.elements = set()
		self.oxides = set()

	def tablize(self, data, header=None, labels=None):
		if data:
			data = self.flatten_data(data)

			if 'elements' in header:
				data = tuple(data)
				header.remove('elements')
				els = list(self.elements)
				els.sort()
				oxs = list(self.oxides)
				oxs.sort()
				header[12:12] = oxs
				header[12:12] = els

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
			self.handle_elements(item)
			self.handle_oxides(item)
			flat_item = self.flatten_item(item)
			yield flat_item

	def handle_elements(self,item):
		for e in item['elements']:
			col = '{} ({})'.format(e['symbol'],e['measurement_unit'])
			prec = '{} Precision ({})'.format(e['symbol'],e['precision_type'])
			item[col] = e['amount']
			item[prec] = e['precision']
			self.elements.add(col)
			self.elements.add(prec)

	def handle_oxides(self,item):
		for o in item['oxides']:
			col = '{} ({})'.format(o['species'],o['measurement_unit'])
			prec = '{} Precision ({})'.format(o['species'],o['precision_type'])
			item[col] = o['amount']
			item[prec] = o['precision']
			self.oxides.add(col)
			self.oxides.add(prec)
