import streamlit as st
from src.Invoice_extract_app import create_docs
import requests
import json
import uuid

# Function to map LLM response to the new API format
def map_llm_to_api(llm_response):
    num_at_card = str(uuid.uuid4())
    
    api_input = {
        "DocType": "Invoice_Document",
        "DocDate": llm_response["invoiceDate"],
        "DocDueDate": llm_response["invoiceDate"],
        "CardCode": llm_response["supplierCode"],
        "NumAtCard": num_at_card,
        "Comments": "Comment from Test API",
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
    headers = {'Content-Type': 'application/json'}
    
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
    data = create_docs(file)

    # Upload the Invoices (pdf files)
    file = st.file_uploader("Upload invoices here, only PDF and jpeg files allowed", type=["pdf", "jpeg"],accept_multiple_files=True)

    submit = st.button("Extract Data")
    post_to_sap = st.button("Post to SAP")

    if submit:
        with st.spinner('Wait for it...'):
            st.write(data)
        st.success("Augment this information with human validation")


    for i, llm_response in enumerate(data):
        st.json(llm_response)

    if post_to_sap:
        sap_api_url = st.text_input("SAP API URL", "https://api.sap.com/example/endpoint")
        username = st.text_input("Username", "your_username")
        password = st.text_input("Password", "your_password", type="password")

        if sap_api_url and username and password:
            for llm_response in data:
                api_input = map_llm_to_api(llm_response)
                response = post_to_sap_api(api_input, sap_api_url, username, password)
                st.write(f"Response Status Code for Invoice {llm_response['invoiceNo']}: {response.status_code}")
                st.json(response.json())
        else:
            st.error("Please provide SAP API URL, Username, and Password")


#Invoking main function
if __name__ == '__main__':
    main()