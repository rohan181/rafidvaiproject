from django.shortcuts import render
from .forms import CarrierCalculatorForm, METAL_TO_ION_DATA
import numpy as np
import json
from math import sqrt, log, exp, pi

# Constants
k_boltzmann = 8.617e-5  # eV/K
D0 = 10.5  # cm²/s
Ea_Arsenic = 4.05  # eV
Ea_Phosphorus = 3.66  # eV
Ea_Boron = 3.46

def calculate_diffusion_coeff(T_celsius, metal_type):
    """Calculate diffusion coefficient based on temperature and metal type"""
    T_kelvin = T_celsius + 273.15
    if metal_type == 'Arsenic':
        Ea = Ea_Arsenic
    elif metal_type == 'Phosphorus ':  # Note: original spelled as "Phosphorus "
        Ea = Ea_Phosphorus
    else:
        Ea = Ea_Arsenic  # Default
    
    kT = k_boltzmann * T_kelvin
    D = D0 * exp(-Ea / kT)
    return D

def index(request):
    form = CarrierCalculatorForm()
    chart_data = None
    
    if request.method == 'POST':
        form = CarrierCalculatorForm(request.POST)
        if form.is_valid():
            metal_type = form.cleaned_data['metal_type']
            ion_energy = form.cleaned_data['ion_energy']
            nb = form.cleaned_data['nb']
            q = form.cleaned_data['q']
            tox = form.cleaned_data['tox']
            
            # Get anneal parameters from form
            anneal_temp_c = form.cleaned_data['anneal_temp_c']
            anneal_time_s = form.cleaned_data['anneal_time_s']  # Now from form
            anneal_time_min = anneal_time_s / 60  # Convert to minutes for display
            
            # Get ion energy data based on selected metal
            ion_data = METAL_TO_ION_DATA[metal_type]
            rp = ion_data[ion_energy]["rp"]  # Projected Range
            sig = ion_data[ion_energy]["sig"]  # Standard Deviation
            
            # Calculate diffusion coefficient
            D = calculate_diffusion_coeff(anneal_temp_c, metal_type)
            
            # Generate x values for plotting - make sure we cover both static and diffused distributions
            sig_t = np.sqrt(sig**2 + 2 * D * anneal_time_s)
            x_min = max(0, rp - 5 * sig)  # Don't go below 0
            x_max = rp + 5 * max(sig, sig_t)  # Extend to cover the wider distribution
            x_vals_cm = np.linspace(x_min, x_max, 1000)
            
            # Static (as-implanted) distribution
            np_ = q / (sig * np.sqrt(2 * np.pi))  # Peak concentration
            N_static = np_ * np.exp(-((x_vals_cm - rp)**2) / (2 * sig**2)) - nb
            N_static = np.maximum(N_static, 0)  # Ensure no negative concentrations
            
            # Diffused distribution
            np_t = q / (sig_t * np.sqrt(2 * np.pi))  # Reduced peak concentration after diffusion
            N_diff = np_t * np.exp(-((x_vals_cm - rp)**2) / (2 * sig_t**2)) - nb
            N_diff = np.maximum(N_diff, 0)  # Ensure no negative concentrations
            
            # Calculate concentration at oxide thickness
            N_x_tox_static = np_ * np.exp(-((tox - rp)**2) / (2 * sig**2)) - nb
            N_x_tox_static = max(N_x_tox_static, 0)
            
            # Calculate diffused concentration at oxide thickness
            N_x_tox_diff = np_t * np.exp(-((tox - rp)**2) / (2 * sig_t**2)) - nb
            N_x_tox_diff = max(N_x_tox_diff, 0)
            
            # Calculate junction depth
            xj_static = rp + sig * sqrt(2 * log(np_ / nb)) if np_ > nb else 0
            xj_eff_static = xj_static - tox if xj_static > tox else 0
            
            # Calculate diffused junction depth
            xj_diff = rp + sig_t * sqrt(2 * log(np_t / nb)) if np_t > nb else 0
            xj_eff_diff = xj_diff - tox if xj_diff > tox else 0

            # Δxj = xj_diff − xj_static
            delta_xj = xj_diff - xj_static if xj_diff and xj_static else 0
            # Rp′ = Rp + Δxj / 2
            rp_prime = rp + (delta_xj / 2)
            # ΔRp = Rp′ − Rp
            delta_rp = rp_prime - rp


            chart_data = {
                'ion_energy': ion_energy,
                'metal_type': metal_type,
                'x_vals': x_vals_cm.tolist(),
                'N_static': N_static.tolist(),
                'N_diff': N_diff.tolist(),
                'tox': tox,
                'tox_A': tox * 1e8,  # Convert to Angstrom
                'N_x_tox': float(N_x_tox_diff),  # Use diffused value
                'N_x_tox_static': float(N_x_tox_static),  # Static value
                'xj_static': xj_static,
                'xj_eff_static': xj_eff_static,
                'xj_diff': xj_diff,
                'xj_eff_diff': xj_eff_diff,
                'rp': rp,
                'sig': sig,
                'anneal_time': anneal_time_s,
                'anneal_temp': anneal_temp_c,
                'rp_prime': rp_prime,
                'delta_rp': delta_rp, 
                'D': float(D)  # Diffusion coefficient
            }

    # Set default anneal time for display when form is not submitted
    default_anneal_time_s = 50
    anneal_time_min = default_anneal_time_s / 60

    context = {
        'form': form,
        'chart_data': json.dumps(chart_data) if chart_data else None,
        'anneal_time_min': anneal_time_min,  # Pass minutes to template
    }
    
    # Add ion data for JavaScript
    context['metal_ion_data_json'] = json.dumps({
        metal: list(data.keys()) for metal, data in METAL_TO_ION_DATA.items()
    })
    
    return render(request, 'index.html', context)