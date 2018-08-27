from __future__ import unicode_literals

from django.contrib.gis.db import models


class Users(models.Model):
    user_id = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=128, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=15, blank=True, null=True)
    institution = models.CharField(max_length=300, blank=True, null=True)
    reference_email = models.CharField(max_length=255, blank=True, null=True)
    confirmation_code = models.CharField(max_length=32, blank=True, null=True)
    enabled = models.CharField(max_length=1)
    role_id = models.SmallIntegerField(blank=True, null=True)
    contributor_code = models.CharField(max_length=32, blank=True, null=True)
    contributor_enabled = models.CharField(max_length=1, blank=True, null=True)
    professional_url = models.CharField(max_length=255, blank=True, null=True)
    research_interests = models.CharField(max_length=1024, blank=True, null=True)
    request_contributor = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class RockType(models.Model):
    rock_type_id = models.SmallIntegerField(primary_key=True)
    rock_type = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'rock_type'


class Samples(models.Model):
    sample_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    sesar_number = models.CharField(max_length=9, blank=True, null=True)
    public_data = models.CharField(max_length=1)
    collection_date = models.DateTimeField(blank=True, null=True)
    date_precision = models.SmallIntegerField(blank=True, null=True)
    number = models.CharField(max_length=35)
    rock_type = models.ForeignKey(RockType)
    user = models.ForeignKey(Users)
    location_error = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    collector = models.CharField(max_length=50, blank=True, null=True)
    collector_0 = models.ForeignKey(Users,
                                    db_column='collector_id',
                                    related_name='+',
                                    blank=True,
                                    null=True)  # Field renamed because of name conflict.
    location_text = models.CharField(max_length=50, blank=True, null=True)
    location = models.GeometryField()

    class Meta:
        managed = False
        db_table = 'samples'


class MetamorphicGrades(models.Model):
    metamorphic_grade_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'metamorphic_grades'


class SampleMetamorphicGrades(models.Model):
    sample = models.ForeignKey('Samples')
    metamorphic_grade = models.ForeignKey(MetamorphicGrades)

    class Meta:
        managed = False
        db_table = 'sample_metamorphic_grades'
        unique_together = (('sample', 'metamorphic_grade'),)


class MetamorphicRegions(models.Model):
    metamorphic_region_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    shape = models.GeometryField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    label_location = models.GeometryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metamorphic_regions'


class SampleMetamorphicRegions(models.Model):
    sample = models.ForeignKey('Samples')
    metamorphic_region = models.ForeignKey(MetamorphicRegions)

    class Meta:
        managed = False
        db_table = 'sample_metamorphic_regions'
        unique_together = (('sample', 'metamorphic_region'),)


class SampleMetamorphicRegionsBkup(models.Model):
    sample_id = models.BigIntegerField(blank=True, null=True)
    metamorphic_region_id = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_metamorphic_regions_bkup'


class Minerals(models.Model):
    mineral_id = models.SmallIntegerField(primary_key=True)
    real_mineral = models.ForeignKey('self')
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'minerals'


class SampleMinerals(models.Model):
    mineral = models.ForeignKey(Minerals)
    sample = models.ForeignKey('Samples')
    amount = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sample_minerals'
        unique_together = (('mineral', 'sample'),)


class Reference(models.Model):
    reference_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'reference'


class SampleReference(models.Model):
    sample = models.ForeignKey('Samples')
    reference = models.ForeignKey(Reference)

    class Meta:
        managed = False
        db_table = 'sample_reference'
        unique_together = (('sample', 'reference'),)


class Regions(models.Model):
    region_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'regions'


