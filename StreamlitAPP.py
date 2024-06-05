import streamlit as st
from src.Invoice_extract_app import create_docs


def main():

    st.set_page_config(page_title="Invoice Extraction Bot")
    st.title("Invoice Extraction Bot... ")


    # Upload the Invoices (pdf files)
    file = st.file_uploader("Upload invoices here, only PDF and jpeg files allowed", type=["pdf", "jpeg"],accept_multiple_files=True)

    submit=st.button("Extract Data")

    if submit:
        with st.spinner('Wait for it...'):
            data = create_docs(file)
            st.write(data)
            df=create_docs(file)
            # st.write(df.head())

            # data_as_csv= df.to_csv(index=False).encode("utf-8")
            # st.download_button(
            #     "Download data as CSV", 
            #     data_as_csv, 
            #     "benchmark-tools.csv",
            #     "text/csv",
            #     key="download-tools-csv")
        st.success("Augment this information with human validation")


#Invoking main function
if __name__ == '__main__':
    main()