import os

import pandas as pd
import requests
from dotenv import load_dotenv

# Loads .env variables
load_dotenv()

# Define variables
directus_instance = os.getenv("DIRECTUS_INSTANCE")
directus_login = f"{directus_instance}/auth/login"
directus_status = f"{directus_instance}/items/Treatment_Status/"
directus_collections = [
    "QField_Data",
    "Inat_Data",
    "Field_Samples",
    "Lab_Extracts",
    "Aliquots",
    "Mass_Spectrometry_Analysis",
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

    directus_ms = f"{directus_instance}/items/Mass_Spectrometry_Analysis/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_ms}?limit=-1")

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]
        is_converted = [item["converted"] for item in data]
        ms_id = [item["mass_spec_id"] for item in data]
        df_data = []
        for i in range(len(is_converted)):
            if is_converted[i] is False:
                directus_patch = directus_ms + ms_id[i]
                observation = {"converted": True}
                df_data.append(data[i])
                # response = session.patch(url=directus_patch, headers=headers, json=observation)

        # Convert the list of dictionaries to a DataFrame
        df_ms = pd.DataFrame(df_data)

        # Add prefix to column headers
        df = df_ms.add_prefix("ms_")

    # Retrieve aliquots informations

    directus_aliquots = f"{directus_instance}/items/Aliquots/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_aliquots}?limit=-1")

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_al = pd.DataFrame(data)

        # Add prefix to column headers
        df_al = df_al.add_prefix("al_")

        # Merge the two DataFrames
        df = df.merge(df_al, left_on="ms_aliquot_id", right_on="al_aliquot_id", how="left")

    # Retrieve extracts informations

    directus_extracts = f"{directus_instance}/items/Lab_Extracts/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_extracts}?limit=-1")

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_ex = pd.DataFrame(data)

        # Add prefix to column headers
        df_ex = df_ex.add_prefix("ex_")
        # Merge the two DataFrames
        df = df.merge(df_ex, left_on="al_lab_extract_id", right_on="ex_lab_extract_id", how="left")

    # Retrieve field samples informations

    directus_field_samples = f"{directus_instance}/items/Field_Samples/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_field_samples}?limit=-1")

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_fs = pd.DataFrame(data)

        # Add prefix to column headers
        df_fs = df_fs.add_prefix("fs_")
        # Merge the two DataFrames
        df = df.merge(df_fs, left_on="ex_field_sample_id", right_on="fs_field_sample_id", how="left")

    # Retrieve inat informations

    directus_inat = f"{directus_instance}/items/Inat_Data/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_inat}?limit=-1")
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_inat = pd.DataFrame(data)

        # Add prefix to column headers
        df_inat = df_inat.add_prefix("inat_")
        # Merge the two DataFrames
        df = df.merge(df_inat, left_on="fs_field_sample_id", right_on="inat_emi_external_id", how="left")

    # Retrieve QField informations

    directus_qf = f"{directus_instance}/items/Qfield_Data/"

    # Make a GET request to retrieve data
    response = session.get(url=f"{directus_qf}?limit=-1")
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()["data"]

        # Convert the list of dictionaries to a DataFrame
        df_qf = pd.DataFrame(data)

        # Add prefix to column headers
        df_qf = df_qf.add_prefix("qf_")
        # Merge the two DataFrames
        df = df.merge(df_qf, left_on="fs_field_sample_id", right_on="qf_field_sample_id_pk", how="left")

for _, row in df.iterrows():
    if row["ex_dried_weight"] != "":
        row["ex_dried_plant_weight"] = row["ex_dried_weight"]
    if row["ex_solvent_volume"] != "":
        row["ex_solvent_volume_micro"] = row["ex_solvent_volume"]
df["sample_type"] = ""
for index, row in df.iterrows():
    if "blk" in row["al_aliquot_id"]:
        df.at[index, "sample_type"] = "blank"
    else:
        df.at[index, "sample_type"] = "sample"

