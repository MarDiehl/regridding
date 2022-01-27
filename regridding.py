#!/usr/bin/env python

import tempfile
import shutil

import numpy as np
import h5py

import damask

name_l = 'tensionX'
name_g = 'simple'
prefix = 'rg'

rst = h5py.File(f'{name_g}_{name_l}_restart.hdf5')
res = h5py.File(f'{name_g}_{name_l}.hdf5')
for ext in ['sta','hdf5','C_ref']:
    shutil.copy(f'{name_g}_{name_l}.{ext}',f'{name_g}-{prefix}_{name_l}.{ext}')

file_grid = tempfile.NamedTemporaryFile(delete=False,suffix='.vti')
file_grid.write(res[f'setup/{name_g}.vti'][0])
file_grid.close()
grid = damask.Grid.load(file_grid.name)

cells_new = grid.cells*2

mat_config = damask.ConfigMaterial(res[f'setup/material.yaml'][0].decode()) # needed?

F = np.swapaxes(rst['solver/F'],0,2).reshape(rst['solver/F'].shape[:3][::-1]+(3,3))

old_to_new = damask.grid_filters.regrid(grid.size,F,cells_new)

grid_new = damask.Grid(grid.material.flatten()[old_to_new].reshape(cells_new),grid.size,grid.origin)
grid_new.save(f'{name_g}-rg')

mapping_phase_new = res['cell_to/phase'][:,0][old_to_new] # only one constituent

with h5py.File(f'{name_g}-rg_{name_l}_restart.hdf5','w') as rst_new:

    solver = rst_new.create_group('solver')
    for d in rst['solver']:
        if 'aim' in d or 'Avg' in d:
            solver.create_dataset(d,data=rst[f'solver/{d}'])
        else:
            d_ = np.reshape(rst[f'solver/{d}'],(-1,9))
            shape = (3,3) if d == 'F_lastInc' else (9,)
            solver.create_dataset(d,data=d_[old_to_new].reshape(tuple(cells_new[::-1])+shape))

    phase = rst_new.create_group('phase')
    for p in rst['phase']:
        m = mapping_phase_new[mapping_phase_new['label']==p.encode()]['entry']
        phase.create_group(p)
        for d in rst[f'phase/{p}']:
            rst_new[f'phase/{p}'].create_dataset(d,data=rst[f'phase/{p}/{d}'][()][m])

    homogenization = rst_new.create_group('homogenization')
    for h in rst['homogenization']:
        homogenization.create_group(h)

