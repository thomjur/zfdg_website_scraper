from sklearn.preprocessing import StandardScaler as SS
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from selenium import webdriver
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import pickle, sys
import shutil, os

class Analyzer():
    '''
    main class to analyze website-corpus; need to initialize corpus first
    '''

    def __init__(self):
        self.data_dict = self.openDataDict_()
        self.data_df = self.convertDict2Df_()
        self.column_selection = ["total_images", "big_images", "middle_images", "small_images", "very_small_images", "background_images",
                                                "total_length", "headings", "external_links", "internal_links", "total_links", "total_videos", "small_videos", "big_videos",
                                                "RA_big_images/total_images", "RA_middle_images/total_images",
                                                "RA_small_images/total_images", "RA_total_images/total_length", "RA_big_and_middle_images/total_length",
                                                "RA_internal_links/external_links", "RA_very_small_images/total_images", "RA_headings/total_length",
                                                ]

    # private methods

    def convertDict2Df_(self):
        '''
        PRIVATE method: converting self.data_dict to pandas DataFrame
        '''
        df = pd.DataFrame.from_dict(self.data_dict, orient="index").drop(columns=["images", "text_complete"])
        # creating ratios
        df["RA_big_images/total_images"] = df["big_images"] / df["total_images"]
        df["RA_middle_images/total_images"] = df["middle_images"] / df["total_images"]
        df["RA_small_images/total_images"] = df["small_images"] / df["total_images"]
        df["RA_very_small_images/total_images"] = df["very_small_images"] / df["total_images"]
        df["RA_total_images/total_length"] = df["total_images"] / df["total_length"]
        df["RA_big_and_middle_images/total_length"] = (df["big_images"] + df["middle_images"]) / df["total_length"]
        df["RA_internal_links/external_links"] = df["internal_links"] / df["external_links"]
        df["RA_headings/total_length"] = df["headings"] / df["total_length"]
        return df
   
    def openDataDict_(self):
        try:
            with open("merged_data_dict.pickle", "rb") as f:
                dd_ = pickle.load(f)
            if dd_:
                return dd_
            else:
                raise Exception("Sorry, merged_data_dict.pickle needs to be present in folder! Create first with DataPreparation() class!")
        except:
            raise Exception("Sorry, a problem occurred! Remember that merged_data_dict.pickle needs to be present in folder! Create first with DataPreparation() class!")

    def showWebsitesInCluster_(self, clustered_df):
        '''
        PRIVATE method: show websites ordered by cluster; part of clusteringKMeans()
        '''
        with open("websites.csv", "r", encoding="utf-8") as f:
            orig_websites = f.readlines()
        clusters = np.sort(clustered_df["clusters"].unique())
        for cluster in clusters:
            print(f"Websites in cluster {cluster}:")
            print("-----------------------------------------------")
            print()
            for row in clustered_df[clustered_df["clusters"] == cluster].iterrows():
                print(row[0])
                for website in orig_websites:
                    if row[0] in website:
                        print(website.split(",")[0])
            print()
        

    # public methods


    def getScreenshotsFromClusters(self, clustered_df):
        '''
        this method saves a screenshot from each website in Screenshots/<Cluster>
        '''
        shutil.rmtree("Screenshots")
        os.makedirs("Screenshots")
        cluster_list = clustered_df["clusters"].unique()
        for cluster in cluster_list:
            os.makedirs(f"Screenshots/{cluster}")
        browser = webdriver.Edge("webdriver/msedgedriver.exe")
        with open("websites.csv", "r", encoding="utf-8") as f:
            orig_websites = f.readlines()
        for _, row in clustered_df.iterrows():
            print(row.name)
            row_cluster = int(row["clusters"])
            print(row_cluster)
            for website in orig_websites:
                if row.name in website:
                    original_website = website.split(",")[0]
            browser.get(original_website)
            browser.maximize_window()
            browser.implicitly_wait(5)
            input("Press press any key to take screenshot of current website...")
            print(f"Screenshots/{row_cluster}/{row.name}.png")
            browser.save_screenshot(f"Screenshots/{row_cluster}/{row.name}.png")
        browser.quit()
        

    def getColumnSelection(self):
        '''
        returns the currently set columns for KMeans standardization and clustering process; can be reset with setColumnSelection(); DEFAULT = all columns
        '''
        print(f"Currently, the following columns are selected: {self.column_selection}")

    def getDataFrame(self):
        '''
        returns the dataframe self.data_df based on current column selection
        '''
        return self.data_df[self.column_selection]   

    def getFullDataFrame(self):
        '''
        returns full dataframge with all columns
        '''
        return self.data_df
        
    def clusterDataKMeans(self, df_scaled, n=3):
        '''
        clustering data with K-Means
        '''
        kmeans = KMeans(n_clusters=n, random_state=42)
        kmeans.fit(df_scaled)
        df_cp = df_scaled.copy()
        df_cp["clusters"] = kmeans.labels_
        self.showWebsitesInCluster_(df_cp)
        return df_cp

    def createElbowPlot(self, df):
        '''
        create an elbow plot for a dataframe
        '''
        cluster_range = list(range(2,9))
        inertia_list = []
        print(f"Creating elbow plot in range between {cluster_range} n for KMeans.")
        for k in cluster_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(df)
            inertia_list.append(kmeans.inertia_)
        # plotting
        fig = plt.figure(figsize=(7,7))
        ax = fig.add_subplot(111)
        sns.lineplot(y=inertia_list, x=cluster_range, ax=ax)
        ax.set_xlabel("Clusters")
        ax.set_ylabel("Inertia")
        ax.set_xticks(cluster_range)
        plt.show()

    def setColumnSelection(self, list_):
        '''
        allows to set columns from self.data_df that should be included in the KMeans standardization and clustering process; DEFAULT is all columns are selected
        '''
        self.column_selection = list_
        print("Columns successfully changed!")

    def standardizeData(self, df_orig):
        '''
        standardize data with the help of sklearn's StandardScaler() class
        '''
        scaler = SS()
        scaled_columns = scaler.fit_transform(df_orig[self.column_selection])
        df_cp = df_orig[self.column_selection].copy()
        for num, column in enumerate(self.column_selection):
            df_cp[column + "_scaled"] = scaled_columns[:,num]
        return df_cp.iloc[:,len(self.column_selection):]

    def visualizeCluster(self, clustered_df, column1, column2):
        '''
        visualize a cluster based on two columns
        '''
        sns.scatterplot(x=column1, y=column2, hue="clusters", data=clustered_df)