columns_to_keep = [
    "ms_mass_spec_id",
    "al_aliquot_id",
    "sample_type",
    "fs_field_sample_id",
    "inat_taxon_name",
    "ex_lab_extract_id",
    "ex_batch_id",
    "ms_user_created",
    "ms_date_created",
    "ms_UUID_mass_spec",
    "ms_injection_volume",
    "ms_injection_method",
    "ms_ms_id",
    "al_user_created",
    "al_date_created",
    "al_UUID_aliquot",
    "al_aliquot_volume_microliter",
    "ex_user_created",
    "ex_date_created",
    "ex_user_updated",
    "ex_date_updated",
    "ex_UUID_lab_extract",
    "ex_dried_plant_weight",
    "ex_extraction_method",
    "ex_solvent_volume_micro",
    "fs_user_created",
    "fs_date_created",
    "fs_UUID_field_sample",
    "qf_field_sample_name",
    "qf_latitude",
    "qf_longitude",
    "qf_ipen",
    "qf_comment_eco",
    "qf_soil_type",
    "qf_weather",
    "qf_comment_env",
    "qf_herbivory_percent",
    "qf_temperature_celsius",
    "inat_id",
    "inat_quality_grade",
    "inat_uuid",
    "inat_observed_on_details_date",
    "inat_identifications_most_agree",
    "inat_species_guess",
    "inat_identifications_most_disagree",
    "inat_site_id",
    "inat_created_time_zone",
    "inat_observed_time_zone",
    "inat_description",
    "inat_observed_on",
    "inat_updated_at",
    "inat_captive",
    "inat_taxon_is_active",
    "inat_taxon_ancestry",
    "inat_taxon_min_species_ancestry",
    "inat_taxon_endemic",
    "inat_taxon_iconic_taxon_id",
    "inat_taxon_min_species_taxon_id",
    "inat_taxon_threatened",
    "inat_taxon_rank_level",
    "inat_taxon_introduced",
    "inat_taxon_native",
    "inat_taxon_parent_id",
    "inat_taxon_rank",
    "inat_taxon_extinct",
    "inat_taxon_id",
    "inat_taxon_ancestor_ids",
    "inat_taxon_created_at",
    "inat_taxon_default_photo_id",
    "inat_taxon_default_photo_url",
    "inat_taxon_default_photo_flags",
    "inat_taxon_default_photo_square_url",
    "inat_taxon_default_photo_medium_url",
    "inat_taxon_observations_count",
    "inat_taxon_universal_search_rank",
    "inat_taxon_current_synonymous_taxon_ids",
    "inat_taxon_atlas_id",
    "inat_taxon_wikipedia_url",
    "inat_taxon_iconic_taxon_name",
    "inat_taxon_preferred_common_name",
    "inat_ident_taxon_ids",
    "inat_outlinks",
    "inat_faves_count",
    "inat_num_identification_agreements",
    "inat_comments",
    "inat_map_scale",
    "inat_uri",
    "inat_project_ids",
    "inat_community_taxon_id",
    "inat_geojson_type",
    "inat_geojson_coordinates",
    "inat_identifications_count",
    "inat_location",
    "inat_votes",
    "inat_user_id",
    "inat_user_login",
    "inat_user_name",
    "inat_user_observations_count",
    "inat_user_identifications_count",
    "inat_user_journal_posts_count",
    "inat_user_activity_count",
    "inat_user_species_count",
    "inat_user_universal_search_rank",
    "inat_user_roles",
    "inat_identifications_some_agree",
    "inat_project_ids_without_curator_id",
    "inat_place_guess",
    "inat_identifications",
    "inat_project_observations",
    "inat_photos",
    "inat_faves",
    "inat_photo_url",
    "inat_taxon_conservation_status_id",
    "inat_taxon_conservation_status_source_id",
    "inat_taxon_conservation_status_authority",
    "inat_taxon_conservation_status_iucn",
    "inat_emi_external_id",
    "inat_taxon_conservation_status_user_id",
    "inat_taxon_complete_rank",
    "inat_taxon_complete_species_count",
]
final_df = df[columns_to_keep]

column_rename = {
    "ms_mass_spec_id": "sample_filename",
    "al_aliquot_id": "sample_id",
    "fs_field_sample_id": "source_id",
    "inat_taxon_name": "source_taxon",
    "ms_user_created": "ms_operator",
    "ms_UUID_mass_spec": "ms_UUID",
    "ms_inj_volume": "ms_inj_vol",
    "ms_injection_method": "ms_inj_vol",
    "ms_ms_id": "ms_id",
    "al_UUID_aliquot": "al_UUID",
    "al_aliquot_volume_microliter": "al_vol_microliter",
    "ex_lab_extract_id": "lab_extract",
    "ex_UUID_lab_extract": "ex_UUID",
    "ex_dried_plant_weight": "ex_dried_weight",
    "ex_extraction_method": "extr_meth",
    "ex_solvent_volume_micro": "ex_solv_vol_micro",
    "fs_UUID_field_sample": "fs_UUID",
    "qf_field_sample_name": "qf_sample_name",
}
final_df = final_df.rename(columns=column_rename)
final_df.drop_duplicates(subset=["sample_filename"], keep="first", inplace=True)
filename_tsv = "metadata.tsv"
filename_csv = "metadata.csv"
final_df.to_csv(filename_tsv, sep="\t", index=False)
final_df.to_csv(filename_csv, index=False)
