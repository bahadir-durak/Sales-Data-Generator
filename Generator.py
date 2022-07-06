import numpy.random
import pandas as pd
import numpy as np
import random
from datetime import date, timedelta
from time import perf_counter

start = perf_counter()

read_or_generate = 0                    # 0: Read basic data, generate sales, 1: Generate everything
max_sales = 1000000                     # Maximum number of generated sales data
begda = date(2021, 1, 1)                # Beginning date of the sales data
endda = date(2021, 3, 31)               # End date of the sales data
special_days = []                       # Special dates such as Mother's Day, Christmas Eve, etc.
num_stores = 3                          # Number of stores
num_cat = 20                            # Number of product categories
num_pro = 1500                          # Number of products
num_cust = 5000                         # Number of customers
num_trends = 100                        # Number of trending products
num_season = 100                        # Number of seasonal products
min_trends = -20                        # Minimum trend coefficient
max_trends = 20                         # Maximum trend coefficient
min_price = 1                           # Minimum product price
max_price = 100                         # Maximum product price
min_prom_len_days = 2                   # Minimum promotion duration in days
max_prom_len_days = 14                  # Maximum promotion duration in days
min_prom_discount = 10                  # Minimum discount rate (%)
max_prom_discount = 50                  # Maximum discount rate (%)
min_visit_frequency = 1                 # Minimum visit frequency of a customer (days)
max_visit_frequency = 30                # Maximum visit frequency of a customer (days)
min_shopping_volume = 1                 # Minimum number of items in a customer's basket
max_shopping_volume = 50                # Maximum number of items in each customer's basket
min_season = 1                          # Minimum length of season in months
max_season = 6                          # Maximum length of season in months
average_daily_customers = 750           # Average number of daily customers
weekend_ratio = 50                      # Rate of increase in number of visitors at weekends (%)
special_day_ratio = 100                 # Rate of increase in number of visitors at special days (%)
seasonality_ratio = 500                 # Maximum rate of increase in sales of seasonal products (%)
substitute_ratio = 20                   # Average percentage of the products that has substitutes
complementary_ratio = 20                # Average percentage of the products that has a complementary product
promotion_rate = 3                      # Number of simultaneous promotions
yearly_inflation_rate = 3               # Yearly inflation rate
pricing_period = 30                     # Maximum effective duration of price changes on customers' decisions
num_substitution = 3                    # Number of levels for substitution effects
min_substitution = 10                   # Average effect of a low level substitute (%)
dif_substitution = 20                   # Difference between the average effects of two consecutive levels of substitution
num_complement = 3                      # Number of levels for complementary effects
min_complement = 10                     # Average effect of a low level complement (%)
dif_complement = 20                     # Difference between the average effects of two consecutive levels of complements

####################################################################################################################
# # # # # # # # # # #      Stores      # # # # # # # # # #
# Probability indicates the customer's probability of visiting the store
####################################################################################################################
def generate_stores(read_or_generate):
    if read_or_generate == 1:
        cols = ['StoreID', 'Probability']
        stores = pd.DataFrame(columns=cols)
        for i in range(num_stores):
            stores = pd.concat([stores, pd.DataFrame([[i, random.random()]], columns=cols)], ignore_index=True)
        stores.to_excel('stores.xlsx')
    else:
        stores = pd.read_excel('stores.xlsx')
    return stores

