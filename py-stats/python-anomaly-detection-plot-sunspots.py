
# coding: utf-8

# In[1]:


import matplotlib.pyplot as plt
from numpy import loadtxt
import numpy as np
import pandas as pd
from matplotlib import style
style.use('fivethirtyeight')

get_ipython().run_line_magic('matplotlib', 'inline')


# In[49]:


# 1. Download sunspot dataset and upload the same to dataset directory
#    Load the sunspot dataset as an Array
#!mkdir -p dataset
#!wget -c -b http://www-personal.umich.edu/~mejn/cp/data/sunspots.txt -P dataset
data = loadtxt("dataset/sunspots.txt", float)

'''
import matplotlib.dates as mdates

def convert_date(date_bytes):
    return mdates.strpdate2num('%m/%d/%y')(date_bytes.decode('ascii'))

data = loadtxt("dataset/webTraffic.csv", delimiter=',', skiprows=1, converters={0: convert_date})
'''

# 2. View the data as a table
data_frame = pd.DataFrame(data, columns=['Months', 'SunSpots'])
data_frame.describe()


# In[93]:


df = pd.DataFrame(data_frame.SunSpots[:1500])

df['MA_10'] = df.SunSpots.rolling(10).mean()
df['SD_10'] = df.SunSpots.rolling(10).std()

df.head(15)


# In[94]:


plt.figure(figsize=(25,15))
plt.grid(True)

plt.plot(df['SunSpots'], marker='*', label='Traffic', color='green', ls='dashed', linewidth=1)

plt.plot(df['MA_10'], label='MA', color='blue', linewidth=2)
plt.plot(df['SD_10'], label='SD', color='magenta', linewidth=2, ls='dashdot')

plt.legend(loc=2)


# In[97]:


'''
#3 sigma rule
    https://en.wikipedia.org/wiki/68%E2%80%9395%E2%80%9399.7_rule
    
# Mean (+/-) SD (standard deviation) * SIGMA
'''
# sigma = 1
df['LOW_1'] = df.MA_10 - df.SD_10 
df['HIGH_1'] = df.MA_10 + df.SD_10

# sigma = 2 
df['LOW_2'] = df.MA_10 - df.SD_10 * 2
df['HIGH_2'] = df.MA_10 + df.SD_10 * 2

# sigma = 3
df['LOW_3'] = df.MA_10 - df.SD_10 * 3
df['HIGH_3'] = df.MA_10 + df.SD_10 * 3

df.head(15)


# In[98]:


'''
# 1,2 Sigma outliers
df['Anomaly'] = (df.SunSpots >= df.HIGH_2) | \
                    (df.SunSpots <= df.LOW_2)  | \
                    (df.SunSpots >= df.HIGH_1) | \
                    (df.SunSpots <= df.LOW_1)
'''

# 2-SIGMA outliers
df['Anomaly'] = (df.SunSpots >= df.HIGH_2) |                     (df.SunSpots <= df.LOW_2)


#np.where(df['age']>=50, 'yes', 'no')
filt_spot = df.loc[df['Anomaly'] == True]
filt_spot.head(15)


# In[99]:


'''
=============    ===============================
    character        description
=============    ===============================
    ``'.'``          point marker
    ``','``          pixel marker
    ``'o'``          circle marker
    ``'v'``          triangle_down marker
    ``'^'``          triangle_up marker
    ``'*'``          star marker
    ``'+'``          plus marker
    ``'x'``          x marker
=============    ===============================
'''

plt.figure(figsize=(25,10))
plt.grid(True)
plt.plot(filt_spot['SunSpots'], marker='*', markersize=20, label='Traffic', color='blue', linewidth=0.1)

#plt.plot(filt_spot['LOW_1'], label='LOW', linewidth=2, ls='dotted')
#plt.plot(filt_spot['HIGH_1'], label='HIGH', linewidth=2, ls='dotted')

plt.plot(filt_spot['LOW_2'], label='LOW', color='green', linewidth=3, ls='dotted')
plt.plot(filt_spot['HIGH_2'], label='HIGH', color='red', linewidth=3, ls='dotted')

plt.legend(loc=2)

