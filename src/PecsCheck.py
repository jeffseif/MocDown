#! /usr/bin/env python3

###
### Imports
###

from MocDown import * ;
arguments.isQuiet = True;

###
### Classes
###

###
# 
###
class PECSDepletion(DepletionCalculation):
    '''PECS-syle replacement for DepletionCalculation.''';
    def __init__(self, originalTransportFile, depletionCalculationPickle, recycleIndex):
        '''Construct a new instance.''';
        ###
        # Grab transport file
        ###
        self.originalTransportFile = originalTransportFile;
        ###
        # Prepare depletion
        ###
        self.PrepareDepletion(depletionCalculationPickle);
        ###
        # Recycle index
        ###
        self.recycleIndex = recycleIndex;
        ###
        # Deplete
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
        '''Return number of depletion steps.''';
        return len(self.GetParameter('depletionStepTimeIntervals'));
    ###
    # Generic getter methods
    ###
    def GetCellNumberBurnRate(self, cellNumber):
        '''Return cell flux or power for current depletion step.''';
        return self.cellNumber2OrigenPowers[cellNumber][self.GetDepletionStep()];
    ###
    def GetCellNumber2Micros(self):
        '''Return dictionary mapping cell to one-group microscopic cross-sections for current depletion step.''';
        return {cellNumber : micros[self.GetDepletionStep()] for cellNumber, micros in self.cellNumber2Micros.items()};
    ###
    def GetCellNumberMicros(self, cellNumber):
        '''Return one-group microscopic cross-sections of a cell for this depletion step.''';
        return self.GetCellNumber2Micros()[cellNumber];
    ###
    def GetCellNumberVolume(self, cellNumber):
        '''Return volume of a cell.''';
        return self.cellNumber2Volume[cellNumber];
    ###
    def GetCellNumber2Zam2Moles(self):
        '''Return dictionary mapping cell to isotope to moles for current depletion step.''';
        return {cellNumber : zam2Moles[self.GetDepletionStep()] for cellNumber, zam2Moles in self.cellNumber2Zam2Moles.items()};
    ###
    def GetCellNumberZam2Moles(self, cellNumber):
        '''Return dictionary mapping isotope to moles of a cell for this depletion step.''';
        try:
            ###
            # If TAPE7.OUT exists from a previous ORIGEN calculation,
            # grab zam2Moles from there
            ###
            return {Zaid2Zam(zaid) : moles for zaid, moles in self.GetCellNumber2OrigenCalculation()[cellNumber].GetZaid2Moles().items()};
        except (KeyError, TypeError):
            ###
            # No ORIGEN calculation is performed either for this depletion step, or for this cell
            ###
            return self.cellNumber2Zam2Moles[cellNumber][self.GetDepletionStep()];
    ###
    def GetDefaultPhotonLibraryFileName(self):
        '''Return ORIGEN2 default photon library filename.''';
        return self.GetParameter('origenLibraryPathTemplate').format(self.GetParameter('defaultPhotonLibrary'));
    ###
    def GetDisplayFiles(self):
        '''Return if file operations are verbose.''';
        return not arguments.isQuiet;
    ###
    def GetIsPickleTransmute(self):
        '''Return if current depletion step is to be transmuted using pickles.''';
        return True;
    ###
    def GetParameters(self):
        '''Return mocdown input file parameters.''';
        return self.parameters;
    ###
    def GetPickle(self):
        '''Return depletion calculation pickle.''';
        return self.depletionCalculationPickle;
    ###
    def GetPickleFileName(self):
        '''Return depletion calculation pickle filename.''';
        return self.pickleFileName;
    ###
    def GetRecycleIndex(self):
        '''Return index of current recycling step.''';
        return self.recycleIndex;
    ###
    # Depletion methods
    ###
    def Deplete(self):
        '''Execute PECS-style depletion.''';
        ###
        # Iterate over depletion steps
        ###
        while self.GetDepletionStep() < len(self):
            ###
            # Transmute calculation
            ###
            self.TransmuteThreads(GetCurrentWorkingDirectory() + '/');
            ###
            # Pickle depletion object
            ###
            self.PickleDepletionStep(self.GetOriginalTransportFile());
            ###
            # Increment depletion step
            ###
            self.IncrementDepletionStep();
        ###
        # Pickle depletion object -- post-transmute
        ###
        self.PickleDepletionStep(self.GetOriginalTransportFile());
        ###
        PrintNow('> {} has completed all {} depletion step(s)'.format(__file__, len(self)));
        ###
        return;
    ###
    def PrepareDepletion(self, depletionCalculationPickle):
        '''Populate default PECS-style depletion parameters.''';
        ###
        # Set depletion step
        ###
        self.depletionStep = 0;
        ###
        # Set coolant density / fuel temperature calculations
        ###
        self.coolantDensityCalculations = self.previousCoolantDensityCalculations = self.fuelTemperatureCalculations = self.previousFuelTemperatureCalculations = None;
        ###
        # Set DS -> pickle
        ###
        self.depletionStep2DepletionStepPickle = {};
        ###
        # Define MT #'s for each ORIGEN library group (1 = Activation products, 2 = Actinides, and 3 = Fission Products)
        ###
        self.origen2Lib2Mts = {
            1 : (102, 16, 107, 103),
            2 : (102, 16, 17, 18),
            3 : (102, 16, 107, 103),
        };
        ###
        # Parameters
        ###
        self.parameters = depletionCalculationPickle.parameters;
        ###
        # Read default decay, photon, and cross-section libraries
        ###
        for defaultLibrary in ('defaultDecayLibrary', 'defaultPhotonLibrary', 'defaultXsLibrary'):
            setattr(self, defaultLibrary, ReadFile(self.GetParameter('origenLibraryPathTemplate').format(self.GetParameter(defaultLibrary)), display = self.GetDisplayFiles()));
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
        # Grab transmutation constants from pickle
        ###
        for attribute in ('cellNumber2Micros', 'cellNumber2OrigenPowers', 'cellNumber2Volume', 'powerCells'):
            setattr(self, attribute, getattr(depletionCalculationPickle, attribute));
        self.cellNumber2Zam2Moles = {cellNumber : zam2Moles[ : 1] for cellNumber, zam2Moles in depletionCalculationPickle.cellNumber2Zam2Moles.items()};
        ###
        # Maybe remove transport and trasmute log files
        ###
        for logFileName in ('transport.log', 'transmute.log'):
            RemoveFile(logFileName, display = self.GetDisplayFiles());
        ###
        # Set transmutation results to None
        ###
        self.cellNumber2OrigenCalculation = None;
        ###
        return;
    ###
    def TransmuteThreads(self, currentDir):
        '''Execute transmute concurrently for each cell.''';
        PrintNow('> Executing {:d} concurrent ORIGEN thread(s) for {}'.format(self.GetParameter('numberOfOrigenThreads'), self.GetDepletionString()));
        ###
        # Multiple concurrent ORIGEN threads for each burn cell
        ###
        self.cellNumber2BurnRate = {};
        ###
        thread = 0;
        threads = len(self.GetBurnCells());
        with Futures.ThreadPoolExecutor(max_workers = self.GetParameter('numberOfOrigenThreads')) as executor:
            future2CellNumber = {executor.submit(self.TransmuteThread, cellNumber, currentDir) : cellNumber for cellNumber in self.GetBurnCells()};
            ###
            for future in Futures.as_completed(future2CellNumber):
                if future.exception() is not None:
                    raise(future.exception());
                else:
                    thread += 1;
                    PrintNow('> Completed burning cell #{:d} (thread {:d} of {:d})'.format(future2CellNumber[future], thread, threads));
        ###
        # Extract and attach cell # -> Origen calculation, ZAm -> moles
        ###
        cellNumber2Transmute = {cellNumber : future.result() for future, cellNumber in future2CellNumber.items()};
        self.cellNumber2OrigenCalculation, = [{cellNumber : transmute[index] for cellNumber, transmute in cellNumber2Transmute.items()} for index in range(1)];
        for cellNumber, zam2Moles in self.cellNumber2Zam2Moles.items():
            zam2Moles.append({Zaid2Zam(zaid) : moles for zaid, moles in self.GetCellNumber2OrigenCalculation()[cellNumber].GetZaid2Moles().items()});
        ###
        return;
    ###
    def TransmuteThread(self, cellNumber, currentDir):
        '''Execute transmute concurrently for a cell.''';
        ###
        # Move to temporary directory
        ###
        tmpDir = MakeTemporaryDirectory(display = self.GetDisplayFiles());
        ###
        # Write transmutation inputs;
        ###
        micros = self.PrepareTransmute(cellNumber, tmpDir);
        ###
        # Run transmutation calculation;
        # Parse transport results
        ###
        origenCalculation = self.Transmute(cellNumber, tmpDir, currentDir);
        ###
        # Attach micros to origenCalculation
        ###
        origenCalculation.AttachMicros(micros);
        ###
        # Clean up files
        ###
        self.CleanUpFiles(tmpDir);
        ###
        return origenCalculation, ;
    ###
    def PrepareTransmute(self, cellNumber, tmpDir = './'):
        '''Prepare transmute calculation.''';
        PrintNow('> Writing transmute input for cell #{:d}'.format(cellNumber));
        ###
        # origen (ORIGEN executable)
        ###
        SymbolicLink(self.GetParameter('origenExecutablePath'), '{}origen'.format(tmpDir), display = self.GetDisplayFiles());
        ###
        # TAPE10.INP (default photon library):
        ###
        SymbolicLink(self.GetDefaultPhotonLibraryFileName(), '{}TAPE10.INP'.format(tmpDir), display = self.GetDisplayFiles());
        ###
        # TAPE4.INP (.pch punch card):
        # Cell moles
        ###
        zam2Moles = self.GetCellNumberZam2Moles(cellNumber);
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
            ###
            def HelperMicros(zam, micros, mts, excites):
                ###
                multipliers = [excite for excite in excites] + [1 - excite for excite in excites] + [1] * 2;
                ###
                return [multipliers[index] * micros[(zam, mts[index])] for index in range(-4, 2)];
            ###
            micros = self.GetCellNumberMicros(cellNumber);
            ###
            cellZams = set(zam for zam, reactionNumber in micros);
            ###
            reXs = ReCompile(r'^ *(\d+) +(\d+)');
            xsLibraryLines = [];
            for line in self.GetDefaultXsLibrary().split('\n'):
                try:
                    lib, zam = reXs.search(line).groups();
                    ###
                    zam = int(float(zam));
                    if zam in cellZams:
                        lib = int(float(lib));
                        mts = self.GetOrigen2LibMts(lib);
                        ###
                        line = origenXsLibraryTemplate.format(lib = lib, zam = zam, sigma = HelperMicros(zam, micros, mts, self.GetLibZamExcite(lib, zam)));
                except AttributeError:
                    pass;
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
        xsLibs = sorted(self.GetLib2Zams().keys());
        ###
        burnMode = 'IRP';
        if self.GetIsDecayStep():
            ###
            # Decay cell
            ###
            cellBurnRate = 0;
        else:
            ###
            # Burn cell
            ###
            cellBurnRate = self.GetCellNumberBurnRate(cellNumber);
        ###
        timeLapse = self.GetDepletionStepTimeInterval();
        timeSteps = len([line for line in origenInputFileTemplate.split('\n') if 'timeEnds' in line]);
        timeEnds = [timeLapse * (index + 1) / timeSteps for index in range(timeSteps)];
        ###
        WriteFile('{}TAPE5.INP'.format(tmpDir), origenInputFileTemplate.format(xsLibs = xsLibs, burnMode = burnMode, timeEnds = timeEnds, cellBurnRate = cellBurnRate), display = self.GetDisplayFiles());
        ###
        self.cellNumber2BurnRate[cellNumber] = cellBurnRate;
        ###
        return micros;
    ###
    def Transmute(self, cellNumber, tmpDir = './', currentDir = ''):
        '''Execute ORIGEN2.''';
        PrintNow('> Burning cell #{:d} at {:10.5E} {:s} in `{:s}\''.format(cellNumber, self.GetCellNumberBurnRate(cellNumber), self.GetParameter('burnUnits'), tmpDir));
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
        return OrigenCalculation('72c', self.GetCellNumberVolume(cellNumber), tmpDir);