# class ImageTypes(models.Model):
#     image_type_id = models.SmallIntegerField(primary_key=True)
#     image_type = models.CharField(null=False, max_length=100)
#     abbreviation = models.CharField(max_length=10)
#     comments = models.CharField(max_length=250)
#
#     class Meta:
#         managed = False
#         db_table = 'image_type'
#
#
# class Images(models.Model):
#     image_id = models.BigIntegerField(primary_key=True)
#     checksum = models.CharField(max_length=50, null=False)
#     version = models.IntegerField(null=False)
#     sample_id = models.BigIntegerField
#     subsample_id = models.BigIntegerField
#     image_format_id = models.SmallIntegerField
#     image_type_id = models.SmallIntegerField(null=False)
#     width = models.SmallIntegerField(null=False)
#     height = models.SmallIntegerField(null=False)
#     collector = models.CharField(max_length=50)
#     description = models.CharField(max_length=1024)
#     scale = models.SmallIntegerField
#     user_id = models.IntegerField(null=False)
#     public_data = models.CharField(max_length=1, null=False)
#     checksum_64x64 = models.CharField(max_length=50, null=False)
#     checksum_half = models.CharField(max_length=50, null=False)
#     filename = models.CharField(max_length=256, null=False)
#     checksum_mobile = models.CharField(max_length=50)
#
#     class Meta:
#         managed = False
#         db_table = 'images'

class SampleRegions(models.Model):
    sample = models.ForeignKey('Samples')
    region = models.ForeignKey(Regions)

    class Meta:
        managed = False
        db_table = 'sample_regions'
        unique_together = (('sample', 'region'),)


class SampleAliases(models.Model):
    sample_alias_id = models.BigIntegerField(primary_key=True)
    sample = models.ForeignKey('Samples', blank=True, null=True)
    alias = models.CharField(max_length=35)

    class Meta:
        managed = False
        db_table = 'sample_aliases'
        unique_together = (('sample', 'alias'),)



class SubsampleType(models.Model):
    subsample_type_id = models.SmallIntegerField(primary_key=True)
    subsample_type = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'subsample_type'


class Subsamples(models.Model):
    subsample_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    public_data = models.CharField(max_length=1)
    sample = models.ForeignKey(Samples)
    user = models.ForeignKey('Users')
    grid_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=100)
    subsample_type = models.ForeignKey(SubsampleType)

    class Meta:
        managed = False
        db_table = 'subsamples'
        # unique_together = (('sample_id', 'None'),)


class Grids(models.Model):
    grid_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    subsample = models.ForeignKey('Subsamples')
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    public_data = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'grids'


