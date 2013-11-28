#! /usr/bin/env python3

###
### Library imports
###

if 'Offline' in __file__.split('/')[-1].replace('.py', ''):
    from MocDown import Array,\
                        Class,\
                        Exponent,\
                        LinearInterpolate,\
                        McnpInputFile,\
                        MocDownInputFile,\
                        Nan2Num,\
                        NaturalLogarithm,\
                        NonZero,\
                        PrintNow,\
                        WordArrange,\
                        WriteFile,\
                        ZaIsActinide,\
                        Zeros,\
                        avogadrosNumber,\
                        epsilon;

###
### Custom classes
###

###
# Void-fraction and critical power ratio calculation results
###
class BoilingCalculation:
    def __init__(self, cellNumbers, cellNumber2PreviousMassDensity, cellNumber2MassDensity, axialPowers, axialQualitys, axialVoidFractions, finePositionCPRs, minimumCriticalPowerRatio, minimumCriticalPowerRatioQuality, minimumCriticalPowerRatioLocation, criticalPowerRatioLimit, flowLengths, axialPressureDrops, transportOutputFile):
        self.cellNumbers = cellNumbers;
        self.cellNumber2PreviousMassDensity = cellNumber2PreviousMassDensity;
        self.cellNumber2MassDensity = cellNumber2MassDensity;
        ###
        # Iterate over cell #
        ###
        self.cellNumber2ThermalPower = {};
        self.cellNumber2Quality = {};
        self.cellNumber2VoidFraction = {};
        self.cellNumber2PressureDrop = {};
        for index in range(len(self.GetCellNumbers())):
            cellNumber = self.GetCellNumbers()[index];
            ###
            self.cellNumber2ThermalPower[cellNumber] = axialPowers[index];
            self.cellNumber2Quality[cellNumber] = axialQualitys[index];
            self.cellNumber2VoidFraction[cellNumber] = axialVoidFractions[index];
            self.cellNumber2PressureDrop[cellNumber] = axialPressureDrops[index];
        ###
        self.flowLengths = flowLengths;
        ###
        self.finePositionCPRs = finePositionCPRs;
        self.minimumCriticalPowerRatio = minimumCriticalPowerRatio;
        self.minimumCriticalPowerRatioQuality = minimumCriticalPowerRatioQuality;
        self.minimumCriticalPowerRatioLocation = minimumCriticalPowerRatioLocation;
        self.criticalPowerRatioLimit = criticalPowerRatioLimit;
        ###
        self.multiplicationFactor = transportOutputFile.GetMultiplicationFactor();
        self.multiplicationFactorSigma = transportOutputFile.GetMultiplicationFactorSigma();
        ###
        return;
    ###
    def __str__(self):
        lines = ['< Void fraction and pressure drop calculation outlet summary >'];
        ###
        attributeName = (
            ('cellNumber2PreviousMassDensity', 'ρorg [kg/m³]', 'G'),
            ('cellNumber2Quality',             'x', '.1%'),
            ('cellNumber2VoidFraction',        'α', '.1%'),
            ('cellNumber2MassDensity',         'ρ [kg/m³]', 'G'),
            ('cellNumber2PressureDrop',        'ΔP [MPa]', 'G'),
        );
        ###
        cellNumber = self.GetOutletCellNumber();
        for attribute, name, format in attributeName:
            lines.append('{{:<13s}} = {{:>13{}}}'.format(format).format(name, getattr(self, attribute)[cellNumber]));
        ###
        lines.append('< Minimum critical power ratio calculation summary >');
        attributeName = (
            ('minimumCriticalPowerRatio',         'MCPR', 'G'),
            ('minimumCriticalPowerRatioQuality',  'x(MCPR)', '.1%'),
            ('minimumCriticalPowerRatioLocation', 'z(MCPR) [m]', 'G'),
        );
        for attribute, name, format in attributeName:
            lines.append('{{:<13s}} = {{:>13{}}}'.format(format).format(name, getattr(self, attribute)));
        ###
        if self.GetMinimumCriticalPowerRatio() < self.GetCriticalPowerRatioLimit():
            lines.append('Warning: The MCPR limit of {} is violated'.format(self.GetCriticalPowerRatioLimit()));
        ###
        return '\n'.join('{:^59}'.format(line) for line in lines);
    ###
    def GetCellNumbers(self):
        return self.cellNumbers;
    ###
    def GetCellNumberAccumulatedFlowLength(self, cellNumber):
        return sum(self.flowLengths[ : self.GetCellNumbers().index(cellNumber) + 1]);
    ###
    def GetCellNumberFlowLength(self, cellNumber):
        return self.flowLengths[self.GetCellNumbers().index(cellNumber)];
    ###
    def GetCellNumberPressureDrop(self, cellNumber):
        return self.cellNumber2PressureDrop[cellNumber];
    ###
    def GetCellNumberPreviousMassDensity(self, cellNumber):
        return self.cellNumber2PreviousMassDensity[cellNumber];
    ###
    def GetCellNumberThermalPower(self, cellNumber):
        return self.cellNumber2ThermalPower[cellNumber];
    ###
    def GetCellNumberLinearHeatRate(self, cellNumber):
        return self.GetCellNumberThermalPower(cellNumber) / self.GetCellNumberFlowLength(cellNumber) / 1e2;
    ###
    def GetCellNumberQuality(self, cellNumber):
        return self.cellNumber2Quality[cellNumber];
    ###
    def GetCellNumberVoidFraction(self, cellNumber):
        return self.cellNumber2VoidFraction[cellNumber];
    ###
    def GetCellNumberMassDensity(self, cellNumber):
        return self.cellNumber2MassDensity[cellNumber];
    ###
    def GetCriticalPowerRatioLimit(self):
        return self.criticalPowerRatioLimit;
    ###
    def GetFinePositionCPRs(self):
        return self.finePositionCPRs;
    ###
    def GetMinimumCriticalPowerRatio(self):
        return self.minimumCriticalPowerRatio;
    ###
    def GetMinimumCriticalPowerRatioLocation(self):
        return self.minimumCriticalPowerRatioLocation;
    ###
    def GetMinimumCriticalPowerRatioQuality(self):
        return self.minimumCriticalPowerRatioQuality;
    ###
    def GetMultiplicationFactor(self):
        return self.multiplicationFactor;
    ###
    def GetMultiplicationFactorSigma(self):
        return self.multiplicationFactorSigma;
    ###
    def GetPressureDrop(self):
        return self.GetCellNumberPressureDrop(self.GetOutletCellNumber());
    ###
    def GetOutletCellNumber(self):
        return self.GetCellNumbers()[-1];
    ###
    def GetUpdateCellNumbers(self):
        return [cellNumber for cellNumber in self.cellNumber2MassDensity];
