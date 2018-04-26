from codecademySQL import sql_query
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency


'''
Get and examine datasets
'''

visits = sql_query('''
SELECT *
FROM visits
''')
# print (visits.head())

fitness_tests = sql_query('''
SELECT *
FROM fitness_tests
''')
# print (fitness_tests.head())

applications = sql_query('''
SELECT *
FROM applications
''')
# print (applications.head())

purchases = sql_query('''
SELECT *
FROM purchases
''')
# print (purchases.head())

df = sql_query('''
SELECT visits.first_name,
        visits.last_name,
        visits.gender,
        visits.email,
        visits.visit_date,
        fitness_tests.fitness_test_date,
        applications.application_date,
        purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON visits.first_name = fitness_tests.first_name
    AND visits.last_name = fitness_tests.last_name
    AND visits.email = fitness_tests.email
LEFT JOIN applications
    ON visits.first_name = applications.first_name
    AND visits.last_name = applications.last_name
    AND visits.email = applications.email
LEFT JOIN purchases
    ON visits.first_name = purchases.first_name
    AND visits.last_name = purchases.last_name
    AND visits.email = purchases.email
WHERE visits.visit_date >= '7-1-17'
''')
# print (df.head(50))
# print (len(df))


'''
Investigate the A and B groups
'''
# Adding a column to the df table

df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'A' if pd.notnull(x) else 'B')
# print (df.head(50))
# df.to_csv('dataframe.csv',sep=',')

ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()
# print (ab_counts.head(50))

# Plot the above as a pie chart and save for presentation
# plt.figure()
# plt.pie(ab_counts.first_name.values, labels = ['A','B'], autopct='%.2f')
# plt.axis('equal')
# plt.title('Percentage of A/B Test Groups')
# # plt.show()
# plt.savefig('ab_test_chart.png')


'''
Who picks up an application?
'''

df['is_application'] = df.application_date.apply(lambda x: 'No Application' if pd.isnull(x) else 'Application')
# print (df.head(50))

app_counts = df.groupby(['ab_test_group','is_application']).first_name.count().reset_index()
# print (app_counts)

# Pivot app_counts with ab_test_group as the index, is_application as columns
app_pivot = app_counts.pivot(index='ab_test_group',\
                             columns='is_application',\
                             values='first_name')\
                            .reset_index()
# print (app_pivot)

# Define new column 'Total', the sum of Application and No Application
app_pivot['Total'] = app_pivot.apply(lambda row: \
                    row['Application'] \
                    + row['No Application'], \
                    axis = 1)

app_pivot['Percent with Application'] = app_pivot.apply(lambda row: \
                                        row['Application']/row['Total'],\
                                        axis = 1)

# print (app_pivot)

# Perfrom chi2 test to see if percentage difference is statistically significant

contingency = [[250, 2254],
               [325, 2175]]
a,pval,b,c = chi2_contingency(contingency)
# print (pval)

# Pval <0.05 therefore it is highly likely this is not a significant difference in the data


'''
Who purchases a membership?
'''

df['is_member'] = df.purchase_date.apply(lambda x: \
                'Member' if pd.notnull(x) \
                else 'Not Member')
# print (df.head(50))

# Create dataframe that just contains people who picked up an application

just_apps = df[df.is_application=='Application']
# print (just_apps.head(50))

# How many people that picked up an application are and aren't members? Also pivot table
just_apps_counts = just_apps.groupby(['ab_test_group','is_member']).first_name.count().reset_index()
# print (just_apps_counts)

member_pivot = just_apps_counts.pivot(index='ab_test_group', \
                    columns='is_member', \
                    values='first_name')\
                    .reset_index()

# Add Total and Percent Purchase columns to table
member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot['Member'] / member_pivot['Total']
# print (member_pivot)

# Perform hypothesis test to test statistical significance of difference
contingency = [[200, 50],
               [250, 75]]
a,pval,b,c = chi2_contingency(contingency)
# print (pval)

# Perform same process as above on original df data

df_members = df.groupby(['ab_test_group','is_member']).first_name.count().reset_index()
# print (df_members.head())

# Pivot table
final_member_pivot = df_members.pivot(index = 'ab_test_group',\
                        columns = 'is_member',\
                        values = 'first_name')\
                        .reset_index()

# Add Total and Percent Purchase columns
final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot['Member']/final_member_pivot['Total']
print (final_member_pivot)

# Perform hypothesis test to test statistical significance of difference
contingency = [[200, 2304],
               [250, 2250]]
a,pval,b,c = chi2_contingency(contingency)
# print (pval)


'''
Summarise the acquisition funnel with a chart
'''

# Bar charts showing the difference between Group A and B at each stage of the process
# Percnt of visitors who apply
plt.figure()
data = app_pivot['Percent with Application'].values
plt.bar(range(len(data)),data)
ax = plt.subplot()
ax.set_xticks(range(len(data)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
ax.set_yticks([0.0,0.05,0.10,0.15])
ax.set_yticklabels(['0%','5%','10%','15%'])
plt.title('Percent of Visitors Who Apply')
# plt.show()
plt.savefig('visitors_apply.png')

#
# #Percent of applicants who purchase a membership
plt.figure()
data = member_pivot['Percent Purchase'].values
plt.bar(range(len(data)),data)
ax = plt.subplot()
ax.set_xticks(range(len(data)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
ax.set_yticks([0.0,0.2,0.4,0.6,0.8,1.0])
ax.set_yticklabels(['0%','20%','40%','60%','80%','100%'])
plt.title('Percent of Applicants Who Purchase a Membership')
# plt.show()
plt.savefig('applicants_membership.png')
#
# # Percent of visitors who purchase a membership
plt.figure()
data = final_member_pivot['Percent Purchase'].values
plt.bar(range(len(data)),data)
ax = plt.subplot()
ax.set_xticks(range(len(data)))
ax.set_xticklabels(['Fitness Test','No Fitness Test'])
ax.set_yticks([0.0,0.04,0.08,0.12])
ax.set_yticklabels(['0%','4%','8%','12%'])
plt.title('Percent of Visitors Who Purchase a Membership')
# plt.show()
plt.savefig('visitors_membership.png')
