"""Rebuild a SPICE netlist from the Sim.* fields in thermostat.kicad_sch (an independent
check of what KiCad's simulator should produce) and run it with ngspice.
Usage: python3 schematic_to_spice.py [tstop]"""
import re,subprocess,sys,json
sys.path.insert(0,'.')
import os
SCR=os.path.dirname(os.path.abspath(__file__))+'/'
exec(open(SCR+'sch_nets.py').read().replace("json.dump","(lambda *a,**k:None)"))
lib=open('thermostat_models.lib').read()
ports={m.group(1):m.group(2).split() for m in re.finditer(r'^\.subckt\s+(\S+)\s+(.*)$',lib,re.M)}
def node(n):
    if n=='GND':return '0'
    return 'n_'+re.sub(r'[^A-Za-z0-9]','_',n.replace('+','p'))
sims={}
for s in find(sch,'symbol'):
    ref=prop(s,'Reference');sf={p[1]:p[2] for p in find(s,'property') if p[1].startswith('Sim.')}
    if sf:sims[ref]=sf
out=['* generated from thermostat.kicad_sch Sim.* fields','.include thermostat_models.lib']
for ref,sf in sorted(sims.items()):
    pm=dict(x.split('=') for x in sf['Sim.Pins'].split())
    nodes={mp:node(sch_pin.get((ref,sp),'@nc_%s_%s'%(ref,sp))) for sp,mp in pm.items()}
    dev=sf['Sim.Device'];par=sf.get('Sim.Params','')
    if dev in('R','C'):
        out.append('%s %s %s %s'%(ref if ref[0]==dev else dev+'_'+ref,nodes['+'],nodes['-'],par.split('=')[1]))
    elif dev=='V':
        p=dict(x.split('=') for x in par.split())
        if sf['Sim.Type']=='SIN':spec='SIN(%s %s %s)'%(p['dc'],p['ampl'],p['f'])
        else:spec='PULSE(%s %s %s %s %s %s %s)'%(p['y1'],p['y2'],p['td'],p['tr'],p['tf'],p['tw'],p['per'])
        out.append('%s %s %s %s'%(ref,nodes['+'],nodes['-'],spec))
    elif dev=='SUBCKT':
        nm=sf['Sim.Name'];out.append('X%s %s %s'%(ref,' '.join(nodes[p] for p in ports[nm]),nm))
tstop=sys.argv[1] if len(sys.argv)>1 else '0.8'
probes=['RC_24VAC_UNFUSED','C_24VAC','VRECT_DC','VCLAMP','+5V','Y1','GP_Y1']
out+=['.options method=gear reltol=1e-3','.tran 20u %s 0 50u uic'%tstop,'.control','run','set wr_singlescale',
 'wrdata from_schematic.dat '+' '.join('v(%s)'%node(p) for p in probes),'quit','.endc','.end']
open('from_schematic.cir','w').write('\n'.join(out)+'\n')
r=subprocess.run(['ngspice','-b','from_schematic.cir'],capture_output=True,text=True)
print('\n'.join(l for l in (r.stdout+r.stderr).splitlines() if re.search('rror|rows|Warn|unknown|warning',l,re.I) and 'no DC value' not in l))
