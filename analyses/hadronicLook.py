#!/usr/bin/env python

import os,analysis,utils,steps,calculables,calculablesJet

def makeSteps() :
    jets=("ak5Jet","Pat")
    #jets=("ak5JetJPT","Pat")
    #jets=("ak5JetPF","Pat")
    
    metCollection="met"
    metSuffix="Calo"
    metSuffix=jets[0][:3].upper()
    metSuffix+="TypeII"
    #metSuffix="PF"
    
    leptonSuffix="Pat"
    #leptonSuffix="PF"
    
    listOfSteps=[
        steps.progressPrinter(),
        
        steps.ptHatHistogrammer(),
        steps.jetPtSelector(jets,80.0,0),
        #steps.jetPtSelector(jets,40.0,1),
        steps.leadingUnCorrJetPtSelector( [jets],80.0 ),
        steps.hltFilter("HLT_Jet50U"),
        steps.hltPrescaleHistogrammer(["HLT_ZeroBias","HLT_Jet15U","HLT_Jet30U","HLT_Jet50U","HLT_MET45"]),

        steps.minNCleanJetEventFilter(jets,2),
        steps.maxNOtherJetEventFilter(jets,0),
        steps.cleanJetPtHistogrammer(jets),
        steps.hbheNoiseFilter(),
        steps.cleanJetHtMhtHistogrammer(jets),
        #steps.crockVariablePtGreaterFilter(100.0,jetCollection+"Mht"+jetSuffix),
        
        steps.variableGreaterFilter(300.0,jets[0]+"SumPt"+jets[1]),
        steps.alphaHistogrammer(jets),
        
        steps.variableGreaterFilter(0.55,jets[0]+"AlphaT"+jets[1]),
        #steps.displayer(jets[0],jets[1],metCollection,metSuffix,leptonSuffix,genJetCollection="ak5Jet",outputDir="/vols/cms02/%s/tmp/"%os.environ["USER"],scale=200.0),
        #steps.eventPrinter(),
        #steps.jetPrinter(jets),
        #steps.htMhtPrinter(jets),
        #steps.nJetAlphaTPrinter(jets)
        ]
    return listOfSteps

def makeCalculables() :
    jetTypes = [("ak5Jet","Pat"),("ak5JetJPT","Pat"),("ak5JetPF","Pat")]
    listOfCalculables = calculables.zeroArgs()
    listOfCalculables += [ calculablesJet.indices( collection = jetType, ptMin = 20.0, etaMax = 3.0, flagName = "JetIDloose") for jetType in jetTypes]
    listOfCalculables += [ calculablesJet.sumPt(   collection = jetType)                                                      for jetType in jetTypes]
    listOfCalculables += [ calculablesJet.sumP4(   collection = jetType)                                                      for jetType in jetTypes]
    listOfCalculables += [ calculablesJet.deltaPseudoJet( collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.alphaT(         collection = jetType) for jetType in jetTypes ]
    listOfCalculables += [ calculablesJet.diJetAlpha(     collection = jetType) for jetType in jetTypes ]
    return listOfCalculables

#def dummy(location,itemsToSkip=[],sizeThreshold=0,pruneList=True,nMaxFiles=-1) :
#    return []
#utils.fileListFromSrmLs=dummy

a=analysis.analysis(name = "hadronicLook",
                    outputDir = "/vols/cms02/%s/tmp/"%os.environ["USER"],
                    listOfSteps = makeSteps(),
                    listOfCalculables = makeCalculables()
                    )

# a.addSample( sampleName="JetMETTau.Run2010A", nMaxFiles = -1, nEvents = -1, lumi = 0.012+0.120+0.1235,#/pb
#              listOfFileNames = utils.fileListFromDisk(location="/vols/cms02/elaird1/06_skims/take3/",pruneList=False) )

# a.addSample( sampleName="qcd_py_pt30", nMaxFiles = 6, nEvents = -1, xs = 6.041e+07,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_06_24_18_09_51/") )

a.addSample( sampleName="qcd_py_pt80", nMaxFiles=1, nEvents=1000, xs = 9.238e+05,#pb
             listOfFileNames=utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_00_55_17/"))

# a.addSample( sampleName="qcd_py_pt170", nMaxFiles = 6, nEvents = -1, xs = 2.547e+04,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/gouskos//ICF/automated/2010_07_06_01_33_23/") )

# a.manageNonBinnedSamples(ptHatLowerThresholdsAndSampleNames=[(30,"qcd_py_pt30"),(80,"qcd_py_pt80"),(170,"qcd_py_pt170")],mergeIntoOnePlot=True,mergeName="qcd_py")

# a.addSample( sampleName="tt_tauola_mg", nMaxFiles = 6, nEvents = -1, xs = 95.0,#pb
#              listOfFileNames = utils.getCommandOutput2("ls /vols/cms01/mstoye/ttTauola_madgraph_V11tag/SusyCAF_Tree*.root | grep -v 4_2").split("\n") )

# a.addSample( sampleName="gammajets_mg_pt40_100", nMaxFiles = 1, nEvents = -1, xs = 23620,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb//ICF/automated/2010_07_26_15_14_40//PhotonJets_Pt40to100-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

# a.addSample( sampleName="gammajets_mg_pt100_200", nMaxFiles = 6, nEvents = -1, xs = 3476,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt100to200-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

# a.addSample( sampleName="gammajets_mg_pt200", nMaxFiles = 6, nEvents = -1, xs = 485,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/arlogb/ICF/automated/2010_07_26_15_14_40/PhotonJets_Pt200toInf-madgraph.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

# a.addSample( sampleName="z_inv_mg", nMaxFiles = 6, nEvents = -1, xs=4500.0,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/zph04/ICF/automated/2010_07_14_11_52_58/",
#                                                        itemsToSkip=["14_3.root"]))

# a.addSample( sampleName="z_jets_mg", nMaxFiles = 6, nEvents = -1, xs=2400.0,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_07_05_22_43_20/", pruneList=False) )

# a.addSample( sampleName="w_jets_mg", nMaxFiles = 6, nEvents = -1, xs=24170.0,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/jad/ICF/automated//2010_06_18_22_33_23/") )

# a.addSample( sampleName="lm0", nMaxFiles = -1, nEvents = -1, xs = 38.93,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_16_12_54_00/LM0.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/"))

# a.addSample( sampleName="lm1", nMaxFiles = -1, nEvents = -1, xs = 4.888,#pb
#              listOfFileNames = utils.fileListFromSrmLs(location="/pnfs/hep.ph.ic.ac.uk/data/cms/store/user/bainbrid/ICF/automated/2010_07_12_17_52_54/LM1.Spring10-START3X_V26_S09-v1.GEN-SIM-RECO/") )

a.loop( nCores = 6 )
#a.plot( mergeAllMc=False )
