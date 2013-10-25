#! /usr/bin/env python3

__author__ = 'Jeffrey Seifried';
__email__ = 'jeffrey.seifried@gmail.com';
__version__ = '1.0';
__year__ = '2013';

###
### Standard library imports
###

from argparse import ArgumentParser;
from concurrent import futures as Futures;
from csv import reader as CsvReader,\
                writer as CsvWriter;
from glob import glob as Glob;
from gzip import open as GzipOpen;
from math import pi as pi;
from numpy import array as Array,\
                  concatenate as Concatenate,\
                  diff as Difference,\
                  empty as Empty,\
                  exp as Exponent,\
                  interp as LinearInterpolate,\
                  log as NaturalLogarithm,\
                  logspace as LogSpace,\
                  nan_to_num as Nan2Num,\
                  nonzero as NonZero,\
                  seterr as SetNumpyError,\
                  zeros as Zeros;
SetNumpyError(invalid = 'ignore', divide = 'ignore');
from os import getcwd as GetCurrentWorkingDirectory,\
               mkdir as LibMakeDirectory,\
               remove as LibRemoveFile,\
               rmdir as LibRemoveDirectory,\
               stat as FileStatus,\
               symlink as LibSymbolicLink,\
               system as SystemCall;
from os.path import exists as Exists,\
                    getmtime as GetModificationTime;
from pickle import dump as Pickle,\
                   dumps as PickleString,\
                   load as UnPickle,\
                   UnpicklingError;
from random import randint as RandomInteger;
from re import compile as ReCompile;
from shutil import copyfile as LibCopyFile,\
                   move as LibMoveFile,\
                   rmtree as LibRemoveTree;
from sys import modules as Modules,\
                stdout as StdOut;
from tempfile import mkdtemp as LibMakeTemporaryDirectory;
from time import sleep as Sleep;

###
### Physical constants (http://physics.nist.gov/cuu/Constants/Table/allascii.txt)
###

###
# Avogadro's number * cm² / barns [cm² / b · mol]
###
avogadrosNumber = 6.02214129e23 / 1e24;
###
# Atomic mass constant energy equivalent
###
mevPerCSquaredPerAmu = 931.494061;
###
# Boltzmann's constant [J / K]
###
boltzmannsConstant = 1.3806488e-23;
###
# Neutron mass [atomic mass units]
###
neutronMass = 1.00866491600;
###
# Unit conversions
###
joulePerMev = 1.602176565e-13;
mevPerJoule = 1. / joulePerMev;
mevPerKelvin = boltzmannsConstant * mevPerJoule;
kelvinPerMev = 1. / mevPerKelvin;
daysPerYear = 365.242;

###
### Constants
###

###
# Computer epsilon
###
epsilon = 1e-9;
###
# ORIGEN2.2 input file template
### # FIXME absorption rate (19) and fission rate (21) now; radioactivity (7) and ingestion hazard (15) later?
origenInputFileTemplate = '''\
 -1
 -1
 -1
 TIT
 BAS
 LIP    1 1 0
 LIB    0 1 2 3 -{xsLibs[0]:d} -{xsLibs[1]:d} -{xsLibs[2]:d} 9 50 0 4 0
 OPTL   8 8 8 8 8  8 8 8 8 8  8 8 8 8 8  8 8 8 5 8  5 8 8 8
 OPTA   8 8 8 8 8  8 8 8 8 8  8 8 8 8 8  8 8 8 5 8  5 8 8 8
 OPTF   8 8 8 8 8  8 8 8 8 8  8 8 8 8 8  8 8 8 5 8  5 8 8 8
 CUT    3 1.0E-24 28 1.0E-75 -1
 INP    1 -2 0 0 1 1
 BUP
 {burnMode}    {timeEnds[0]:.5E} {cellBurnRate:.5E}  1  2 4 2
 {burnMode}    {timeEnds[1]:.5E} {cellBurnRate:.5E}  2  3 4 0
 {burnMode}    {timeEnds[2]:.5E} {cellBurnRate:.5E}  3  4 4 0
 {burnMode}    {timeEnds[3]:.5E} {cellBurnRate:.5E}  4  5 4 0
 {burnMode}    {timeEnds[4]:.5E} {cellBurnRate:.5E}  5  6 4 0
 {burnMode}    {timeEnds[5]:.5E} {cellBurnRate:.5E}  6  7 4 0
 {burnMode}    {timeEnds[6]:.5E} {cellBurnRate:.5E}  7  8 4 0
 {burnMode}    {timeEnds[7]:.5E} {cellBurnRate:.5E}  8  9 4 0
 {burnMode}    {timeEnds[8]:.5E} {cellBurnRate:.5E}  9 10 4 0
 {burnMode}    {timeEnds[9]:.5E} {cellBurnRate:.5E} 10 11 4 0
 {burnMode}    {timeEnds[10]:.5E} {cellBurnRate:.5E} 11  1 4 0
 {burnMode}    {timeEnds[11]:.5E} {cellBurnRate:.5E}  1  2 4 0
 {burnMode}    {timeEnds[12]:.5E} {cellBurnRate:.5E}  2  3 4 0
 {burnMode}    {timeEnds[13]:.5E} {cellBurnRate:.5E}  3  4 4 0
 {burnMode}    {timeEnds[14]:.5E} {cellBurnRate:.5E}  4  5 4 0
 {burnMode}    {timeEnds[15]:.5E} {cellBurnRate:.5E}  5  6 4 0
 {burnMode}    {timeEnds[16]:.5E} {cellBurnRate:.5E}  6  7 4 0
 {burnMode}    {timeEnds[17]:.5E} {cellBurnRate:.5E}  7  8 4 0
 {burnMode}    {timeEnds[18]:.5E} {cellBurnRate:.5E}  8  9 4 0
 {burnMode}    {timeEnds[19]:.5E} {cellBurnRate:.5E}  9 10 4 0
 BUP
 PCH    10 10 10
 OUT    10 1 0 0
 STP    4
0''';
###
# ORIGEN2.2 punch card template
###
origenPunchCardTemplate = '''\
{lib:d} {zam:d} {moles:.9E} 0 0 0 0 0 0''';
###
# ORIGEN2.2 cross-section library template
###
origenXsLibraryTemplate = '''\
{lib:>3d} {zam:>7d} {sigma[0]:.4E} {sigma[1]:.4E} {sigma[2]:.4E} {sigma[3]:.4E} {sigma[4]:.4E} {sigma[5]:.4E} -1''';
###
# Regular expression for numeric strings
###
reNumber = ReCompile(r'[0-9]+', 2 | 8);

###
### Custom classes
###

###
###
###
class Coordinate:
    def __init__(self, x, y):
        self.x = x;
        self.y = y;
        ###
        return;
    ###
    def GetX(self):
        return self.x;
    ###
    def GetY(self):
        return self.y;
###
# Empty Class
###
class Class:
    pass;
