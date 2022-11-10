import streamlit as st
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import datetime
from datetime import date
from datetime import datetime
import re
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
st.set_page_config(layout = 'wide')
#-----------------------------------------------------------------------------#
# Import data
def load_excel(path, sheet):

                 return pd.read_excel(path, sheet_name=sheet)



lbn_data=load_excel('Lebanon_Poverty_2022.xlsx',"Sheet1")

with open('lbn_admin0.json') as response:

    counties = json.load(response)



for feature in counties['features']:

    feature['id'] = feature['properties']['admin1Name']

counties = counties

lbn_data=lbn_data[lbn_data['Coverage']=='Urban/Built Up']

lbn_data.reset_index(drop=True, inplace=True)
#-----------------------------------------------------------------------------#
# Button html code
m = st.markdown("""

    <style>

    div.stButton > button:first-child {

        background-color: #1f6ebc;

        color: white;

        height: 2em;

        width: 16em;

        border-radius:8px;

        font-size:20px;

        font-weight: bold;

        margin:0px;

        display: block;

    }

    div.stButton > button:hover {

            background:linear-gradient(to bottom, #b2d8fe 5%, #b2d8fe 100%);

            background-color:#b2d8fe;

    }

    div.stButton > button:active {

            position:relative;

            top:3px;

    }

    </style>""", unsafe_allow_html=True)
#-----------------------------------------------------------------------------#
# Defining a function to clean the scraped prices
def clean_price(num):
    clean_num = re.sub(',', '', num)
    return clean_num
#-----------------------------------------------------------------------------#
# Defining a function to scrape
def get_price(links):
    response_n = []
    for url in urls:
        try:
            session = HTMLSession()
            response = session.get(url)
            #st.write(response.status_code)

            src = response.content
            soup = BeautifulSoup(src, 'lxml')
            response_n.append(soup)

        except requests.exceptions.RequestException as e:
            st.write(e)

    # empty lists to store scraped output
    date_scraped = [];
    prod_name = [];
    brand_name = [];
    prod_price_currency = [];
    prod_price = [];
    next_delivery_date = [];
    next_delivery_time = [];
    supermarket_name = [];
    food_category = []
    commodity = [];
    unit = []

    # Iterating over every response
    for i in response_n:
        products = i.find_all('div', class_= 'maincontent-wrapper')

        # Get date (data scraping was done)
        now = datetime.now()

        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        today = now.strftime("%m/%d/%Y")

        for product in products:
            # append date the product was scraped to the df
            date_scraped.append(today)

            # product name
            product_name = product.find('span', class_='base')
            product_name = product_name.get_text(strip=True)
            prod_name.append(product_name)

            # brand name
            brand = product.find('span', class_='prod_brand')
            brand = brand.get_text(strip=True)
            brand = re.sub('By', '', brand).strip()
            brand_name.append(brand)

            # currency
            currency = product.find('span', class_='price')
            currency = currency.get_text(strip=True)
            currency = re.sub(r"\d","",currency)
            currency = re.sub(r",","",currency).strip()
            prod_price_currency.append(currency)

            # price
            price = product.find('span', class_='price')
            price = price.get_text(strip=True)
            price = re.sub('LBP', '', price).strip()
            prod_price.append(price)

            # next delivery date
            try:
                next_delivery_d = product.find('strong', class_='delivery-slot-available')
                next_delivery_d = next_delivery_d.get_text(strip=True)
                next_delivery_d = re.sub('Next Available Delivery Time Slot', "", next_delivery_d)
                next_delivery_d = re.sub(r"(.*)\|(.*)", r"\1", next_delivery_d).strip()
                next_delivery_date.append(next_delivery_d)
            except:
                next_delivery_d = 'Out of stock'
                next_delivery_date.append(next_delivery_d)

            # next delivery time
            try:
                next_delivery_t = product.find('strong', class_='delivery-slot-available')
                next_delivery_t = next_delivery_t.get_text(strip = True)
                next_delivery_t = re.sub('Next Available Delivery Time Slot', "", next_delivery_t)
                next_delivery_t = re.sub(r"(.*)\|(.*)", r"\2", next_delivery_t).strip()
                next_delivery_time.append(next_delivery_t)
            except:
                next_delivery_t = 'Out of stock'
                next_delivery_time.append(next_delivery_t)

            # supermarket name
            market = 'Spinneys'
            supermarket_name.append(market)

            # unit
            scale = product.find('span', class_='prod_weight')
            scale = scale.get_text(strip = True)
            unit.append(scale)

