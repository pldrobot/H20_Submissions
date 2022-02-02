import pickle

open_file_ = open("Appdata/W_Data_Dict.pickle", "rb")
W_Data_Dict = pickle.load(open_file_)
open_file_.close()
print('File Loaded')
with open('Appdata/W_Data_Dict.pick4', 'wb') as f:
    pickle.dump(W_Data_Dict, f, protocol=4)
print('File Saved')