###
# Steam thermodynamic properties
###
class Steam:
    def __init__(self, pressure, temperature, massFlowRate, heatedDiameter, hydraulicDiameter, flowArea):
        ###
        # Import IAPWS97 steam properties library
        ###
        import iapws;
        ###
        # Gravitational accelration [m/s²]
        ###
        self.gravity = 9.80665;
        ###
        # Critical pressure [MPa]
        ###
        self.criticalPressure = iapws.Pc;
        ###
        # Pressure [MPa]
        ###
        self.pressure = pressure;
        ###
        # Temperature [K]
        ###
        self.temperature = temperature;
        ###
        # Mass flow rate [kg/s]
        ###
        self.massFlowRate = massFlowRate;
        ###
        # Heated diameter [m]
        ###
        self.heatedDiameter = heatedDiameter;
        ###
        # Hydraulic diameter [m]
        ###
        self.hydraulicDiameter = hydraulicDiameter;
        ###
        # Cross-sectional flow area [m²]
        ###
        self.flowArea = flowArea;
        ###
        # Mass flux [kg/m²·s]
        ###
        self.massFlux = self.massFlowRate / self.flowArea;
        ###
        # Sub-cooled, saturated liquid, and saturated vapor
        ###
        inlet  = iapws.IAPWS97(P = self.pressure, T = self.temperature);
        liquid = iapws.IAPWS97(P = self.pressure, x = 0);
        vapor  = iapws.IAPWS97(P = self.pressure, x = 1);
        ###
        # Mass density [kg/m³]
        ###
        self.densityInlet   = inlet.rho;
        self.densityLiquid  = liquid.rho;
        self.densityVapor   = vapor.rho;
        ###
        # Specific enthalpy [kJ/kg]
        ###
        self.enthalpyInlet  = inlet.h;
        self.enthalpyLiquid = liquid.h;
        self.enthalpyVapor  = vapor.h;
        ###
        # Surface tension [N/m]
        ###
        self.surfaceTension = liquid.sigma;
        ###
        # Dynamic viscosity [Pa·s]
        ###
        liquid = iapws.IAPWS97(P = self.pressure, T = liquid.T - 1e-9);
        vapor  = iapws.IAPWS97(P = self.pressure, T = vapor.T + 1e-9);
        self.dynamicViscosityInlet        = inlet.mu;
        self.dynamicViscosityLiquid       = liquid.mu;
        self.dynamicViscosityVapor        = vapor.mu;
        ###
        return;
    ###
    def __str__(self):
        lines = ['< Steam thermodynamic properties summary >'];
        ###
        attributeName = (
            ('gravity',                'g [m/s²]'),
            ('criticalPressure',       'Pcrit [MPa]'),
            ('pressure',               'Psat [MPa]'),
            ('temperature',            'Tin [K]'),
            ('massFlowRate',           'mdot [kg/s]'),
            ('heatedDiameter',         'Dh [m]'),
            ('hydraulicDiameter',      'De [m]'),
            ('flowArea',               'A [m²]'),
            ('densityInlet',           'ρin [kg/m³]'),
            ('densityLiquid',          'ρl [kg/m³]'),
            ('densityVapor',           'ρv [kg/m³]'),
            ('enthalpyInlet',          'hin [kJ/kg]'),
            ('enthalpyLiquid',         'hl [kJ/kg]'),
            ('enthalpyVapor',          'hv [kJ/kg]'),
            ('surfaceTension',         'σ [N/m]'),
            ('dynamicViscosityInlet',  'μin [Pa·s]'),
            ('dynamicViscosityLiquid', 'μl [Pa·s]'),
            ('dynamicViscosityVapor',  'μv [Pa·s]'),
        );
        ###
        for attribute, name in attributeName:
            lines.append('{:<13s} = {:>13G}'.format(name, getattr(self, attribute)));
        ###
        return '\n'.join('{:^59}'.format(line) for line in lines);

###
### Custom functions
###

###
# Library-specific MocDown input parameters
###
def GetLibraryParametersConverters(self):
    ###
    # Default parameter values
    ###
    parameters = {
        # #
        'criticalPowerRatioFallbackIndex' : 41,
        # #.#
        # #
        'coolantDensityDampingCoefficient' : 1,
        'coolantFlowArea' : 0.030115717, # [m²]
        'coolantHeatedDiameter' : 0.004692958, # [m]
        'coolantHydraulicDiameter' : 0.00397346, # [m]
        'coolantInletPressure' : 7.25, # [MPa]
        'coolantInletTemperature' : 555.71, # [K]
        'coolantMassFlowRate' : 29.68, # [kg/s]
        'criticalPowerRatioLimit' : 1.3,
        'thermalHydraulicConvergenceTolerance' : 5e-2,
        # ''.lower()
        'criticalPowerRatioCorrelation' : 'm-cise',
        'pressureDropCorrelation' : 'epri',
        'thermalHydraulicConvergenceNormType' : '2',
        'voidFractionCorrelation' : 'relap',
        # [#]
        'coolantBypassCells' : [],
        # [#.#]
        'coolantFlowLengths' : [], # [m]
        # fuels -> cools
        'assemblyFuelsToCools' : [],
    };
    ###
    # Default converters
    ###
    Bool = lambda value, values: bool(int(value));
    Float = lambda value, values: float(value);
    FuelsToCools = lambda value, values: [tuple({tuple(int(float(fuel)) for fuel in fuels.strip('( )').split()) : tuple(int(float(cool)) for cool in cools.strip('( )').split())} for fuels2Cools in value.split(',') for fuels, cools in [fuels2Cools.split(':')])];
    Int = lambda value, values: int(float(value));
    ###
    def ListInt(value, values):
        out = [];
        for index in range(len(values)):
            if '..' in values[index]:
                lo, hi = values[index].split('.')[0 : 3 : 2];
                out.extend(range(int(float(lo)), int(float(hi)) + 1));
            else:
                out.append(int(float(values[index].strip(','))));
        return out;
    ###
    def ListFloat(value, values):
        out = [];
        for index in range(len(values)):
            if 'r' in values[index]:
                repeat, number = values[index].split('r');
                out.extend([float(number)] * int(float(repeat)));
            else:
                out.append(float(values[index].strip(',')));
        return out;
    ###
    Lower = lambda value, values: value.strip().lower();
    Return = lambda value, values: value.strip();
    ###
    converters = {
        # #
        'criticalPowerRatioFallbackIndex' : Int,
        # #.#
        'coolantDensityDampingCoefficient' : Float,
        'coolantFlowArea' : Float,
        'coolantHeatedDiameter' : Float,
        'coolantHydraulicDiameter' : Float,
        'coolantInletPressure' : Float,
        'coolantInletTemperature' : Float,
        'coolantMassFlowRate' : Float,
        'criticalPowerRatioLimit' : Float,
        'thermalHydraulicConvergenceTolerance' : Float,
        # ''.lower()
        'criticalPowerRatioCorrelation' : Lower,
        'pressureDropCorrelation' : Lower,
        'thermalHydraulicConvergenceNormType' : Lower,
        'voidFractionCorrelation' : Lower,
        # fuels -> cools
        'assemblyFuelsToCools' : FuelsToCools,
        # [#]
        'coolantBypassCells' : ListInt,
        # [#.#]
        'coolantFlowLengths' : ListFloat,
    };
    ###
    return parameters, converters;
