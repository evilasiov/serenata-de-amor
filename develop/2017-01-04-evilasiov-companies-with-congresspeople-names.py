
# coding: utf-8

# # Look for companies with congresspeople names
# 
# Sometimes the trade company name is the owner's name, specially when it has just a single parter. Searching for these companies (possibly filtering by legal_entity equals to 213-5 - EMPRESARIO (INDIVIDUAL)) may bring good results.

# In[1]:

from serenata_toolbox.datasets import fetch

fetch('2016-12-06-reimbursements.xz', '../data')
fetch('2016-09-03-companies.xz', '../data')
fetch('2016-12-21-deputies.xz', '../data')


# In[2]:

import numpy as np
import pandas as pd

data = pd.read_csv('../data/2016-12-06-reimbursements.xz',
                   dtype={'cnpj_cpf': np.str},
                   low_memory=False)


# In[3]:

data['supplier'].unique()


# In[4]:

data['congressperson_name'].unique()


# In[5]:

deputies = pd.read_csv('../data/2016-12-21-deputies.xz',
                       usecols=['congressperson_id', 'civil_name'])
deputies.head()


# Looking for exact matches of names (in supplier names).

# In[6]:

import unicodedata

def normalize_string(string):
    if isinstance(string, str):
        nfkd_form = unicodedata.normalize('NFKD', string.lower())
        return nfkd_form.encode('ASCII', 'ignore').decode('utf-8')


# In[7]:

data.congressperson_name = data.congressperson_name.apply(normalize_string)
data.supplier = data.supplier.apply(normalize_string)
deputies.civil_name = deputies.civil_name.apply(normalize_string)


# In[8]:

supplier_has_congressperson_name =     data['supplier'].isin(deputies['civil_name'])
data.loc[supplier_has_congressperson_name,
                   ['issue_date', 'congressperson_name', 'supplier', 'subquota_description', 'cnpj_cpf', 'document_id', 'total_net_value']]


# In[9]:

companies = pd.read_csv('../data/2016-09-03-companies.xz', low_memory=False)


# In[10]:

companies['cnpj'].head()


# In[11]:

companies['cnpj'] = companies['cnpj'].str.replace(r'[\.\/\-]', '')


# In[12]:

data = pd.merge(data, companies,
       how='left',
       left_on='cnpj_cpf',
       right_on='cnpj')


# In[13]:

data.name = data.name.apply(normalize_string)
data.trade_name = data.trade_name.apply(normalize_string)


# In[14]:

suspect_row = data.supplier.isin(deputies['civil_name']) | data.name.isin(deputies['civil_name']) | data.trade_name.isin(deputies['civil_name']) 
data[suspect_row].shape


# In[15]:

import re

regex = re.compile(r'(?:{})'.format('|'.join(deputies.civil_name)))
rows = data.supplier.apply(lambda name: regex.search(name) is not None)
data[rows].shape


# In[16]:

data.loc[rows,
         ['issue_date', 'congressperson_name', 'supplier', 'subquota_description', 'cnpj_cpf', 'document_id', 'total_net_value']]


# In[17]:

deputies[deputies.civil_name == 'joao rodrigues']


# So far we've been searching for congresspeople putting money in others' companies. When paying for a non-relative congressperson may be legal, but could raise corruption suspicions when combined with other irregularities.

# In[18]:

data = pd.merge(data, deputies, how='left')


# In[19]:

d = data.head()
rows = (data['supplier'] == data['civil_name']) | (data['supplier'] == data['congressperson_name'])
data.loc[rows,
         ['issue_date', 'congressperson_name', 'supplier', 'subquota_description', 'cnpj_cpf', 'document_id', 'total_net_value']]


# In the previous query, many rows are false positives, given mistakes filling the form. Despite of CNPJ number is right, the supplier field was registered incorrectly, using the congressperson name.

# In[ ]:



