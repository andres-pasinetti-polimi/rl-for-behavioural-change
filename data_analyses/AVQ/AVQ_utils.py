import numpy as np

def can_convert_to_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    

def get_hhs_for_population(population, no_none=False):
    hhs_list = []
    physical_activity_items_list = []
    alcohol_items_list = []
    diet_items_list = []
    for i in range(population.shape[0]):
        #print(f"User: {i}")
        user = population.iloc[i]
        hhs, physical_activity_items, alcohol_items, diet_items = get_user_hhs(user)
        hhs_list.append(hhs)
        #physical_activity_items_list.append(physical_activity_items)
        #alcohol_items_list.append(alcohol_items)
        #diet_items_list.append(diet_items)
        
    if no_none:
        hhs_list = [d for d in hhs_list if None not in d.values()]

    return hhs_list#, physical_activity_items_list, alcohol_items_list, diet_items_list


def get_dem_hhs_for_population(population, no_none=True):
    hhs_list = get_hhs_for_population(population)
    demography_var = ['ETAMi',  # età
                      'SESSO',  
                      'STCIVMi',# stato civile
                      'ISTRMi', # grado d'istruzione
                      'SITEC'   # soddisfazione per la situazione economica negli ultimi 12 mesi
    ]
    dem_hhs_list = []
    for i in range(len(hhs_list)):
        if not None in hhs_list[i].values():
            demography = {'età': population.iloc[i]['ETAMi'],
                          'sesso': population.iloc[i]['SESSO'],
                          'stato civile': population.iloc[i]['STCIVMi'],
                          'istruzione': population.iloc[i]['ISTRMi'],
                          'soddisfazione economica': population.iloc[i]['SITEC']
            }
            population.iloc[i][demography_var]
            dem_hhs_list.append({'demography': demography, 'hhs': hhs_list[i]})

    if no_none:
        dem_hhs_list = [d for d in dem_hhs_list 
                        if (None not in d['demography'].values() 
                            and
                            None not in d['hhs'].values())]

    return dem_hhs_list


