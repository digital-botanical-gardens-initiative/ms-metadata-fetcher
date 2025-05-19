import os

import pandas as pd
import requests
from dotenv import load_dotenv

# Loads .env variables
load_dotenv()


# Define variables
directus_instance = os.getenv("DIRECTUS_INSTANCE")
directus_login = f"{directus_instance}/auth/login"
# directus_status = f"{directus_instance}/items/Treatment_Status/"
directus_collections = [
    "Field_Data",
    "Curation_Data",
    "Dried_Samples_Data",
    "Extraction_Data",
    "Aliquoting_Data",
    "MS_Data",
]
directus_email = os.getenv("DIRECTUS_EMAIL")
directus_password = os.getenv("DIRECTUS_PASSWORD")


# Create a session object for making requests
session = requests.Session()

# Send a POST request to the login endpoint
response = session.post(directus_login, json={"email": directus_email, "password": directus_password})

# Test if connection is successful
if response.status_code == 200:
    # Stores the access token
    data = response.json()["data"]
    directus_token = data["access_token"]

    # Construct headers with authentication token
    headers = {"Authorization": f"Bearer {directus_token}", "Content-Type": "application/json"}

    # Retrieve ms informations

    directus_ms = f"{directus_instance}/items/MS_Data/"

    # Make a GET request to retrieve data
    # Here you can set the limit (e.g. limit=5) to retrieve only a few records for testing purposes
    # limit=-1 retrieves all records
    response = session.get(
        url=f"{directus_ms}?filter[batch][_eq]=114&fields=*,parent_sample_container.*,injection_volume_unit.*,injection_method.*,instrument_used.*,batch.*,user_created.*,user_update.*&limit=-1"
    )
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_ms = pd.json_normalize(data)

        # Add prefix to column headers
        df = df_ms.add_prefix("ms_")

        # Retrieve aliquots informations

        directus_aliquots = f"{directus_instance}/items/Aliquoting_Data/"

        # Make a GET request to retrieve data
        response = session.get(
            url=f"{directus_aliquots}?fields=*,sample_container.*,parent_sample_container.*,parent_container.*,aliquot_volume_unit.*,user_created.*,user_update.*&limit=-1"
        )

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()["data"]

            # Convert the list of dictionaries to a DataFrame
            df_al = pd.json_normalize(data)

            # Add prefix to column headers
            df_al = df_al.add_prefix("al_")

            # Merge the two DataFrames
            df = df.merge(df_al, left_on="ms_parent_sample_container.id", right_on="al_sample_container.id", how="left")

    # Retrieve extracts informations

    directus_extracts = f"{directus_instance}/items/Extraction_Data/"

    # Make a GET request to retrieve data
    response = session.get(
        url=f"{directus_extracts}?fields=*,sample_container.*,parent_sample_container.*,parent_container.*,dried_weight_unit.*,solvent_volume_unit.*,extraction_method.*,extraction_container.*,batch.*,user_created.*,user_update.*&limit=-1"
    )

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_ex = pd.json_normalize(data)

        # Add prefix to column headers
        df_ex = df_ex.add_prefix("ex_")
        # Merge the two DataFrames
        df = df.merge(df_ex, left_on="al_parent_sample_container.id", right_on="ex_sample_container.id", how="left")

    # Retrieve field samples informations

    directus_field_samples = f"{directus_instance}/items/Dried_Samples_Data/"

    # Make a GET request to retrieve data
    response = session.get(
        url=f"{directus_field_samples}?fields=*,sample_container.*,parent_container.*,field_data.*,user_created.*,user_update.*&limit=-1"
    )

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_fs = pd.json_normalize(data)

        # Add prefix to column headers
        df_fs = df_fs.add_prefix("dsp_")
        # Merge the two DataFrames
        df = df.merge(df_fs, left_on="ex_parent_sample_container.id", right_on="dsp_sample_container.id", how="left")

    # Retrieve inat informations

    directus_inat = f"{directus_instance}/items/Curation_Data/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_inat}?limit=-1")
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_inat = pd.json_normalize(data)

        # Add prefix to column headers
        df_inat = df_inat.add_prefix("inat_")
        # Merge the two DataFrames
        df = df.merge(df_inat, left_on="dsp_sample_container.container_id", right_on="inat_emi_external_id", how="left")


