import numpy,math,utils,minuit
import ROOT as r

###########################
class minuitLeptonicTop(object) :
    '''Fit jet, lepton, and missing energy to the hypothesis t-->blv.'''

    def __init__(self, bP4, bResolution, muP4, nuX, nuY, nuErr, 
                 massT = 172.0, widthT = 13.1/2, massW = 80.4, zPlus = True ) :

        T,B,mu,nu = tuple( utils.vessel() for i in range(4) )

        T.mass = massT ;
        T.invWidth2 = widthT**(-2);  
        B.raw = bP4;
        B.invRes2 = bResolution**(-2); 
        mu.P4 = muP4

        phi = math.atan2(2*nuErr.xy, nuErr.xx - nuErr.yy)
        nu.cos = math.cos(phi) ; nu.sin = math.sin(phi)
        nu.invSigmaS2 = 1.0 / ( nuErr.xx*nu.cos**2 - 2*nuErr.xy*nu.cos*nu.sin + nuErr.yy*nu.sin**2 )
        nu.invSigmaL2 = 1.0 / ( nuErr.xx*nu.sin**2 + 2*nuErr.xy*nu.cos*nu.sin + nuErr.yy*nu.cos**2 )
        nu.rawX = nuX ; nu.rawY = nuY
        nu.fitted = utils.LorentzV()
        
        for item in ["T","B","mu","nu","massW","zPlus"] : setattr(self,item,eval(item))
        self.cache()
        self.fit()

    def cache(self) :
        self.B.rawX = self.B.raw.X()
        self.B.rawY = self.B.raw.Y()
        self.mu.X = self.mu.P4.X()
        self.mu.Y = self.mu.P4.Y()
        self.mu.Z = self.mu.P4.Z()
        self.mu.E = self.mu.P4.E()
        self.mu.T2 = self.mu.P4.Perp2()
        self.mu.T = math.sqrt(self.mu.T2)
        self.mu.phi = self.mu.P4.Phi()

    def fit(self) :
        def fnc(db,dS,dL) :
            nuX = self.nu.rawX  -  db * self.B.rawX  +  dS * self.nu.cos + dL * self.nu.sin
            nuY = self.nu.rawY  -  db * self.B.rawY  -  dS * self.nu.sin + dL * self.nu.cos
            self.setFittedNu(nuX,nuY)
            self.B.fitted = self.B.raw * (1+db)

            T = self.mu.P4 + self.nu.fitted + self.B.fitted
            return ( self.T.invWidth2 * (self.T.mass - T.M())**2 +
                     self.B.invRes2 * db**2 +
                     self.nu.invSigmaS2 * dS**2 +
                     self.nu.invSigmaL2 * dL**2 )

        m = minuit.minuit(fnc, db=0, dS=0, dL=0)
        m.mnexcm("MIGRAD", 500, 1)
        fitted = m.values()
        self.chi2_ = fnc(**fitted)
        if 0 <= self.discriminant :  return

        def fnc(db,phi) :
            self.B.fitted = self.B.raw * (1+db)
            self.setBoundaryFittedNu(phi)
            dX = self.nu.fitted.X() - self.nu.rawX + db * self.B.rawX
            dY = self.nu.fitted.Y() - self.nu.rawY + db * self.B.rawY
            dS = dX * self.nu.cos - dY * self.nu.sin
            dL = dX * self.nu.sin + dY * self.nu.cos

            T = self.mu.P4 + self.nu.fitted + self.B.fitted
            return ( self.T.invWidth2 * (self.T.mass - T.M())**2 +
                     self.B.invRes2 * db**2 +
                     self.nu.invSigmaS2 * dS**2 +
                     self.nu.invSigmaL2 * dL**2 )
        m = minuit.minuit(fnc, db=0, phi = math.atan2(self.nu.rawY, self.nu.rawX))
        m.mnexcm("MIGRAD", 500, 1)
        fitted = m.values()
        self.chi2_ = fnc(**fitted)
        
    def setFittedNu(self,nuX,nuY) :
        P = self.massW**2 + 2* ( self.mu.X*nuX + self.mu.Y*nuY )
        self.discriminant = 1 - 4 * self.mu.T2 * (nuX**2+nuY**2) / P**2
        sign = 0 if self.discriminant < 0 else 1 if self.zPlus else -1
        nuZ = 0.5 * P / self.mu.T2 * (self.mu.Z + sign * self.mu.E * self.discriminant)
        self.nu.fitted.SetPxPyPzE(nuX,nuY,nuZ,math.sqrt(nuX**2+nuY**2+nuZ**2))

    def setBoundaryFittedNu(self,phi) :
        nuT = 0.5 * self.massW**2 / (self.mu.T * (1 - math.cos(self.mu.phi-phi)))
        self.setFittedNu(nuT*math.cos(phi), nuT*math.sin(phi))
        
    def chi2(self) : return self.chi2_
    