###
# RBWR-Th recycling scheme
###
def RbwrThRecycle(bocTransportFile, eocTransportFile):
    ###
    # Hard code the blanket and seed cell parameters
    ###
    numberOfUpperBlanketCells = 15;
    numberOfUpperSeedCells = 30;
    numberOfLowerSeedCells = 0;
    numberOfLowerBlanketCells = 10;
    ###
    lowerSeedRemovalFraction = 0.5;
    ###
    # This is a switch for: (True) Jeff's vanilla cell numbering and (False) Chris and George's cell numbering
    ###
    if True:
        firstCellNumber = 3;
        ###
        # Define the blanket and seed cell numbers
        ###
        previous = firstCellNumber;
        upperBlanketCellNumbers = list(range(previous, previous + numberOfUpperBlanketCells));
        previous = max(upperBlanketCellNumbers) + 1;
        upperSeedCellNumbers    = list(range(previous, previous + numberOfUpperSeedCells));
        previous = max(upperBlanketCellNumbers + upperSeedCellNumbers) + 1;
        lowerSeedCellNumbers    = list(range(previous, previous + numberOfLowerSeedCells));
        previous = max(upperBlanketCellNumbers + upperSeedCellNumbers + lowerSeedCellNumbers) + 1;
        lowerBlanketCellNumbers = list(range(previous, previous + numberOfLowerBlanketCells));
    else:
        firstCellNumber = 1001;
        ###
        # Define the blanket and seed cell numbers
        ###
        previous = firstCellNumber;
        lowerBlanketCellNumbers = list(range(previous, previous + numberOfLowerBlanketCells));
        previous = max(lowerBlanketCellNumbers) + 1;
        lowerSeedCellNumbers    = list(range(previous, previous + numberOfLowerSeedCells));
        previous = max(lowerBlanketCellNumbers + lowerSeedCellNumbers) + 1;
        upperSeedCellNumbers    = list(range(previous, previous + numberOfUpperSeedCells));
        previous = max(lowerBlanketCellNumbers + lowerSeedCellNumbers + upperSeedCellNumbers) + 1;
        upperBlanketCellNumbers = list(range(previous, previous + numberOfUpperBlanketCells));
    ###
    # Isotopic ZA strings
    ###
    oxygen = 8016;
    thorium = 90232;
    ###
    # Calculate the number of BOEC seed heavy-metal moles;
    # This number is conserved across recycles
    ###
    chargeMoles = sum(moles for cellNumber in upperSeedCellNumbers + lowerSeedCellNumbers for za, moles in bocTransportFile.FindCell(cellNumber).GetZa2Moles().items() if ZaIsActinide(za));
    ###
    # Construct the seed charge:
    # First, EOEC heavy metal moles are accumulated;
    # Second, any mole deficit or surplus is made up with thorium
    # Third, add twice as many oxygen moles as heavy metal moles
    ###
    za2ChargeMoles = {};
    for cellNumber in upperBlanketCellNumbers + upperSeedCellNumbers + lowerSeedCellNumbers + lowerBlanketCellNumbers:
        for za, moles in eocTransportFile.FindCell(cellNumber).GetZa2Moles().items():
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
    za2ChargeMoles[oxygen] = 2 * chargeMoles;
    ###
    # Distribute the seed charge:
    # First, split moles evenly between (equal-volumed) seed cells
    # Second, remove a fraction of the lower seed cell transthorium moles, replacing them with thorium
    # Third, distribute the removed moles among the upper seed cells, displacing thorium
    # Fourth, match BOEC moles for each cell by adjusting thoria moles
    ###
    numberOfSeedCells = numberOfUpperSeedCells + numberOfLowerSeedCells;
    cellNumber2Za2ChargeMoles = {cellNumber : {za : moles / numberOfSeedCells for za, moles in za2ChargeMoles.items()} for cellNumber in upperSeedCellNumbers + lowerSeedCellNumbers};
    ###
    fromLowerSeed = {};
    for cellNumber in lowerSeedCellNumbers:
        for za, moles in cellNumber2Za2ChargeMoles[cellNumber].items():
            if za not in (oxygen, thorium):
                minusMoles = moles * lowerSeedRemovalFraction;
                cellNumber2Za2ChargeMoles[cellNumber][za] -= minusMoles;
                cellNumber2Za2ChargeMoles[cellNumber][thorium] += minusMoles;
                try:
                    fromLowerSeed[za] += minusMoles;
                except KeyError:
                    fromLowerSeed[za] = minusMoles;
    ###
    for cellNumber in upperSeedCellNumbers:
        for za, moles in fromLowerSeed.items():
            cellNumber2Za2ChargeMoles[cellNumber][za] += moles / numberOfUpperSeedCells;
            cellNumber2Za2ChargeMoles[cellNumber][thorium] -= moles / numberOfUpperSeedCells;
    ###
    for cellNumber in upperSeedCellNumbers + lowerSeedCellNumbers:
        bocCell = bocTransportFile.FindCell(cellNumber);
        deviation = bocCell.GetMoles() - sum(cellNumber2Za2ChargeMoles[cellNumber].values());
        try:
            cellNumber2Za2ChargeMoles[cellNumber][thorium] += deviation * 1 / 3;
            cellNumber2Za2ChargeMoles[cellNumber][oxygen] += deviation * 2 / 3;
        except KeyError:
            cellNumber2Za2ChargeMoles[cellNumber][thorium] = deviation * 1 / 3;
            cellNumber2Za2ChargeMoles[cellNumber][oxygen] = deviation * 2 / 3;
        assert(cellNumber2Za2ChargeMoles[cellNumber][thorium] > 0);
    ###
    # Distribute the blanket charge:
    # Simply grab the BOEC moles
    ###
    cellNumber2Za2ChargeMoles.update({cellNumber : bocTransportFile.FindCell(cellNumber).GetZa2Moles() for cellNumber in upperBlanketCellNumbers + lowerBlanketCellNumbers});
    ###
    # Recharge cells
    ###
    for cellNumber in upperBlanketCellNumbers + upperSeedCellNumbers + lowerSeedCellNumbers + lowerBlanketCellNumbers:
        za2ChargeMoles = cellNumber2Za2ChargeMoles[cellNumber];
        ###
        # Replace cell cards
        ###
        cell = eocTransportFile.FindCell(cellNumber);
        ###
        numberDensity = sum(za2ChargeMoles.values()) / cell.GetVolume() * avogadrosNumber;
        cellCard = cell.GetMaterialDensityRegex().sub('{:+10.7f}'.format(numberDensity), cell.GetRaw());
        ###
        eocTransportFile.ReplaceNewputCard(cell, cellCard);
        ###
        # Replace material cards
        ###
        material = eocTransportFile.FindCellMaterial(cellNumber);
        ###
        suffix = cell.GetSuffix();
        totalMoles = sum(za2ChargeMoles.values()) / 3;
        zaid2AtomFraction = {'{}.{}'.format(za, suffix) : moles / totalMoles for za, moles in za2ChargeMoles.items()};
        materialCard = WordArrange(words = ('{:>10} {:+.5E}'.format(zaid, atomFraction) for zaid, atomFraction in sorted(zaid2AtomFraction.items(), key = lambda item: (item[1], item[0]), reverse = True)), prefix = '\nm{:<6d}'.format(material.GetNumber()), indent = 8);
        ###
        eocTransportFile.ReplaceNewputCard(material, materialCard);
    ###
    return eocTransportFile;