# class AdminUsers(models.Model):
#     admin_id = models.IntegerField(primary_key=True)
#     user = models.ForeignKey('Users')
#
#     class Meta:
#         managed = False
#         db_table = 'admin_users'
#
#
class ChemicalAnalyses(models.Model):
    chemical_analysis_id = models.BigIntegerField(primary_key=True)
    version = models.IntegerField()
    subsample = models.ForeignKey('Subsamples')
    public_data = models.CharField(max_length=1)
    reference_x = models.FloatField(blank=True, null=True)
    reference_y = models.FloatField(blank=True, null=True)
    stage_x = models.FloatField(blank=True, null=True)
    stage_y = models.FloatField(blank=True, null=True)
    image = models.ForeignKey('Images', blank=True, null=True)
    analysis_method = models.CharField(max_length=50, blank=True, null=True)
    where_done = models.CharField(max_length=50, blank=True, null=True)
    analyst = models.CharField(max_length=50, blank=True, null=True)
    analysis_date = models.DateTimeField(blank=True, null=True)
    date_precision = models.SmallIntegerField(blank=True, null=True)
    reference = models.ForeignKey('Reference', blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    mineral = models.ForeignKey('Minerals', blank=True, null=True)
    user = models.ForeignKey('Users')
    large_rock = models.CharField(max_length=1)
    total = models.FloatField(blank=True, null=True)
    spot_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'chemical_analyses'


class ChemicalAnalysisElements(models.Model):
    chemical_analysis = models.ForeignKey(ChemicalAnalyses)
    element = models.ForeignKey('Elements')
    amount = models.FloatField()
    precision = models.FloatField(blank=True, null=True)
    precision_type = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit = models.CharField(max_length=4, blank=True, null=True)
    min_amount = models.FloatField(blank=True, null=True)
    max_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chemical_analysis_elements'
        unique_together = (('chemical_analysis', 'element'),)


class ChemicalAnalysisOxides(models.Model):
    chemical_analysis = models.ForeignKey(ChemicalAnalyses)
    oxide = models.ForeignKey('Oxides')
    amount = models.FloatField()
    precision = models.FloatField(blank=True, null=True)
    precision_type = models.CharField(max_length=3, blank=True, null=True)
    measurement_unit = models.CharField(max_length=4, blank=True, null=True)
    min_amount = models.FloatField(blank=True, null=True)
    max_amount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chemical_analysis_oxides'
        unique_together = (('chemical_analysis', 'oxide'),)


class ElementMineralTypes(models.Model):
    element = models.ForeignKey('Elements')
    mineral_type = models.ForeignKey('MineralTypes')

    class Meta:
        managed = False
        db_table = 'element_mineral_types'
        unique_together = (('element', 'mineral_type'),)


class Elements(models.Model):
    element_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    alternate_name = models.CharField(max_length=100, blank=True, null=True)
    symbol = models.CharField(unique=True, max_length=4)
    atomic_number = models.IntegerField()
    weight = models.FloatField(blank=True, null=True)
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'elements'
#
#
class Georeference(models.Model):
    georef_id = models.BigIntegerField(primary_key=True)
    title = models.TextField()
    first_author = models.TextField()
    second_authors = models.TextField(blank=True, null=True)
    journal_name = models.TextField()
    full_text = models.TextField()
    reference_number = models.TextField(blank=True, null=True)
    reference_id = models.BigIntegerField(blank=True, null=True)
    doi = models.TextField(blank=True, null=True)
    journal_name_2 = models.TextField(blank=True, null=True)
    publication_year = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'georeference'


class ImageComments(models.Model):
    comment_id = models.BigIntegerField(primary_key=True)
    image = models.ForeignKey('Images')
    comment_text = models.TextField()
    version = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'image_comments'


class ImageFormat(models.Model):
    image_format_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'image_format'


class ImageOnGrid(models.Model):
    image_on_grid_id = models.BigIntegerField(primary_key=True)
    grid = models.ForeignKey(Grids)
    image = models.ForeignKey('Images')
    top_left_x = models.FloatField()
    top_left_y = models.FloatField()
    z_order = models.SmallIntegerField()
    opacity = models.SmallIntegerField()
    resize_ratio = models.FloatField()
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    checksum = models.CharField(max_length=50)
    checksum_64x64 = models.CharField(max_length=50)
    checksum_half = models.CharField(max_length=50)
    locked = models.CharField(max_length=1)
    angle = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'image_on_grid'


class ImageReference(models.Model):
    image = models.ForeignKey('Images')
    reference = models.ForeignKey('Reference')

    class Meta:
        managed = False
        db_table = 'image_reference'


class ImageType(models.Model):
    image_type_id = models.SmallIntegerField(primary_key=True)
    image_type = models.CharField(unique=True, max_length=100)
    abbreviation = models.CharField(unique=True, max_length=10, blank=True, null=True)
    comments = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'image_type'


class Images(models.Model):
    image_id = models.BigIntegerField(primary_key=True)
    checksum = models.CharField(max_length=50)
    version = models.IntegerField()
    sample = models.ForeignKey('Samples', blank=True, null=True)
    subsample = models.ForeignKey('Subsamples', blank=True, null=True)
    image_format = models.ForeignKey(ImageFormat, blank=True, null=True)
    image_type = models.ForeignKey(ImageType)
    width = models.SmallIntegerField()
    height = models.SmallIntegerField()
    collector = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    scale = models.SmallIntegerField(blank=True, null=True)
    user = models.ForeignKey('Users')
    public_data = models.CharField(max_length=1)
    checksum_64x64 = models.CharField(max_length=50)
    checksum_half = models.CharField(max_length=50)
    filename = models.CharField(max_length=256)
    checksum_mobile = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'images'

#
#
#
# class MetamorphicRegionsBkup(models.Model):
#     metamorphic_region_id = models.BigIntegerField(blank=True, null=True)
#     name = models.CharField(max_length=50, blank=True, null=True)
#     shape = models.GeometryField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     label_location = models.GeometryField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'metamorphic_regions_bkup'
#
#
class MineralRelationships(models.Model):
    parent_mineral = models.ForeignKey('Minerals', related_name='parent')
    child_mineral = models.ForeignKey('Minerals', related_name='child')

    class Meta:
        managed = False
        db_table = 'mineral_relationships'
        unique_together = (('parent_mineral', 'child_mineral'),)
#
#
class MineralTypes(models.Model):
    mineral_type_id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'mineral_types'



class OxideMineralTypes(models.Model):
    oxide = models.ForeignKey('Oxides')
    mineral_type = models.ForeignKey(MineralTypes)

    class Meta:
        managed = False
        db_table = 'oxide_mineral_types'
        unique_together = (('oxide', 'mineral_type'),)


class Oxides(models.Model):
    oxide_id = models.SmallIntegerField(primary_key=True)
    element = models.ForeignKey(Elements)
    oxidation_state = models.SmallIntegerField(blank=True, null=True)
    species = models.CharField(unique=True, max_length=20, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    cations_per_oxide = models.SmallIntegerField(blank=True, null=True)
    conversion_factor = models.FloatField()
    order_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oxides'
#
#
# class ProjectInvites(models.Model):
#     invite_id = models.IntegerField(primary_key=True)
#     project = models.ForeignKey('Projects')
#     user = models.ForeignKey('Users')
#     action_timestamp = models.DateTimeField()
#     status = models.CharField(max_length=32, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'project_invites'
#
#
# class ProjectMembers(models.Model):
#     project = models.ForeignKey('Projects')
#     user = models.ForeignKey('Users')
#
#     class Meta:
#         managed = False
#         db_table = 'project_members'
#         unique_together = (('project_id', 'user_id'),)
#
#
# class ProjectSamples(models.Model):
#     project = models.ForeignKey('Projects')
#     sample = models.ForeignKey('Samples')
#
#     class Meta:
#         managed = False
#         db_table = 'project_samples'
#
#
# class Projects(models.Model):
#     project_id = models.IntegerField(primary_key=True)
#     version = models.IntegerField()
#     user = models.ForeignKey('Users')
#     name = models.CharField(max_length=50)
#     description = models.CharField(max_length=300, blank=True, null=True)
#     isactive = models.CharField(max_length=1, blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'projects'
#         unique_together = (('user_id', 'name'),)
#
#
#
#
#
# class RoleChanges(models.Model):
#     role_changes_id = models.BigIntegerField(primary_key=True)
#     user = models.ForeignKey('Users')
#     sponsor = models.ForeignKey('Users')
#     request_date = models.DateTimeField()
#     finalize_date = models.DateTimeField(blank=True, null=True)
#     role = models.ForeignKey('Roles')
#     granted = models.CharField(max_length=1, blank=True, null=True)
#     grant_reason = models.TextField(blank=True, null=True)
#     request_reason = models.TextField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'role_changes'
#         unique_together = (('user_id', 'granted', 'role_id'),)
#
#
# class Roles(models.Model):
#     role_id = models.SmallIntegerField(primary_key=True)
#     role_name = models.CharField(max_length=50)
#     rank = models.SmallIntegerField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'roles'
#

#
#
# class SampleComments(models.Model):
#     comment_id = models.BigIntegerField(primary_key=True)
#     sample = models.ForeignKey('Samples')
#     user = models.ForeignKey('Users')
#     comment_text = models.TextField()
#     date_added = models.DateTimeField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'sample_comments'
#
#
# class UploadedFiles(models.Model):
#     uploaded_file_id = models.BigIntegerField(primary_key=True)
#     hash = models.CharField(max_length=50)
#     filename = models.CharField(max_length=255)
#     time = models.DateTimeField()
#     user = models.ForeignKey('Users', blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'uploaded_files'
#
#
#
#
# class UsersRoles(models.Model):
#     user_id = models.IntegerField()
#     role_id = models.SmallIntegerField()
#
#     class Meta:
#         managed = False
#         db_table = 'users_roles'
#
#

class XrayImage(models.Model):
    image = models.OneToOneField(Images, primary_key=True)
    element = models.CharField(max_length=256, blank=True, null=True)
    dwelltime = models.SmallIntegerField(blank=True, null=True)
    current = models.SmallIntegerField(blank=True, null=True)
    voltage = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'xray_image'
