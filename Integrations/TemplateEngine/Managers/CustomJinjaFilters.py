# This Manager is used as a template for custom Jinja filters.
# Duplicate this file and rename it to CustomFilters.  

# Add additional filters to the file and they will be available within the templates.
# 
# Filters are Python functions that take the value to the left of the filter
# as the first argument and produce a new value. Arguments passed to the filter 
# are passed after the value.

# For example, the filter {{ 42|myfilter(23) }} is called behind the scenes as myfilter(42, 23).

# To use a custom filter, write a function that takes at least a value argument and returns a value.

# Here is an example filter that formats epoch time as Human time.

'''
import time

def epochTimeToHuman(epoch_time):
    epoch_time = int(epoch_time) / 1000
    human_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(epoch_time))
    return(str(human_time))
'''