###
# Polynomial interpolation
###
def PolynomialInterpolation(x, xp, yp, order):
    from numpy import polyfit, polyval;
    ###
    return polyval(polyfit(xp, yp, order), x);
###
# Multi-batch core keff @ EOC
###
def MultiBatchCoreKeffEoc(self):
    ###
    # Extract coarse times, keffs, and powers
    ###
    coarseIndex = [index for index in range(len(self)) if self.GetDepletionCalculationPickle().multiplicationFactors[index] is not None];
    ###
    coarseTimes = [self.GetParameter('depletionStepTimeEnds')[index] for index in coarseIndex];
    coarsePowers = [self.GetParameter('depletionStepPowers')[index] for index in coarseIndex];
    coarseKeffs = [self.GetDepletionCalculationPickle().multiplicationFactors[index] for index in coarseIndex];
    ###
    # Construct core keffs from coarse keffs (which may or may not coincide with batch keffs)
    # Right now, it is assumed that each batch produces the same power
    # Later, we will modify this using coarseTimes/coarsePowers values interpolated
    # Also, get rid of the E_f and nu assumptions via the memo
    ### # FIXME Address this
    coreTimes, coreKeffs = MultiBatchHarmonicMean(coarseTimes, coarseKeffs);
    ###
    return coreKeffs[-1];
###
# Multi-batch harmonic mean
###
def MultiBatchHarmonicMean(times, values, order = 4, weights = None, timeSteps = 500, batches = 5):
    ###
    # If not provided, assume equal power fractions between batches
    ###
    if weights is None:
        weights = [1 / batches] * batches;
    ###
    period = max(times) / batches;
    ###
    if True:
        ###
        # Reactivity is interpolated with an nth order polynomial fit
        ###
        return [period * timeStep / timeSteps for timeStep in range(timeSteps + 1)], [1 / sum(PolynomialInterpolation(period * (timeStep / timeSteps + index), times, weights[index] / Array(values), order) for index in range(batches)) for timeStep in range(timeSteps + 1)];
    else:
        ###
        # Reactivity is interpolated with a piecewise linear fit
        ###
        return [period * timeStep / timeSteps for timeStep in range(timeSteps + 1)], [1 / sum(LinearInterpolate(period * (timeStep / timeSteps + index), times, weights[index] / Array(values)) for index in range(batches)) for timeStep in range(timeSteps + 1)];
###
# Multi-batch core keff(t) as a function of time
###
MultiBatchCoreKeff = MultiBatchHarmonicMean;
###
# Multi-batch core keff @ EOC, with varied cycle lengths
###
def MultiBatchCoreKeffEocCycleStretch(times, values, order = 4, minimum = 0., maximum = 2., number = 500):
    ###
    # Linear interpolation/extrapolation
    ###
    def InterpExtrap(xp, yp, x, order):
        x = Array(x);
        ###
        if True:
            ###
            # Polynomial interpolation
            ###
            y = PolynomialInterpolation(x, xp, yp, order);
        else:
            ###
            # Piece-wise linear interpolation
            ###
            y = LinearInterpolate(x, xp, yp);
        ###
        # Linear extrapolation
        ###
        if any(x < xp[0]):
            y[x < xp[0]] = yp[0] + (x[x < xp[0]] - xp[0]) / (xp[1] - xp[0]) * (yp[1] - yp[0]);
        if any(x > xp[-1]):
            y[x > xp[-1]] = yp[-1] + (x[x > xp[-1]] - xp[-1]) / (xp[-2] - xp[-1]) * (yp[-2] - yp[-1]);
        ###
        return y;
    ###
    maxTime = max(times);
    ###
    harmonicTimes = [];
    harmonicMeans = [];
    ###
    for index in range(number + 1):
        newTime = maxTime * (minimum + (maximum - minimum) * (index / number));
        ###
        newTimes = [time for time in times if time < newTime] + [newTime];
        newValues = values[ : len(newTimes) - 1] + list(InterpExtrap(times, values, [newTime], order));
        ###
        junk, means = MultiBatchHarmonicMean(newTimes, newValues, timeSteps = 1);
        ###
        harmonicTimes.append(newTime);
        harmonicMeans.append(means[-1]);
    ###
    return harmonicTimes, harmonicMeans;
###
# Generic void fraction correlation (Carey, p.512)
###
def VoidFractionGeneric(x, rhol, rhov, mul, muv, Bb, n1, n2, n3):
    ###
    return 1 / (1 + Bb * ((1 - x) / x) ** n1 * (rhov / rhol) ** n2 * (mul / muv) ** n3);
