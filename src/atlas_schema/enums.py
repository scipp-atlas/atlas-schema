from __future__ import annotations

from enum import IntEnum

from atlas_schema.typing_compat import Annotated


# https://gitlab.cern.ch/atlas/athena/-/blob/74f43ff0910edb2a2bd3778880ccbdad648dc037/Generators/TruthUtils/TruthUtils/TruthClasses.h#L51-103
class ParticleType(IntEnum):
    Unknown: Annotated[int, "Unknown"] = 0
    UnknownElectron: Annotated[int, "UnknownElectron"] = 1
    IsoElectron: Annotated[int, "IsoElectron"] = 2
    NonIsoElectron: Annotated[int, "NonIsoElectron"] = 3
    BkgElectron: Annotated[int, "BkgElectron"] = 4
    UnknownMuon: Annotated[int, "UnknownMuon"] = 5
    IsoMuon: Annotated[int, "IsoMuon"] = 6
    NonIsoMuon: Annotated[int, "NonIsoMuon"] = 7
    BkgMuon: Annotated[int, "BkgMuon"] = 8
    UnknownTau: Annotated[int, "UnknownTau"] = 9
    IsoTau: Annotated[int, "IsoTau"] = 10
    NonIsoTau: Annotated[int, "NonIsoTau"] = 11
    BkgTau: Annotated[int, "BkgTau"] = 12
    UnknownPhoton: Annotated[int, "UnknownPhoton"] = 13
    IsoPhoton: Annotated[int, "IsoPhoton"] = 14
    NonIsoPhoton: Annotated[int, "NonIsoPhoton"] = 15
    BkgPhoton: Annotated[int, "BkgPhoton"] = 16
    Hadron: Annotated[int, "Hadron"] = 17
    Neutrino: Annotated[int, "Neutrino"] = 18
    NuclFrag: Annotated[int, "NuclFrag"] = 19
    NonPrimary: Annotated[int, "NonPrimary"] = 20
    GenParticle: Annotated[int, "GenParticle"] = 21
    SUSYParticle: Annotated[int, "SUSYParticle"] = 22
    OtherBSMParticle: Annotated[int, "OtherBSMParticle"] = 39
    BBbarMesonPart: Annotated[int, "BBbarMesonPart"] = 23
    BottomMesonPart: Annotated[int, "BottomMesonPart"] = 24
    CCbarMesonPart: Annotated[int, "CCbarMesonPart"] = 25
    CharmedMesonPart: Annotated[int, "CharmedMesonPart"] = 26
    BottomBaryonPart: Annotated[int, "BottomBaryonPart"] = 27
    CharmedBaryonPart: Annotated[int, "CharmedBaryonPart"] = 28
    StrangeBaryonPart: Annotated[int, "StrangeBaryonPart"] = 29
    LightBaryonPart: Annotated[int, "LightBaryonPart"] = 30
    StrangeMesonPart: Annotated[int, "StrangeMesonPart"] = 31
    LightMesonPart: Annotated[int, "LightMesonPart"] = 32
    BJet: Annotated[int, "BJet"] = 33
    CJet: Annotated[int, "CJet"] = 34
    LJet: Annotated[int, "LJet"] = 35
    GJet: Annotated[int, "GJet"] = 36
    TauJet: Annotated[int, "TauJet"] = 37
    UnknownJet: Annotated[int, "UnknownJet"] = 38


