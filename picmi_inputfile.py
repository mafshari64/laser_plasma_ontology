
# Import necessary PICMI classes from a PIConGPU LWFA simulation based on .param files:
# https://github.com/ComputationalRadiationPhysics/picongpu/blob/dev/share/picongpu/examples/LaserWakefield/include/picongpu/param
#and  .cfg file:
# https://github.com/ComputationalRadiationPhysics/picongpu/blob/dev/share/picongpu/examples/LaserWakefield/etc/picongpu/8.cfg

from picongpu import picmi
from picongpu import pypicongpu
import numpy as np

##### Input parameters:

# moving_window_velocity = [0.0, 0.9, 0.0] still unsupported
#custom templates: period_diagnostic = 100

# Enable or disable IONIZATION based on speciesInitialization.param
ENABLE_IONS = True
ENABLE_IONIZATION = True

numberCells = np.array([192 , 2048, 192])
cellSize = np.array([0.1772e-6, 0.4430e-7, 0.1772e-6])  # unit: meter)
# Define the simulation grid based on grid.param
grid = picmi.Cartesian3DGrid(
    picongpu_n_gpus=[2,4,1],
    number_of_cells=numberCells.tolist(),  
    lower_bound=[0, 0, 0],
    upper_bound=(numberCells * cellSize).tolist(),
    lower_boundary_conditions =["open", "open", "open"], 
    upper_boundary_conditions =["open", "open", "open"])

# Define Gaussian density profile parameters based on density.param
gaussianDensity = picmi.FoilDistribution(
    density = 1.e25,
    front = 8.0e-5,
    thickness = 2.0e-5,
    exponential_pre_plasma_length = 8.0e-5,
    exponential_post_plasma_length = 8.0e-5,
    exponential_pre_plasma_cutoff = 1.0,
    exponential_post_plasma_cutoff = 1.0)

# for particle type see https://github.com/openPMD/openPMD-standard/pull/264/files
electrons = picmi.Species(
    particle_type='electron',
    name='electron',
    initial_distribution=gaussianDensity     
)

# for particle type see https://github.com/openPMD/openPMD-standard/pull/264/files
hydrogen_ionization = picmi.Species(
    particle_type='H',
    name='hydrogen',
    initial_distribution=gaussianDensity,
    charge_state=0,
    picongpu_ionization_electrons = electrons
)
hydrogen_fully_ionized = picmi.Species(
    particle_type='H',
    name='hydrogen',
    initial_distribution=gaussianDensity,
    picongpu_fully_ionized = True
)

solver = picmi.ElectromagneticSolver(
    grid=grid,
    method='Yee',
)

laser = picmi.GaussianLaser(
    wavelength= 0.8e-6,
    waist= 5.0e-6 / 1.17741,
    duration= 5.e-15,
    propagation_direction= [0., 1., 0.],
    polarization_direction= [1., 0., 0.],
    focal_position= [float(numberCells[0]*cellSize[0]/2.), 4.62e-5, float(numberCells[2]*cellSize[2]/2.)],
    centroid_position=[float(numberCells[0]*cellSize[0]/2.), 0., float(numberCells[2]*cellSize[2]/2.)],
    picongpu_polarization_type = pypicongpu.laser.GaussianLaser.PolarizationType.CIRCULAR,
    a0=8.0,
    picongpu_phase = 0.0
)

randomLayout=picmi.PseudoRandomLayout(n_macroparticles_per_cell = 2)

# Initialize particles  based on speciesInitialization.param

sim = picmi.Simulation(
    solver=solver,
    max_steps= 4000,
    time_step_size=1.39e-16,
    picongpu_template_dir = "/home/afshar87/afshari/simulation/picongpu/share/picongpu/examples/LaserWakefield"
    )

sim.add_species(electrons, layout=randomLayout)

# Add species initializations to the simulation based on speciesInitialization.param
if ENABLE_IONS:
    if ENABLE_IONIZATION:
        sim.add_species(hydrogen_ionization, layout=randomLayout)
    else:
        sim.add_species(hydrogen_fully_ionized, layout=randomLayout)

sim.add_laser(laser, None)

# Creates a directory  input  to write the simulation input, where we can run pic-build and subsequently tbg
pypicongpu_sim = sim.get_as_pypicongpu()  # sim.get_as_pypicongpu() method translates the picmi.Simulation object into a PIConGPU-specific configuration object.

# for custom user input. stuff not yet standardised in PICMI https://github.com/ComputationalRadiationPhysics/picongpu/pull/4878

movingWindowInput = pypicongpu.customuserinput.CustomUserInput()
movingWindowInput.addToCustomInput({"moving_window_velocity_X": 0.0,"moving_window_velocity_Y": 0.9,"moving_window_velocity_Z": 0.0}, "movingWindow")
pypicongpu_sim.add_custom_user_input(movingWindowInput)

minWeightInput = pypicongpu.customuserinput.CustomUserInput()
minWeightInput.addToCustomInput({"minimumWeight": 10.0}, "minimumWeight")
pypicongpu_sim.add_custom_user_input(minWeightInput)

ionizationModels = pypicongpu.customuserinput.CustomUserInput()
ionizationModels.addToCustomInput({
    "BSIEffectiveZ": True,
    "ADKCircPol": True,
    "BSI": False,
    "BSIStarkShifted":False, 
    "Keldysh":False,
    "ThomasFermi":False}, "ionizationModels")
pypicongpu_sim.add_custom_user_input(ionizationModels)