def get_user_hhs(user, verbose=False):
    ### Smoking
    if can_convert_to_int(user['FUMO']) and int(user['FUMO']) in [2, 3]:
        smoking = 10
    elif can_convert_to_int(user['NSIGARM']):
        range_smoking = 17
        smoking = abs(int(user['NSIGARM'])-range_smoking)/range_smoking*10//1
        smoking = round(smoking)
    else:
        if verbose: print("No smoking information. Default: smoking=None")
        smoking = None


    ### Physical Activity   
    # SPOCON: Nel suo tempo libero pratica con carattere di continuità uno o più sport?
    # SPOSAL: Nel suo tempo libero pratica saltuariamente uno o più sport?
    # ATTFIS: Le capita di svolgere nel tempo libero qualche attività fisica?
    # ORESETSP: Ore di attività sportiva praticate nell'ultima settimana

    spocon = (
        int(user['SPOCON']) if can_convert_to_int(user['SPOCON']) else
        None
    )

    sposal = (
        int(user['SPOSAL']) if can_convert_to_int(user['SPOSAL']) else
        None
    )

    attfis = (
        int(user['ATTFIS']) if can_convert_to_int(user['ATTFIS']) else
        None
    )

    oresetsp = (
        int(user['ORESETSP']) if can_convert_to_int(user['ORESETSP']) else
        None
    )

    if can_convert_to_int(user['ATTFIS']) and int(user['ATTFIS']) == 1:
        physical_activity = 0                        # no attività fisica nel tempo libero
    else: 
        if can_convert_to_int(user['ORESETSP']):     # ore di attività sportiva a settimana
            physical_activity = (
                0 if int(user['ORESETSP']) == 1 else # nell'ultima settimana non ho praticato
                4 if int(user['ORESETSP']) == 2 else # fino a due ore a settimana
                7 if int(user['ORESETSP']) == 3 else # da più di 2 fino a 4 ore
                10 # int(user['ORESETSP']) >= 4      # più di 4 ore a settimana
            )
        else: # svolge attività fisica ma no sport ?
            if can_convert_to_int(user['ATTFIS']):
                physical_activity = (
                    4 if int(user['ATTFIS']==2) else # una o più volte a settimana
                    2 if int(user['ATTFIS']==3) else # una o più volte al mese
                    1 #if int(user['ATTFIS']==4)     # più raramente
                )
            elif can_convert_to_int(user['SPOSAL']):
                physical_activity = (
                    2 if int(user['SPOSAL'])==2 else # pratica salutariamente (assumo 1 o 2 volte al mese)
                    0
                )

    physical_activity_items= {'spocon': spocon, 'sposal': sposal, 'attfis': attfis, 'oresetsp': oresetsp}

    ### Alcohol
    # should differenciate between men and women
    # Non-drinker:                                                             10   --> daily_drinks == 0 and bicalc == 0
    # Occasional drinker (1 or 2 drinks, monthly or less):                      9   --> daily_drinks <= 2/30
    # Occasional drinker (3 or 4 drinks, monthly or less):                      8   --> 2/30 < daily_drinks <= 4/30
    # Occasional drinker (1 or 2 drinks, 2-4 times times a month):              7   --> 4/30 < daily_drinks <= 2*4/30
    # Occasional drinker (3 or 4 drinks, 2-4 times times a month):              7   --> 2*40/30 < daily_drinks <= 4*4/30
    # Heavy drinker (1 or 2 drinks, 2-3 times a week), no binge drinking:       6   --> 4*4/30 < daily_drinks <= 2*3/7
    # Heavy drinker (3 or 4 drinks, 2-3 times a week), no binge drinking:       5   --> 2*3/7 < daily_drinks <= 4*3/7
    # Heavy drinker (1 or 2 drinks, 4 or more times a week), no binge drinking: 4   --> 4*3/7 < daily_drinks <= 2*7/7
    # Heavy drinker (3 or 4 drinks, 4 or more times a week), no binge drinking: 3   --> 2*7/7 < daily_drinks <= 4*7/7
    # Occasional drinker (5 or more drinks, monthly or less), binge drinking:   2   --> bicalc == 2 (approx.)
    # Occasional drinker (5 or more drinks, 2-4 times a month), binge drinking: 2   --> 
    # Heavy drinker (5 or more drinks, 2-3 times a week), binge drinking:       1   --> 
    # Heavy drinker (5 or more drinks, 4 or more times a week), binge drinking: 0   --> daily_drinks > 4 (approx.)

    # Available data:
    # BIRRA: quantità di birra giornaliera
    # BICBIRRAM: bicchieri di birra giornalieri
    # VINO: quantità di vino giornaliera
    # BICVINOM: bicchieri di vino giornalieri
    # LIQUOR, ALCOL, AMAR: quantità di superalcolici, aperitivi alcolici, amari giornaliera 
    # BICALTROM: bicchieri di altro giornalieri
    # BFPAS: frequenza con cui capita di bere vino o alcolici fuori dai pasti                                   # approx. IRRILEVANTE SE ABBIAMO QUELLI PRIMA
    # BICFUORIM: bicchieri di vino o alcolici consimuati fuori dai pasti settimanalmente                        # TROPPO POCHE RISPOSTE
    # BICALC: consumo di almeno 6 biccheri di alcol in un'unica occasione negli ultimi 12 mesi
    # NBICALCM: no. volte di consumo di almeno 6 biccheri di alcol in un'unica occasione negli ultimi 12 mesi   # TROPPO POCHE RISPOSTE


    quantity_to_daily = {
        1: 3,
        2: 1.5,
        3: 3/7,
        4: 1/10,
        5: 1/50,
        6: 0,
        None: None 
    }

    beer_daily = (
        int(user['BICBIRRAM']) if can_convert_to_int(user['BICBIRRAM']) else
        quantity_to_daily[int(user['BIRRA'])] if can_convert_to_int(user['BIRRA']) else
        None
    ) 

    wine_daily = (
        int(user['BICVINOM']) if can_convert_to_int(user['BICVINOM']) else
        quantity_to_daily[int(user['VINO'])] if can_convert_to_int(user['VINO']) else
        None
    )

    liquor = (
        int(user['LIQUOR']) if can_convert_to_int(user['LIQUOR']) else
        None 
    )
    liquor_daily = quantity_to_daily[liquor]

    ape = (
        int(user['ALCOL']) if can_convert_to_int(user['ALCOL']) else
        None 
    )
    ape_daily = quantity_to_daily[ape]

    amar = (
        int(user['AMAR']) if can_convert_to_int(user['AMAR']) else
        None 
    )
    amar_daily = quantity_to_daily[amar]

    other_daily_items = [liquor_daily, ape_daily, amar_daily]
    other_daily_avail = [other for other in other_daily_items if other is not None]
    other_daily = np.sum(other_daily_avail)

    if beer_daily == None and wine_daily == None and other_daily == None:
        if verbose: print("No daily drinks information. Default: daily_drinks=None")
        daily_drinks=None
    else: # Assume None = 0
        daily_drink_items = [beer_daily, wine_daily, other_daily]
        available_daily_drink_items = [drink for drink in daily_drink_items if drink is not None]
        daily_drinks = np.sum(available_daily_drink_items)

    # quante volte a settimana bevi fuori dai pasti
    outside_weekly_freq = (
        None if user['BFPAS']==' ' else
        7 if int(user['BFPAS']) == 1 else
        2 if int(user['BFPAS']) == 2 else
        0.5 if int(user['BFPAS']) == 3 else
        0 #if int(user['BFPAS']) == 4
    )

    # quanti bicchieri bevi fuori dai pasti in una settimana
    outside_weekly = (
        None if not can_convert_to_int(user['BICFUORIM']) else      # MOST PEOPLE DO NOT GIVE AN ANSWER
        int(user['BICFUORIM']) if int(user['BICFUORIM']) < 9 else
        15 if int(user['BICFUORIM']) == 10 else
        25 #if int(user['BICFUORIM']) == 11
    ) 

    bicalc = (
        None if not can_convert_to_int(user['BICALC']) else
        int(user['BICALC'])
    )
    
    nbicalcm = (
        None if not can_convert_to_int(user['NBICALCM']) else
        int(user['NBICALCM'])
    )

    """
    # more is unhealthy
    outside_meal_drinking = (
        None if outside_weekly == None or outside_weekly_freq == None else
        10 if outside_weekly/outside_weekly_freq >= 5 else
        0 
    )
    if outside_meal_drinking==None:
        if verbose: print("No outside_meal_drinking information. Default: outside_meal_drinking=0")
        outside_meal_drinking=0
    """

    alcohol_items = {'beer_daily': beer_daily, 'wine_daily': wine_daily, 'other_daily': other_daily, 
                     'outside_weekly_freq': outside_weekly_freq, 'outside_weekly': outside_weekly, 
                     'bicalc': bicalc, 'nbicalcm': nbicalcm}

    def assign_alcohol_score(daily_drinks, bicalc):
        if daily_drinks == 0 and bicalc == 0:
            return 10
        elif bicalc == 2:  # Includes binge drinking cases
            return 2
        elif daily_drinks <= 2/30:
            return 9
        elif daily_drinks <= 4/30:
            return 8
        elif daily_drinks <= 2*4/30:
            return 7
        elif daily_drinks <= 4*4/30:
            return 7
        elif daily_drinks <= 2*3/7:
            return 6
        elif daily_drinks <= 4*3/7:
            return 5
        elif daily_drinks <= 2*7/7:
            return 4
        elif daily_drinks <= 4*7/7:
            return 3
        elif daily_drinks > 4:
            return 0
        return None

    alcohol = assign_alcohol_score(daily_drinks, bicalc)

    ### Diet
    fruit_veg = 0
    fruit_daily = (
        None if not can_convert_to_int(user['FRUTTA']) and not can_convert_to_int(user['PZFRUTTA']) else
        0 if int(user['FRUTTA'])>=3 else
        int(user['PZFRUTTA'])
    )
    if fruit_daily == None:
        if verbose: print("No fruits consumption information. Default: fruit_veg=None")
        fruit_veg = None

    veg_daily = (
        0 if can_convert_to_int(user['VERD']) and int(user['VERD'])>=3 else
        int(user['PZVERD']) if can_convert_to_int(user['PZVERD']) else
        None
    )
    
    if veg_daily == None:
        if verbose: print("No vegetables consumption information. Default: fruit_veg=None")
        fruit_veg = None

    if fruit_veg == 0:
        fruit_veg_daily = fruit_daily + veg_daily
        fruit_veg = (
            0 if fruit_veg_daily == 0 else
            0.25 if fruit_veg_daily in [1, 2] else
            0.5 if fruit_veg_daily in [3, 4] else
            1 if fruit_veg_daily >= 5 else
            None
        )

    daily_servings = {
        1: 2,
        2: 1,
        3: 3/7, # qualche volta a settimana
        4: 1/10, # meno di una volta a settimana
        5: 0
    }
    if can_convert_to_int(user['LEGUMI']):
        legumes_daily = daily_servings[int(user['LEGUMI'])]
        legumes = (
            0 if legumes_daily <= 1/10 else
            1 if legumes_daily >= 3/7 else
            None
        )
    else:
        if verbose: print("No legumes consumption information. Default: legumes=None")
        legumes = None

    # red meat: ·1-2 per day→0 / 4-6 servings per week→0.25 / 2-3 servings per week→0.75 / ≤1 servings per week→1

    if not (can_convert_to_int(user['CMAIAL']) and can_convert_to_int(user['CBOV'] and can_convert_to_int(user['COV']))):
        if verbose: print("No red meat consumption information. Default: red_meat=None")
        red_meat = None
    else: # Assume None = 0
        red_meat_items = [daily_servings[int(user[meat_var])] for meat_var in ['CMAIAL', 'CBOV', 'COV']  if can_convert_to_int(user[meat_var])]
        available_red_meat_items = [item for item in red_meat_items if item is not None]
        red_meat_daily = np.sum(available_red_meat_items)
        red_meat = (
            0 if red_meat_daily >= 1 else
            0.25 if (red_meat_daily >= 4/7 and red_meat_daily < 1) else
            0.5 if (red_meat_daily >= 2/7 and red_meat_daily < 4/7) else
            1 if red_meat_daily < 2/7 else
            None
        )
    
    if can_convert_to_int(user['SALUMI']):
        processed_meat_daily = daily_servings[int(user['SALUMI'])]
        processed_meat = (
            0 if processed_meat_daily >= 1 else
            0.25 if (processed_meat_daily >= 3/7 and processed_meat_daily < 1) else
            0.5 if (processed_meat_daily >= 1/7 and processed_meat_daily < 3/7) else
            1 if processed_meat_daily < 1/7 else
            None
        )
    else:
        if verbose: print("No processed meat consumption information. Default: processed_meat=None")
        processed_meat = None

    if can_convert_to_int(user['DOLCI']):
        sweets_daily = daily_servings[int(user['DOLCI'])]
        sweets = (
            0 if sweets_daily >= 1 else
            0.25 if (sweets_daily >= 3/7 and sweets_daily < 1) else
            0.5 if (sweets_daily >= 1/7 and sweets_daily < 3/7) else
            1 if sweets_daily < 1/7 else
            None
        )
    else:
        if verbose: print("No sweets consumption information. Default: sweets=None")
        sweets = None

    if can_convert_to_int(user['SNACK']):
        snacks_daily = daily_servings[int(user['SNACK'])]
        snacks = (
            0 if snacks_daily >= 1 else
            0.25 if (snacks_daily >= 3/7 and snacks_daily < 1) else
            0.5 if (snacks_daily >= 1/7 and snacks_daily < 3/7) else
            1 if snacks_daily < 1/7 else
            None    
        )
    else:
        if verbose: print("No snacks consumption information. Default: snacks=None")
        snacks = None

    if can_convert_to_int(user['BGAS']):
        sugary_beverages = (
            0 if int(user['BGAS']) <= 3 else
            0.25 if int(user['BGAS']) == 4 else
            0.75 if int(user['BGAS']) == 5 else
            1 if int(user['BGAS']) == 6 else
            None
        )
    else:
        if verbose: print("No sugary beverages consumption information. Default: sugary_beverages=None")
        sugary_beverages = None

    if can_convert_to_int(user['BMI']):
        bmi = (
            0 if (int(user['BMI']) == 1 or int(user['BMI']) == 4) else
            0.5 if int(user['BMI']) == 3 else
            1 if int(user['BMI']) == 2 else
            None
        )
    else:
        if verbose: print("No bmi information. Default: bmi=None")
        bmi = None

    if alcohol!=None:
        alc = alcohol/10
    else:
        if verbose: print("No alcohol consumption information. Default: alc=None")
        alc = None

    diet_items = [fruit_veg, legumes, red_meat, processed_meat, sweets, snacks, sugary_beverages, bmi, alc]
    available_diet_items = [item for item in diet_items if item is not None]
    none_count = diet_items.count(None)
    if none_count >= 3:
        if verbose: print("Too few diet information available. Default: diet=None")
        diet=None
    else:    
        diet = np.sum(available_diet_items)/len(available_diet_items)*10
        diet = round(diet)

    ### Mental Wellbeing
    if can_convert_to_int(user['MH']):
        mental_wellbeing = int(user['MH'])//10
    else:
        mental_wellbeing = None        

    hhs = {"Smoking": smoking, "Physical Activity": physical_activity, "Alcohol": alcohol, "Diet": diet, "Mental Wellbeing": mental_wellbeing}
    
    return hhs, physical_activity_items, alcohol_items, diet_items



