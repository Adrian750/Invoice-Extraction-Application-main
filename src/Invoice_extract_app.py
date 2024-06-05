import os
import json
import re
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.utils import read_file
from pydantic import BaseModel, Field
from typing import List

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

load_dotenv()

key = os.getenv("OPENAI_API_KEY")


#Function to extract data from text
def extracted_data(invoice_data):

    # Define the structure of an invoice line item
    class InvoiceLineItem(BaseModel):
        lineNo: int = Field(description="Line number of the invoice item")
        description: str = Field(description="Extracted line item description")
        netAmount: float = Field(description="Extracted net amount for the line item")
        vatAmount: float = Field(description="Extracted VAT amount for the line item")
        grossAmount: float = Field(description="Extracted gross amount for the line item")

    # Define the structure of the invoice
    class Invoice(BaseModel):
        invoiceDate: str = Field(description="Extracted invoice date in YYYY-MM-DD format")
        invoiceNo: str = Field(description="Extracted invoice number")
        supplierCode: str = Field(description="Extracted supplier code")
        supplierName: str = Field(description="Extracted supplier name")
        serviceDescription: str = Field(description="Extracted service description")
        totalNetAmount: float = Field(description="Extracted total net amount")
        totalVatAmount: float = Field(description="Extracted total VAT amount")
        totalGrossAmount: float = Field(description="Extracted total gross amount")
        invoiceDetails: List[InvoiceLineItem] = Field(description="List of extracted line items from the invoice")    

    
    # Set up a parser
    parser = PydanticOutputParser(pydantic_object= Invoice)
    parser.get_format_instructions()

    
    template = """

    Extract the relevant invoice details and format them in the following JSON structure. Ensure accuracy and completeness for each field.

    Input:
    ```
    {invoice}
    ```

    Output format:
    ```
    {output_format}
    ```

    Ensure that the extracted data accurately matches the information in the invoice. 
    Each field should reflect the corresponding details precisely as presented in the source document.
    """

    prompt_template = PromptTemplate(input_variables=["invoice","output_format"], template=template)

    llm = ChatOpenAI(openai_api_key = key, model_name = 'gpt-3.5-turbo', temperature = 0.9)

    prompt = prompt_template.format(invoice =invoice_data, output_format = parser.get_format_instructions())

    full_response=llm.invoke(prompt)

    # try:
    #     parsed_response = InvoiceLineItem.parse_raw(full_response.content)
    #     print(parsed_response)
    # except Exception as e:
    #     print(f"Error parsing response: {e}")


    # Use regex to extract the content part
    content_match = re.search(r"AIMessage\(content='(.*?)', response_metadata=", full_response, re.DOTALL)

    if content_match:
        content_json = content_match.group(1)
        
        # Decode any escape characters if necessary
        content_json = content_json.encode().decode('unicode_escape')

        # Parse the JSON content
        content_dict = json.loads(content_json)
        
        # Pretty-print the content
        response = json.dumps(content_dict, indent=4)
        return response
    else:
        return "Content not found."
    

    


def create_docs(file_list):

    invoice_list = []
    # invoice_output = []

    for filename in file_list:
        text_extracted = read_file(filename)
        llm_extracted_data = extracted_data(text_extracted)
        invoice_list.append(llm_extracted_data)
    
    # for invoice in invoice_list:
    #     invoice = dict(invoice)
    #     df = pd.json_normalize(invoice, "invoiceDetails", [key for key in invoice.keys() if key != 'invoiceDetails'])
    #     invoice_output.append(df)

    # # Concatenate all DataFrames
    # combined_df = pd.concat(invoice_output, ignore_index=True)
    return invoice_list