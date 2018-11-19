# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2018, Caleb Bell <Caleb.Andrew.Bell@gmail.com>

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

import numpy as np
from numpy.testing import assert_allclose
import pytest
from thermo.utils import normalize
from thermo.eos import *
from thermo.eos_mix import *
from scipy.misc import derivative
from scipy.optimize import minimize, newton
from math import log, exp, sqrt
from thermo import Mixture
from thermo.property_package import *


def test_bubble_T_PR():
    Ps = np.logspace(np.log10(1e3), np.log10(8e6), 100).tolist()
    # Value working for sure!
    # A long enough list of points may reveal errors
    # Need to check for singularities in results!
    # Lagrange multiplier is needed.
    T_bubbles_expect = [135.77792634341301, 136.56179975223873, 137.35592304111714, 138.1605125904237, 138.97579118069618, 139.80198815378043, 140.63933971310234, 141.48808915266713, 142.34848716775062, 143.22079210796352, 144.10527026879004, 145.00219623035326, 145.9118531621595, 146.8345331709676, 147.77053765471518, 148.7201776796149, 149.68377437184307, 150.66165932879846, 151.65417505244912, 152.6616753977778, 153.68452605664353, 154.72310505184726, 155.7778032642612, 156.8490249894867, 157.937188514101, 159.04272673536184, 160.16608780166473, 161.30773579673297, 162.46815145564204, 163.64783292476886, 164.84729656230823, 166.06707778415586, 167.30773196086088, 168.56983536585116, 169.8539861804285, 171.16080556094636, 172.49093877035423, 173.84505638241404, 175.22385556194536, 176.6280614293828, 178.058428515323, 179.51574231484207, 181.00082094865053, 182.5145169422077, 184.0577191341151, 185.63135472512306, 187.2363914833706, 188.8738401205766, 190.54475685783353, 192.25024620138348, 193.991463951159, 195.76962046909824, 197.5859842371162, 199.4418857394953, 201.33872170960848, 203.27795978657647, 205.26114363572563, 207.28989859303456, 209.36593790645554, 211.49106965667633, 213.66720445521423, 215.89636403432021, 218.18069086349888, 220.52245895198226, 222.92408602593875, 225.3881473051149, 227.91739114691686, 230.5147568796014, 233.18339521130144, 235.92669168167328, 238.74829372436815, 241.65214202994656, 244.64250705759693, 247.7240317371467, 250.90178165300227, 254.18130431821905, 257.5686995555806, 261.07070353354993, 264.69478970158224, 268.44929079409445, 272.3435473154688, 276.3880896135361, 280.59486299764814, 284.9775086709067, 289.5517180159047, 294.3356847958481, 299.35069043485873, 304.62187400558975, 310.17926492998157, 316.059200210731, 322.3063237832385, 328.97650301847204, 336.14126110695065, 343.8948656757251, 352.36642480869347, 361.7423599546769, 372.31333661508177, 384.5907961800425, 399.6948959805394, 422.0030866468656]

    m = Mixture(['CO2', 'n-hexane'], zs=[.5, .5], T=300, P=1E6)
    pkg = GceosBase(eos_mix=PRMIX, VaporPressures=m.VaporPressures, Tms=m.Tms, Tbs=m.Tbs, 
                     Tcs=m.Tcs, Pcs=m.Pcs, omegas=m.omegas, kijs=[[0,0],[0,0]], eos_kwargs=None)

    bubs = []
    
    for P in Ps:
        bubs.append(pkg.bubble_T(P, m.zs, maxiter=20, xtol=1e-10, maxiter_initial=20, xtol_initial=1e-1))
    assert_allclose(bubs, T_bubbles_expect)


def test_C1_C10_PT_flash():

    m = Mixture(['methane', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10'], zs=[.1]*10, T=300, P=1E6)
    pkg = GceosBase(eos_mix=PRMIX, VaporPressures=m.VaporPressures, Tms=m.Tms, Tbs=m.Tbs, 
                     Tcs=m.Tcs, Pcs=m.Pcs, omegas=m.omegas, kijs=None, eos_kwargs=None)
    pkg.flash(m.zs, T=300, P=1e5)
    assert_allclose(pkg.V_over_F, 0.3933480636546702, atol=.001)