import pandas as pd
import matplotlib.pyplot as plt

def plot_2_populations(df1, df2, var, figsize=(5, 3)):
    # Compute the value counts for both DataFrames
    value_counts_1 = df1[var].value_counts()
    value_counts_2 = df2[var].value_counts()

    def get_dataframe_variable_name(df, globals_dict):
        return [name for name, value in globals_dict.items() if value is df][0]
    
    hhs_pop_1[0] = get_dataframe_variable_name(df1, globals())
    hhs_pop_2[0] = get_dataframe_variable_name(df2, globals())
    
    # Align the value counts by index
    aligned_counts = pd.DataFrame({
        hhs_pop_1[0]: value_counts_1,
        hhs_pop_2[0]: value_counts_2
    }).fillna(0).sort_index()  # Align and sort by index

    # Plot the grouped bar chart
    plt.figure(figsize=figsize)
    x = range(len(aligned_counts.index))  # Positions for bars

    # Bar width and offsets
    bar_width = 0.35
    plt.bar(x, aligned_counts[hhs_pop_1[0]], width=bar_width, label=hhs_pop_1[0], color='skyblue', edgecolor='black')
    plt.bar([pos + bar_width for pos in x], aligned_counts[hhs_pop_2[0]], width=bar_width, label=hhs_pop_2[0], color='orange', edgecolor='black')

    # Customize the plot
    plt.xticks([pos + bar_width / 2 for pos in x], aligned_counts.index, rotation=0)  # Center the ticks
    plt.title(f'Comparison of {var} Value Counts Between {hhs_pop_1[0]} and {hhs_pop_2[0]}')
    plt.xlabel(f'{var} Values')
    plt.ylabel('Count')
    plt.legend(title='Datasets')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()