#             # food category
#             food = 'milk and dairy'
#             food_category.append(food)

#             # item
#             food_item_name = 'Powder milk'
#             commodity.append(food_item_name)

    # creating a df from the lists
    df = pd.DataFrame({'date' : date_scraped, 'product_name' : prod_name, 'unit': unit,
                       #'category' : food_category, #'commodity' : commodity,
                       'currency' : prod_price_currency, 'price' : prod_price,
                       'delivery_date' : next_delivery_date, 'delivery_time' : next_delivery_time,
                       'supermarket' : supermarket_name})
    #st.write('success')
    #st.write(df)

    return df
#-----------------------------------------------------------------------------#
# title
col1, col2, col3 = st.columns([2,5,2])
with col2:
    st.image('spoonful.png')
# col1, col2, col3 = st.columns([1,5,2])
# with col1:
#     st.image('hackathon.jpeg', use_column_width=None)
# with col2:
#     #st.title('Food Assistance Optimizer')
#     st.markdown(f"""
#             <h1>
#                 <h1 style="vertical-align:center;font-size:55px;padding-left:150px;color:#1f6ebc;padding-top:5px;margin-left:0em";>
#                 Food Basket Optimizer
#             </h1>""",unsafe_allow_html = True)
# with col3:
#     st.image('wfp.png')
#-----------------------------------------------------------------------------#
col1, col2, col3 = st.columns([1,1,2])

with col1:
    # Select a country
    option = st.selectbox('Select a country', ('Lebanon', 'Other'))

with col2:
    # Select a region
    option_region = st.selectbox('Select a region', lbn_data['Lebanon_Region'].unique().tolist())

with col3:
    # Determine the number of boxes needed (by geographic region)
    st.markdown(f'<p style="background-color:#FFFFFF;font-family:Arial;text-align:center; color:#FFFFFF;font-size:10px;border-radius:0%;">The number of vulnerable households: '+ str(round(((lbn_data['Total_Area'][lbn_data['Lebanon_Region']==option_region].item())*(lbn_data['Population_Density'][lbn_data['Lebanon_Region']==option_region].item())/10000)/4)) + '</p>', unsafe_allow_html=True)

    st.markdown(f'<p style="background-color:#edfcff;font-family:Arial;text-align:center; color:#1f6ebc;font-size:20px;border-radius:0%;">The number of vulnerable households: '+ str(round(((lbn_data['Total_Area'][lbn_data['Lebanon_Region']==option_region].item())*(lbn_data['Population_Density'][lbn_data['Lebanon_Region']==option_region].item())/10000)/4)) + '</p>', unsafe_allow_html=True)
#-----------------------------------------------------------------------------#
# Determine the number of boxes needed (by geographic region)
# st.markdown(f'<p style="background-color:#edfcff;font-family:Arial;text-align:center; color:#1f6ebc;font-size:30px;border-radius:0%;">The number of vulnerable households: '+ str(round(((lbn_data['Total_Area'][lbn_data['Lebanon_Region']==option_region].item())*(lbn_data['Population_Density'][lbn_data['Lebanon_Region']==option_region].item())/10000)/4)) + '</p>', unsafe_allow_html=True)
#-----------------------------------------------------------------------------#

