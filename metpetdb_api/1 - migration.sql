-- Script drops un-necessary tables and handles composite keys

DROP TABLE chemical_analyses_archive CASCADE;

DROP TABLE chemical_analysis_elements_archive CASCADE;

DROP TABLE chemical_analysis_elements_dup CASCADE;

DROP TABLE chemical_analysis_oxides_archive CASCADE;

DROP TABLE chemical_analysis_oxides_dup CASCADE;

DROP TABLE element_mineral_types_dup CASCADE;

DROP TABLE georeference_bkup CASCADE;

-- DROP TABLE georeference_bkup_2 CASCADE;

DROP TABLE mineral_relationships_dup CASCADE;

DROP TABLE oxide_mineral_types_dup CASCADE;

DROP TABLE reference_bkup CASCADE;

-- DROP TABLE reference_bkup_2 CASCADE;

DROP TABLE sample_metamorphic_grades_archive CASCADE;

DROP TABLE sample_metamorphic_grades_dup CASCADE;

DROP TABLE sample_metamorphic_regions_dup CASCADE;

DROP TABLE sample_minerals_archive CASCADE;

DROP TABLE sample_minerals_dup CASCADE;

DROP TABLE sample_reference_archive CASCADE;

DROP TABLE sample_reference_bkup CASCADE;

DROP TABLE sample_reference_dup CASCADE;

DROP TABLE sample_regions_archive CASCADE;

DROP TABLE sample_regions_dup CASCADE;

DROP TABLE samples_archive CASCADE;

DROP TABLE subsamples_archive CASCADE;

-- Handle composite keys

--http://postgresql.1045698.n5.nabble.com/Sequence-vs-Serial-td2149000.html

ALTER TABLE chemical_analysis_elements OWNER TO metpetdb;

ALTER TABLE chemical_analysis_elements DROP CONSTRAINT IF EXISTS analysis_elements_sk;

ALTER TABLE chemical_analysis_elements ADD CONSTRAINT analysis_elements_uk UNIQUE (chemical_analysis_id, element_id);

ALTER TABLE chemical_analysis_elements ADD COLUMN id SERIAL;

ALTER TABLE chemical_analysis_elements ADD PRIMARY KEY (id);

ALTER TABLE chemical_analysis_oxides DROP CONSTRAINT IF EXISTS analysis_oxides_sk;

ALTER TABLE chemical_analysis_oxides ADD CONSTRAINT analysis_oxides_uk UNIQUE (chemical_analysis_id , oxide_id);

ALTER TABLE chemical_analysis_oxides ADD COLUMN id SERIAL;

ALTER TABLE chemical_analysis_oxides ADD PRIMARY KEY (id);

ALTER TABLE element_mineral_types DROP CONSTRAINT IF EXISTS element_mineral_types_sk;

ALTER TABLE element_mineral_types ADD CONSTRAINT element_mineral_types_uk UNIQUE (element_id , mineral_type_id );

ALTER TABLE element_mineral_types ADD COLUMN id SERIAL;

ALTER TABLE element_mineral_types ADD PRIMARY KEY (id);

-- ALTER TABLE geometry_columns DROP CONSTRAINT IF EXISTS geometry_columns_pk;

-- ALTER TABLE geometry_columns ADD CONSTRAINT geometry_columns_uk UNIQUE (f_table_catalog , f_table_schema , f_table_name , f_geometry_column);

-- ALTER TABLE geometry_columns ADD COLUMN id SERIAL;

-- ALTER TABLE geometry_columns ADD PRIMARY KEY (id);

ALTER TABLE image_reference DROP CONSTRAINT IF EXISTS image_reference_pk;

ALTER TABLE image_reference ADD CONSTRAINT image_reference_uk UNIQUE (image_id , reference_id);

ALTER TABLE image_reference ADD COLUMN id SERIAL;

ALTER TABLE image_reference ADD PRIMARY KEY (id);

ALTER TABLE mineral_relationships DROP CONSTRAINT IF EXISTS mineral_relationships_sk;

ALTER TABLE mineral_relationships ADD CONSTRAINT mineral_relationships_uk UNIQUE (parent_mineral_id , child_mineral_id);

ALTER TABLE mineral_relationships ADD COLUMN id SERIAL;

ALTER TABLE mineral_relationships ADD PRIMARY KEY (id);

ALTER TABLE oxide_mineral_types DROP CONSTRAINT IF EXISTS oxide_mineral_types_sk;

ALTER TABLE oxide_mineral_types ADD CONSTRAINT oxide_mineral_types_uk UNIQUE (oxide_id , mineral_type_id);

ALTER TABLE oxide_mineral_types ADD COLUMN id SERIAL;

ALTER TABLE oxide_mineral_types ADD PRIMARY KEY (id);

ALTER TABLE project_members DROP CONSTRAINT IF EXISTS project_members_nk;

ALTER TABLE project_members ADD CONSTRAINT project_members_uk UNIQUE (project_id , user_id);

ALTER TABLE project_members ADD COLUMN id SERIAL;

ALTER TABLE project_members ADD PRIMARY KEY (id);

ALTER TABLE sample_metamorphic_grades DROP CONSTRAINT IF EXISTS samples_metgrade_pk;

ALTER TABLE sample_metamorphic_grades ADD CONSTRAINT samples_metgrade_uk UNIQUE (sample_id , metamorphic_grade_id);

ALTER TABLE sample_metamorphic_grades ADD COLUMN id SERIAL;

ALTER TABLE sample_metamorphic_grades ADD PRIMARY KEY (id);

ALTER TABLE sample_metamorphic_regions DROP CONSTRAINT IF EXISTS samples_metregion_pk;

ALTER TABLE sample_metamorphic_regions ADD CONSTRAINT samples_metregion_uk UNIQUE (sample_id , metamorphic_region_id);

ALTER TABLE sample_metamorphic_regions ADD COLUMN id SERIAL;

ALTER TABLE sample_metamorphic_regions ADD PRIMARY KEY (id);

ALTER TABLE sample_minerals DROP CONSTRAINT IF EXISTS sample_minerals_nk;

ALTER TABLE sample_minerals ADD CONSTRAINT sample_minerals_uk UNIQUE (mineral_id , sample_id);

ALTER TABLE sample_minerals ADD COLUMN id SERIAL;

ALTER TABLE sample_minerals ADD PRIMARY KEY (id);

ALTER TABLE sample_reference DROP CONSTRAINT IF EXISTS sample_reference_pk;

ALTER TABLE sample_reference ADD CONSTRAINT sample_reference_pk UNIQUE (sample_id , reference_id);

ALTER TABLE sample_reference ADD COLUMN id SERIAL;

ALTER TABLE sample_reference ADD PRIMARY KEY (id);

ALTER TABLE sample_regions DROP CONSTRAINT IF EXISTS sample_region_pk;

ALTER TABLE sample_regions ADD CONSTRAINT sample_region_uk UNIQUE (sample_id , region_id);

ALTER TABLE sample_regions ADD COLUMN id SERIAL;

ALTER TABLE sample_regions ADD PRIMARY KEY (id);

-- project_samples has no primary key

ALTER TABLE project_samples ADD COLUMN id SERIAL;

ALTER TABLE project_samples ADD PRIMARY KEY (id);


ALTER TABLE users ALTER COLUMN password DROP NOT NULL;

ALTER TABLE users ALTER COLUMN password TYPE character varying(128);