####################################################################################################################
# # # # # # # # # # #      Product Categories and Products      # # # # # # # # # #
# Demand rates are relative sales potentials of each product within the category
# Elasticity is the demand sensitivity of products against price changes
# There can be positive or negative demand
# If the product is a seasonal product, BegSeason is the beginning of the season, and EndSeason is the end of it.
#   Up is the rate that indicates how much the product is affected by seasonality.
####################################################################################################################
def generate_products(read_or_generate):
    categories = list(range(num_cat))
    if read_or_generate == 1:
        cols = ['Category', 'ProductID', 'Price', 'Demand', 'Elasticity', 'Trend', 'BegSeason', 'EndSeason', 'Up']
        products = pd.DataFrame(columns=cols)
        for i in range(num_pro):
            price = random.randint(min_price, max_price)
            demand_rate = random.random()
            elasticity = 2 * random.random() + 1
            trend_coefficient = 0
            if random.random() < (num_trends / num_pro):
                trend_coefficient = random.uniform(min_trends, max_trends)
            beg_season = 0
            end_season = 0
            up = 0
            if random.random() < (num_season / num_pro):
                beg_season = np.random.choice(list(range(1, 13)), 1, replace=False)[0]
                end_season = beg_season + numpy.random.choice(list(range(min_season - 1, max_season)), 1, replace=False)[0]
                up = random.uniform(100, seasonality_ratio)
            products = pd.concat([products, pd.DataFrame([[random.choice(categories), i, price, demand_rate, elasticity, \
                                                           trend_coefficient, beg_season, end_season, up]], columns=cols)],
                                 ignore_index=True)
        products = products.sort_values(by=['Category', 'ProductID'])
        products.to_excel('products.xlsx')
    else:
        products = pd.read_excel('products.xlsx')
    return categories, products

####################################################################################################################
# # # # # # # # # # #      Product Substitutes      # # # # # # # # # #
# Number of products having substitutes are randomly selected.
# There may be more than one substitutes for a product, but probability of having an additional substitute is half
#   of the previous one.
# Strength indicates the strength of the relationship between a product and its substitute. The products with higher
#   strength are affected more negatively when their substitutes are in promotion.
#
####################################################################################################################
def generate_substitutes(read_or_generate, products):
    if read_or_generate == 1:
        cols = ['Category', 'ProductID', 'Substitute', 'Strength']
        substitutes = pd.DataFrame(columns=cols)
        for i in range(num_pro):
            if random.random() < (substitute_ratio / num_pro):
                category = products[products['ProductID'] == i]['Category'].values[0]
                product_list = list(products[products['Category'] == category]['ProductID'].values)
                stop = 2
                while stop >= 1:
                    substitute = i
                    while substitute == i:
                        substitute = np.random.choice(product_list, 1, replace=False)[0]
                    product_list.remove(substitute)
                    strength = np.random.choice(list(range(num_substitution)), 1, replace=False)[0]
                    strength = min_substitution + dif_substitution * strength
                    substitutes = pd.concat([substitutes, pd.DataFrame([[category, i, substitute,
                                                                         random.uniform(strength - (dif_substitution / 2),
                                                                                        strength + (dif_substitution / 2))]],
                                                                       columns=cols)], ignore_index=True)
                    if random.random() < 1 / stop:
                        stop *= 2
                    else:
                        stop = 0
        substitutes.to_excel('substitutes.xlsx')
    else:
        substitutes = pd.read_excel('substitutes.xlsx')
    return substitutes

####################################################################################################################
# # # # # # # # # # #      Complementary Products       # # # # # # # # # #
# Number of products having a complementary product are randomly selected.
# Strength indicates the strength of the relationship between a product and its complementary product. The products
#   with higher strength are affected more when their complementary products are added to the basket.
#
####################################################################################################################
def generate_complements(read_or_generate, products):
    if read_or_generate == 1:
        cols = ['Category', 'ProductID', 'Complement', 'Strength']
        complements = pd.DataFrame(columns=cols)
        product_list = list(products['ProductID'].values)
        for i in range(num_pro):
            if random.random() < (complementary_ratio / num_pro):
                complement = i
                while complement == i:
                    complement = np.random.choice(product_list, 1, replace=False)[0]
                category = products[products['ProductID'] == i]['Category'].values[0]
                strength = np.random.choice(list(range(num_complement)), 1, replace=False)[0]
                strength = min_complement + dif_complement * strength
                complements = pd.concat([complements, pd.DataFrame([[category, i, complement,
                                                                     random.uniform(strength - (dif_complement / 2),
                                                                                    strength + (dif_complement / 2))]],
                                                                   columns=cols)], ignore_index=True)
        complements.to_excel('complements.xlsx')
    else:
        complements = pd.read_excel('complements.xlsx')
    return complements