###########################
class minuitHadronicTop(object) :
    '''Fit three jets to the hypothesis t-->bqq.

    Index 0 is the b-jet.
    Resolutions are expected in units of sigma(pT)/pT.'''

    def __init__(self, jetP4s, jetResolutions, massT = 172.0, widthT = 13.1/2, massW = 80.4, widthW = 2.085/2 ) :
        assert len(jetP4s) == 3 == len(jetResolutions), "Please specify 3 and only 3 jets."
        J,W,T = tuple( utils.vessel() for i in range(3) )

        J.raw = jetP4s
        J.invRes2 = [ jr**(-2) for jr in jetResolutions ]

        T.mass = massT ;   T.invWidth2 = widthT**(-2)
        W.mass = massW ;   W.invWidth2 = widthW**(-2)

        for item in ["J","T","W"] : setattr(self,item,eval(item))
        self.fit()

    def fit(self) :
        def fnc(db,dp,dq) :
            d = [db,dp,dq]
            fitted = [jet*(1+delta) for delta,jet in zip(d,self.J.raw)]
            W = fitted[1]+fitted[2]
            T = fitted[0]+W
            return ( self.T.invWidth2 * (self.T.mass - T.M())**2 +
                     self.W.invWidth2 * (self.W.mass - W.M())**2 +
                     sum([r*delta**2 for delta,r in zip(d,self.J.invRes2)]) )

        m = minuit.minuit(fnc)        
        m.mnexcm("MIGRAD", 500, 1)
        fitted = m.values()
        self.chi2_ = fnc(**fitted)
        self.J.delta = [fitted[s] for s in ['db','dp','dq']]
        self.J.fitted = [jet*(1+delta) for delta,jet in zip(self.J.delta,self.J.raw)]

    def chi2(self) : return self.chi2_
    
###########################
class linearHadronicTop(object) :
    '''Fit three jets to the hypothesis t-->bqq.

    Index 0 is the b-jet.
    Resolutions are expected in units of sigma(pT)/pT.'''

    def chi2(self, key = None) :
        if key==None : return sum( [self.chi2(key) for key in ["J","W","T"]])
        elif key=="J": return sum([ d*d*r for d,r in zip( self.J.delta, self.J.invRes2 ) ])
        elif key=="W": return self.W.invWidth2 * ( self.W.mass - (self.J.fitted[1] + self.J.fitted[2]).M() )**2
        elif key=="T": return self.T.invWidth2 * ( self.T.mass - sum( self.J.fitted, utils.LorentzV()).M() )**2

    def __init__(self, jetP4s, jetResolutions, massT = 172.0, widthT = 13.1/2, massW = 80.4, widthW = 2.085/2 ) :
        assert len(jetP4s) == 3 == len(jetResolutions), "Please specify 3 and only 3 jets."
        J,W,T = tuple( utils.vessel() for i in range(3) )

        J.raw = jetP4s
        J.invRes2 = [ jr**(-2) for jr in jetResolutions ]
        m2 = [(J.raw[i]+J.raw[j]).M2() for i,j in [tuple(set([0,1,2])-set([k])) for k in [0,1,2]]]

        T.rawMass2 = sum( jetP4s, utils.LorentzV()).M2()
        T.mass = massT ;   T.invWidth2 = widthT**(-2) ;   T.R = massT / math.sqrt(T.rawMass2) ; T.L = 0.5 * T.invWidth2 / T.rawMass2
        W.mass = massW ;   W.invWidth2 = widthW**(-2) ;   W.R = massW / math.sqrt(m2[0])      ; W.Lambda =  W.invWidth2 * m2[0]     

        for item in ["J","T","W","m2"] : setattr(self,item,eval(item))
        J.delta = numpy.linalg.solve( self.matrix(), -self.constants() )
        J.fitted = [ j * (1+d) for j,d in zip(J.raw,J.delta) ]

    def matrix(self) :
        m = []
        m.append([     self.element(0,i) for i in range(3)       ])
        m.append([ m[0][1], self.element(1,1), self.element(1,2) ])
        m.append([ m[0][2],           m[1][2], self.element(2,2) ])
        return numpy.array(m)

    def constants(self) : return numpy.array([self.constant(i) for i in range(3)])
    def constant(self, i, key = None):
        if key==None : return sum( [self.constant(i,key) for key in ["W","T"]] )
        elif key=="W": return ( 1 - self.W.R ) * self.W.Lambda
        elif key=="T": return ( 1 - self.T.R ) * self.T.invWidth2 * (sum(self.m2)-self.m2[i])

    def element(self,i,j, key = None) :
        if key==None : return sum( [self.element(i,j,key) for key in ["J","W","T"]] )
        elif key=="J": return [ 0, 2*self.J.invRes2[i] ][i==j]
        elif key=="W": return self.W.Lambda * [ 1-0.5*self.W.R,  0.5*self.W.R ][i==j] if i and j else 0
        elif key=="T":
            T = self.T
            sumM2 = sum(self.m2)
            m2_i = sumM2 - self.m2[i]
            m2_j = sumM2 - self.m2[j]
            term2 = [(1-T.R) * T.invWidth2 * (sumM2 - self.m2[i] - self.m2[j] ) , 0 ][i==j]
            return term2  +  m2_i * m2_j * T.L * T.R


