import csv
import math
from collections import defaultdict

# 1. Fetch URLs from the 2026-sample
urls = {}
with open('auctionDraftAverages-2026-sample.csv', mode='r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        urls[row['School']] = row['SchoolURL']

# 2. Read new top schools data
schools = []
with open('draft-info/2026-04-07-top-schools.csv', mode='r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        school = row['School']
        conf = row['Conference']
        pts = float(row['ProjectedPoints'])
        
        # LeagifyPosition calculation
        l_pos = "Flex" # Default anything non-power 4 to Flex this year
        if conf == "SEC": l_pos = "SEC"
        elif conf == "ACC": l_pos = "ACC"
        elif conf == "Big 12": l_pos = "Big 12"
        elif conf == "Big Ten": l_pos = "Big Ten"
        
        schools.append({
            'School': school,
            'Conference': conf,
            'ProjectedPoints': row['ProjectedPoints'],
            'NumberOfProspects': row['NumberOfProspects'],
            'SchoolURL': urls.get(school, ''),
            'SuggestedAuctionValue': '',
            'LeagifyPosition': l_pos,
            '_pts': pts
        })

# 3. Group and compute averages
grouped = defaultdict(list)
for s in schools:
    grouped[s['LeagifyPosition']].append(s)

draftable_avg = {}
replacement_avg = {}

for pos, group in grouped.items():
    group.sort(key=lambda x: x['_pts'], reverse=True)
    
    if pos in ("SEC", "Big Ten"):
        top_n = 12
    else:
        top_n = 6 # ACC, Big 12, Flex will all use 6 drafted spots
        
    top_rows = group[:top_n]
    
    avg_top = sum(x['_pts'] for x in top_rows) / len(top_rows) if top_rows else 0
    
    # Use "First Team Out" as the realistic replacement value
    if len(group) > top_n:
        avg_rem = group[top_n]['_pts']
    else:
        # Fallback if there aren't enough teams
        avg_rem = top_rows[-1]['_pts'] if top_rows else 0
        
    draftable_avg[pos] = math.trunc(avg_top * 100) / 100.0
    replacement_avg[pos] = math.trunc(avg_rem * 100) / 100.0

# 4. Generate final output with computations
fieldnames = [
    'School', 'Conference', 'ProjectedPoints', 'NumberOfProspects',
    'SchoolURL', 'SuggestedAuctionValue', 'LeagifyPosition',
    'ProjectedPointsAboveAverage', 'ProjectedPointsAboveReplacement',
    'AveragePointsForPosition', 'ReplacementValueAverageForPosition'
]

def format_num(val):
    if val == int(val):
        return str(int(val))
    return str(val)

with open('auctionDraftAverages-2026.csv', mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for s in schools:
        pos = s['LeagifyPosition']
        d_avg = draftable_avg[pos]
        r_avg = replacement_avg[pos]
        
        p = s['_pts']
        
        paa = math.trunc((p - d_avg) * 100) / 100.0
        par = math.trunc((p - r_avg) * 100) / 100.0
        
        row_out = {
            'School': s['School'],
            'Conference': s['Conference'],
            'ProjectedPoints': s['ProjectedPoints'],
            'NumberOfProspects': s['NumberOfProspects'],
            'SchoolURL': s['SchoolURL'],
            'SuggestedAuctionValue': s['SuggestedAuctionValue'],
            'LeagifyPosition': s['LeagifyPosition'],
            'ProjectedPointsAboveAverage': format_num(paa),
            'ProjectedPointsAboveReplacement': format_num(par),
            'AveragePointsForPosition': format_num(d_avg),
            'ReplacementValueAverageForPosition': format_num(r_avg)
        }
        writer.writerow(row_out)

print("Created auctionDraftAverages-2026.csv successfully.")