def plot_var(df, var):
    # Get the value counts of the 'VINO' column
    value_counts = df[var].value_counts()

    def get_dataframe_variable_name(df, globals_dict):
        return [name for name, value in globals_dict.items() if value is df][0]
    
    df_name = get_dataframe_variable_name(df, globals())

    # Create the bar plot
    plt.figure(figsize=(10, 3))
    value_counts.sort_index().plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f'Counts of Each Value of {var} in {df_name}')
    plt.xlabel(f'{var} Values')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()




from collections import Counter
def plot_pop_var_perc(hhs_pop_dict, pillar, figsize=(5, 3)):
    hhs_pop = list(hhs_pop_dict.items())[0][1]
    hhs_list = [hhs[pillar] for hhs in hhs_pop]
    hhs_list_avail = [hhs for hhs in hhs_list if hhs is not None]

    value_counts = Counter(hhs_list_avail)
    total_count = sum(value_counts.values())
    avail_perc = len(hhs_list_avail)/len(hhs_list)
    percentages = {key: (count / total_count) * 100 for key, count in value_counts.items()}

    df_name = list(hhs_pop_dict.items())[0][0]
    
    # Align the value counts by index
    aligned_counts = pd.DataFrame({
        df_name: percentages
    }).sort_index()  # Align and sort by index

    # Plot the grouped bar chart
    plt.figure(figsize=figsize)
    x = sorted(list(value_counts.keys()))  # Positions for bars

    # Bar width and offsets
    bar_width = 0.35
    plt.bar(x, aligned_counts[df_name], width=bar_width, label=df_name, color='skyblue', edgecolor='black')

    # Customize the plot
    #plt.xticks([pos + bar_width / 2 for pos in x], aligned_counts.index, rotation=0)  # Center the ticks
    plt.title(f'{pillar} - {df_name} ({round(avail_perc, 2)})')
    plt.xlabel(f'{pillar}')
    plt.xticks(list(value_counts.keys()))
    plt.ylabel('Percentage')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()



