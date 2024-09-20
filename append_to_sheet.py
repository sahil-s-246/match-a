import gspread
import os
import gspread.exceptions
import streamlit as st

# The keys you wish to retrieve from the .env file
keys = [
    "type",
    "project_id",
    "private_key_id",
    "private_key",
    "client_email",
    "client_id",
    "auth_uri",
    "token_uri",
    "auth_provider_x509_cert_url",
    "client_x509_cert_url",
    "universe_domain"
]
cred = {key: st.secrets[key].replace('\\n', '\n') for key in keys}
gc = gspread.service_account_from_dict(cred)


def append_to_sheet(val):
    sheet = gc.open_by_key(os.getenv("s_url")).sheet1
    sheet.append_row(val)

