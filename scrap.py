import streamlit as st
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
import time

def scrape_data(parcel_numbers, selected_fields, selected_domains):
    rows = []
    total_requests = len(parcel_numbers)
    start_time = time.time()

    for selected_domain in selected_domains:
        for idx, txroll_cadaccountnumber in enumerate(parcel_numbers, start=1):
            url = f'https://esearch.{selected_domain}/Property/View/{txroll_cadaccountnumber}?year=2023'
            r = requests.get(url)
            try:
                soup = BeautifulSoup(r.content, 'html.parser')
                # soup = soup.find_all('div', class_='panel panel-primary')[2].find_all('tr')


                # Initialize all fields to empty strings
                scraped_data = {
                    'Geographic_ID':'',
                    'Property_ID': '',
                    'Type': '',
                    'Situs_Address': '',
                    'Land_Non_Homesite_Value': '',
                }
                if 'Geographic_ID' in selected_fields:
                    Geographic_ID = re.findall(
                        r'Geographic ID: <\/strong>[^<>]*', str(soup))
                    Geographic_ID = ' '.join(Geographic_ID)
                    Geographic_ID = re.sub('\s+', ' ', Geographic_ID)
                    Geographic_ID = Geographic_ID.split('Geographic ID:')[1].replace('</strong>', '').strip()
                    scraped_data['Geographic_ID'] = Geographic_ID

                if 'Property_ID' in selected_fields:
                    Property_ID = re.findall(
                        r'Property ID:<\/th>\s+<td class="tbltrwidth">[^<>]*', str(soup))
                    Property_ID = ' '.join(Property_ID)
                    Property_ID = re.sub('\s+', ' ', Property_ID)
                    Property_ID = Property_ID.split('Property ID:')[1].replace('</th> <td class="tbltrwidth">','').strip()
                    scraped_data['Property_ID'] = Property_ID
                if 'Type' in selected_fields:
                    Type = re.findall(
                        r'Type:<\/th>\s+<td>[^<>]*', str(soup))
                    Type = ' '.join(Type)
                    Type = re.sub('\s+', ' ', Type)
                    Type = Type.split('Type:')[1].replace('</th> <td>', '').strip()
                    scraped_data['Type'] = Type

                if 'Situs_Address' in selected_fields:
                    Situs_Address = re.findall(
                        r'Situs Address:<\/th><td colspan="3">[\!\@\#\$\%\^\&\*\(\)\-\w\s\,\.\/\;\:\"\']+', str(soup))
                    Situs_Address = ' '.join(Situs_Address)
                    Situs_Address = re.sub('\s+', ' ', Situs_Address)
                    Situs_Address = Situs_Address.split('Situs Address:')[1].replace('</th><td colspan="3">', '').strip()
                    scraped_data['Situs_Address'] = Situs_Address


                row_dict = {'domain': selected_domain, 'parcel_number': txroll_cadaccountnumber, **scraped_data}
                rows.append(row_dict)

                # Display estimated time remaining
                elapsed_time = time.time() - start_time
                avg_time_per_request = elapsed_time / idx if idx > 0 else 0
                remaining_requests = total_requests - idx
                estimated_time_remaining = avg_time_per_request * remaining_requests

                st.markdown(f"<p style='color: green;'>Estimated time remaining: {round(estimated_time_remaining, 2)} seconds  {idx} completed</p>",
                            unsafe_allow_html=True)

            except Exception as e:
                st.warning(f"Failed to fetch data for parcel number {txroll_cadaccountnumber} on domain {selected_domain}: {str(e)}")
                # Set all selected fields to empty strings
                scraped_data = {field: '' for field in selected_fields}

            # Append the row_dict to the rows list

    result_df = pd.DataFrame(rows)
    return result_df

def main():


    st.title('Esearch Site Property Scraper')
    st.write("Upload an Excel file containing 'parcel_number' column.")

    uploaded_file = st.file_uploader("Upload Excel file", type=['xlsx', 'xls'])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            parcel_numbers = df['parcel_number'].tolist()

            # Define available fields for selection
            available_fields = ['Select All','Geographic_ID','Property_ID','Type','Situs_Address']  # Add more fields here

            # Checkbox options for selecting fields
            selected_fields = st.multiselect('Select Fields for Output', available_fields)

            # Define available domains for selection
            list2 = ['dallamcad.org','delta-cad.org','fallscad.net','galvestoncad.org','bastropcad.org']
            selected_domains = st.multiselect('Select Domains', list2)

            # Check if 'Select All' is chosen and update selected_fields accordingly
            if 'Select All' in selected_fields:
                selected_fields = available_fields[1:]  # Exclude the 'Select All' option

            if st.button('Scrape Data'):
                scraped_data = scrape_data(parcel_numbers, selected_fields, selected_domains)
                st.write(scraped_data)

                # Download the output file
                csv = scraped_data.to_csv(index=False)
                st.download_button(label="Download Output", data=csv, file_name='grafton_scraped_data.csv',
                                   mime='text/csv')

        except Exception as e:
            st.warning(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
