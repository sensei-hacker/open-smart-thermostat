import re,math,json,collections
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','')
S=os.path.dirname(os.path.abspath(__file__))+'/'
def parse(s):
    stack=[[]]
    for m in re.finditer(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+',s):
        x=m.group(0)
        if x=='(':stack.append([])
        elif x==')':l=stack.pop();stack[-1].append(l)
        else:stack[-1].append(x[1:-1] if x[0]=='"' else x)
    return stack[0][0]
def find(l,k):return [c for c in l if isinstance(c,list) and c and c[0]==k]
def f1(l,k):
    r=find(l,k);return r[0] if r else None
def prop(sym,name):
    for p in find(sym,'property'):
        if p[1]==name:return p[2]

# ---------------- schematic ----------------
sch=parse(open(D+'thermostat.kicad_sch').read())
libs={}
for ls in find(f1(sch,'lib_symbols'),'symbol'):
    pins=[]
    def walk(node,unit):
        for c in node:
            if isinstance(c,list) and c:
                if c[0]=='symbol':
                    m=re.search(r'_(\d+)_(\d+)$',c[1]);walk(c,int(m.group(1)) if m else unit)
                elif c[0]=='pin':
                    at=f1(c,'at');nm=f1(c,'name');nu=f1(c,'number')
                    pins.append((unit,nu[1],nm[1],float(at[1]),float(at[2])))
    walk(ls,0)
    libs[ls[1]]=pins

UF={}
def fd(a):
    UF.setdefault(a,a)
    while UF[a]!=a:
        UF[a]=UF[UF[a]];a=UF[a]
    return a
def un(a,b):UF[fd(a)]=fd(b)
def P(x,y):return (round(float(x),2),round(float(y),2))

wires=[]
for w in find(sch,'wire'):
    pts=[P(p[1],p[2]) for p in find(f1(w,'pts'),'xy')]
    wires.append(pts)
    for a,b in zip(pts,pts[1:]):un(a,b)
junc=[P(f1(j,'at')[1],f1(j,'at')[2]) for j in find(sch,'junction')]
def on_seg(p,a,b):
    (x,y),(x1,y1),(x2,y2)=p,a,b
    if abs((x2-x1)*(y-y1)-(y2-y1)*(x-x1))>0.02:return False
    return min(x1,x2)-0.01<=x<=max(x1,x2)+0.01 and min(y1,y2)-0.01<=y<=max(y1,y2)+0.01
segs=[(a,b) for pts in wires for a,b in zip(pts,pts[1:])]
def attach(p):
    fd(p)
    for a,b in segs:
        if on_seg(p,a,b):un(p,a)
labels=[]
for k in ('label','global_label','hierarchical_label'):
    for l in find(sch,k):
        at=f1(l,'at');labels.append((l[1],P(at[1],at[2])))
for j in junc:attach(j)
for n,p in labels:attach(p)

parts={}   # ref -> dict
pinpts=[]  # (ref,pin,name,pt)
powerlabels=[]
for s in find(sch,'symbol'):
    lid=f1(s,'lib_id')
    if not lid:continue
    lid=lid[1];ref=prop(s,'Reference');val=prop(s,'Value')
    at=f1(s,'at');x,y=float(at[1]),float(at[2]);rot=float(at[3]) if len(at)>3 else 0
    mir=f1(s,'mirror');mir=mir[1] if mir else ''
    unit=f1(s,'unit');unit=int(unit[1]) if unit else 1
    isp=lid.startswith('power:') or ref.startswith('#PWR')
    if not isp:
        parts[ref]=dict(value=val,lib=lid,fp=prop(s,'Footprint'),dnp=bool(f1(s,'dnp') and f1(s,'dnp')[1]=='yes'))
    cand=[]
    plist=[q for q in libs[lid] if q[0] in (0,unit)]
    def tf(px,py,variant):
        rr=rot
        if variant==0:   # mirror then rotate
            if mir=='x':py=-py
            if mir=='y':px=-px
        r=math.radians(rr);rx=px*math.cos(r)-py*math.sin(r);ry=px*math.sin(r)+py*math.cos(r)
        if variant==1:   # rotate then mirror
            if mir=='x':ry=-ry
            if mir=='y':rx=-rx
        return P(x+rx,y-ry)
    best=None
    for v in (0,1):
        pts=[tf(q[3],q[4],v) for q in plist]
        sc=sum(1 for pt in pts if any(on_seg(pt,a,b) for a,b in segs) or any(abs(pt[0]-lp[0])<.01 and abs(pt[1]-lp[1])<.01 for _,lp in labels))
        if best is None or sc>best[0]:best=(sc,v)
    for (u,num,name,px,py) in plist:
        pt=tf(px,py,best[1])
        attach(pt)
        if isp:powerlabels.append((val,pt))
        else:pinpts.append((ref,num,name,pt))
# merge by label name
byname=collections.defaultdict(list)
for n,p in labels+powerlabels:byname[n].append(p)
for n,ps in byname.items():
    for p in ps[1:]:un(ps[0],p)
netname={}
for n,ps in byname.items():netname[fd(ps[0])]=n
sch_nets=collections.defaultdict(set)
for ref,num,name,pt in pinpts:
    root=fd(pt)
    nm=netname.get(root,'@%s,%s'%root)
    sch_nets[nm].add((ref,num))
# rename unnamed by member
sch_pin={}
for n,s in sch_nets.items():
    for rp in s:sch_pin[rp]=n

# ---------------- pcb ----------------
pcb=parse(open(D+'thermostat.kicad_pcb').read())
pparts={};pcb_nets=collections.defaultdict(set)
for fp in find(pcb,'footprint'):
    ref=prop(fp,'Reference')
    pparts[ref]=dict(value=prop(fp,'Value'),lib=fp[1])
    for pad in find(fp,'pad'):
        net=f1(pad,'net')
        pcb_nets[net[1] if net else '(none)'].add((ref,pad[1]))
json.dump(dict(sch_parts=parts,pcb_parts=pparts,
  sch_nets={k:sorted(v) for k,v in sch_nets.items()},
  pcb_nets={k:sorted(v) for k,v in pcb_nets.items()}),open(S+'nets.json','w'),indent=1)
print(len(parts),'sch parts',len(pparts),'pcb parts',len(sch_nets),'sch nets',len(pcb_nets),'pcb nets')
