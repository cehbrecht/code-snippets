import time
import ocgis
from ocgis.test.base import create_gridxy_global, create_exact_field

ocgis.env.ADD_OPS_MPI_BARRIER = False
ocgis.env.OVERWRITE = True


# Path to the output netCDf file.
PATH = 'foo.nc'

tic = time.time()

# Create a test grid.
grid = create_gridxy_global()
# Create an exact field on the grid.
field = create_exact_field(grid, 'foo')
# Write the field to disk.
field.write(PATH)

rd = ocgis.RequestDataset(PATH)

# Calculate a monthly mean.
ops = ocgis.OcgOperations(dataset=rd, calc=[{'func': 'mean', 'name': 'mean'}], calc_grouping=['month'],
                          prefix='mean',
                          dir_output='.',
                          output_format='nc')
# Exexcute the operations. This may be done in parallel with "mpirun".
output = ops.execute()

# Inspect the data on rank 0 only.
if ocgis.vm.rank == 0:
    print("run inspect")
    ocgis.RequestDataset(output).inspect()

tac = time.time()
msg = "Completion time [#{}/{}]: {} seconds\n".format(ocgis.vm.rank, ocgis.vm.size, tac - tic)
print(msg)