# Empty list to store url of each category
urls = []

# Select brand for each category
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    with st.expander("Powder Milk 🥛"):
        milk_choice = st.radio("Select a brand:", ('Dano', 'Regilait', 'Nido', 'None of these brands'), index = 3
        )
        if milk_choice == 'Dano':
            urls.append('https://www.spinneyslebanon.com/powder-milk-147016-v001.html')
        elif milk_choice == 'Regilait':
            urls.append('https://www.spinneyslebanon.com/regilait-instant-low-fat-milk-powder-14-fat-800g.html')
        elif milk_choice == 'Nido':
            urls.append('https://www.spinneyslebanon.com/sachet-powder-milk-188911-v001.html')
        else:
            pass
with col2:
    with st.expander("Pasta 🍝"):
        pasta_choice = st.radio("Select a brand:", ('Panzani', 'Barilla', 'Pezzullo', 'None of these brands'), index = 3
        )
        if pasta_choice == 'Panzani':
            urls.append('https://www.spinneyslebanon.com/panzani-spaghetti-pasta-500g.html')
        elif pasta_choice == 'Barilla':
            urls.append('https://www.spinneyslebanon.com/barilla-spaghetti-n-7-500g-137383-v001.html')
        elif pasta_choice == 'Pezzullo':
            urls.append('https://www.spinneyslebanon.com/spaghetti-pasta-sp-pr-555438-v002.html')
        else:
            pass

with col3:
    with st.expander("Tuna 🐟"):
        tuna_choice = st.radio("Select a brand:", ('Siblou', 'Plein Soleil', 'Spinneys', 'None of these brands'), index = 3
        )
        if tuna_choice == 'Siblou':
            urls.append('https://www.spinneyslebanon.com/siblou-white-tuna-in-water-185g.html')
        elif tuna_choice == 'Plein Sloeil':
            urls.append('https://www.spinneyslebanon.com/plein-soleil-white-tuna-in-vegetable-oil-canned-185g.html')
        elif tuna_choice == 'Spinneys':
            urls.append('https://www.spinneyslebanon.com/white-meat-tuna-in-veg-oil.html')
        else:
            pass
with col4:
    with st.expander("Cheese 🧀"):
        cheese_choice = st.radio("Select a brand:", ('Picon', 'Bella', 'Bihar', 'None of these brands'), index = 3
        )
        if cheese_choice == 'Picon':
            urls.append('https://www.spinneyslebanon.com/picon-cheese-portions-120g.html')
        elif cheese_choice == 'Bella':
            urls.append('https://www.spinneyslebanon.com/cheese-spread-triangles.html')
        elif cheese_choice == 'Bihar':
            urls.append('https://www.spinneyslebanon.com/triangles-cheese.html')
        else:
            pass
with col5:
    with st.expander("Sunflower Oil 🌻"):
        oil_choice = st.radio("Select a brand:", ('Spinneys', 'Plein Soleil', 'Mazola', 'None of these brands'), index = 3
        )
        if oil_choice == 'Spinneys':
            urls.append('https://www.spinneyslebanon.com/spinneys-sunflower-oil-1-7l.html')
        elif oil_choice == 'Plein Soleil':
            urls.append('https://www.spinneyslebanon.com/sunflower-oil-362165-v001.html')
        elif oil_choice == 'Mazola':
            urls.append('https://www.spinneyslebanon.com/sunflower-oil-541287-v001.html')
        else:
            pass

# URL & Budget
col1, col2, col3 = st.columns([1,1,2])

