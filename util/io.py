#!/usr/bin/python3
"""Some useful commands for reading/writing to/from standard output
"""
import datetime
import os

def line_print(str):
    print(str + '\n-------------------------')

def get_time_string():
    return datetime.datetime.now().strftime('%H:%M:%S')

def get_datetime_filename():
    return datetime.datetime.now().strftime('%Y_%m%d_%H%M')

def query(prompt,accepted_resp = ['y','n']):
    resp = input(prompt).lower()
    while resp not in accepted_resp:
        err_str = 'Use one of ' + str(accepted_resp) + ':'
        resp = input(err_str)
    
    return resp

def check_folder(fol_name):
    if not os.path.exists(fol_name):
        os.makedirs(fol_name)