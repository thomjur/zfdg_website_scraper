from sklearn.preprocessing import StandardScaler as SS
from sklearn.cluster import KMeans
import pandas as pd
import pickle

class Analyzer():
    '''
    DESCRIPTION
    '''

    def __init__(self):
        self.data_dict = self.openDataDict_()
        self.data_df = self.convertDict2Df_()

    # private methods

    def convertDict2Df_(self):
        '''
        converting self.data_dict to pandas DataFrame
        '''
        return pd.DataFrame.from_dict(self.data_dict, orient="index").drop(columns=["images", "text_complete"])
    
    def openDataDict_(self):
        try:
            with open("merged_data_dict.pickle", "rb") as f:
                dd_ = pickle.load(f)
            if dd_:
                return dd_
            else:
                raise Exception("Sorry, merged_data_dict.pickle needs to be present in folder! Create first with DataPreparation() class!")
                return -1
        except:
            raise Exception("Sorry, a problem occurred! Remember that merged_data_dict.pickle needs to be present in folder! Create first with DataPreparation() class!")

    # public methods

    def clusterData(self, df_scaled, n=3):
        '''
        clustering data with 3 KMeans
        '''
        kmeans = KMeans(n_clusters=n, random_state=42)
        kmeans.fit(df_scaled)
        df_cp = df_scaled.copy()
        df_cp["clusters"] = kmeans.labels_
        return df_cp

    def standardizeData(self, df_orig):
        '''
        standardize data with the help of sklearn's StandardScaler() class
        '''
        scaler = SS()
        scaled_columns = scaler.fit_transform(df_orig[["total_images", "big_images", "middle_images", "small_images", "background_images",
                                                "total_length", "external_links", "internal_links", "total_links"]])
        df_cp = df_orig.copy()
        df_cp["total_images_scaled"] = scaled_columns[:,0]
        df_cp["big_images_scaled"] = scaled_columns[:,1]
        df_cp["middle_images_scaled"] = scaled_columns[:,2]
        df_cp["small_images_scaled"] = scaled_columns[:,3]
        df_cp["background_images_scaled"] = scaled_columns[:,4]
        df_cp["total_length_scaled"] = scaled_columns[:,5]
        df_cp["external_links_scaled"] = scaled_columns[:,6]
        df_cp["internal_links_scaled"] = scaled_columns[:,7]
        df_cp["total_links_scaled"] = scaled_columns[:,8]
        return df_cp.iloc[:,9:]