###########################
class linearWbTop(object) :
    '''Fit the b jet in the hypothesis t-->bW'''

    def chi2(self) :
        return ( self.b.invRes2 * self.b.delta**2 +
                 self.topInvWidth2 * (self.massTop - (self.b.fitted+self.W).M())**2 )

    def __init__(self,bjet,bresolution,W,
                 massTop=172.0,widthTop=13.1/2) :

        rawTop2 = (bjet+W).M2()
        topInvWidth2 = widthTop**(-2)

        R = massTop / math.sqrt(rawTop2)
        A = (rawTop2 - W.M2()) * topInvWidth2
        B = rawTop2 * topInvWidth2

        b = utils.vessel()
        b.raw = bjet
        b.invRes2 = bresolution**(-2)
        b.delta = A*(R-1) / (2*b.invRes2 + 0.5*R*A*A/B)
        b.fitted = b.raw * (1+b.delta)

        for item in ['b','W','massTop','topInvWidth2'] : setattr(self,item,eval(item))

###########################
class minuitMuNuW(object) :

    def __init__(self, muP4, nuX, nuY, covErr, massW=80.4) :
        self.nuP4 = utils.LorentzV().SetPxPyPzE(nuX,nuY,0.0,math.sqrt(nuX**2+nuY**2))
        for item in ['muP4','covErr','massW'] : setattr(self,item,eval(item))
        self.fittedNu = (utils.LorentzV(),utils.LorentzV())

        if 0 <= self.discriminant() : self.solve()
        else : self.fit()

    def discriminant(self) :
        self.muT2 = self.muP4.Perp2()
        self.nuT2 = self.nuP4.Perp2()
        self.P = self.massW**2 + 2 * (self.nuP4.X()*self.muP4.X() + self.nuP4.Y()*self.muP4.Y())

        self.discriminant =  1  -  4 * self.muT2 * self.nuT2 / self.P**2
        return self.discriminant

    def solve(self) :
        nuX,nuY = self.nuP4.X(), self.nuP4.Y()
        muZ,muE = self.muP4.z(), self.muP4.E()
        sqrtDisc = math.sqrt(self.discriminant)
        base = 0.5 * self.P / self.muT2
        zplus = base*(muZ+muE*sqrtDisc)
        zminus = base*(muZ-muE*sqrtDisc)
        self.fittedNu[0].SetPxPyPzE(nuX, nuY, zplus,  math.sqrt(self.nuT2 + zplus**2))
        self.fittedNu[1].SetPxPyPzE(nuX, nuY, zminus, math.sqrt(self.nuT2 + zminus**2))
        self.chi2 = 0.0

    def fit(self) :
        phi = 0.5 * math.atan2(self.covErr.xy, self.covErr.xx-self.covErr.yy) 
        R = r.Math.RotationZ(phi)
        rNuP4 = R(self.nuP4)
        rMuP4 = R(self.muP4)
        cos = R.CosAngle()
        sin = R.SinAngle()
        sigma2x = self.covErr.xx*cos**2 - 2*self.covErr.xy*cos*sin + self.covErr.yy*sin**2
        sigma2y = self.covErr.xx*sin**2 + 2*self.covErr.xy*cos*sin + self.covErr.yy*cos**2
        assert sigma2x > 0, sigma2x
        assert sigma2y > 0, sigma2y
        rnuX,rnuY = rNuP4.x(),rNuP4.y()
        rmuX,rmuY = rMuP4.x(),rMuP4.y()
        rMuPhi = rMuP4.Phi()

        muT = math.sqrt(self.muT2)
        def NUT(dphi) : return 0.5 * self.massW**2 / (muT*(1-math.cos(dphi)))

        def fnc(phi) :
            nuT = NUT(rMuPhi-phi)
            x = nuT*math.cos(phi)
            y = nuT*math.sin(phi)
            val = ( (x - rnuX)**2/sigma2x +
                    (y - rnuY)**2/sigma2y )
            return val
        
        m = minuit.minuit(fnc, phi = rNuP4.Phi() )
        if m.mnexcm("MIGRAD", 500, 1) : m.printStatus()
        fitted = m.values()
        self.chi2 = fnc(**fitted)

        nuT = NUT(rMuPhi-fitted['phi'])
        fitNuX = nuT * math.cos(fitted['phi'])
        fitNuY = nuT * math.sin(fitted['phi'])

        P = self.massW**2 + 2 * (rmuX*fitNuX + rmuY*fitNuY)
        fitNuZ = 0.5 * self.muP4.Z() * P / self.muT2
        self.fittedNu[0].SetPxPyPzE(fitNuX,fitNuY,fitNuZ,math.sqrt(fitNuX**2+fitNuY**2+fitNuZ**2))

        R.Invert()
        self.fittedNu = ( R(self.fittedNu[0]) , None )
        
