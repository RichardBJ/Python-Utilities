#!/usr/bin/env python
# coding: utf-8

# In[151]:


print("Running")


# In[152]:


from tslearn.metrics import dtw
from matplotlib import pyplot as plt
import numpy as np


#strip of zero bnd ones
a=[0]*10
a.extend([1]*5)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*16)
a.extend([1]*50)
a.extend([0]*102)

# another one
b=[0]*100
b.extend([1]*5)
b.extend([0]*6)
b.extend([1]*15)
b.extend([0]*60)
b.extend([0]*15)
b.extend([0]*16)
b.extend([1]*5)
b.extend([0]*12)
c=[0 if val==1 else 1 for val in a]
plt.subplot(3,1,1)
plt.plot(a)
ad=np.diff(np.asarray(a))
plt.plot(ad-1)
plt.subplot(3,1,2)
plt.plot(b)
bd=np.diff(np.asarray(b))
plt.plot(bd-1)
plt.subplot(3,1,3)
plt.plot(c)
cd=np.diff(np.asarray(c))
plt.plot(cd-1)


# In[203]:


d=[]
for i in range(250):
    d.append(dtw(a, b,sakoe_chiba_radius = i))
plt.plot(d)
print(dtw(a, b,sakoe_chiba_radius = 10))
print("This is a really bad detection very little accuracy")
print("ab dwt: ",dtw(ad, bd,sakoe_chiba_radius = 10))
na=np.count_nonzero(np.diff(a))+np.count_nonzero(np.diff(b))
print("normalised ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10)/na)
print("differential ab dwt: ",dtw(ad, bd,sakoe_chiba_radius = 10))


# In[204]:


d=[]
for i in range(250):
    d.append(dtw(a, c,sakoe_chiba_radius = i))
plt.plot(d)
print(dtw(a, c,sakoe_chiba_radius = 10))
na=np.count_nonzero(np.diff(a))+np.count_nonzero(np.diff(c))
print("This is entirely inverted. effectively 100% wrong")
print("normalised ac dwt: ",dtw(a, c,sakoe_chiba_radius = 10)/na)
print(dtw(ad, cd,sakoe_chiba_radius = 10))


# In[207]:


#strip of zero bnd ones
a=[0]*10
a.extend([1]*5)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*16)
a.extend([1]*50)
a.extend([0]*102)

# another one
b=[0]*10
b.extend([1]*5)
b.extend([0]*6)
b.extend([1]*15)
b.extend([0]*6)
b.extend([0]*15)
b.extend([0]*16)
b.extend([1]*45)
b.extend([0]*102)
plt.subplot(2,1,1)
plt.plot(a)
plt.subplot(2,1,2)
plt.plot(b)


# In[208]:


d=[]
for i in range(250):
    d.append(dtw(a, b,sakoe_chiba_radius = i))