def plot_2_pop_hhs_perc(hhs_populations, pillar, figsize=(4, 3)):
    hhs_pop_1 = list(hhs_populations.items())[0]
    hhs_pop_2 = list(hhs_populations.items())[1]

    hhs_list_1 = [hhs[pillar] for hhs in hhs_pop_1[1]]
    hhs_list_1_avail = [hhs for hhs in hhs_list_1 if hhs is not None]
    
    hhs_list_2 = [hhs[pillar] for hhs in hhs_pop_2[1]]
    hhs_list_2_avail = [hhs for hhs in hhs_list_2 if hhs is not None]

    value_counts_1 = Counter(hhs_list_1_avail)
    total_count_1 = sum(value_counts_1.values())
    avail_perc_1 = len(hhs_list_1_avail)/len(hhs_list_1)
    percentages_1 = {key: (count / total_count_1) * 100 for key, count in value_counts_1.items()}

    value_counts_2 = Counter(hhs_list_2_avail)
    total_count_2 = sum(value_counts_2.values())
    avail_perc_2 = len(hhs_list_2_avail)/len(hhs_list_2)
    percentages_2 = {key: (count / total_count_2) * 100 for key, count in value_counts_2.items()}
    
    # Align the value counts by index
    aligned_counts = pd.DataFrame({
        hhs_pop_1[0]: percentages_1,
        hhs_pop_2[0]: percentages_2
    }).fillna(0).sort_index()  # Align and sort by index

    # Plot the grouped bar chart
    plt.figure(figsize=figsize)
    x = range(len(aligned_counts.index))  # Positions for bars

    # Bar width and offsets
    bar_width = 0.35
    plt.bar(x, aligned_counts[hhs_pop_1[0]], width=bar_width, label=hhs_pop_1[0], color='skyblue', edgecolor='black')
    plt.bar([pos + bar_width for pos in x], aligned_counts[hhs_pop_2[0]], width=bar_width, label=hhs_pop_2[0], color='orange', edgecolor='black')

    # Customize the plot
    plt.xticks([pos + bar_width / 2 for pos in x], aligned_counts.index, rotation=0)  # Center the ticks
    plt.title(f'Comparison of {pillar} HHS between {hhs_pop_1[0]} ({round(avail_perc_1, 2)}) and {hhs_pop_2[0]} ({round(avail_perc_2, 2)})', fontsize=10)
    plt.xlabel(f'{pillar} HHS')
    plt.ylabel('Percentage')
    plt.ylim(0,100)
    plt.legend(title='Populations')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()



