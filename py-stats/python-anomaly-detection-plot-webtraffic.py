
# coding: utf-8

# In[14]:


import matplotlib.pyplot as plt
from numpy import loadtxt
import numpy as np
import pandas as pd
from matplotlib import style
style.use('fivethirtyeight')

get_ipython().run_line_magic('matplotlib', 'inline')


# In[41]:


# 1. Download sunspot dataset and upload the same to dataset directory
#    Load the sunspot dataset as an Array
#!mkdir -p dataset
#!wget -c -b http://www-personal.umich.edu/~mejn/cp/data/Impression.txt -P dataset

import matplotlib.dates as mdates

def convert_date(date_bytes):
    return mdates.strpdate2num('%m/%d/%y')(date_bytes.decode('ascii'))

data = loadtxt("dataset/webTraffic.csv", delimiter=',', skiprows=1, converters={0: convert_date})

# 2. View the data as a table
data_frame = pd.DataFrame(data, columns=['Day', 'Impression'])

#data_frame.head(15)
data_frame.describe()


# In[50]:


df = pd.DataFrame(data_frame.Impression)

df['MA_10'] = df.Impression.rolling(10).mean()
df['SD_10'] = df.Impression.rolling(10).std()

df.head(15)


# In[51]:


plt.figure(figsize=(25,15))
plt.grid(True)

plt.plot(df['Impression'], marker='*', label='Traffic', color='green', ls='dashed', linewidth=1)

plt.plot(df['MA_10'], label='MA', color='blue', linewidth=2)
plt.plot(df['SD_10'], label='SD', color='magenta', linewidth=2, ls='dashdot')

plt.legend(loc=2)


# In[52]:


'''
#3 sigma rule
    https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
    
# Mean (+/-) SD (standard deviation) * SIGMA
'''

df['LOW_1'] = df.MA_10 - df.SD_10 
df['HIGH_1'] = df.MA_10 + df.SD_10
df
df['LOW_2'] = df.MA_10 - df.SD_10 * 2
df['HIGH_2'] = df.MA_10 + df.SD_10 * 2

#df['LOW_3'] = df.MA_10 - df.SD_10 * 3
#df['HIGH_3'] = df.MA_10 + df.SD_10 * 3

df.head(15)


# In[56]:


#'''
# 1,2 Sigma outliers
df['Anomaly'] = (df.Impression >= df.HIGH_2) |                         (df.Impression <= df.LOW_2) |                         (df.Impression >= df.HIGH_1) |                         (df.Impression <= df.LOW_1)
'''

# 2-SIGMA outliers
df['Anomaly'] = (df.Impression >= df.HIGH_2) | \
                        (df.Impression <= df.LOW_2)    
'''

filt_spot = df.loc[df['Anomaly'] == True]
filt_spot
#filt_spot.describe()


# In[59]:


plt.figure(figsize=(25,15))
plt.grid(True)

plt.plot(filt_spot['Impression'], marker='*', label='Traffic', color='blue', ls='solid', linewidth=0.1)

plt.plot(filt_spot['LOW_1'], label='LOW', color='green', linewidth=2, ls='dotted')
plt.plot(filt_spot['HIGH_1'], label='HIGH', color='red', linewidth=2, ls='dotted')

plt.plot(filt_spot['LOW_2'], label='LOW', color='green', linewidth=2, ls='dotted')
plt.plot(filt_spot['HIGH_2'], label='HIGH', color='red', linewidth=2, ls='dotted')

print("Plotting")

plt.legend(loc=2)

