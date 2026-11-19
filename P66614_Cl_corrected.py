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
# [Rev. R1.13, R2.6] treatment of aqueous waste streams (per m3)
wastewater_LCA = np.reshape(LCA_assumptions.loc['wastewater_LCA',:].iloc[2:].to_numpy(dtype=float), (1,-1))


steel_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['steel_fraction'], correlation_distributions, correlation_parameters, n_samples)
concrete_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['concrete_fraction'], correlation_distributions, correlation_parameters, n_samples)
electricity_cost, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['electricity_cost'], correlation_distributions, correlation_parameters, n_samples)


# Hot plate rated power
ptfe_throughput_t_per_year, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['ptfe_throughput_t_per_year'],correlation_distributions,correlation_parameters,n_samples)
hotplate_power, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_power'],correlation_distributions,correlation_parameters,n_samples)
hotplate_max_temperature, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_max_temperature'],correlation_distributions,correlation_parameters,n_samples)
hotplate_weight, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['hotplate_weight'],correlation_distributions,correlation_parameters,n_samples)

# Times
# [Rev. R2.5] scenario switch: 'ground' (0.5 h + grinding) or 'bulk' (48-72 h, no grinding)
import os
SCENARIO = os.environ.get('SCENARIO', 'ground')
REUSE_OVERRIDE = os.environ.get('REUSE')
OUTFILE = os.environ.get('OUTFILE', 'P66614_Cl_' + SCENARIO + '.xlsx')
time_key = 'heating_time_ground' if SCENARIO == 'ground' else 'heating_time_bulk'
time_100C, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc[time_key],correlation_distributions,correlation_parameters, n_samples)

# [Rev. R1.3, R1.14, R2.6] auxiliary unit operations (kW, h per batch)
grinding_power, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['grinding_power'],correlation_distributions,correlation_parameters, n_samples)
grinding_time, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['grinding_time'],correlation_distributions,correlation_parameters, n_samples)
vacuum_pump_power, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['vacuum_pump_power'],correlation_distributions,correlation_parameters, n_samples)
filtration_time, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['filtration_time'],correlation_distributions,correlation_parameters, n_samples)
# [Rev. R1.14] thermodynamic energy estimate for lab operations (Piccinno et al., 2016)
T_ambient, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['T_ambient'],correlation_distributions,correlation_parameters, n_samples)
heating_efficiency, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['heating_efficiency'],correlation_distributions,correlation_parameters, n_samples)
latent_heat_acetone, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['latent_heat_acetone'],correlation_distributions,correlation_parameters, n_samples)
rotovap_bath_temperature, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['rotovap_bath_temperature'],correlation_distributions,correlation_parameters, n_samples)
residual_liquid_on_solids, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['residual_liquid_on_solids'],correlation_distributions,correlation_parameters, n_samples)
latent_heat_drying, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['latent_heat_drying'],correlation_distributions,correlation_parameters, n_samples)
drying_efficiency, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['drying_efficiency'],correlation_distributions,correlation_parameters, n_samples)

# [Rev. R1.13, R2.6] neutralization of the acidic extraction liquor
acid_liquor_mass, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['acid_liquor_mass'],correlation_distributions,correlation_parameters, n_samples)
acid_liquor_HCl_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['acid_liquor_HCl_fraction'],correlation_distributions,correlation_parameters, n_samples)
alkaline_liquor_mass, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['alkaline_liquor_mass'],correlation_distributions,correlation_parameters, n_samples)
HCL_wt_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['HCL_wt_fraction'],correlation_distributions,correlation_parameters, n_samples)
H2O2_wt_fraction, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['H2O2_wt_fraction'],correlation_distributions,correlation_parameters, n_samples)
acetone_recovery, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['acetone_recovery'],correlation_distributions,correlation_parameters, n_samples)
# Sensitivity only (not part of the base case): system-expansion credit for recovered materials
CREDIT = os.environ.get('CREDIT', '0') == '1'
recovered_PTFE_yield, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['recovered_PTFE_yield'],correlation_distributions,correlation_parameters, n_samples)
recovered_Fe_oxide_yield, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['recovered_Fe_oxide_yield'],correlation_distributions,correlation_parameters, n_samples)
substitution_ratio, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['substitution_ratio'],correlation_distributions,correlation_parameters, n_samples)
virgin_PTFE_price, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['virgin_PTFE_price'],correlation_distributions,correlation_parameters, n_samples)

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
#density_NaOH, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['density_NaOH'], correlation_distributions, correlation_parameters, n_samples)



# [Rev. R2.1, R2.5] corrected composition: 0.45 g PTFE + 0.05 g Fe3O4 per 0.5 g batch
Fe3O4_mass, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['Fe3O4_mass'], correlation_distributions, correlation_parameters, n_samples)
PTFE_mass, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['PTFE_mass'], correlation_distributions, correlation_parameters, n_samples)

