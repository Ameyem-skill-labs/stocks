import pickle

data_folder="D:/SoftwareWebApps/Python/python_wb/Stocks/Data/NSE/"
pickle_path='D:\SoftwareWebApps\Python\python_wb\Stocks\Data\stock_pickle\\'
def save_pkl(file,var):
    with open(file, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump(var, f)
        f.close()
def load_pkl(file):
    with open(file, 'rb') as f:  # Python 3: open(..., 'wb')
        var = pickle.load(f)
        f.close()
    return var
