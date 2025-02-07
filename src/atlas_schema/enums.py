from __future__ import annotations

from enum import IntEnum


class ParticleType(IntEnum):
    """
    `Docstring1 <https://google.com/#1>`_.
    """

    Unknown = 0
    UnknownElectron = 1
    IsoElectron = 2
    NonIsoElectron = 3
    BkgElectron = 4
    UnknownMuon = 5
    IsoMuon = 6
    NonIsoMuon = 7
    BkgMuon = 8
    UnknownTau = 9
    IsoTau = 10
    NonIsoTau = 11
    BkgTau = 12
    UnknownPhoton = 13
    IsoPhoton = 14
    NonIsoPhoton = 15
    BkgPhoton = 16
    Hadron = 17
    Neutrino = 18
    NuclFrag = 19
    NonPrimary = 20
    GenParticle = 21
    SUSYParticle = 22
    OtherBSMParticle = 39
    BBbarMesonPart = 23
    BottomMesonPart = 24
    CCbarMesonPart = 25
    CharmedMesonPart = 26
    BottomBaryonPart = 27
    CharmedBaryonPart = 28
    StrangeBaryonPart = 29
    LightBaryonPart = 30
    StrangeMesonPart = 31
    LightMesonPart = 32
    BJet = 33
    CJet = 34
    LJet = 35
    GJet = 36
    TauJet = 37
    UnknownJet = 38


class ParticleOrigin(IntEnum):
    """
    `Docstring2 <https://google.com/#2>`_.
    """

    NonDefined = 0
    SingleElec = 1
    SingleMuon = 2
    SinglePhot = 3
    SingleTau = 4
    PhotonConv = 5
    DalitzDec = 6
    ElMagProc = 7
    Mu = 8
    TauLep = 9
    top = 10
    QuarkWeakDec = 11
    WBoson = 12
    ZBoson = 13
    Higgs = 14
    HiggsMSSM = 15
    HeavyBoson = 16
    WBosonLRSM = 17
    NuREle = 18
    NuRMu = 19
    NuRTau = 20
    LQ = 21
    SUSY = 22
    OtherBSM = 46
    LightMeson = 23
    StrangeMeson = 24
    CharmedMeson = 25
    BottomMeson = 26
    CCbarMeson = 27
    JPsi = 28
    BBbarMeson = 29
    LightBaryon = 30
    StrangeBaryon = 31
    CharmedBaryon = 32
    BottomBaryon = 33
    PionDecay = 34
    KaonDecay = 35
    BremPhot = 36
    PromptPhot = 37
    UndrPhot = 38
    ISRPhot = 39
    FSRPhot = 40
    NucReact = 41
    PiZero = 42
    DiBoson = 43
    ZorHeavyBoson = 44
    MultiBoson = 47
    QCD = 45


class PhotonID(IntEnum):
    """
    `Docstring3 <https://google.com/#3>`_.
    """

    Rhad = 10  # ClusterHadronicLeakage_Photon
    E277 = 11  # ClusterMiddleEnergy_Photon
    Reta = 12  # ClusterMiddleEratio37_Photon
    Rphi = 13  # ClusterMiddleEratio33_Photon
    Weta2 = 14  # ClusterMiddleWidth_Photon
    f1 = 15  # ClusterStripsEratio_Photon
    DeltaE = 17  # ClusterStripsDeltaE_Photon
    Wstot = 18  # ClusterStripsWtot_Photon
    fside = 19  # ClusterStripsFracm_Photon
    Ws3 = 20  # ClusterStripsWeta1c_Photon
    ERatio = 21  # ClusterStripsDEmaxs1_Photon