reuse_cycles, correlation_distributions, correlation_parameters = lhs.lhs_distribution(design_assumptions.loc['reuse_cycles'], correlation_distributions, correlation_parameters, n_samples)
if REUSE_OVERRIDE is not None:
    reuse_cycles = np.full((n_samples, 1), float(REUSE_OVERRIDE))
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
#mass_NaOH = NaOH_amount * density_NaOH #gm
NaOH_molarity = 6.0      # mol/L
NaOH_molar_mass = 40.0   # g/mol

mass_NaOH = (NaOH_amount / 1000.0 * NaOH_molarity * NaOH_molar_mass)

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

# [Rev. R1.10, R2.5] functional unit: 1 kg of Fe-PTFE composite treated (LCA and LCC)
composite_mass_kg = col(np.maximum((PTFE_mass + Fe3O4_mass) / 1000.0, eps))   # kg per batch
PTFE_mass_kg      = col(np.maximum(PTFE_mass / 1000.0, eps))

# %% Reuse accounting
total_composite_kg = composite_mass_kg * reuse_cycles   # composite treated over all cycles
total_PTFE_kg = PTFE_mass_kg * reuse_cycles
cleaning_cycles = reuse_cycles

# [Rev. R1.6, R1.13, R2.3] Only the IL is regenerated. Its inventory is charged once,
# and the loss after each cycle (1 - recovery_fraction, measured in Table S4) is
# replaced before the next cycle: makeup = inventory * (1 - r) * (n - 1).
IL_use_factor = 1.0 + (1.0 - recovery_fraction) * (reuse_cycles - 1.0)

# Fresh HCl and H2O2 are supplied for every extraction (Section 3.3), so they scale with n.
total_P66614_Cl_cost_USD = (
    col(total_cost_P66614_Cl) * IL_use_factor
    + (col(total_cost_HCL) + col(total_cost_H2O2)) * reuse_cycles
    + reconditioning_cost_per_cycle_USD * reuse_cycles
)

# %% Energy
# [Rev. R1.14] Energy is estimated from process thermodynamics rather than equipment
# nameplate ratings, following Piccinno et al. (2016). Each heat duty is divided by a
# device efficiency. Mechanical operations (grinding, vacuum) use rated power x time.
# Hotplate heating: original formulation, charged once (unchanged from the submitted model)
E_100C_kWh  = (hotplate_power * (50  / hotplate_max_temperature)) * time_100C  / 1000

E_grinding_kWh = grinding_power * grinding_time if SCENARIO == 'ground' else 0.0 * grinding_power
E_filtration_kWh = vacuum_pump_power * filtration_time

# rotary evaporation of the acetone wash (sensible heat to bath temperature + latent heat)
Q_rotovap_kJ = acetone_amount * density_acetone * (2.2e-3 * (rotovap_bath_temperature - T_ambient) + latent_heat_acetone)
E_rotovap_kWh = Q_rotovap_kJ / heating_efficiency / 3600.0

# drying residual liquid from the recovered PTFE-rich and Fe-containing solids
solids_dried_g = PTFE_mass + Fe3O4_mass
E_drying_kWh = solids_dried_g * residual_liquid_on_solids * latent_heat_drying / drying_efficiency / 3600.0

# [Rev. R1.3, R1.14, R2.6] added operations repeat in every batch; hotplate heating is charged once
energy_aux_per_batch = E_grinding_kWh + E_filtration_kWh + E_rotovap_kWh + E_drying_kWh
energy_demand = col(E_100C_kWh) + col(energy_aux_per_batch) * reuse_cycles
energy_cost_kg = (energy_demand * electricity_cost) / np.maximum(total_composite_kg, eps)  # USD per kg composite
energy_cost = energy_cost_kg #USD/kg
# %% Output OM style cost per kg PTFE
# [Rev. R1.13, R2.6] NaOH to neutralize residual HCl in the acidic liquor (HCl + NaOH -> NaCl + H2O)
mass_NaOH_neutralization = acid_liquor_mass * acid_liquor_HCl_fraction / 36.46 * 40.0   # g per batch
total_cost_NaOH_neutralization = mass_NaOH_neutralization * NaOH_cost / 1000.0         # USD per batch

cost_per_kg_PTFE_P666614_Cl_reuse = total_P66614_Cl_cost_USD/ np.maximum(total_composite_kg, eps)
#OM_cost = cost_per_kg_PTFE_P666614_Cl_reuse + total_cost_acetone/np.maximum(total_PTFE_kg, eps) + total_cost_NaOH/np.maximum(total_PTFE_kg, eps)

OM_cost = (
    cost_per_kg_PTFE_P666614_Cl_reuse
    + (col(total_cost_acetone) * (1.0 + (1.0 - col(acetone_recovery)) * (cleaning_cycles - 1.0))) / np.maximum(total_composite_kg, eps)
    + (total_cost_NaOH * cleaning_cycles) / np.maximum(total_composite_kg, eps)
    + (total_cost_NaOH_neutralization * cleaning_cycles) / np.maximum(total_composite_kg, eps)
)

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



