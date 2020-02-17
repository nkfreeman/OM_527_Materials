def normalize_weights_dictionary(weights_dict):
    """
    Normalizes weights provided as values in passed weight_dict so that 
    the sum of the weights equals 1.

    Arguments
    ----------    
    weights_dict: a dictionary containing the columns to be included in the weighted sum 
    as keys, and the associated values as values
    
    Returns
    ------
    A copy of weights_dict that has been normalized
           
    """   
    
    return {key: value/sum(weights_dict.values()) for key, value in weights_dict.items()}


def normalize_array(array):
    """
    Normalizes values in array or list.

    Arguments
    ----------    
    array: a python list, pandas series, or numpy array containing values to normalize.
    
    Returns
    ------
    A copy of the array that has been normalized
           
    """   
    from sklearn import preprocessing
    import numpy as np
    import pandas as pd
    
    temp_array = np.array(array)
    temp_array = temp_array.reshape(-1,1)
    return preprocessing.MinMaxScaler().fit_transform(temp_array)


def compute_weighted_sum(data, weights_dict):
    """
    Computes weighted sum for specified columns

    Arguments
    ----------
    data : a pandas DataFrame object that contains the columns to be weighted and the
    normalized scores for each alternative
    
    weights_dict: a dictionary containing the columns to be included in the weighted sum as keys,
    and the associated values as values
    
    Returns
    ------
    A list specifying the weighted sum calculations
           
    """   
    import pandas as pd

    temp = pd.Series(index = data.index, data = 0)

    for key, weight in weights_dict.items():
        if key in data.columns:
            temp += data[key]*weight
        else:
            continue
            
    return temp.tolist()


def compute_weighted_product(data, weights_dict):
    """
    Computes weighted product for specified columns

    Arguments
    ----------
    data : a pandas DataFrame object that contains the columns to be weighted and the
    normalized scores for each alternative
    
    weights_dict: a dictionary containing the columns to be included in the weighted product as keys,
    and the associated values as values
    
    Returns
    ------
    A list specifying the weighted product calculations
           
    """   
    import pandas as pd
    
    temp = pd.Series(index = data.index, data = 1)
    for key, weight in weights_dict.items():
        if key in data.columns:
            temp *= (data[key]**weight)
        else:
            continue
            
    return temp.tolist()


def compute_TOPSIS(data, weights_dict):
    """
    Computes TOPSIS score for specified columns

    Arguments
    ----------
    data : a pandas DataFrame object that contains the columns to be weighted and the
    normalized scores for each alternative
    
    weights_dict: a dictionary containing the columns to be included in the weighted product as keys,
    and the associated values as values
    
    Returns
    ------
    A list specifying the TOPSIS calculations
           
    """   
    import numpy as np
    import pandas as pd
    
    #Step 0 
    temp_df = data.copy()
    criteria_columns = list(weights_dict.keys())
    criteria_columns = [col for col in criteria_columns if col in temp_df.columns]

    #Step 1
    evaluation_matrix = temp_df[criteria_columns].values

    #Step 2
    squared_evaluation_matrix = evaluation_matrix**2
    normalized_evaluation_matrix = evaluation_matrix/np.sqrt(np.sum(squared_evaluation_matrix, axis=0))

    #Step 3
    weight_values = list(weights_dict.values())
    weight_values = np.array(weight_values)
    weight_values = weight_values/weight_values.sum()
    weighted_matrix = normalized_evaluation_matrix * weight_values

    #Step 4
    PIS = np.max(weighted_matrix, axis=0)
    NIS = np.min(weighted_matrix, axis=0)

    #Step 5
    intermediate = (weighted_matrix - PIS)**2
    Dev_Best = np.sqrt(intermediate.sum(axis = 1))

    intermediate = (weighted_matrix - NIS)**2
    Dev_Worst = np.sqrt(intermediate.sum(axis = 1))

    #Step 6
    Closeness = Dev_Worst/(Dev_Best+Dev_Worst)

    #Step 7
    return Closeness.tolist()


