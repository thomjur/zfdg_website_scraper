from sklearn.preprocessing import StandardScaler as SS
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import seaborn as sns
import pandas as pd
import pickle, sys

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

    def getBuiltWithCategorical(self):
        '''
        creates a dataframe with one hot encoding of information stored in builtwith.pickle; this can be used with cluserData()
        '''
        try:
            with open("builtwith.pickle", "rb") as f:
                bw_dict = pickle.load(f)
        except:
            print("Please create builtwith.pickle with DataPreparation class first! Closing...")
            sys.exit()
            
        df = pd.DataFrame.from_dict(bw_dict, orient="index")
        new_frame = pd.DataFrame(index=df.index)
        # I have completely forgotten what's going on here... but it work :D
        for num, column in enumerate(df.columns):
            zero_ = f"zero_{num}"
            col_ = df[column].fillna(zero_)
            col_ = col_.apply(lambda x: [x] if x == zero_ else x)
            mlb = MultiLabelBinarizer()
            nuu = mlb.fit_transform(col_)
            nuuu = pd.DataFrame(nuu, columns=mlb.classes_, index=df.index).drop(columns=[zero_])
            new_frame = pd.concat([new_frame, nuuu], axis=1)
        return new_frame

    def getCosine4CategoricalData(self, df):
        '''
        getting cosine similarity for df with one hot encoded categorical features
        '''
        cosine_data = cosine_similarity(df)
        return pd.DataFrame(cosine_data, columns=df.index, index=df.index)

    def clusterDataKMeans(self, df_scaled, n=3):
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

    def visualizeCluster(self, clustered_df, column1, column2):
        '''
        visualize a cluster based on two columns
        '''
        sns.scatterplot(x=column1, y=column2, hue="clusters", data=clustered_df)