# [Rev. R1.13] fresh acid and oxidant in every cycle
# ecoinvent HCl and H2O2 datasets are per kg of pure substance; apply to the active mass (Table S5)
hydrochloric_acid = (mass_HCL * HCL_wt_fraction / 1000) * HCL_LCA * cleaning_cycles
hydrogen_per_oxide = (mass_H2O2 * H2O2_wt_fraction / 1000) * H2O2_LCA * cleaning_cycles
#acetone = (mass_acetone / 1000) * acetone_LCA
# [Rev. R2.3, R2.6] acetone wash is recovered by rotary evaporation (Table S5):
# charge once, then make up losses each subsequent cycle
acetone_use_factor = 1.0 + (1.0 - col(acetone_recovery)) * (cleaning_cycles - 1.0)
acetone = (
    (mass_acetone / 1000)
    * acetone_LCA
    * acetone_use_factor
)

# [Rev. R1.6, R1.13] IL inventory plus makeup for measured losses
P66614_Cl = (mass_P66614_Cl / 1000) * P66614_Cl_LCA * IL_use_factor
#sodium_hydroxide = (mass_NaOH / 1000) * P66614_Cl_LCA
#sodium_hydroxide = (mass_NaOH / 1000) * NaOH_LCA
sodium_hydroxide = (
    (mass_NaOH / 1000)
    * NaOH_LCA
    * cleaning_cycles
)

sodium_hydroxide_neutralization = (mass_NaOH_neutralization / 1000) * NaOH_LCA * cleaning_cycles
# neutralized acidic liquor + alkaline mother liquor (and neutralization reagent), density ~1 g/mL
wastewater_m3 = (acid_liquor_mass + alkaline_liquor_mass + mass_NaOH_neutralization) / 1e6
wastewater_treatment = wastewater_m3 * wastewater_LCA * cleaning_cycles

total_impacts_OM = (hydrochloric_acid + hydrogen_per_oxide + acetone + P66614_Cl + sodium_hydroxide + sodium_hydroxide_neutralization + wastewater_treatment) / np.maximum(total_composite_kg, eps) #LCA/kg composite

total_impacts_energy = (energy_demand * electricity_LCA) / np.maximum(total_composite_kg, eps) #LCA/kg composite


total_impacts= total_impacts_capital + total_impacts_OM + total_impacts_energy

# %% Sensitivity: avoided production of virgin PTFE and iron oxide (ISO 14044 system expansion).
# Applied to all nine TRACI categories; off by default so the base case is unchanged.
total_impacts_credit = np.zeros_like(total_impacts)
if CREDIT:
    ptfe_cf = LCA_assumptions.loc['virgin_PTFE_LCA',:].iloc[2:].to_numpy(dtype=float)
    feox_cf = LCA_assumptions.loc['virgin_Fe_oxide_LCA',:].iloc[2:].to_numpy(dtype=float)
    if np.isnan(ptfe_cf).any() or np.isnan(feox_cf).any():
        raise ValueError('Fill virgin_PTFE_LCA and virgin_Fe_oxide_LCA in assumptions.xlsx (ecoinvent 3.10, TRACI 2.1) before running CREDIT=1')
    total_impacts_credit = -col(substitution_ratio) * (col(recovered_PTFE_yield) * ptfe_cf.reshape(1, -1)
                                                    + col(recovered_Fe_oxide_yield) * feox_cf.reshape(1, -1))
total_impacts_net = total_impacts + total_impacts_credit
# matching cost credit: market value of the recovered PTFE at the same substitution ratio (USD/kg composite)
cost_credit = -col(substitution_ratio) * col(recovered_PTFE_yield) * col(virgin_PTFE_price) if CREDIT else np.zeros_like(col(total_cost))
total_cost_net = col(total_cost) + cost_credit


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


with pd.ExcelWriter(OUTFILE) as writer:
    df_results.to_excel(writer, sheet_name="results", index=False)
    df_total_impacts_capital.to_excel(writer, sheet_name="capital_impacts", index=False)
    df_total_impacts_OM.to_excel(writer, sheet_name="OM_impacts", index=False)
    df_total_impacts_energy.to_excel(writer, sheet_name="energy_impacts", index=False)
    df_cost.to_excel(writer, sheet_name="cost", index=False)
    df_impacts.to_excel(writer, sheet_name="impacts_PTFE", index=False)
    sensitivity.to_excel(writer, sheet_name="sensitivity_PTFE")
    if CREDIT:
        pd.DataFrame(total_impacts_credit, columns=df_impacts.columns).to_excel(writer, sheet_name="credit_impacts", index=False)
        pd.DataFrame(total_impacts_net, columns=df_impacts.columns).to_excel(writer, sheet_name="impacts_net_of_credit", index=False)
        pd.DataFrame({"cost_credit": np.ravel(cost_credit), "total_cost_net_of_credit": np.ravel(total_cost_net)}).to_excel(writer, sheet_name="cost_net_of_credit", index=False)
    dfinputs.to_excel(writer, sheet_name='inputs')