# https://gitlab.cern.ch/atlas/athena/-/blob/74f43ff0910edb2a2bd3778880ccbdad648dc037/Generators/TruthUtils/TruthUtils/TruthClasses.h#L51-103
class ParticleOrigin(IntEnum):
    NonDefined: Annotated[int, "NonDefined"] = 0
    SingleElec: Annotated[int, "SingleElec"] = 1
    SingleMuon: Annotated[int, "SingleMuon"] = 2
    SinglePhot: Annotated[int, "SinglePhot"] = 3
    SingleTau: Annotated[int, "SingleTau"] = 4
    PhotonConv: Annotated[int, "PhotonConv"] = 5
    DalitzDec: Annotated[int, "DalitzDec"] = 6
    ElMagProc: Annotated[int, "ElMagProc"] = 7
    Mu: Annotated[int, "Mu"] = 8
    TauLep: Annotated[int, "TauLep"] = 9
    top: Annotated[int, "top"] = 10
    QuarkWeakDec: Annotated[int, "QuarkWeakDec"] = 11
    WBoson: Annotated[int, "WBoson"] = 12
    ZBoson: Annotated[int, "ZBoson"] = 13
    Higgs: Annotated[int, "Higgs"] = 14
    HiggsMSSM: Annotated[int, "HiggsMSSM"] = 15
    HeavyBoson: Annotated[int, "HeavyBoson"] = 16
    WBosonLRSM: Annotated[int, "WBosonLRSM"] = 17
    NuREle: Annotated[int, "NuREle"] = 18
    NuRMu: Annotated[int, "NuRMu"] = 19
    NuRTau: Annotated[int, "NuRTau"] = 20
    LQ: Annotated[int, "LQ"] = 21
    SUSY: Annotated[int, "SUSY"] = 22
    OtherBSM: Annotated[int, "OtherBSM"] = 46
    LightMeson: Annotated[int, "LightMeson"] = 23
    StrangeMeson: Annotated[int, "StrangeMeson"] = 24
    CharmedMeson: Annotated[int, "CharmedMeson"] = 25
    BottomMeson: Annotated[int, "BottomMeson"] = 26
    CCbarMeson: Annotated[int, "CCbarMeson"] = 27
    JPsi: Annotated[int, "JPsi"] = 28
    BBbarMeson: Annotated[int, "BBbarMeson"] = 29
    LightBaryon: Annotated[int, "LightBaryon"] = 30
    StrangeBaryon: Annotated[int, "StrangeBaryon"] = 31
    CharmedBaryon: Annotated[int, "CharmedBaryon"] = 32
    BottomBaryon: Annotated[int, "BottomBaryon"] = 33
    PionDecay: Annotated[int, "PionDecay"] = 34
    KaonDecay: Annotated[int, "KaonDecay"] = 35
    BremPhot: Annotated[int, "BremPhot"] = 36
    PromptPhot: Annotated[int, "PromptPhot"] = 37
    UndrPhot: Annotated[int, "UndrPhot"] = 38
    ISRPhot: Annotated[int, "ISRPhot"] = 39
    FSRPhot: Annotated[int, "FSRPhot"] = 40
    NucReact: Annotated[int, "NucReact"] = 41
    PiZero: Annotated[int, "PiZero"] = 42
    DiBoson: Annotated[int, "DiBoson"] = 43
    ZorHeavyBoson: Annotated[int, "ZorHeavyBoson"] = 44
    MultiBoson: Annotated[int, "MultiBoson"] = 47
    QCD: Annotated[int, "QCD"] = 45


# https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/EGammaIdentificationRun2#Photon_isEM_word
class PhotonID(IntEnum):
    Rhad: Annotated[int, "ClusterHadronicLeakage_Photon"] = 10
    E277: Annotated[int, "ClusterMiddleEnergy_Photon"] = 11
    Reta: Annotated[int, "ClusterMiddleEratio37_Photon"] = 12
    Rphi: Annotated[int, "ClusterMiddleEratio33_Photon"] = 13
    Weta2: Annotated[int, "ClusterMiddleWidth_Photon"] = 14
    f1: Annotated[int, "ClusterStripsEratio_Photon"] = 15
    DeltaE: Annotated[int, "ClusterStripsDeltaE_Photon"] = 17
    Wstot: Annotated[int, "ClusterStripsWtot_Photon"] = 18
    fside: Annotated[int, "ClusterStripsFracm_Photon"] = 19
    Ws3: Annotated[int, "ClusterStripsWeta1c_Photon"] = 20
    ERatio: Annotated[int, "ClusterStripsDEmaxs1_Photon"] = 21