# Create sample_type column
df["sample_type"] = ""
for index, row in df.iterrows():
    if "blk" in row["al_sample_container.container_id"]:
        df.at[index, "sample_type"] = "blank"
    else:
        df.at[index, "sample_type"] = "sample"

columns_to_keep = [
    "ms_date_created",
    "ms_uuid_ms_file",
    "ms_status_comment",
    "ms_filename",
    "ms_injection_volume",
    "ms_injection_volume_unit.unit_name",
    "ms_injection_volume_unit.symbol",
    "ms_injection_method.status",
    "ms_injection_method.date_created",
    "ms_injection_method.method_name",
    "ms_injection_method.method_description",
    "ms_instrument_used.status",
    "ms_instrument_used.instrument_id",
    "ms_batch.status",
    "ms_batch.batch_id",
    "ms_batch.comments",
    "ms_batch.old_id",
    "ms_batch.short_description",
    "ms_batch.description",
    "ms_user_created.first_name",
    "ms_user_created.last_name",
    "ms_user_created.email",
    "al_status",
    "al_aliquot_volume",
    "al_sample_container.status",
    "al_sample_container.container_id",
    "al_sample_container.old_id",
    "al_parent_container.status",
    "al_parent_container.container_id",
    "al_aliquot_volume_unit.unit_name",
    "al_aliquot_volume_unit.symbol",
    "al_user_created.first_name",
    "al_user_created.last_name",
    "al_user_created.email",
    "ex_status",
    "ex_date_created",
    "ex_dried_weight",
    "ex_solvent_volume",
    "ex_sample_container.status",
    "ex_sample_container.container_id",
    "ex_sample_container.old_id",
    "ex_parent_container.status",
    "ex_parent_container.container_id",
    "ex_dried_weight_unit.unit_name",
    "ex_dried_weight_unit.symbol",
    "ex_solvent_volume_unit.unit_name",
    "ex_solvent_volume_unit.symbol",
    "ex_extraction_method.status",
    "ex_extraction_method.method_name",
    "ex_extraction_method.method_description",
    "ex_batch.status",
    "ex_batch.batch_id",
    "ex_batch.comments",
    "ex_batch.old_id",
    "ex_batch.short_description",
    "ex_batch.description",
    "ex_user_created.first_name",
    "ex_user_created.last_name",
    "ex_user_created.email",
    "ex_extraction_container.status",
    "ex_extraction_container.brand",
    "dsp_status",
    "dsp_date_created",
    "dsp_sample_container.status",
    "dsp_sample_container.container_id",
    "dsp_sample_container.old_id",
    "dsp_parent_container.status",
    "dsp_parent_container.container_id",
    "dsp_parent_container.old_id",
    "dsp_field_data.collector_fullname",
    "dsp_field_data.observation_subject",
    "dsp_field_data.inat_upload",
    "dsp_field_data.is_wild",
    "dsp_field_data.taxon_name",
    "dsp_field_data.sample_id",
    "dsp_field_data.collector_orcid",
    "dsp_field_data.collector_inat",
    "dsp_field_data.latitude",
    "dsp_field_data.longitude",
    "dsp_field_data.qfield_project",
    "dsp_field_data.comment_eco",
    "dsp_field_data.weather",
    "dsp_field_data.sample_name",
    "dsp_field_data.name_proposition",
    "dsp_field_data.ipen",
    "dsp_field_data.match_name",
    "dsp_field_data.comment_env",
    "dsp_field_data.herbivory_percent",
    "dsp_field_data.temperature_°C",
    "dsp_field_data.geometry.type",
    "dsp_field_data.geometry.coordinates",
    "dsp_field_data.date",
    "dsp_user_created.first_name",
    "dsp_user_created.last_name",
    "dsp_user_created.email",
    "dsp_field_data.geometry",
    "inat_id",
    "inat_status",
    "inat_date_created",
    "inat_quality_grade",
    "inat_identifications_most_agree",
    "inat_species_guess",
    "inat_created_at",
    "inat_taxon_name",
    "inat_comments",
    "inat_emi_external_id",
    "sample_type",
]
final_df = df[columns_to_keep]

final_df.drop_duplicates(subset=["ms_filename"], keep="first", inplace=True)
final_df["ms_filename"] = final_df["ms_filename"].apply(lambda x: f"{x}.mzML")
filename_tsv = "metadata.tsv"
filename_csv = "metadata.csv"
final_df.to_csv(filename_tsv, sep="\t", index=False)
final_df.to_csv(filename_csv, index=False)
