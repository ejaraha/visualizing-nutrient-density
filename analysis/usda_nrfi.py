# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 18:10:10 2019

@author: sjara
"""
from __future__ import absolute_import, division, print_function

import pandas as pd
import numpy as np

# IMPORT products.csv, nutrients.csv, serving_size.csv
products_drop = ["data_source", "gtin_upc", "date_modified", "date_available", "ingredients_english"]
products = pd.read_csv("C:\Data\Products.csv", dtype="object").drop(labels=products_drop, axis=1)
nutrients = pd.read_csv("C:\Data\Nutrients.csv", dtype="object").drop(labels="Derivation_Code", axis=1)
serving_size = pd.read_csv("C:\Data\Serving_size.csv", dtype="object").drop(labels="Preparation_State", axis=1)

# MERGE nutrients + products = branded_plus
branded_plus = nutrients.merge(products,how="left",left_on="NDB_No", right_on="NDB_Number")
# MERGE branded_plus + serving_size = branded_plus
branded_plus = branded_plus.merge(serving_size, how="left", on="NDB_No").drop(labels="NDB_Number", axis=1)

# LAUNDER str --> float32
float_cols = ["Output_value","Serving_Size","Household_Serving_Size"]
branded_plus[float_cols] = branded_plus[float_cols].astype("float32")
# LAUNDER na  --> "" for non-numeric columns
object_cols = branded_plus.columns.drop(float_cols)
branded_plus[object_cols] = branded_plus[object_cols].fillna("", axis=1)
# LAUNDER lowercase
branded_plus.columns = [i.lower() for i in list(branded_plus.columns)]


# ADD COL: dri
## SOURCE: NIH Office of Dietary Supplements ::: Nutrient Recommendations :: Dietary Reference Intakes
##### DRI = Daily Reference Intake = umbrella term which encompasses RDA, AI, and UL
######## RDA = Rcommeneded Dietary Allowance = ~"avg daily intake sufficient for 97-98% healthy people"~
######## AI = Adequate Intake = assumption for when evidence is insufficient for RDA
######## UL = Tolerable Upper Intake Level = max intake unlikely to cause adverse effects 
########### DV = Daily Value = RDA +AI ..... (for convenice on nutrition labels)
## **added sugar and saturated fat info from FDA 2015-2020 Dietary Guidelines 2000 cal diet (not included in DRI)
## **DRI values are for averages of male/female DRIs aged 19-50
dietary_reference_intake = pd.DataFrame({"nutrient_code_usda":\
                                ["318", "401", "340",\
                                 "203", "301", "304",\
                                 "303", "291", "306",\
                                 "606", "539", "307"],\
                            "nutrient_name_dri":\
                                ["vitamin a", "vitamin c", "vitamin e",\
                                 "protein", "calcium", "magnesium",\
                                 "iron", "total fiber","potassium",\
                                 "fatty acids, total saturated", "sugars, added", "sodium"], 
                            "dri":\
                                # 0.56 mg vitE = 1 IU (avg synth and natural) # 0.3 mcg vitA = 1 IU 
                                [900/0.3,90,15/0.56,\
                                  51,1000,363,\
                                  13,32,4700,\
                                  22,50,1500],\
                             "dri_uom":\
                                 ["iu/d","mg/d","iu/d",\
                                  "g/d","mg/d","mg/d",\
                                  "mg/d","g/d","mg/d",\
                                  "g/d","g/d","mg/d"]})



branded_plus = branded_plus.merge(dietary_reference_intake, how="left", left_on="nutrient_code", right_on="nutrient_code_usda").drop(labels=["nutrient_code_usda","nutrient_name_dri"], axis=1)

# ADD COL: energy_value 
energy_df = branded_plus[["ndb_no","output_value", "output_uom"]].loc[branded_plus.nutrient_code == "208"]
energy_df.columns = ["ndb_no_energy","energy_value", "energy_uom"]
branded_plus = branded_plus.merge(energy_df, left_on = "ndb_no", right_on="ndb_no_energy", how="left")
branded_plus = branded_plus.drop(labels="ndb_no_energy", axis=1)

# ADD COLS: energy_per_serving, energy_per_serving_uom
branded_plus["energy_per_serving"] = (branded_plus.energy_value / 100)*branded_plus.serving_size
branded_plus["energy_per_serving_uom"] = 'kcal'

# ADD COL: nrn
## calculated for each nutrient in a food item
## sum of nrns for a food item = NRFI for that food item
## NRn can be calculated based on nutrient / 100 kcal OR nutrient / serving size
nrn = branded_plus.output_value / branded_plus.dri 
nrn = np.where(nrn>100,100,nrn)         # %DV is capped at 100% daily value
#branded_plus["nrn"] = nrn / branded_plus.energy_value * 100  #####per 100 kcal
branded_plus["nrn"] = (nrn / 100) * branded_plus.serving_size  ######per serving size

# DEFINE INDEX: nutrients that increase the nrfi (positive)
pos = branded_plus.nutrient_code.isin(["318", "401", "340",\
                                       "203", "301", "304",\
                                       "303", "291", "306"])

# DEFINE INDEX: nutrients that lower the nrfi (negative)
neg = branded_plus.nutrient_code.isin(["606", "539", "307"])

# CREATE DF: [[ndb_no , sum positive nrn , sum negative nrn]]
nrfi = branded_plus[["ndb_no", "nrn"]][pos].groupby(["ndb_no"], as_index=False).sum()
nrfi["nrn_neg"] = branded_plus[["ndb_no", "nrn"]][neg].groupby(["ndb_no"], as_index=False).sum().nrn
nrfi.columns=["ndb_no","nrn_pos", "nrn_neg"]

# ADD COL: nrfi
## NRFI = sum of positive and negative nrn for a food item 
nrfi["nrfi"] = nrfi.nrn_pos - nrfi.nrn_neg

# MERGE: nrfi + branded_plus = nrfi
drop_cols = ["nutrient_code", "nutrient_name","output_value", "output_uom", "dri", "dri_uom", "nrn", "energy_value", "energy_uom"]
nrfi = nrfi.merge(branded_plus.drop(labels=drop_cols, axis=1), how="left", on="ndb_no")
nrfi = nrfi.drop(labels=["nrn_pos", "nrn_neg"], axis=1)
nrfi = nrfi.drop_duplicates()
nrfi.head()

# export to csv
nrfi.to_csv("C:\\BirdEye\\Temple Learning\\Application Development for GIS\\tutorial_proj\\nrfi_ss.csv",index=False)
branded_plus.to_csv("C:\\BirdEye\\Temple Learning\\Application Development for GIS\\tutorial_proj\\branded_plus_ss.csv",index=False)
