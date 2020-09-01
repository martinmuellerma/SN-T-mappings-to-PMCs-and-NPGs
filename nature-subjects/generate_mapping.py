# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime

def load_datasets(nat_file, snt_file):
    # nature subjects
    nat = pd.read_excel(
        nat_file,
        usecols=['Code', 'Subject name', 'Alternative label(s)']
    )[['Code', 'Subject name', 'Alternative label(s)']]
    # sn-t
    snt = pd.read_excel(
        snt_file,
        usecols=['Subject ID', 'subject-name', 'Synonyms']
    )[['Subject ID', 'subject-name', 'Synonyms']]
    return nat, snt

def transform_datasets(nat, snt):
    # nature subjects
    nat = nat.drop_duplicates()
    nat.columns = ['nature_code', 'nature_subject_name', 'nature_synonyms']
    nat.loc[:,'nature_subject_name'] = nat['nature_subject_name'].str.strip().str.lower()
    nat.loc[:,'nature_synonyms'] = nat['nature_synonyms'].str.strip().str.lower()
    # sn-t
    snt = snt.drop_duplicates()
    snt.columns = ['snt_id', 'snt_subject_name', 'snt_synonyms']
    snt.loc[:,'snt_subject_name'] = snt['snt_subject_name'].str.strip().str.lower()
    snt.loc[:,'snt_synonyms'] = snt['snt_synonyms'].str.strip().str.lower()
    return nat, snt

def generate_and_direct_match(nat, snt):
    df = pd.merge(nat, snt, how='left', left_on='nature_subject_name', right_on='snt_subject_name')
    df.loc[~df['snt_id'].isna(),'match_type'] = 'direct'
    return df

def label_synonym_match(nat, snt, df):
    for i in df[df['match_type'] != 'direct'].index:
        A = [x.strip() for x in df.at[i, 'nature_subject_name'].split(',')]
        A_plus = []
        if str(df.at[i, 'nature_synonyms']) != 'nan':
            A_plus = A + [x.strip() for x in df.at[i, 'nature_synonyms'].split(',')]
        for j in snt.index:
            match = False
            B = [x.strip() for x in snt.at[j, 'snt_subject_name'].split(',')]
            B_plus = []
            if str(snt.at[j, 'snt_synonyms']) != 'nan':
                B_plus = B + [x.strip() for x in snt.at[j, 'snt_synonyms'].split(',')]
            if bool(list(set(A) & set(B_plus))) | bool(list(set(A_plus) & set(B))) | bool(list(set(A) & set(B))):
                df.loc[i, 'snt_id'] = snt.at[j, 'snt_id']
                df.loc[i, 'snt_subject_name'] = snt.at[j, 'snt_subject_name']
                df.loc[i, 'snt_synonyms'] = snt.at[j, 'snt_synonyms']
                df.loc[i, 'match_type'] = 'label-synonym'
                break
    return df

def synonym_synonym_match(nat, snt, df):
    for i in df[~df['match_type'].isin(['direct', 'label-synonym'])].index:
        if str(df.at[i, 'nature_synonyms']) != 'nan':
            A = [x.strip() for x in df.at[i, 'nature_synonyms'].split(',')]
            for j in snt.index:
                if str(snt.at[j, 'snt_synonyms']) != 'nan':
                    B = [x.strip() for x in snt.at[j, 'snt_synonyms'].split(',')]
                    if list(set(A) & set(B)):
                        df.loc[i, 'snt_id'] = snt.at[j, 'snt_id']
                        df.loc[i, 'snt_subject_name'] = snt.at[j, 'snt_subject_name']
                        df.loc[i, 'snt_synonyms'] = snt.at[j, 'snt_synonyms']
                        df.loc[i, 'match_type'] = 'synonym-synonym'
                        break
    return df

def save_file(df, filename):
    sheetname = datetime.datetime.strftime(datetime.date.today(), format="As of %Y-%m-%d")
    df.to_excel(filename, index=False, sheet_name=sheetname)

def main():
    nat, snt = load_datasets("Nature Subjects Ontology-March-2020.xlsx", "ontology_2020-05-29_09-00-35.xlsx")
    nat, snt = transform_datasets(nat, snt)
    df = generate_and_direct_match(nat, snt)
    df = label_synonym_match(nat, snt, df)
    df = synonym_synonym_match(nat, snt, df)
    save_file(df, "nature_subjects_to_snt(test).xlsx")

if __name__ == "__main__":
    main()