###
# Depletion calculation
###
class DepletionCalculation:
    def __init__(self, arguments, isPickleTransmute = False):
        ###
        # Set argument attributes
        ###
        self.arguments = arguments;
        ###
        # Set isPickleTransmute
        ###
        self.isPickleTransmute = isPickleTransmute;
        ###
        # Parse transport file
        ###
        self.originalTransportFile = ReadTransportFile(arguments.transportFileName);
        ###
        # Maybe populate depletion steps
        ###
        self.PopulateDepletionSteps();
        ###
        # Run depletion calculation
        ###
        self.Deplete();
        ###
        # Collate pickles
        ###
        self.depletionCalculationPickle = DepletionCalculationPickle(self);
        ###
        return;
    ###
    def __len__(self):
        return len(mocDownInputFile);
    ###
    # Generic getter methods
    ###
    def GetArguments(self):
        return self.arguments;
    ###
    def GetBurnCells(self):
        return self.GetParameter('burnCells');
    ###
    def GetBurnMode(self):
        return ['IRF', 'IRP'][self.GetParameter('isPowerMode')];
    ###
    def GetBurnRate(self):
        if self.GetParameter('isPowerMode'):
            return self.GetDepletionStepPower();
        else:
            return self.GetDepletionStepFlux();
    ###
    def GetCellNumberBurnRate(self, cellNumber):
        return self.GetCellNumber2BurnRate()[cellNumber];
    ###
    def GetCellNumber2BurnRate(self):
        return self.cellNumber2BurnRate;
    ###
    def GetCellNumberDecayPower(self, cellNumber, offset = 0):
        try:
            return self.depletionStep2CellNumber2DecayPower[self.GetDepletionStep(offset)][cellNumber];
        except KeyError:
            return 0;
    ###
    def GetCellNumberThermalPower(self, transportOutputFile, cellNumber, includeDecayHeat = True):
        if transportOutputFile.GetIsCoupled():
            ###
            # This is a coupled neutron/photon transport calculation;
            # F6:np tallies are a good estimate for thermal power
            ###
            thermalPower = float(transportOutputFile.GetCellNumberParticlePower(cellNumber, mnemonic = 'f6'));
        else:
            ###
            # This is a neuton-only transport calculation;
            # A Q-value estimate must be made for thermal power
            ###
            thermalPower = float(transportOutputFile.GetCellNumberQPower(cellNumber, mocDownInputFile.GetParameter('qValueMethod')));
        ###
        # If requested, add decay heat
        ###
        if includeDecayHeat:
            thermalPower += self.GetCellNumberDecayPower(cellNumber);
        ###
        return thermalPower;
    ###
    def GetCellNumber2Micros(self):
        return self.cellNumber2Micros;
    ###
    def GetCellNumber2OrigenCalculation(self):
        return self.cellNumber2OrigenCalculation;
    ###
    def GetCellNumber2Zam2Moles(self):
        return self.cellNumber2Zam2Moles;
    ###
    def GetCoolantDensityCalculations(self):
        return self.coolantDensityCalculations;
    ###
    def GetDefaultDecayLibrary(self):
        return self.defaultDecayLibrary;
    ###
    def GetDefaultPhotonLibrary(self):
        return self.defaultPhotonLibrary;
    ###
    def GetDefaultXsLibrary(self):
        return self.defaultXsLibrary;
    ###
    def GetDepletionCalculationPickle(self):
        return self.depletionCalculationPickle;
    ###
    def GetDepletionStepFlux(self):
        return self.GetParameter('depletionStepFluxes')[self.GetDepletionStep()];
    ###
    def GetDepletionStepPickle(self, offset = 0):
        try:
            return self.depletionStep2DepletionStepPickle[self.GetDepletionStep(offset)];
        except KeyError:
            return None;
    ###
    def GetDepletionStepPower(self):
        return self.GetParameter('depletionStepPowers')[self.GetDepletionStep()];
    ###
    def GetDepletionStepTimeInterval(self):
        return self.GetParameter('depletionStepTimeIntervals')[self.GetDepletionStep()];
    ###
    def GetDepletionStep(self, offset = 0):
        return self.depletionStep + offset;
    ###
    def GetDepletionString(self):
        return 'DS #{:d} of {:d}'.format(self.GetDepletionStep(), len(self));
    ###
    def GetEitherUpdate(self):
        return self.GetParameter('updateCoolantDensities') or self.GetParameter('updateFuelTemperatures');
    ###
    def GetFileName(self, extension = None, withoutTH = False):
        fileName = self.GetOriginalTransportFile().GetNewputFileName(self.GetDepletionStep());
        if self.GetEitherUpdate() and not withoutTH:
            fileName += '-{:d}'.format(self.GetTransportIteration());
        ###
        if extension is not None:
            fileName += '.{}'.format(extension);
        ###
        return fileName;
    ###
    def GetFuelTemperatureCalculations(self):
        return self.fuelTemperatureCalculations;
    ###
    def GetDisplayFiles(self):
        return not bool(self.GetArguments().isQuiet);
    ###
    def GetForceDecayTransport(self):
        return self.GetParameter('forceDecayTransport');
    ###
    def GetIncludeDecayHeat(self):
        return self.GetParameter('includeDecayHeat');
    ###
    def GetIsDecayStep(self):
        return (self.GetParameter('isPowerMode') and 0 == self.GetDepletionStepPower()) or (not self.GetParameter('isPowerMode') and 0 == self.GetDepletionStepFlux());
    ###
    def GetIsLesserMcnp(self):
        ###
        # This is specific to the berkelium.nuc.berkeley.edu and hopper.nersc.gov clusters (circa November, 2012)!
        ###
        return all(dir not in self.GetParameter('mcnpExecutablePath') for dir in ('MCNP5-1.60', 'MCNP6', 'MCNPX', 'm1537'));
    ###
    def GetIsOrigen2(self):
        return any(executable in self.GetParameter('origenExecutablePath') for executable in ('o2_fast', 'o2_thermal'));
    ###
    def GetIsPickleTransmute(self):
        return self.isPickleTransmute;
    ###
    def GetIsRestart(self):
        return bool(self.GetArguments().isRestart);
    ###
    def GetIsVerbose(self):
        return bool(self.GetArguments().isVerbose);
    ###
    def GetLibZams(self, lib):
        return self.GetLib2Zams()[lib];
    ###
    def GetLib2Zams(self):
        return self.lib2Zams;
    ###
    def GetLibZamExcite(self, lib, zam):
        return self.lib2Zam2Excite[lib][zam];
    ###
    def GetMaterialNumberZaid(self, materialNumber):
        return self.GetMaterialNumber2Zaid()[materialNumber];
    ###
    def GetMaterialNumber2Zaid(self):
        return self.materialNumber2Zaid;
    ###
    def GetTransmuteTallyNumber(self):
        return self.transmuteTallyNumber;
    ###
    def GetOrigen2LibMts(self, lib):
        return self.GetOrigen2Lib2Mts()[lib % 10];
    ###
    def GetOrigen2Lib2Mts(self):
        return self.origen2Lib2Mts;
    ###
    def GetOriginalTransportFile(self):
        return self.originalTransportFile;
    ###
    def GetParameter(self, key):
        return self.GetParameters()[key];
    ###
    def GetParameters(self):
        return mocDownInputFile.GetParameters();
    ###
    def GetPreviousCoolantDensityCalculations(self):
        return self.previousCoolantDensityCalculations;
    ###
    def GetPreviousFuelTemperatureCalculations(self):
        return self.previousFuelTemperatureCalculations;
    ###
    def GetTransportIteration(self):
        if not hasattr(self, 'transportIteration'):
            self.transportIteration = 0;
        ###
        return self.transportIteration;
    ###
    def GetXsDirZaids(self):
        return self.xsDirZaids;
    ###
    def GetZa2WattsPerMole(self):
        return self.za2WattsPerMole;
    ###
    # Depletion methods
    ###
    def PopulateDepletionSteps(self):
        ###
        # Populate depletion step time intervals, fluxes, and powers if the total depletion time is provided
        ###
        if self.GetParameter('depletionTime') is not None:
            ###
            if self.GetParameter('depletionFlux') is not None:
                if self.GetParameter('depletionFlux') and self.GetParameter('depletionTime'):
                    ###
                    # Determine days -> fluence conversion
                    ###
                    days2Fluence = self.GetParameter('depletionFlux');
                    fluenceLeft = self.GetParameter('depletionTime') * days2Fluence;
                    ###
                    # Populate fluence steps
                    ###
                    fluenceStep = self.GetParameter('minimumFluenceStep');
                    depletionStepFluences = [];
                    while fluenceLeft:
                        ###
                        # Don't burn beyond what is left!
                        ###
                        fluenceStep = min(fluenceStep, fluenceLeft);
                        ###
                        # Append fluenceStep
                        ###
                        depletionStepFluences.append(fluenceStep);
                        fluenceLeft -= fluenceStep;
                        ###
                        # Double fluenceStep
                        # Limit to maximumFluenceStep
                        ###
                        fluenceStep *= 2;
                        fluenceStep = min(fluenceStep, self.GetParameter('maximumFluenceStep'));
                    ###
                    # Convert fluence steps -> time steps
                    ###
                    mocDownInputFile.parameters['depletionStepTimeIntervals'] = [SafeDivide(depletionStepFluence, days2Fluence) for depletionStepFluence in depletionStepFluences];
                else:
                    ###
                    # Decay step or transport-only
                    ###
                    mocDownInputFile.parameters['depletionStepTimeIntervals'] = [self.GetParameter('depletionTime')];
                ###
                # Repeat the power for each time step
                ###
                mocDownInputFile.parameters['depletionStepFluxes'] = [self.GetParameter('depletionFlux')] * len(self);
            elif self.GetParameter('depletionPower') is not None:
                if self.GetParameter('depletionPower') and self.GetParameter('depletionTime'):
                    ###
                    # Determine days -> BU conversion
                    ###
                    days2Burnup = SafeDivide(self.GetParameter('depletionPower'), self.GetOriginalTransportFile().GetHeavyMetalMT());
                    burnupLeft = self.GetParameter('depletionTime') * days2Burnup;
                    ###
                    # Populate burnup steps
                    ###
                    burnupStep = self.GetParameter('minimumBurnupStep');
                    depletionStepBurnups = [];
                    while burnupLeft:
                        ###
                        # Don't burn beyond what is left!
                        ###
                        burnupStep = min(burnupStep, burnupLeft);
                        ###
                        # Append burnupStep
                        ###
                        depletionStepBurnups.append(burnupStep);
                        burnupLeft -= burnupStep;
                        ###
                        # Double burnupStep;
                        # Limit it to maximumBurnupStep
                        ###
                        burnupStep *= 2;
                        burnupStep = min(burnupStep, self.GetParameter('maximumBurnupStep'));
                    ###
                    # Convert burnup steps -> time steps
                    ###
                    mocDownInputFile.parameters['depletionStepTimeIntervals'] = [SafeDivide(depletionStepBurnup, days2Burnup) for depletionStepBurnup in depletionStepBurnups];
                else:
                    ###
                    # Decay step or transport-only
                    ###
                    mocDownInputFile.parameters['depletionStepTimeIntervals'] = [self.GetParameter('depletionTime')];
                ###
                # Repeat the power for each time step
                ###
                mocDownInputFile.parameters['depletionStepPowers'] = [self.GetParameter('depletionPower')] * len(self);
            ###
            # Erase depletion time;
            # For iteration purposes, this can be modified and the depletion steps will be regenerated
            ###
            mocDownInputFile.parameters['depletionTime'] = None;
            ###
            # Maybe append decay step
            ###
            if bool(self.GetParameter('depletionTerminalDecayTime')):
                ###
                # Decay time
                ###
                mocDownInputFile.parameters['depletionStepTimeIntervals'].append(self.GetParameter('depletionTerminalDecayTime') * daysPerYear);
                ###
                # Power or flux
                ###
                if self.GetParameter('isPowerMode'):
                    mocDownInputFile.parameters['depletionStepPowers'].append(0);
                else:
                    mocDownInputFile.parameters['depletionStepFluxes'].append(0);
        ###
        # Calculate depletion step time ends
        ###
        mocDownInputFile.parameters['depletionStepTimeEnds'] = [sum(self.GetParameter('depletionStepTimeIntervals')[ : index]) for index in range(len(self) + 1)];
        ###
        return;
    ###
    def Deplete(self):
        PrintNow('> {} will perform {} depletion step(s)'.format(__file__, len(self)));
        ###
        # Prepare depletion
        ###
        self.PrepareDepletion();
        ###
        # Iterate over depletion steps
        ###
        while self.GetDepletionStep() < len(self):
            ###
            # Try to unpickle depletion step
            ###
            self.TryUnpickle();
            ###
            # If this is a restart step, unpickle files and skip
            ###
            if self.GetIsRestart() and self.GetDepletionStepPickle() is not None:
                PrintNow('> This is a restart step ... skipping {}'.format(self.GetDepletionString()));
                depletionStepPickle = self.GetDepletionStepPickle();
                ###
                # Maybe write the unpickled transport input
                ###
                if not Exists(self.GetFileName('i')) and depletionStepPickle.GetTransportInputRaw() is not None:
                    WriteFile(self.GetFileName('i', withoutTH = True), depletionStepPickle.GetTransportInputRaw(), display = self.GetDisplayFiles());
                ###
                # Maybe write the unpickled transport output
                ###
                if not Exists(self.GetFileName('o')) and depletionStepPickle.GetTransportOutputRaw() is not None:
                    WriteFile(self.GetFileName('o', withoutTH = True), depletionStepPickle.GetTransportOutputRaw(), display = self.GetDisplayFiles());
                ###
                # Grab the pickle'd ORIGEN calculations and decay powers
                ###
                self.cellNumber2OrigenCalculation = {cellNumber : depletionStepPickle.GetCellNumberOrigenCalculation(cellNumber) for cellNumber in depletionStepPickle.GetBurnCells()};
                self.depletionStep2CellNumber2DecayPower[self.GetDepletionStep(offset = +1)] = depletionStepPickle.GetCellNumber2NextDecayPower();
                ###
                # Increment depletion step
                ###
                self.IncrementDepletionStep();
                ###
                # Kick out of depletion step
                ###
                continue;
            ###
            # Transport calculation with possible iterations on densities or temperatures
            ###
            transportFile = self.TransportConvergence();
            ###
            # Transmute calculation
            ###
            self.TransmuteThreads(transportFile, GetCurrentWorkingDirectory() + '/');
            ###
            # Pickle depletion object after every depletion step for restarts, recycles, and plotting
            ###
            self.PickleDepletionStep(transportFile);
            ###
            # Increment depletion step
            ###
            self.IncrementDepletionStep();
        ###
        # Prepare end-of-depletion transport input
        ###
        self.PrepareTransport();
        ###
        # Pickle depletion object -- post-transmute, but pre-transport
        ###
        self.PickleDepletionStep(McnpInputFile(self.GetFileName('i', withoutTH = (self.GetDepletionStep() >= len(self)))));
        ###
        PrintNow('> {} has completed all {} depletion step(s)'.format(__file__, len(self)));
        ###
        return;
    ###
    def PrepareDepletion(self):
        ###
        # Set depletion step
        ###
        self.depletionStep = 0;
        ###
        # Set coolant density / fuel temperature calculations
        ###
        self.coolantDensityCalculations = [];
        self.previousCoolantDensityCalculations = [];
        self.fuelTemperatureCalculations = [];
        self.previousFuelTemperatureCalculations = [];
        ###
        # Set DS -> pickle
        ###
        self.depletionStep2DepletionStepPickle = {};
        ###
        # Define MT #'s for each ORIGEN library group (1 = Activation products, 2 = Actinides, and 3 = Fission Products)
        ###
        self.origen2Lib2Mts = {
            1 : (102, 16, 107, 103),
            2 : (102, 16, 17, -6),
            3 : (102, 16, 107, 103),
        };
        ###
        # Read default decay, photon, and cross-section libraries
        ###
        for defaultLibrary in ('defaultDecayLibrary', 'defaultPhotonLibrary', 'defaultXsLibrary'):
            setattr(self, defaultLibrary, ReadFile(self.GetParameter('origenLibraryPathTemplate').format(self.GetParameter(defaultLibrary)), display = self.GetDisplayFiles()));
        ###
        # Maybe populate molar decay heat conversions
        ###
        self.za2WattsPerMole = {};
        if self.GetIncludeDecayHeat():
            iuConversion = {
                '1' : 1,
                '2' : 1 / 60,
                '3' : 1 / 60 / 60,
                '4' : 1 / 60 / 60 / 24,
                '5' : 1 / 60 / 60 / 24 / daysPerYear,
                '6' : 0,
                '7' : 1 / 60 / 60 / 24 / daysPerYear / 1e3,
                '8' : 1 / 60 / 60 / 24 / daysPerYear / 1e6,
                '9' : 1 / 60 / 60 / 24 / daysPerYear / 1e9,
            };
            logOfTwo = NaturalLogarithm(2);
            ###
            for match in ReCompile(r'^ *\d {2,3}([\d]{5,7}) +(\d) +([\d\.e+\- ]{9}).+\n[\d ]{20}([\d\.e+\- ]{9} ){3}', 2 | 8).finditer(self.GetDefaultDecayLibrary()):
                zam, iu, thalf, qrec = match.groups();
                ###
                self.za2WattsPerMole[Zaid2Za(Zam2Zaid(int(float(zam)), ''))] = logOfTwo * SafeDivide(iuConversion[iu], float(thalf.replace(' ', ''))) * float(qrec.replace(' ', '')) * joulePerMev * (avogadrosNumber * 1e24);
        ###
        # Initiate cell # -> decay powers (delayed β's and γ's);
        # Assume that only burn cells have appreciable decay heat
        ###
        self.depletionStep2CellNumber2DecayPower = {self.GetDepletionStep(offset = 0) : {cellNumber : self.GetOriginalTransportFile().GetCellNumberDecayPower(cellNumber, self.GetZa2WattsPerMole()) for cellNumber in self.GetBurnCells()}};
        ###
        # Populate cross-section library metastable fractions
        ###
        def HelperExcited(*args):
            return SafeDivide(args[2], args[0] + args[2]), SafeDivide(args[3], args[1] + args[3]);
        ###
        libs = set(int(float(lib)) for lib in ReCompile(r'^ *(\d{1,3}) +', 2 | 8).findall(self.GetDefaultXsLibrary()));
        ###
        self.lib2Zams = {};
        self.lib2Zam2Excite = {};
        for lib in libs:
            self.lib2Zams[lib] = [];
            self.lib2Zam2Excite[lib] = {};
            for match in ReCompile(r'^ *{} +(\d{{5,7}}) +([\d\.e+\-]+) +([\d\.e+\-]+) +[\d\.e+\-]+ +[\d\.e+\-]+ +([\d\.e+\-]+) +([\d\.e+\-]+) + [\d\.e+\-]+ *$'.format(lib), 2 | 8).finditer(self.GetDefaultXsLibrary()):
                zam = int(float(match.group(1)));
                self.lib2Zams[lib].append(zam);
                self.lib2Zam2Excite[lib][zam] = HelperExcited(*(float(group.replace(' ', '')) for group in match.groups()[1 : ]));
        ###
        # Populate xsdir cross-section zaids
        ###
        self.xsDirZaids = sorted(m.group() for m in ReCompile(r'\d{4,6}\.\d{2}c', 2 | 8).finditer(xsDir));
        ###
        # Maybe remove transport and trasmute log files
        ###
        if not self.GetIsRestart():
            for logFileName in ('transport.log', 'transmute.log'):
                RemoveFile(logFileName, display = self.GetDisplayFiles());
        ###
        # Set transmutation results to None
        ###
        self.cellNumber2OrigenCalculation = self.cellNumber2Zam2Moles = self.cellNumber2Micros = None;
        ###
        # Set transmutation constant tally number
        ###
        self.transmuteTallyNumber = 4;
        ###
        return;
    ###
    def TryUnpickle(self):
        ###
        # If a restart is requested, attempt to load the depletion step pickle;
        # If the pickle doesn't exist, fail to as if the restart was not requested (for that depletion step)
        ###
        self.depletionStep2DepletionStepPickle[self.GetDepletionStep()] = None;
        ###
        if self.GetIsRestart() or self.GetIsPickleTransmute():
            ###
            extension = 'pkl';
            if self.GetParameter('compressPickles'):
                extension += '.gz';
            ###
            if Exists('{}.{}'.format(self.GetFileName(withoutTH = True), extension)):
                self.depletionStep2DepletionStepPickle[self.GetDepletionStep()] = self.UnpickleDepletionStep();
                ###
                if self.GetDepletionStepPickle().GetParameters() != self.GetParameters():
                    Warning('{} input parameters do not match that of the pickle'.format(__file__));
        ###
        return;
    ###
    def TransportConvergence(self):
        transportFile = None;
        ###
        # Archive the most relevant coolant density calculation:
        # First, for restarts, during the first non-pickle step (before any have been performed), unpickle the most recent one;
        # Second, for recycles, during transmute-only cycles (when none are performed), unpickle the current one
        # Third, if any have been performed, archive the most recent one;
        ###
        if self.GetIsRestart() and self.GetDepletionStepPickle(offset = -1) is not None and any(self.GetDepletionStepPickle(offset = -1).GetCoolantDensityCalculations()):
            self.previousCoolantDensityCalculations = [coolantDensityCalculation for coolantDensityCalculation in self.GetDepletionStepPickle(offset = -1).GetCoolantDensityCalculations() if coolantDensityCalculation is not None];
        ###
        if self.GetIsPickleTransmute() and self.GetDepletionStepPickle(offset = +0) is not None and any(self.GetDepletionStepPickle(offset = +0).GetCoolantDensityCalculations()):
            self.previousCoolantDensityCalculations = [coolantDensityCalculation for coolantDensityCalculation in self.GetDepletionStepPickle(offset = +0).GetCoolantDensityCalculations() if coolantDensityCalculation is not None];
        ###
        if any(self.GetCoolantDensityCalculations()):
            self.previousCoolantDensityCalculations = [coolantDensityCalculation for coolantDensityCalculation in self.GetCoolantDensityCalculations() if coolantDensityCalculation is not None];
        ###
        self.coolantDensityCalculations = [];
        ###
        # Archive the most relevant fuel temperature calculation:
        # First, for restarts, during the first non-pickle step (before any have been performed), unpickle the most recent one;
        # Second, for recycles, during transmute-only cycles (when none are performed), unpickle the current one
        # Third, if any have been performed, archive the most recent one;
        ###
        if self.GetIsRestart() and self.GetDepletionStepPickle(offset = -1) is not None and any(self.GetDepletionStepPickle(offset = -1).GetFuelTemperatureCalculations()):
            self.previousFuelTemperatureCalculations = [fuelTemperatureCalculation for fuelTemperatureCalculation in self.GetDepletionStepPickle(offset = -1).GetFuelTemperatureCalculations() if fuelTemperatureCalculation is not None];
        ###
        if self.GetIsPickleTransmute() and self.GetDepletionStepPickle(offset = +0) is not None and any(self.GetDepletionStepPickle(offset = +0).GetFuelTemperatureCalculations()):
            self.previousFuelTemperatureCalculations = [fuelTemperatureCalculation for fuelTemperatureCalculation in self.GetDepletionStepPickle(offset = +0).GetFuelTemperatureCalculations() if fuelTemperatureCalculation is not None];
        ###
        if any(self.GetFuelTemperatureCalculations()):
            self.previousFuelTemperatureCalculations = [fuelTemperatureCalculation for fuelTemperatureCalculation in self.GetFuelTemperatureCalculations() if fuelTemperatureCalculation is not None];
        ###
        self.fuelTemperatureCalculations = [];
        ###
        # Fixed-point iteration, rotating between transport, coolant density updates, and fuel temperature updates;
        # Convergence is signified by transportFile's input file not having a newputRaw
        ###
        while transportFile is None or transportFile.GetIsUpdated():
            ###
            # Write transport input with necessary tallies
            ###
            self.PrepareTransport(transportFile);
            ###
            # Run tranport calculation;
            # Parse results
            ###
            transportFile = self.Transport();
            ###
            # Clean up files
            ###
            self.CleanUpFiles();
            ###
            # Maybe update material densities;
            ###
            self.coolantDensityCalculations.append(self.UpdateCoolantDensitys(transportFile));
            ###
            # Maybe update material temperatures
            ###
            self.fuelTemperatureCalculations.append(self.UpdateFuelTemperatures(transportFile));
            ###
            # Increment transport iteration
            ###
            self.IncrementTransportIteration();
        ###
        # Transport iterations are complete!
        ###
        self.ResetTransportIteration();
        ###
        return transportFile;
    ###
    def PrepareTransport(self, transportFile = None):
        PrintNow('> Writing MCNP input for {}{}'.format(self.GetDepletionString(), ['', '; transport iteration #{:d}'.format(self.GetTransportIteration())][self.GetTransportIteration() > 0]));
        ###
        # If this is the first transport iteration, then grab the original transport input file;
        # Otherwise, the correct tallies and burned cell densities
        ###
        if 0 == self.GetTransportIteration():
            transportFile = self.GetOriginalTransportFile();
            ###
            # We want a clean input file to work with
            ###
            transportFile.ResetNewput();
            ###
            # Determine zaids;
            # Maybe replace burned cells and materials
            ###
            if self.GetCellNumber2OrigenCalculation() is None:
                ###
                # This is the first depletion step
                ###
                zaids = {zaid for cellNumber in self.GetBurnCells() for zaid in transportFile.FindCellMaterial(cellNumber).GetZaids()};
            elif isinstance(self.GetCellNumber2OrigenCalculation(), dict):
                ###
                # This is the nth depletion step
                ###
                zaids = set();
                for cellNumber, origenCalculation in self.GetCellNumber2OrigenCalculation().items():
                    ###
                    # Kick out insignificant zaids and zaids without xsdir entries
                    ###
                    minimumIsotopeCutoff = self.GetParameter('minimumIsotopeCutoff');
                    zaid2AbsorptionFraction = {zaid : absorptionFraction for zaid, absorptionFraction in origenCalculation.GetZaid2AbsorptionFraction().items() if absorptionFraction > minimumIsotopeCutoff if zaid in self.GetXsDirZaids()};
                    zaid2AtomFraction = {zaid : atomFraction for zaid, atomFraction in origenCalculation.GetZaid2AtomFraction().items() if atomFraction > minimumIsotopeCutoff if zaid in self.GetXsDirZaids()};
                    zaid2FissionFraction = {zaid : fissionFraction for zaid, fissionFraction in origenCalculation.GetZaid2FissionFraction().items() if fissionFraction > minimumIsotopeCutoff if zaid in self.GetXsDirZaids()};
                    zaid2WeightFraction = {zaid : weightFraction for zaid, weightFraction in origenCalculation.GetZaid2WeightFraction().items() if weightFraction > minimumIsotopeCutoff if zaid in self.GetXsDirZaids()};
                    ###
                    # Take the union of absorption-, atom-, fission-, and weight-fraction-sufficient zaids
                    ###
                    for zaid2Fraction in (zaid2AbsorptionFraction, zaid2FissionFraction, zaid2WeightFraction):
                        zaid2AtomFraction.update({zaid : origenCalculation.GetZaid2AtomFraction()[zaid] for zaid in set(zaid2Fraction) - set(zaid2AtomFraction)});
                    ###
                    # Update zaids set
                    ###
                    zaids.update(zaid2AtomFraction);
                    ###
                    # Replace original cell with burned cell
                    ###
                    cell = transportFile.FindCell(cellNumber);
                    cellCard = cell.GetMaterialDensityRegex().sub('{:+10.7f}'.format(origenCalculation.GetNumberDensity()), cell.GetRaw());
                    transportFile.ReplaceNewputCard(cell, cellCard);
                    ###
                    # Replace original material with burned material
                    ###
                    material = transportFile.FindCellMaterial(cellNumber);
                    materialCard = WordArrange(words = ('{:>10} {:+.5E}'.format(zaid, atomFraction) for zaid, atomFraction in sorted(zaid2AtomFraction.items(), key = lambda item: (item[1], item[0]), reverse = True)), prefix = '\nm{:<6d}'.format(material.GetNumber()), indent = 8);
                    transportFile.ReplaceNewputCard(material, materialCard);
            ###
            # If this is not the last depletion step, attach single-zaid materials and tallys
            ###
            if self.GetDepletionStep() < len(self):
                ###
                # Determine existing (and therefore unavailable) material and tally numbers
                ###
                unavailable = {mnemonic : set() for mnemonic in ('f1', 'f2', 'f4', 'fm4', 'f5', 'f6', 'f7', 'f8')};
                unavailable['m'] = {material.GetNumber() for material in transportFile.GetMaterials()};
                unavailable['m'].update((0, ));
                ###
                for tally in transportFile.GetTallys():
                    tallyNumber = tally.GetNumber();
                    unavailable['f{}'.format(tallyNumber % 10)].update((tallyNumber // 10, ));
                ###
                mnemonic2NewLines = {};
                ###
                # Single-za materials;
                # Find unique material number for each zaid;
                # Material numbers limits in MCNP5-1.51 are 5-digits; those of later versions are 8-digits
                ###
                mnemonic = 'm';
                numberOfDigits = [8, 4][self.GetIsLesserMcnp()];
                zaid2MaterialNumber = {};
                ###
                for zaid in zaids:
                    za = Zaid2Za(zaid);
                    if za not in unavailable[mnemonic] and NaturalLogarithm(za) < NaturalLogarithm(10) * numberOfDigits:
                        materialNumber = za;
                    else:
                        materialNumber = UniqueDigits(numberOfDigits, unavailable[mnemonic]);
                    ###
                    unavailable[mnemonic].update((materialNumber, ));
                    ###
                    zaid2MaterialNumber[zaid] = materialNumber;
                mnemonic2NewLines[mnemonic] = ('m{:<6} {:>10} +1.0'.format(materialNumber, zaid) for zaid, materialNumber in sorted(zaid2MaterialNumber.items(), key = lambda item: NumericStringKey(item[0])));
                ###
                # Invert and attach zaid -> material #
                ###
                self.materialNumber2Zaid = {materialNumber : zaid for zaid, materialNumber in zaid2MaterialNumber.items()};
                ###
                # Burn cell flux and reaction rate tallies;
                # Find unique tally number
                # Tally numbers limits in MCNP5-1.51 are 3-digits; those of later versions are 4-digits
                ###
                mnemonic = 'f4';
                numberOfDigits = [3, 4][self.GetIsLesserMcnp()];
                for tallyNumber in range(100):
                    if tallyNumber not in unavailable[mnemonic]:
                        break;
                    tallyNumber = None;
                if tallyNumber is None:
                    tallyNumber = UniqueDigits(numberOfDigits, unavailable[mnemonic]);
                ###
                self.transmuteTallyNumber = 10 * tallyNumber + 4;
                ###
                unavailable[mnemonic].update((tallyNumber, ));
                ###
                # Tally cards
                ###
                mnemonic2NewLines[mnemonic] = [WordArrange(words = sorted(self.GetBurnCells()), prefix = 'f{}:n'.format(10 * tallyNumber + int(float(mnemonic[-1]))))];
                ###
                mnemonic = 'fm4';
                ###
                def Zaid2Mts(zaid):
                    zam = Zaid2Zam(zaid);
                    mts = {mt for lib, zams in self.GetLib2Zams().items() if zam in zams for mt in self.GetOrigen2LibMts(lib)};
                    ###
                    if mts:
                        return sorted(mts);
                    ###
                    return self.GetOrigen2LibMts(1);
                ###
                bins = ['(1)'] + ['(1 {} ({}))'.format(materialNumber, ') ('.join(str(reactionNumber) for reactionNumber in Zaid2Mts(zaid))) for zaid, materialNumber in sorted(zaid2MaterialNumber.items(), key = lambda item: NumericStringKey(item[0]))];
                mnemonic2NewLines[mnemonic] = [WordArrange(words = bins, prefix = 'fm{}:n'.format(10 * tallyNumber + int(float(mnemonic[-1]))))];
                ###
                # Thermal power tallies;
                # Only include them when coupled neutron/photon transport is performed
                ###
                if transportFile.GetIsCoupled():
                    mnemonic = 'f6';
                    mnemonic2NewLines[mnemonic] = [WordArrange(words = transportFile.GetPowerCells(), prefix = 'f{}:{}'.format(10 * tallyNumber + int(float(mnemonic[-1])), transportFile.GetMode()))];
                ###
                # Append new lines to input raw
                ###
                if mnemonic2NewLines:
                    transportFile.AppendNewputCard('\n'.join('\n'.join(newLines) for mnemonic, newLines in sorted(mnemonic2NewLines.items())));
        ###
        # Grab the most relevant coolant density calculation
        ###
        coolantDensityCalculation = None;
        ###
        if any(self.GetPreviousCoolantDensityCalculations()):
            coolantDensityCalculation = [coolantDensityCalculation for coolantDensityCalculation in self.GetPreviousCoolantDensityCalculations() if coolantDensityCalculation is not None][-1];
        ###
        if any(self.GetCoolantDensityCalculations()):
            coolantDensityCalculation = [coolantDensityCalculation for coolantDensityCalculation in self.GetCoolantDensityCalculations() if coolantDensityCalculation is not None][-1];
        ###
        # If a coolant density update exist, implement it
        ###
        if coolantDensityCalculation is not None:
            ###
            # Iterate over assemblies
            ###
            for assemblyCalculation in coolantDensityCalculation.values():
                ###
                # Iterate over coolant cells
                ###
                for cellNumber in assemblyCalculation.GetUpdateCellNumbers():
                    ###
                    # Replace original cell with transport-updated cell
                    ###
                    cell = transportFile.FindCell(cellNumber);
                    cellCard = cell.GetMaterialDensityRegex().sub('{:+10.7f}'.format(-abs(assemblyCalculation.GetCellNumberMassDensity(cellNumber))), cell.GetRaw());
                    transportFile.ReplaceNewputCard(cell, cellCard);
        ###
        # Grab the most relevant coolant density calculation
        ###
        fuelTemperatureCalculation = None;
        ###
        if any(self.GetPreviousFuelTemperatureCalculations()):
            fuelTemperatureCalculation = [fuelTemperatureCalculation for fuelTemperatureCalculation in self.GetPreviousFuelTemperatureCalculations() if fuelTemperatureCalculation is not None][-1];
        ###
        if any(self.GetFuelTemperatureCalculations()):
            fuelTemperatureCalculation = [fuelTemperatureCalculation for fuelTemperatureCalculation in self.GetFuelTemperatureCalculations() if fuelTemperatureCalculation is not None][-1];
        ###
        # If a fuel temperature update exist, implement it
        ###
        if fuelTemperatureCalculation is not None:
            # FIXME Implement this
            pass;
        ###
        # Write new input
        ###
        WriteFile(self.GetFileName('i', withoutTH = (self.GetDepletionStep() >= len(self))), transportFile.GetNewputRaw(), display = self.GetDisplayFiles());
        ###
        return;
    ###
    def Transport(self):
        ###
        # Ensure necessary files do/don't exist
        ###
        AssertFileExists(self.GetFileName('i'));
        for extension in ('o', 'src', 'tpe'):
            RemoveFile(self.GetFileName(extension), display = self.GetDisplayFiles());
        ###
        # Maybe copy mcnp source to .src
        ###
        sourceFileName = self.GetParameter('mcnpSourceFileName');
        if Exists(sourceFileName):
            CopyFile(sourceFileName, self.GetFileName('src'), display = GetDisplayFiles());
        ###
        if self.GetIsDecayStep() or self.GetIsPickleTransmute():
            ###
            # Transport is not requested;
            # Return the input file
            ###
            return McnpInputFile(self.GetFileName('i'));
        else:
            ###
            if 0:
                SystemCall('tar -xvf {}'.format(self.GetFileName('tar')));
            else:
                PrintNow('> Executing MCNP for {}{}'.format(self.GetDepletionString(), ['', '; transport iteration #{:d}'.format(self.GetTransportIteration())][self.GetTransportIteration() > 0]));
                ###
                # Transport is requested;
                # Execute MCNP
                ###
                SystemCall(self.GetParameter('mcnpRunCommand').format(executable = self.GetParameter('mcnpExecutablePath'), baseName = self.GetFileName(), xsdir = self.GetParameter('mcnpXsdirPath')));
            ###
            # Parse transport output file
            ###
            PrintNow('> Parsing MCNP output for {}{}'.format(self.GetDepletionString(), ['', '; transport iteration #{:d}'.format(self.GetTransportIteration())][self.GetTransportIteration() > 0]));
            ###
            transportOutputFile = McnpOutputFile(self.GetFileName('o'));
            ###
            # Populate transport source rate
            ###
            if self.GetParameter('isPowerMode'):
                ###
                # Pth = Pd + Tth * S -> S = (Pth - Pd) / Tth
                ###
                totalThermalPower = self.GetBurnRate() * 1e6;
                delayedThermalPower = sum(self.GetCellNumberDecayPower(cellNumber) for cellNumber in self.GetBurnCells());
                promptThermalPower = sum(float(self.GetCellNumberThermalPower(transportOutputFile, cellNumber, includeDecayHeat = False)) for cellNumber in transportOutputFile.GetPowerCells());
                ###
                sourceRate = (totalThermalPower - delayedThermalPower) / promptThermalPower;
            else:
                trackLengthVolumes = zip(*{cellNumber : self.GetCellNumberTrackLengthVolume(cellNumber) for cellNumber in self.GetTallyIndices('f4')}.values());
                ###
                sourceRate = SafeDivide(SafeDivide(*(float(sum(trackLengthVolume)) for trackLengthVolume in trackLengthVolumes)), self.GetBurnRate());
            ###
            transportOutputFile.PopulateSourceRate(sourceRate);
            ###
            # Maybe print transport output report
            ###
            if self.GetIsVerbose():
                PrintNow(transportOutputFile);
            ###
            return transportOutputFile;
    ###
    def UpdateCoolantDensitys(self, transportOutputFile):
        ###
        # Kick out if density updates are not requested
        ###
        if not self.GetParameter('updateCoolantDensities'):
            return;
        ###
        # Kick out if decay step or transmute-only
        ###
        if self.GetIsDecayStep() or self.GetIsPickleTransmute():
            return;
        ###
        return;
    ###
    def UpdateFuelTemperatures(self, transportOutputFile):
        ###
        # Kick out if temperatures updates are not requested
        ###
        if not self.GetParameter('updateFuelTemperatures'):
            return;
        ###
        # Kick out if decay step or transmute-only
        ###
        if self.GetIsDecayStep() or self.GetIsPickleTransmute():
            return;
        ###
        return;
    ###
    def IncrementTransportIteration(self):
        self.transportIteration += 1;
        ###
        return;
    ###
    def ResetTransportIteration(self):
        ###
        if self.GetEitherUpdate():
            PrintNow('> Transport converged after {:d} iterations {}'.format(self.GetTransportIteration(), self.GetDepletionString()));
            ###
            # Link base file names to final iterations
            ###
            self.transportIteration -= 1;
            ###
            SymbolicLink(self.GetFileName('i'), self.GetFileName('i', withoutTH = True), display = self.GetDisplayFiles());
            ###
            # Transport is not performed for decay steps or pickle transmute
            ###
            if not self.GetIsDecayStep() and not self.GetIsPickleTransmute():
                SymbolicLink(self.GetFileName('o'), self.GetFileName('o', withoutTH = True), display = self.GetDisplayFiles());
        ###
        # Reset transport iteration number
        ###
        self.transportIteration = 0;
        ###
        return;
    ###
    def TransmuteThreads(self, transportOutputFile, currentDir):
        ###
        # Kick out, if this is a transport-only simulation
        ###
        if self.GetDepletionStepTimeInterval() == 0:
            ###
            # Null the cell # -> burnRate, micros, zam2Moles
            ###
            self.cellNumber2BurnRate = self.cellNumber2Zam2Moles = self.cellNumber2Micros = {cellNumber : None for cellNumber in self.GetBurnCells()};
            ###
            # Populate decay heat (delayed β's and γ's)
            ###
            self.depletionStep2CellNumber2DecayPower[self.GetDepletionStep(offset = +1)] = self.depletionStep2CellNumber2DecayPower[self.GetDepletionStep(offset = +0)];
            ###
            return;
        ###
        PrintNow('> Executing {:d} concurrent ORIGEN thread(s) for {}'.format(self.GetParameter('numberOfOrigenThreads'), self.GetDepletionString()));
        ###
        # Multiple concurrent ORIGEN threads for each burn cell
        ###
        self.cellNumber2BurnRate = {};
        ###
        thread = 0;
        threads = len(self.GetBurnCells());
        with Futures.ThreadPoolExecutor(max_workers = self.GetParameter('numberOfOrigenThreads')) as executor:
            future2CellNumber = {executor.submit(self.TransmuteThread, cellNumber, transportOutputFile, currentDir) : cellNumber for cellNumber in self.GetBurnCells()};
            ###
            for future in Futures.as_completed(future2CellNumber):
                if future.exception() is not None:
                    raise(future.exception());
                else:
                    thread += 1;
                    PrintNow('> Completed burning cell #{:d} (thread {:d} of {:d})'.format(future2CellNumber[future], thread, threads));
        ###
        # Extract and attach cell # -> Origen calculation, ZAm -> moles, micros
        ###
        cellNumber2Transmute = {cellNumber : future.result() for future, cellNumber in future2CellNumber.items()};
        self.cellNumber2OrigenCalculation, self.cellNumber2Zam2Moles, self.cellNumber2Micros = [{cellNumber : transmute[index] for cellNumber, transmute in cellNumber2Transmute.items()} for index in range(3)];
        ###
        # Populate decay heat (delayed β's and γ's)
        ###
        self.depletionStep2CellNumber2DecayPower[self.GetDepletionStep(offset = +1)] = {cellNumber : origenCalculation.GetDecayPower(self.GetZa2WattsPerMole()) for cellNumber, origenCalculation in self.GetCellNumber2OrigenCalculation().items()};
        ###
        return;
    ###
    def TransmuteThread(self, cellNumber, transportOutputFile, currentDir):
        ###
        # Find cell
        ###
        cell = transportOutputFile.FindCell(cellNumber);
        ###
        # Move to temporary directory
        ###
        tmpDir = MakeTemporaryDirectory(display = self.GetDisplayFiles());
        ###
        # Write transmutation inputs;
        ###
        zam2Moles, micros = self.PrepareTransmute(transportOutputFile, cell, tmpDir);
        ###
        # Run transmutation calculation;
        # Parse transport results
        ###
        origenCalculation = self.Transmute(cell, tmpDir, currentDir);
        ###
        # Attach micros to origenCalculation
        ###
        origenCalculation.AttachMicros(micros);
        ###
        # Clean up files
        ###
        self.CleanUpFiles(tmpDir);
        ###
        return origenCalculation, zam2Moles, micros;
    ###
    def PrepareTransmute(self, transportOutputFile, cell, tmpDir = './'):
        PrintNow('> Writing transmute input for cell #{:d}'.format(cell.GetNumber()));
        ###
        # Extract cell #
        ###
        cellNumber = cell.GetNumber();
        ###
        # origen (ORIGEN executable)
        ###
        SymbolicLink(self.GetParameter('origenExecutablePath'), '{}origen'.format(tmpDir), display = self.GetDisplayFiles());
        ###
        # TAPE10.INP (default photon library):
        ###
        if self.GetIsPickleTransmute():
            ###
            # This is a pickle transmute cycle, so grab the unpickled TAPE10
            ###
            WriteFile('{}TAPE10.INP'.format(tmpDir), self.GetDepletionStepPickle().GetCellNumberTAPE10(cellNumber), display = self.GetDisplayFiles());
        else:
            WriteFile('{}TAPE10.INP'.format(tmpDir), self.GetDefaultPhotonLibrary(), display = self.GetDisplayFiles());
        ###
        # TAPE4.INP (.pch punch card):
        # Cell moles
        ###
        try:
            ###
            # If TAPE7.OUT exists from a previous ORIGEN calculation,
            # grab zam2Moles from there
            ###
            zam2Moles = {Zaid2Zam(zaid) : moles for zaid, moles in self.GetCellNumber2OrigenCalculation()[cellNumber].GetZaid2Moles().items()};
        except (KeyError, TypeError):
            ###
            # No ORIGEN calculation is performed either for this depletion step, or for this cell
            ###
            zam2Moles = {Za2Zam(za) : moles for za, moles in cell.GetZa2Moles().items()};
        ###
        WriteFile('{}TAPE4.INP'.format(tmpDir), '\n'.join(origenPunchCardTemplate.format(lib = lib % 10, zam = zam, moles = zam2Moles[zam]) for lib, zams in sorted(self.GetLib2Zams().items()) for zam in zams if zam in zam2Moles) + '\n0 0 0 0', display = self.GetDisplayFiles());
        ###
        # TAPE9.INP (default decay and modified cross-section library):
        # Cell microscopic cross-sections
        # Cell zams
        # Cross-section library
        ###
        if self.GetIsDecayStep():
            ###
            # No transport is done, so default libraries are used
            ###
            micros = {};
            ###
            WriteFile('{}TAPE9.INP'.format(tmpDir), self.GetDefaultDecayLibrary() + self.GetDefaultXsLibrary(), display = self.GetDisplayFiles());
        else:
            if self.GetIsPickleTransmute():
                ###
                # This is a pickle transmute cycle, so grab the unpickled micros and TAPE9
                ###
                micros = self.GetDepletionStepPickle().GetCellNumberMicros(cellNumber);
                ###
                WriteFile('{}TAPE9.INP'.format(tmpDir), self.GetDepletionStepPickle().GetCellNumberTAPE9(cellNumber), display = self.GetDisplayFiles());
            else:
                ###
                # Transport-update cross-sections are required;
                # Calculate them from transport results
                ###
                def HelperMicros(zam, micros, mts, excites):
                    ###
                    multipliers = [excite for excite in excites] + [1 - excite for excite in excites] + [1] * 2;
                    ###
                    return [multipliers[index] * micros[(zam, mts[index])] for index in range(-4, 2)];
                ###
                # Extract transmutation cross-sections
                ###
                tallyNumber = self.GetTransmuteTallyNumber();
                tally = next(tally for tally in transportOutputFile.GetTallys('fm4') if tallyNumber == tally.GetNumber());
                micros = {(Zaid2Zam(self.GetMaterialNumberZaid(materialNumber)), reactionNumber) : transportOutputFile.GetCellNumberMicroscopicCrossSection(cellNumber, materialNumber, reactionNumber) for materialNumber, reactionNumber in (tallyBin[2 : ] for tallyBin in tally.GetMultiplierBins() if cellNumber == tallyBin[0]) if materialNumber};
                ###
                cellZams = set(zam for zam, reactionNumber in micros);
                ###
                reXs = ReCompile(r'^ *(\d+) +(\d+)');
                xsLibraryLines = [];
                for line in self.GetDefaultXsLibrary().split('\n'):
                    match = reXs.search(line);
                    ###
                    # Kick out if format line
                    ###
                    if match is None:
                        xsLibraryLines.append(line);
                        ###
                        continue;
                    ###
                    lib, zam = match.groups();
                    ###
                    zam = int(float(zam));
                    if zam in cellZams:
                        lib = int(float(lib));
                        mts = self.GetOrigen2LibMts(lib);
                        ###
                        line = origenXsLibraryTemplate.format(lib = lib, zam = zam, sigma = HelperMicros(zam, micros, mts, self.GetLibZamExcite(lib, zam)));
                    ###
                    xsLibraryLines.append(line);
                ###
                WriteFile('{}TAPE9.INP'.format(tmpDir), self.GetDefaultDecayLibrary() + '\n'.join(xsLibraryLines), display = self.GetDisplayFiles());
        ###
        # TAPE5.INP (.inp instructions):
        # Cross-section library numbers
        # Flux or power mode
        # Inner depletion timestep endtimes
        ###
        if self.GetIsPickleTransmute():
            ###
            # This is a pickle transmute cycle, so grab the unpickled cell burn rate and TAPE5
            ###
            cellBurnRate = self.GetDepletionStepPickle().GetCellNumberBurnRate(cellNumber);
            ###
            WriteFile('{}TAPE5.INP'.format(tmpDir), self.GetDepletionStepPickle().GetCellNumberTAPE5(cellNumber), display = self.GetDisplayFiles());
        else:
            xsLibs = sorted(self.GetLib2Zams().keys());
            ###
            burnMode = self.GetBurnMode();
            if self.GetIsDecayStep():
                ###
                # Decay cell
                ###
                cellBurnRate = 0;
            else:
                ###
                # Burn cell
                ###
                if self.GetParameter('isPowerMode'):
                    ###
                    # Extract ORIGEN power that matches flux magnitudes
                    ###
                    cellBurnRate = transportOutputFile.GetCellNumberOrigenPower(cellNumber, isOrigen2 = self.GetIsOrigen2());
                    ###
                    # Convert powers Wth -> MWth
                    ###
                    cellBurnRate *= 1e-6;
                else:
                    cellBurnRate = float(transportOutputFile.GetCellNumberScalarFlux(cellNumber));
            ###
            timeLapse = self.GetDepletionStepTimeInterval();
            timeSteps = len([line for line in origenInputFileTemplate.split('\n') if 'timeEnds' in line]);
            timeEnds = [timeLapse * (index + 1) / timeSteps for index in range(timeSteps)];
            ###
            WriteFile('{}TAPE5.INP'.format(tmpDir), origenInputFileTemplate.format(xsLibs = xsLibs, burnMode = burnMode, timeEnds = timeEnds, cellBurnRate = cellBurnRate), display = self.GetDisplayFiles());
        ###
        self.cellNumber2BurnRate[cellNumber] = cellBurnRate;
        ###
        return zam2Moles, micros;
    ###
    def Transmute(self, cell, tmpDir = './', currentDir = ''):
        PrintNow('> Burning cell #{:d} at {:10.5E} {:s} in `{:s}\''.format(cell.GetNumber(), self.GetCellNumberBurnRate(cell.GetNumber()), self.GetParameter('burnUnits'), tmpDir));
        ###
        # Ensure necessary files do/don't exist
        ###
        for tapeNumber in (4, 5, 9, 10):
            AssertFileExists('{}TAPE{:d}.INP'.format(tmpDir, tapeNumber));
        ###
        # Execute ORIGEN
        ###
        SystemCall(self.GetParameter('origenRunCommand').format(tmpDir, currentDir));
        ###
        # Parse transmute results
        ###
        return OrigenCalculation(cell.GetSuffix(), cell.GetVolume(), tmpDir);
    ###
    def PickleDepletionStep(self, transportOutputFile):
        PrintNow('> Pickling {}'.format(self.GetDepletionString()));
        ###
        self.depletionStep2DepletionStepPickle[self.GetDepletionStep()] = DepletionStepPickle('{}.{}'.format(self.GetFileName(withoutTH = True), 'pkl'), transportOutputFile, self);
        ###
        return;
    ###
    def UnpickleDepletionStep(self):
        PrintNow('> Unpickling {}'.format(self.GetDepletionString()));
        ###
        extension = 'pkl';
        if self.GetParameter('compressPickles'):
            extension += '.gz';
        ###
        return DepletionStepPickle('{}.{}'.format(self.GetFileName(withoutTH = True), extension));
    ###
    def CleanUpFiles(self, tmpDir = None):
        if tmpDir is None:
            ###
            # Transport files
            ###
            for extension in ('src', 'tpe'):
                RemoveFile(self.GetFileName(extension), display = self.GetDisplayFiles());
        else:
            ###
            # Transmute files
            ###
            for tapeNumber in (3, 4, 5, 9, 10):
                RemoveFile('{}TAPE{:d}.INP'.format(tmpDir, tapeNumber), display = self.GetDisplayFiles());
            ###
            for tapeNumber in (6, 7, 11, 12, 13, 15, 16, 50):
                RemoveFile('{}TAPE{:d}.OUT'.format(tmpDir, tapeNumber), display = self.GetDisplayFiles());
            ###
            RemoveFile('{}origen'.format(tmpDir), display = self.GetDisplayFiles());
            RemoveDirectory(tmpDir, display = self.GetDisplayFiles());
        ###
        return;
    ###
    def IncrementDepletionStep(self):
        self.depletionStep += 1;
        ###
        return;
    ###
    def ProcessFuel(self):
        return None;
    ###
    def MultiplicationFactor(self):
        return [multiplicationFactor for multiplicationFactor in self.GetDepletionCalculationPickle().multiplicationFactors if multiplicationFactor is not None][-1];
    ###
    def MultiplicationFactorSigma(self):
        return [multiplicationFactorSigma for multiplicationFactorSigma in self.GetDepletionCalculationPickle().multiplicationFactorSigmas if multiplicationFactorSigma is not None][-1];
###
# Depletion calculation pickle
###
class DepletionCalculationPickle:
    def __init__(self, args):
        if isinstance(args, str):
            PrintNow('> Unpickling depletion calculation');
            ###
            fileName = args;
            ###
            # Maybe gunzip;
            # Unpickle
            ###
            PrintNow('{} >>'.format(fileName));
            try:
                with open(fileName, 'rb') as f:
                    ###
                    pickle = UnPickle(f);
            except UnpicklingError:
                with GzipOpen(fileName, 'rb') as f:
                    ###
                    pickle = UnPickle(f);
            ###
            # Transfer pickle attributes to instance
            ###
            for attribute in ('cellNumber2BurnRates', 'cellNumber2DecayPowers', 'cellNumber2FissionPowers', 'cellNumber2Micros', 'cellNumber2OrigenFluxes', 'cellNumber2OrigenPowers', 'cellNumber2PromptPowers', 'cellNumber2ScalarFluxes', 'cellNumber2ThermalPowers', 'cellNumber2Volume', 'cellNumber2Zaid2MassDensitys', 'cellNumber2Zaid2NumberDensitys', 'cellNumber2Zam2Moles', 'coolantDensityCalculations', 'fuelTemperatureCalculations', 'mevPerFissions', 'multiplicationFactorSigmas', 'multiplicationFactors', 'neutronsPerFissions', 'parameters', 'powerCells', 'sourceRates'):
                try:
                    setattr(self, attribute, getattr(pickle, attribute));
                except AttributeError:
                    Warning('The depletion calculation pickle was created with an older version of {}'.format(__file__));
        ###
        else:
            PrintNow('> Pickling depletion calculation');
            ###
            depletionCalculation = args;
            ###
            # Input parameters
            ###
            self.parameters = depletionCalculation.GetParameters();
            ###
            # Transport
            ###
            self.cellNumber2Zaid2NumberDensitys = {};
            self.cellNumber2Zaid2MassDensitys = {};
            ###
            self.multiplicationFactors = [];
            self.multiplicationFactorSigmas = [];
            self.neutronsPerFissions = [];
            self.mevPerFissions = [];
            self.sourceRates = [];
            ###
            self.cellNumber2DecayPowers = {};
            self.cellNumber2FissionPowers = {};
            self.cellNumber2PromptPowers = {};
            self.cellNumber2ScalarFluxes = {};
            self.cellNumber2ThermalPowers = {};
            ###
            # Transport convergence
            ###
            self.coolantDensityCalculations = [];
            self.fuelTemperatureCalculations = [];
            ###
            # Transmute
            ###
            self.cellNumber2BurnRates = {};
            self.cellNumber2Micros = {};
            self.cellNumber2OrigenFluxes = {};
            self.cellNumber2OrigenPowers = {};
            self.cellNumber2Zam2Moles = {};
            ###
            # Iterate over depletion steps
            ###
            depletionCalculation.depletionStep = 0;
            while depletionCalculation.GetDepletionStep() <= len(depletionCalculation):
                ###
                # Extract depletion step pickle;
                # Parse transport input file;
                # Maybe parse transport output file
                ###
                depletionStepPickle = depletionCalculation.GetDepletionStepPickle();
                ###
                # Transport
                ###
                self.multiplicationFactors.append(depletionStepPickle.GetMultiplicationFactor());
                self.multiplicationFactorSigmas.append(depletionStepPickle.GetMultiplicationFactorSigma());
                self.neutronsPerFissions.append(depletionStepPickle.GetNeutronsPerFission());
                self.mevPerFissions.append(depletionStepPickle.GetMevPerFission());
                self.sourceRates.append(depletionStepPickle.GetSourceRate());
                ###
                # Transport convergence
                ###
                self.coolantDensityCalculations.append(depletionStepPickle.GetCoolantDensityCalculations());
                self.fuelTemperatureCalculations.append(depletionStepPickle.GetFuelTemperatureCalculations());
                ###
                # Iterate over power cells for transport results
                ###
                for cellNumber in depletionStepPickle.GetPowerCells():
                    ###
                    # Instantiate cell lists
                    ###
                    if 0 == depletionCalculation.GetDepletionStep():
                        self.cellNumber2Zaid2NumberDensitys[cellNumber] = [];
                        self.cellNumber2Zaid2MassDensitys[cellNumber] = [];
                        ###
                        self.cellNumber2DecayPowers[cellNumber] = [];
                        self.cellNumber2FissionPowers[cellNumber] = [];
                        self.cellNumber2PromptPowers[cellNumber] = [];
                        self.cellNumber2ScalarFluxes[cellNumber] = [];
                        self.cellNumber2ThermalPowers[cellNumber] = [];
                    ###
                    self.cellNumber2Zaid2NumberDensitys[cellNumber].append(depletionStepPickle.GetCellNumberZaid2NumberDensity(cellNumber));
                    self.cellNumber2Zaid2MassDensitys[cellNumber].append(depletionStepPickle.GetCellNumberZaid2MassDensity(cellNumber));
                    ###
                    self.cellNumber2DecayPowers[cellNumber].append(depletionStepPickle.GetCellNumberDecayPower(cellNumber));
                    self.cellNumber2FissionPowers[cellNumber].append(depletionStepPickle.GetCellNumberFissionPower(cellNumber));
                    self.cellNumber2PromptPowers[cellNumber].append(depletionStepPickle.GetCellNumberPromptPower(cellNumber));
                    self.cellNumber2ScalarFluxes[cellNumber].append(depletionStepPickle.GetCellNumberScalarFlux(cellNumber));
                    self.cellNumber2ThermalPowers[cellNumber].append(depletionStepPickle.GetCellNumberThermalPower(cellNumber));
                ###
                # Iterate over burn cells for transmute results
                ###
                for cellNumber in self.GetBurnCells():
                    ###
                    # Instantiate cell lists
                    ###
                    if 0 == depletionCalculation.GetDepletionStep():
                        self.cellNumber2BurnRates[cellNumber] = [];
                        self.cellNumber2Micros[cellNumber] = [];
                        self.cellNumber2OrigenFluxes[cellNumber] = [];
                        self.cellNumber2OrigenPowers[cellNumber] = [];
                        self.cellNumber2Zam2Moles[cellNumber] = [];
                    ###
                    if depletionCalculation.GetDepletionStep() == len(depletionCalculation):
                        burnRate = micros = None;
                    else:
                        burnRate = depletionStepPickle.GetCellNumberBurnRate(cellNumber);
                        micros = depletionStepPickle.GetCellNumberMicros(cellNumber);
                    ###
                    if depletionCalculation.GetDepletionStep() == len(depletionCalculation) or depletionCalculation.GetDepletionStepTimeInterval() == 0:
                        origenFlux = origenPower = None;
                    else:
                        origenFlux = depletionStepPickle.GetCellNumberOrigenFlux(cellNumber);
                        origenPower = depletionStepPickle.GetCellNumberOrigenPower(cellNumber);
                    zam2Moles = depletionStepPickle.GetCellNumberZam2Moles(cellNumber);
                    ###
                    self.cellNumber2BurnRates[cellNumber].append(burnRate);
                    self.cellNumber2Micros[cellNumber].append(micros);
                    self.cellNumber2OrigenFluxes[cellNumber].append(origenFlux);
                    self.cellNumber2OrigenPowers[cellNumber].append(origenPower);
                    self.cellNumber2Zam2Moles[cellNumber].append(zam2Moles);
                ###
                # Increment depletion step
                ###
                depletionCalculation.IncrementDepletionStep();
            ###
            self.powerCells = depletionStepPickle.GetPowerCells();
            self.cellNumber2Volume = {cellNumber : depletionStepPickle.GetCellNumberVolume(cellNumber) for cellNumber in self.GetPowerCells()};
            ###
            # Pickle
            ###
            self.Save(baseName = depletionCalculation.GetOriginalTransportFile().GetFileName(), display = depletionCalculation.GetDisplayFiles());
            ###
            # Return depletion step counter to end
            ###
            depletionCalculation.depletionStep -= 1;
        ###
        return;
    ###
    def __len__(self):
        return len(self.GetParameter('depletionStepTimeIntervals')) + 1;
    ###
    def Save(self, baseName, display):
        ###
        # Pickle;
        # Maybe gzip
        ###
        extension = 'pkl';
        if self.GetParameter('compressPickles'):
            extension += '.gz';
        fileName = '{}.{}'.format(baseName, extension);
        ###
        RemoveFile(fileName, display = display);
        PrintNow('{} <<'.format(fileName));
        if self.GetParameter('compressPickles'):
            with GzipOpen(fileName, 'wb', compresslevel = 5) as f:
                f.write(PickleString(self));
        else:
            with open(fileName, 'wb') as f:
                Pickle(self, f);
        ###
        return;
    ###
    # Generic getter methods
    ###
    def GetBurnCells(self):
        return self.GetParameter('burnCells');
    ###
    def GetCellNumberVolume(self, cellNumber):
        return self.cellNumber2Volume[cellNumber];
    ###
    def GetDecayPowers(self):
        return [sum(decayPower for decayPowers in self.cellNumber2DecayPowers.values() for decayPower in [decayPowers[depletionStep]] if decayPower is not None) for depletionStep in range(len(self))];
    ###
    def GetDepletionStepTimeEnds(self):
        return self.GetParameter('depletionStepTimeEnds');
    ###
    def GetDepletionStepTimeIntervals(self):
        return self.GetParameter('depletionStepTimeIntervals');
    ###
    def GetFileName(self):
        return self.fileName;
    ###
    def GetFIMAs(self):
        heavyMetalMoles = [sum(moles for cellNumber in self.GetBurnCells() for zam, moles in self.cellNumber2Zam2Moles[cellNumber][depletionStep].items() if ZaIsActinide(Zam2Za(zam))) for depletionStep in range(len(self))];
        ###
        return [1 - moles / heavyMetalMoles[0] for moles in heavyMetalMoles];
    ###
    def GetFissionPowers(self):
        return [sum(fissionPower for fissionPowers in self.cellNumber2FissionPowers.values() for fissionPower in [fissionPowers[depletionStep]] if fissionPower is not None) for depletionStep in range(len(self))];
    ###
    def GetMultiplicationFactors(self):
        return self.multiplicationFactors;
    ###
    def GetMultiplicationFactorSigmas(self):
        return self.multiplicationFactorSigmas;
    ###
    def GetOrigenFluxes(self):
        cellNumber2Volume = self.cellNumber2Volume;
        return [sum(origenFlux * cellNumber2Volume[cellNumber] for cellNumber, origenFluxes in self.cellNumber2OrigenFluxes.items() for origenFlux in [origenFluxes[depletionStep]] if origenFlux is not None) / sum(cellNumber2Volume.values()) for depletionStep in range(len(self))];
    ###
    def GetOrigenPowers(self):
        return [sum(origenPower for origenPowers in self.cellNumber2OrigenPowers.values() for origenPower in [origenPowers[depletionStep]] if origenPower is not None) for depletionStep in range(len(self))];
    ###
    def GetPromptPowers(self):
        return [sum(promptPower for promptPowers in self.cellNumber2PromptPowers.values() for promptPower in [promptPowers[depletionStep]] if promptPower is not None) for depletionStep in range(len(self))];
    ###
    def GetParameter(self, key):
        return self.GetParameters()[key];
    ###
    def GetParameters(self):
        return self.parameters;
    ###
    def GetPowerCells(self):
        return self.powerCells;
    ###
    def GetScalarFluxes(self):
        cellNumber2Volume = self.cellNumber2Volume;
        return [sum(scalarFlux * cellNumber2Volume[cellNumber] for cellNumber, scalarFluxes in self.cellNumber2ScalarFluxes.items() for scalarFlux in [scalarFluxes[depletionStep]] if scalarFlux is not None) / sum(cellNumber2Volume.values()) for depletionStep in range(len(self))];
    ###
    def GetSourceRates(self):
        return self.sourceRates;
    ###
    def GetThermalPowers(self):
        return [sum(thermalPower for thermalPowers in self.cellNumber2ThermalPowers.values() for thermalPower in [thermalPowers[depletionStep]] if thermalPower is not None) for depletionStep in range(len(self))];
    ###
    def GetZa2Masses(self):
        za2Masses = [];
        for depletionStep in range(len(self)):
            za2Masses.append({});
            for cellNumber in self.GetBurnCells():
                volume = self.GetCellNumberVolume(cellNumber);
                for zaid, massDensity in self.cellNumber2Zaid2MassDensitys[cellNumber][depletionStep].items():
                    try:
                        za2Masses[depletionStep][Zaid2Za(zaid)] += massDensity * volume;
                    except KeyError:
                        za2Masses[depletionStep][Zaid2Za(zaid)] = massDensity * volume;
        ###
        return za2Masses;
    ###
    def GetZa2Moles(self):
        za2Moles = [];
        for depletionStep in range(len(self)):
            za2Moles.append({});
            for cellNumber in self.GetBurnCells():
                for zam, moles in self.cellNumber2Zam2Moles[cellNumber][depletionStep].items():
                    try:
                        za2Moles[depletionStep][Zam2Za(zam)] += moles;
                    except KeyError:
                        za2Moles[depletionStep][Zam2Za(zam)] = moles;
        ###
        return za2Moles;
###
# Depletion step dump
###
class DepletionStepPickle:
    def __init__(self, *args):
        if 3 == len(args):
            ###
            # Pickle data
            ###
            fileName, transportFile, depletionCalculation = args;
            ###
            # General
            ###
            if depletionCalculation.GetParameter('compressPickles'):
                fileName += '.gz';
            self.fileName = fileName;
            self.powerCells = transportFile.GetPowerCells();
            self.cellNumber2Volume = {cellNumber : transportFile.FindCell(cellNumber).GetVolume() for cellNumber in self.GetPowerCells()};
            self.parameters = depletionCalculation.GetParameters();
            self.xsDirZaids = depletionCalculation.GetXsDirZaids();
            ###
            # Transport convergence
            ###
            self.coolantDensityCalculations = depletionCalculation.GetCoolantDensityCalculations();
            self.fuelTemperatureCalculations = depletionCalculation.GetFuelTemperatureCalculations();
            ###
            # Transmute
            ###
            cellNumber2BurnRate = depletionCalculation.GetCellNumber2BurnRate();
            cellNumber2OrigenCalculation = depletionCalculation.GetCellNumber2OrigenCalculation();
            cellNumber2Micros = depletionCalculation.GetCellNumber2Micros();
            cellNumber2Zam2Moles = depletionCalculation.GetCellNumber2Zam2Moles();
            ###
            if depletionCalculation.GetDepletionStep() == len(depletionCalculation) and cellNumber2OrigenCalculation is not None:
                cellNumber2Zam2Moles = {cellNumber : {Zaid2Zam(zaid) : moles for zaid, moles in origenCalculation.GetZaid2Moles().items()} for cellNumber, origenCalculation in cellNumber2OrigenCalculation.items()};
            ###
            self.cellNumber2BurnRate = cellNumber2BurnRate;
            self.cellNumber2OrigenCalculation = cellNumber2OrigenCalculation;
            self.cellNumber2Micros = cellNumber2Micros;
            self.cellNumber2Zam2Moles = cellNumber2Zam2Moles;
            ###
            # Transport input
            ###
            self.transportInputRaw = transportFile.GetInputRaw();
            ###
            self.cellNumber2Zaid2NumberDensity = {cellNumber : transportFile.FindCell(cellNumber).GetZaid2NumberDensity() for cellNumber in self.GetPowerCells()};
            self.cellNumber2Zaid2MassDensity = {cellNumber : transportFile.FindCell(cellNumber).GetZaid2MassDensity() for cellNumber in self.GetPowerCells()};
            ###
            # Transport output
            ###
            if depletionCalculation.GetDepletionStep() == len(depletionCalculation) or depletionCalculation.GetIsDecayStep() or depletionCalculation.GetIsPickleTransmute():
                self.transportOutputRaw = None;
                ###
                self.multiplicationFactor = self.multiplicationFactorSigma = self.neutronsPerFission = self.mevPerFission = self.sourceRate = None;
                ###
                self.cellNumber2DecayPower = self.cellNumber2FissionPower = self.cellNumber2NextDecayPower = self.cellNumber2ScalarFlux = self.cellNumber2PromptPower = self.cellNumber2ThermalPower = {cellNumber : None for cellNumber in self.GetPowerCells()};
            else:
                self.transportOutputRaw = transportFile.GetOutputRaw();
                ###
                self.multiplicationFactor = transportFile.GetMultiplicationFactor();
                self.multiplicationFactorSigma = transportFile.GetMultiplicationFactorSigma();
                self.neutronsPerFission = transportFile.GetNeutronsPerFission();
                self.mevPerFission = transportFile.GetMevPerFission();
                self.sourceRate = transportFile.GetSourceRate(realSourceRate = True);
                ###
                self.cellNumber2DecayPower = {cellNumber : depletionCalculation.GetCellNumberDecayPower(cellNumber, offset = +0) for cellNumber in self.GetPowerCells()};
                self.cellNumber2NextDecayPower = {cellNumber : depletionCalculation.GetCellNumberDecayPower(cellNumber, offset = +1) for cellNumber in self.GetPowerCells()};
                self.cellNumber2FissionPower = {cellNumber : float(transportFile.GetCellNumberFissionPower(cellNumber)) for cellNumber in self.GetPowerCells()};
                self.cellNumber2ScalarFlux = {cellNumber : float(transportFile.GetCellNumberScalarFlux(cellNumber)) for cellNumber in self.GetPowerCells()};
                self.cellNumber2PromptPower = {cellNumber : depletionCalculation.GetCellNumberThermalPower(transportFile, cellNumber, includeDecayHeat = False) for cellNumber in self.GetPowerCells()};
                self.cellNumber2ThermalPower = {cellNumber : depletionCalculation.GetCellNumberThermalPower(transportFile, cellNumber, includeDecayHeat = True) for cellNumber in self.GetPowerCells()};
            ###
            # Pickle;
            # Maybe gzip
            ###
            RemoveFile(fileName, display = depletionCalculation.GetDisplayFiles());
            PrintNow('{} <<'.format(fileName));
            if depletionCalculation.GetParameter('compressPickles'):
                with GzipOpen(fileName, 'wb', compresslevel = 5) as f:
                    f.write(PickleString(self));
            else:
                with open(fileName, 'wb') as f:
                    Pickle(self, f);
        ###
        elif 1 == len(args):
            ###
            # Unpickle data
            ###
            fileName, = args;
            ###
            # Maybe gunzip;
            # Unpickle
            ###
            PrintNow('{} >>'.format(fileName));
            try:
                with open(fileName, 'rb') as f:
                    ###
                    pickle = UnPickle(f);
            except UnpicklingError:
                with GzipOpen(fileName, 'rb') as f:
                    ###
                    pickle = UnPickle(f);
            ###
            # Transfer pickle attributes to instance
            ###
            for attribute in ('cellNumber2BurnRate', 'cellNumber2DecayPower', 'cellNumber2FissionPower', 'cellNumber2NextDecayPower', 'cellNumber2Micros', 'cellNumber2OrigenCalculation', 'cellNumber2PromptPower', 'cellNumber2ScalarFlux', 'cellNumber2ThermalPower', 'cellNumber2Volume', 'cellNumber2Zaid2NumberDensity', 'cellNumber2Zaid2MassDensity', 'cellNumber2Zam2Moles', 'coolantDensityCalculations', 'fileName', 'fuelTemperatureCalculations', 'parameters', 'mevPerFission', 'multiplicationFactor', 'multiplicationFactorSigma', 'neutronsPerFission', 'powerCells', 'sourceRate', 'transportInputRaw', 'transportOutputRaw', 'xsDirZaids'):
                try:
                    setattr(self, attribute, getattr(pickle, attribute));
                except AttributeError:
                    Warning('The depletion step pickle was created with an older version of {}'.format(__file__));
        ###
        return;
    ###
    # Generic getter methods
    ###
    def GetBurnCells(self):
        return self.GetParameter('burnCells');
    ###
    def GetCellNumberBurnRate(self, cellNumber):
        return self.cellNumber2BurnRate[cellNumber];
    ###
    def GetCellNumberDecayPower(self, cellNumber):
        return self.GetCellNumber2DecayPower()[cellNumber];
    ###
    def GetCellNumber2DecayPower(self):
        return self.cellNumber2DecayPower;
    ###
    def GetCellNumberFissionPower(self, cellNumber):
        return self.cellNumber2FissionPower[cellNumber];
    ###
    def GetCellNumber2NextDecayPower(self):
        return self.cellNumber2NextDecayPower;
    ###
    def GetCellNumberOrigenCalculation(self, cellNumber):
        return self.cellNumber2OrigenCalculation[cellNumber];
    ###
    def GetCellNumberOrigenFlux(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetFlux();
    ###
    def GetCellNumberOrigenPower(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetPower();
    ###
    def GetCellNumberPromptPower(self, cellNumber):
        return self.cellNumber2PromptPower[cellNumber];
    ###
    def GetCellNumberMicros(self, cellNumber):
        return self.cellNumber2Micros[cellNumber];
    ###
    def GetCellNumberScalarFlux(self, cellNumber):
        return self.cellNumber2ScalarFlux[cellNumber];
    ###
    def GetCellNumberTAPE4(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetTAPE4();
    ###
    def GetCellNumberTAPE5(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetTAPE5();
    ###
    def GetCellNumberTAPE6(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetTAPE6();
    ###
    def GetCellNumberTAPE7(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetTAPE7();
    ###
    def GetCellNumberTAPE9(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetTAPE9();
    ###
    def GetCellNumberTAPE10(self, cellNumber):
        return self.GetCellNumberOrigenCalculation(cellNumber).GetTAPE10();
    ###
    def GetCellNumberThermalPower(self, cellNumber):
        return self.cellNumber2ThermalPower[cellNumber];
    ###
    def GetCellNumberVolume(self, cellNumber):
        return self.cellNumber2Volume[cellNumber];
    ###
    def GetCellNumberZaid2NumberDensity(self, cellNumber):
        return self.cellNumber2Zaid2NumberDensity[cellNumber];
    ###
    def GetCellNumberZaid2MassDensity(self, cellNumber):
        return self.cellNumber2Zaid2MassDensity[cellNumber];
    ###
    def GetCellNumberZam2Moles(self, cellNumber):
        return self.cellNumber2Zam2Moles[cellNumber];
    ###
    def GetCoolantDensityCalculations(self):
        return self.coolantDensityCalculations;
    ###
    def GetDepletionStepTimeEnds(self):
        return self.GetParameter('depletionStepTimeEnds');
    ###
    def GetDepletionStepTimeIntervals(self):
        return self.GetParameter('depletionStepTimeIntervals');
    ###
    def GetFileName(self):
        return self.fileName;
    ###
    def GetFuelTemperatureCalculations(self):
        return self.fuelTemperatureCalculations;
    ###
    def GetParameter(self, key):
        return self.GetParameters()[key];
    ###
    def GetParameters(self):
        return self.parameters;
    ###
    def GetMevPerFission(self):
        return self.mevPerFission;
    ###
    def GetMultiplicationFactor(self):
        return self.multiplicationFactor;
    ###
    def GetMultiplicationFactorSigma(self):
        return self.multiplicationFactorSigma;
    ###
    def GetNeutronsPerFission(self):
        return self.neutronsPerFission;
    ###
    def GetPowerCells(self):
        return self.powerCells;
    ###
    def GetTransportInputRaw(self):
        return self.transportInputRaw;
    ###
    def GetTransportOutputRaw(self):
        return self.transportOutputRaw;
    ###
    def GetSourceRate(self):
        return self.sourceRate;
###
# Fuel temperature calculation results
###
class FuelTemperatureCalculation:
    def __init__(self):
        return;
###
# Material composition
###
class MaterialComposition:
    def __init__(self, materialDensity, isotope2Fraction):
        fractionSum = sum(isotope2Fraction.values());
        ###
        # Determine if isotopes are expressed as isotope's or za's for molar mass lookup
        # Extract ZAs
        # Determine most frequent library suffix
        ###
        isotope = next(iter(isotope2Fraction));
        if isinstance(isotope, str):
            MolarMass = Zaid2MolarMass;
            ###
            self.zas = sorted(Zaid2Za(zaid) for zaid in isotope2Fraction);
            ###
            suffixes = [isotope.split('.')[-1] for isotope in isotope2Fraction];
            count2Suff = {suffixes.count(suffix) : suffix for suffix in set(suffixes)};
            self.suffix = count2Suff[max(count2Suff)];
        elif isinstance(isotope, int):
            MolarMass = lambda za: za2MolarMass[za];
            ###
            self.zas = sorted(isotope2Fraction);
            ###
            self.suffix = None;
        ###
        # Calculate isotope -> a, w
        ###
        self.isotope2AtomFraction = {};
        self.isotope2WeightFraction = {};
        ###
        if all(fraction > 0 for fraction in isotope2Fraction.values()):
            ###
            # Atom fractions are provided
            ###
            mix = sum(atomFraction * MolarMass(isotope) for isotope, atomFraction in isotope2Fraction.items()) / fractionSum;
            for isotope, atomFraction in isotope2Fraction.items():
                ###
                # Atom fraction
                ###
                atomFraction /= fractionSum;
                self.isotope2AtomFraction[isotope] = atomFraction;
                ###
                # Weight fraction
                ###
                molarMass = MolarMass(isotope);
                weightFraction = atomFraction * molarMass / mix;
                self.isotope2WeightFraction[isotope] = weightFraction;
            ###
            # Cell molar mass
            ###
            self.cellMolarMass = atomFraction * molarMass / weightFraction;
        elif all(fraction < 0 for fraction in isotope2Fraction.values()):
            ###
            # Weight fractions are provided
            ###
            for isotope, weightFraction in isotope2Fraction.items():
                ###
                # Weight fraction
                ###
                weightFraction /= fractionSum;
                self.isotope2WeightFraction[isotope] = weightFraction;
            fractionSum = abs(fractionSum);
            ###
            # Cell molar mass
            ###
            self.cellMolarMass = fractionSum / sum(weightFraction / MolarMass(isotope) for isotope, weightFraction in self.isotope2WeightFraction.items());
            ###
            for isotope, weightFraction in self.isotope2WeightFraction.items():
                weightFraction = weightFraction;
                ###
                # Atom fraction
                ###
                molarMass = MolarMass(isotope);
                atomFraction = weightFraction / fractionSum * self.cellMolarMass / molarMass;
                self.isotope2AtomFraction[isotope] = atomFraction;
        ###
        # Calculate ρ [g/cm³], N [a/b·cm], isotope -> ρ, N
        ###
        self.isotope2MassDensity = {};
        self.isotope2NumberDensity = {};
        ###
        if materialDensity > 0:
            ###
            # Given cell number density
            ###
            self.numberDensity = abs(materialDensity);
            for isotope in isotope2Fraction:
                atomFraction = self.isotope2AtomFraction[isotope];
                ###
                # Number density
                ###
                numberDensity = atomFraction * self.numberDensity;
                self.isotope2NumberDensity[isotope] = numberDensity;
                ###
                # Mass density
                ###
                molarMass = MolarMass(isotope);
                massDensity = numberDensity * molarMass / avogadrosNumber;
                self.isotope2MassDensity[isotope] = massDensity;
            ###
            # Cell mass density
            ###
            self.massDensity = sum(self.isotope2MassDensity.values());
        elif materialDensity < 0:
            ###
            # Given cell mass density
            ###
            self.massDensity = abs(materialDensity);
            for isotope in isotope2Fraction:
                weightFraction = self.isotope2WeightFraction[isotope];
                ###
                # Mass density
                ###
                massDensity = weightFraction * self.massDensity;
                self.isotope2MassDensity[isotope] = massDensity;
                ###
                # Number density
                ###
                molarMass = MolarMass(isotope);
                numberDensity = massDensity * avogadrosNumber / molarMass;
                self.isotope2NumberDensity[isotope] = numberDensity;
            ###
            # Cell number density
            ###
            self.numberDensity = sum(self.isotope2NumberDensity.values());
        ###
        return;
###
# MocDown input file
###
class MocDownInputFile:
    def __init__(self, arguments):
        self.fileName = None or hasattr(arguments, 'mocDownInputFileName') and arguments.mocDownInputFileName;
        ###
        # Maybe read file
        ###
        try:
            AssertFileExists(self.GetFileName());
            ###
            self.inputRaw = ReadFile(self.GetFileName(), display = not bool(arguments.isQuiet));
        except IOError:
            self.inputRaw = '';
        ###
        self.Populate();
        ###
        if bool(arguments.isVerbose):
            PrintNow(self);
        ###
        return;
    ###
    def __len__(self):
        if self.GetParameter('isPredictorMode'):
            return self.GetParameter('depletionStepTimeIntervals') * (self.GetParameter('numberOfPredictorSteps') + self.GetParameter('numberOfCorrectorSteps'));
        ###
        return len(self.GetParameter('depletionStepTimeIntervals'));
    ###
    def __str__(self):
        lines = ['< MocDown input summary for `{}\' >'.format(self.GetFileName())];
        ###
        for key, value in sorted(self.GetParameters().items()):
            lines.append('{:<38s} = {:>38}'.format(key, repr(value)));
        ###
        return '\n'.join('{:^89}'.format(line) for line in lines);
    ###
    # Generic getter methods
    ###
    def GetFileName(self):
        return self.fileName;
    ###
    def GetInputRaw(self):
        return self.inputRaw;
    ###
    def GetParameter(self, key):
        return self.GetParameters()[key];
    ###
    def GetParameters(self):
        return self.parameters;
    ###
    # Population methods
    ###
    def Populate(self):
        ###
        # Default parameter values
        ###
        self.parameters = {
            # (#,#,...):(#,#, ...), ...
            'assemblyFuelsToCools' : [],
            # [#]
            'burnCells' : [],
            # T/F
            'compressPickles' : True,
            # [#]
            'coolantBypassCells' : [],
            # #
            'coolantDensityDampingCoefficient' : 1,
            # [m²]
            'coolantFlowArea' : 0.030115717,
            # [m]
            'coolantFlowLengths' : [],
            # [m]
            'coolantHeatedDiameter' : 0.004692958,
            # [m]
            'coolantHydraulicDiameter' : 0.00397346,
            # [MPa]
            'coolantInletPressure' : 7.25,
            # [K]
            'coolantInletTemperature' : 555.71,
            # [kg/s]
            'coolantMassFlowRate' : 29.68,
            # ''
            'criticalPowerRatioCorrelation' : 'm-cise',
            # #
            'criticalPowerRatioFallbackIndex' : 41,
            # #
            'criticalPowerRatioLimit' : 1.3,
            # ''
            'defaultDecayLibrary' : 'decay',
            # ''
            'defaultPhotonLibrary' : 'gxuo2brm',
            # ''
            'defaultXsLibrary' : 'pwru50',
            # [n/cm²·s]
            'depletionStepFluxes' : [],
            # [MWth]
            'depletionStepPowers' : [],
            # [days]
            'depletionStepTimeIntervals' : [],
            # [years]
            'depletionTerminalDecayTime' : None,
            # [n/cm²·s]
            'depletionFlux' : None,
            # [MWth]
            'depletionPower' : None,
            # [days]
            'depletionTime' : None,
            # T/F
            'forceDecayTransport' : False,
            # T/F
            'includeDecayHeat' : True,
            # ''
            'isotopicsConvergenceNormType' : 'inf',
            # #
            'isotopicsConvergenceTolerance' : 1e-5,
            # [MWd/MTHM]
            'maximumBurnupStep' : 5e3,
            # [n/cm²] # FIXME Pick reasonable numbers!
            'maximumFluenceStep' : 8e21,
            # ''
            'mcnpExecutablePath' : '/usr/local/LANL/MCNP6/bin/mcnp6.mpi',
            # ''
            'mcnpRunCommand' : 'DATAPATH="" ; srun {executable} tasks 6 i={baseName}.i me={baseName}.mesh o={baseName}.o r={baseName}.tpe s={baseName}.src x={xsdir} >> transport.log 2>&1 ;',
            # ''
            'mcnpSourceFileName' : 'source',
            # ''
            'mcnpXsdirPath' : '/usr/local/LANL/MCNP_BINDATA/xsdir',
            # [MWd/MTHM]
            'minimumBurnupStep' : 2e2,
            # [g/cm³]
            'minimumCellMassDensityCutoff' : 1e-3,
            # [n/cm²] # FIXME Pick reasonable numbers!
            'minimumFluenceStep' : 3e20,
            # #
            'minimumIsotopeCutoff' : 1e-8,
            # #
            'multiplicationFactorConvergenceTolerance' : 100e-5,
            # #
            'numberOfPredictorSteps' : 0,
            # #
            'numberOfCorrectorSteps' : 0,
            # #
            'numberOfOrigenThreads' : 1,
            # ''
            'origenExecutablePath' : '/usr/local/ORIGEN/bin/o2_fast',
            # ''
            'origenLibraryPathTemplate' : '/usr/local/ORIGEN/libs/{}.lib',
            # ''
            'origenRunCommand' : 'cd {} ; ./origen >> {}transmute.log 2>&1',
            # ''
            'pressureDropCorrelation' : 'epri',
            # ''
            'qValueMethod' : 'origens',
            # T/F
            'recycleToEquilibrium' : False,
            # ['']
            'supplementaryMocdownLibrary' : [],
            # ''
            'thermalHydraulicConvergenceNormType' : '2',
            # #
            'thermalHydraulicConvergenceTolerance' : 5e-2,
            # T/F
            'updateCoolantDensities' : False,
            # T/F
            'updateFuelTemperatures' : False,
            # ''
            'voidFractionCorrelation' : 'relap',
        };
        ###
        # Custom parameter values
        ###
        reComments = ReCompile(r'\s*#.*', 2 | 8);
        for line in self.GetInputRaw().split('\n'):
            line = line.strip();
            ###
            # Remove comments
            ###
            line = reComments.sub('', line);
            ###
            # Kick out blank and commented lines
            ###
            if not line:
                continue;
            ###
            # Extract key and value(s)
            ###
            key, *value = line.split('=');
            key = ''.join(word.lower().capitalize() for word in key.split());
            key = key[0].lower() + key[1 : ];
            ###
            value = '='.join(value);
            values = [value.strip('[,];') for value in value.split() for value in value.split(',')];
            ###
            # Convert list and string parameters
            ###
            if key in ('burnCells', 'coolantBypassCells'):
                value = [];
                for index in range(len(values)):
                    if '..' in values[index]:
                        lo, hi = values[index].split('.')[0 : 3 : 2];
                        value.extend(range(int(float(lo)), int(float(hi)) + 1));
                    else:
                        value.append(int(float(values[index].strip(','))));
            elif key in ('coolantFlowLengths', ):
                value = [];
                for index in range(len(values)):
                    if 'r' in values[index]:
                        repeat, number = values[index].split('r');
                        value.extend([float(number)] * int(float(repeat)));
                    else:
                        value.append(float(values[index].strip(',')));
                ###
                assert(all(v > 0 for v in value));
            elif key in ('depletionStepFluxes', 'depletionStepPowers', 'depletionStepTimeIntervals'):
                value = [float(value) for value in values];
            elif key in ('mcnpRunCommand', 'origenRunCommand'):
                value = value.strip(' ;') + ' ;';
            elif key in ('assemblyFuelsToCools', ):
                value = value.split(',');
            else:
                value = ''.join(value.split());
            ###
            # Convert mapping parameters
            ###
            if key in ('assemblyFuelsToCools', ):
                value = tuple({tuple(int(float(fuel)) for fuel in fuels.strip('( )').split()) : tuple(int(float(cool)) for cool in cools.strip('( )').split())} for fuels2Cools in value for fuels, cools in [fuels2Cools.split(':')]);
            ###
            # Convert bool parameters
            ###
            if key in ('compressPickles', 'forceDecayTransport', 'includeDecayHeat', 'recycleToEquilibrium', 'updateCoolantDensities', 'updateFuelTemperatures'):
                value = bool(int(value));
            ###
            # Convert float parameters
            ###
            if key in ('coolantDensityDampingCoefficient', 'coolantFlowArea', 'coolantHeatedDiameter', 'coolantHydraulicDiameter', 'coolantInletPressure', 'coolantInletTemperature', 'coolantMassFlowRate', 'criticalPowerRatioLimit', 'depletionTerminalDecayTime', 'depletionFlux', 'depletionPower', 'depletionTime', 'isotopicsConvergenceTolerance', 'maximumBurnupStep', 'maximumFluenceStep', 'minimumBurnupStep', 'minimumCellMassDensityCutoff', 'minimumFluenceStep', 'minimumIsotopeCutoff', 'multiplicationFactorConvergenceTolerance', 'thermalHydraulicConvergenceTolerance'):
                value = float(value);
            ###
            # Convert int parameters
            ###
            if key in ('criticalPowerRatioFallbackIndex', 'numberOfPredictorSteps', 'numberOfCorrectorSteps', 'numberOfOrigenThreads'):
                value = int(float(value));
            ###
            # Convert lower parameters
            ###
            if key in ('criticalPowerRatioCorrelation', 'isotopicsConvergenceNormType', 'pressureDropCorrelation', 'thermalHydraulicConvergenceNormType', 'voidFractionCorrelation'):
                value = value.lower();
            ###
            # Only allow for defined parameters
            ###
            assert(key in self.GetParameters());
            ###
            if key in ('assemblyFuelsToCools', 'supplementaryMocdownLibrary'):
                self.parameters[key].append(value);
            else:
                self.parameters[key] = value;
        ###
        # Determine isPredictorMode
        ###
        self.parameters['isPredictorMode'] = bool(self.GetParameter('numberOfPredictorSteps')) and bool(self.GetParameter('numberOfCorrectorSteps'));
        ###
        # Error checking for depletion step times and powers/fluxes
        ###
        if self.GetParameter('depletionStepTimeIntervals'):
            ###
            # Time intervals are provided;
            ###
            assert(self.GetParameter('depletionTime') is None);
            ###
            if bool(self.GetParameter('depletionStepFluxes')):
                ###
                # Fluxes are provided
                # Error check
                ###
                assert(not(self.GetParameter('depletionStepPowers')) and self.GetParameter('depletionFlux') is None and self.GetParameter('depletionPower') is None);
                ###
                assert(len(self) == len(self.GetParameter('depletionStepPowers')));
            elif bool(self.GetParameter('depletionStepPowers')):
                ###
                # Powers are provided;
                # Error check
                ###
                assert(not(self.GetParameter('depletionStepFluxes')) and self.GetParameter('depletionFlux') is None and self.GetParameter('depletionPower') is None);
                ###
                assert(len(self) == len(self.GetParameter('depletionStepPowers')));
            elif self.GetParameter('depletionFlux') is not None:
                ###
                # Single flux is provided;
                # Error check and populate
                ###
                assert(self.GetParameter('depletionPower') is None);
                ###
                self.parameters['depletionStepFluxes'] = [self.GetParameter('depletionFlux')] * len(self);
            elif self.GetParameter('depletionPower') is not None:
                ###
                # Single power is provided;
                # Error check and populate
                ###
                assert(self.GetParameter('depletionFlux') is None);
                ###
                self.parameters['depletionStepPowers'] = [self.GetParameter('depletionPower')] * len(self);
            ###
            # Maybe append decay step
            ###
            if bool(self.GetParameter('depletionTerminalDecayTime')):
                ###
                # Decay time
                ###
                self.parameters['depletionStepTimeIntervals'].append(self.GetParameter('depletionTerminalDecayTime') * daysPerYear);
                ###
                # Power or flux
                ###
                if bool(self.GetParameter('depletionStepPowers')) or bool(self.GetParameter('depletionPower')):
                    self.parameters['depletionStepPowers'].append(0);
                else:
                    self.parameters['depletionStepFluxes'].append(0);
        elif bool(self.GetParameter('depletionTime')):
            ###
            # Only total depletion time is provided;
            # Depletion step powers/fluxes will be populated within the DepletionCalculation
            ###
            if bool(self.GetParameter('depletionFlux')):
                ###
                # Single flux is provided
                ###
                assert(not(self.GetParameter('depletionStepFluxes')) and not(self.GetParameter('depletionStepPowers')) and self.GetParameter('depletionPower') is None);
            elif bool(self.GetParameter('depletionPower')):
                ###
                # Single power is provided
                ###
                assert(not(self.GetParameter('depletionStepFluxes')) and not(self.GetParameter('depletionStepPowers')) and self.GetParameter('depletionFlux') is None);
        ###
        # Determine isPowerMode
        ###
        self.parameters['isPowerMode'] = (self.GetParameter('depletionStepPowers') is not None) or (self.GetParameter('depletionPower') is not None);
        ###
        # Determine burnUnits
        ###
        self.parameters['burnUnits'] = ['n/cm²·s', 'MWth'][self.GetParameter('isPowerMode')];
        ###
        return;
###
# MCNP card
###
class McnpCard:
    def __init__(self, raw):
        self.raw = raw;
        ###
        self.Populate();
        return;
    ###
    def __hash__(self):
        return self.GetNumber();
    ###
    def __lt__(self, other):
        assert(isinstance(other, self.__class__));
        return self.GetNumber() < other.GetNumber();
    ###
    def __str__(self):
        return self.GetRaw();
    ###
    # Generic getter methods
    ###
    def GetRaw(self):
        return self.raw;
    ###
    def GetNumber(self):
        return self.number;
    ###
    # Regular expression builder
    ###
    def GetRegex(self):
        output = '\n' + self.GetRaw();
        ###
        # Escape special regex characters
        ###
        for character in r'().+-*?':
            output = output.replace(character, r'\{}'.format(character));
        ###
        # Clean up spaces
        ###
        output = ReCompile(r' +').sub(r'[\s&]+', output);
        ###
        return ReCompile(output);
    ###
    # Population methods
    ###
    def Populate(self):
        return;
###
# MCNP cell
###
class McnpCell(McnpCard):
    ###
    # Generic getter methods
    ###
    def GetFillUniverse(self):
        return self.fillUniverse;
    ###
    def GetHeavyMetalMT(self):
        return self.GetMass() / 1e6 * sum(weightFraction for zaid, weightFraction in self.GetZaid2WeightFraction().items() if ZaIsActinide(Zaid2Za(zaid)));
    ###
    def GetImportance(self):
        return self.importance;
    ###
    def GetLatticeType(self):
        return self.latticeType;
    ###
    def GetMass(self):
        return self.GetMassDensity() * self.GetVolume();
    ###
    def GetMassDensity(self):
        return self.massDensity;
    ###
    def GetMaterialDensity(self):
        return self.materialDensity;
    ###
    def GetMaterialDensityRegex(self):
        return self.materialDensityRegex;
    ###
    def GetMaterialNumber(self):
        return self.materialNumber;
    ###
    def GetMoles(self):
        return self.numberDensity * self.GetVolume() / avogadrosNumber;
    ###
    def GetNumberDensity(self):
        return self.numberDensity;
    ###
    def GetSuffix(self):
        return self.suffix;
    ###
    def GetSurfaceNumbers(self):
        return self.surfaceNumbers;
    ###
    def GetTemperature(self):
        return self.temperature;
    ###
    def GetTemperatureRegex(self):
        return self.temperatureRegex;
    ###
    def GetUniverse(self):
        return self.universe;
    ###
    def GetVolume(self):
        return self.volume;
    ###
    def GetZa2Moles(self):
        volume = self.GetVolume();
        za2Moles = {};
        for zaid, numberDensity in self.GetZaid2NumberDensity().items():
            za = Zaid2Za(zaid);
            moles = numberDensity * volume / avogadrosNumber;
            ###
            try:
                za2Moles[za] += moles;
            except KeyError:
                za2Moles[za] = moles;
        ###
        return za2Moles;
    ###
    def GetZaid2AtomFraction(self):
        return self.zaid2AtomFraction;
    ###
    def GetZaidMass(self, zaid):
        return self.GetZaidMassDensity(zaid) * self.GetVolume();
    ###
    def GetZaidMassDensity(self, zaid):
        return self.GetZaid2MassDensity()[zaid];
    ###
    def GetZaid2MassDensity(self):
        return self.zaid2MassDensity;
    ###
    def GetZaidMoles(self, zaid):
        return self.GetZaidNumberDensity(zaid) * self.GetVolume() / avogadrosNumber;
    ###
    def GetZaidNumberDensity(self, zaid):
        return self.GetZaid2NumberDensity()[zaid];
    ###
    def GetZaid2NumberDensity(self):
        return self.zaid2NumberDensity;
    ###
    def GetZaid2WeightFraction(self):
        return self.zaid2WeightFraction;
    ###
    def GetZaids(self):
        return sorted(self.zaid2AtomFraction);
    ###
    # Population methods
    ###
    def Populate(self):
        cellNumber, materialNumber, materialDensity, surfaceNumbers, junk, parameters, junk = ReCompile(r'^(\d{1,8}\s+)(\d{1,8}\s+)([\d\.e+\-]+\s+)?((:?[+\-]?\d{1,8}\s*)*)((.|\n)+)$', 2 | 8).search(self.GetRaw()).groups();
        ###
        # cell number, material number, material density, surface numbers, material density regex
        ###
        self.number = int(float(cellNumber));
        self.materialNumber = int(float(materialNumber));
        ###
        if not self.GetMaterialNumber() and materialDensity is not None:
            ###
            # Material density stole a surface!
            # When the material number is null, the density is absent, so the first surface is grabbed by the material density
            ###
            surfaceNumbers = '{} {}'.format(materialDensity, surfaceNumbers);
            materialDensity = None;
        ###
        if materialDensity is not None:
            regex = materialDensity.replace(' ', '');
            ###
            # Escape special regex characters
            ###
            for character in r'.+-':
                regex = regex.replace(character, r'\{}'.format(character));
            self.materialDensityRegex = ReCompile(regex);
            ###
            materialDensity = float(materialDensity);
        ###
        self.materialDensity = materialDensity;
        self.surfaceNumbers = [int(float(surface)) for surface in surfaceNumbers.replace(':', ' ').split()];
        ###
        # Optional parameters
        ###
        parameters = ReCompile(r'(imp|vol|pwt|ext|fcl|wwn|dxc|nonu|pd|tmp|u|trcl|lat|fill)', 2 | 8).split(parameters)[1 : ];
        parameters = {parameters[index].lower() : parameters[index + 1] for index in range(0, len(parameters) - 1, 2)};
        ###
        # importance, volume, temperature, temperature regex, universe, lattice type, fill universe
        ###
        self.importance = 1;
        self.volume = 0;
        self.temperature = 0;
        regex = '';
        self.universe = None;
        self.latticeType = None;
        self.fillUniverse = None;
        ###
        for key, value in parameters.items():
            keyValue = key + value;
            value = value.replace('=', ' ');
            if 'imp' == key:
                self.importance = float(value.split()[-1]);
            elif 'vol' == key:
                self.volume = float(value);
            elif 'tmp' == key:
                regex = keyValue;
                self.temperature = float(value);
            elif 'u' == key:
                self.universe = int(float(value));
            elif 'lat' == key:
                self.latticeType = int(float(value));
#            elif 'fill' == key: # FIXME
#                self.fillUniverse = int(float(value)); # FIXME
        ###
        # Escape special regex characters
        ###
        for character in r'.+-':
            regex = regex.replace(character, r'\{}'.format(character));
        self.temperatureRegex = ReCompile(regex);
        ###
        return;
###
# MCNP surface
###
class McnpSurface(McnpCard):
    ###
    # Generic getter methods
    ###
    def GetMnemonic(self):
        return self.mnemonic;
    ###
    # Population methods
    ###
    def Populate(self):
        surfaceNumber, transformationNumber, mnemonic, parameters = ReCompile(r'^[+\*]?(\d{1,8}\s+)([+\-]?\d{1,3}\s+)?([psckgthr][ep/]?[oxyzqp]?\s+)(.+)$', 2 | 8).search(self.GetRaw()).groups();
        ###
        # surface number, transformation number, mnemonic
        ###
        self.number = int(float(surfaceNumber));
        if transformationNumber != None:
            transformationNumber = int(float(transformationNumber));
        self.transformationNumber = transformationNumber;
        self.mnemonic = mnemonic.strip().lower();
        ###
        # geometric parameters
        ###
        self.parameters = [float(parameter) for parameter in parameters.split()];
        return;
###
# MCNP material
###
class McnpMaterial(McnpCard):
    def __len__(self):
        return len(self.GetZaid2Fraction());
    ###
    # Generic getter methods
    ###
    def GetIsSingleIsotope(self):
        return len(self) == 1;
    ###
    def GetZa(self, index = 0):
        return self.GetZas()[index];
    ###
    def GetZas(self):
        return self.zas;
    ###
    def GetZaids(self):
        return self.GetZaid2Fraction().keys();
    ###
    def GetZaid2Fraction(self):
        return self.zaid2Fraction;
    ###
    # Population methods
    ###
    def Populate(self):
        card = [word for word in self.GetRaw().split()];
        materialNumber = card[0].lower().strip('m');
        self.number = int(float(materialNumber));
        self.zaid2Fraction = {card[index] : float(card[index + 1]) for index in range(1, len(card) - 1, 2)};
        self.zas = sorted({Zaid2Za(zaid) for zaid in self.GetZaid2Fraction().keys()});
        ###
        return;
###
# MCNP tally
###
class McnpTally(McnpCard):
    def __contains__(self, other):
        if isinstance(other, str):
            return any(particle in other for particle in self.GetParticles());
        ###
        elif isinstance(other, float):
            return hasattr(self, 'tallyTags') and other in self.tallyTags;
        ###
        elif isinstance(other, int):
            return other in self.GetSpaces();
        ###
        return other.GetNumber() in self.GetSpaces();
    ###
    def __len__(self):
        return len(self.GetSpaces());
    ###
    # Generic getter methods
    ###
    def GetEnergys(self):
        return self.energys;
    ###
    def GetParticles(self):
        return self.particles;
    ###
    def GetResultString(self):
        return self.resultString;
    ###
    def GetMnemonic(self):
        return self.mnemonic;
    ###
    def GetSpaces(self):
        return self.spaces;
    ###
    def GetSpaceType(self):
        if self.GetMnemonic() in ('f1', 'f2'):
            return 'surface';
        else:
            return 'cell';
    ###
    # Physical quantity getter methods
    ###
    def GetTallyResults(self, *args):
        ###
        # Tally-type-specific indicies (space, angle, multiplier bin)
        ###
        if self.GetMnemonic() in ('f1', ):
            jndex = (0, 1);
        elif self.GetMnemonic() in ('f2', 'f4', 'f5', 'f6', 'f7', 'f8'):
            jndex = (0, );
        elif self.GetMnemonic() in ('fm4', ):
            jndex = (0, 2);
        ###
        # Indices are none-valued unless specified
        ###
        index = [None] * 3;
        for kndex in range(len(args)):
            index[jndex[kndex]] = args[kndex];
        index = tuple(index);
        ###
        return self.results[index];
    ###
    # Population methods
    ###
    def Populate(self):
        self.PopulateGenerics();
        ###
        return;
    ###
    def PopulateAngles(self, angles):
        self.angles = angles;
        ###
        return;
    ###
    def PopulateGenerics(self):
        multiplier, tallyNumber, particleOne, particleTwo = ReCompile(r'f(m?)(\d{1,8})\s*:?\s*([np]?)\s*,?\s*([np]?)', 2 | 8).search(self.GetRaw()).groups();
        self.number = int(float(tallyNumber));
        self.mnemonic = 'f{}{}'.format(['', multiplier][multiplier != None], self.GetNumber() % 10);
        self.particles = ''.join((particleOne, particleTwo));
        return;
    ###
    def PopulateEnergys(self, energys):
        self.energys = energys;
        ###
        return;
    ###
    def PopulateResults(self, resultString):
        self.resultString = resultString;
        ###
        reSpaces = ReCompile(r' {2,}', 2 | 8);
        reSpace = ReCompile(r'^ {}  ?(\d+)[(\d)<]* +$'.format(self.GetSpaceType()), 2 | 8);
        reAngle = ReCompile(r'^ [ca][on][sg][il][ne][e ] bin:  ([ \-]\d\.[ \d]{5}E[+\-]\d{2}) to ([ \-]\d\.[ \d]{5}E[+\-]\d{2}) [m ][u ] +$', 2 | 8);
        reMultiplierBin = ReCompile(r'^ multiplier bin:  [ \-]\d\.\d{5}E[+\-]\d{2} +(\d+)? +([ :\d\-]+)? +$', 2 | 8);
        reNumerics = ReCompile(r'^ {4}(\d\.\d{4}E[+\-]\d{2}| {2}total {3}| {10}) {3}(\d\.\d{5}E[+\-]\d{2}) (\d\.\d{4}$)', 2 | 8);
        ###
        # Energys
        ###
        try:
            energys = self.GetEnergys();
        except AttributeError:
            energys = [];
        ###
        # Build empty results array
        ###
        self.results = {};
        ###
        for block in iter(ReCompile('^ $', 2 | 8).split(self.GetResultString())[1 : ]):
            ###
            # Space
            ###
            space = reSpace.search(block);
            space = space and int(space.group(1));
            ###
            # Angle
            ###
            angle = reAngle.search(block);
            angle = angle and (float(angle) for angle in (angle.group(1, 2)));
            ###
            # Multiplier bin
            ###
            multiplierBin = reMultiplierBin.search(block);
            ###
            if multiplierBin is not None:
                groups = multiplierBin.groups();
                if all(group is not None for group in groups):
                    try:
                        multiplierBin = (int(float(groups[0])), int(float(groups[1])));
                    except ValueError:
                        multiplierBin = (int(float(groups[0])), reSpaces.sub(' ', groups[1].strip()).replace(' : ', ':'));
                else:
                    multiplierBin = None;
            ###
            if self.mnemonic not in ('fm4', 'fm5') and multiplierBin is not None and len(multiplierBin) > 1:
                continue;
            ###
            self.results[(space, angle, multiplierBin)] = TallyResult(reNumerics.finditer(block), len(energys));
        ###
        return;
    ###
    def PopulateSpaces(self):
        spaces = ' '.join(self.GetRaw().split()[1 : ]);
        ###
        if any(character in self.GetRaw() for character in '()'):
            startStop = [];
            level = 0;
            for index in range(len(spaces)):
                if '(' == spaces[index]:
                    level += 1;
                    if 1 == level:
                        start = index;
                elif ')' == spaces[index]:
                    level -= 1;
                    if 0 == level:
                        stop = index;
                        startStop.append((start, stop));
            ###
            spaces = [spaces[start + 1 : stop] for start, stop in startStop];
        else:
            spaces = [word for word in spaces.split()];
        ###
        self.spaces = [int(float(word)) for word in self.GetRaw().split()[1 : ] if all(character not in word for character in '()')];
        ###
        return;
###
# MCNP F1 surface current tally
###
class McnpSurfaceCurrentTally(McnpTally):
    pass;
###
# MCNP F2 surface flux tally
###
class McnpSurfaceFluxTally(McnpTally):
    pass;
###
# MCNP F4 cell flux tally
###
class McnpCellFluxTally(McnpTally):
    pass;
###
# MCNP FM4 cell flux multiplier tally
###
class McnpCellFluxMultiplierTally(McnpTally):
    ###
    # Generic getter methods
    ###
    def GetMultiplierBins(self):
        return self.multiplierBins;
    ###
    # Population methods
    ###
    def CrackBin(self, tallyBin):
        tallyBin = iter(tallyBin.split());
        ###
        multiplier = next(tallyBin);
        multiplier = float(multiplier);
        ###
        try:
            materialNumber = int(float(next(tallyBin)));
            reactionNumbers = [];
            for reactionNumber in (reactionNumber.strip('()') for reactionNumber in ReCompile('\) +\(').split(' '.join(tallyBin))):
                try:
                    reactionNumbers.append(int(float(reactionNumber)));
                except ValueError:
                    reactionNumbers.append(reactionNumber);
        except StopIteration:
            materialNumber = None;
            reactionNumbers = [None];
        ###
        return ((multiplier, materialNumber, reactionNumber) for reactionNumber in reactionNumbers);
    ###
    def PopulateSpaces(self, tallys):
        for tally in tallys:
            if tally.GetMnemonic() in ('f4', 'f5') and tally.GetNumber() == self.GetNumber():
                self.particles = tally.GetParticles();
                self.spaces = tally.GetSpaces();
                break;
        return;
    ###
    def PopulateMultiplierBins(self, cells):
        ###
        # Multiplier bins and particles
        ###
        particleOne, particleTwo, multiplierBins, junk = (group.strip() for group in ReCompile(r'fm\d{0,7}4:?\s*([np]?)\s*,?\s*([np]?)\s+((.|\n)+)', 2 | 8).search(self.GetRaw()).groups());
        ###
        # Overwrite inherited particles from F4 tally
        ###
        self.particles = ''.join((particleOne, particleTwo)) or self.particles;
        ###
        # Segregate multiplier bins
        ###
        if ('(', ')') != (multiplierBins[0], multiplierBins[-1]):
            multiplierBins = [multiplierBins];
        else:
            startStop = [];
            level = 0;
            for index in range(len(multiplierBins)):
                if '(' == multiplierBins[index]:
                    level += 1;
                    if 1 == level:
                        start = index;
                elif ')' == multiplierBins[index]:
                    level -= 1;
                    if 0 == level:
                        stop = index;
                        startStop.append((start, stop));
            ###
            multiplierBins = [multiplierBins[start + 1 : stop] for start, stop in startStop];
        ###
        # Crack open bin string
        ###
        multiplierBins = [crackedBins for tallyBin in multiplierBins for crackedBins in self.CrackBin(tallyBin)];
        ###
        # Check and normalize multiplier
        # attach multiplier bins
        ###
        cellNumber2MaterialNumber = {cell.GetNumber() : cell.GetMaterialNumber() for cell in cells};
        self.multiplierBins = [];
        for cellNumber in self.GetSpaces():
            for multiplier, materialNumber, reactionNumber in multiplierBins:
                if materialNumber == cellNumber2MaterialNumber[cellNumber] and not(multiplier > 1):
                    ###
                    # Real material tally
                    ###
                    multiplier = -1. * bool(multiplier);
                elif materialNumber not in cellNumber2MaterialNumber.values():
                    ###
                    # Single-isotope tally
                    ###
                    multiplier = +1. * bool(multiplier);
                elif materialNumber is None and reactionNumber is None:
                    ###
                    # Only the flux is extracted
                    ###
                    pass;
                else:
                    ###
                    # Cell flux multiplier tally may have a multiplier of improper sign
                    ###
                    pass;
                ###
                self.multiplierBins.append((cellNumber, multiplier, materialNumber, reactionNumber));
        ###
        return;
###
# MCNP F5 detector tally
###
class McnpDetectorTally(McnpTally):
    pass;
###
# MCNP FM5 detector multiplier tally
###
class McnpDetectorMultiplierTally(McnpCellFluxMultiplierTally):
    pass;
###
# MCNP F6 cell energy deposition tally
###
class McnpCellEnergyDepositionTally(McnpTally):
    pass;
###
# MCNP F7 cell fission energy deposition tally
###
class McnpCellFissionEnergyDepositionTally(McnpTally):
    pass;
###
# MCNP F8 cell pulse height tally
###
class McnpCellPulseHeightTally(McnpTally):
    pass;
###
# MCNP input file parser
###
class McnpInputFile:
    def __init__(self, fileName, outputRaw = None):
        self.outputRaw = outputRaw;
        ###
        # Read input raw or extract it from the output raw
        ###
        if self.GetOutputRaw():
            self.fileName = ReCompile(r'\.o$', 2 | 8).sub('', fileName);
            ###
            reInputRaw = ReCompile(r'(?<=\d- {7})[\S ]+', 2 | 8);
            inputRaw = '\n'.join(line.group() for block in ReCompile(r'^1', 8).split(self.GetOutputRaw()) if 'mcnp' == block[ : 4] for line in reInputRaw.finditer(block));
        else:
            self.fileName = fileName;
            ###
            inputRaw = ReadFile(self.GetFileName(), display = not bool(arguments.isQuiet));
        ###
        # Strip whitespace from the ends of lines
        ###
        self.inputRaw = '\n'.join(line.rstrip() for line in inputRaw.split('\n')).rstrip();
        ###
        self.Populate();
        ###
        return;
    ###
    # Mathematical operator overloaders
    ###
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            ###
            # Sum isotopic moles over cells
            ###
            za2MolesOne = self.GetZa2Moles();
            za2MolesTwo = other.GetZa2Moles();
            ###
            # Zero-value missing za's
            ###
            za2MolesOne.update({za : 0 for za in set(za2MolesTwo) - set(za2MolesOne)});
            za2MolesTwo.update({za : 0 for za in set(za2MolesOne) - set(za2MolesTwo)});
            ###
            # Calculate fractional difference
            ###
            totalMoles = 0.5 * (sum(za2MolesOne.values()) + sum(za2MolesTwo.values()));
            ###
            relativeDifferences = Array([abs(za2MolesOne[za] - za2MolesTwo[za]) / totalMoles for za in za2MolesOne]);
            ###
            # Calculate convergence norm
            ###
            normType = mocDownInputFile.GetParameter('isotopicsConvergenceNormType');
            if normType in ('1', 'one'):
                norm = relativeDifferences.mean();
            elif normType in ('2', 'two'):
                norm = (relativeDifferences ** 2.).mean() ** 0.5;
            elif normType in ('inf', 'infinite', 'infinity'):
                norm = relativeDifferences.max();
            ###
            return norm;
    ###
    def __rsub__(self, other):
        return -self.__sub__(other);
    ###
    # Generic getter methods
    ###
    def GetAngles(self):
        return self.angles;
    ###
    def GetCellBlock(self):
        return self.cellBlock;
    ###
    def GetCellNumberDecayPower(self, cellNumber, za2WattsPerMole):
        cell = self.FindCell(cellNumber);
        ###
        return sum(moles * za2WattsPerMole[za] for za, moles in cell.GetZa2Moles().items() if za in za2WattsPerMole);
    ###
    def GetCellNumberPaths(self, cellNumber):
        return self.GetCellNumber2Paths()[cellNumber];
    ###
    def GetCellNumber2Paths(self):
        return self.cellNumber2Paths;
    ###
    def GetCells(self):
        return self.cells;
    ###
    def GetCellNumbers(self):
        return self.cellNumbers;
    ###
    def GetDataBlock(self):
        return self.dataBlock;
    ###
    def GetEnergys(self):
        return self.energys;
    ###
    def GetFileName(self):
        return self.fileName;
    ###
    def GetFissionCells(self):
        fissionCells = [];
        for cellNumber in self.GetPowerCells():
            material = self.FindCellMaterial(cellNumber);
            ###
            if any(ZaIsActinide(za) and za not in (89225, 89226, 99253) for za in material.GetZas()):
                fissionCells.append(cellNumber);
        ###
        return fissionCells;
    ###
    def GetHeavyMetalMT(self):
        return sum(cell.GetHeavyMetalMT() for cell in self.GetCells() if cell.GetMaterialNumber());
    ###
    def GetInputRaw(self):
        return self.inputRaw;
    ###
    def GetIsKcode(self):
        return self.GetNamedCard('kcode') is not None;
    ###
    def GetInputRawWithoutComments(self):
        return self.inputRawWithoutComments;
    ###
    def GetIsCoupled(self):
        return 'p' in self.GetMode();
    ###
    def GetIsMultiplyRootedLeafCell(self, leafCell):
        return leafCell in self.GetMultiplyRootedLeafCells();
    ###
    def GetMultiplyRootedLeafCell(self, leafCell):
        return self.GetMultiplyRootedLeafCells()[leafCell];
    ###
    def GetMultiplyRootedLeafCells(self):
        return self.multiplyRootedLeafCells;
    ###
    def GetMaterials(self):
        return self.materials;
    ###
    def GetMaterialNumbers(self):
        return self.materialNumbers;
    ###
    def GetMode(self):
        return ''.join(str(self.GetNamedCard('mode')).split()[1 : ]).lower();
    ###
    def GetNamedCard(self, cardName):
        namedCards = self.GetNamedCards();
        if cardName in namedCards:
            return namedCards[cardName];
    ###
    def GetNamedCards(self):
        return self.namedCards;
    ###
    def GetOutputRaw(self):
        return self.outputRaw;
    ###
    def GetPowerCells(self):
        powerCells = [];
        for cell in self.GetCells():
            ###
            # Kick out immaterial cells
            # Only cells with materials can contribute directly to heating
            ###
            if not cell.GetMaterialNumber():
                continue;
            ###
            # Kick out low-density cells
            # Low-density cells are assumed to not contribute sufficiently to heating
            ###
            if cell.GetMaterialDensity() is not None and cell.GetMassDensity() < mocDownInputFile.GetParameter('minimumCellMassDensityCutoff'):
                continue;
            ###
            powerCells.append(cell.GetNumber());
        ###
        return powerCells;
    ###
    def GetSurfaces(self):
        return self.surfaces;
    ###
    def GetSurfaceBlock(self):
        return self.surfaceBlock;
    ###
    def GetTallyIndices(self, mnemonic):
        return self.GetTallyType2Indices()[mnemonic.lower()];
    ###
    def GetTallyType2Indices(self):
        return self.tallyType2Indices;
    ###
    def GetTallys(self, mnemonic = None):
        if mnemonic is not None:
            return (tally for tally in self.GetTallys() if tally.GetMnemonic() == mnemonic);
        return self.tallys;
    ###
    def GetZa2Moles(self):
        za2Moles = {};
        for cell in self.GetCells():
            if cell.GetMaterialNumber():
                for za, moles in cell.GetZa2Moles().items():
                    try:
                        za2Moles[za] += moles;
                    except KeyError:
                        za2Moles[za] = moles;
        return za2Moles;
    ###
    # Constructed getter methods
    ###
    def FindCell(self, cellNumber):
        return self.GetCells()[self.GetCellNumbers().index(cellNumber)];
    ###
    def FindCellMaterial(self, cellNumber):
        cell = self.FindCell(cellNumber);
        if not cell:
            return;
        ###
        materialNumber = cell.GetMaterialNumber();
        return self.FindMaterial(materialNumber);
    ###
    def FindCellSurfaces(self, cellNumber):
        cell = self.FindCell(cellNumber);
        if not cell:
            return;
        ###
        surfaceNumbers = (abs(surfaceNumber) for surfaceNumber in cell.GetSurfaceNumbers());
        return (surface for surface in self.GetSurfaces() if surface.GetNumber() in surfaceNumbers);
    ###
    def FindLeafCells(self, cells):
        try:
            leafCells = [];
            ###
            # Accumulate leafcell tree
            ###
            for cell in cells:
                if cell.GetFillUniverse():
                    ###
                    # Grab child nodes
                    ###
                    leafCells.extend(self.FindLeafCells(childCell for childCell in self.GetCells() if childCell.GetUniverse() == cell.GetFillUniverse()));
                else:
                    ###
                    # Grab current node
                    ###
                    leafCells.append(cell);
            return set(leafCells);
        except TypeError:
            if isinstance(cells, int):
                return self.FindLeafCells(self.FindCell(cells));
            return self.FindLeafCells([cells]);
    ###
    def FindMaterial(self, materialNumber):
        if 0 != materialNumber:
            return self.GetMaterials()[self.GetMaterialNumbers().index(materialNumber)];
    ###
    def FindRootCells(self, cells):
        try:
            rootCells = [];
            ###
            # Accumulate rootcell tree
            ###
            for cell in cells:
                if cell.GetUniverse():
                    ###
                    # Grab parent nodes
                    ###
                    rootCells.extend(self.FindRootCells(parentCell for parentCell in self.GetCells() if parentCell.GetFillUniverse() == cell.GetUniverse()));
                else:
                    ###
                    # Grab current nodes
                    ###
                    rootCells.append(cell);
            return set(rootCells);
        except TypeError:
            if isinstance(cells, int):
                return self.FindRootCells(self.FindCell(cells));
            return self.FindRootCells([cells]);
    ###
    def FindSingleZaidMaterialNumber(self, zaid):
        for material in self.GetMaterials():
            if material.GetIsSingleIsotope():
                if zaid in material.GetZaids():
                    return material.GetNumber();
    ###
    # Input card stripping methods
    ###
    def Block2SingleLineCards(self, raw):
        reIndent = ReCompile(r'^( {5,}|\t)', 2 | 8);
        reAmpersand = ReCompile(r'&\s{1,}$', 2 | 8);
        ###
        cards = [];
        continuation = False;
        for line in raw.strip().split('\n'):
            line = line.rstrip();
            ###
            continuation |= bool(reIndent.search(line));
            if continuation:
                cards[-1] += '\n' + line;
            else:
                cards.append(line);
            ###
            continuation = bool(reAmpersand.search(line));
        ###
        return cards;
    ###
    def GetCellCards(self):
        return self.Block2SingleLineCards(self.GetCellBlock());
    ###
    def GetDataCards(self):
        return self.Block2SingleLineCards(self.GetDataBlock());
    ###
    def GetSurfaceCards(self):
        return self.Block2SingleLineCards(self.GetSurfaceBlock());
    ###
    # Population methods
    ###
    def Populate(self):
        ###
        # Populate input blocks
        ###
        self.PopulateInputBlocks();
        ###
        # Populate cells
        ###
        self.cells = [McnpCell(cellCard) for cellCard in self.GetCellCards()[1 : ]];
        self.cellNumbers = [cell.GetNumber() for cell in self.GetCells()];
        ###
        # Populate cell heirarchy
        ###
        self.PopulateCellHeirarchy();
        ###
        # Populate surfaces
        ###
        self.surfaces = [McnpSurface(surfaceCard) for surfaceCard in self.GetSurfaceCards()];
        ###
        # Populate data cards
        ###
        self.PopulateDataCards();
        ###
        # Populate cell material attributes
        ###
        self.PopulateCellMaterialAttributes();
        ###
        # Populate tally energys, angles, and spaces and cell flux multiplier tally bins
        ###
        self.PopulateTallySpecifics();
        ###
        # Populate cell -> tally indices
        ###
        self.PopulateTallyIndices();
        ###
        return;
    ###
    def PopulateInputBlocks(self):
        ###
        # cell block, surface block, data block
        ###
        self.inputRawWithoutComments = '\n'.join(line.split('$')[0].rstrip() for line in self.GetInputRaw().split('\n') if line[ : 2].lower() not in ('c', 'c ')).rstrip();
        self.cellBlock, self.surfaceBlock, self.dataBlock = ReCompile(r'\n[ \t]*\n', 8).split(self.GetInputRawWithoutComments());
        ###
        return;
    ###
    def PopulateCellHeirarchy(self):
        ###
        # Build childCell -> parentCells
        ###
        cell2ParentCells = {childCell : [parentCell for parentCell in self.GetCells() if childCell.GetUniverse() if parentCell.GetFillUniverse() == childCell.GetUniverse()] for childCell in self.GetCells()};
        ###
        # Populated leafCell -> ... -> rootCell paths
        # Depth-first searches are performed, ascending from each leafCell
        ###
        paths = [];
        path = [];
        branches = [sorted([leafCell for leafCell in self.GetCells() if not leafCell.GetFillUniverse()], reverse = True)];
        ###
        while branches:
            ###
            # New path based upon branch listing
            ###
            if not branches[-1]:
                ###
                # The current level has no branches
                ###
                if 1 == len(branches):
                    ###
                    # No more branch levels exist
                    # Break
                    ###
                    break;
                ###
                # Descend a level
                ###
                path.pop();
                branches.pop();
                ###
                continue;
            else:
                ###
                # Move next branch to path
                ###
                path.append(branches[-1].pop());
            ###
            parents = sorted(cell2ParentCells[path[-1]], reverse = True);
            while parents:
                ###
                # Acsend to root cell, while keeping track of branching cells
                ###
                path.append(parents.pop());
                branches.append(parents);
                parents = sorted(cell2ParentCells[path[-1]], reverse = True);
            else:
                ###
                # Ascent is finished
                # Note if it connects a leafCell to a rootCell
                ###
                if not path[-1].GetUniverse():
                    paths.append(list(path));
                path.pop();
        ###
        # Convert cell paths -> cell number paths
        ###
        paths = [[cell.GetNumber() for cell in path] for path in paths];
        ###
        # Match redundant paths
        ###
        matchSets = [];
        for index in range(len(paths)):
            for jndex in range(len(paths)):
                match = True;
                ###
                # Kick out paths of unequal length
                ###
                if len(paths[index]) != len(paths[jndex]):
                    match = False;
                    continue;
                ###
                previous = True;
                for kndex in range(len(paths[index])):
                    current = paths[index][kndex] == paths[jndex][kndex];
                    ###
                    # Kick out paths with non-matching leaf or root nodes
                    ###
                    if kndex in (0, len(paths[index]) - 1) and not current:
                        match = False;
                        break;
                    ###
                    # Kick out paths with two consecutive non-matching nodes
                    ###
                    if not (previous or current):
                        match = False;
                        break;
                    ###
                    previous = current;
                ###
                if match:
                    ###
                    # The two paths match
                    # Add them to the set of matching paths or ...
                    ###
                    matchNoted = False;
                    for matchSet in matchSets:
                        if any(kndex in matchSet for kndex in (index, jndex)):
                            matchNoted = True;
                            matchSet.update((index, jndex));
                    ###
                    # ... create a new set of matching paths
                    ###
                    if not matchNoted:
                        matchSets.append({index, jndex});
        ###
        # Merge redundant paths
        ###
        self.cellNumber2Paths = {};
        for matchSet in matchSets:
            mergedPath = [];
            cellNumber = None;
            for index in matchSet:
                if cellNumber is None:
                    cellNumber = paths[index][0];
                for jndex in range(len(paths[index])):
                    try:
                        mergedPath[jndex].update((paths[index][jndex], ));
                    except IndexError:
                        mergedPath.append(set((paths[index][jndex], )));
            mergedPath = [sorted(element) for element in mergedPath];
            ###
            if len(mergedPath) > 1:
                mergedPath[-1][-1] *= -1;
            ###
            cellNumber = mergedPath[0][0];
            try:
                self.cellNumber2Paths[cellNumber].append(mergedPath);
            except KeyError:
                self.cellNumber2Paths[cellNumber] = [mergedPath];
        ###
        # Populate multiply-rooted leaf cells
        ###
        self.multiplyRootedLeafCells = {cellNumber : [path[-1][0] for path in paths] for cellNumber, paths in self.GetCellNumber2Paths().items() if len(paths) > 1};
        ###
        return;
    ###
    def PopulateDataCards(self):
        ###
        # Populate defaults
        ###
        self.namedCards = {
            ###
            # title
            ###
            'title' : McnpCard(self.GetInputRaw().split('\n')[0]),
            ###
            # Uncoupled neutron transport
            ###
            'mode'  : McnpCard('mode n'),
        };
        ###
        # Initialize multi-card containers
        ###
        self.angles = {};
        self.namedCards['angles'] = [];
        self.energys = {};
        self.namedCards['energys'] = [];
        self.materials = [];
        self.materialNumbers = [];
        self.tallys = [];
        self.namedCards['tallyComments'] = [];
        self.namedCards['thermalScatters'] = [];
        ###
        # Define regex's for mnemonic and tally number
        ###
        reMnemonic = ReCompile(r'^[\*]?([a-z]{1,5})', 2 | 8);
        reTallyNumber = ReCompile(r'(\d{1,8})', 2 | 8);
        ###
        # Parse data cards
        ###
        for dataCard in self.GetDataCards():
            mnemonic = [word for word in dataCard.split()][0];
            mnemonicLetters = reMnemonic.search(mnemonic).group(1).lower();
            ###
            # Problem type cards
            ###
            if mnemonicLetters in ('mode'):
                ###
                # mode
                ###
                if 'mode' == mnemonicLetters:
                    self.namedCards['mode'] = McnpCard(dataCard);
                    continue;
            ###
            # Geometry cards
            ###
            if mnemonicLetters in ('vol', 'area', 'u', 'trcl', 'lat', 'fill', 'tr', 'uran'):
                ###
                # volumes
                ###
                if 'vol' == mnemonicLetters:
                    volumes = [];
                    for volume in dataCard.split()[1 : ]:
                        if 'j' in volume:
                            number = int(float(volume.lower().replace('j', '')));
                            volumes.extend([0., ] * number);
                        else:
                            volumes.append(float(volume));
                    ###
                    index = 0;
                    for cell in self.GetCells():
                        cell.volume = volumes[index];
                        index += 1;
                    continue;
            ###
            # Source specification cards
            ###
            if mnemonicLetters in ('sdef', 'si', 'sp', 'sb', 'ds', 'sc', 'ssw', 'ssr', 'kcode', 'ksrc', 'hsrc'):
                ###
                # sdef
                ###
                if 'sdef' == mnemonicLetters:
                    self.namedCards['sdef'] = McnpCard(dataCard);
                    continue;
                ###
                # kcode
                ###
                if 'kcode' == mnemonicLetters:
                    self.namedCards['kcode'] = McnpCard(dataCard);
                    continue;
                ###
                # ksrc
                ###
                if 'ksrc' == mnemonicLetters:
                    self.namedCards['ksrc'] = McnpCard(dataCard);
                    continue;
            ###
            # Tally specification cards
            ###
            if mnemonicLetters in ('f', 'fc', 'e', 't', 'c', 'fq', 'fm', 'de', 'df', 'em', 'tm', 'cm', 'cf', 'sf', 'fs', 'sd', 'fu', 'tf', 'dd', 'dxt', 'ft', 'fmesh', 'spdtl'):
                ###
                # tally
                ###
                if mnemonicLetters in ('f', 'fm'):
                    tallyNumber = reTallyNumber.search(mnemonic).group(1);
                    tallyType = int(float(tallyNumber)) % 10;
                    ###
                    if 1 == tallyType:
                        self.tallys.append(McnpSurfaceCurrentTally(dataCard));
                        continue;
                    if 2 == tallyType:
                        self.tallys.append(McnpSurfaceFluxTally(dataCard));
                        continue;
                    if 4 == tallyType:
                        if 'f' == mnemonicLetters:
                            self.tallys.append(McnpCellFluxTally(dataCard));
                        elif 'fm' == mnemonicLetters:
                            self.tallys.append(McnpCellFluxMultiplierTally(dataCard));
                        continue;
                    if 5 == tallyType:
                        if 'f' == mnemonicLetters:
                            self.tallys.append(McnpDetectorTally(dataCard));
                        elif 'fm' == mnemonicLetters:
                            self.tallys.append(McnpDetectorMultiplierTally(dataCard));
                        continue;
                    if 6 == tallyType:
                        self.tallys.append(McnpCellEnergyDepositionTally(dataCard));
                        continue;
                    if 7 == tallyType:
                        self.tallys.append(McnpCellFissionEnergyDepositionTally(dataCard));
                        continue;
                    if 8 == tallyType:
                        self.tallys.append(McnpCellPulseHeightTally(dataCard));
                        continue;
                ###
                # tally comment
                ###
                if 'fc' == mnemonicLetters:
                    self.namedCards['tallyComments'].append(McnpCard(dataCard));
                    continue;
                ###
                # energys
                ###
                if 'e' == mnemonicLetters:
                    energyNumber = int(float(mnemonic.lower().replace('e', '').replace(':', '')));
                    stringEnergys = dataCard.split()[1 : ];
                    energys = [];
                    for index in range(len(stringEnergys)):
                        if 'log' in stringEnergys[index]:
                            energys.extend(LogSpace(NaturalLogarithm(float(stringEnergys[index - 1])) / NaturalLogarithm(10.), NaturalLogarithm(float(stringEnergys[index + 1])) / NaturalLogarithm(10.), float(stringEnergys[index].lower().replace('ilog', '')) + 2)[1 : -1]);
                        else:
                            energys.append(float(stringEnergys[index]));
                    self.energys[energyNumber] = Array(energys);
                    ###
                    self.namedCards['energys'].append(McnpCard(dataCard));
                    continue;
                ###
                # angles
                ###
                if 'c' == mnemonicLetters:
                    angleNumber = int(float(mnemonic.lower().replace('c', '')));
                    self.angles[angleNumber] = Array([float(angle) for angle in dataCard.split()[1 : ]]);
                    ###
                    self.namedCards['angles'].append(McnpCard(dataCard));
                    continue;
            ###
            # Material specification cards
            ###
            if mnemonicLetters in ('m', 'mpn', 'drxs', 'totnu', 'nonu', 'awtab', 'xs', 'void', 'pikmt', 'mgopt'):
                ###
                # materials
                ###
                if 'm' == mnemonicLetters:
                    self.materials.append(McnpMaterial(dataCard));
                    self.materialNumbers.append(self.materials[-1].GetNumber());
                    continue;
            ###
            # Energy and thermal treatment specification cards
            ###
            if mnemonicLetters in ('phys', 'tmp', 'thyme', 'mt'):
                ###
                # thermal scatter library
                ###
                if 'mt' == mnemonicLetters:
                    self.namedCards['thermalScatters'].append(McnpCard(dataCard));
                    continue;
            ###
            # Problem cutoff cards
            ###
            if mnemonicLetters in ('cut', 'elpt', 'notrn', 'nps', 'ctme'):
                ###
                # nps
                ###
                if 'nps' == mnemonicLetters:
                    self.namedCards['nps'] = McnpCard(dataCard);
                    continue;
            ###
            # User data arrays
            ###
            if mnemonicLetters in ('idum', 'rdum'):
                continue;
            ###
            # Peripheral cards
            ###
            if mnemonicLetters in ('prdmp', 'lost', 'rand', 'dbcn', 'files', 'print', 'talnp', 'mplot', 'ptrac', 'pert'):
                ###
                # print tables
                ###
                if 'print' == mnemonicLetters:
                    self.namedCards['print'] = McnpCard(dataCard);
                    continue;
        return;
    ###
    def PopulateCellMaterialAttributes(self):
        ###
        # Calculate cell number densities, regardless of material density / fraction provided
        ###
        for cell in self.GetCells():
            material = self.FindCellMaterial(cell.GetNumber());
            ###
            # Kick out immaterial cells
            ###
            if material is None:
                continue;
            ###
            composition = MaterialComposition(materialDensity = cell.GetMaterialDensity(), isotope2Fraction = material.GetZaid2Fraction());
            ###
            for attribute in ('numberDensity', 'massDensity', 'cellMolarMass', 'isotope2AtomFraction', 'isotope2WeightFraction', 'isotope2NumberDensity', 'isotope2MassDensity', 'suffix', 'zas'):
                myAttribute = attribute.replace('isotope', 'zaid');
                setattr(cell, myAttribute, getattr(composition, attribute));
        ###
        return;
    ###
    def PopulateTallySpecifics(self):
        for tally in self.GetTallys():
            ###
            # Attach energy bins
            ###
            for tallyNumber, energyBins in self.GetEnergys().items():
                if 0 == tallyNumber or tallyNumber == tally.GetNumber():
                    tally.PopulateEnergys(energyBins);
            ###
            # Attach angle bins
            ###
            if tally.GetMnemonic() == 'f1':
                for tallyNumber, angleBins in self.GetAngles().items():
                    if 0 == tallyNumber or tallyNumber == tally.GetNumber():
                        tally.PopulateAngles(angleBins);
            ###
            # Attach multiplier bins
            ###
            if tally.GetMnemonic() in ('fm4', 'fm5'):
                ###
                # FM4 tallys inherit the particles and spaces of their sibling F4 tally
                ###
                tally.PopulateSpaces(self.GetTallys());
                ###
                # Having the necessary information
                ###
                tally.PopulateMultiplierBins(self.GetCells());
            else:
                tally.PopulateSpaces();
        ###
        return;
    ###
    def PopulateTallyIndices(self):
        tallyType2Indices = {mnemonic : [] for mnemonic in ('f1', 'f2', 'f4', 'f5', 'f6', 'f7', 'f8')};
        tallyType2Indices['fm4'] = {};
        ###
        for cell in self.GetCells():
            ###
            # Kick out non-root and non-leaf (but not necessarily immaterial) cells
            # Leaf cells contain physical materials and can contribute to reaction rates
            # Root cells (redundantly) contain leaf cells but conveniently capture contributions from all their leaves
            ###
            if cell.GetUniverse() and cell.GetFillUniverse():
                continue;
            ###
            # Straight cell tallys (F4, F6, F7)
            ###
            for mnemonic in ('f4', 'f6', 'f7'):
                ###
                # Consider cell and its leaves
                ###
                for leafCell in self.FindLeafCells(cell):
                    for tally in self.GetTallys(mnemonic):
                        if leafCell in tally:
                            tallyType2Indices[mnemonic].append(cell.GetNumber());
            ###
            # Straight surface tallys (F1, F2)
            ###
            for mnemonic in ('f1', 'f2'):
                ###
                # Kick out cells without cell flux tallys
                ###
                if cell.GetNumber() not in tallyType2Indices['f4']:
                    continue;
                ###
                # Do not consider cell leaves
                ###
                for surface in self.FindCellSurfaces(cell.GetNumber()):
                    for tally in self.GetTallys(mnemonic):
                        if surface in tally:
                            tallyType2Indices[mnemonic].append(cell.GetNumber());
            ###
            # Cell multiplier tallys (FM4)
            ###
            mnemonic = 'fm4';
            ###
            # Consider cell and its leaves
            ###
            for leafCell in self.FindLeafCells(cell):
                leafCellNumber = leafCell.GetNumber();
                for tally in self.GetTallys(mnemonic):
                    if leafCell in tally:
                        indices = [tuple([bin, 0][bin is None] for bin in tallyBin[2 : ]) for tallyBin in tally.GetMultiplierBins() if leafCellNumber == tallyBin[0]];
                        try:
                            tallyType2Indices[mnemonic][cell.GetNumber()].extend(indices);
                        except KeyError:
                            tallyType2Indices[mnemonic][cell.GetNumber()] = indices;
        ###
        # Unique sort indices
        ###
        for mnemonic in ('f1', 'f2', 'f4', 'fm4', 'f5', 'f6', 'f7', 'f8'):
            if 'fm4' == mnemonic:
                tallyType2Indices[mnemonic] = {key : sorted(set(value)) for key, value in tallyType2Indices[mnemonic].items()};
                tallyType2Indices[mnemonic] = {key : tuple([value, None][value == 0] for value in values) for key, values in tallyType2Indices[mnemonic].items()};
            else:
                tallyType2Indices[mnemonic] = sorted(set(tallyType2Indices[mnemonic]));
        ###
        self.tallyType2Indices = tallyType2Indices;
        return;
    ###
    # Report methods
    ###
    def Report(self, arguments):
        ###
        if arguments.reportCells:
            ###
            # Extract material cells
            ###
            cells = sorted(cell for cell in self.GetCells() if cell.GetMaterialDensity());
            ###
            # cell # -> material number, number density, mass density, volume, atoms, mass, temperature
            ###
            PrintNow(
                '> Cell material numbers, number densities, mass densities, volumes, atoms, masses, and temperatures',
                '{:^8}{:^12}{:^14}{:^11}{:^14}{:^14}{:^14}{:^17}'.format('Cell #', 'Material #', 'N [a/b·cm]', 'ρ [g/cm³]', 'Volume [cm³]', 'Atoms [mol]', 'Mass [g]', 'Temperature [K]'),
                *('{0.number:^8}{0.materialNumber:^12}{0.numberDensity:^14.6G}{0.massDensity:^11.4G}{0.volume:^14.6E}{1:^14.6E}{2:^14.6E}{3:^17.0G}'.format(cell, cell.GetMoles(), cell.GetMass(), cell.GetTemperature() * kelvinPerMev) for cell in cells),
                sep = '\n'
                );
            ###
            # cell # -> isotope, temperature id, temperature, number density, mass density, atoms, mass
            ###
            PrintNow(
                '> Cell isotopes, temperature ids, number densities, mass densities, atoms, and masses',
                '{:^8}{:^9}{:^17}{:^14}{:^11}{:^14}{:^14}'.format('Cell #', 'Isotope', 'Temperature [K]', 'N [a/b·cm]', 'ρ [g/cm³]', 'Atoms [mol]', 'Mass [g]'),
                *('{:^8}{:^9}{:^17}{:^14.6G}{:^11.4G}{:^14.6E}{:^14.6E}'.format(cell.GetNumber(), Zaid2Isotope(zaid), '.{} ({})'.format(Zaid2Id(zaid), int(round(zaid2Temperature[zaid] * kelvinPerMev / 15)) * 15), cell.GetZaidNumberDensity(zaid), cell.GetZaidMassDensity(zaid), cell.GetZaidMoles(zaid), cell.GetZaidMass(zaid)) for cell in cells for zaid in sorted(cell.GetZaids(), key = NumericStringKey)),
                sep = '\n'
                );
        ###
        if arguments.reportIsotopes:
            ###
            # Union of isotopes
            ###
            PrintNow(
                '> All isotopes',
                *('{:>10}'.format(zaid) for zaid in sorted({zaid for material in self.GetMaterials() for zaid in material.GetZaids()}, key = NumericStringKey)),
                sep = '\n'
                );
        ###
        if arguments.reportTallys:
            ###
            # tally # -> tally type, spaces
            ###
            PrintNow(
                '> Tally spaces',
                '{:^9}{:^6}{:^50}'.format('Tally #', 'Type', 'Surfaces or cells'),
                *('{0.number:^9}{0.mnemonic:^6}{1:^50}'.format(tally, ', '.join(str(space) for space in tally.GetSpaces())) for tally in self.GetTallys()),
                sep = '\n'
                );
        ###
        return;
    ###
    # Automated input file methods
    ###
    def AppendNewputCard(self, card):
        self.newputRaw += '\n{}'.format(str(card).strip());
        ###
        return;
    ###
    def GetIsUpdated(self):
        return hasattr(self, 'newputRaw');
    ###
    def GetNewputFileName(self, depletionStep):
        fileName = self.GetFileName();
        if '.' in fileName:
            fileName = '.'.join(fileName.split('.')[ : -1]);
        ###
        return '{}.{:03d}'.format(fileName, depletionStep);
    ###
    def GetNewputRaw(self):
        return self.newputRaw;
    ###
    def ResetNewput(self):
        self.newputRaw = self.GetInputRaw();
        ###
        return;
    ###
    def ReplaceNewputCard(self, oldCard, newCard):
        if not hasattr(self, 'newputRaw'):
            self.ResetNewput();
        ###
        if newCard:
            newCard = '\n{}'.format(str(newCard).strip());
        ###
        self.newputRaw = oldCard.GetRegex().sub(newCard, self.GetNewputRaw());
        ###
        return;
    ###
    def ReplaceNamedNewputCard(self, oldCardName, newCard):
        oldCard = self.GetNamedCard(oldCardName);
        ###
        self.ReplaceNewputCard(oldCard, newCard);
        ###
        return;
###
# MCNP output file parser
###
class McnpOutputFile:
    def __init__(self, fileName):
        self.fileName = fileName;
        ###
        self.outputRaw = ReadFile(self.GetFileName(), display = not bool(arguments.isQuiet));
        ###
        self.Populate();
        ###
        return;
    ###
    def __str__(self):
        lines = ['< Transport results summary for `{}\' >'.format(self.GetFileName())];
        ###
        nameValue = (
            ('keff', '{:.5f} ± {:.5f}'.format(self.GetMultiplicationFactor(), self.GetMultiplicationFactorSigma())),
            ('nu', '{:.3f}    [n/fiss]'.format(self.GetNeutronsPerFission())),
            ('Q', '{:.2f}   [MeV/fiss]'.format(self.GetMevPerFission())),
            ('src', '{:.5E} [n/s]'.format(self.GetSourceRate(realSourceRate = True))),
        );
        ###
        for name, value in nameValue:
                lines.append('{:<9s} = {:>23s}'.format(name, value));
        ###
        return '\n'.join('{:^59}'.format(line) for line in lines);
    ###
    # Generic getter methods
    ###
    def GetFileName(self):
        return self.fileName;
    ###
    def GetOutputRaw(self):
        return self.outputRaw;
    ###
    def GetMevPerFission(self):
        return self.mevPerFission;
    ###
    def GetMcnpInputFile(self):
        return self.mcnpInputFile;
    ###
    def GetMultiplicationFactor(self):
        return self.multiplicationFactor;
    ###
    def GetMultiplicationFactorRV(self):
        return RandomVariable(self.GetMultiplicationFactor(), self.GetMultiplicationFactorSigma(), isStd = True);
    ###
    def GetMultiplicationFactorSigma(self):
        return self.multiplicationFactorSigma;
    ###
    def GetNeutronsPerFission(self):
        return self.neutronsPerFission;
    ###
    def GetSourceRate(self, realSourceRate = False):
        try:
            multiplier = 1.;
            if realSourceRate:
                multiplier = self.GetMultiplicationFactor();
            ###
            return self.sourceRate * multiplier;
        except AttributeError:
            return 1.;
    ###
    # Automated input file methods
    ###
    def GetIsUpdated(self):
        return hasattr(self.GetMcnpInputFile(), 'newputRaw');
    ###
    # Physical quantity getter methods
    ###
    def GetCellNumberFissionPower(self, cellNumber):
        return self.GetCellNumberQPower(cellNumber, 'mcnp');
    ###
    def GetCellNumberFissionRate(self, cellNumber, mnemonic = 'fm4'):
        ###
        # Accumulate fission rate from each leaf cell
        ###
        reactionNumber = -6;
        ###
        return sum(self.GetCellNumberReactionRate(leafCell.GetNumber(), self.FindSingleZaidMaterialNumber(zaid), reactionNumber, doFloat = True) for leafCell in self.FindLeafCells(cellNumber) for zaid in self.FindCellMaterial(cellNumber).GetZaids() if ZaIsActinide(Zaid2Za(zaid)));
    ###
    def GetCellNumberOrigenPower(self, cellNumber, isOrigen2):
        return self.GetCellNumberQPower(cellNumber, qMethod = ['origens', 'origen2'][isOrigen2]);
    ###
    def GetCellNumberMicroscopicCrossSection(self, cellNumber, materialNumber, reactionNumber):
        ###
        # reactionNumber = -6 is synonymous with reactionNumber = 18
        ###
        if 18 == reactionNumber:
            reactionNumber = -6;
        ###
        # Ignore the possibility of leaf cells
        ###
        scalarFlux = 0;
        for tally in self.GetTallys('f4'):
            if cellNumber in tally:
                try:
                    ###
                    # [n/cm²·sn]
                    ###
                    scalarFlux = float(tally.GetTallyResults(cellNumber));
                except KeyError:
                    ###
                    # Continue on fail
                    ###
                    continue;
                ###
                # Kick out after a single tally
                ###
                break;
        ###
        # Ignore the possibility of leaf cells
        ###
        reactionsPerN = 0;
        for tally in self.GetTallys('fm4'):
            ###
            # Kick out tallies that do not contain cell
            ###
            if cellNumber not in tally:
                continue;
            try:
                ###
                # Ignore the possibility of non-unity multipliers
                # [rxn/sn·N]
                ###
                reactionsPerN = float(tally.GetTallyResults(cellNumber, (materialNumber, reactionNumber)));
            except KeyError:
                ###
                # Perhaps another tally for this cell contains the multiplier bins we want
                ###
                continue;
            ###
            # Kick out after a single tally
            ###
            break;
        ###
        return SafeDivide(reactionsPerN, scalarFlux);
    ###
    def GetCellNumberParticlePower(self, cellNumber, mnemonic = 'f6'):
        power = 0;
        ###
        for tally in self.GetTallys(mnemonic):
            ###
            # Kick out tallies that do not contain cell
            ###
            if cellNumber not in tally:
                continue;
            ###
            multiplier = self.FindCell(cellNumber).GetMass() * joulePerMev;
            ###
            # [Jth/sn]
            ###
            power += tally.GetTallyResults(cellNumber) * multiplier;
        ###
        return power * self.GetSourceRate();
    ###
    def GetCellNumberQPower(self, cellNumber, qMethod):
        if 'mcnp' == qMethod:
            ZRs = ((QFissionMCNP, -6), );
        elif 'monteburns2' == qMethod:
            ZRs = ((QFissionMonteburns2, -6), );
        elif 'origen2' == qMethod or 'mocup' == qMethod or 'imocup' == qMethod:
            ZRs = ((QFissionOrigen2, -6), );
        elif 'origens' == qMethod:
            ZRs = ((QFissionOrigenS, -6), (QCaptureOrigenS, 102));
        ###
        return joulePerMev * sum(sum(Za2Q(Zaid2Za(zaid)) * self.GetCellNumberReactionRate(cellNumber, self.FindSingleZaidMaterialNumber(zaid), reactionNumber, doFloat = True) for zaid in self.FindCellMaterial(cellNumber).GetZaids() if ZaIsActinide(Zaid2Za(zaid))) for Za2Q, reactionNumber in ZRs);
    ###
    def GetCellNumberReactionRate(self, cellNumber, materialNumber, reactionNumber, mnemonic = 'fm4', forMicro = False, doFloat = False):
        ###
        #
        ###
        FloatHelper = float;
        if not doFloat:
            FloatHelper = lambda arg: arg;
        ###
        # reactionNumber = -6 is synonymous with reactionNumber = 18
        ###
        if 18 == reactionNumber:
            reactionNumber = -6;
        ###
        # Accumulate reaction rate from each leaf cell
        ###
        totalReactionRatePerNumberDensity = totalVolume = 0;
        for leafCell in self.FindLeafCells(cellNumber):
            ###
            # Use leaf cell materials if no material number is given
            ###
            leafCellMaterialNumber = materialNumber or leafCell.GetMaterialNumber();
            ###
            leafCellMaterial = self.FindMaterial(leafCellMaterialNumber);
            ###
            # Divide by the number of physical instantiations of leaf cell
            ###
            divisor = 1.;
            if self.GetIsMultiplyRootedLeafCell(leafCell.GetNumber()):
                divisor *= len(self.GetMultiplyRootedLeafCell(leafCell.GetNumber()));
            ###
            for tally in self.GetTallys(mnemonic):
                ###
                # Kick out tallies that do not contain leaf cell
                ###
                if leafCell not in tally:
                    continue;
                ###
                for multiplierBin in tally.GetMultiplierBins():
                    ###
                    # Kick out multiplier bins that do not contain leaf cell number, reaction number
                    ###
                    if (cellNumber, leafCellMaterialNumber, reactionNumber) != (multiplierBin[0], multiplierBin[2], multiplierBin[3]):
                        continue;
                    ###
                    # Volume
                    ###
                    volume = leafCell.GetVolume();
                    totalVolume += volume;
                    ###
                    # Divide out non-unity multipliers
                    ###
                    multiplier = SafeDivide(volume, abs(multiplierBin[1]));
                    ###
                    # Multiply isotopic tallys by the number density
                    ###
                    if not forMicro:
                        if leafCellMaterial.GetIsSingleIsotope():
                            zaid = next(iter(leafCellMaterial.GetZaids()));
                            ###
                            try:
                                numberDensity = leafCell.GetZaidNumberDensity(zaid);
                            except KeyError:
                                numberDensity = 0;
                            multiplier *= numberDensity;
                    ###
                    # [rxn/sn] or [rxn/sn·N]
                    ###
                    totalReactionRatePerNumberDensity += FloatHelper(tally.GetTallyResults(leafCell.GetNumber(), (leafCellMaterialNumber, reactionNumber))) * SafeDivide(multiplier, divisor);
        ###
        if not forMicro:
            totalVolume = 1.;
        ###
        return SafeDivide(totalReactionRatePerNumberDensity * self.GetSourceRate(), totalVolume);
    ###
    def GetCellNumberScalarFlux(self, cellNumber, mnemonic = 'f4'):
        ###
        # flux = track length / volume
        ###
        return SafeDivide(*self.GetCellNumberTrackLengthVolume(cellNumber, mnemonic));
    ###
    def GetCellNumberTrackLengthVolume(self, cellNumber, mnemonic = 'f4'):
        totalTrackLength = totalVolume = 0;
        ###
        # Accumulate track lengths and volumes from each leaf cell
        ###
        for leafCell in self.FindLeafCells(cellNumber):
            ###
            # Volume;
            # Divide by the number of physical instantiations of leaf cell
            ###
            volume = leafCell.GetVolume();
            if self.GetIsMultiplyRootedLeafCell(leafCell.GetNumber()):
                volume /= len(self.GetMultiplyRootedLeafCell(leafCell.GetNumber()));
            totalVolume += volume;
            ###
            # Track length
            ###
            trackLength = 0;
            for tally in self.GetTallys(mnemonic):
                if leafCell in tally:
                    try:
                        ###
                        # [n·cm/sn]
                        ###
                        trackLength += tally.GetTallyResults(leafCell.GetNumber()) * volume;
                    except KeyError:
                        ###
                        # Continue on fail
                        ###
                        continue;
            ###
            totalTrackLength += trackLength;
        ###
        return (totalTrackLength * self.GetSourceRate(), totalVolume);
    ###
    # Population methods
    ###
    def Populate(self):
        ###
        # Populate mcnp input file
        ###
        self.mcnpInputFile = McnpInputFile(self.GetFileName(), self.GetOutputRaw());
        ###
        # Populate pointers to mcnp input file methods
        ###
        self.PopulateMcnpInputFileMethods();
        ###
        # Populate tally results
        ###
        self.PopulateTallyResults();
        ###
        # Populate kcode results
        ###
        if self.GetIsKcode():
            self.PopulateMultiplicationResults();
        ###
        return;
    ###
    def PopulateMcnpInputFileMethods(self):
        mcnpInputFileMethods = (
            'FindCell',
            'FindCellMaterial',
            'FindLeafCells',
            'FindMaterial',
            'FindSingleZaidMaterialNumber',
            'GetCells',
            'GetFissionCells',
            'GetInputRaw',
            'GetIsCoupled',
            'GetIsKcode',
            'GetIsMultiplyRootedLeafCell',
            'GetMaterials',
            'GetMultiplyRootedLeafCell',
            'GetNewputRaw',
            'GetPowerCells',
            'GetTallys',
            'GetTallyIndices',
            'ReplaceNewputCard',
            'ResetNewput',
            );
        ###
        mcnpInputFile = self.GetMcnpInputFile();
        ###
        for method in mcnpInputFileMethods:
            setattr(self, method, getattr(mcnpInputFile, method));
        ###
        return;
    ###
    def PopulateTallyResults(self):
        ###
        # Parse tally results
        ###
        tallyBlocks = ['1{}'.format(block) for block in ReCompile(r'^1', 2 | 8).split(self.GetOutputRaw()) if 'tally ' == block[ : 6] and 'f' != block[6]];
        for tally in self.GetTallys():
            reTally = ReCompile(r'^1tally *{}'.format(tally.GetNumber()), 2 | 8);
            ###
            for tallyBlock in tallyBlocks:
                if reTally.search(tallyBlock):
                    tally.PopulateResults(tallyBlock);
                    ###
                    break;
        ###
        return;
    ###
    def PopulateMultiplicationResults(self):
        ###
        # Kick out if multiplication results don't exist
        ###
        if not ReCompile(r'final estimated', 2 | 8).search(self.GetOutputRaw()):
            Warning('Transport output does not contain multiplication factor results');
            ###
            self.neutronsPerFission = self.multiplicationFactor = self.multiplicationFactorSigma = self.mevPerFission = None;
            return;
        ###
        # Neutrons per fission
        ###
        self.neutronsPerFission = float(ReCompile(r'the average number of neutrons produced per fission = ([\d\.]{5})', 2 | 8).search(self.GetOutputRaw()).group(1));
        ###
        # Multiplication factor and its counting uncertainty
        ###
        multiplicationFactor, multiplicationFactorSigma = ReCompile(r'the final estimated.+([\d\.]{7}) with an estimated.+([\d\.]{7})', 2 | 8).search(self.GetOutputRaw()).groups();
        ###
        self.multiplicationFactor = float(multiplicationFactor);
        self.multiplicationFactorSigma = float(multiplicationFactorSigma);
        ###
        # Effective fission Q
        ###
        fissionPower = sum(float(self.GetCellNumberFissionPower(cellNumber)) for cellNumber in self.GetFissionCells());
        fissionRate = sum(float(self.GetCellNumberFissionRate(cellNumber)) for cellNumber in self.GetFissionCells());
        ###
        self.mevPerFission = SafeDivide(fissionPower * mevPerJoule, fissionRate);
        ###
        return;
    ###
    def PopulateSourceRate(self, sourceRate):
        self.sourceRate = sourceRate;
        ###
        return;
    ###
    # Report methods
    ###
    def Report(self, arguments):
        ###
        if arguments.reportKeff:
            ###
            # Call __str__ method
            ###
            PrintNow(self);
        ###
        if arguments.writeEnergyDepositions: # FIXME Thermal energy? Decay heat too?
            ###
            pass;
        ###
        if arguments.writeFissionEnergyDepositions:
            ###
            # Fission-Energy-Deposition
            # F
            ###
            fileName = '{}.{}'.format(self.GetMcnpInputFile().GetFileName(), 'fedep');
            tallyResults = {(cellNumber, ) : self.GetCellNumberFissionPower(cellNumber) for cellNumber in self.GetTallyIndices('f4')}; # FIXME This is a float instead of a TallyResult!
            ###
            baseUnits = 'J_f / source - ';
            if arguments.writeFissionEnergyDepositions in ('ebin', 'bin'):
                getter, units = 'GetPerBins', '{}Ebin'.format(baseUnits);
            elif arguments.writeFissionEnergyDepositions in ('energy', 'mev'):
                getter, units = 'GetPerEnergys', '{}MeV'.format(baseUnits);
            elif arguments.writeFissionEnergyDepositions in ('lethargy', 'leth'):
                getter, units = 'GetPerLethargys', '{}lethargy'.format(baseUnits);
            elif arguments.writeFissionEnergyDepositions in ('normalized', 'norm'):
                getter, units = 'GetNormPerLethargys', '1 / lethargy';
            elif arguments.writeFissionEnergyDepositions in ('uncertainty', 'std'):
                getter, units = 'GetRelativeUncertaintys', '1 / \sigma / Ebin';
            ###
            headerFormat = 'Fission-Energy-Deposition (cell {{}}) [{}]'.format(units);
            ###
            self.WritePhysicalQuantity(fileName, getter, headerFormat, tallyResults, arguments.downSample);
        ###
        if arguments.writeMicroscopicCrosssections:
            ###
            pass;
        ###
        if arguments.writeReactionRates:
            ###
            # Reaction-Rate
            # R
            ###
            fileName = '{}.{}'.format(self.GetMcnpInputFile().GetFileName(), 'rxn');
            cellNumber2PossibleMaterialNumbers = self.GetCellNumber2PossibleMaterialNumbers();
            tallyResults = {(cellNumber, materialNumber, reactionNumber) : self.GetCellNumberReactionRate(cellNumber, materialNumber, reactionNumber) for cellNumber, multiplierBins in self.GetTallyIndices('fm4').items() for materialNumber, reactionNumber in multiplierBins if materialNumber in cellNumber2PossibleMaterialNumbers[cellNumber]};
            ###
            baseUnits = 'reactions / source - ';
            if arguments.writeReactionRates in ('ebin', 'bin'):
                getter, units = 'GetPerBins', '{}Ebin'.format(baseUnits);
            elif arguments.writeReactionRates in ('energy', 'mev'):
                getter, units = 'GetPerEnergys', '{}MeV'.format(baseUnits);
            elif arguments.writeReactionRates in ('lethargy', 'leth'):
                getter, units = 'GetPerLethargys', '{}lethargy'.format(baseUnits);
            elif arguments.writeReactionRates in ('normalized', 'norm'):
                getter, units = 'GetNormPerLethargys', '1 / lethargy';
            elif arguments.writeReactionRates in ('uncertainty', 'std'):
                getter, units = 'GetRelativeUncertaintys', '1 / \sigma / Ebin';
            ###
            headerFormat = 'Reaction-Rate (cell {{}}; material {{}}; reaction {{}}) [{}]'.format(units);
            ###
            self.WritePhysicalQuantity(fileName, getter, headerFormat, tallyResults, arguments.downSample);
        ###
        if arguments.writeScalarFluxes:
            ###
            fileName = '{}.{}'.format(self.GetMcnpInputFile().GetFileName(), 'flx');
            ###
            # Scalar-Flux
            # \phi
            ###
            tallyResults = {(cellNumber, ) : self.GetCellNumberScalarFlux(cellNumber) for cellNumber in self.GetTallyIndices('f4')};
            baseUnits = 'particles / source - cm^2 - ';
            ###
            if arguments.writeScalarFluxes in ('ebin', 'bin'):
                getter, units = 'GetPerBins', '{}Ebin'.format(baseUnits);
            elif arguments.writeScalarFluxes in ('energy', 'mev'):
                getter, units = 'GetPerEnergys', '{}MeV'.format(baseUnits);
            elif arguments.writeScalarFluxes in ('lethargy', 'leth'):
                getter, units = 'GetPerLethargys', '{}lethargy'.format(baseUnits);
            elif arguments.writeScalarFluxes in ('normalized', 'norm'):
                getter, units = 'GetNormPerLethargys', '1 / lethargy';
            elif arguments.writeScalarFluxes in ('uncertainty', 'std'):
                getter, units = 'GetRelativeUncertaintys', '1 / \sigma / Ebin';
            ###
            headerFormat = 'Scalar-Flux (cell {{}}) [{}]'.format(units);
            ###
            self.WritePhysicalQuantity(fileName, getter, headerFormat, tallyResults, arguments.downSample);
        ###
        # Call MCNP input file's report
        ###
        self.GetMcnpInputFile().Report(arguments);
        ###
        return;
    ###
    def WritePhysicalQuantity(self, fileName, getter, headerFormat, tallyResults, downSample):
        ###
        # Kick out null tally results
        ###
        if not tallyResults or not any(float(tallyResult) for tallyResult in tallyResults.values()):
            return;
        ###
        # Down-sample results
        ###
        while downSample:
            isNegative = downSample < 0;
            tallyResults = {key : tallyResult.HalfSample(isNegative) for key, tallyResult in tallyResults.items()};
            downSample -= (-1) ** isNegative;
        ###
        # Header line
        ###
        headers = ['Neutron Energy [MeV]'];
        headers.extend(headerFormat.format(*key) for key in sorted(tallyResults));
        ###
        # Data lines
        ###
        data = next(iter(tallyResults.values())).GetEnergys().reshape(-1, 1);
        data = Concatenate((data, Concatenate(list(getattr(tallyResults[key], getter)().reshape(-1, 1) for key in sorted(tallyResults)), axis = 1)), axis = 1);
        ###
        # Kick out null-valued data
        ###
        if not len(data):
            return;
        ###
        # Write .csv file
        ###
        WriteCsvFile(fileName, [headers], data);
        ###
        return;
###
# ORIGEN2.2 output file parser
###
class OrigenCalculation:
    def __init__(self, suffix, cellVolume, directory = ''):
        self.suffix = suffix;
        self.volume = cellVolume;
        self.directory = directory;
        ###
        self.Populate();
        ###
        return;
    ###
    # Generic getter methods
    ###
    def GetBurnup(self):
        return self.burnup;
    ###
    def GetDecayPower(self, za2WattsPerMole):
        return sum(moles * za2WattsPerMole[Zaid2Za(zaid)] for zaid, moles in self.GetZaid2Moles().items() if Zaid2Za(zaid) in za2WattsPerMole);
    ###
    def GetDirectory(self):
        return self.directory;
    ###
    def GetFlux(self):
        return self.flux;
    ###
    def GetMoles(self):
        return sum(self.GetZaid2Moles().values());
    ###
    def GetPower(self):
        return self.power;
    ###
    def GetSuffix(self):
        return self.suffix;
    ###
    def GetNumberDensity(self):
        return sum(self.GetZaid2NumberDensity().values());
    ###
    def GetMassDensity(self):
        return sum(self.GetZaid2MassDensity().values());
    ###
    def GetMicros(self):
        return self.micros;
    ###
    def GetTableTotal(self, tableNumber):
        return sum(self.GetZaidTableNumber2Value(tableNumber).values());
    ###
    def GetTAPE4(self):
        return self.TAPE4;
    ###
    def GetTAPE5(self):
        return self.TAPE5;
    ###
    def GetTAPE6(self):
        return self.TAPE6;
    ###
    def GetTAPE7(self):
        return self.TAPE7;
    ###
    def GetTAPE9(self):
        return self.TAPE9;
    ###
    def GetTAPE10(self):
        return self.TAPE10;
    ###
    def GetVolume(self):
        return self.volume;
    ###
    def GetZaid2AbsorptionFraction(self):
        tableNumber = 19;
        totalAbsorptionRate = self.GetTableTotal(tableNumber);
        ###
        return {zaid : absorptionRate / totalAbsorptionRate for zaid, absorptionRate in self.GetZaidTableNumber2Value(tableNumber).items()};
    ###
    def GetZaid2AtomFraction(self):
        totalMoles = self.GetMoles();
        ###
        return {zaid : moles / totalMoles for zaid, moles in self.GetZaid2Moles().items()};
    ###
    def GetZaid2FissionFraction(self):
        tableNumber = 21;
        totalFissionRate = self.GetTableTotal(tableNumber);
        ###
        return {zaid : fissionRate / totalFissionRate for zaid, fissionRate in self.GetZaidTableNumber2Value(tableNumber).items()};
    ###
    def GetZaid2Moles(self):
        return self.zaid2Moles;
    ###
    def GetZaid2NumberDensity(self):
        volume = self.GetVolume();
        ###
        return {zaid : moles * avogadrosNumber / volume for zaid, moles in self.GetZaid2Moles().items()};
    ###
    def GetZaid2MassDensity(self):
        volume = self.GetVolume();
        ###
        return {zaid : moles * Zaid2MolarMass(zaid) / volume for zaid, moles in self.GetZaid2Moles().items()};
    ###
    def GetZaidTableNumber2Value(self, tableNumber):
        return self.zaid2TableNumber2Value[tableNumber];
    ###
    def GetZaid2WeightFraction(self):
        totalMassDensity = self.GetMassDensity();
        ###
        return {zaid : massDensity / totalMassDensity for zaid, massDensity in self.GetZaid2MassDensity().items()};
    ###
    # Population methods
    ###
    def AttachMicros(self, micros):
        self.micros = micros;
        ###
        return;
    ###
    def Populate(self):
        ###
        # Read TAPE4.INP
        ###
        self.TAPE4 = ReadFile('{}TAPE4.INP'.format(self.GetDirectory()), display = not bool(arguments.isQuiet));
        ###
        # Read TAPE5.INP
        ###
        self.TAPE5 = ReadFile('{}TAPE5.INP'.format(self.GetDirectory()), display = not bool(arguments.isQuiet));
        ###
        # Read TAPE6.OUT
        ###
        self.TAPE6 = ReadFile('{}TAPE6.OUT'.format(self.GetDirectory()), display = not bool(arguments.isQuiet));
        ###
        # Read TAPE7.OUT
        ###
        self.TAPE7 = ReadFile('{}TAPE7.OUT'.format(self.GetDirectory()), display = not bool(arguments.isQuiet));
        ###
        # Read TAPE9.INP
        ###
        self.TAPE9 = ReadFile('{}TAPE9.INP'.format(self.GetDirectory()), display = not bool(arguments.isQuiet));
        ###
        # Read TAPE10.INP
        ###
        self.TAPE10 = ReadFile('{}TAPE10.INP'.format(self.GetDirectory()), display = not bool(arguments.isQuiet));
        ###
        # Extract isotopic moles from .pch file
        ###
        suffix = self.GetSuffix();
        numbers = [float(number) for line in self.GetTAPE7().split('\n') for number in line[5 : ].split()];
        self.zaid2Moles = {Zam2Zaid(int(numbers[index]), suffix) : numbers[index + 1] for index in range(0, len(numbers) - 4, 2) if numbers[index + 1] and numbers[index]};
        ###
        # Extract burnup, flux, and power from .pch file
        ###
        self.burnup, self.flux, self.power = numbers[-3 : ];
        ###
        # Extract absorption rate (19) and fission rate (21) from .out file
        ###
        reBlock = r'^0 +{}( .+\n){{,70}}^[01]';
        reIsotopeValue = ReCompile(r'^([ A-Z]{3}[ 0-9]{3}M?) +( \d\.\d{3}e[+\-]\d\d)+$', 2 | 8);
        ###
        TAPE6 = self.GetTAPE6();
        tableNumbers = (7, 15, 19, 21); # FIXME For when parsing Ci's and radiotoxicities
        tableNumbers = (19, 21);
        self.zaid2TableNumber2Value = {tableNumber : {Zam2Zaid(Isotope2Zam(isotope), suffix) : float(value) for block in ReCompile(reBlock.format(tableNumber), 2 | 8).finditer(TAPE6) for isotopeValue in reIsotopeValue.finditer(block.group()) for isotope, value in [isotopeValue.groups()] if float(value) > 0} for tableNumber in tableNumbers};
        ###
        return;
###
# Random variable: float with uncertainty
###
class RandomVariable:
    def __abs__(self):
        expected = abs(self.GetExp());
        variance = self.GetVar();
        ###
        return RandomVariable(expected, variance, isVar = True);
    def __bool__(self):
        return bool(self.GetExp());
    ###
    def __float__(self):
        return self.GetExp();
    ###
    def __init__(self, expected, uncertainty, isStd = False, isVar = False):
        self.expected = float(expected);
        uncertainty = float(uncertainty);
        ###
        if isStd:
            self.variance = uncertainty ** 2;
        elif isVar:
            self.variance = uncertainty;
        else:
            self.variance = expected ** 2 * uncertainty ** 2;
        ###
        return;
    ###
    def __lt__(self, other):
        return float(self) < other;
    ###
    def __str__(self):
        return '{:>+10.5f} ± {: >7.5f}'.format(self.GetExp(), self.GetStd());
    ###
    # Mathematical operator overloaders
    ###
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            ###
            # Expected is affected
            ###
            expected = self.GetExp() + other;
            ###
            # Variance is not affected
            ###
            variance = self.GetVar();
        elif isinstance(other, self.__class__):
            ###
            # var = var_a + var_b + (2 * corr_ab * std_a * std_b)
            # Correlation is assumed as 0 for addition
            ###
            correlationCoefficient = 0;
            ###
            expected = self.GetExp() + other.GetExp();
            variance = self.GetVar() + other.GetVar() + (2 * self.GetStd() * other.GetStd() * correlationCoefficient);
        elif isinstance(other, TallyResult):
            return other.__add__(self);
        ###
        return RandomVariable(expected, variance, isVar = True);
    ###
    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            ###
            # Expected, variance is affected
            ###
            expected = self.GetExp() * other;
            variance = self.GetVar() * other ** 2;
        elif isinstance(other, self.__class__):
            ###
            # relvar = relvar_a + relvar_b + (2 * relstd_a * relstd_b * corr_ab)
            # Correlation is assumed as +1 for multiplication
            ###
            correlationCoefficient = +1;
            ###
            expected = self.GetExp() * other.GetExp();
            variance = expected ** 2 * (self.GetRelVar() + other.GetRelVar() + 2 * self.GetRelStd() * other.GetRelStd() * correlationCoefficient);
        elif isinstance(other, TallyResult):
            return other.__mul__(self);
        ###
        return RandomVariable(expected, variance, isVar = True);
    ###
    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self * SafeDivide(1, other);
        elif isinstance(other, self.__class__):
            ###
            # relvar = relvar_a + relvar_b + (2 * relstd_a * relstd_b * corr_ab)
            # Correlation is assumed as -1 for division
            ###
            correlationCoefficient = -1;
            ###
            expected = SafeDivide(self.GetExp(), other.GetExp());
            variance = expected ** 2 * abs(self.GetRelVar() + other.GetRelVar() - 2 * self.GetRelStd() * other.GetRelStd() * correlationCoefficient);
        ###
        return RandomVariable(expected, variance, isVar = True);
    ###
    def __pow__(self, other):
        assert(isinstance(other, int) or isinstance(other, float));
        ###
        if other < 0:
            return (RandomVariable(1, 0) / self).__pow__(-1 * other);
        elif 0 == other:
            return 1;
        elif 0 == other % 2:
            return (self * self).__pow__(other / 2);
        else:
            return self * self.__pow__(other - 1);
    ###
    __radd__ = __add__;
    ###
    __rmul__ = __mul__;
    ###
    __rtruediv__ = lambda self, other: other * self.__pow__(-1);
    ###
    def __sub__(self, other):
        return self.__add__(-other);
    ###
    def __rsub__(self, other):
        return -self.__sub__(other);
    ###
    def __pos__(self):
        return self;
    ###
    def __neg__(self):
        return -1 * self;
    ###
    def __eq__(self, other):
        return float(self) == float(other);
    ###
    def __lt__(self, other):
        return float(self) < float(other);
    ###
    # Getters
    ###
    def GetExp(self):
        return self.expected;
    ###
    def GetRelStd(self):
        return self.GetRelVar() ** 0.5;
    ###
    def GetStd(self):
        return self.GetVar() ** 0.5;
    ###
    def GetRelVar(self):
        return SafeDivide(self.GetVar(), self.GetExp() ** 2);
    ###
    def GetVar(self):
        return self.variance;
    ###
    GetElements = GetTotalElement = GetExp;
    GetRelativeVariances = GetRelVar;
    GetRelativeUncertaintys = GetTotalRelativeUncertainty = GetRelStd;
###
# Accelerated recycle calculation
###
class RecycleCalculation:
    def __init__(self, arguments):
        ###
        # Set argument attributes
        ###
        self.arguments = arguments;
        ###
        # Run recycle calculation
        ###
        self.Recycle();
        ###
        return;
    ###
    # Generic getter methods
    ###
    def GetArguments(self):
        return self.arguments;
    ###
    def GetDisplayFiles(self):
        return not bool(self.GetArguments().isQuiet);
    ###
    def GetIsPickleTransmute(self):
        return self.isPickleTransmute;
    ###
    def GetParameter(self, key):
        return self.GetParameters()[key];
    ###
    def GetParameters(self):
        return mocDownInputFile.GetParameters();
    ###
    def GetRecycleIndex(self):
        return self.recycleIndex;
    ###
    def GetRecycleString(self):
        return '{} recycle #{:d}'.format(['transport/transmute', 'transmute-only'][self.GetIsPickleTransmute()], self.GetRecycleIndex());
    ###
    # Recycle methods
    ###
    def Recycle(self):
        PrintNow('> {} will recycle to equilibrium'.format(__file__));
        ###
        # First, a transport/transmute recycle is performed;
        # In order to preserve it for multiplication convergence, isConverged is set to True
        ###
        transportFile = depletionCalculation = None;
        ###
        self.recycleIndex = self.isPickleTransmute = False;
        isConverged = True;
        ###
        # Recycle until multiplication has converged
        ###
        while True:
            ###
            # Save previous calculation for multiplication convergence
            ###
            previousDepletionCalculation = depletionCalculation;
            ###
            # Recycle until isotopics have converged
            ###
            while True:
                ###
                # Prepare depletion calculation
                ###
                self.PrepareRecycle(transportFile);
                ###
                # Run depletion calculation
                ###
                PrintNow('> Depleting {}'.format(self.GetRecycleString()));
                depletionCalculation = DepletionCalculation(self.GetArguments(), isPickleTransmute = self.GetIsPickleTransmute());
                ###
                # Switch off restarts following the first depletion cycle
                ###
                self.arguments.isRestart = False;
                ###
                # Save previous transport file for isotopics convergence
                ###
                previousTransportFile = transportFile;
                ###
                # Extract processed transport input raw for isotopics convergence
                ###
                transportFile = depletionCalculation.ProcessFuel();
                ###
                # Archive depletion calculation recycle
                ###
                self.ArchiveRecycle();
                ###
                # Kick out if isotopics have converged
                ###
                if isConverged:
                    break;
                ###
                # Determine if BOEC isotopics have converged;
                # If so, kick out after one last transport/transmute recycle;
                # If not, continue transmute-only recycles
                ###
                isConverged = self.IsotopicsHaveConverged(previousTransportFile, transportFile);
                ###
                self.isPickleTransmute = not isConverged;
                ###
                # Increment recycle index
                ###
                self.IncrementRecycleIndex();
            ###
            # Determine if EOEC multiplication has converged;
            # If so, kick out immediately;
            # If not, continue transmute-only recycles
            ###
            if self.MultiplicationHasConverged(previousDepletionCalculation, depletionCalculation):
                break;
            else:
                isConverged = False;
                ###
                self.isPickleTransmute = True;
            ###
            # Increment recycle index
            ###
            self.IncrementRecycleIndex();
        ###
        # Prepare BOEC transport input
        ###
        self.PrepareRecycle(transportFile, finale = True);
        ###
        return;
    ###
    def PrepareRecycle(self, transportFile, finale = False):
        ###
        # If this is a pickle transmute recycle, unarchive pickles from the previous recycle
        ###
        if self.GetIsPickleTransmute() and bool(self.GetRecycleIndex()) and not finale:
            PrintNow('> Unarchiving (linking) previous recycle');
            directoryName = './{:03d}/'.format(self.GetRecycleIndex() - 1);
            linkFiles = (linkFile.replace(directoryName, '') for linkFile in Glob('{}/{}*.pkl*'.format(directoryName, arguments.transportFileName)));
            ###
            for linkFile in sorted(linkFiles):
                SymbolicLink('{}{}'.format(directoryName, linkFile), linkFile, display = self.GetDisplayFiles());
        ###
        # Maybe write processed input
        ###
        if transportFile is not None:
            WriteFile(arguments.transportFileName, transportFile.GetNewputRaw(), display = self.GetDisplayFiles());
        ###
        return;
    ###
    def ArchiveRecycle(self):
        PrintNow('> Archiving {}'.format(self.GetRecycleString()));
        ###
        # Create backup depletion directory
        ###
        directoryName = './{:03d}/'.format(self.GetRecycleIndex());
        MakeDirectory(directoryName, self.GetDisplayFiles());
        ###
        # Move depletion files
        ###
        transportFileName = arguments.transportFileName;
        moveFiles = [transportFileName, 'transport.log', 'transmute.log'];
        moveFiles.extend(fileName for extension in ('i', 'o', 'pkl', 'gz') for fileName in Glob('{}*.{}'.format(transportFileName, extension)));
        if '.' in transportFileName:
            removeExtension = transportFileName.split('.')[-1];
            moveFiles.extend(fileName for extension in ('i', 'o', 'pkl', 'gz') for fileName in Glob('{}*.{}'.format(transportFileName.replace(removeExtension, ''), extension)));
        ###
        for moveFile in sorted(set(moveFiles), reverse = True):
            MoveFile(moveFile, '{}{}'.format(directoryName, moveFile), display = self.GetDisplayFiles());
        ###
        return;
    ###
    def IncrementRecycleIndex(self):
        self.recycleIndex += 1;
        ###
        return;
    ###
    def IsotopicsHaveConverged(self, transportOne, transportTwo):
        if transportOne is None or transportTwo is None:
            PrintNow('> Isotopics convergence: UNDEFINED during {} ... continue transmute-only recycle'.format(self.GetRecycleString()));
            ###
            return False;
        ###
        norm = abs(transportOne - transportTwo);
        ###
        normType = self.GetParameter('isotopicsConvergenceNormType');
        if normType in ('1', 'one'):
            normCharacter = '1';
        elif normType in ('2', 'two'):
            normCharacter = '2';
        elif normType in ('inf', 'infinite', 'infinity'):
            normCharacter = '∞';
        ###
        if norm > self.GetParameter('isotopicsConvergenceTolerance'):
            PrintNow('> Isotopics convergence: FAILURE (|Δiso|{} = {:.1E} > {:.1E}) during {} ... continue transmute-only recycle'.format(normCharacter, norm, self.GetParameter('isotopicsConvergenceTolerance'), self.GetRecycleString()));
            ###
            return False;
        else:
            PrintNow('> Isotopics convergence: SUCCESS (|Δiso|{} = {:.1E} ≤ {:.1E}) during {} ... perform one last transport/transmute recycle'.format(normCharacter, norm, self.GetParameter('isotopicsConvergenceTolerance'), self.GetRecycleString()));
            ###
            return True;
    ###
    def MultiplicationHasConverged(self, depletionOne, depletionTwo):
        if depletionOne is None or depletionTwo is None:
            PrintNow('> Multiplication convergence: UNDEFINED during {} ... continue transmute-only recycle'.format(self.GetRecycleString()));
            ###
            return False;
        ###
        keffOne, kSigmaOne = depletionOne.MultiplicationFactor(), depletionOne.MultiplicationFactorSigma();
        keffTwo, kSigmaTwo = depletionTwo.MultiplicationFactor(), depletionTwo.MultiplicationFactorSigma();
        ###
        deltaK = abs(keffOne - keffTwo);
        deltaSigmaK = (kSigmaOne ** 2 + kSigmaTwo ** 2) ** 0.5;
        ###
        if deltaK > self.GetParameter('multiplicationFactorConvergenceTolerance'):
            PrintNow('> Multiplication convergence: FAILURE (Δk = {:.5f} ± {:.5f} > {:.5f}) during {} ... continue transmute-only recycle'.format(deltaK, deltaSigmaK, self.GetParameter('multiplicationFactorConvergenceTolerance'), self.GetRecycleString()));
            ###
            return False;
        else:
            PrintNow('> Multiplication convergence: SUCCESS (Δk = {:.5f} ± {:.5f} ≤ {:.5f}) during {} ... equilibrium search is finished'.format(deltaK, deltaSigmaK, self.GetParameter('multiplicationFactorConvergenceTolerance'), self.GetRecycleString()));
            ###
            return True;
###
# Tally result
###
class TallyResult:
    def __bool__(self):
        return bool(self.GetTotalElement());
    ###
    def __float__(self):
        return self.GetTotalElement();
    ###
    def __init__(self, *args):
        if 2 == len(args):
            ###
            # Match iterator and number of iterations
            ###
            matches, numberOfIterations = args;
            ###
            index = 0;
            self.energys, self.elements, self.variances = (Empty(numberOfIterations) for index in range(3));
            ###
            for match in matches:
                if numberOfIterations > max(1, index):
                    ###
                    # Energys, elements, variances
                    ###
                    energy, element, relativeUncertainty = (float(number) for number in match.groups());
                    ###
                    self.energys[index], self.elements[index], self.variances[index] = energy, element, element ** 2. * relativeUncertainty ** 2.;
                else:
                    ###
                    # Total element, total variance
                    ###
                    totalElement, totalRelativeUncertainty = (float(number) for number in match.group(2, 3));
                    ###
                    self.totalElement, self.totalVariance = totalElement, totalElement ** 2. * totalRelativeUncertainty ** 2.;
                    ###
                ###
                index += 1;
        ###
        elif 5 == len(args):
            ###
            # Energys, elements, variances, total element, total variance
            ###
            self.energys, self.elements, self.variances, self.totalElement, self.totalVariance = args;
        ###
        return;
    ###
    def __len__(self):
        return len(self.GetEnergys());
    ###
    # Mathematical operator overloaders
    ###
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            ###
            # Elements and sum(elements) are affected
            ###
            elements = self.GetElements() + other;
            totalElement = self.GetTotalElement() + other;
            ###
            # Variances and sum(variances) are not affected
            ###
            variances = self.GetVariances();
            totalVariance = self.GetTotalVariance();
        ###
        elif isinstance(other, self.__class__):
            assert(len(self) == len(other) and all(self.GetEnergys() == other.GetEnergys()));
            ###
            # var = var_a + var_b + (2 * corr_ab * std_a * std_b)
            # Correlation is assumed as 0 for addition
            ###
            correlationCoefficient = 0;
            ###
            elements = self.GetElements() + other.GetElements();
            variances = self.GetVariances() + other.GetVariances() + (2. * self.GetUncertaintys() * other.GetUncertaintys() * correlationCoefficient);
            totalElement = self.GetTotalElement() + other.GetTotalElement();
            totalVariance = self.GetTotalVariance() + other.GetTotalVariance();
        ###
        return TallyResult(self.GetEnergys(), elements, variances, totalElement, totalVariance);
    ###
    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            ###
            # Elements, variances, sum(elements), sum(variances) are affected
            ###
            elements = self.GetElements() * other;
            variances = self.GetVariances() * (other ** 2.);
            totalElement = self.GetTotalElement() * other;
            totalVariance = self.GetTotalVariance() * (other ** 2.);
        elif isinstance(other, self.__class__) or isinstance(other, RandomVariable):
            if isinstance(other, self.__class__):
                assert(len(self) == len(other) and all(self.GetEnergys() == other.GetEnergys()));
            ###
            # relvar = relvar_a + relvar_b + (2 * relstd_a * relstd_b * corr_ab)
            # Correlation is assumed as 1 for multiplication
            ###
            correlationCoefficient = +1.;
            ###
            elements = self.GetElements() * other.GetElements();
            variances = elements ** 2. * (self.GetRelativeVariances() + other.GetRelativeVariances() + (2. * self.GetRelativeUncertaintys() * other.GetRelativeUncertaintys() * correlationCoefficient));
            ###
            if len(self):
                totalElement = sum(elements);
                ###
                totalVariance = sum(variances);
            else:
                totalElement = self.GetTotalElement() * other.GetTotalElement();
                ###
                totalVariance = totalElement ** 2. * (self.GetTotalRelativeUncertainty() ** 2. + other.GetTotalRelativeUncertainty() ** 2. + (2. * self.GetTotalRelativeUncertainty() * other.GetTotalRelativeUncertainty() * correlationCoefficient));
        ###
        return TallyResult(self.GetEnergys(), elements, variances, totalElement, totalVariance);
        ###
    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self * SafeDivide(1., other);
        elif isinstance(other, self.__class__) or isinstance(other, RandomVariable):
            if isinstance(other, self.__class__):
                assert(len(self) == len(other) and all(self.GetEnergys() == other.GetEnergys()));
            ###
            # relvar = relvar_a + relvar_b - (2 * relstd_a * relstd_b * corr_ab)
            # Correlation is assumed as 1 for division
            ###
            correlationCoefficient = +1.;
            ###
            elements = self.GetElements() / other.GetElements();
            variances = elements ** 2. * abs(self.GetRelativeVariances() + other.GetRelativeVariances() - (2. * self.GetRelativeUncertaintys() * other.GetRelativeUncertaintys() * correlationCoefficient));
            ###
            # Change nan's to zero's
            ###
            elements = Nan2Num(elements);
            elements[abs(elements) > 1e100] = 0;
            variances = Nan2Num(variances);
            variances[abs(variances) > 1e100] = 0;
            ###
            if len(self):
                totalElement = sum(elements);
                ###
                totalVariance = sum(variances);
            else:
                totalElement = SafeDivide(self.GetTotalElement(), other.GetTotalElement());
                ###
                totalVariance = totalElement ** 2. * (self.GetTotalRelativeUncertainty() ** 2. + other.GetTotalRelativeUncertainty() ** 2. - (2. * self.GetTotalRelativeUncertainty() * other.GetTotalRelativeUncertainty() * correlationCoefficient));
        ###
        return TallyResult(self.GetEnergys(), elements, variances, totalElement, totalVariance);
    ###
    __radd__ = __add__;
    ###
    __rmul__ = __mul__;
    ###
    def __sub__(self, other):
        return self.__add__(-other);
    ###
    def __rsub__(self, other):
        return -self.__sub__(other);
    ###
    def __pos__(self):
        return self;
    ###
    def __neg__(self):
        return -1. * self;
    ###
    # Generic getter methods
    ###
    def GetElements(self):
        return self.elements;
    ###
    def GetEnergys(self):
        return self.energys;
    ###
    def GetTotalElement(self):
        return self.totalElement;
    ###
    def GetTotalVariance(self):
        return self.totalVariance;
    ###
    def GetVariances(self):
        return self.variances;
    ###
    # Algorithmic methods
    ###
    def HalfSample(self, doAverage = False):
        isOdd = len(self) % 2;
        ###
        energys = self.GetEnergys()[1 - isOdd : : 2];
        ###
        elements = self.GetElements()[1 - isOdd : : 2] + Concatenate(((0., ) * isOdd, self.GetElements()[isOdd : : 2]));
        variances = self.GetVariances()[1 - isOdd : : 2] + Concatenate(((0., ) * isOdd, self.GetVariances()[isOdd : : 2]));
        totalElement = self.GetTotalElement();
        totalVariance = self.GetTotalVariance();
        ###
        if doAverage:
            elements[isOdd : ] /= 2.;
            variances[isOdd : ] /= 4;
            totalElement /= 2;
            totalVariance /= 4;
        ###
        return TallyResult(energys, elements, variances, totalElement, totalVariance);
    ###
    # Derived statistical getter methods
    ###
    def GetUncertaintys(self):
        return self.GetVariances() ** 0.5;
    ###
    def GetRelativeUncertaintys(self):
        return self.GetRelativeVariances() ** 0.5;
    ###
    def GetRelativeVariances(self):
        return Nan2Num(SafeDivide(self.GetVariances(), self.GetElements() ** 2.));
    ###
    def GetTotalRelativeUncertainty(self):
        return SafeDivide(self.GetTotalVariance(), self.GetTotalElement() ** 2.) ** 0.5;
    ###
    def GetTotalUncertainty(self):
        return self.GetTotalRelativeUncertainty() * abs(self.GetTotalElement());
    ###
    # Bin parameter getter methods
    ###
    def GetEnergyBinMeans(self):
        return self.GetEnergys() - 0.5 * self.GetEnergyPerBins();
    ###
    def GetEnergyPerBins(self):
        return Concatenate((self.GetEnergys()[ : 1], Difference(self.GetEnergys())));
    ###
    def GetLethargyPerBins(self):
        return Nan2Num(-NaturalLogarithm(1. - self.GetEnergyPerBins() / self.GetEnergys()));
    ###
    # Element per getter methods
    ###
    GetPerBins = GetElements;
    ###
    def GetPerEnergys(self):
        return SafeDivide(self.GetPerBins(), self.GetEnergyPerBins());
    ###
    def GetPerLethargys(self):
        return SafeDivide(self.GetPerBins(), self.GetLethargyPerBins());
    ###
    def GetNormPerLethargys(self):
        return SafeDivide(self.GetPerLethargys(), self.GetTotalElement());

###
### Custom functions
###

###
# Assert file exists
###
def AssertFileExists(fileName):
    try:
        assert(isinstance(fileName, str) and Exists(fileName) and FileStatus(fileName)[6]);
    except AssertionError:
        raise IOError('File `{}\' was not found or is empty'.format(fileName));
    ###
    return;
###
# Copy file
###
def CopyFile(pathOne, pathTwo, display = True):
    if display:
        PrintNow('{} -> {}'.format(pathOne, pathTwo));
    if Exists(pathTwo):
        RemoveFile(pathTwo, display);
    if Exists(pathOne):
        LibCopyFile(pathOne, pathTwo);
    ###
    return;
###
# Run gnuplot;
# Run epstopng;
# Run epstopdf;
# Delete .{dat?,plt?}
###
def DoGnuPlot(fileName, keepPlt = False):
    gnuplot = '/usr/local/gnuplot422/bin/gnuplot';
    print('Running gnuplot, epstopng, epstopdf, rm on `{}\'.'.format(fileName.replace('.plt', '')));
    ###
    SystemCall('TMPDIR="/tmp" ; [ -e {eps} ] && rm -f {eps} ; {gnuplot} < {plt} > {eps} && convert -antialias -compress Lossless -density 350 -flatten -quality 95 {eps} {png} && epstopdf {eps} && rm -f {delete}'.format(gnuplot = gnuplot, delete = ['{} {}'.format(fileName, fileName.replace('.plt', '.dat')), ''][keepPlt], eps = fileName.replace('.plt', '.eps'), plt = fileName, png = fileName.replace('.plt', '.png')));
    return;
###
# File exists and is newer
###
def ExistsAndNewer(pathOne, pathTwo):
    AssertFileExists(pathTwo);
    return Exists(pathOne) and GetModificationTime(pathTwo) < GetModificationTime(pathOne);
###
# Import supplementary libraries;
###
def ImportLibraries(moduleFileNames):
    ###
    # Iterate over libraries
    ###
    for moduleFileName in moduleFileNames:
        ###
        # Import module
        ###
        module = __import__(moduleFileName);
        ###
        # Iterate over module contents
        ###
        for subModule in dir(module):
            ###
            # Attach module methods to MocDown
            ###
            for mocDownClass in (DepletionCalculation, RecycleCalculation):
                if subModule in dir(mocDownClass):
                    ###
                    # Kick out builtin methods
                    ###
                    if '__' == subModule[ : 2] == subModule[-2 : ]:
                        continue;
                    ###
                    setattr(mocDownClass, subModule, getattr(module, subModule));
        ###
        # Attach functions and variables
        ###
        currentModule = Modules[__name__];
        for variableName in ('Array', 'Exponent', 'LinearInterpolate', 'McnpInputFile', 'Nan2Num', 'NaturalLogarithm', 'NonZero', 'PrintNow', 'Warning', 'WordArrange', 'WriteFile', 'ZaIsActinide', 'Zeros', 'avogadrosNumber', 'epsilon', 'mocDownInputFile', 'xsDir', 'za2MolarMass'):
            variable = getattr(currentModule, variableName);
            setattr(module, variableName, variable);
###
# Convert isotope string -> ZAm
###
def Isotope2Zam(isotope):
    m = 'M' == isotope[-1];
    A = reNumber.search(isotope).group();
    Z = z2Element.index(isotope.rstrip('M').replace(A, '').strip().capitalize());
    ###
    return int(Z) * 10000 + int(A) * 10 + m;
###
# Reaction numbers of interest and the za's that cause them
# Based upon ENDF/B-VII.0, Low-fidelity covariance library
###
def IsZaReactionNumberOfInterest(za, reactionNumber):
    z, a = za // 1000, za % 1000;
    ###
    # (n, n) can be significant for any isotope
    ###
    if 2 == reactionNumber:
        return True;
    ###
    # (n, n') can be significant for any isotope, but does not exist for some
    ###
    if 4 == reactionNumber:
        return za not in (1001, 1002, 1003, 2003, 2004, 4007, 4009, 23000, 28059, 33074, 39090, 91231, 91233, 98253, 99253);
    ###
    # (n, 2n) can be significant for any isotope, but does not exist for some
    ###
    if 16 == reactionNumber:
        return za not in (1001, 2003, 2004, 3006, 4007, 5010, 6000, 98253, 99253);
    ###
    # (n, 3n) is assumed only significant for actinides, but does not exist for some
    ###
    if 17 == reactionNumber:
        return ZaIsActinide(za) and za not in (92234, 92236, 93237, 94238, 94240, 94241, 94242, 95241, 95242, 95243, 96242, 96243, 96244, 96245, 98253, 99253);
    ###
    # (n, fission) is assumed only significant for actinides, but does not exist for some
    ###
    if 18 == reactionNumber:
        return ZaIsActinide(za) and za not in (89225, 89226, 99253);
    ###
    # (n, \gamma) can be significant for any isotope, but does not exist for some
    ###
    if 102 == reactionNumber:
        return za not in (1003, 2004, 4007);
    ###
    # (n, p) is assumed only significant for fission products, but does not exist for some
    ###
    if 103 == reactionNumber:
        return z < 89 and za not in (1001, 1002, 1003, 2004, 3007, 4007);
    ###
    # (n, t) is significant below 14.1 MeV for these isotopes
    ###
    if 205 == reactionNumber:
        return za in (3006, 3007, 4009, 5011, 7014, 7015, 9019);
    ###
    # (n, a) is assumed only significant for actinides
    ###
    if 107 == reactionNumber:
        return ZaIsActinide(za);
    ###
    # MCNP's -6 is equivalent to MT = 18
    ###
    if -6 == reactionNumber:
        return IsZaReactionNumberOfInterest(za, 18);
    ###
    # 205 is a better MT than 105
    ###
    if 105 == reactionNumber:
        return IsZaReactionNumberOfInterest(za, 205);
    ###
    # Unaccounted-for reactions are assumed to be not of interest
    ###
    return False;
###
# Make directory
###
def MakeDirectory(directoryName, display = True):
    RemoveTree(directoryName, display = display);
    if display:
        PrintNow('{} ^^'.format(directoryName));
    LibMakeDirectory(directoryName);
    ###
    return;
###
# Make directory
###
def MakeTemporaryDirectory(display = True):
    directoryName = LibMakeTemporaryDirectory() + '/';
    if display:
        PrintNow('{} ^^'.format(directoryName));
    ###
    return directoryName;
###
# Move file
###
def MoveFile(pathOne, pathTwo, display = True):
    if display:
        PrintNow('{} -> {}'.format(pathOne, pathTwo));
    if Exists(pathOne):
        LibMoveFile(pathOne, pathTwo);
    ###
    return;
###
# Key for extracting numerics from strings
###
def NumericStringKey(string):
    output = [];
    for character in string:
        if character in '0123456789':
            digit = int(character);
            if output and isinstance(output[-1], int):
                output[-1] = output[-1] * 10 + digit;
            else:
                output.append(digit);
        else:
            output.append(character.lower());
    ###
    return output;
###
# Print now
###
def PrintNow(*arguments, sep = '\n'):
    print(*arguments, sep = sep);
    StdOut.flush();
    ###
    return;
###
# Q-fission of MCNP
###
def QFissionMCNP(ZA):
    za2Q = {
        90232 : 171.91,
        91233 : 175.57,
        92233 : 180.84,
        92234 : 179.45,
        92235 : 180.88,
        92236 : 179.50,
        92237 : 180.40,
        92238 : 181.31,
        92239 : 180.40,
        92240 : 180.40,
        93237 : 183.67,
        94238 : 186.65,
        94239 : 189.44,
        94240 : 186.36,
        94241 : 188.99,
        94242 : 185.98,
        94243 : 187.48,
        95241 : 190.83,
        95242 : 190.54,
        95243 : 190.25,
        96242 : 190.49,
        96244 : 190.49,
    };
    ###
    try:
        return za2Q[ZA];
    except KeyError:
        return 180;
###
# Q-fission of MONTEBURNS2
###
def QFissionMonteburns2(ZA):
    za2Q = {
        90227 : 0.9043,
        90229 : 0.9247,
        90232 : 0.9573,
        91231 : 0.9471,
        91233 : 0.9850,
        92232 : 0.9553,
        92233 : 0.9881,
        92234 : 0.9774,
        92235 : 1.0000,
        92236 : 0.9973,
        92237 : 1.0074,
        92238 : 1.0175,
        93237 : 1.0073,
        93238 : 1.0175,
        94238 : 1.0175,
        94239 : 1.0435,
        94240 : 1.0379,
        94241 : 1.0536,
        94242 : 1.0583,
        95241 : 1.0513,
        95242 : 1.0609,
        95243 : 1.0685,
        96242 : 1.0583,
        96243 : 1.0685,
        96244 : 1.0787,
        96245 : 1.0889,
        96246 : 1.0991,
        96248 : 1.1195,
        96249 : 1.1296,
        98251 : 1.1501,
        99254 : 1.1807,
    };
    try:
        multiplier = za2Q[ZA];
    except KeyError:
        multiplier = 1;
    ###
    return 200 * multiplier;
###
# Q-fission of ORIGEN2.2
###
def QFissionOrigen2(ZA):
    Z, A = ZA // 1000, ZA % 1000;
    return 1.29927E-03 * (Z ** 2. * A ** 0.5) + 33.12;
###
# Q-capture of ORIGENS
###
def QCaptureOrigenS(ZA):
    za2Q = {
         1001 : 2.225,
         5010 : 2.790,
         8016 : 4.143,
        26056 : 7.600,
        28058 : 9.020,
        40090 : 7.203,
        40091 : 8.635,
        40092 : 6.758,
        40096 : 5.571,
        42095 : 9.154,
        43095 : 7.710,
        44101 : 9.216,
        45103 : 6.999,
        45105 : 7.094,
        47109 : 6.825,
        54131 : 8.936,
        54135 : 7.880,
        55133 : 6.704,
        55134 : 6.550,
        60143 : 7.817,
        60145 : 7.565,
        61147 : 5.900,
        61148 : 7.266,
        62147 : 8.140,
        62149 : 7.982,
        62150 : 5.596,
        62151 : 8.258,
        62152 : 5.867,
        63153 : 6.444,
        63154 : 8.167,
        63155 : 6.490,
        90230 : 5.010,
        90232 : 4.786,
        90233 : 6.080,
        91231 : 5.660,
        91233 : 5.197,
        92232 : 5.930,
        92233 : 6.841,
        92234 : 5.297,
        92235 : 6.545,
        92236 : 5.124,
        92238 : 4.804,
        93237 : 5.490,
        93239 : 4.970,
        94238 : 5.550,
        94239 : 6.533,
        94240 : 5.241,
        94241 : 6.301,
        94242 : 5.071,
        94243 : 6.020,
        95241 : 5.529,
        95242 : 6.426,
        95243 : 5.363,
        96244 : 6.451,
        96245 : 6.110,
    };
    ###
    try:
        return za2Q[ZA];
    except KeyError:
        return 5;
###
# Q-fission of ORIGEN-S
###
def QFissionOrigenS(ZA):
    za2Q = {
        90230 : 190.00,
        90232 : 189.21,
        90233 : 190.00,
        91231 : 190.00,
        91233 : 189.10,
        92233 : 191.29,
        92234 : 190.30,
        92235 : 194.02,
        92236 : 192.80,
        92238 : 198.12,
        93237 : 195.10,
        94238 : 197.80,
        94239 : 200.05,
        94240 : 199.79,
        94241 : 202.22,
        94242 : 200.62,
        95241 : 202.30,
        95242 : 202.29,
        95243 : 202.10,
    };
    ###
    try:
        return za2Q[ZA];
    except KeyError:
        return 200;
###
# Read ascii file
###
def ReadFile(fileName, display = True, size = -1):
    try:
        AssertFileExists(fileName);
    except OSError:
        seconds = 3;
        if display:
            PrintNow('> File `{}\' does not exist ... waiting {:d} seconds and checking again ...'.format(fileName, seconds));
        Sleep(seconds);
        ###
        AssertFileExists(fileName);
    ###
    with open(fileName, 'rb') as f:
        if display:
            PrintNow('{} >>'.format(fileName));
        raw = f.read(size);
    ###
    return raw.decode('utf-8', 'ignore');
###
# Read xsdir from DATAPATH
###
def ReadXsDir(path = None, display = True):
    ###
    # 1) Use xsdir in current directory
    # 2) Use path provided by argument
    # 3) Use DATAPATH path defined in env
    ###
    paths = ['xsdir', path];
    ###
    try:
        from os import environ;
        ##
        paths.append('{}/xsdir'.format(environ['DATAPATH']).replace('//', '/'));
    except KeyError:
        pass;
    ###
    for path in paths:
        try:
            AssertFileExists(path);
            ###
            return ReadFile(path, display);
        except IOError:
            continue;
###
# Parse MCNP5, MCNP6, or MCNPX input/output file
###
def ReadTransportFile(fileName):
    raw = ReadFile(fileName, False, 4000);
    ###
    if bool(ReCompile(r'^1mcnp', 2 | 8).search(raw)):
        return McnpOutputFile(fileName);
    else:
        return McnpInputFile(fileName);
###
# Remove directory
###
def RemoveDirectory(directoryName, display = True):
    if Exists(directoryName):
        if display:
            PrintNow('{} XX'.format(directoryName));
        LibRemoveDirectory(directoryName);
    ###
    return;
###
# Remove directory tree
###
def RemoveTree(directoryName, display = True):
    if Exists(directoryName):
        if display:
            PrintNow('{}* XX'.format(directoryName));
        LibRemoveTree(directoryName);
    ###
    return;
###
# Remove file
###
def RemoveFile(fileName, display = True):
    if Exists(fileName):
        if display:
            PrintNow('{} XX'.format(fileName));
        LibRemoveFile(fileName);
    ###
    return;
###
# Safely divide two quantities
###
def SafeDivide(numerator, denominator):
    try:
        return numerator / denominator;
    except ZeroDivisionError:
        return 0.;
###
# Determine the slope of a set of points using a simple linear regression
###
def Slope(points):
    return SafeDivide(sum(point.GetX() * point.GetY() for point in points) - SafeDivide(sum(point.GetX() for point in points), len(points)) * sum(point.GetY() for point in points), sum(point.GetX() ** 2 for point in points) - SafeDivide(sum(point.GetX() for point in points) ** 2, len(points)));
###
# Symbolically link files
###
def SymbolicLink(pathOne, pathTwo, display = True):
    AssertFileExists(pathOne);
    RemoveFile(pathTwo, display);
    if display:
        PrintNow('{} -> {}'.format(pathTwo, pathOne));
    LibSymbolicLink(pathOne, pathTwo);
    ###
    return;
###
# Find a unique integer, given a number of digits and container of forbidden integers
###
def UniqueDigits(numberOfDigits, forbiddenNumbers):
    while True:
        output = RandomInteger(0, 10 ** numberOfDigits - 1);
        if output not in forbiddenNumbers:
            return output;
###
# Arrange words of a given format within columns
###
def WordArrange(words, format = '', columnNumber = 80, prefix = '', indent = 5):
    output = '';
    if '{' not in format:
        format = '{{{}}}'.format(format);
    line = [prefix];
    for word in words:
        word = format.format(word);
        if len(line) + len(word) + sum(len(element) for element in line) > columnNumber:
            output += '\n' * bool(output) + ' '.join(line);
            line = [' ' * (indent - 1)];
        line.append(word);
    output += '\n' * bool(output) + ' '.join(line);
    return output;
###
# Display warning messages
###
def Warning(warningMessage):
    PrintNow('Warning:\t{}'.format('\n\t\t'.join(warningMessage.split('\n'))));
    return;
###
# Write .csv file
###
def WriteCsvFile(fileName, *iterables):
    with open(fileName, 'w') as f:
        PrintNow('{} <<'.format(fileName));
        writer = CsvWriter(f, lineterminator = '\n');
        for iterable in iterables:
            writer.writerows(iterable);
    ###
    return;
###
# Write ascii file
###
def WriteFile(fileName, raw, display = True):
    with open(fileName, 'w') as f:
        if display:
            PrintNow('{} <<'.format(fileName));
        f.write(raw);
    ###
    return;
###
# Z # --> Element
###
z2Element = ['n', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Uut', 'Fl', 'Uup', 'Lv', 'Uus', 'Uuo'];
###
# ZA # --> Elemental natural abundance (http://www.nist.gov/pml/data/comp.cfm)
###
za2Abundance = {
    1001 : 0.999885, 1002 : 0.000115, 2003 : 0.00000134, 2004 : 0.99999866, 3006 : 0.0759, 3007 : 0.9241, 4009 : 1., 5010 : 0.199, 5011 : 0.801, 6012 : 0.9893,
    6013 : 0.0107, 7014 : 0.99636, 7015 : 0.00364, 8016 : 0.99757, 8017 : 0.00038, 8018 : 0.00205, 9019 : 1., 10020 : 0.9048, 10021 : 0.0027, 10022 : 0.0925,
    11023 : 1., 12024 : 0.7899, 12025 : 0.1, 12026 : 0.1101, 13027 : 1., 14028 : 0.92223, 14029 : 0.04685, 14030 : 0.03092, 15031 : 1., 16032 : 0.9499,
    16033 : 0.0075, 16034 : 0.0425, 16036 : 0.0001, 17035 : 0.7576, 17037 : 0.2424, 18036 : 0.003365, 18038 : 0.000632, 18040 : 0.996003, 19039 : 0.932581,
    19040 : 0.000117, 19041 : 0.067302, 20040 : 0.96941, 20042 : 0.00647, 20043 : 0.00135, 20044 : 0.02086, 20046 : 0.00004, 20048 : 0.00187, 21045 : 1.,
    22046 : 0.0825, 22047 : 0.0744, 22048 : 0.7372, 22049 : 0.0541, 22050 : 0.0518, 23050 : 0.0025, 23051 : 0.9975, 24050 : 0.04345, 24052 : 0.83789,
    24053 : 0.09501, 24054 : 0.02365, 25055 : 1., 26054 : 0.05845, 26056 : 0.91754, 26057 : 0.02119, 26058 : 0.00282, 27059 : 1., 28058 : 0.680769,
    28060 : 0.262231, 28061 : 0.011399, 28062 : 0.036345, 28064 : 0.009256, 29063 : 0.6915, 29065 : 0.3085, 30064 : 0.48268, 30066 : 0.27975, 30067 : 0.04102,
    30068 : 0.19024, 30070 : 0.00631, 31069 : 0.60108, 31071 : 0.39892, 32070 : 0.2038, 32072 : 0.2731, 32073 : 0.0776, 32074 : 0.3672, 32076 : 0.0783,
    33075 : 1., 34074 : 0.0089, 34076 : 0.0937, 34077 : 0.0763, 34078 : 0.2377, 34080 : 0.4961, 34082 : 0.0873, 35079 : 0.5069, 35081 : 0.4931, 36078 : 0.00355,
    36080 : 0.02286, 36082 : 0.11593, 36083 : 0.115, 36084 : 0.56987, 36086 : 0.17279, 37085 : 0.7217, 37087 : 0.2783, 38084 : 0.0056, 38086 : 0.0986,
    38087 : 0.07, 38088 : 0.8258, 39089 : 1., 40090 : 0.5145, 40091 : 0.1122, 40092 : 0.1715, 40094 : 0.1738, 40096 : 0.028, 41093 : 1., 42092 : 0.1477,
    42094 : 0.0923, 42095 : 0.159, 42096 : 0.1668, 42097 : 0.0956, 42098 : 0.2419, 42100 : 0.0967, 44096 : 0.0554, 44098 : 0.0187, 44099 : 0.1276,
    44100 : 0.126, 44101 : 0.1706, 44102 : 0.3155, 44104 : 0.1862, 45103 : 1., 46102 : 0.0102, 46104 : 0.1114, 46105 : 0.2233, 46106 : 0.2733, 46108 : 0.2646,
    46110 : 0.1172, 47107 : 0.51839, 47109 : 0.48161, 48106 : 0.0125, 48108 : 0.0089, 48110 : 0.1249, 48111 : 0.128, 48112 : 0.2413, 48113 : 0.1222,
    48114 : 0.2873, 48116 : 0.0749, 49113 : 0.0429, 49115 : 0.9571, 50112 : 0.0097, 50114 : 0.0066, 50115 : 0.0034, 50116 : 0.1454, 50117 : 0.0768,
    50118 : 0.2422, 50119 : 0.0859, 50120 : 0.3258, 50122 : 0.0463, 50124 : 0.0579, 51121 : 0.5721, 51123 : 0.4279, 52120 : 0.0009, 52122 : 0.0255,
    52123 : 0.0089, 52124 : 0.0474, 52125 : 0.0707, 52126 : 0.1884, 52128 : 0.3174, 52130 : 0.3408, 53127 : 1., 54124 : 0.000952, 54126 : 0.00089,
    54128 : 0.019102, 54129 : 0.264006, 54130 : 0.04071, 54131 : 0.212324, 54132 : 0.269086, 54134 : 0.104357, 54136 : 0.088573, 55133 : 1., 56130 : 0.00106,
    56132 : 0.00101, 56134 : 0.02417, 56135 : 0.06592, 56136 : 0.07854, 56137 : 0.11232, 56138 : 0.71698, 57138 : 0.0009, 57139 : 0.9991, 58136 : 0.00185,
    58138 : 0.00251, 58140 : 0.8845, 58142 : 0.11114, 59141 : 1., 60142 : 0.272, 60143 : 0.122, 60144 : 0.238, 60145 : 0.083, 60146 : 0.172, 60148 : 0.057,
    60150 : 0.056, 62144 : 0.0307, 62147 : 0.1499, 62148 : 0.1124, 62149 : 0.1382, 62150 : 0.0738, 62152 : 0.2675, 62154 : 0.2275, 63151 : 0.4781,
    63153 : 0.5219, 64152 : 0.002, 64154 : 0.0218, 64155 : 0.148, 64156 : 0.2047, 64157 : 0.1565, 64158 : 0.2484, 64160 : 0.2186, 65159 : 1., 66156 : 0.00056,
    66158 : 0.00095, 66160 : 0.02329, 66161 : 0.18889, 66162 : 0.25475, 66163 : 0.24896, 66164 : 0.2826, 67165 : 1., 68162 : 0.00139, 68164 : 0.01601,
    68166 : 0.33503, 68167 : 0.22869, 68168 : 0.26978, 68170 : 0.1491, 69169 : 1., 70168 : 0.0013, 70170 : 0.0304, 70171 : 0.1428, 70172 : 0.2183,
    70173 : 0.1613, 70174 : 0.3183, 70176 : 0.1276, 71175 : 0.9741, 71176 : 0.0259, 72174 : 0.0016, 72176 : 0.0526, 72177 : 0.186, 72178 : 0.2728,
    72179 : 0.1362, 72180 : 0.3508, 73180 : 0.00012, 73181 : 0.99988, 74180 : 0.0012, 74182 : 0.265, 74183 : 0.1431, 74184 : 0.3064, 74186 : 0.2843,
    75185 : 0.374, 75187 : 0.626, 76184 : 0.0002, 76186 : 0.0159, 76187 : 0.0196, 76188 : 0.1324, 76189 : 0.1615, 76190 : 0.2626, 76192 : 0.4078,
    77191 : 0.373, 77193 : 0.627, 78190 : 0.00014, 78192 : 0.00782, 78194 : 0.32967, 78195 : 0.33832, 78196 : 0.25242, 78198 : 0.07163, 79197 : 1.,
    80196 : 0.0015, 80198 : 0.0997, 80199 : 0.1687, 80200 : 0.231, 80201 : 0.1318, 80202 : 0.2986, 80204 : 0.0687, 81203 : 0.2952, 81205 : 0.7048,
    82204 : 0.014, 82206 : 0.241, 82207 : 0.221, 82208 : 0.524, 83209 : 1., 90232 : 1., 91231 : 1., 92234 : 0.000054, 92235 : 0.007204, 92238 : 0.992742
    };
###
# Convert ZA -> isotope string
###
def Za2Isotope(za, texFormat = False):
    za = int(float(za));
    ###
    z, a = za // 1000, za % 1000;
    ###
    if texFormat:
        return '^{{{}}}{}'.format(a, z2Element[z]);
    ###
    return '{}-{}'.format(z2Element[z], a);
###
# Extract molar mass for a given Z,A from xsdir
###
def Za2MolarMass(xsDir):
    words = xsDir.split();
    words = words[words.index('atomic') + 3 : words.index('directory') - 1];
    return {int(float(words[index])) : float(words[index + 1]) * neutronMass for index in range(0, len(words) - 1, 2)};
###
# Convert ZA -> ZAm
###
def Za2Zam(za):
    ###
    # Change natural carbon to carbon-12
    ###
    za += (za == 6000) * 12;
    ###
    # Determine Z, A, and m
    ###
    Z, A = za // 1000, za % 1000;
    ###
    # Switch Am-242 and Am-242m
    ###
    if 95242 == za:
        return 952421;
    elif 95642 == za:
        return 952420;
    ###
    # Decrement A according to metastable
    ###
    m = (A > 300) * (A - 2 * Z - 300) // 100;
    A -= (A > 300) * (300 + m * 100);
    ###
    return Z * 10000 + A * 10 + m;
###
# Is za an actinide
###
def ZaIsActinide(za):
    return za // 1000 > 88;
###
# Extract temperature ID from ZAID
###
def Zaid2Id(zaid):
    return zaid.split('.')[1];
###
# Convert a zaid string into an isotope string
###
def Zaid2Isotope(zaid, texFormat = False):
    return Za2Isotope(Zaid2Za(zaid));
###
# Extract molar mass for a given ZAID from xsdir
###
def Zaid2MolarMass(zaid):
    try:
        return za2MolarMass[Zaid2Za(zaid)];
    except KeyError:
        return Zaid2Zam(zaid) // 10 % 1000;
###
# Extract temperature for a given ZAID from xsdir
###
def Zaid2Temperature(xsDir):
    lines = xsDir.split('\n');
    ###
    # Find directory line index
    ###
    for index in range(len(lines)):
        if 'directory' in lines[index]:
            directoryIndex = index;
    ###
    # Filter out zaids
    ###
    zaidLines = (' '.join(word for word in line.split() if 'ptable' != word) for line in lines[directoryIndex + 1 : ] if line);
    ###
    # Build zaid --> temperature mapping
    ###
    zaid2Temperature = {zaidLine.split()[0] : zaidLine.split()[-1] for zaidLine in zaidLines};
    ###
    return {zaid : float(temperature) for (zaid, temperature) in zaid2Temperature.items() if any(character in zaid.lower() for character in 'cm')};
###
# Convert ZAID -> ZA
###
def Zaid2Za(zaid):
    return int(float(str(zaid).split('.')[0]));
###
# Convert ZAID -> ZAm
###
def Zaid2Zam(zaid):
    return Za2Zam(Zaid2Za(zaid));
###
# Convert ZAm -> ZA
###
def Zam2Za(zam):
    return zam // 10;
###
# Convert ZAm -> ZAID
###
def Zam2Zaid(zam, suffix):
    za, m = zam // 10, zam % 10;
    ###
    # Change carbon-12 to natural carbon
    ###
    za -= (za == 6012) * 12;
    ###
    # Switch Am-242m and Am-242
    ###
    if (95242, 1) == (za, m):
        return '95242.{}'.format(suffix);
    elif (95242, 0) == (za, m):
        return '95642.{}'.format(suffix);
    ###
    # Increment A according to metastable
    ###
    za += (m > 0) * (300 + 100 * m);
    ###
    return '{:d}.{}'.format(za, suffix);

###
### Script
###

###
# Initiate argument parser and add custom arguments
###
def InterpretArguments():
    ###
    # Script name
    ###
    script = __file__.split('/')[-1].replace('.py', '');
    script2Description = {
        'MocDown'   : 'MOCUP/MONTEBURNS rewritten in Python.  Compatible with MCNP5, MCNP6, MCNPX, and ORIGEN2.2.',
        'ParseMcnp' : 'Script for parsing MCNP5, MCNP6, and MCNPX input and output files.',
    };
    ###
    assert(script in script2Description);
    ###
    parser = ArgumentParser(description = script2Description[script], epilog = 'Version {} | {} {}'.format(__version__, __author__, __year__));
    parser.add_argument('--version', action = 'version', version = '%(prog)s {} | {} {}'.format(__version__, __author__, __year__));
    ###
    action = 'store_true';
    nargs = '?';
    ###
    # Transport file argument
    ###
    parser.add_argument('transportFileName', nargs = nargs, default = 'inp1', help = 'MCNP input file (=inp1 by default)');
    ###
    # MocDown input file argument
    ###
    parser.add_argument('mocDownInputFileName', nargs = nargs, default = 'mocdown.inp', help = 'MocDown input file (= mocdown.inp by default)');
    ###
    # Optional arguments
    ###
    parser.add_argument('--isVerbose', '-v', action = action, help = 'Verbose operation');
    parser.add_argument('--isQuiet', '-q', action = action, help = 'Hide file operation messages');
    ###
    if script == 'MocDown':
        ###
        # MocDown arguments
        ###
        parser.add_argument('--isRestart', '-r', action = action, help = 'Restart depletion from last pickle');
    elif script == 'ParseMcnp':
        ###
        # MCNP input | parsing stdout reports
        ###
        parser.add_argument('--reportCells', '--cel', action = action, help = 'Report problem cell summary');
        parser.add_argument('--reportIsotopes', '--iso', action = action, help = 'Report problem isotope summary');
        parser.add_argument('--reportTallys', '--tal', '--reportFulfilled', '--ful', action = action, help = 'Report problem tally summary');
        parser.add_argument('--reportKeff', '--keff', action = action, help = 'Report problem keff summary');
        ###
        # MCNP output | physical quantity .csv reports
        ###
        choices = ('lethargy', 'leth', 'ebin', 'bin', 'energy', 'mev', 'normalied', 'norm', 'uncertainty', 'std');
        parser.add_argument('--writeEnergyDepositions', '--edep', nargs = nargs, const = choices[0], choices = choices, help = 'Write energy depositions .csv');
        parser.add_argument('--writeFissionEnergyDepositions', '--fedep', nargs = nargs, const = choices[0], choices = choices, help = 'Write fission energy depositions .csv');
        parser.add_argument('--writeMicroscopicCrosssections', '--micro', nargs = nargs, const = choices[0], choices = choices, help = 'Write microscopic cross sections .csv');
        parser.add_argument('--writeReactionRates', '--rxn', nargs = nargs, const = choices[0], choices = choices, help = 'Write reaction rates .csv');
        parser.add_argument('--writeScalarFluxes', '--flx', nargs = nargs, const = choices[0], choices = choices, help = 'Write scalar fluxes .csv');
        ###
        # MCNP output | result down-sampling
        ###
        choices = list(range(1, 16, +1));
        choices.extend(range(0, -16, -1));
        parser.add_argument('--downSample', '--dwn', nargs = nargs, const = choices[0], choices = choices, type = int, help = 'Down-sample results by a factor of 2 ** n.  If n is negative, results will be averaged instead of summed.');
    ###
    arguments = parser.parse_args();
    arguments.script = script;
    ###
    return arguments;
###
# Main()
###
if __name__ == '__main__':
    ###
    # Interpret arguments
    ###
    arguments = InterpretArguments();
    ###
    # Parse MocDown input file
    ###
    mocDownInputFile = MocDownInputFile(arguments);
    ###
    # Parse xsdir
    ###
    xsDir = ReadXsDir(path = mocDownInputFile.GetParameter('mcnpXsdirPath'), display = not bool(arguments.isQuiet));
    za2MolarMass = Za2MolarMass(xsDir);
    ###
    # Import supplementary MocDown library and overwrite DepletionCalculation methods
    ###
    if len(mocDownInputFile.GetParameter('supplementaryMocdownLibrary')):
        ImportLibraries(mocDownInputFile.GetParameter('supplementaryMocdownLibrary'));
    ###
    if arguments.script == 'MocDown':
        ###
        if mocDownInputFile.GetParameter('recycleToEquilibrium'):
            ###
            # Run accelerated depletion/recycle calculation
            ###
            recycleCalculation = RecycleCalculation(arguments);
        else:
            ###
            # Run simple depletion calculation
            ###
            depletionCalculation = DepletionCalculation(arguments);
    elif arguments.script == 'ParseMcnp':
        ###
        zaid2Temperature = Zaid2Temperature(xsDir);
        ###
        # Parse transport file
        ###
        mcnpFile = ReadTransportFile(arguments.transportFileName);
        ###
        # Execute desired reports
        ###
        mcnpFile.Report(arguments);
else:
    ###
    # Empty arguments
    ###
    arguments = Class();
    arguments.isQuiet = arguments.isVerbose = False;
    ###
    # Empty MocDown input file
    ###
    mocDownInputFile = MocDownInputFile(arguments);
    ###
    # Parse xsdir
    ###
    xsDir = ReadXsDir(display = not bool(arguments.isQuiet));
    za2MolarMass = Za2MolarMass(xsDir);