####################################################################################################################
# # # # # # # # # # #      Inflation      # # # # # # # # # #
# Under the effect of inflation, the price of some products will increase at various times during the year
# beg_change is the date of price change, defined randomly.
# There will be 1 increase per product per year on the average (the prices of some products may remain the same,
#   some others may increase two or more times)
# Increase rate is between 0 and (2 * yearly inflation rate), so the average increase rate will be approximately
#   equal to the yearly inflation rate.
####################################################################################################################
def generate_inflation(read_or_generate, products):
    if read_or_generate == 1:
        cols = ['ProductID', 'Beg', 'PrevPrice', 'NewPrice']
        inflation = pd.DataFrame(columns=cols)
        for i in range(int(num_pro * (int((endda - begda).days)) / 365)):
            product_id = random.choice(list(range(num_pro)))
            beg_change = begda + timedelta(days=random.randint(0, int((endda - begda).days)))
            increase = 2 * yearly_inflation_rate * random.random()
            try:
                old_price = inflation[inflation['ProductID'] == product_id]['NewPrice'].values[-1]
            except:
                old_price = products[products['ProductID'] == product_id]['Price'].values[-1]
            new_price = round((1 + increase / 100) * old_price, 2)
            inflation = pd.concat([inflation, pd.DataFrame([[product_id, beg_change, old_price, new_price]], columns=cols)],
                                  ignore_index=True)
        inflation.to_excel('inflation.xlsx')
    else:
        inflation = pd.read_excel('inflation.xlsx')
    return inflation

####################################################################################################################
# # # # # # # # # # #      Promotions      # # # # # # # # # #
# Promoted products are defined randomly considering promotion_rate (Number of simultaneous promotions)
# Promotion durations are defined randomly between min and max duration lengths
# Discount rates are defined randomly between min and max discount rates
####################################################################################################################
def generate_promotions(read_or_generate, products, inflation):
    if read_or_generate == 1:
        cols = ['ProductID', 'Beg', 'End', 'PrevPrice', 'NewPrice']
        discount = pd.DataFrame(columns=cols)
        for i in range(0, int((endda - begda).days) + 1):
            for j in range(num_pro):
                if random.random() <= (2 * promotion_rate) / (100 * (min_prom_len_days + max_prom_len_days)):
                    promotion_duration = random.randint(min_prom_len_days, max_prom_len_days)
                    discount_ratio = random.randint(min_prom_discount, max_prom_discount)
                    try:
                        old_price = inflation[(inflation['ProductID'] == j) & (inflation['Beg'] <= begda + timedelta(days=i))][
                            'NewPrice'].values[-1]
                    except:
                        old_price = products[products['ProductID'] == j]['Price'].values[-1]
                    new_price = round(old_price * (1 - discount_ratio / 100), 2)
                    discount = pd.concat([discount, pd.DataFrame(
                        [[j, begda + timedelta(days=i), begda + timedelta(days=i + promotion_duration), old_price, new_price]],
                        columns=cols)],
                                         ignore_index=True)
        discount.to_excel('discount.xlsx')
    else:
        discount = pd.read_excel('discount.xlsx')
    return discount

####################################################################################################################
# # # # # # # # # # #      Customers      # # # # # # # # # #
# Each customer has a visit frequency, average basket size and different demands for each product categories
# Frequency is the average duration in days between two visits (wd: weekday, we: weekend)
# Volume (average basket size) is defined randomly, but also effected by visit frequency. Customers who visit
#   the store less frequently tend to buy more items.
####################################################################################################################
def generate_customers(read_or_generate, categories, stores):
    if read_or_generate == 1:
        cols = ['CustomerID', 'WdFrequency', 'WeFrequency', 'WdVolume', 'WeVolume'] + categories + ['S' + str(c) for c in list(stores['StoreID'])]
        customer = pd.DataFrame(columns=cols)
        for i in range(num_cust):
            wdfrequency = random.randint(min_visit_frequency, max_visit_frequency)
            wefrequency = random.randint(min_visit_frequency, max_visit_frequency)
            wdvolume = np.ceil(random.randint(min_shopping_volume, max_shopping_volume) * wdfrequency / max_shopping_volume)
            wevolume = np.ceil(random.randint(min_shopping_volume, max_shopping_volume) * wefrequency / max_shopping_volume)
            cat_list = list()
            for j in categories:
                cat_list.append(random.random())
            store_list = list()
            for k in list(stores['StoreID']):
                store_list.append(stores[stores['StoreID'] == k]['Probability'].values[0] * random.random())
            customer = pd.concat([customer, pd.DataFrame([[i, wdfrequency, wefrequency, wdvolume, wevolume] + cat_list + store_list], columns=cols)],
                                 ignore_index=True)
        customer.to_excel('customer.xlsx')
    else:
        customer = pd.read_excel('customer.xlsx')
    return customer

