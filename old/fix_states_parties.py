import pandas
df = pandas.read_csv('candidates_dirty.csv', dtype={'Party': str, 'District': 'Int64'})

# https://gist.github.com/rogerallen/1583593
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

for row in df.itertuples():
    # Change Parties
    if row.Freshman[-3:] == '(R)':
        df.at[row.Index, 'Party'] = 'R'
    elif row.Freshman[-3:] == '(D)':
        df.at[row.Index, 'Party'] = 'D'
    elif row.Freshman[-3:] == '(I)':
        df.at[row.Index, 'Party'] = 'I'
    df.at[row.Index, 'Freshman'] = row.Freshman[:-4]

    # Change Districts
    state_split = row.State.split()
    district_split = state_split[-1] # last element in array, aka the district
    if district_split == 'AL':
        district_split = 0
    else:
        district_split = int(district_split)

    df.at[row.Index, 'District'] = district_split

    # Change States
    wo_district = state_split[:-1]
    if len(wo_district) == 2:
        state = wo_district[0] + ' ' + wo_district[1]
    else:
        state = wo_district[0] # list to string

    # replace state with abbreviation
    df.at[row.Index, 'State'] = us_state_abbrev[state]

df.to_csv('candidates.csv', encoding='utf-8', index=False)
