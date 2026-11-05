from hands import *
BLUE22.pop(70)
assert len(BLUE12)==len(BLUE18)==len(BLUE22)
SPECS['Y-blue']['keys']=[(12,BLUE12),(18,BLUE18),(22,BLUE22)]
SPECS['Y-getopalm']['skinSegment']=True
SPECS['Y-blue']['paleSegment']=True
SPECS['Y-getopalm']['limitation']+=' Skin colour separation inside union of manually traced hand support removes dark-blue uniform leak; enclosed native finger lines retained by hole filling. Cyan glow is intentionally outside alpha except subpixel edge.'
for id in ['Y-getopalm']:make(id)