plt.plot(d)
print(dtw(a, b,sakoe_chiba_radius = 10))
na=np.count_nonzero(np.diff(a))+np.count_nonzero(np.diff(b))
print("Reasonable, just missing one event")
print("normalised ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10)/na)


# https://towardsdatascience.com/jupyter-notebook-to-pdf-in-a-few-lines-3c48d68a7a63
# To produce PDF

# In[209]:


#strip of zero bnd ones
a=[0]*250


# another one
b=[0]*50
b.extend([1]*20)
b.extend([0]*100)

plt.subplot(2,1,1)
plt.plot(a)
plt.subplot(2,1,2)
plt.plot(b)


# In[210]:


na=(np.count_nonzero(np.diff(a))+np.count_nonzero(np.diff(b)))
print("Completely wrong")
print("normalised ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10)/na)


# In[211]:


#What would be the actual maximum distance?
d1=dtw(a, b,sakoe_chiba_radius = 10)
a=[0]*len(a)
b=[1]*len(b)
print("ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10))
print("other normalised ab dwt: ",d1/dtw(a, b,sakoe_chiba_radius = 10))


# In[162]:


#strip of zero bnd ones
a=[0]*250


# another one
b=[0]*50
b.extend([1]*20)
b.extend([0]*20)
b.extend([1]*20)
b.extend([0]*(len(a)-len(b)))
plt.subplot(2,1,1)
plt.plot(a)
plt.subplot(2,1,2)
plt.plot(b)


# In[212]:


na=(np.count_nonzero(np.diff(a))+np.count_nonzero(np.diff(b)))
print("Twice as bad as the previous in a sense....  All events are wrong")
print("normalised ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10)/na)


# In[213]:


#What would be the actual maximum distance?
d1=dtw(a, b,sakoe_chiba_radius = 10)
a=[0]*len(a)
b=[1]*len(b)
print("ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10))
print("other normalised ab dwt: ",d1/dtw(a, b,sakoe_chiba_radius = 10))
#OK looked worse simply because the length of the traces different


# In[230]:


#strip of zero bnd ones
a=[0]*250


# another one
b=[0]*50
b.extend([1]*20)
b.extend([0]*20)
b.extend([1]*20)
b.extend([0]*(len(a)-len(b)))
plt.subplot(2,1,1)
plt.plot(a)
plt.subplot(2,1,2)
plt.plot(b)


# In[166]:


#What would be the actual maximum distance?
d1=dtw(a, b,sakoe_chiba_radius = 10)
na=(np.count_nonzero(np.diff(a))+np.count_nonzero(np.diff(b)))
a=[0]*len(a)
b=[1]*len(b)
print("ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10))
print("normalised ab dwt: ",dtw(a, b,sakoe_chiba_radius = 10)/na)
print("other normalised ab dwt: ",d1/dtw(a, b,sakoe_chiba_radius = 10))
#OK looked worse simply because the length of the traces different


# ## Just simple approach
# 

# In[214]:


#strip of zero bnd ones
a=[0]*10
a.extend([1]*5)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*16)
a.extend([1]*50)
a.extend([0]*102)

# another one
b=[0]*10
b.extend([1]*5)
b.extend([0]*6)
b.extend([1]*15)
b.extend([0]*6)
b.extend([0]*15)
b.extend([0]*16)
b.extend([1]*45)
b.extend([0]*102)
plt.subplot(2,1,1)
plt.plot(a)
plt.subplot(2,1,2)
plt.plot(b)


# In[168]:


ad=np.diff(np.asarray(a))
bd=np.diff(np.asarray(b))


# In[279]:


def ahits(ground,predicted,res=10):
    #differentiate the idealisations so +1=opening and -1=closure
    ad=np.diff(np.asarray(ground))
    bd=np.diff(np.asarray(predicted))
    hits=0  #total correct events
    summer=0 #total GT events
    #find all the GT openings that have matching opening in prediction
    for i, pt in enumerate(ad):
        start=0
        ender=len(ad)
        if i>res:
            start=i-res
        if i<len(ad)-res:
            ender=i+res
        if pt>0:
            summer+=1
            for j in range(start,ender):
                if bd[j]>0:
                    hits+=1
                    break
    #now all the GT closures that have matching close in prediction
    for i, pt in enumerate(ad):
        start=0
        ender=len(ad)
        if i>res:
            start=i-res
        if i<len(ad)-res:
            ender=i+res
        if pt<0:
            summer+=1
            for j in range(start,ender):
                if bd[j]<0:
                    hits+=1
                    break
    if summer == 0:
        TPs=100
    else:
        TPs=  100*hits/summer
    print("TPs= ", TPs)
    miss=0 #total false positives
    summer=0 #total predicted events
    #find all the predicted openings where there was a real in the GT
    for i, pt in enumerate(bd):
        start=0
        ender=len(ad)
        if i>res:
            start=i-res
        if i<len(ad)-res:
            ender=i+res
        if pt>0:
            hit=False
            summer+=1
            for j in range(start,ender):
                if ad[j]>0:
                    hit=True
                    break
            if hit==False:
                miss+=1
                hit=True
    #find all the predicted closures where there was a real in the GT
    for i, pt in enumerate(bd):
        start=0
        ender=len(ad)
        if i>res:
            start=i-res
        if i<len(ad)-res:
            ender=i+res
        if pt<0:
            hit=False
            summer+=1
            for j in range(start,ender):
                if ad[j]<0:
                    hit=True
                    break
            if hit==False:
                miss+=1
    if summer == 0:
        FPs=0
    else:
        print("miss ",miss)
        FPs=100*miss/summer
    print("FPs= ", FPs)
    return TPs,FPs


# In[280]:


a=[0]*10
a.extend([1]*5)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*6)
a.extend([1]*15)
a.extend([0]*16)
a.extend([1]*50)
a.extend([0]*102)

# another one
b=[0]*100
b.extend([1]*5)
b.extend([0]*6)
b.extend([1]*15)
b.extend([0]*60)
b.extend([0]*15)
b.extend([0]*16)
b.extend([1]*5)
b.extend([0]*12)
c=[0 if val==1 else 1 for val in a]
plt.subplot(3,1,1)
plt.plot(a)
ad=np.diff(np.asarray(a))
plt.plot(ad-1)
plt.subplot(3,1,2)
plt.plot(b)
bd=np.diff(np.asarray(b))
plt.plot(bd-1)
plt.subplot(3,1,3)
plt.plot(c)
cd=np.diff(np.asarray(c))
plt.plot(cd-1)


# In[285]:


print(ahits(a,b,res=10))


# In[ ]:




