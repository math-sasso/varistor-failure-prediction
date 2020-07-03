# varistor-failure-prediction

This software is responsable for getting oscilocepe data from its terminal as the proces of data mining and on the next step create the IA algorythim.

## Installation
* It is necessary to install [NI-VISA ](https://www.ni.com/pt-br/support/downloads/drivers/download.ni-visa.html#346210) in you computer
* You should install the requirements in requirements.txt with the command:
```bash
pip install -r requirements.txt
```
* It is mandatory to create the folder Measures

## Usage
There as some steps that have to be follwed:

1 . Connect the osciloscope measuring the **Voltage** on the first channel and the **Current** on the second chanel 

2. Run the file main_two_channels_capture.py

3.  Check the main table will be saved with the name ```exploratory_results.csv``` all the inputed files with the column ```Nome_Arquivo_Medidas``` that will be the referenc to each measure stored on the foldeer Measures.
