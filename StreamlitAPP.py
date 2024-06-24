import streamlit as st
from src.Invoice_extract_app import create_docs
import requests
import json
import uuid

# Function to map LLM response to the new API format
def map_llm_to_api(llm_response):
    # For generation of unique identifier anytime function is called
    num_at_card = str(uuid.uuid4())
    
    # MappingLLM output to SAP B1Input format
    api_input = {
        "DocType": "Invoice_Document",
        "DocDate": llm_response["invoiceDate"],
        "DocDueDate": llm_response["invoiceDate"],
        "CardCode": "S100263",
        "NumAtCard": num_at_card,
        "Comments": "Posting to Test API",
        "DocumentLines": []
    }
    
    for line_item in llm_response["invoiceDetails"]:
        api_line_item = {
            "ItemCode": line_item["lineNo"],
            "ItemDescription": line_item["description"],
            "Quantity": None,
            "Price": line_item["netAmount"],
            "Currency": "NGN",
            "AccountCode": "60116001"
        }
        api_input["DocumentLines"].append(api_line_item)
    
    return api_input

# Function to post the mapped data to SAP API 
def post_to_sap_api(api_input, sap_api_url, username, password):
    headers = {
  'Content-Type': 'application/json',
  'Authorization': 'J0Jhc2ljIGV5SkRiMjF3WVc1NVJFSWlPaUFpUVRJd09EZ3lYMFpTVlZSVVFWOVVNREVpTENBaVZYTmxjazVoYldVaU9pQWliV0Z1WVdkbGNpSjlPa1p5ZFhSMFlVQXlNakk9Jw=='}
    
    response = requests.post(
        sap_api_url,
        auth=(username, password),
        headers=headers,
        data=json.dumps(api_input)
    )
    
    return response

def main():

    st.set_page_config(page_title="Invoice Extraction Bot")
    st.title("Invoice Extraction Bot... ")
    
    # Upload the Invoices (pdf files)
    file = st.file_uploader("Upload invoices here, only PDF and jpeg files allowed", type=["pdf", "jpeg"],accept_multiple_files=True)
    data = create_docs(file)

    submit = st.button("Extract Data")

    if submit:
        with st.spinner('Wait for it...'):
            st.write(data)
        st.success("Augment this information with human validation")

    post_to_sap = st.button("Post to SAP")
    if post_to_sap:
        sap_api_url = st.text_input("SAP API URL", "https://htpc20882p01.cloudiax.com:50000/b1s/v2/PurchaseInvoices")
        username = st.text_input("Username", {"CompanyDB": "A20882_FRUTTA_T01", "UserName": "manager"})
        password = st.text_input("Password", "Frutta@222", type="password")


        if sap_api_url and username and password:
            for i, llm_response in enumerate(data):
                api_input = map_llm_to_api(llm_response)
                response = post_to_sap_api(api_input, sap_api_url, username, password)
                st.write(f"Response Status Code for Invoice {llm_response['invoiceNo']}: {response.status_code}")
        else:
            st.error("Please provide SAP API URL, Username, and Password")


#Invoking main function
if __name__ == '__main__':
    main()