###
#
###
class PECSCalculation(RecycleCalculation):
    '''PECS-syle replacement for RecycleCalculation.''';
    def __init__(self, arguments):
        '''Construct a new instance.''';
        ###
        # Populate
        ###
        self.Populate(arguments);
        ###
        # Equilibrate
        #
        self.Equilibrate();
        ###
        return;
    ###
    # Generic getter methods
    ###
    def GetBaseName(self):
        '''Return base of MCNP input filename.''';
        return self.baseName;
    ###
    def GetDisplayFiles(self):
        '''Return if file operations are verbose.''';
        return not arguments.isQuiet;
    ###
    def GetIsPickleTransmute(self):
        '''PECS-style calculations only transmute!.''';
        return True;
    ###
    def GetOriginalPickle(self):
        '''Return initial pickle.''';
        return self.originalPickle;
    ###
    def GetOriginalTransport(self):
        '''Return initial MCNP input file.''';
        return self.originalTransportFile;
    ###
    def GetRecycleString(self):
        '''Return string for current PECS-style recycling step.''';
        return 'PECS transmute-only recycle #{:d}'.format(self.GetRecycleIndex());
    ###
    # Population methods
    ###
    def Populate(self, arguments):
        '''Populate.''';
        ###
        # Base name
        ###
        self.baseName = arguments.transportFileName;
        ###
        # Parse transport file
        ###
        self.originalTransportFile = ReadTransportFile(arguments.transportFileName);
        ###
        # Parse depletion calculation pickle
        ###
        self.originalPickle = DepletionCalculationPickle(arguments.pickleFileName);
        ###
        # Parameters
        ###
        self.parameters = self.GetOriginalPickle().parameters;
        ###
        self.recycleIndex = 0;
        ###
        return;
    ###
    # PECS methods
    ###
    def Equilibrate(self):
        '''Execute PECS-style recycling.''';
        PrintNow('> {} will recycle to equilibrium'.format(__file__));
        ###
        pickle = self.GetOriginalPickle();
        ###
        isConverged = False;
        ###
        # Iterate until isotopics have converged
        ###
        while not isConverged:
            ###
            # Prepare depletion calculation
            ###
            self.PrepareRecycle(None);
            ###
            # Run depletion calculation
            ###
            PrintNow('> Depleting {}'.format(self.GetRecycleString()));
            depletionCalculation = PECSDepletion(self.GetOriginalTransport(), pickle, self.GetRecycleIndex());
            ###
            # Save previous pickle for isotopics convergence
            ###
            previousPickle = pickle;
            ###
            # Extract processed transport input raw for isotopics convergence
            ###
            pickle = depletionCalculation.ProcessFuel(previousPickle);
            ###
            # Archive depletion calculation recycle
            ###
            self.ArchiveRecycle();
            ###
            # Only check for convergence following the first recycle
            ###
            if bool(self.GetRecycleIndex()):
                ###
                # Determine if BOEC isotopics have converged;
                # If so, kick out after one last transport/transmute recycle;
                # If not, continue transmute-only recycles
                ###
                isConverged = self.IsotopicsHaveConverged(previousPickle, pickle);
            ###
            # Increment recycle index
            ###
            self.IncrementRecycleIndex();
        ###
        # Final pickle
        ###
        pickle.Save(baseName = self.GetBaseName(), display = self.GetDisplayFiles());
        ###
        return;