def create_ahp_rank_matrix_from_gui(criteria):
    '''
    This function is designed to create a ranking matrix for
    applying the analytics heirarchy process (AHP) using user
    input obtained via a simple graphical user interface (GUI)
    
    Arguments      
    criteria: a list object that specifies the criteria
    
    Returns
    ------
    a Numpy array with the rankings
    
    '''

    import tkinter as tk
    from tkinter import ttk
    import tkinter.font as tkFont
    import pandas as pd
    import numpy as np

    box_values = ['extremely more preferable', 
                  'very strongly more preferable',
                  'strongly more preferable',
                  'moderately more preferable',
                  'equally preferable',
                  'moderately less preferable',
                  'strongly less preferable',
                  'very strongly less preferable',
                  'extremely less preferable']

    comparison_scores = {}

    def close_root(): 
        root.destroy()

    def onFrameConfigure(canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))

    # --- main ---

    root = tk.Tk()
    #text = tk.Text(root)
    root.title('AHP Ranking')
    sizex = 1100
    sizey = 600
    posx  = 100
    posy  = 100
    root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))

    canvas = tk.Canvas(root, borderwidth=0)
    frame = tk.Frame(canvas,)
    vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)


    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((4,4), window=frame, anchor="nw")

    frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

    default_font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(size = 14)
    frame.option_add("*Font", default_font)

    row_counter = 0
    for first_index in range(len(criteria)):
        for second_index in range(first_index+1, len(criteria)):
            ttk.Label(frame, 
                  text = f'How do you rate {criteria[first_index]} with respect to {criteria[second_index]}?',
                  justify = 'left',).grid(column=0, row=row_counter, sticky='W', padx=10, pady=10)

            # combobox working in new way with dictionary
            comparison_scores[(criteria[first_index], criteria[second_index])] = tk.StringVar()
            mybox = ttk.Combobox(frame, 
                                 width=26, 
                                 justify ='left', 
                                 textvariable = comparison_scores[(criteria[first_index], criteria[second_index])])
            mybox['values'] = box_values
            mybox.grid(column=1, row=row_counter, padx=10, pady = 10)
            mybox.set(f'equally preferable')
            row_counter += 1

    button = ttk.Button(frame, text = 'Submit', command = close_root)
    button.grid(column=1, row=row_counter, padx=5)

    hsb = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=hsb.set)
    hsb.grid(row=(row_counter + 1))

    root.mainloop()

    A_list = []
    B_list = []
    val_list = []
    for current_tuple in comparison_scores.keys():
        A_list.append(current_tuple[0])
        B_list.append(current_tuple[1])
        val_list.append(comparison_scores[current_tuple].get())

    mapper = {'extremely more preferable' : 9.0,
             'very strongly more preferable' : 7.0,
             'strongly more preferable' : 5.0,
             'moderately more preferable' : 3.0,
             'equally preferable' : 1.0,
             'moderately less preferable' : 0.333,
             'strongly less preferable' : 0.2,
             'very strongly less preferable' : 0.143,
             'extremely less preferable' : 0.111,}

    data = pd.DataFrame.from_dict({'Criterion A':A_list,
                                 'Criterion B':B_list,
                                 'Score':val_list,})
    data['Score'] = data['Score'].map(mapper)

    my_array = np.ones((len(criteria), len(criteria)))

    for i in range(len(criteria)-1):
        for j in range(i+1, len(criteria)):
            val = data.loc[(data['Criterion A']==criteria[i]) & (data['Criterion B']==criteria[j]),'Score'].values
            my_array[i, j] = val
            my_array[j, i] = 1.0/val

    
    weight_dictionary = ahp_weight_determination(criteria, my_array)
    
    return weight_dictionary



def ahp_weight_determination(criteria, criteria_scores):
    '''
    This function is designed to read the ranking matrix computed by the 
    create_rank_matrix_from_comparison_table function and compute the priority
    vector that results from application of the analytics heirarchy process (AHP)
    
    Arguments      
    criteria: a list object that specifies the criteria
    
    criteria_scores: a two-dimensional Numpy array specifying the criteria rankings.
    Note that if n criteria are specified, the shape of the criteria_scores array
    should be n x n
    
    Returns
    ------
    a Numpy array with the rankings
    
    '''
    
    import numpy as np
    
    if criteria_scores.shape == (len(criteria),len(criteria)): 
        criteria_column_sums = np.sum(criteria_scores,axis=0)
        criteria_scores_divided_by_sums = criteria_scores/criteria_column_sums
        criteria_priority_vector = np.average(criteria_scores_divided_by_sums,axis=1)
        
        criteria_max_eigenvalue = np.inner(criteria_priority_vector,criteria_column_sums)
        criteria_CI = (criteria_max_eigenvalue - len(criteria))/(len(criteria)-1)
        RI = [0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49] 
        criteria_CR = criteria_CI/RI[len(criteria)]
    
        if(criteria_CR < 0.10):
            pass
        else:
            print(f'The consistency ratio is {np.round(criteria_CR, 3)}. Thus, the specified preferences are not consistent!\n')
            
        weight_dictionary = {}
        for index, current_criteria in enumerate(criteria):
            weight_dictionary[current_criteria] = criteria_priority_vector[index]
                
        return weight_dictionary
    
    else:
        print('The dimensions of the criteria_scores array do not match the number of specified criteria')

        

