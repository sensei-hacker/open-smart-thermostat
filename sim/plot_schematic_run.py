import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=np.loadtxt('from_schematic.dat'); t=d[:,0]
names=['RC_24VAC_UNFUSED','C_24VAC','VRECT_DC','VCLAMP','+5V','Y1','GP_Y1']
v=dict(zip(names,d[:,1:9].T))
v['Yload']=v['Y1'];v['AC']=v['RC_24VAC_UNFUSED']
ss=(t>0.1)&(t<0.2)
print('VRECT_DC %.1f..%.1f V  VCLAMP %.1f..%.1f V  +5V %.3f V'%(v['VRECT_DC'][ss].min(),v['VRECT_DC'][ss].max(),v['VCLAMP'][ss].min(),v['VCLAMP'][ss].max(),v['+5V'][ss].mean()))
for a,b,lab in ((0.1,0.19,'GPIO low (before 0.2 s)'),(0.3,0.49,'GPIO high (0.2-0.5 s)'),(0.6,0.79,'GPIO low again')):
    m=(t>a)&(t<b);y=v['Yload'][m]   # Y1 vs gnd node; load returns to C
    print('%-26s load voltage pk %.1f V  rms %.1f V'%(lab,abs(y).max(),np.sqrt((y**2).mean())))
fig,ax=plt.subplots(3,1,figsize=(11,9))
ax[0].plot(t,v['AC'],lw=.5,label='24VAC (Rc to C)');ax[0].plot(t,v['VRECT_DC'],label='VRECT_DC');ax[0].plot(t,v['VCLAMP'],label='VCLAMP');ax[0].plot(t,v['+5V'],label='+5V');ax[0].legend(loc='right');ax[0].grid(1);ax[0].set_title('Power chain')
ax[1].plot(t,v['GP_Y1'],label='GP_Y1 (GPIO)');ax[1].plot(t,v['Yload'],lw=.6,label='load voltage (Y1 to C)');ax[1].legend();ax[1].grid(1);ax[1].set_title('Relay channel Y1')
m=(t>0.18)&(t<0.28);ax[2].plot(t[m],v['Yload'][m],label='load voltage');ax[2].plot(t[m],v['AC'][m],alpha=.4,label='24VAC at terminals');ax[2].legend();ax[2].grid(1);ax[2].set_title('Zoom: turn-on at zero crossing');ax[2].set_xlabel('s')
plt.tight_layout();plt.savefig('from_schematic.png',dpi=80)
