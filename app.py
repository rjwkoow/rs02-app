import pandas as pd
import streamlit as st
import numpy as np
import warnings
from io import BytesIO
warnings.filterwarnings("ignore")

def cleaned_data(df):
    #drop the empty column
    df = df.dropna(axis=1, how='all')

    # Iterate through empty values and retain from ascending data
    df['Unnamed: 1'] = df['Unnamed: 1'].fillna(method='ffill')

    #split the unnamed:2 and keep only booking date
    df[['First', 'Second']] = df['Unnamed: 1'].str.split(':', n=1, expand=True)
    df = df.drop('First', axis=1)
    df = df.rename(columns={'Second': 'Booking date'})

    #delete the original Unnamed:2 column
    df = df.drop('Unnamed: 1', axis=1)

    #delete rows that contain 'Sub-Total'
    df = df[~df['RSVN#'].astype(str).str.contains('Sub-Total :')]

    #drop rows that contain value in only column booking date
    df = df.dropna(subset=df.columns[df.columns != 'Booking date'], how='all')
    df = df.reset_index(drop=True)

    #keep only data from the even number row in #Of\r\nRms column and set it to the new column as 'Remark'
    df['Remark'] = df.loc[df.index % 2 != 0, '#Of\r\nRms']

    #change data type of Booking date column from string to datetime
    df['Booking date'] = pd.to_datetime(df['Booking date'],dayfirst = True)

    #iterate a value from a row to the preceding row
    df['Remark'] = df['Remark'].shift(-1)

    #delete the even number rows
    df = df[::2].reset_index(drop=True)

    #set data type in Arrival and Departure columns to be datetime
    df['Arrival'] = pd.to_datetime(df['Arrival'],dayfirst = True)
    df['Departure'] = pd.to_datetime(df['Departure'],dayfirst = True)

    #calculate the stay duration from departure - arrival and create new column as LOS
    df['LOS'] = df['Departure'] - df['Arrival']
    df['LOS'] = df['LOS'].astype(str)

    #calculate the Leadtime from Arrival - booking date and create new column as Leadtime
    df['Leadtime'] = df['Arrival'] - df['Booking date']
    df['Leadtime'] = df['Leadtime'].astype(str)
   

    #rename the Unnamed: 18 as Time
    df = df.rename(columns={'Unnamed: 18': 'Time'})

    #drop the last row
    df = df.drop(df.index[-1])

    return df


def main():
    # Set the title of the app
    st.title("Atmind Group")
    st.title("RS02 cleaning data")

    # Upload the dataset and read it
    uploaded_file = st.file_uploader("Choose a CSV file", type='csv')
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='latin-1',skiprows=4)
        df = cleaned_data(df)
        st.write(df)

        # Convert DataFrame to Excel and write it to BytesIO object
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        output.seek(0)
        
        # Create download button for Excel file
        st.download_button(
            label="Download data as Excel",
            data=output,
            file_name="data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


if __name__ == "__main__":
    main()

