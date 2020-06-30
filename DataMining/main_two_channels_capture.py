# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 09:28:26 2020
Last Update on Thu June 30 11:45:00 2020

@authors: clneto e msasso
"""

import numpy as np
from struct import unpack
import matplotlib.pyplot as plt
import time
import pandas as pd
import serial
import datetime
from pyvisa.highlevel import ResourceManager
import sys
from utils import input_number, input_options, save_exploratory_results, waveform_capture, get_actual_experiment

'''
TODO: Comando para apertar o botão de Run.
'''

#COM_PORT_TEMPERATURE = 'COM6'
COM_PORT_TEMPERATURE = ''
      

def pre_experimemnt_information(dict_results_row,Identificador_varistor=None):
    
    """
    This function returns the updated dict with the pre experiment information

    :param dict_results_row: in this moment it is an empy dict
    :param Identificador_varistor:  String that identifies the varistor. It can be None if it is the first measure on the varistor
    :return: Return the wave Amplitude values and if necessary the time axis value
    """
    
    # Identificador_varistor
    if Identificador_varistor == None:
        Identificador_varistor = input_number('Qual o número identificador do varistor? ')
    dict_results_row['Identificador_varistor'] = Identificador_varistor
    
    # Polaridade
    Polaridade = input_options(question = 'Qual a polaridade? ',options=['p','n'],error_message ='Favor digitar p para positivo ou n para negativo')
    dict_results_row['Polaridade'] = Polaridade
    
    # I_fuga_pre
    I_fuga_pre = input_number('Qual a corrente de fuga pré experimento em [mA]? ')
    dict_results_row['I_fuga_pre'] = I_fuga_pre
    
    # Temp_terminal_pre
    if COM_PORT_TEMPERATURE:
        Temp_terminal_pre = temperature()
    else:
        Temp_terminal_pre = input_number('Qual a temperatura do terminal de fuga pré experimento em [Celcius]? ')
    dict_results_row['Temp_terminal_pre'] = Temp_terminal_pre
    
    # V_oper
    V_oper = input_number('Qual a tensão pré operação em [V]?')
    dict_results_row['V_oper'] = V_oper
    
    # V_oper_nominal
    V_oper_nominal = input_number('Qual a tensão de operação nominal em [V]? ')
    dict_results_row['V_oper_nominal'] = V_oper_nominal
    
    # I_surto_nom
    I_surto_nom = input_number('Qual a corrente de surto nominal em [mA]? ')
    dict_results_row['I_surto_nom'] = I_surto_nom
    
    Fase_nom = input_number('Qual a fase nominal em [graus]? ')
    dict_results_row['Fase_nom'] = Fase_nom
    

    
    return dict_results_row, Identificador_varistor
    
def pos_experimemnt_information(dict_results_row):
    """
    This function returns the updated dcit with the pos experiment information

    :param dict_results_row: dict with pre experiment and experiment name
    :return: Updated dict with the pos experiment information
    """
    
    # I_fuga_pos
    I_fuga_pos = input_number('Qual a corrente de fuga pós experimento em [mA]? ')
    dict_results_row['I_fuga_pos'] = I_fuga_pos
    
    # Temp_terminal_pos
    Temp_terminal_pos = input_number('Qual a temperatura do terminal de fuga pós experimento em [Celcius]? ')
    dict_results_row['Temp_terminal_pos'] = Temp_terminal_pos
    
    # Temp_ambiente_pos
    if COM_PORT_TEMPERATURE:
        Temp_ambiente_pos= temperature()
    else:
        Temp_ambiente_pos = input_number('Qual a temperatura ambiente em [Celcius]? ')
    dict_results_row['Temp_ambiente_pos'] = Temp_ambiente_pos
    
    # V_oper_pos
    V_oper_pos = input_number('Qual a tensão pós operação em [V]? ')
    dict_results_row['V_oper_pos'] = V_oper_pos
    
    return dict_results_row
        


def temperature():
    """
    This function returns the temperatura from the serial port

    :return: Gets the temperature measured
    """
    
    ser = serial.Serial(port=COM_PORT_TEMPERATURE)
    temp = ser.read(16)
    temp = str(temp)
    offset = temp.find('b')
    temp = temp[(offset+2):(offset+7)]
    temp = float(temp)
    return(temp)


if __name__ == '__main__':

    rm = ResourceManager()
    try:
        scope = rm.get_instrument(rm.list_resources()[0])#desta maneira não precisamos nos preocupar com o ID do equipamento 
    except:
        print("Verifique se o osciloscópio est-a conectado")
     
    
    i,Identificador_varistor  = get_actual_experiment()
    preceed_experiment = True
    encerrar = False
    while(preceed_experiment):
        #acontece apenas se o usuário digitar q        
        proceed_varistor = True
        while(proceed_varistor):
        
            dict_results_row= {}
            dict_results_row ,Identificador_varistor =  pre_experimemnt_information(dict_results_row) if (i == 1 and not Identificador_varistor) else pre_experimemnt_information(dict_results_row,Identificador_varistor)
           
            #/* Set up conditional acquisition */
            scope.write("ACQUIRE:STATE OFF")
            scope.write("SELECT:CH1 ON")
            scope.write("ACQUIRE:MODE SAMPLE")
            scope.write("ACQUIRE:STOPAFTER SEQUENCE")
            #/* Acquire waveform data */
            scope.write("ACQUIRE:STATE ON")
            time.sleep(1)
            while scope.query("TRIGGER:STATE?") != 'SAVE\n':
                time.sleep(1)
                print('Aguardando conexão...')
                print(scope.query("TRIGGER:STATE?"))# A outra opção é READY
            if scope.query("TRIGGER:STATE?") == 'SAVE\n':
                time.sleep(1)
                try:
                    print('Fluxo normal')
                    Time,Amplitude = waveform_capture(False,1,scope)
                    time.sleep(2)
                    Ensaio = pd.DataFrame({'Time':Time})
                    Ensaio['Time_Stamp'] = datetime.datetime.now()
                    Ensaio['V_grampeamento[V]'] = Amplitude  * 250
                    #fig, ax = plt.subplots()
                    #ax.plot(Time,Amplitude)
                    #plt.show()
                    Amplitude = waveform_capture(True,2,scope)
                    time.sleep(2)
                    Ensaio['I_surto_medida[mA]'] = Amplitude * 40
                    Ensaio['Power[W]'] = Ensaio['V_grampeamento[V]']*Ensaio['I_surto_medida[mA]']
                    Ensaio['Energy[Joules]'] = Ensaio['Power[W]'] * 6.4e-8
                    Ensaio.to_csv(f"./Measures/{dict_results_row['Identificador_varistor']}_sample{str(i)}.csv",index=False)
                    
                    dict_results_row['Nome_Arquivo_Medidas'] = f"varistor{dict_results_row['Identificador_varistor']}_sample{str(i)}.csv"
                    #fig, ax = plt.subplots()
                    #ax.plot(Time,Amplitude)
                    #plt.show()
                except:
                    print('Fluxo sem Time')
                    Amplitude = waveform_capture(True,1,scope)
                    time.sleep(2)
                    Ensaio = pd.DataFrame()
                    Ensaio['Time_Stamp'] = datetime.datetime.now()
                    Ensaio['V_grampeamento[V]'] = Amplitude
                    Amplitude = waveform_capture(True,2,scope)
                    time.sleep(2)
                    Ensaio['I_surto_medida[mA]'] = Amplitude* 40
                    time.sleep(1)
              
                    if np.mod(i,2) == 0: # pergunta o porquê dissi
                        Ensaio['Power[W]'] = Ensaio['V_grampeamento[V]']*Ensaio['I_surto_medida[mA]']
                        Ensaio['Energy[Joules]'] = Ensaio['Power[W]'] * 6.4e-8
                        Ensaio.to_csv(f"./Measures/{dict_results_row['Identificador_varistor']}_sample{str(i)}.csv",index=False)
                    
                    dict_results_row['Nome_Arquivo_Medidas'] = f"varistor{dict_results_row['Identificador_varistor']}_sample{str(i)}.csv"
                      

                print('Dados colhidos com sucesso!')
            
            dict_results_row = pos_experimemnt_information(dict_results_row) 
            save_exploratory_results(dict_results_row)
            info = input_options(question ="Favor digitar c para continuar com o mesmo varistor ou n para ir ao próximo varistor ou q para sair: ",options=['c','n','q'])
            
            if info == 'c':
                i +=1
            elif info == 'n':
                i = 1
                proceed_varistor = False
            else:
                sys.exit('Program Finished')

            
      
                
    

