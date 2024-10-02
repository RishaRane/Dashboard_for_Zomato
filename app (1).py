
import os
import pandas as pd
import plotly.express as px
import streamlit as st

import warnings
warnings.filterwarnings('ignore')

#configuration
st.set_page_config(page_title = 'Zomato Dashboard', layout = 'wide')

# Set page title
st.title('Dashboard For Zomato Restaurants:bar_chart:')

#moving page title upwards and in center
st.markdown(
    '''<style>
            div.block-container{
              padding-top:2rem;
              text-align:center;
            }
       </style>
    ''', 
    unsafe_allow_html = True)

os.chdir(r'/content')
df = pd.read_csv('zomato.csv')

# 3.1 Sidebar for Restaurant Name
st.sidebar.header('Filters')
res_name = st.sidebar.multiselect('Restaurant Name', df['name'].unique())

if not res_name:
  df1 = df.copy()
else:
  df1 = df[df['name'].isin(res_name)]

# 3.2 Sidebar for restaurant type
res_type = st.sidebar.multiselect('Restaurant Type', df1['rest_type'].unique())

if not res_type:
  df2 = df1.copy()
else:
  df2 = df1[df1['rest_type'].isin(res_type)]

# 3.3 Sidebar for City
city = st.sidebar.multiselect('City', df2['listed_in(city)'].unique())

if not city:
  df3 = df2.copy()
else:
  df3 = df2[df2['listed_in(city)'].isin(city)]

if not res_name and not res_type and not city:
  filters_df = df
elif not res_type and not city:
  filters_df = df1[df1['name'].isin(res_name)]
elif not res_name and not city:
  filters_df = df2[df2['rest_type'].isin(res_type)]
elif not res_name and not res_type:
  filters_df = df3[df3['listed_in(city)'].isin(city)]
elif res_name and res_type:
  filters_df = df3[df1['name'].isin(res_name) & df2['rest_type'].isin(res_type)]
elif res_name and city:
  filters_df = df3[df1['name'].isin(res_name) & df3['listed_in(city)'].isin(city)]
elif res_type and city:
  filters_df = df3[df2['rest_type'].isin(res_type) & df3['listed_in(city)'].isin(city)]
else:
  filters_df = df3[df1['name'].isin(res_name) & df2['rest_type'].isin(res_type) & df3['listed_in(city)'].isin(city)]

block1, block2 = st.columns((2))

filters_df['approx_cost(for two people)'] = pd.to_numeric(filters_df['approx_cost(for two people)'].str.replace(',', ''), errors='coerce')

# 1. Restaurant Type Wise Costs
cost_df = filters_df.groupby(by = 'rest_type', as_index = False)['approx_cost(for two people)'].mean()

with block1:
  st.subheader(' :moneybag: Restaurant Type Wise Cost')
  fig1 = px.bar(cost_df, 
                x = 'rest_type', 
                y = 'approx_cost(for two people)', 
                template = 'seaborn')
  st.plotly_chart(fig1, use_container_width = True)

# 2. City Wise Costs
cost_df = filters_df.groupby(by = 'listed_in(city)', as_index = False)['approx_cost(for two people)'].mean()

with block2:
  st.subheader(' :moneybag: City Wise Costs')
  fig1 = px.pie(cost_df, 
                values = 'approx_cost(for two people)', 
                names = 'listed_in(city)', 
                hole = 0.5)
  st.plotly_chart(fig1, use_container_width = True)

st.subheader('Cost Vs Ratings')

fig3 = px.scatter(filters_df,
                  x='approx_cost(for two people)',
                  y='rate',
                  height=500,
                  width=1000,
                  template='gridon',
                  color='rate')

st.plotly_chart(fig3, use_container_width=True)

st.subheader('Data For Restaurants:page_with_curl:')
with st.expander("Restaurant Summary"):
  st.markdown('Restaurant Data')
  cols = (filters_df[['name', 'online_order', 'book_table', 'phone', 'address']]).astype('str')
  res_summary = pd.pivot_table(data = cols, 
                               index = ['name'],
                               aggfunc=lambda x: ' '.join(x.unique()) if x.notnull().any() else '')
  st.write(res_summary.style.background_gradient(cmap = 'Blues'))

block1, block2 = st.columns((2))

# filters_df['votes'] = pd.to_numeric(filters_df['votes'].str.replace(',', ''), errors='coerce')

# 1. Restaurant Type Wise Votes
cost_df = filters_df.groupby(by = 'rest_type', as_index = False)['votes'].mean()

with block1:
  st.subheader('Restaurant Type Wise Votes')
  fig1 = px.bar(cost_df, 
                x = 'rest_type', 
                y = 'votes', 
                template = 'seaborn', 
                color_discrete_sequence=['#9ACD32'])
  st.plotly_chart(fig1, use_container_width = True)

# 2. City Wise Votes
cost_df = filters_df.groupby(by = 'listed_in(city)', as_index = False)['votes'].mean()

with block2:
  st.subheader('City Wise Votes')
  fig2 = px.pie(cost_df, 
                values = 'votes',
                names = 'listed_in(city)',
                hole = 0.5)
  st.plotly_chart(fig2, use_container_width = True)
st.subheader('Hierarchical View Restaurant Costs :arrow_down:')

data = filters_df.dropna(subset=['listed_in(city)', 'rest_type', 'listed_in(type)'])

mean_cost_df = data.groupby(['listed_in(city)', 'rest_type', 'listed_in(type)'], as_index=False)['approx_cost(for two people)'].mean()

fig4 = px.treemap(mean_cost_df, 
                  path = ['listed_in(city)', 'rest_type', 'listed_in(type)'], 
                  values = 'approx_cost(for two people)',
                  hover_data  = ['approx_cost(for two people)'],
                  color = 'rest_type')
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig4, use_container_width = True)
