#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 14:04:58 2025

@author: md.moshiurrahmantushar
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 2:322:06 2025

@author: Tushar
"""

import numpy as np
import pandas as pd
import copy
import lhs
import math
import matplotlib.pyplot as plt

# specity percentiles to use when extracting mid, low, and high results from uncertainty analysis
output_perc_mid = 50
output_perc_low = 5
output_perc_high = 95


# general parameters - import spreadsheet tabs as dataframes
general_assumptions = pd.read_excel('assumptions.xlsx', sheet_name = 'General', index_col = 'Parameter')
design_assumptions = pd.read_excel('assumptions.xlsx', sheet_name = 'design', index_col='Parameter')
LCA_assumptions = pd.read_excel('assumptions.xlsx', sheet_name = 'LCA', index_col='Parameter')

# number of Monte Carlo runs
n_samples = int(general_assumptions.loc['n_samples','expected'])

# create empty datasets to eventually store data for sensitivity analysis (Spearman's coefficients)
correlation_distributions = np.full((n_samples, n_samples), np.nan)
correlation_parameters = np.full((n_samples, 1), np.nan)
correlation_parameters = correlation_parameters.tolist()

# general inputs
discount_rate, correlation_distributions, correlation_parameters = lhs.lhs_distribution(general_assumptions.loc['discount_rate'], correlation_distributions, correlation_parameters, n_samples)
analysis_period, correlation_distributions, correlation_parameters  = lhs.lhs_distribution(general_assumptions.loc['analysis_period'],correlation_distributions, correlation_parameters, n_samples)
tax_rate, correlation_distributions, correlation_parameters = lhs.lhs_distribution(general_assumptions.loc['tax_rate'], correlation_distributions, correlation_parameters, n_samples)


# LCA inputs (includes factors for all TRACI impact categories)
stainless_steel_LCA = np.reshape(LCA_assumptions.loc['stainless_steel',:].iloc[2:].to_numpy(dtype=float), (1,-1))
concrete_LCA = np.reshape(LCA_assumptions.loc['concrete',:].iloc[2:].to_numpy(dtype=float), (1,-1))

P66614_Cl_LCA = np.reshape(LCA_assumptions.loc['P66614_Cl_LCA',:].iloc[2:].to_numpy(dtype=float), (1,-1))
acetone_LCA = np.reshape(LCA_assumptions.loc['acetone_LCA',:].iloc[2:].to_numpy(dtype=float), (1,-1))
H2O2_LCA = np.reshape(LCA_assumptions.loc['H2O2_LCA',:].iloc[2:].to_numpy(dtype=float), (1,-1))
HCL_LCA = np.reshape(LCA_assumptions.loc['HCL_LCA',:].iloc[2:].to_numpy(dtype=float), (1,-1))
electricity_LCA = np.reshape(LCA_assumptions.loc['electricity',:].iloc[2:].to_numpy(dtype=float), (1,-1))
NaOH_LCA = np.reshape(LCA_assumptions.loc['NaOH_LCA',:].iloc[2:].to_numpy(dtype=float), (1,-1))


steel_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['steel_fraction'], correlation_distributions, correlation_parameters, n_samples)
concrete_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['concrete_fraction'], correlation_distributions, correlation_parameters, n_samples)
electricity_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['electricity_cost'], correlation_distributions, correlation_parameters, n_samples)


# Hot plate rated power
ptfe_throughput_t_per_year, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['ptfe_throughput_t_per_year'],correlation_distributions,correlation_parameters,n_samples)
hotplate_power, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_power'],correlation_distributions,correlation_parameters,n_samples)
hotplate_max_temperature, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_max_temperature'],correlation_distributions,correlation_parameters,n_samples)
hotplate_weight, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_weight'],correlation_distributions,correlation_parameters,n_samples)

# Times
time_100C, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['time_100C'],correlation_distributions,correlation_parameters, n_samples)

#Synthesis of [BMIm][Cl]
P66614_Cl_amount, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['P66614_Cl_amount'], correlation_distributions, correlation_parameters, n_samples)
HCL_amount, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['HCL_amount'], correlation_distributions, correlation_parameters, n_samples)
H2O2_amount, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['H2O2_amount'], correlation_distributions, correlation_parameters, n_samples)
acetone_amount, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['acetone_amount'], correlation_distributions, correlation_parameters, n_samples)
NaOH_amount, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['NaOH_amount'], correlation_distributions, correlation_parameters, n_samples)


density_P66614_Cl, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['density_P66614_Cl'], correlation_distributions, correlation_parameters, n_samples)
density_HCL, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['density_HCL'], correlation_distributions, correlation_parameters, n_samples)
density_H2O2, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['density_H2O2'], correlation_distributions, correlation_parameters, n_samples)
density_acetone, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['density_acetone'], correlation_distributions, correlation_parameters, n_samples)
density_NaOH, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['density_NaOH'], correlation_distributions, correlation_parameters, n_samples)



Iron_Fe, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['Iron_Fe'], correlation_distributions, correlation_parameters, n_samples)
PTFE_mass, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['PTFE_mass'], correlation_distributions, correlation_parameters, n_samples)

reuse_cycles, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['reuse_cycles'], correlation_distributions, correlation_parameters, n_samples)
recovery_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['recovery_fraction'], correlation_distributions, correlation_parameters, n_samples)
reconditioning_cost_per_cycle_USD, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['reconditioning_cost_per_cycle_USD'], correlation_distributions, correlation_parameters, n_samples)

P66614_Cl_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['P66614_Cl_cost'], correlation_distributions, correlation_parameters, n_samples)
HCL_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['HCL_cost'], correlation_distributions, correlation_parameters, n_samples)
H2O2_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['H2O2_cost'], correlation_distributions, correlation_parameters, n_samples)
acetone_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['acetone_cost'], correlation_distributions, correlation_parameters, n_samples)
hotplate_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_cost'], correlation_distributions, correlation_parameters, n_samples)
NaOH_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['NaOH_cost'], correlation_distributions, correlation_parameters, n_samples)

# capture only sampled inputs for sensitivity
def _is_sample_vec(x):
    return isinstance(x, np.ndarray) and x.ndim in (1, 2) and x.shape[0] == n_samples and (x.ndim == 1 or x.shape[1] == 1)

inputs_for_sensitivity = {
    name: np.ravel(val)
    for name, val in locals().items()
    if _is_sample_vec(val)
}
input_name_order = list(inputs_for_sensitivity.keys())  


#%%

cost_P66614_Cl = []
impacts_P66614_Cl = []

# masses from sampled volumes
mass_P66614_Cl = P66614_Cl_amount * density_P66614_Cl #gm
mass_HCL = HCL_amount * density_HCL #gm
mass_H2O2 = H2O2_amount * density_H2O2 #gm
mass_acetone = acetone_amount * density_acetone #gm
mass_NaOH = NaOH_amount * density_NaOH #gm

# total reagents prepared
mass_reagent_prepared = (mass_P66614_Cl + mass_HCL + mass_H2O2)

# %% Cost inputs for P666614_CL step (all results in USD)
total_cost_P66614_Cl = mass_P66614_Cl * P66614_Cl_cost / 1000.0 #USD
total_cost_HCL = mass_HCL * HCL_cost / 1000.0 #USD
total_cost_H2O2 = mass_H2O2 * H2O2_cost / 1000.0 #USD
total_cost_acetone = mass_acetone * acetone_cost / 1000.0 #USD
total_cost_NaOH = mass_NaOH * NaOH_cost / 1000.0 #USD

batch_cost_P66614_CL_USD = (total_cost_P66614_Cl + total_cost_HCL + total_cost_H2O2)

# %% helpers
eps = 1e-12
def col(x):
    return np.asarray(x).reshape(-1, 1)

reuse_cycles = col(reuse_cycles)                               # (10000,1)
recovery_fraction = col(recovery_fraction)                     # (10000,1)
reconditioning_cost_per_cycle_USD = col(reconditioning_cost_per_cycle_USD)  # (10000,1)

# %% Guards and unit setup
reuse_cycles = np.maximum(reuse_cycles, 1)
recovery_fraction = np.clip(recovery_fraction, 0.0, 1.0)

# P66614_Cl inventory used to treat PTFE
mass_reagent_used_kg = col(np.maximum(mass_reagent_prepared / 1000.0, eps))           # (10000,1) if target_mass_P66614_Cl is scalar
PTFE_mass_kg     = col(np.maximum(PTFE_mass / 1000.0, eps))                 # (10000,1)

# %% Reuse accounting
total_PTFE_kg = PTFE_mass_kg * reuse_cycles
initial_inventory_kg = mass_reagent_used_kg

# Makeup mass needed over all cycles to keep inventory constant
recovered_over_cycles = recovery_fraction ** reuse_cycles
makeup_needed_kg = initial_inventory_kg * np.subtract(1.0, recovered_over_cycles)

# %% Costing
#
batch_cost_P66614_CL_USD = col(batch_cost_P66614_CL_USD)  # (10000,1) or scalar

cost_per_kg_P666614_Cl = batch_cost_P66614_CL_USD / np.maximum(initial_inventory_kg, eps)

# Total spend across cycles
total_P66614_Cl_cost_USD = (
    batch_cost_P66614_CL_USD
    + cost_per_kg_P666614_Cl * makeup_needed_kg
    + reconditioning_cost_per_cycle_USD * reuse_cycles
)

# %% Energy
E_100C_kWh  = (hotplate_power * (50  / hotplate_max_temperature)) * time_100C  / 1000

energy_demand = E_100C_kWh
energy_cost_kg = (energy_demand * electricity_cost) / np.maximum(total_PTFE_kg, eps)  # USD per kg PTFE
energy_cost = energy_cost_kg #USD/kg
# %% Output OM style cost per kg PTFE
cost_per_kg_PTFE_P666614_Cl_reuse = total_P66614_Cl_cost_USD/ np.maximum(total_PTFE_kg, eps)
OM_cost = cost_per_kg_PTFE_P666614_Cl_reuse + total_cost_acetone/np.maximum(total_PTFE_kg, eps) + total_cost_NaOH/np.maximum(total_PTFE_kg, eps)

# %% Capital cost (ensure throughput is column vector)
ptfe_throughput_t_per_year = col(ptfe_throughput_t_per_year)  # (10000,1) or scalar expanded

hotplate_capital_annual = hotplate_cost * ((discount_rate * (1+discount_rate)**analysis_period)
                                      / ((1+discount_rate)**analysis_period - 1))

capital_cost = (hotplate_capital_annual / ptfe_throughput_t_per_year)/1000

total_cost = capital_cost + OM_cost + energy_cost


#%% LCA
steel_hotplate_kg = hotplate_weight * steel_fraction
concrete_hotplate_kg = hotplate_weight * concrete_fraction

hotplate_construction_LCA = (steel_hotplate_kg * stainless_steel_LCA + concrete_hotplate_kg * concrete_LCA)
hotplate_construction_LCA_annual = hotplate_construction_LCA / analysis_period

total_impacts_capital = (hotplate_construction_LCA_annual / ptfe_throughput_t_per_year)/1000 #LCA/kg



hydrochloric_acid = (mass_HCL / 1000) * HCL_LCA
hydrogen_per_oxide = (mass_H2O2/ 1000) * H2O2_LCA
acetone = (mass_acetone / 1000) * acetone_LCA
P66614_Cl = (mass_P66614_Cl / 1000) * P66614_Cl_LCA
sodium_hydroxide = (mass_NaOH / 1000) * P66614_Cl_LCA

total_impacts_OM = (hydrochloric_acid + hydrogen_per_oxide + acetone + P66614_Cl + sodium_hydroxide) / np.maximum(total_PTFE_kg, eps) #LCA/kg

total_impacts_energy = (energy_demand * electricity_LCA) / np.maximum(total_PTFE_kg, eps) #LCA/kg


total_impacts= total_impacts_capital + total_impacts_OM + total_impacts_energy


cost_P66614_Cl.extend(np.ravel(total_cost))
impacts_P66614_Cl.extend(np.ravel(total_impacts))



gwp_impacts = total_impacts[:, 1]

#Save  to excel
df_impacts = pd.DataFrame(total_impacts, columns=[
    'AP',    # Acidification Potential
    'GWP',   # Global Warming Potential
    'EFW',   # Ecotoxicity 
    'EP',    # Eutrophication Potential 
    'HTC',   # Human Toxicity, carcinogenic
    'HTNC',  # Human Toxicity, non-carcinogenic
    'ODP',   # Ozone Depletion Potential
    'PMFP',  # Particulate Matter Formation Potential
    'MIR'    # maximum incremental reactivity
])

df_results = pd.DataFrame({
    'cost_P66614_Cl': np.ravel(total_cost),
    'impacts_GWP_P66614_Cl': np.ravel(gwp_impacts)
})


df_cost = pd.DataFrame({
    'capital_cost': np.ravel(capital_cost),
    'OM_cost': np.ravel(OM_cost),
    'energy_cost': np.ravel(energy_cost),
    'total_cost': np.ravel(total_cost),
})

df_total_impacts = pd.DataFrame({
    'total_impacts': np.ravel(total_impacts)
})

df_total_impacts_capital = pd.DataFrame(
    total_impacts_capital,
    columns=df_impacts.columns
)

df_total_impacts_OM = pd.DataFrame(
    total_impacts_OM,
    columns=df_impacts.columns
)

df_total_impacts_energy = pd.DataFrame(
    total_impacts_energy,
    columns=df_impacts.columns
)


#%% sensitivity
dfinputs = pd.DataFrame(inputs_for_sensitivity)[input_name_order]



sensitivity_cost = dfinputs.corrwith(df_cost.total_cost, method='spearman')


sensitivity_total_impacts_AP = dfinputs.corrwith(df_impacts.iloc[:, 0], method='spearman')  # Accessing the first column
sensitivity_total_impacts_GWP = dfinputs.corrwith(df_impacts.iloc[:, 1], method='spearman') 
sensitivity_total_impacts_EFW = dfinputs.corrwith(df_impacts.iloc[:, 2], method='spearman')  
sensitivity_total_impacts_EP = dfinputs.corrwith(df_impacts.iloc[:, 3], method='spearman') 
sensitivity_total_impacts_HTC = dfinputs.corrwith(df_impacts.iloc[:, 4], method='spearman')  
sensitivity_total_impacts_HTNC = dfinputs.corrwith(df_impacts.iloc[:, 5], method='spearman') 
sensitivity_total_impacts_ODP = dfinputs.corrwith(df_impacts.iloc[:, 6], method='spearman')  
sensitivity_total_impacts_PMFP = dfinputs.corrwith(df_impacts.iloc[:, 7], method='spearman') 
sensitivity_total_impacts_MIR = dfinputs.corrwith(df_impacts.iloc[:, 8], method='spearman') 

sensitivity = pd.DataFrame({
     'cost' :sensitivity_cost, 'AP' : sensitivity_total_impacts_AP,
     'GWP' : sensitivity_total_impacts_GWP, 'EFW' : sensitivity_total_impacts_EFW,
     'EP' : sensitivity_total_impacts_EP, 'HTC' : sensitivity_total_impacts_HTC,
     'HTNC' : sensitivity_total_impacts_HTNC, 'ODP' : sensitivity_total_impacts_ODP,
     'PMFP' : sensitivity_total_impacts_PMFP,'MIR' : sensitivity_total_impacts_MIR,
})


with pd.ExcelWriter("P66614_Cl.xlsx") as writer:
    df_results.to_excel(writer, sheet_name="results", index=False)
    df_total_impacts_capital.to_excel(writer, sheet_name="capital_impacts", index=False)
    df_total_impacts_OM.to_excel(writer, sheet_name="OM_impacts", index=False)
    df_total_impacts_energy.to_excel(writer, sheet_name="energy_impacts", index=False)
    df_cost.to_excel(writer, sheet_name="cost", index=False)
    df_impacts.to_excel(writer, sheet_name="impacts_PTFE", index=False)
    sensitivity.to_excel(writer, sheet_name="sensitivity_PTFE")
    dfinputs.to_excel(writer, sheet_name='inputs')