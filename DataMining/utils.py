# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 09:28:26 2020
Last Update on Thu June 30 11:45:00 2020

@authors: clneto e msasso
"""
import numpy as np
from struct import unpack
import pandas as pd

def input_phase(message):
    """
    This function manages the phase input as a number if there is a phase or n if dont

    :param message: message text
    :return: Return the phase information that will be inputed in the dataframe row
    """
    infonum = 'info_num'
    while type(infonum) != float and infonum!= 'n':
        info = input(message)
        try:
            if info!= 'n':
                infonum = float(info)
            else:
                infonum = info
        except:
           print("Favor Digitar apenas numeros se houver fase ou n se não houve")      
    return info
 

def input_number(message):
    """
    This function manages the float number inputs created by the user

    :param message: message text
    :return: Return the information that will be inputed in the dataframe row
    """
    infonum = 'info_num'
    while type(infonum) != float:
        info = input(message)
        try:
            infonum = float(info)
        except:
           print("Favor Digitar apenas numeros")        
    return info


def input_options(question, options, error_message= None):
    """
    This function manages the optional inputs created by the user

    :param question: question text
    :param options:  List of options the have to pe choosed by the user as a list of strings
    :return: Return the information that will be inputed in the dataframe row
    """
    erm = error_message if error_message else question
    infos_string = 'not_ok'
    while infos_string != 'ok':
        info = input(question)
        if info in options:
            infos_string = 'ok'
        else:
            print(erm)
    return info


def save_exploratory_results(dict_results_row):
    """
    This function save a row with the column informations in a CSV
    
    :param dict_results_row: A list with all values to append in a dataframe
    """
    list_results_row = list(dict_results_row.values())
    try:
        exploratory_results = pd.read_csv('./exploratory_results.csv')
    except:
        exploratory_results = pd.DataFrame(columns=['Identificador_varistor', 'Polaridade','I_fuga_pre[uA]', 'Temp_terminal_pre[Celcius]', 
        'V_oper[V]', 'V_oper_nominal[V]', 'I_surto_nom[uA]', 'Fase_nom[graus]', 'Nome_Arquivo_Medidas', 'I_fuga_pos[uA]',
        'Temp_terminal_pos[Celcius]', 'Temp_ambiente_pos[Celcius]', 'V_oper_pos[V]'])
    exploratory_results = exploratory_results.append(pd.Series(list_results_row, index=exploratory_results.columns), ignore_index=True)
    exploratory_results.to_csv('./exploratory_results.csv', index=False)


def waveform_capture(ch, scope):
    """
    This function capture the wave and return a numpy array representing it

    :param time_axis_set: False to return the time axis and True to dont return it  
    :param ch: Wich chanel from the oscilopcpe is beeing measured as integer
    :param scope: the scope object
    :return: Return the wave Amplitude values and if necessary the time axis value
    """
    # Data Chanel Captures
    scope.write('DATA:SOU CH'+str(ch))
    scope.write('DATA:WIDTH 1')
    scope.write('DATA:ENC RPB')
    # Parameters Capturing
    ymult = float(scope.query('WFMPRE:YMULT?'))
    yzero = float(scope.query('WFMPRE:YZERO?'))
    yoff = float(scope.query('WFMPRE:YOFF?'))
    xincr = float(scope.query('WFMPRE:XINCR?'))
    # Data Management
    scope.write('CURVE?')
    data = scope.read_raw()
    headerlen = 2 + int(data[1])
    # header = data[:headerlen]
    ADC_wave = data[headerlen:-1]
    ADC_wave = np.array(unpack('%sB' % len(ADC_wave), ADC_wave))
    Volts = (ADC_wave - yoff) * ymult + yzero
    Time = np.arange(0, xincr * len(Volts), xincr)
    return(Time, Volts)


def get_actual_experiment():
    """
    This function manages if it will be start from a new varistor or continue measures from where it stop

    :return: the measure number and the varistor identifier
    """
    info = input("Para começar do zero digite 0, para continuar de onde parou digite 1: ")
    if info == '0':
        i = 1
        Identificador_varistor = None
    elif info == '1':
        Identificador_varistor = input_number('Qual o número identificador do varistor? ')
        try:
            exp_results = pd.read_csv('./exploratory_results.csv') 
            unique_file_measeures = exp_results['Nome_Arquivo_Medidas'].unique()
            var_name = 'varistor' + Identificador_varistor + '_sample'
            experiments = [] 
            for name in unique_file_measeures:
                if var_name in name:
                    experiments.append(int(name.split(var_name)[1].split('.csv')[0]))
            i = max(experiments)+1 if experiments else 1
        except:
            i = 1
    return i, Identificador_varistor