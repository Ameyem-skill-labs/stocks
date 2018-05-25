# %reset
# 'http://www.bseindia.com/download/BhavCopy/Equity/EQ230110_CSV.ZIP'
from datetime import datetime
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
import os
import numpy as np
import pickle
class NseFolder2Pickle:
    def __init__(self, data_folder="D:/SoftwareWebApps/Python/python_wb/Stocks/Data/NSE/",
                 pickle_path='D:\SoftwareWebApps\Python\python_wb\Stocks\Data\stock_pickle\\'):
        self.data_folder=data_folder
         # returns list
        self.pickle_path=pickle_path


    # In[41]:
    def get_dir(self):
        return os.listdir(self.data_folder)
    def save_pkl(self,file,var):
        with open(file, 'wb') as f:
            pickle.dump(var, f)
            f.close()
    def load_pkl(self,file):
        with open(file, 'rb') as f: 
            var = pickle.load(f)
            f.close()
        return var

    def stock_array(self,table_name):
        empty_array=[]
        return empty_array

    def put_entry(self,table_arrays,symbols, valarray):
        i=0
        default=[]
        for val in valarray:
            table_arrays.setdefault(symbols[i],default)
            table_arrays[symbols[i]].append(val)
            i +=1
        return table_arrays
    def armarray_table_fns(self,symbols):
        return    dict((s,self.stock_array(s)) for s in symbols)
    def update_tables(self,table_arrays,symbols):
        table_arrays.update(self.armarray_table_fns(symbols))
        return table_arrays

    def csvdf_process(self,myZip):
        df=pd.read_csv(myZip)
        if 'Unnamed: 13' in df.columns:
            df=df.drop(['Unnamed: 13'], axis=1)
        tstamp=datetime.strptime(df['TIMESTAMP'].iloc[0],'%d-%b-%Y')
        df.SERIES=df.SERIES.replace(np.nan, 'NA', regex=True)
        symbols=df.SYMBOL.values
        sr=df.SERIES.values
        symbols= np.array(  [sr[i]+'_'+symbols[i] for i in range(0,len(sr))], dtype=object)
        df['TIMESTAMP']=tstamp
        df=df[df.columns[2:-1]].drop('PREVCLOSE',1)
        if len(df.columns)==8:
            df['TOTALTRADES']=0
        values=df.values

        return symbols,values


    # In[46]:

    def get_tablearray(self,files_not_in_pickle):
        # here table_fns are table arrays
        k=0 #one if tests for k value be careful
        started=datetime.now()
        old=datetime.now()
        table_fns={}
        tables=[]
        if(len(files_not_in_pickle)==0):
            print("There is nothing to update the pickle files...")
            return tables, table_fns
        print("Reading from zip -> csv from {} files".format(len(files_not_in_pickle)))
        for file in files_not_in_pickle:
            zip_ref = ZipFile(self.data_folder+file, 'r')
            # try:   
            with zip_ref as my_zip_file:
                    with my_zip_file.open(my_zip_file.namelist()[0]) as myZip:
                        symbols,values=self.csvdf_process(myZip)
                               
                        tbls_not_in_db=np.setdiff1d(symbols,tables)            
                        if(k==0):
                            table_fns= self.update_tables(table_fns,symbols)

                        if(len(tables)>0 and len(tbls_not_in_db)>0):
                            table_fns= self.update_tables(table_fns,tbls_not_in_db)
                        tables=np.asarray(list(table_fns.keys())).astype(object) 
                        table_fns=self.put_entry(table_fns, symbols, values)
                        k+=1
                        print(k,end=', ')
                        if (k%100==0):            
                            print("{} of {} csv files read into system..".format(k,len(files_not_in_pickle)))
                            nowtime=datetime.now()
                            print("last 100files took ..")
                            print(nowtime-old)
                            print("From first it took ..",end='')
                            print(nowtime-started)
                            old=nowtime

            # except:
            #     print("Zip file not good for file: {}".format(file))
        print("Reading from zip -> csv Completed ..")
        return tables, table_fns


    def main(self):
        ldirlist=np.array(self.get_dir())

        print("Welcome to NSE pickle DataBase update.... ")
        i=0
        try:
            columns=self.load_pkl(self.pickle_path+'columns_ref.pkl')
            dirlist_written=self.load_pkl(self.pickle_path+'wrtitten_files.pkl')
            symbols_pkl=self.load_pkl(self.pickle_path+'symbols.pkl')
        except:
            columns=[]
            dirlist_written=[]
            symbols_pkl=[]
        stime=datetime.now()
        dts=[datetime.strptime(fname[2:11],'%d%b%Y') for fname in ldirlist]
        ldirlist=ldirlist[np.argsort(dts)]
        files_not_in_pickle=np.setdiff1d(ldirlist,dirlist_written)
        dts=[datetime.strptime(fname[2:11],'%d%b%Y') for fname in files_not_in_pickle]
        files_not_in_pickle=files_not_in_pickle[np.argsort(dts)]
        tables, table_arrays=self.get_tablearray(files_not_in_pickle)
        # if(len(tables)==0):
        #     print("Completed...")
        #     return
        tbls_not_in_pkl=np.setdiff1d(tables,symbols_pkl) 
        tbls_in_pkl=np.intersect1d(tables,symbols_pkl) 
        tbls_all=np.union1d(tables,symbols_pkl) 

        columns=['OPEN','HIGH','LOW','CLOSE','LAST','TOTTRDQTY','TOTTRDVAL','TIMESTAMP','TOTALTRADES']
        stime=datetime.now()
        self.save_pkl(self.pickle_path+'columns_ref.pkl',columns)
        self.save_pkl(self.pickle_path+'wrtitten_files.pkl',ldirlist)
        self.save_pkl(self.pickle_path+'symbols.pkl',tbls_all)
        self.save_pkl(self.pickle_path+'latest_symbols.pkl',tables)
        
        i=0
        for tbl in tbls_in_pkl:
            # Saving the objects:
            stock_array=self.load_pkl(self.pickle_path+tbl+'.pkl')
            stock_array.extend(table_arrays.get(tbl))    
            self.save_pkl(self.pickle_path+tbl+'.pkl',stock_array)
            i +=1
            if i%100 ==0:
                print('{} files among {} re-written'.format(i,len(tbls_in_pkl)))
        i=0    
        for tbl in tbls_not_in_pkl:
            self.save_pkl(self.pickle_path+tbl+'.pkl',table_arrays.get(tbl))
            i +=1
            if i%2 ==0:
                print('{} files among {} new files written'.format(i,len(tbls_not_in_pkl)))
        print('Toal {} new files for new symbols written'.format(len(tbls_not_in_pkl)))
        print("For all It took {} time".format(datetime.now()-stime))