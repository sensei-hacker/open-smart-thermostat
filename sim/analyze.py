import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=np.loadtxt('power_chain.dat',skiprows=1)
t,vun,vf,vr,v9,v5,vg,i9,i5=d.T
if1=(vun-vf)/1.0   # F1 = 1 ohm (A)
ss=t>0.5   # steady state window
def pp(x):return x[ss].max()-x[ss].min()
print('VRECT_DC  min/max/mean  %.2f %.2f %.2f V  ripple p-p %.2f V'%(vr[ss].min(),vr[ss].max(),vr[ss].mean(),pp(vr)))
print('+9V       min/max       %.3f %.3f V'%(v9[ss].min(),v9[ss].max()))
print('+5V       min/max       %.3f %.3f V  ripple p-p %.1f mV'%(v5[ss].min(),v5[ss].max(),pp(v5)*1e3))
print('F1 current peak %.2f A  RMS %.3f A'%(abs(if1[ss]).max(),np.sqrt((if1[ss]**2).mean())))
print('F1 dissipation (1 ohm assumed) %.2f W'%((if1[ss]**2).mean()*1.0))
print('Peak inrush current (all time) %.2f A'%abs(if1).max())
print('Peak |V| on unfused AC %.1f V'%abs(vun).max())
iin=i9+i5
print('9V rail load: Dial %.0f mA + 5V stage %.0f mA'%(i9[ss].mean()*1e3,i5[ss].mean()*1e3))
print('7805 dissipation %.2f W'%(((v9[ss]-v5[ss])*i5[ss]).mean()))
fig,ax=plt.subplots(3,1,figsize=(11,10))
ax[0].plot(t,vun,lw=.5,label='RC_24VAC_UNFUSED');ax[0].plot(t,vr,label='VRECT_DC');ax[0].plot(t,v9,label='+9V');ax[0].plot(t,v5,label='+5V')
ax[0].set_title('Start-up, 24.1 VAC unloaded');ax[0].legend();ax[0].grid(1)
m=(t>0.70)&(t<0.75)
ax[1].plot(t[m],vr[m],label='VRECT_DC ripple');ax[1].plot(t[m],vun[m]/1.5,alpha=.3,label='AC /1.5');ax[1].legend();ax[1].grid(1);ax[1].set_title('Steady state (50 ms)')
ax[2].plot(t,if1,lw=.5,label='F1 current (A)');ax[2].legend();ax[2].grid(1);ax[2].set_xlabel('s')
plt.tight_layout();plt.savefig('power_chain.png',dpi=80)
