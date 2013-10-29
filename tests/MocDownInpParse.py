#! /usr/bin/env python3

###
### Import
###

from MocDown import * ;

###
### Constants
###

###
# Test cases
###
mocDownInputFileName2Parameters = {
    '../examples/rbwrThPin/mocdown.inp' : {'defaultDecayLibrary': 'decay', 'burnCells': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57], 'origenLibraryPathTemplate': '/usr/local/ORIGEN/libs/{}.lib', 'minimumCellMassDensityCutoff': 0.001, 'minimumBurnupStep': 200.0, 'supplementaryMocdownLibrary': [], 'includeDecayHeat': True, 'qValueMethod': 'origens', 'compressPickles': True, 'numberOfCorrectorSteps': 0, 'burnUnits': 'MWth', 'numberOfPredictorSteps': 0, 'mcnpXsdirPath': '/usr/local/LANL/MCNP_BINDATA/xsdir', 'mcnpExecutablePath': '/usr/local/LANL/MCNP6/bin/mcnp6.mpi', 'updateCoolantDensities': False, 'minimumIsotopeCutoff': 1e-07, 'mcnpRunCommand': 'DATAPATH="" ; srun {executable} tasks 6 i={baseName}.i me={baseName}.mesh o={baseName}.o r={baseName}.tpe s={baseName}.src x={xsdir} >> transport.log 2>&1 ;', 'isotopicsConvergenceNormType': 'inf', 'updateFuelTemperatures': False, 'multiplicationFactorConvergenceTolerance': 0.001, 'forceDecayTransport': False, 'depletionTime': 100.0, 'maximumFluenceStep': 8e+21, 'numberOfOrigenThreads': 20, 'defaultPhotonLibrary': 'gxuo2brm', 'depletionPower': 0.02, 'depletionStepPowers': [], 'origenExecutablePath': '/usr/local/ORIGEN/bin/o2_fast', 'maximumBurnupStep': 2500.0, 'mcnpSourceFileName': 'source', 'isotopicsConvergenceTolerance': 1e-05, 'isPowerMode': True, 'depletionStepFluxes': [], 'depletionFlux': None, 'defaultXsLibrary': 'amo0tttc', 'origenRunCommand': 'cd {} ; ./origen >> {}transmute.log 2>&1 ;', 'depletionTerminalDecayTime': None, 'minimumFluenceStep': 3e+20, 'recycleToEquilibrium': False, 'depletionStepTimeIntervals': [], 'isPredictorMode': False},
    '../examples/rbwrThAssembly/mocdown.inp' : {'maximumFluenceStep': 8e+21, 'includeDecayHeat': True, 'criticalPowerRatioFallbackIndex': 41, 'maximumBurnupStep': 2500.0, 'mcnpXsdirPath': '/usr/local/LANL/MCNP_BINDATA/xsdir', 'depletionStepPowers': [], 'isotopicsConvergenceNormType': 'inf', 'depletionStepTimeIntervals': [], 'qValueMethod': 'origens', 'mcnpRunCommand': 'DATAPATH="" ; srun {executable} tasks 6 i={baseName}.i me={baseName}.mesh o={baseName}.o r={baseName}.tpe s={baseName}.src x={xsdir} >> transport.log 2>&1 ;', 'burnUnits': 'MWth', 'mcnpSourceFileName': 'source', 'isotopicsConvergenceTolerance': 3e-06, 'depletionPower': 16.35833333333333, 'numberOfPredictorSteps': 0, 'thermalHydraulicConvergenceNormType': 'inf', 'depletionTime': 1780.0, 'isPowerMode': True, 'supplementaryMocdownLibrary': ['RbwrTh'], 'criticalPowerRatioLimit': 1.3, 'compressPickles': True, 'origenLibraryPathTemplate': '/usr/local/ORIGEN/libs/{}.lib', 'minimumFluenceStep': 3e+20, 'coolantHydraulicDiameter': 0.004113888, 'defaultDecayLibrary': 'decay', 'origenExecutablePath': '/usr/local/ORIGEN/bin/o2_fast', 'depletionTerminalDecayTime': 3.0, 'coolantInletTemperature': 555.71, 'depletionStepFluxes': [], 'isPredictorMode': False, 'defaultPhotonLibrary': 'gxuo2brm', 'origenRunCommand': 'cd {} ; ./origen >> {}transmute.log 2>&1 ;', 'depletionFlux': None, 'assemblyFuelsToCools': [({(1000,): (2000,)}, {(1001,): (2001,)}, {(1002,): (2002,)}, {(1003,): (2003,)}, {(1004,): (2004,)}, {(1005,): (2005,)}, {(1006,): (2006,)}, {(1007,): (2007,)}, {(1008,): (2008,)}, {(1009,): (2009,)}, {(1010,): (2010,)}, {(1011,): (2011,)}, {(1012,): (2012,)}, {(1013,): (2013,)}, {(1014,): (2014,)}, {(1015,): (2015,)}, {(1016,): (2016,)}, {(1017,): (2017,)}, {(1018,): (2018,)}, {(1019,): (2019,)}, {(1020,): (2020,)}, {(1021,): (2021,)}, {(1022,): (2022,)}, {(1023,): (2023,)}, {(1024,): (2024,)}, {(1025,): (2025,)}, {(1026,): (2026,)}, {(1027,): (2027,)}, {(1028,): (2028,)}, {(1029,): (2029,)}, {(1030,): (2030,)}, {(1031,): (2031,)}, {(1032,): (2032,)}, {(1033,): (2033,)}, {(1034,): (2034,)}, {(1035,): (2035,)}, {(1036,): (2036,)}, {(1037,): (2037,)}, {(1038,): (2038,)}, {(1039,): (2039,)}, {(1040,): (2040,)}, {(1041,): (2041,)}, {(1042,): (2042,)}, {(1043,): (2043,)}, {(1044,): (2044,)}, {(1045,): (2045,)}, {(1046,): (2046,)}, {(1047,): (2047,)}, {(1048,): (2048,)}, {(1049,): (2049,)}, {(1050,): (2050,)}, {(1051,): (2051,)}, {(1052,): (2052,)}, {(1053,): (2053,)}, {(1054,): (2054,)}, {(1055,): (2055,)}, {(): (2056,)})], 'numberOfOrigenThreads': 20, 'pressureDropCorrelation': 'epri', 'criticalPowerRatioCorrelation': 'm-cise', 'multiplicationFactorConvergenceTolerance': 0.0005, 'numberOfCorrectorSteps': 0, 'updateCoolantDensities': True, 'updateFuelTemperatures': False, 'coolantHeatedDiameter': 0.004428861, 'coolantInletPressure': 7.25, 'coolantFlowArea': 0.028420944, 'mcnpExecutablePath': '/usr/local/LANL/MCNP6/bin/mcnp6.mpi', 'coolantFlowLengths': [0.3, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.037, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 0.046666667, 1.3], 'minimumCellMassDensityCutoff': 0.001, 'minimumIsotopeCutoff': 1e-07, 'recycleToEquilibrium': False, 'forceDecayTransport': False, 'thermalHydraulicConvergenceTolerance': 0.01, 'coolantMassFlowRate': 29.68, 'coolantBypassCells': [7000], 'voidFractionCorrelation': 'relap', 'defaultXsLibrary': 'amo0tttc', 'burnCells': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055], 'coolantDensityDampingCoefficient': 1.0, 'minimumBurnupStep': 200.0},
    '../examples/sphere/mocdown.inp' : {'minimumCellMassDensityCutoff': 0.001, 'isPowerMode': True, 'isPredictorMode': False, 'updateCoolantDensities': False, 'depletionFlux': None, 'qValueMethod': 'origens', 'minimumBurnupStep': 200.0, 'depletionStepTimeIntervals': [], 'forceDecayTransport': False, 'minimumFluenceStep': 3e+20, 'defaultXsLibrary': 'amo0tttc', 'numberOfCorrectorSteps': 0, 'depletionPower': 0.02, 'isotopicsConvergenceNormType': 'inf', 'burnCells': [1], 'depletionTerminalDecayTime': None, 'mcnpExecutablePath': '/usr/local/LANL/MCNP6/bin/mcnp6.mpi', 'multiplicationFactorConvergenceTolerance': 0.001, 'includeDecayHeat': False, 'depletionTime': 5000.0, 'defaultPhotonLibrary': 'gxuo2brm', 'defaultDecayLibrary': 'decay', 'compressPickles': True, 'origenLibraryPathTemplate': '/usr/local/ORIGEN/libs/{}.lib', 'burnUnits': 'MWth', 'maximumFluenceStep': 8e+21, 'origenRunCommand': 'cd {} ; ./origen >> {}transmute.log 2>&1 ;', 'numberOfPredictorSteps': 0, 'minimumIsotopeCutoff': 1e-10, 'recycleToEquilibrium': False, 'maximumBurnupStep': 2500.0, 'depletionStepFluxes': [], 'mcnpXsdirPath': '/usr/local/LANL/MCNP_BINDATA/xsdir', 'mcnpRunCommand': 'DATAPATH="" ; srun {executable} tasks 6 i={baseName}.i me={baseName}.mesh o={baseName}.o r={baseName}.tpe s={baseName}.src x={xsdir} >> transport.log 2>&1 ;', 'isotopicsConvergenceTolerance': 1e-05, 'origenExecutablePath': '/usr/local/ORIGEN/bin/o2_fast', 'mcnpSourceFileName': 'source', 'numberOfOrigenThreads': 20, 'depletionStepPowers': [], 'updateFuelTemperatures': False, 'supplementaryMocdownLibrary': []},
};

###
### Functions
###

###
# Null library parameters and converters
###
def GetLibraryParametersConverters(self):
    return {}, {};
###
# Check mocdown.inp parsing
###
def CompareParse(mocDownInputFileName, parameters):
    ###
    arguments = Class();
    arguments.isQuiet = arguments.isVerbose = False;
    arguments.mocDownInputFileName = mocDownInputFileName;
    ###
    MocDownInputFile.GetLibraryParametersConverters = GetLibraryParametersConverters;
    mocDownInputFile = MocDownInputFile(arguments);
    ImportLibraries(mocDownInputFile);
    mocDownInputFile.Populate();
    ###
    if parameters != mocDownInputFile.GetParameters():
        print(mocDownInputFile.GetParameters());
    ###
    return parameters == mocDownInputFile.GetParameters();

###
### Script
###

###
# main()
###
for mocDownInputFileName, parameters in mocDownInputFileName2Parameters.items():
    if CompareParse(mocDownInputFileName, parameters):
        print('PASS');
