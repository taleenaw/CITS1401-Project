"""
CITS1401 Project 2 - Population Analysis Tool
Name: Taleena Watts
Student ID: 24228963

This program reads population data for sa2 and sa3 areas across Australia,
and produces three outputs:
1. largest populations by age group
2. large SA3 statistics
3. similarity between SA2 areas

All outputs follow the project specification for CITS1401 project 2.
"""


#reads file lines safely
def read_file_lines(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except:
        print(f"Error: couldn’t open {filename}.")
        return None

#standard deviation formula from project doc
def calculate_std(values):
    if len(values) == 0:
        return 0
    avg = sum(values) / len(values)
    if len(values) == 1:
        return 0
    variance = sum((val - avg) ** 2 for val in values) / (len(values) - 1)
    return round(variance ** 0.5, 4)

#cosine similarity formula from project doc
def cosine_similarity(vec1, vec2):
    dot = sum(vec1[i] * vec2[i] for i in range(len(vec1)))
    mag1 = sum(vec1[i] ** 2 for i in range(len(vec1))) ** 0.5
    mag2 = sum(vec2[i] ** 2 for i in range(len(vec2))) ** 0.5
    if mag1 == 0 or mag2 == 0:
        return 0
    return round(dot / (mag1 * mag2), 4)

def main(csvfile_1, csvfile_2):
    areas_lines = read_file_lines(csvfile_1)
    pops_lines = read_file_lines(csvfile_2)
    if areas_lines is None or pops_lines is None:
        return {}, {}, {}

    #clean + lowercase headers (for flexible matching)
    areas_header = [h.lower().strip() for h in areas_lines[0].strip().split(',')]
    pops_header = [h.lower().strip() for h in pops_lines[0].strip().split(',')]

    required_areas = ['s_t name', 's_t code', 'sa3 code', 'sa3 name', 'sa2 code', 'sa2 name']
    required_pops = ['area_code_level2']
    try:
        areas_idx = {key: areas_header.index(key) for key in required_areas}
        pops_idx = {
            'sa2 code': pops_header.index('area_code_level2'),
            'age_groups_start': 2  #populations start at col 3 (index 2)
        }
    except ValueError:
        print("Error: Missing required columns.")
        return {}, {}, {}

    #track duplicate rows so we dont re-add
    seen_area_rows = set()
    seen_pop_rows = set()

    #temporary mapping to store valid SA2 rows (to help keep track)
    valid_sa2_codes = set()

    #build areas mappings (sa2 → sa3 → state + sa2 names)
    sa2_to_sa3 = {}
    sa2_names = {}
    sa3_info = {}

    #process areas file
    for line in areas_lines[1:]:
        clean_line = line.strip()
        if clean_line in seen_area_rows:
            continue  # skip duplicate
        seen_area_rows.add(clean_line)

        parts = clean_line.split(',')
        if len(parts) < 5 or '' in parts:
            continue  #skip bad (invalid) rows

        sa2_code = parts[areas_idx['sa2 code']].strip()
        sa3_code = parts[areas_idx['sa3 code']].strip()
        sa3_name = parts[areas_idx['sa3 name']].strip().lower()
        state = parts[areas_idx['s_t name']].strip().lower()
        state_code = parts[areas_idx['s_t code']].strip()
        sa2_name = parts[areas_idx['sa2 name']].strip().lower()

        #save mappings
        sa2_to_sa3[sa2_code] = sa3_code
        sa2_names[sa2_code] = sa2_name
        if sa3_code not in sa3_info:
            sa3_info[sa3_code] = {
                'name': sa3_name,
                'state_name': state,
                'state_code': state_code,
                'sa2_listed': []
            }
        sa3_info[sa3_code]['sa2_listed'].append(sa2_code)

        valid_sa2_codes.add(sa2_code) #this keeps track of valid sa2s

    #builds population data
    popdata = {}
    age_groups = []

    for i, line in enumerate(pops_lines[1:]):
        clean_line = line.strip()
        if clean_line in seen_pop_rows:
            continue  #this skip duplicate or invalid rows
        seen_pop_rows.add(clean_line)

        parts = clean_line.split(',')
        if len(parts) < 3 or '' in parts:
            continue

        sa2_code = parts[pops_idx['sa2 code']].strip()
        if sa2_code not in valid_sa2_codes:
            continue  #skip if no matching valid sa2 in areas

        if not age_groups:
            age_groups = [h.replace("age ", "").strip() for h in pops_header[2:]]

        try:
            values = [int(x.strip()) for x in parts[2:]]
            if any(val < 0 for val in values): 
                continue
            popdata[sa2_code] = values
        except:
            continue 
    
    #cleans out invalid sa2s that don't have both area + pop data (just in case)
    valid_sa2_codes = valid_sa2_codes.intersection(popdata.keys())

    for sa3 in sa3_info.values():
        sa3['sa2_listed'] = [sa2 for sa2 in sa3['sa2_listed'] if sa2 in valid_sa2_codes]

    if not sa2_to_sa3 or not popdata:
        print("Error: No valid data to process.")
        return {}, {}, {}

    if not valid_sa2_codes:
        print("Error: No valid SA2 data after cleaning.")
        return {}, {}, {}


    OP1 = {}

    for age_idx, age_group in enumerate(age_groups):
        state_totals = {}
        sa3_totals = {}
        sa2_totals = {}

        for sa2_code, pop_list in popdata.items():
            count = pop_list[age_idx]

            sa3_code = sa2_to_sa3[sa2_code]
            sa3_data = sa3_info[sa3_code]
            state_name = sa3_data['state_name']

            # Count totals
            state_totals[state_name] = state_totals.get(state_name, 0) + count
            sa3_totals[sa3_code] = sa3_totals.get(sa3_code, 0) + count
            sa2_totals[sa2_code] = sa2_totals.get(sa2_code, 0) + count

        max_state = min(
            [s for s in state_totals if state_totals[s] == max(state_totals.values())]
        )

        max_sa3 = min(
            [s for s in sa3_totals if sa3_totals[s] == max(sa3_totals.values())]
        )

        max_sa2 = min(
            [s for s in sa2_totals if sa2_totals[s] == max(sa2_totals.values())]
        )

        #this formats age groups like '0-9' or '80-None'
        if '-' in age_group:
            bounds = age_group.split('-')
            lower = bounds[0]
            upper = bounds[1]
        else:
            lower = age_group.split()[0]
            upper = 'None'

        formatted_key = f"{lower}-{upper}"

        #save as op1
        OP1[formatted_key] = [
            max_state,
            sa3_info[max_sa3]['name'],
            sa2_names[max_sa2]
        ]

    OP2 = {}

    for sa3_code, sa3_data in sa3_info.items():
        state_code = sa3_data['state_code']
        sa2_list = sa3_data['sa2_listed']

        total_pop = 0
        sa2_pops = {}

        for sa2_code in sa2_list:
            if sa2_code in popdata:
                sa2_total = sum(popdata[sa2_code])
                sa2_pops[sa2_code] = sa2_total
                total_pop += sa2_total

        if total_pop >= 150000:
            if state_code not in OP2:
                OP2[state_code] = {}
            max_sa2 = min(
                [s for s in sa2_pops if sa2_pops[s] == max(sa2_pops.values())]
            )
            std_dev = calculate_std(popdata[max_sa2])
            OP2[state_code][sa3_code] = [
                max_sa2,
                sa2_pops[max_sa2],
                std_dev
            ]
    #this makes sure that all state codes with no sa3s will be added as an empty dictionary
    all_state_codes = set(sa3_data['state_code'] for sa3_data in sa3_info.values())
       
    for state_code in all_state_codes:
        if state_code not in OP2:
            OP2[state_code] = {}

    all_states = set(sa3_data['state_code'] for sa3_data in sa3_info.values())
    
    OP3 = {}
    for sa3_code, sa3_data in sa3_info.items():
        sa3_name = sa3_data['name']
        sa2_list = sa3_data['sa2_listed']
        if len(sa2_list) < 15:
            continue  #skips sa3s with fewer than 15 sa2 areas

        #does population percentage for each sa2 in sa3
        sa2_percentages = {}
        for sa2_code in sa2_list:
            if sa2_code in popdata:
                total_pop = sum(popdata[sa2_code])
                if total_pop == 0:
                    percentages = [0] * len(popdata[sa2_code])
                else:
                    percentages = [count / total_pop for count in popdata[sa2_code]]
                sa2_percentages[sa2_code] = percentages
                    
        sa2_codes = list(sa2_percentages.keys())      
        max_similarity = -1.0
        candidates = []

        #find max cos similarity among all sa2 pairs in sa3
        for i in range(len(sa2_codes)):
            for j in range(i + 1, len(sa2_codes)):
                code1, code2 = sa2_codes[i], sa2_codes[j]
                vec1, vec2 = sa2_percentages[code1], sa2_percentages[code2]
                # Calculate cosine similarity without rounding (for accuracy)
                dot = sum(vec1[k] * vec2[k] for k in range(len(vec1)))
                mag1 = sum(val*val for val in vec1) ** 0.5
                mag2 = sum(val*val for val in vec2) ** 0.5
                sim = 0.0 if (mag1 == 0 or mag2 == 0) else dot / (mag1 * mag2)
                    
                if sim > max_similarity:
                    max_similarity = sim
                    candidates = [(tuple(sorted([sa2_names[code1], sa2_names[code2]])), 
                                   tuple(sorted([code1, code2], key=lambda x: sa2_names[x])))]
                elif sim == max_similarity:
                    candidates.append((tuple(sorted([sa2_names[code1], sa2_names[code2]])), 
                                       tuple(sorted([code1, code2], key=lambda x: sa2_names[x]))))

        #pick the lexicographically earliest pair by sa2 names
        if candidates:
            #sorts by second name then first name to enforce correct lexicographic order
            candidates.sort(key=lambda entry: (entry[0][1], entry[0][0]))
            best_names, best_pair = candidates[0]
            OP3[sa3_name] = [
                sa2_names[best_pair[0]], 
                sa2_names[best_pair[1]], 
                round(max_similarity, 4)  #rounds for output
            ]

        
    #all done! return 3 outputs :)

    return OP1, OP2, OP3

"""
Debugging Documentation:

Issue 1 (2025 May 6):
* Error Description:
KeyError: 's_t code' when trying to parse the areas CSV file.

* Erroneous Code Snippet:
state_code = parts[areas_idx['s_t code']].strip()

* Test Case:
main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2.csv')

* Reflection:
I forgot to include 's_t code' in my required_areas list so when I tried to access it by the header column, it crashed. It took me a while to realize the project doc said it was needed but I had only added 's_t name'. This made me learn to properly check my column requirements carefully.

------------------------

Issue 2 (2025 May 8):
* Error Description:
KeyError when building OP1 because sa2_names[max_sa2] was missing.

* Erroneous Code Snippet:
OP1[formatted_key] = [max_state, sa3_info[max_sa3]['name'], sa2_names[max_sa2]]

* Test Case:
main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2.csv')

* Reflection:
The program crashed on some SA2 areas because my sa2_names dictionary didn’t include all valid sa2 codes. This made me realise that I was accepting rows with missing sa2 names and not fixing invalid rows, i fixed this by making sure to skip rows with any empty values at the start of reading files.

------------------------

Issue 3 (2025 May 17):
* Error Description:
Standard deviation always returned 0 even when populations were different.

* Erroneous Code Snippet:
variance = sum((val - avg) ** 2 for val in values) / len(values)

* Test Case:
main('SampleData_Areas_P2.csv', 'SampleData_Populations_P2.csv')

* Reflection:
I accidentally used the population formula instead of the sample formula (I divided by N instead of N-1). I googled the difference and saw the project doc linked the formula too. I changed it to divide by (len(values) - 1) and that worked so I learned that tiny math errors can mess up results even when code looks fine.

"""