####################################################################################################################
# # # # # # # # # # #      Sales Data      # # # # # # # # # #
# 1- A probability list is created considering the frequencies of customers
# 2- Number of customers visiting the store for each day is defined randomly within the range of
#   average daily customers +-50%. If it is weekend it is increased by "weekend_ratio" +-20%. If it is a special
#   day it is increased by "special_day_ratio" +-20%.
# 3- The customers visiting the store for each day is defined randomly considering probability list
# 4- For each visiting customer, category probability list is created considering customer's category demand rates
# 5- For each visiting customer, basket size is defined randomly within the range of average basket size of the
#   customer +-50%
# 6- For each visiting customer, selected categories are defined randomly considering category probability lists
# 7- Within each selected category, product demand rates are updated considering price changes (with inflation
#   or promotions). Current price and the average price of "pricing_period" is used for calculation. By this method,
#   promotion fatigue is also considered.
# 8- Product demand rates are updated considering trends
# 9- Product demand rates are updated considering seasonality
# 10- Within each selected category, a product is selected randomly considering updated product demand rates
# 11- The number of pieces of selected product is defined randomly and added to customer basket
# 12 - The increase in sales of promoted products will partially increase total sales
####################################################################################################################
stores = generate_stores(read_or_generate)
categories, products = generate_products(read_or_generate)
substitutes = generate_substitutes(read_or_generate, products)
complements = generate_complements(read_or_generate, products)
inflation = generate_inflation(read_or_generate, products)
discount = generate_promotions(read_or_generate, products, inflation)
customer = generate_customers(read_or_generate, categories, stores)

