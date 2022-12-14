import streamlit as st
import os
from stat_thermo import *

if __name__ == "__main__":
    st.write('''
    # Statistical Thermodynamics Reactor!
    ''')

    st.write('''
    Calculates the thermodynamics state functions for a reaction!
    For more options and information, check out the [GitHub repository](https://github.com/lmonari5/stat_thermo_reactor.git)
    ''')

    dU0 = st.text_input('Reaction ΔU at 0K [Joule/mol]', help='Internal Energy difference at 0 Kelvin and standard pressure')
    data["U0"] = None
    if dU0:
        data["U0"] = float(dU0)
    T = st.text_input('Reaction Temperature [Kelvin]')
    if T:
        T = float(T)

    st.write('''
    ## Add Molecules:
    ''')
    with st.form("add_molecules", clear_on_submit=True):
        name = st.text_input('Name/Formula', help='Name of the molecule')
        s_c = st.text_input('stoichiometric number', help='Reaction stoichiometric number (positive value)')
        sign_dict = {'Reactant': -1, 'Product': +1}
        sign = sign_dict[st.selectbox('The molecule is', ('Reactant', 'Product'))]
        if s_c: s_c = float(s_c) * sign
        P = st.text_input('P: Pressure [bar]', '')
        if P: P = float(P)
        m = st.text_input('m: molecular mass [dalton]', '')
        if m: m = float(m)
        B = st.text_input('B: rotational constant [cm-1]', '')
        if B: B = float(B)
        A = st.text_input('A: other rotational constant [cm-1]', 0)
        if A: A = float(A)
        C = st.text_input('C: other rotational constant [cm-1]', 0)
        if C: C = float(C)
        linearity_dict = {'Linear': True, 'Non-linear': False, 'an Atom': 'Atom'}
        linear = linearity_dict[st.selectbox('The molecule is', ('Linear', 'Non-linear', 'an Atom'))]
        o = st.text_input('o: symmetry number',
                          help='The symmetry number a of a molecule is the order of the finite rotational sub-group of the point group of the molecule')
        if o: o = float(o)
        n_mod_raw = st.text_input('List of the vibrational mode frequencies [cm-1] separated by a comma')
        if n_mod_raw:
            n_mod = [float(i) for i in n_mod_raw.split(',')]
        n_deg_raw = st.text_input('List of the vibrational mode degeneracies separated by a comma')
        if n_deg_raw:
            n_deg = [float(i) for i in n_deg_raw.split(',')]
        En_raw = st.text_input('List of the electron level Energies [cm-1] separated by a comma')
        if En_raw:
            En = [float(i) for i in En_raw.split(',')]
        gn_list_elec_raw = st.text_input('List of the electron levels degeneracies separated by a comma')
        if gn_list_elec_raw:
            gn_list_elec = [float(i) for i in gn_list_elec_raw.split(',')]
        spin_list_raw = st.text_input('List of nuclear spins separated by a comma')
        if spin_list_raw:
            spin_list = [float(i) for i in spin_list_raw.split(',')]
        load = st.form_submit_button('Add Molecule')

        if load:
            data[name] = dict()
            data[name]["s_c"] = int(s_c)
            data[name]["param"] = [P, m, B, o, linear, n_mod, n_deg, gn_list_elec, En, spin_list, A, C]

    st.write('''
    #### Remove molecules:
    ''')
    mol_list = [mol for mol in data if mol != 'U0']
    del_mol = st.selectbox('Select the molecule to remove', mol_list + ['All'])
    delete = st.button('delete')
    if delete and del_mol == 'All':
        for mol in mol_list:
            del(data[mol])
    elif delete:
        del(data[del_mol])

    st.write('''
    ## Reaction:
    ''')
    mol_list = [mol for mol in data if mol != 'U0']
    react_list = []
    product_list = []
    for mol in mol_list:
        if data[mol]["s_c"] < 0:
            react_list.append(f'{-data[mol]["s_c"]} {mol}')
        else:
            product_list.append(f'{data[mol]["s_c"]} {mol}')
    st.write(f'''
    #### {' + '.join(react_list)} ⇌	{' + '.join(product_list)}
    ''')

    st.write('''
    ## Compute:
    ''')
    to_compute = st.selectbox('Select the parameters to calculate', ('Partition Function',
                                                                     'Internal Energy',
                                                                     'Entropy',
                                                                     'Gibbs Free Energy and Reaction Constant'))
    compute = st.button('Compute')
    if compute:
        mol_list = [mol for mol in data if mol != 'U0']
        if to_compute == 'Partition Function':
            for mol in mol_list:
                Q_fast(mol, T)
        elif to_compute == 'Internal Energy':
            for mol in mol_list:
                U_fast(mol, T)
        elif to_compute == 'Entropy':
            for mol in mol_list:
                S_fast(mol, T)
        elif to_compute == 'Gibbs Free Energy and Reaction Constant':
            k_fast(T)
        save()

    st.write('''
    ## Results:
    ''')

    try:
        df = prepare_df()
        st.dataframe(df)
    except Exception as e:
        st.write('Not able to print the DataFrame')
        print(e)

    save_as = st.selectbox('Save results as', ('csv', 'xlsx'))
    filename = 'stat_thermo_results.' + save_as
    if filename in os.listdir():
        with open(filename, "rb") as file:
            btn = st.download_button(label="Download Results Table",
                                     data=file,
                                     file_name=filename,
                                     mime="image/png")