with col1:
    # Input budget
    budget = st.text_input('Total funds allocated in USD')

    basket0 = st.button('Your Selected Mix')

    if "basket0" not in st.session_state:

        st.session_state.basket0=False

    if basket0 or st.session_state.basket0:

        st.session_state.basket0=True
        try:
    # if st.button('Calculate basket price'):
        #st.write('Please wait ⏳')

          df = get_price(urls)

          # cleaning the prices
          df['price_clean'] = df['price'].apply(lambda x:clean_price(x))

          # changing data type to float
          df['price_clean'] = df['price_clean'].astype('float')

          # extracting cleaned prices to list
          col_list = df.price_clean.values.tolist()

          # summing the prices to get the total price of the food basket
          final_price_lbp = round(sum(col_list))
          final_price_usd = round(final_price_lbp/30300, 2)
          #st.write(round(final_price))
          #st.write('Total basket price in USD: ', final_price_usd)

          ### Output ###
          st.markdown(f'<p style="text-align:center; color:#0d0d0c;font-family:Arial;font-size:18px;border-radius:0%;">Your Selected Subsidy Food Basket Price (USD):</p>', unsafe_allow_html=True)



          st.markdown(f'<p style="text-align:center; color:#0d0d0c;font-family:Arial Black;font-size:18px;border-radius:0%;">'+ str(final_price_usd) + '</p>', unsafe_allow_html=True)



          st.markdown(f'<p style="text-align:center; color:#0d0d0c;font-family:Arial;font-size:18px;border-radius:0%;">Number of Households Served:</p>', unsafe_allow_html=True)



          st.markdown(f'<p style="text-align:center; color:#8F00FF;font-family:Arial Black;font-size:25px;border-radius:0%;">'+ str(round(int(budget)/final_price_usd)) + '</p>', unsafe_allow_html=True)
        except:
          st.write('Please select basket choices.')