def plot_hhs_population(hhs_population, name_population, figsize=(8, 4)):
    pillars = ['Smoking', 'Physical Activity', 'Alcohol', 'Diet', 'Mental Wellbeing']
    hhs_by_pillar = {pillar: [hhs[pillar] for hhs in hhs_population] for pillar in pillars}
    hhs_avail_by_pillar = {
        pillar: [hhs for hhs in hhs_by_pillar[pillar] if hhs is not None] 
        for pillar in pillars
    }
    avail_perc_by_pillar = {pillar: len(hhs_avail_by_pillar[pillar])/len(hhs_by_pillar[pillar]) for pillar in pillars}        
    counts_by_pillar = {pillar: Counter(hhs_avail_by_pillar[pillar]) for pillar in pillars}
    total_counts_by_pillar = {pillar: sum(counts_by_pillar[pillar].values()) for pillar in pillars}
    perc_by_pillars = {
        pillar: {key: (value / total_counts_by_pillar[pillar]) * 100 for key, value in counts.items()}
        for pillar, counts in counts_by_pillar.items()
    }

    # Align the value counts by index
    aligned_counts = pd.DataFrame(perc_by_pillars).sort_index()  # Align and sort by index

    # Plot the grouped bar chart
    plt.figure(figsize=figsize)
    x = range(len(aligned_counts.index))  # Positions for bars

    # Bar width and offsets
    bar_width = 0.15
    x_positions = range(len(aligned_counts.index))  # X-axis positions

    # Create bars for each pillar
    for i, pillar in enumerate(pillars):
        offsets = [pos + i * bar_width for pos in x_positions]
        plt.bar(
            offsets,
            aligned_counts[pillar],
            width=bar_width,
            label=pillar,
            edgecolor='black',
        )

    # Customize the plot
    # Customize the plot
    plt.xticks(
        [pos + bar_width * (len(pillars) - 1) / 2 for pos in x_positions],
        aligned_counts.index,
        rotation=0,
    )
    plt.title(f'HHS distribution by pillar - {name_population}', fontsize=14)
    plt.xlabel('HHS')
    plt.ylabel('Percentage')
    plt.ylim(0, 90)
    plt.legend(title='Pillars', loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()


def compare_best_worst_by_var(df, hhs_list, var, n_users):
    # Function to calculate the mean of available (non-None) values in a dictionary
    def calculate_mean(d):
        values = [v for v in d.values() if v is not None]
        return sum(values) / len(values) if values else float('-inf')  # Handle empty case

    # Enumerate the data to keep track of the original index
    data_with_indices = [(i, d, calculate_mean(d)) for i, d in enumerate(hhs_list)]

    # Sort by mean in descending order
    ordered_data = sorted(data_with_indices, key=lambda x: x[2], reverse=True)

    # Extract the sorted dictionaries while keeping their original positions
    sorted_dicts = [{"original_index": i, "dictionary": d} for i, d, _ in ordered_data]

    healthiest_users = []
    for i in [dict['original_index'] for dict in sorted_dicts][:n_users]:
        healthiest_users.append(df.iloc[i][var])

    unhealthiest_users = []
    for i in [dict['original_index'] for dict in sorted_dicts][-n_users:]:
        unhealthiest_users.append(df.iloc[i][var])

    def plot_2_lists(list1, list2):
        # Preprocess lists: replace non-convertible values with "NA"
        list1 = [int(x) if can_convert_to_int(x) else "NA" for x in list1]
        list2 = [int(x) if can_convert_to_int(x) else "NA" for x in list2]
        
        # Count occurrences of each value in both lists
        count1 = Counter(list1)
        count2 = Counter(list2)

        # Custom sorting function to ensure "NA" is last
        def sort_key(value):
            # Treat non-NA values normally, but place "NA" last
            if value == "NA":
                return (1, value)  # Place "NA" last
            return (0, value)  # All other values will be sorted normally

        # Get all unique values across both lists, and ensure "NA" is last
        all_values = sorted(set(count1.keys()).union(set(count2.keys())), key=sort_key)
        
        # Prepare data for plotting
        values1 = [count1.get(value, 0) for value in all_values]
        values2 = [count2.get(value, 0) for value in all_values]

        # Convert y-values to percentages
        total_count1 = sum(values1)
        total_count2 = sum(values2)
        values1_percentage = [v / total_count1 * 100 if total_count1 > 0 else 0 for v in values1]
        values2_percentage = [v / total_count2 * 100 if total_count2 > 0 else 0 for v in values2]

        # Bar width and positions
        x = np.arange(len(all_values))
        bar_width = 0.4

        # Create the plot
        plt.bar(x - bar_width / 2, values1_percentage, width=bar_width, label=f'Healthiest {n_users} users', color='blue')
        plt.bar(x + bar_width / 2, values2_percentage, width=bar_width, label=f'Unhealthiest {n_users} users', color='orange')

        # Add labels and title
        plt.xlabel(f'{var} values')
        plt.ylabel('Percentage of Occurrences')
        plt.title(f'{var} Distribution in the Healthiest and Unhealthiest {n_users} Users')
        plt.xticks(x, all_values)  # Set unique values as x-axis labels
        plt.legend()

        # Show the plot
        plt.tight_layout()
        plt.show()

    plot_2_lists(healthiest_users, unhealthiest_users)