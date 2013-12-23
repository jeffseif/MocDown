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
### Custom functions
###

###
# RBWR-AC recycling scheme
###
def RbwrACRecycle(bocTransportFile, eocTransportFile):
    '''Override fuel processing.''';
    ###
    # Hard code the blanket and seed cell parameters
    ###
    numberOfUpperBlanketCells = 8;
    numberOfUpperSeedCells = 12;
    numberOfInternalBlanketCells = 12;
    numberOfLowerSeedCells = 12;
    numberOfLowerBlanketCells = 12;
    ###
    firstCellNumber = 3;
    ###
    # Define the blanket and seed cell numbers
    ###
    previous = firstCellNumber;
    upperBlanketCellNumbers    = list(range(previous, previous + numberOfUpperBlanketCells));
    previous = max(upperBlanketCellNumbers) + 1;
    upperSeedCellNumbers       = list(range(previous, previous + numberOfUpperSeedCells));
    previous = max(upperBlanketCellNumbers + upperSeedCellNumbers) + 1;
    internalBlanketCellNumbers = list(range(previous, previous + numberOfInternalBlanketCells));
    previous = max(upperBlanketCellNumbers + upperSeedCellNumbers + internalBlanketCellNumbers) + 1;
    lowerSeedCellNumbers       = list(range(previous, previous + numberOfLowerSeedCells));
    previous = max(upperBlanketCellNumbers + upperSeedCellNumbers + internalBlanketCellNumbers + lowerSeedCellNumbers) + 1;
    lowerBlanketCellNumbers    = list(range(previous, previous + numberOfLowerBlanketCells));
    ###
    upperSeedVolumeFraction = 28 / (28 + 19.3);
    lowerSeedVolumeFraction = 1 - upperSeedVolumeFraction;
    ###
    # Isotopic ZA
    ###
    oxygen = 8016;
    depletedUranium = {
        92235 : 2.5e-3,
        92238 : 1 - 2.5e-3,
        };
    ###
    # Calculate the number of BOEC seed heavy-metal moles;
    # This number is conserved across recycles
    ###
    chargeMoles = sum(moles for cellNumber in upperSeedCellNumbers + lowerSeedCellNumbers for za, moles in bocTransportFile.FindCell(cellNumber).GetZa2Moles().items() if ZaIsActinide(za));
    ###
    # Construct the seed charge:
    # First, EOEC heavy metal moles are accumulated;
    # Second, any mole deficit or surplus is made up with uranium
    # Third, add twice as many oxygen moles as heavy metal moles
    ###
    za2ChargeMoles = {};
    for cellNumber in upperBlanketCellNumbers + upperSeedCellNumbers + internalBlanketCellNumbers + lowerSeedCellNumbers + lowerBlanketCellNumbers:
        for za, moles in eocTransportFile.FindCell(cellNumber).GetZa2Moles().items():
            if ZaIsActinide(za):
                try:
                    za2ChargeMoles[za] += moles;
                except KeyError:
                    za2ChargeMoles[za] = moles;
    ###
    deviation = chargeMoles - sum(za2ChargeMoles.values());
    uranium2Fraction = {za : moles for za, moles in za2ChargeMoles.items() if 92 == za // 1000};
    uranium2Fraction = {za : moles / sum(uranium2Fraction.values()) for za, moles in uranium2Fraction.items()};
    try:
        for za, fraction in uranium2Fraction.items():
            za2ChargeMoles[za] += deviation * fraction;
    except KeyError:
        for za, fraction in uranium2Fraction.items():
            za2ChargeMoles[za] = deviation * fraction;
    assert(all(za2ChargeMoles[za] > 0 for za in depletedUranium));
    ###
    za2ChargeMoles[oxygen] = 2 * chargeMoles;
    ###
    # Distribute the seed charge:
    # First, split moles evenly between seed cells
    # Second, match BOEC moles for each cell by adjusting depleted urania moles
    ###
    cellNumber2Za2ChargeMoles = {cellNumber : {za : moles * upperSeedVolumeFraction / numberOfUpperSeedCells for za, moles in za2ChargeMoles.items()} for cellNumber in upperSeedCellNumbers};
    cellNumber2Za2ChargeMoles.update({cellNumber : {za : moles * lowerSeedVolumeFraction / numberOfUpperSeedCells for za, moles in za2ChargeMoles.items()} for cellNumber in lowerSeedCellNumbers});
    ###
    for cellNumber in upperSeedCellNumbers + lowerSeedCellNumbers:
        bocCell = bocTransportFile.FindCell(cellNumber);
        deviation = bocCell.GetMoles() - sum(cellNumber2Za2ChargeMoles[cellNumber].values());
        try:
            for za, fraction in depletedUranium.items():
                cellNumber2Za2ChargeMoles[cellNumber][za] += deviation * fraction * 1 / 3;
            cellNumber2Za2ChargeMoles[cellNumber][oxygen] += deviation * 2 / 3;
        except KeyError:
            for za, fraction in depletedUranium.items():
                cellNumber2Za2ChargeMoles[cellNumber][za] = deviation * fraction * 1 / 3;
            cellNumber2Za2ChargeMoles[cellNumber][oxygen] = deviation * 2 / 3;
        assert(all(cellNumber2Za2ChargeMoles[cellNumber][za] > 0 for za in depletedUranium));
    ###
    # Distribute the blanket charge:
    # Simply grab the BOEC moles
    ###
    cellNumber2Za2ChargeMoles.update({cellNumber : bocTransportFile.FindCell(cellNumber).GetZa2Moles() for cellNumber in upperBlanketCellNumbers + internalBlanketCellNumbers + lowerBlanketCellNumbers});
    ###
    # Recharge cells
    ###
    for cellNumber in upperBlanketCellNumbers + upperSeedCellNumbers + internalBlanketCellNumbers + lowerSeedCellNumbers + lowerBlanketCellNumbers:
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
### Replacement for DepletionCalculation methods
###

###
# DepletionCalculation.ProcessFuel()
###
ProcessFuel = lambda self : RbwrACRecycle(self.GetOriginalTransportFile(), McnpInputFile(self.GetFileName('i', withoutTH = True)));

###
### Offline helper functions
###

###
# Process fuel
###
def ProcessFuelOffline(bocFileName, eocFileName, newFileName):
    '''Offline fuel processing helper.''';
    newInputFile = RbwrACRecycle(McnpInputFile(bocFileName), McnpInputFile(eocFileName));
    ###
    WriteFile(newFileName, newInputFile.GetNewputRaw());
    ###
    return;