with col2:
    # Input supplier URL
    supplier = st.text_input('Supplier URL', value = 'www.spinneyslebanon.com')

    optimized_prices = []
    basket1 = st.button("Spoonful's Recommendation")
    if "basket1" not in st.session_state:
        st.session_state.basket1=False
    if basket1 or st.session_state.basket1:
        st.session_state.basket1=True

        # st.header('Optimized food item brands:')
        if milk_choice != 'None of these brands':
            urls = ['https://www.spinneyslebanon.com/powder-milk-147016-v001.html',
            'https://www.spinneyslebanon.com/regilait-instant-low-fat-milk-powder-14-fat-800g.html',
            'https://www.spinneyslebanon.com/sachet-powder-milk-188911-v001.html'
            ]

            # scrape urls
            df_milk = get_price(urls)

            # clean price column
            df_milk['price_clean'] = df_milk['price'].apply(lambda x:clean_price(x))

            # convert price_clean column to float
            df_milk['price_clean'] = df_milk['price_clean'].astype('float')

            # extract price_clean column to list (to compare prices)
            col_list = df_milk.price_clean.values.tolist()

            # # display the product name with the minimum price
            # optimal_milk = df_milk[df_milk['price_clean'] == df_milk['price_clean'].min()].iloc[0,1]
            # #st.write(df_milk[df_milk['price_clean'] == df_milk['price_clean'].min()].iloc[0,1])
            # if optimal_milk == 'SACHET POWDER MILK':
            #     st.write('Best milk brand: Nido')
            # elif optimal_milk == 'Dano Powder Milk':
            #     st.write('Best milk brand: Dano')
            # elif optimal_milk == 'Regilait Instant Low Fat Milk Powder 14% Fat 800G':
            #     st.write('Best milk brand: Regilait')

            # appending optimized price to optimized_prices list
            optimized_prices.append(df_milk[df_milk['price_clean'] == df_milk['price_clean'].min()].iloc[0,8])

        else:
            pass

        if pasta_choice != 'None of these brands':
            urls = ['https://www.spinneyslebanon.com/panzani-spaghetti-pasta-500g.html',
            'https://www.spinneyslebanon.com/barilla-spaghetti-n-7-500g-137383-v001.html',
            'https://www.spinneyslebanon.com/spaghetti-pasta-sp-pr-555438-v002.html'
            ]

            # scrape urls
            df_pasta = get_price(urls)

            # clean price column
            df_pasta['price_clean'] = df_pasta['price'].apply(lambda x:clean_price(x))

            # convert price_clean column to float
            df_pasta['price_clean'] = df_pasta['price_clean'].astype('float')

            # extract price_clean column to list (to compare prices)
            col_list = df_pasta.price_clean.values.tolist()

            # # display the product name with the minimum price
            # optimal_pasta = df_pasta[df_pasta['price_clean'] == df_pasta['price_clean'].min()].iloc[0,1]
            # if optimal_pasta == 'SPAGHETTI PASTA SP.PR':
            #     st.write('Best pasta brand: Pezzullo')
            # elif optimal_pasta == 'Barilla Spaghetti n.7 500G':
            #     st.write('Best pasta brand: Barilla')
            # elif optimal_pasta == 'Panzani Spaghetti Pasta 500G':
            #     st.write('Best pasta brand: Panzani')

            # appending optimized price to optimized_prices list
            optimized_prices.append(df_pasta[df_pasta['price_clean'] == df_pasta['price_clean'].min()].iloc[0,8])

        else:
            pass

        if tuna_choice != 'None of these brands':
            urls = ['https://www.spinneyslebanon.com/siblou-white-tuna-in-water-185g.html',
            'https://www.spinneyslebanon.com/plein-soleil-white-tuna-in-vegetable-oil-canned-185g.html',
            'https://www.spinneyslebanon.com/white-meat-tuna-in-veg-oil.html'
            ]

            # scrape urls
            df_tuna = get_price(urls)

            # clean price column
            df_tuna['price_clean'] = df_tuna['price'].apply(lambda x:clean_price(x))

            # convert price_clean column to float
            df_tuna['price_clean'] = df_tuna['price_clean'].astype('float')

            # extract price_clean column to list (to compare prices)
            col_list = df_tuna.price_clean.values.tolist()

            # # display the product name with the minimum price
            # optimal_tuna = df_tuna[df_tuna['price_clean'] == df_tuna['price_clean'].min()].iloc[0,1]
            # if optimal_tuna == 'Siblou White Tuna In Water - 185G':
            #     st.write('Best tuna brand: Siblou')
            # elif optimal_tuna == 'Plein Soleil White Tuna In Vegetable Oil Canned 185G':
            #     st.write('Best tuna brand: Plein Soleil')
            # elif optimal_tuna == 'Spinneys White Meat Tuna In Vegetable Oil':
            #     st.write('Best tuna brand: Spinneys')

            # appending optimized price to optimized_prices list
            optimized_prices.append(df_tuna[df_tuna['price_clean'] == df_tuna['price_clean'].min()].iloc[0,8])

        else:
            pass

        if cheese_choice != 'None of these brands':
            urls = ['https://www.spinneyslebanon.com/picon-cheese-portions-120g.html',
            'https://www.spinneyslebanon.com/cheese-spread-triangles.html',
            'https://www.spinneyslebanon.com/triangles-cheese.html'
            ]

            # scrape urls
            df_cheese = get_price(urls)

            # clean price column
            df_cheese['price_clean'] = df_cheese['price'].apply(lambda x:clean_price(x))

            # convert price_clean column to float
            df_cheese['price_clean'] = df_cheese['price_clean'].astype('float')

            # extract price_clean column to list (to compare prices)
            col_list = df_cheese.price_clean.values.tolist()

            # # display the product name with the minimum price
            # optimal_cheese = df_cheese[df_cheese['price_clean'] == df_cheese['price_clean'].min()].iloc[0,1]
            # if optimal_cheese == 'Picon Cheese Portions 120G':
            #     st.write('Best cheese brand: Picon')
            # elif optimal_cheese == 'CHEESE SPREAD TRIANGLES':
            #     st.write('Best cheese brand: Bella')
            # elif optimal_cheese == 'TRIANGLES CHEESE':
            #     st.write('Best cheese brand: Bihar')

            # appending optimized price to optimized_prices list
            optimized_prices.append(df_cheese[df_cheese['price_clean'] == df_cheese['price_clean'].min()].iloc[0,8])

        else:
            pass

        if oil_choice != 'None of these brands':
            urls = ['https://www.spinneyslebanon.com/spinneys-sunflower-oil-1-7l.html',
            'https://www.spinneyslebanon.com/sunflower-oil-362165-v001.html',
            'https://www.spinneyslebanon.com/sunflower-oil-541287-v001.html'
            ]

            # scrape urls
            df_oil = get_price(urls)

            # clean price column
            df_oil['price_clean'] = df_oil['price'].apply(lambda x:clean_price(x))

            # convert price_clean column to float
            df_oil['price_clean'] = df_oil['price_clean'].astype('float')

            # extract price_clean column to list (to compare prices)
            col_list = df_oil.price_clean.values.tolist()

            # # display the product name with the minimum price
            # optimal_oil = df_oil[df_oil['price_clean'] == df_oil['price_clean'].min()].iloc[0,1]
            # if optimal_oil == 'Spinneys Sunflower Oil 1.7L':
            #     st.write('Best sunflower oil brand: Spinneys')
            # elif optimal_oil == 'Plein Soleil Sunflower Oil 1.8L':
            #     st.write('Best sunflower oil brand: Plein Soleil')
            # elif optimal_oil == 'Mazola Sunflower Oil 1.5L':
            #     st.write('Best sunflower oil brand: Mazola')

            # appending optimized price to optimized_prices list
            optimized_prices.append(df_oil[df_oil['price_clean'] == df_oil['price_clean'].min()].iloc[0,8])

        else:
            pass
        # calculating the optimized price of the basket
        optimized_price_of_basket = sum(optimized_prices)
        optimized_price_of_basket = optimized_price_of_basket/30300
        optimized_price_of_basket = round(optimized_price_of_basket,2)
        #st.write('Total basket price in USD: ', optimized_price_of_basket)

        # difference (amount saved)
        # diff = final_price_usd - optimized_price_of_basket
        # diff = round(diff, 2)
        # st.write('Amount saved: $', diff)


        ### OUTPUT ###
        st.markdown(f'<p style="text-align:center; color:#0d0d0c;font-family:Arial;font-size:18px;border-radius:0%;">Spoonful Subsidy Food Basket Price (USD):</p>', unsafe_allow_html=True)



        st.markdown(f'<p style="text-align:center; color:#0d0d0c;font-family:Arial Black;font-size:18px;border-radius:0%;">'+ str(optimized_price_of_basket) + '</p>', unsafe_allow_html=True)



        st.markdown(f'<p style="text-align:center; color:#0d0d0c;font-family:Arial;font-size:18px;border-radius:0%;">Number of Households Served:</p>', unsafe_allow_html=True)



        st.markdown(f'<p style="text-align:center; color:#8F00FF;font-family:Arial Black;font-size:25px;border-radius:0%;">'+ str(round(int(budget)/optimized_price_of_basket)) + '</p>', unsafe_allow_html=True)

        with st.expander("Explore the optimized brands"):
            # display the brand names of the cheapest commodities

            # MILK
            # display the product name with the minimum price
            if milk_choice != 'None of these brands':
                optimal_milk = df_milk[df_milk['price_clean'] == df_milk['price_clean'].min()].iloc[0,1]
                #st.write(df_milk[df_milk['price_clean'] == df_milk['price_clean'].min()].iloc[0,1])
                if optimal_milk == 'SACHET POWDER MILK':
                    st.write('Best milk brand: Nido')
                elif optimal_milk == 'Dano Powder Milk':
                    st.write('Best milk brand: Dano')
                elif optimal_milk == 'Regilait Instant Low Fat Milk Powder 14% Fat 800G':
                    st.write('Best milk brand: Regilait')

            # PASTA
            # display the product name with the minimum price
            if pasta_choice != 'None of these brands':
                optimal_pasta = df_pasta[df_pasta['price_clean'] == df_pasta['price_clean'].min()].iloc[0,1]
                if optimal_pasta == 'SPAGHETTI PASTA SP.PR':
                    st.write('Best pasta brand: Pezzullo')
                elif optimal_pasta == 'Barilla Spaghetti n.7 500G':
                    st.write('Best pasta brand: Barilla')
                elif optimal_pasta == 'Panzani Spaghetti Pasta 500G':
                    st.write('Best pasta brand: Panzani')

            # TUNA
            # display the product name with the minimum price
            #df_tuna[df_tuna['price_clean'] == df_tuna['price_clean'].min()].iloc[0,1]
            if tuna_choice != 'None of these brands':
                optimal_tuna = df_tuna[df_tuna['price_clean'] == df_tuna['price_clean'].min()].iloc[0,1]
                if optimal_tuna == 'Siblou White Tuna In Water - 185G':
                    st.write('Best tuna brand: Siblou')
                elif optimal_tuna == 'Plein Soleil White Tuna In Vegetable Oil Canned 185G':
                    st.write('Best tuna brand: Plein Soleil')
                elif optimal_tuna == 'Spinneys White Meat Tuna In Vegetable Oil':
                    st.write('Best tuna brand: Spinneys')

            # CHEESE
            # display the product name with the minimum price
            if cheese_choice != 'None of these brands':
                optimal_cheese = df_cheese[df_cheese['price_clean'] == df_cheese['price_clean'].min()].iloc[0,1]
                if optimal_cheese == 'Picon Cheese Portions 120G':
                    st.write('Best cheese brand: Picon')
                elif optimal_cheese == 'CHEESE SPREAD TRIANGLES':
                    st.write('Best cheese brand: Bella')
                elif optimal_cheese == 'TRIANGLES CHEESE':
                    st.write('Best cheese brand: Bihar')

            # SUNFLOWER OIL
            # display the product name with the minimum price
            if oil_choice != 'None of these brands':
                optimal_oil = df_oil[df_oil['price_clean'] == df_oil['price_clean'].min()].iloc[0,1]
                if optimal_oil == 'Spinneys Sunflower Oil 1.7L':
                    st.write('Best sunflower oil brand: Spinneys')
                elif optimal_oil == 'Plein Soleil Sunflower Oil 1.8L':
                    st.write('Best sunflower oil brand: Plein Soleil')
                elif optimal_oil == 'Mazola Sunflower Oil 1.5L':
                    st.write('Best sunflower oil brand: Mazola')

#-----------------------------------------------------------------------------#
fig = px.choropleth(lbn_data, geojson=counties, locations='Lebanon_Region', color='predictions',

                           color_continuous_scale="bluered",

                    basemap_visible=False,

                    hover_data=["Lebanon_Region","predictions"],

                           labels={'predictions':'Poverty', 'Lebanon_Region':'Lebanese District'}

                          )

fig.update_geos(fitbounds="geojson")
fig.update_layout(showlegend=False,coloraxis_showscale=False)



fig.add_scattergeo(

  geojson=counties,

  locations = lbn_data['Lebanon_Region'],

  text = round(lbn_data['predictions'],2),

    textfont=dict(

        family="arial black",

        size=10,

        color="Grey"

    ),

  mode = 'text'

)
#-----------------------------------------------------------------------------#
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

with col3:

    fig.update_layout (title_text = 'Lebanese Districts Poverty Predictions in 2020 <br> by Deploying Satellite Imagery Data on Random Forest Regressor', title_x = 0.5,plot_bgcolor='Light Grey', showlegend=False,

                                                title_font_family="Arial",title_font_size=18)

    st.plotly_chart(fig)
