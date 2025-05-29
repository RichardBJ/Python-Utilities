#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 22:56:26 2018
@author: Richard
"""
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
import pandas as pd
#remember uppercase for Pythion2.7
#lowercase for 3+
from tkinter import filedialog

import importlib
  
class Fileoid:        

    def __init__(self, name):
        global dataset
        
        self.name = name
        #dont have to read the whole thing
        nrows=100000000
        skiprows=0
        width=16
        height=4
        df=pd.read_csv(self.name,header=None,
                       nrows=nrows,skiprows=1)   #NOTE SOMETIMES THERE IS A HEADER!! 
        #...just in case there was a header
        #skip one row!!
        print(len(df))
        self.dragging=False
        b_input=[]
#        df.drop
        #Just to check
        print(df.loc[:10])
        bite=70000 #chunk to SEE at one time
        if bite>len(df):
            bite=len(df)
        #format of data is time,raw,label
        dataset=df.values
        '''
        temporary!!!
        '''
        #dataset[:,0]=dataset[:,0]/6     
        '''
        Correction
        Sometimes INVERT
        '''
        #dataset[:,1]=dataset[:,1]*-1        
#        print(dataset[:10,:])
        mind=np.min(dataset[:,1])
        maxd=np.max(dataset[:,1])
        spand=abs(maxd-mind)
        scaler=(bite/4)/spand
        si=(dataset[5,0]-dataset[0,0])/5
        s=int(1/si)
        sx=s
        plt.ioff()
        
#        print(scaler)
        dataset[:,1]=dataset[:,1]*scaler
        for i in range(len(dataset)):
            if dataset[i,2]==1:
                 dataset[i,2]= dataset[i,1]
                 b_input.append(i)
        self.fig, self.ax = plt.subplots(figsize=(width,height))
        plt.axis([0, bite, np.min(dataset[:,1]),np.max(dataset[:,1])])
        titletxt=str(len(df))+'_pts; LH click to add; RH click or middle button select to delete, close to save, toggle "D" b4 panning'
        plt.title(titletxt)
        plt.show()
        self.a = plt.plot(range(len(dataset)),dataset[:,1],color='red',zorder=5)[0]
        while sx<len(dataset):
            self.ax.axvline(x=sx, ymin=0, ymax=1,zorder=0)
            sx=sx+s
        self.b = plt.scatter(b_input,dataset[b_input,2],color='grey',s=50,picker=1,zorder=10)
        self.cid1 = self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.cid2= self.fig.canvas.mpl_connect('button_press_event',self.add_or_remove_point)
        self.cid3= self.fig.canvas.mpl_connect('close_event',self.on_shut)
        self.cid4=RectangleSelector(self.ax, self.line_select_callback,
                                       drawtype='box', useblit=True,
                                       button=[2],  # don't use middle button
                                       minspanx=5, minspany=5,
                                       spancoords='pixels',
                                       interactive=True)

        print ('init end')
    
    def closest_node(self, node, nodes):
        self.node=node
        self.nodes=nodes
        self.nodes = np.array(self.nodes)
        deltas = np.abs(self.nodes - self.node) 
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)    
        return np.argmin(dist_2)
    
    def add_or_remove_point(self,event):
        if event.dblclick==True:
#                    plt.close('all')
                    return 0             
        if self.dragging==True:
            return 0
               
        self.xydata_a = np.stack(self.a.get_data(),axis=1)        
        self.xdata_a = self.a.get_xdata()
        self.ydata_a = self.a.get_ydata()
        self.xydata_b = self.b.get_offsets()
        self.xdata_b = self.b.get_offsets()[:,0]
        self.ydata_b = self.b.get_offsets()[:,1]
         
        #click x-value
        self.xdata_click = event.xdata
        self.ydata_click = event.ydata
      
        #index of nearest x-value in a
        self.xdata_nearest_index_a=self.closest_node([self.xdata_click ,self.ydata_click],self.xydata_a)
        self.xdata_nearest_index_b=self.closest_node([self.xdata_click ,self.ydata_click],self.xydata_b)
        #new scatter point x-value
                 
        self.new_xdata_point_b = self.xdata_a[self.xdata_nearest_index_a]
        #new scatter point [x-value, y-value]
        self.new_xydata_point_b = self.xydata_a[self.new_xdata_point_b,:]
                       
        if event.button == 1:
            if self.new_xdata_point_b not in self.xdata_b:
                #insert new scatter point into b
                self.new_xydata_b = np.insert(self.xydata_b,0,self.new_xydata_point_b,axis=0)
                #sort b based on x-axis values
                self.new_xydata_b = self.new_xydata_b[np.argsort(self.new_xydata_b[:,0])]
                #update b
                self.b.set_offsets(self.new_xydata_b)
                plt.draw()
                          
        elif event.button == 3:
            self.new_xdata_point_b = self.xdata_b[self.xdata_nearest_index_b]
            if self.new_xdata_point_b in self.xdata_b:
                #remove xdata point b
                self.new_xydata_b = np.delete(self.xydata_b,np.where(self.xdata_b==self.new_xdata_point_b),axis=0)
                #update b
                self.b.set_offsets(self.new_xydata_b)
            plt.draw()
        
        
    def line_select_callback(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
#        print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
#        print(" The button you used were: %s %s" % (eclick.button, erelease.button))

        x1=int(x1)
        x2=int(x2)
        if x2<x1:
            temp=x1
            x1=x2
            x2=temp
            
        if y2<y1:
            tempf=y1
            y1=y2
            y2=tempf
        
        for pts in range(x1,x2):
            if pts in self.xdata_b:
                self.xydata_b= self.b.get_offsets()
                self.xdata_b = self.b.get_offsets()[:,0]
                self.ydata_b = self.b.get_offsets()[:,1]
                if  (self.ydata_b[np.where(self.xdata_b==pts)]<y2)&(self.ydata_b[np.where(self.xdata_b==pts)]>y1):
                    self.new_xydata_b = np.delete(self.xydata_b,np.where(self.xdata_b==pts),axis=0)
                    self.b.set_offsets(self.new_xydata_b)
        plt.draw()

    def on_key(self,event):
        global bang
        print('you pressed', event.key)
        if event.key=='x': 
            plt.close('all')
#            doesnt work!!

            
        if self.dragging==False:
            self.dragging=True
            print('PAN mode')
        else:
            self.dragging=False
            print('SELECT mode')
            
    def on_shut(self,event):
        
        global dataset
        global bang
        
        print(event)
        if event=="x":
            return 0
        else:
            print('Hey you shut me!!')
            labels=self.b.get_offsets()[:,0]
            dataset[:,2]=0
    #        print('len dataset',len(dataset))
            for i in range(len(labels)):
                dataset[int(labels[i]),2]=1
          
            
            #intervals in samplepoints!
            intervals=np.diff(labels)
            #in time =
            SI=(dataset[20,0]-dataset[10,0])/10
            print('SI=',SI)
            intervals =intervals*SI
            mhr=60/np.mean(intervals)
            print('mean HR',mhr)
 #untested bit!!
            bang=0
            plt.close('all')
        
    print('class created')

if __name__ == "__main__":
    
    for num in range(1):
        print("NOTE: around lines 40 or so you can divide tm/6 if wrong time or invert if necessary")
        importlib.reload(plt)
        root = filedialog.Tk()
        root.filename =  filedialog.askopenfilename(initialdir = "/",  title = "Select file",filetypes = (("csv DL file","*.csv"),("all files","*.*")))
        file2open=root.filename
        print (file2open)
        trial = Fileoid(file2open)    
        root.withdraw()
    #    plt.gca(); plt.gcf().ginput(4)
        while not 'bang' in locals():
            plt.pause(1)
      
        print ('completed')
        
        del bang
        del dataset
        del trial
        #try once more to close!!
        plt.close('all')
        