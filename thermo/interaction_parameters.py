  # -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2017, 2018, 2019 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from __future__ import division

__all__ = ['InteractionParameterDB']

import os
import numpy as np
from math import isnan
from chemicals.utils import can_load_data, PY37
from chemicals.identifiers import check_CAS, sorted_CAS_key

'''Need to be able to add NRTL parameters sets (T dept)
Need to add single kijis, and kijs with T dept
'''

folder = os.path.join(os.path.dirname(__file__), 'Phase Change')
chemsep_db_path = os.path.join(folder, 'ChemSep')



class InteractionParameterDB(object):

    def __init__(self):
        self.tables = {}
        self.metadata = {}

    def load_json(self, file, name):
        import json
        f = open(file).read()
        dat = json.loads(f)
        self.tables[name] = dat['data']
        self.metadata[name] = dat['metadata']

    def validate_table(self, name):
        table = self.tables[name]
        meta = self.metadata[name]
        components = meta['components']
        necessary_keys = meta['necessary keys']
        # Check the CASs
        for key in table:
            CASs = key.split(' ')
            # Check the key is the right length
            assert len(CASs) == components
            # Check all CAS number keys are valid
            assert all(check_CAS(i) for i in CASs)

            values = table[key]
            for i in necessary_keys:
                # Assert all necessary keys are present
                assert i in values
                val = values[i]
                # Check they are not None
                assert val is not None
                # Check they are not nan
                assert not isnan(val)


    def has_ip_specific(self, name, CASs, ip):
        if self.metadata[name]['symmetric']:
            key = ' '.join(sorted_CAS_key(CASs))
        else:
            key = ' '.join(CASs)
        table = self.tables[name]
        if key not in table:
            return False
        return ip in table[key]

    def get_ip_specific(self, name, CASs, ip):
        if self.metadata[name]['symmetric']:
            key = ' '.join(sorted_CAS_key(CASs))
        else:
            key = ' '.join(CASs)
        try:
            return self.tables[name][key][ip]
        except KeyError:
            return self.metadata[name]['missing'][ip]

    def get_tables_with_type(self, ip_type):
        tables = []
        for key, d in self.metadata.items():
            if d['type'] == ip_type:
                tables.append(key)
        return tables

    def get_ip_automatic(self, CASs, ip_type, ip):
        table = self.get_tables_with_type(ip_type)[0]
        return self.get_ip_specific(table, CASs, ip)

    def get_ip_symmetric_matrix(self, name, CASs, ip, T=298.15):
        table = self.tables[name]
        N = len(CASs)
        values = [[None for i in range(N)] for j in range(N)]
        for i in range(N):
            for j in range(N):
                if i == j:
                    i_ip = 0.0
                elif values[j][i] is not None:
                    continue # already set
                else:
                    i_ip = self.get_ip_specific(name, [CASs[i], CASs[j]], ip)
                values[i][j] = values[j][i] = i_ip
        return values

    def get_ip_asymmetric_matrix(self, name, CASs, ip, T=298.15):
        table = self.tables[name]
        N = len(CASs)
        values = [[None for i in range(N)] for j in range(N)]
        for i in range(N):
            for j in range(N):
                if i == j:
                    i_ip = 0.0
                else:
                    i_ip = self.get_ip_specific(name, [CASs[i], CASs[j]], ip)
                values[i][j] = i_ip
        return values


ip_files = {'ChemSep PR': os.path.join(chemsep_db_path, 'pr.json'),
            'ChemSep NRTL': os.path.join(chemsep_db_path, 'nrtl.json')}

_loaded_interactions = False
def load_all_interaction_parameters():
    global IPDB, _loaded_interactions

    IPDB = InteractionParameterDB()
    for name, file in ip_files.items():
        IPDB.load_json(file, name)

    _loaded_interactions = True

if PY37:
    def __getattr__(name):
        if name in ('IPDB',):
            load_all_interaction_parameters()
            return globals()[name]
        raise AttributeError("module %s has no attribute %s" %(__name__, name))
else:
    if can_load_data:
        load_all_interaction_parameters()



# Nothing wrong with storing alpha twice...

#
# TODO change above models to include T dependence; need a model which has it though!
# That probably means a user db

#ans = IPDB.get_ip_asymmetric_matrix('ChemSep NRTL', ['64-17-5', '7732-18-5'], 'bij')
#ans = IPDB.get_ip_asymmetric_matrix('ChemSep NRTL', ['64-17-5', '7732-18-5', '67-56-1'], 'alphaij')
## alphas are good too.