cols = ['Date', 'Store', 'CustomerID', 'Category', 'ProductID', 'Amount', 'Price']
sales = pd.DataFrame(columns=cols)
sales_count = 0
wdclist = list(customer['WdFrequency'])
s = sum(wdclist)
wd_probability_list = [c / s for c in wdclist]
weclist = list(customer['WeFrequency'])
s = sum(weclist)
we_probability_list = [c / s for c in weclist]
all_complements = list(complements['Complement'].values)
for i in range(1 + int((endda - begda).days)):
    if max_sales <= sales_count:
        break
    demand_log = dict()
    price_log = dict()
    curr_date = begda + timedelta(days=i)
    num_visitor = random.randint(int(average_daily_customers / 2), int(3 * average_daily_customers / 2))
    if curr_date.weekday() > 4:
        num_visitor = int(num_visitor * (1 + weekend_ratio / 100) * (0.4 * random.random() + 0.8))
        probability_list = we_probability_list
    else:
        probability_list = wd_probability_list
    if curr_date in special_days:
        num_visitor = int(num_visitor * (1 + special_day_ratio / 100) * (0.4 * random.random() + 0.8))
    daily_customer_list = numpy.random.choice(list(customer['CustomerID']), num_visitor, p=probability_list,
                                              replace=False)
    for j in daily_customer_list:
        if max_sales <= sales_count:
            break
        store_preferences = customer[customer['CustomerID'] == j][
            ['S' + str(c) for c in list(stores['StoreID'])]].values
        s = sum(store_preferences[0])
        store_probability = [c / s for c in store_preferences]
        selected_store = np.random.choice(stores['StoreID'], 1, p=list(store_probability[0]), replace=False)
        preference_list = customer[customer['CustomerID'] == j][categories].values[0]
        s = sum(preference_list)
        customer_probability = [c / s for c in preference_list]
        if curr_date.weekday() > 4:
            average_volume = int(customer[customer['CustomerID'] == j]['WeVolume'])
        else:
            average_volume = int(customer[customer['CustomerID'] == j]['WdVolume'])
        vol = random.randint(int(average_volume / 2), int(3 * average_volume / 2))
        basket = list()
        while vol > 0 and max_sales > sales_count:
            selected_category = numpy.random.choice(categories, 1, p=customer_probability, replace=False)
            product_list = products[products['Category'] == selected_category[0]]['ProductID'].values
            product_demands = products[products['Category'] == selected_category[0]]['Demand'].values
            try:
                product_demands = demand_log[selected_category[0]]
            except:
                for index, value in enumerate(product_demands):
                    price = products[products['ProductID'] == product_list[index]]['Price'].values
                    try:
                        last_price = \
                        inflation[(inflation['ProductID'] == product_list[index]) & (inflation['Beg'] <= curr_date)][
                            'NewPrice'].values[-1]
                    except:
                        last_price = price[0]
                    try:
                        last_price = discount[
                            (discount['ProductID'] == product_list[index]) & (discount['Beg'] <= curr_date) & (
                                        discount['End'] >= curr_date)]['NewPrice'].values[-1]
                    except:
                        pass
                    price_log[product_list[index]] = last_price
                    average_price = 0
                    pcols = ['Beg', 'End', 'PrevPrice', 'NewPrice']
                    price_changes = pd.DataFrame(columns=pcols)
                    try:
                        inf_beg = inflation[(inflation['ProductID'] == product_list[index]) & (
                                    inflation['Beg'] >= curr_date - timedelta(days=pricing_period))]['Beg'].values
                        inf_pre_pri = inflation[(inflation['ProductID'] == product_list[index]) & (
                                    inflation['Beg'] >= curr_date - timedelta(days=pricing_period))]['PrevPrice'].values
                        inf_new_pri = inflation[(inflation['ProductID'] == product_list[index]) & (
                                    inflation['Beg'] >= curr_date - timedelta(days=pricing_period))]['NewPrice'].values
                    except:
                        inf_beg = list()
                    for k in range(len(inf_beg)):
                        price_changes = pd.concat([price_changes,
                                                   pd.DataFrame([[inf_beg[k], 0, inf_pre_pri[k], inf_new_pri[k]]],
                                                                columns=pcols)], ignore_index=True)
                    try:
                        dis_beg = discount[
                            (discount['ProductID'] == product_list[index]) & (discount['Beg'] <= curr_date) & (
                                        discount['End'] >= curr_date - timedelta(days=pricing_period))]['Beg'].values
                        dis_end = discount[
                            (discount['ProductID'] == product_list[index]) & (discount['Beg'] <= curr_date) & (
                                        discount['End'] >= curr_date - timedelta(days=pricing_period))]['End'].values
                        dis_pre_pri = discount[
                            (discount['ProductID'] == product_list[index]) & (discount['Beg'] <= curr_date) & (
                                        discount['End'] >= curr_date - timedelta(days=pricing_period))][
                            'PrevPrice'].values
                        dis_new_pri = discount[
                            (discount['ProductID'] == product_list[index]) & (discount['Beg'] <= curr_date) & (
                                        discount['End'] >= curr_date - timedelta(days=pricing_period))][
                            'NewPrice'].values
                    except:
                        dis_beg = list()
                    for k in range(len(dis_beg)):
                        price_changes = pd.concat([price_changes, pd.DataFrame(
                            [[dis_beg[k], dis_end[k], dis_pre_pri[k], dis_new_pri[k]]], columns=pcols)],
                                                  ignore_index=True)
                    if len(price_changes) > 0:
                        all_price = [0] * pricing_period
                        for c_index, row in price_changes.iterrows():
                            for d, val in enumerate(all_price):
                                if row['End'] == 0:
                                    if all_price[d] == 0:
                                        if row['Beg'] > curr_date - timedelta(days=pricing_period - d):
                                            all_price[d] = row['PrevPrice']
                                        else:
                                            all_price[d] = row['NewPrice']
                                    else:
                                        if row['Beg'] > curr_date - timedelta(days=pricing_period - d):
                                            pass
                                        else:
                                            all_price[d] = row['NewPrice']
                                else:
                                    if all_price[d] == 0:
                                        if row['Beg'] > curr_date - timedelta(days=pricing_period - d) or row[
                                            'End'] < curr_date - timedelta(days=pricing_period - d):
                                            all_price[d] = row['PrevPrice']
                                        else:
                                            all_price[d] = row['NewPrice']
                                    else:
                                        if row['Beg'] > curr_date - timedelta(days=pricing_period - d) or row[
                                            'End'] < curr_date - timedelta(days=pricing_period - d):
                                            pass
                                        else:
                                            all_price[d] = row['NewPrice']
                        average_price = np.average(all_price)
                    else:
                        average_price = last_price
                    product_demands[index] = (0.8 + 0.4 * random.random()) * value * ((average_price / last_price) **
                                                                                      products[products['ProductID'] ==
                                                                                               product_list[index]][
                                                                                          'Elasticity'].values[0])
                    product_trend = products[products['ProductID'] == product_list[index]]['Trend'].values[0]
                    if product_trend != 0:
                        product_demands[index] = product_demands[index] * (
                                    1 + ((curr_date - begda).days / 365) * (product_trend / 100))
                    product_seasonality_beg = \
                    products[products['ProductID'] == product_list[index]]['BegSeason'].values[0]
                    product_seasonality_end = \
                    products[products['ProductID'] == product_list[index]]['EndSeason'].values[0]
                    product_seasonality_up = products[products['ProductID'] == product_list[index]]['Up'].values[0]
                    if product_seasonality_beg != 0 and (
                            (product_seasonality_beg <= curr_date.month <= product_seasonality_end) or (
                            product_seasonality_beg <= 12 + curr_date.month <= product_seasonality_end)):
                        product_demands[index] = product_demands[index] * product_seasonality_up / 100
                    substitute_list = substitutes[substitutes['ProductID'] == product_list[index]]['Substitute'].values
                    strength_list = substitutes[substitutes['ProductID'] == product_list[index]]['Strength'].values
                    for subindex, subvalue in enumerate(substitute_list):
                        if len(discount[(discount['ProductID'] == subvalue) & (discount['Beg'].dt.date <= curr_date) & (
                                discount['End'].dt.date >= curr_date)]['Beg'].values) >= 1:
                            product_demands[index] = product_demands[index] * (1 - (strength_list[subindex] / 100))
                    complement_list = complements[complements['ProductID'] == product_list[index]]['Complement'].values
                    strength_list = complements[complements['ProductID'] == product_list[index]]['Strength'].values
                    for subindex, subvalue in enumerate(complement_list):
                        if subvalue in basket:
                            product_demands[index] = product_demands[index] * (1 + (strength_list[subindex] / 100))
                    demand_log[selected_category[0]] = product_demands
            s = sum(product_demands)
            product_probability = [c / s for c in product_demands]
            selected_product = numpy.random.choice(product_list, 1, p=product_probability, replace=False)
            count = 0
            while selected_product[0] in basket and count < 10:
                selected_product = numpy.random.choice(product_list, 1, p=product_probability, replace=False)
                count += 1
            if count == 10:
                continue
            amount_preferences = [100, 10, 5, 3, 1]
            s = sum(amount_preferences)
            amount_probability = [c / s for c in amount_preferences]
            amount = numpy.random.choice(list(range(1, 6)), 1, p=amount_probability, replace=False)
            sales = pd.concat([sales, pd.DataFrame([[curr_date, selected_store[0], j, selected_category[0],
                                                     selected_product[0], amount[0], price_log[selected_product[0]]]],
                                                   columns=cols)],
                              ignore_index=True)
            sales_count += 1
            basket.append(selected_product[0])
            if selected_product[0] in all_complements:
                p = complements[complements['Complement'] == selected_product[0]]['ProductID'].values[0]
                c = products[products['ProductID'] == p]['Category'].values[0]
                try:
                    del demand_log[c]
                except:
                    pass
            selected_product_index = np.where(product_list == selected_product[0])
            sales_inc_prob = product_demands[selected_product_index[0]] / \
                             products[products['Category'] == selected_category[0]]['Demand'].values[
                                 selected_product_index[0]]
            if sales_inc_prob > 1 and random.random() > (1 / sales_inc_prob):
                pass
            else:
                vol -= 1
            if sales_count % (max_sales//100) == 0:
                print(curr_date, sales_count/(max_sales//100), perf_counter() - start)
sales.to_excel('sales.xlsx')
stop = perf_counter()
print(stop - start)
