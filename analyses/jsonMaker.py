import os,analysis,calculables,steps,samples

class jsonMaker(analysis.analysis) :
    def listOfSteps(self,params) :
        return [ steps.Print.progressPrinter(2,300),
                 steps.Other.jsonMaker(),
                 ]

    def listOfCalculables(self,params) :
        return calculables.zeroArgs()

    def listOfSamples(self,params) :
        from samples import specify
        jw = calculables.Other.jsonWeight("/home/hep/elaird1/supy/Cert_160404-166502_7TeV_PromptReco_Collisions11_JSON.txt", acceptFutureRuns = False) #485/pb        
        
        out = []
        #out += specify(names = "Photon.Run2011A-May10ReReco-v1.AOD.Henning.L1", weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Ted1.L1",     weights = jw)
        #out += specify(names = "Photon.Run2011A-PromptReco-v4.AOD.Ted2.L1",     weights = jw)
        
        out += specify(names = [ "SingleMu.Run2011A-May10-v1.FJ.Burt",
                                 "SingleMu.Run2011A-PR-v4.FJ.Burt1",
                                 "SingleMu.Run2011A-PR-v4.FJ.Burt2",
                                 "SingleMu.Run2011A-PR-v4.FJ.Burt3",
                                 ]) # no json filtering necessary, golden json used
        return out

    def listOfSampleDictionaries(self) :
        return [samples.jetmet, samples.muon, samples.photon, samples.electron]

    def mainTree(self) :
        return ("lumiTree","tree")

    def otherTreesToKeepWhenSkimming(self) :
        return []