###
### Functions
###

###
# DepletionCalculationPickle.__sub__()
###
DepletionCalculationPickle.__sub__ = McnpInputFile.__sub__;
###
# DepletionCalculationPickle.GetZa2Moles()
###
def GetZa2Moles(self, cellNumbers = None, endOfCycle = False):
    '''Override dicionary mapping isotope to moles.''';
    cellNumber2Zam2Moles = self.cellNumber2Zam2Moles;
    ###
    if cellNumbers is None:
        cellNumbers = cellNumber2Zam2Moles.keys();
    ###
    za2Moles = {};
    ###
    for cellNumber, zam2Moles in cellNumber2Zam2Moles.items():
        ###
        # Kick out cell #'s which are not requested
        ###
        if cellNumber not in cellNumbers:
            continue;
        ###
        zam2Mole = [zam2Mole for zam2Mole in zam2Moles if zam2Mole][0 - endOfCycle];
        ###
        for zam, moles in zam2Mole.items():
            try:
                za2Moles[Zam2Za(zam)] += moles;
            except KeyError:
                za2Moles[Zam2Za(zam)] = moles;
    ###
    return za2Moles;
###
DepletionCalculationPickle.GetZa2Moles = GetZa2Moles;
###
# PECSDepletion.ProcessFuel()
###
def ProcessFuel(self, previousPickle):
    '''Override fuel processing.''';
    ###
    # Hard code the blanket and seed cell parameters
    ###
    if False:
        lowerBlanketCellNumbers = list(range(1001, 1001 + 10));
        seedCellNumbers =         list(range(1011, 1011 + 30));
        upperBlanketCellNumbers = list(range(1041, 1041 + 15));
    elif True:
        lowerBlanketCellNumbers = [2000];
        seedCellNumbers = [1000];
        upperBlanketCellNumbers = [];
    else:
        lowerBlanketCellNumbers = [2000, 2001];
        seedCellNumbers = [1000, 1001];
        upperBlanketCellNumbers = [];
    ###
    numberOfSeedCells = len(seedCellNumbers);
    ###
    # Isotopic ZA strings
    ###
    thorium = 90232;
    ###
    # Calculate the number of BOEC seed heavy-metal moles;
    # This number is conserved across recycles
    ###
    chargeMoles = sum(moles for za, moles in previousPickle.GetZa2Moles(seedCellNumbers).items() if ZaIsActinide(za));
    ###
    # Construct the seed charge:
    # First, EOEC heavy metal moles are accumulated;
    # Second, any mole deficit or surplus is made up with thorium
    ###
    currentPickle = self.GetPickle();
    za2ChargeMoles = {};
    for za, moles in currentPickle.GetZa2Moles(upperBlanketCellNumbers + seedCellNumbers + lowerBlanketCellNumbers, endOfCycle = bool(self.GetRecycleIndex())).items():
        if ZaIsActinide(za):
            try:
                za2ChargeMoles[za] += moles;
            except KeyError:
                za2ChargeMoles[za] = moles;
    ###
    deviation = chargeMoles - sum(za2ChargeMoles.values());
    try:
        za2ChargeMoles[thorium] += deviation;
    except KeyError:
        za2ChargeMoles[thorium] = deviation;
    assert(za2ChargeMoles[thorium] > 0);
    ###
    ###
    # Distribute the seed charge:
    # First, split moles evenly between (equal-volumed) seed cells
    # Second, match BOEC moles for each cell by adjusting thoria moles
    ###
    cellNumber2Za2ChargeMoles = {cellNumber : {za : moles / numberOfSeedCells for za, moles in za2ChargeMoles.items()} for cellNumber in seedCellNumbers};
    ###
    for cellNumber in seedCellNumbers:
        cellMoles = sum(previousPickle.GetZa2Moles([cellNumber]).values());
        deviation = cellMoles - sum(cellNumber2Za2ChargeMoles[cellNumber].values());
        try:
            cellNumber2Za2ChargeMoles[cellNumber][thorium] += deviation;
        except KeyError:
            cellNumber2Za2ChargeMoles[cellNumber][thorium] = deviation;
        assert(cellNumber2Za2ChargeMoles[cellNumber][thorium] > 0);
    ###
    # Distribute the blanket charge:
    # Simply grab the BOEC moles
    ###
    cellNumber2Za2ChargeMoles.update({cellNumber : previousPickle.GetZa2Moles([cellNumber]) for cellNumber in upperBlanketCellNumbers + lowerBlanketCellNumbers});
    ###
    # Recharge cells
    ###
    currentPickle.cellNumber2Zam2Moles = {cellNumber : [{Za2Zam(za) : moles for za, moles in za2ChargeMoles.items()}] for cellNumber, za2ChargeMoles in cellNumber2Za2ChargeMoles.items()};
    ###
    return currentPickle;
###
PECSDepletion.ProcessFuel = ProcessFuel;

###
### Script
###

###
# Main()
###
if __name__ == '__main__':
    ###
    # Interpret arguments
    ###
    from sys import argv;
    argv.reverse();
    script = argv.pop();
    ###
    # MCNP input file name
    ###
    if argv:
        arguments.transportFileName = argv.pop();
    else:
        arguments.transportFileName = 'inp1';
    ###
    # Isotopic convergence tolerance
    ###
    if argv:
        mocDownInputFile.parameters['isotopicsConvergenceTolerance'] = float(argv.pop());
    else:
        mocDownInputFile.parameters['isotopicsConvergenceTolerance'] = 1e-9;
    ###
    # MocDown depletion calculation pickle
    ###
    arguments.pickleFileName = '{}.pkl.gz'.format(arguments.transportFileName);
    ###
    # Find equilibrium
    ###
    nemCalculation = PECSCalculation(arguments);