###
# Homogeneous void fraction correlation (Carey, p.512)
###
def VoidFractionHomogeneous(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    ###
    return VoidFractionGeneric(x = x, rhol = rhol, rhov = rhov, mul = mul, muv = muv, Bb = 1, n1 = 1, n2 = 1, n3 = 0);
###
# Zivi void fraction correlation (Carey, p.512)
###
def VoidFractionZivi(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    ###
    return VoidFractionGeneric(x = x, rhol = rhol, rhov = rhov, mul = mul, muv = muv, Bb = 1, n1 = 1, n2 = 2 / 3, n3 = 0);
###
# Wallis void fraction correlation (Carey, p.512)
###
def VoidFractionWallis(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    ###
    return VoidFractionGeneric(x = x, rhol = rhol, rhov = rhov, mul = mul, muv = muv, Bb = 1, n1 = 0.72, n2 = 0.4, n3 = 0.08);
###
# Lockhart and Martinelli void fraction correlation (Carey, p.512)
###
def VoidFractionLM(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    ###
    return VoidFractionGeneric(x = x, rhol = rhol, rhov = rhov, mul = mul, muv = muv, Bb = 0.28, n1 = 0.64, n2 = 0.36, n3 = 0.07);
###
# Thom void fraction correlation (Carey, p.512)
###
def VoidFractionThom(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    ###
    return VoidFractionGeneric(x = x, rhol = rhol, rhov = rhov, mul = mul, muv = muv, Bb = 1, n1 = 1, n2 = 0.89, n3 = 0.18);
###
# Baroczy void fraction correlation (Carey, p.512)
###
def VoidFractionBaroczy(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    ###
    return VoidFractionGeneric(x = x, rhol = rhol, rhov = rhov, mul = mul, muv = muv, Bb = 1, n1 = 0.74, n2 = 0.65, n3 = 0.13);
###
# Generic drift-flux void fraction correlation
###
def VoidFractionDriftFlux(x, rhol, rhov, G, C0, Vvj):
    ###
    return 1 / (C0 * (1 + (1 - x) / x * rhov / rhol) + Vvj * rhov / x / G);
###
# Bestion void fraction correlation
###
def VoidFractionBestion(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    g = steam.gravity;
    G = steam.massFlux;
    De = steam.hydraulicDiameter;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    rholv = rhol - rhov;
    ###
    # Calculate intermediate variables
    ###
    jv = G * x / rhov;
    jl = G * (1 - x) / rhol;
    ###
    jgst = jv * (rhov / (g * De * rholv)) ** 0.5;
    C0 = 1.;
    ###
    Vvj = 0.188 * jv / jgst;
    ###
    # Return drift-flux void fraction
    ###
    return VoidFractionDriftFlux(x = x, rhol = rhol, rhov = rhov, G = G, C0 = C0, Vvj = Vvj);
###
# Liao/Parlos/Griffith (LPG) void fraction correlation
###
def VoidFractionLPG(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    g = steam.gravity;
    G = steam.massFlux;
    De = steam.hydraulicDiameter;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    rholv = rhol - rhov;
    sigma = steam.surfaceTension;
    ###
    # Calculate intermediate variables
    ###
    jv = G * x / rhov;
    jl = G * (1 - x) / rhol;
    ###
    jgst = jv * (rhov / (g * De * rholv)) ** 0.5;
    ###
    boundary = 2.34 - 1.07 * (g * sigma * rholv / rhol ** 2.) ** 0.25;
    ###
    # Instantiate void fraction
    ###
    alpha = Array([0.] * len(quality));
    ###
    # Iterate over spatial regions
    ###
    for index in range(len(x)):
        ###
        # Determine flow regime
        ###
        if jl[index] > boundary:
            regime = 0;
        elif jgst[index] > 1:
            regime = 1;
        else:
            regime = 2;
        ###
        # Use value of prior cell as a first guess for the void fraction, if it exists
        ###
        if index:
            alpha[index] = alpha[index - 1];
        ###
        # Fixed-point iteration
        ###
        difference = epsilon;
        while difference >= epsilon:
            previous = alpha[index];
            if 0 == regime:
                ###
                # Bubbly
                ###
                C0 = 1.;
                Vvj = 1.53 * (1. - alpha[index]) ** 2. * (g * sigma * rholv / rhol ** 2.) ** 0.25;
            elif 1 == regime:
                ###
                # Annular
                ###
                C0 = 1. + (1. - alpha[index]) / (alpha[index] + 4. * (rhov / rhol) ** 0.5);
                Vvj = (C0 - 1.) * (g * De * rholv * (1 - alpha[index]) / (0.015 * rhol)) ** 0.5;
            elif 2 == regime:
                ###
                # Churn/slug
                ###
                C0 = 1.2 - 0.2 * (rhov / rhol) ** 0.5 * (1. - Exponent(-18. * alpha[index]));
                Vvj = 0.33 * (g * sigma * rholv / rhov ** 2.) ** 0.25;
            ###
            alpha[index] = VoidFractionDriftFlux(x = x[index], rhol = rhol, rhov = rhov, G = G, C0 = C0, Vvj = Vvj);
            ###
            difference = abs(previous - alpha[index]);
        ###
        # Smooth discontinuities between flow-regimes
        ###
        if 0 == regime:
            alphaBubbly = alpha[index];
        elif 1 == regime:
            try:
                alpha[index] = max(alpha[index], alphaSlug);
            except UnboundLocalError:
                alpha[index] = max(alpha[index], alphaBubbly);
        elif 2 == regime:
            alphaSlug = alpha[index];
    ###
    # Return drift-flux void fraction
    ###
    return alpha;
###
# Chexal-Lellouche void fraction correlation
###
def VoidFractionChexalLellouche(steam, quality):
    ###
    # Extract steam properties
    ###
    x = quality;
    g = steam.gravity;
    G = steam.massFlux;
    De = steam.hydraulicDiameter;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    rholv = rhol - rhov;
    rhovOl = rhov / rhol;
    sigma = steam.surfaceTension;
    mul = steam.dynamicViscosityLiquid;
    muv = steam.dynamicViscosityVapor;
    P = steam.pressure;
    Pcrit = steam.criticalPressure;
    ###
    # Calculate static variables
    ###
    Rel = G * (1 - x) * De / mul;
    Rev = G *  x * De / muv;
    ###
    B1 = Array([min(0.8, 1 / (1 + Exponent(-max(Rel[index], Rev[index]) / 6e4))) for index in range(len(x))]);
    K0 = B1 + (1 - B1) * rhovOl ** 0.25;
    r = (1 + 1.57 * rhovOl) / (1 - B1);
    C1 = 4 * Pcrit ** 2. / P / (Pcrit - P);
    ###
    C3 = Array([max(0.5, 2 * Exponent(-abs(Rel[index]) / 6e4)) for index in range(len(x))]);
    C5 = (150 * rhovOl) ** 0.5;
    if 1 / rhovOl <= 18:
        C2 = 0.4757 * (-NaturalLogarithm(rhovOl)) ** 0.7;
    else:
        if C5 >= 1:
            C2 = 1;
        else:
            C2 = 1 / (1 - Exponent(-C5 / (1 - C5)));
    ###
    C7 = (0.09144 / De) ** 0.6;
    if C7 >= 1:
        C4 = 1;
    else:
        C4 = 1 / (1 - Exponent(-C5 / (1 - C5)));
    ###
    # Instantiate void fraction
    ###
    alpha = Array([0.] * len(quality));
    ###
    # Iterate over spatial regions
    ###
    for index in range(len(x)):
        ###
        # Use value of prior cell as a first guess for the void fraction, if it exists
        ###
        if index:
            alpha[index] = alpha[index - 1];
        ###
        # Fixed-point iteration
        ###
        difference = epsilon;
        while difference >= epsilon:
            previous = alpha[index];
            C9 = (1 - alpha[index]) ** B1[index];
            Vvj = 2 ** 0.5 * (g * sigma * rholv / rhol ** 2.) ** 0.25 * C2 * C3[index] * C4 * C9;
            L = (1 - Exponent(-C1 * alpha[index])) / (1 - Exponent(-C1));
            C0 = L / (K0[index] + (1 - K0[index]) * alpha[index] ** r[index]);
            ###
            alpha[index] = VoidFractionDriftFlux(x = x[index], rhol = rhol, rhov = rhov, G = G, C0 = C0, Vvj = Vvj);
            difference = abs(previous - alpha[index]);
    ###
    # Return drift-flux void fraction
    ###
    return alpha;
###
# Chexal-Lellouche void fraction correlation
###
VoidFractionRELAP = VoidFractionChexalLellouche;
###
# MIT-modified CISE-4 critical power ratio correlation
###
def CriticalPowerRatioMITCISE4(steam, axialPowers, flowLengths, endIndex):
    ###
    # Extract steam properties
    ###
    mdot = steam.massFlowRate;
    G = steam.massFlux;
    Dh = steam.heatedDiameter;
    De = steam.hydraulicDiameter;
    P = steam.pressure;
    Pcrit = steam.criticalPressure;
    hfg = steam.enthalpyVapor - steam.enthalpyLiquid;
    dhsub = steam.enthalpyLiquid - steam.enthalpyInlet;
    Pz = Array([axialPower for axialPower in axialPowers]);
    dz = flowLengths;
    ###
    # Define correlation limits
    ###
    limits = {
        'G'    : (100, 2035),
        'De'   : (0.00235, 0.00703),
        'P'    : (1, 8.6),
        };
    ###
    # Check limits
    ###
    try:
        assert(min(limits['G']) <= G <= max(limits['G']));
    except AssertionError:
        PrintNow('Mass flux violates MCPR correlation limits');
    ###
    try:
        assert(min(limits['De']) <= De <= max(limits['De']));
    except AssertionError:
        PrintNow('Hydraulic diameter violates MCPR correlation limits');
    ###
    try:
        assert(min(limits['P']) <= P <= max(limits['P']));
    except AssertionError:
        PrintNow('System pressure violates MCPR correlation limits');
    ###
    # Apply safety margin
    ###
    mdot *= 0.95;
    G *= 0.95;
    Pz *= 1.25;
    ###
    # Determine the location of the onset of boiling for a peaked channel
    ###
    onsetIndex = NonZero(Pz.cumsum() / mdot >= dhsub)[0][0];
    ###
    # Calculate static variables
    ###
    b = 0.199 * (Pcrit / P - 1) ** 0.4 * G * De ** 1.2;
    Gstar = 3375. * (1 - P / Pcrit) ** 3.;
    if G <= Gstar:
        a = (1 + (1 - P / Pcrit) ** -3. * 0.7 * G / 6750.) ** -1.;
    else:
        a = (1 - P / Pcrit) / (0.7 * G / 1000.) ** (1. / 3.);
    ###
    # Iterate over spatial regions
    ###
    criticalQuality = Zeros(Pz.shape);
    criticalPowerRatio = Zeros(Pz.shape);
    boilingLength = 0;
    thermalPower = sum(Pz[ : onsetIndex]);
    for index in range(onsetIndex + 1, endIndex):
        boilingLength += dz[index];
        thermalPower += Pz[index];
        ###
        criticalQuality[index] = (De / Dh) * a / (1 + b / boilingLength);
        criticalPowerRatio[index] = mdot * hfg * criticalQuality[index] / thermalPower;
    ###
    return criticalQuality, criticalPowerRatio;
###
# Hitachi-modified CISE-4 critical power ratio correlation
###
##### FIXME: This is a proprietary correlation.  Please run hitachi.sh to patch this file.
###
# Generic two-phase pressure drop correlation
###
def PressureDropTwoPhase(steam, quality, voidFraction, massDensity, flowLengths, twoPhaseFrictionMultiplier):
    ###
    # Extract steam properties
    ###
    x = quality;
    alpha = voidFraction;
    rhomix = massDensity;
    dz = flowLengths;
    phi2 = twoPhaseFrictionMultiplier;
    g = steam.gravity;
    G = steam.massFlux;
    De = steam.hydraulicDiameter;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    mul = steam.dynamicViscosityLiquid;
    ###
    # Calculate intermediate variables;
    # One over the dynamic density;
    # Fanning friction factor
    ###
    vm = Nan2Num(x ** 2. / rhov / alpha + (1 - x) ** 2. / rhov / (1 - alpha));
    flo = 0.079 * (G * De / mul) ** -0.25;
    ###
    # Iterate over spatial regions
    ###
    dP = Zeros(x.shape);
    for index in range(1, len(x)):
        ###
        # Accumulate;
        # Acceleration;
        # Gravitational;
        # Frictional
        ###
        dP[index] = dP[index - 1] + \
                    G ** 2. * (vm[index] - vm[index - 1]) + \
                    g * 0.5 * (dz[index - 1] + dz[index]) * 0.5 * (rhomix[index - 1] + rhomix[index]) + \
                    2. * flo * G ** 2. / De / rhol * 0.5 * (dz[index - 1] + dz[index]) * 0.5 * (phi2[index - 1] + phi2[index]);
    ###
    return dP;
###
# EPRI two-phase friction multiplier correlation
###
def PressureDropEPRI(steam, quality, voidFraction, massDensity, flowLengths):
    ###
    # Extract steam properties
    ###
    x = quality;
    G = steam.massFlux;
    rhol = steam.densityLiquid;
    rhov = steam.densityVapor;
    P = steam.pressure;
    Pcrit = steam.criticalPressure;
    ###
    # Calculate two-phase friction multiplier
    ###
    if P >= 4.14:
        Cf = 1.02 * x ** -0.175 * (G / 1356.) ** -0.45;
    else:
        Cf = 0.357 * x ** -0.175 * (G / 1356.) ** -0.45 * (1. + 10. * P / Pcrit);
    twoPhaseFrictionMultiplier = 1. + (rhol / rhov - 1.) * x * Nan2Num(Cf);
    ###
    return PressureDropTwoPhase(steam = steam, quality = quality, voidFraction = voidFraction, massDensity = massDensity, flowLengths = flowLengths, twoPhaseFrictionMultiplier = twoPhaseFrictionMultiplier);
###
# RBWR-Th boiling calculation
###
def RbwrThBoilingCalculation(self, transportOutputFile):
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
    # Cell # -> Wth
    ###
    cellNumber2ThermalPower = {cellNumber : self.GetCellNumberThermalPower(transportOutputFile, cellNumber, includeDecayHeat = True) for cellNumber in transportOutputFile.GetPowerCells()};
    ###
    PrintNow('> Calculating coolant densities for {}: {:.2f} MWth'.format(self.GetDepletionString(), sum(cellNumber2ThermalPower.values()) / 1e6));
    ###
    # Fuel -> Cool
    ###
    assemblys = self.GetParameter('assemblyFuelsToCools');
    ###
    # Extract steam properties
    ###
    steam = Steam(pressure = self.GetParameter('coolantInletPressure'), temperature = self.GetParameter('coolantInletTemperature'), massFlowRate = self.GetParameter('coolantMassFlowRate'), heatedDiameter = self.GetParameter('coolantHeatedDiameter'), hydraulicDiameter = self.GetParameter('coolantHydraulicDiameter'), flowArea = self.GetParameter('coolantFlowArea'));
    ###
    if self.GetIsVerbose():
        PrintNow(steam);
    ###
    # Iterate over assemblies
    ###
    assemblyIndex = 0;
    assemblyIndex2VoidFractionCalculation = {};
    for assembly in assemblys:
        ###
        # Extract original water densities
        ###
        cellNumbers = [cool for fuels2Cools in assembly for cools in fuels2Cools.values() for cool in cools];
        cellNumber2PreviousMassDensity = {cellNumber : transportOutputFile.FindCell(cellNumber).GetMassDensity() for cellNumber in cellNumbers + self.GetParameter('coolantBypassCells')};
        ###
        # Build axial power list;
        # Coolant is heated by fuels AND by cools
        ###
        axialZones = len(assembly);
        axialPowers = [sum(cellNumber2ThermalPower[fuel] for fuels in fuels2Cools for fuel in fuels if fuel not in fuels2Cools[fuels]) + sum(cellNumber2ThermalPower[cool] for cools in fuels2Cools.values() for cool in cools) for fuels2Cools in assembly];
        ###
        # Distribute missing powers
        ###
        allFuels = {fuel for fuels2Cools in assembly for fuels in fuels2Cools for fuel in fuels};
        allCools = {cool for fuels2Cools in assembly for cools in fuels2Cools.values() for cool in cools};
        missingCellNumbers = set(cellNumber2ThermalPower.keys()) - (allFuels | allCools);
        if missingCellNumbers:
            missingPower = sum(cellNumber2ThermalPower[cellNumber] for cellNumber in missingCellNumbers);
            PrintNow('> Distributing {:.0f} Wth from cell #\'s {:s} among {:d} cells in assembly #{:d}'.format(missingPower, ' '.join(str(missingCellNumber) for missingCellNumber in missingCellNumbers), axialZones, assemblyIndex));
            missingPower /= axialZones;
            axialPowers = [axialPower + missingPower for axialPower in axialPowers];
        ###
        # Slice axial power array;
        ###
        zoneSlices = 500;
        axialPowers = Array([axialPower / zoneSlices for axialPower in axialPowers for index in range(zoneSlices)]);
        ###
        # Convert axial powers Wth -> kWth
        ###
        axialPowers /= 1e3;
        ###
        # Initialize axial quality, void fraction, and density
        ###
        axialQualitys = Zeros(axialPowers.shape);
        axialVoidFractions = Zeros(axialPowers.shape);
        axialMassDensitys = Zeros(axialPowers.shape);
        ###
        # Determine the locations of the onset of boiling and end of heating
        ###
        onsetIndex = NonZero(axialPowers.cumsum() / steam.massFlowRate >= (steam.enthalpyLiquid - steam.enthalpyInlet))[0][0];
        ###
        for endIndex in range(len(assembly)):
            fuels2Cools = assembly[-(endIndex + 1)];
            if set(next(fuels for fuels in fuels2Cools)) != set(next(cools for cools in fuels2Cools.values())):
                break;
            endIndex = None;
        ###
        if endIndex is None:
            endIndex = 0;
        endIndex = (axialZones - endIndex) * zoneSlices;
        ###
        onePhaseSlice = slice(0, onsetIndex);
        twoPhaseSlice = slice(onsetIndex, axialZones * zoneSlices);
        ###
        # Calculate axial qualities
        ###
        latentHeat = steam.enthalpyVapor - steam.enthalpyLiquid;
        axialQualitys[twoPhaseSlice] = Array([axialPowers[twoPhaseSlice] / steam.massFlowRate / latentHeat]).cumsum();
        ###
        # Calculate axial void fractions
        ###
        voidFractionCorrelation = self.GetParameter('voidFractionCorrelation');
        ###
        if voidFractionCorrelation in ('bestion', ):
            VoidFractionCorrelation = VoidFractionBestion;
        elif voidFractionCorrelation in ('lpg', 'bestest', 'liao'):
            VoidFractionCorrelation = VoidFractionLPG;
        elif voidFractionCorrelation in ('relap', ):
            VoidFractionCorrelation = VoidFractionRELAP;
        elif voidFractionCorrelation in ('hom', 'homogeneous'):
            VoidFractionCorrelation = VoidFractionHomogeneous;
        elif voidFractionCorrelation in ('zivi', ):
            VoidFractionCorrelation = VoidFractionZivi;
        elif voidFractionCorrelation in ('wallis', ):
            VoidFractionCorrelation = VoidFractionWallis;
        elif voidFractionCorrelation in ('lm', 'lockhart', 'martinelli'):
            VoidFractionCorrelation = VoidFractionLM;
        elif voidFractionCorrelation in ('thom', ):
            VoidFractionCorrelation = VoidFractionThom;
        elif voidFractionCorrelation in ('baroczy', ):
            VoidFractionCorrelation = VoidFractionBaroczy;
        else:
            raise ValueError('Void fraction correlation `{}\' is unrecognized'.format(voidFractionCorrelation));
        axialVoidFractions[twoPhaseSlice] = VoidFractionCorrelation(steam, axialQualitys[twoPhaseSlice]);
        ###
        # Calculate axial mass densitys
        # Linearly interpolate density until boiling onset
        ###
        axialMassDensitys[onePhaseSlice] = steam.densityInlet + Array([(index / onsetIndex) * (steam.densityLiquid - steam.densityInlet) for index in range(onsetIndex)]);
        axialMassDensitys[twoPhaseSlice] = axialVoidFractions[twoPhaseSlice] * steam.densityVapor + (1 - axialVoidFractions[twoPhaseSlice]) * steam.densityLiquid;
        ###
        # Construct slice flow lengths
        ###
        flowLengths = [flowLength / zoneSlices for flowLength in self.GetParameter('coolantFlowLengths') for index in range(zoneSlices)];
        ###
        # Calculate critical quality and critical power ratio
        ###
        criticalPowerRatioCorrelation = self.GetParameter('criticalPowerRatioCorrelation');
        ###
        if criticalPowerRatioCorrelation in ('m-cise', ):
            CriticalPowerRatioCorrelation = CriticalPowerRatioMITCISE4;
        elif criticalPowerRatioCorrelation in ('h-cise', ):
            CriticalPowerRatioCorrelation = CriticalPowerRatioHitachiCISE4;
        else:
            raise ValueError('Critical power ratio correlation `{}\' is unrecognized'.format(criticalPowerRatioCorrelation));
        axialCriticalQualitys, axialCriticalPowerRatios = CriticalPowerRatioCorrelation(steam, axialPowers, flowLengths, endIndex);
        ###
        # Determine the minimum critical power ratio, its quality, and its location
        ###
        from numpy import nanargmin as NanArgMin;
        ###
        CPR = Array([element for element in axialCriticalPowerRatios]);
        CPR[NonZero(CPR == 0)] = None;
        ###
        # Find initial CPR peak to ignore
        ###
        for peakIndex in range(len(CPR) - 1):
            if CPR[peakIndex + 1] < CPR[peakIndex]:
                break;
            ###
            peakIndex = None;
        if peakIndex is None:
            ###
            # If the CPR monotonically increases, fall back onto an a priori index
            ###
            Warning('There is no valid MCPR ... the CPR at the fallback location is chosen instead');
            peakIndex = self.GetParameter('criticalPowerRatioFallbackIndex') * zoneSlices;
        ###
        troughIndex = peakIndex + NanArgMin(CPR[peakIndex : ]);
        ###
        minimumCriticalPowerRatio = axialCriticalPowerRatios[troughIndex];
        minimumCriticalPowerRatioLocation = sum(flowLengths[ : troughIndex]);
        minimumCriticalPowerRatioQuality = axialCriticalQualitys[troughIndex];
        ###
        # Calculate pressure drop
        ###
        pressureDropCorrelation = self.GetParameter('pressureDropCorrelation');
        ###
        if pressureDropCorrelation in ('epri', 'reddy', 'vipre', 'cobra'):
            PressureDropCorrelation = PressureDropEPRI;
        else:
            raise ValueError('Pressure drop correlation `{}\' is unrecognized'.format(pressureDropCorrelation));
        axialPressureDrops = PressureDropCorrelation(steam, axialQualitys, axialVoidFractions, axialMassDensitys, flowLengths);
        ###
        # Collapse axial power, quality, void fraction, density, and pressure drop arrays
        ###
        def Collapse(array, indexs, jndexs):
            return Array([array[(index) * jndexs : (index + 1) * jndexs].mean() for index in range(indexs)]);
        ###
        axialPowers = Collapse(axialPowers, axialZones, zoneSlices) * zoneSlices;
        axialQualitys = Collapse(axialQualitys, axialZones, zoneSlices);
        axialVoidFractions = Collapse(axialVoidFractions, axialZones, zoneSlices);
        axialMassDensitys = Collapse(axialMassDensitys, axialZones, zoneSlices);
        axialPressureDrops = Collapse(axialPressureDrops, axialZones, zoneSlices);
        finePositionCPRs = [(sum(flowLengths[ : index]), axialCriticalPowerRatios[index]) for index in range(len(axialCriticalPowerRatios))];
        ###
        # Convert axial power kWth -> Wth;
        # Convert density kg/m³ -> g/cc;
        # Convert pressure drop Pa -> MPa
        ###
        axialPowers *= 1e3;
        axialMassDensitys /= 1e3;
        axialPressureDrops /= 1e6;
        ###
        # Cell # -> mass density
        ### # FIXME Fix for multiple coolant cells
        cellNumber2MassDensity = {cellNumbers[index] : axialMassDensitys[index] for index in range(len(cellNumbers))};
        ###
        # Average previous and current water density estimates
        ###
        theta = self.GetParameter('coolantDensityDampingCoefficient');
        for cellNumber, massDensity in cellNumber2MassDensity.items():
            cellNumber2MassDensity[cellNumber] = theta * massDensity + (1 - theta) * cellNumber2PreviousMassDensity[cellNumber];
        ###
        # Set bypass density to that of the inlet
        ###
        inletMassDensity = cellNumber2MassDensity[next(iter(cellNumbers))];
        cellNumber2MassDensity.update({cellNumber : inletMassDensity for cellNumber in self.GetParameter('coolantBypassCells')});
        ###
        # Calculate convergence norm
        ###
        relativeDifferences = Array([abs(cellNumber2MassDensity[cellNumber] / cellNumber2PreviousMassDensity[cellNumber] - 1) for cellNumber in cellNumbers + self.GetParameter('coolantBypassCells')]);
        ###
        normType = self.GetParameter('thermalHydraulicConvergenceNormType');
        if normType in ('1', 'one'):
            norm = relativeDifferences.mean();
            normCharacter = '1';
        elif normType in ('2', 'two'):
            norm = (relativeDifferences ** 2.).mean() ** 0.5;
            normCharacter = '2';
        elif normType in ('inf', 'infinite', 'infinity'):
            norm = relativeDifferences.max();
            normCharacter = '∞';
        ###
        # If unconverged, signal transport file update
        ###
        tolerance = self.GetParameter('thermalHydraulicConvergenceTolerance');
        ###
        if norm > tolerance:
            PrintNow('> Coolant density {}-norm {:.1%} > {:.1%} ... assembly #{:d} needs updating for {}'.format(normCharacter, norm, tolerance, assemblyIndex, self.GetDepletionString()));
            ###
            # Record the need for updates
            ###
            transportOutputFile.ResetNewput();
        else:
            PrintNow('> Coolant density {}-norm {:.1%} ≤ {:.1%} ... assembly #{:d} has converged for {}'.format(normCharacter, norm, tolerance, assemblyIndex, self.GetDepletionString()));
        ###
        boilingCalculation = BoilingCalculation(cellNumbers = cellNumbers, cellNumber2PreviousMassDensity = cellNumber2PreviousMassDensity, cellNumber2MassDensity = cellNumber2MassDensity, axialPowers = axialPowers, axialQualitys = axialQualitys, axialVoidFractions = axialVoidFractions, finePositionCPRs = finePositionCPRs, minimumCriticalPowerRatio = minimumCriticalPowerRatio, minimumCriticalPowerRatioQuality = minimumCriticalPowerRatioQuality, minimumCriticalPowerRatioLocation = minimumCriticalPowerRatioLocation, criticalPowerRatioLimit = self.GetParameter('criticalPowerRatioLimit'), flowLengths = self.GetParameter('coolantFlowLengths'), axialPressureDrops = axialPressureDrops, transportOutputFile = transportOutputFile);
        if self.GetIsVerbose():
            PrintNow(boilingCalculation);
        ###
        assemblyIndex2VoidFractionCalculation[assemblyIndex] = boilingCalculation;
        ###
        assemblyIndex += 1;
    ### # FIXME Multiple assemblies!?!
    return assemblyIndex2VoidFractionCalculation;

###
### Replacement for DepletionCalculation methods
###

###
# DepletionCalculation.ProcessFuel()
###
ProcessFuel = lambda self : RbwrThRecycle(self.GetOriginalTransportFile(), McnpInputFile(self.GetFileName('i', withoutTH = True)));
###
# DepletionCalculation.MultiplicationFactor()
###
MultiplicationFactor = MultiBatchCoreKeffEoc;
###
# DepletionCalculation.UpdateCoolantDensitys()
###
UpdateCoolantDensitys = RbwrThBoilingCalculation;

###
### Offline helper functions
###

###
# Coolant density calculation
### # FIXME Implement this?  We will probably have to strip out the meat of RbwrThBoilingCalculation and point to that
def UpdateCoolantDensitysOffline():
    UpdateCoolantDensitys;
    ###
    return;
###
# Process fuel
###
def ProcessFuelOffline(bocFileName, eocFileName, newFileName):
    newInputFile = RbwrThRecycle(McnpInputFile(bocFileName), McnpInputFile(eocFileName));
    ###
    WriteFile(newFileName, newInputFile.GetNewputRaw());
    ###
    return;