gaussianProfile = pypicongpu.species.operation.densityprofile.Gaussian()
gaussianProfile.gasFactor = -1.0
gaussianProfile.gasPower = 4.0

gaussianProfile.vacuumCellsY = 50

gaussianProfile.gasCenterLeft = 8.0e-5
gaussianProfile.gasCenterRight = 10.0e-5

gaussianProfile.gasSigmaLeft = 8.0e-5
gaussianProfile.gasSigmaRight = 8.0e-5

pypicongpu_sim.init_manager.all_operations[0].profile = gaussianProfile

# for generating setup with custom input see standard implementation
# https://github.com/ComputationalRadiationPhysics/picongpu/blob/dev/lib/python/picongpu/picmi/simulation.py

#  *** 
# 
# 1-sim involves defining the grid, species, laser, and other simulation parameters using the picmi module.
# 2-pypicongpu_sim is an instance of a class that contains the specific configurations and setup for the PIConGPU simulation. 
# It is generated by the sim.get_as_pypicongpu() method. 
# This method converts the picmi.Simulation object into a format that PIConGPU can understand and use. 
# Essentially, pypicongpu_sim holds all the information about the simulation, including the grid setup,
# species definitions, laser configurations, and custom user inputs.
# 3-sim.write_input_file takes the PIConGPU-specific configuration object and writes all necessary input files to the specified directory, here eg "test_masoud".
sim.write_input_file("test_masoud", pypicongpu_sim) # for pypicongpu_sim refers to above lines *** 






# @todo

# Visualization and Scaling Constants based on png.param
# SCALE_IMAGE = 1.0
# SCALE_TO_CELLSIZE = True
# WHITE_BOX_PER_GPU = False
# EM_FIELD_SCALE_CHANNEL1 = 7
# EM_FIELD_SCALE_CHANNEL2 = -1
# EM_FIELD_SCALE_CHANNEL3 = -1
# CUSTOM_NORMALIZATION_SI = [5.0e12 / cst.c, 5.0e12, 15.0]
# PRE_PARTICLE_DENS_OPACITY = 0.25
# PRE_CHANNEL1_OPACITY = 1.0
# PRE_CHANNEL2_OPACITY = 1.0
# PRE_CHANNEL3_OPACITY = 1.0

# Visualization diagnostics settings based on 8.cfg and png.param
# ''visualization_diag = picmi.FieldDiagnostic(
# grid=grid,
# period=period_diagnostic,
# #data_list=['Ex', 'Ey', 'Ez', 'Bx', 'By', 'Bz', 'Jx', 'Jy', 'Jz'],
# data_list=['E','B', 'J'],
# scale_image=SCALE_IMAGE,
# scale_to_cellsize=SCALE_TO_CELLSIZE,
# white_box_per_GPU=WHITE_BOX_PER_GPU,
# em_field_scale_channel1=EM_FIELD_SCALE_CHANNEL1,
# em_field_scale_channel2=EM_FIELD_SCALE_CHANNEL2,
# em_field_scale_channel3=EM_FIELD_SCALE_CHANNEL3,
# custom_normalization_si=CUSTOM_NORMALIZATION_SI,
# pre_particle_dens_opacity=PRE_PARTICLE_DENS_OPACITY,
# pre_channel1_opacity=PRE_CHANNEL1_OPACITY,
# pre_channel2_opacity=PRE_CHANNEL2_OPACITY,
# pre_channel3_opacity=PRE_CHANNEL3_OPACITY
# )

# PNG image output for rough electron density and laser preview
# png_YX = picmi.ParticleDiagnostic(
#     period=period_diagnostic,
#     species=[Electrons()],
#     data_list=['position', 'momentum', 'weighting'], ??
#     data_list=['density'], ??
#     output_format='png',
#     write_dir ='pngElectronsYX',
#     slice_data={'axis': 'yx', 'slice': 0.5} ??
# )

# ???? i think we do not need it-
# laser_particle_diag = picmi.ParticleDiagnostic(
#     period=period_diagnostic,
#     species=[laser_electrons],
#     data_list=['position', 'momentum', 'weighting']
# )

# # Energy histogram for electrons based on 8.cfg
# energy_histogram = picmi.ParticleDiagnostic(
#     period=period_diagnostic,
#     species=[Electrons()],
#     data_list=['energy'],
#     num_bins=1024,
#     lower_bound=0.0,
#     upper_bound=1000.0,
#     filter='all'
# )

# # Longitudinal phase space for electrons based on 8.cfg
# phase_space_diag = picmi.ParticleDiagnostic(
#     period=period_diagnostic,
#     species=[Electrons()],
#     data_list=['position', 'momentum'],
#     phase_space=[{'axis': 'y', 'momentum': 'py', 'min': -1.0, 'max': 1.0}]
# )

# # OpenPMD output : Macro particle counter for electrons based on 8.cfg
# openpmd_diag = picmi.ParticleDiagnostic(
#     period=period_diagnostic,
#     species=[Electrons()], ??
#     data_list=['macro_particle_count'],    ??
#     output_format='openpmd',
#     write_dir ='simData',  ??  
#     checkpointing={'backend': 'openPMD', 'period': 100, 'restart_backend': 'openPMD'} ??
# )


# Macro particle counter for electrons
# macro_particle_counter = picmi.ParticleDiagnostic(
#     period= period_diagnostic,
#     species=[Electrons()],
#     data_list=['macro_particle_count']
# )