def robust_ranking(self,
                   index_column,
                   perturbation_range = 0.1,
                   top_values = 5,
                   perturbations = 100,
                   random_seed = 0,
                   show_plot = True):
    
    '''
    Performs a robust ranking procedure that identfies the proportion of times where
    the available alternatives appear as top choice under weight perturbations in the
    range defined by the perturbation_range.

    Parameters
    ----------
    data : a pandas DataFrame object that contains the specified columns
        
    weights_dict: a dictionary containing the columns to be included in the weighted product as keys,
    and the associated values as values
    
    index_column: a string specifying the column of alternatives
    
    show_plot: True or False to denote whether or not a plot of
    the robust rankings should be produced
        
    perturbations: an integer specifying the number of times to
        perturb the weights
    
    top_values: specifies the number of alternatives to keep from each ranking (highest ranked scores kept)
    
    perturbation_range: The perturbation range to consider (expressed as a proportion)    \
    
    random_seed: float specifying seed for random number generator
    

    Yields
    ------
    a DataFrame indicating the proportion of times each alternative appears in top ranking
    '''
    import numpy as np
    import pandas as pd

    np.random.seed(random_seed)

    criteria = list(self.weights_dict.keys())
    starting_weights = np.array(list(self.weights_dict.values()))

    a = np.zeros(shape = (len(self.data.index), 4))
    counts_df = pd.DataFrame(a, columns=[index_column, 'WS', 'WP', 'TOPSIS'])
    counts_df[index_column] = self.data[index_column]

    for perturbation in range(perturbations):
        perturbation_vector = 1.0 + np.random.uniform(low = -1.0*perturbation_range,
                                                        high = perturbation_range,
                                                        size= len(starting_weights))

        perturbed_weights = perturbation_vector * starting_weights
        perturbed_weights = list(perturbed_weights/perturbed_weights.sum())
        perturbed_weights_dict = dict(zip(criteria, perturbed_weights))

        a = np.zeros(shape = (len(self.data.index), 4))
        df = pd.DataFrame(a, columns=[index_column, 'WS', 'WP', 'TOPSIS'])
        df[index_column] = self.data[index_column]
        df['WS'] = compute_weighted_sum(self.data, perturbed_weights_dict)
        df['WP'] = compute_weighted_product(self.data, perturbed_weights_dict)
        df['TOPSIS'] = compute_TOPSIS(self.data, perturbed_weights_dict)

        WS_top = df.nlargest(top_values, 'WS')[index_column].tolist()
        WP_top = df.nlargest(top_values, 'WP')[index_column].tolist()
        TOPSIS_top = df.nlargest(top_values, 'TOPSIS')[index_column].tolist()

        counts_df.loc[counts_df[index_column].isin(WS_top), 'WS'] += 1
        counts_df.loc[counts_df[index_column].isin(WP_top), 'WP'] += 1
        counts_df.loc[counts_df[index_column].isin(TOPSIS_top), 'TOPSIS'] += 1

    counts_df[['WS', 'WP', 'TOPSIS']] = counts_df[['WS', 'WP', 'TOPSIS']]/perturbations
    counts_df = counts_df.sort_values(['WS', 'WP', 'TOPSIS'], ascending = False)
    mask = counts_df[['WS', 'WP', 'TOPSIS']].sum(axis = 1) > 0
    counts_df = counts_df[mask]

    if show_plot:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plot_df = counts_df.melt(id_vars = 'Company Name')

        fig, ax = plt.subplots(1,1, figsize = (10, 6))
        sns.barplot(x = 'Company Name',
                    y = 'value',
                    hue = 'variable',
                    data = plot_df,
                    edgecolor = 'k'
                   )

        ax.tick_params(axis = 'x', rotation = 30, labelsize = 12)
        ax.set_xticklabels(ax.get_xticklabels(), ha = 'right')
        ax.tick_params(axis = 'y', labelsize = 12)
        ax.set_ylabel('Proportion', fontsize = 14)
        
        handles, labels = ax.get_legend_handles_labels()
        lgd = ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(1.1, 0.5))

        plt.show()
       
    return counts_df
        

class mcdm_instance():
    '''
    A class for a multi-criteria decision-making instance. The class accepts a 
    DataFrame (df) that should include columns for each ranking attribute and rows 
    for each alternative. The scores for each ranking attribute should be normalized
    and in a "high is better" format. The class also requires a dictionary of weights
    (weights_dict). The dictionary keys specify columns in the data that will be used
    to evaluate alternatives. Any normalization of the weights should be done before
    constructing the class.
    '''
    
    def __init__(self, 
                 df, 
                 weights_dict):
        
        self.data = df
        self.weights_dict = weights_dict
        
        self.data['WS'] = compute_weighted_sum(self.data, self.weights_dict)
        self.data['WP'] = compute_weighted_product(self.data, self.weights_dict)
        self.data['TOPSIS'] = compute_TOPSIS(self.data, self.weights_dict)  
        
    perform_robust_ranking = robust_ranking