
import pandas as pd
import numpy as np

def data_frame_organise(input):
    df = input
    del df["Order_ID"]
    del df["Event_Type"]
    df["DateTime"] = pd.to_datetime(df["DateTime"], format='%Y-%m-%d %H:%M:%S:%f')
    df.set_index(df["DateTime"], inplace=True)
    del df["DateTime"]
    df = df.between_time('10:00', '15:30')
    df = df.resample("100ms").mean()
    df = df.fillna(method='ffill')  # Forward fill
    df["Price"] = df["Price"]/10000
    df["Mid"] = (df["Ask_Price_Level_1"] + df["Bid_Price_Level_1"]) /2
    df["Spread"] = df["Ask_Price_Level_1"] - df["Bid_Price_Level_1"]
    df["Return"] = np.log(df["Price"]/df["Price"].shift(1))
    df["Return"].iloc[0] = 0
    df["Price_Direction"] = np.sign(df["Return"].round(4))
    df["Target"] = np.sign(df["Return"].round(4)).shift(-1)
    df["Target"].iloc[-1] = 0 
    for i in range(1,11):
        df[f"Relative_Ask_Price_Level_{i}"] = (df[f"Ask_Price_Level_{i}"] - df["Mid"]) / df["Mid"]
        df[f"Relative_Bid_Price_Level_{i}"] = (df[f"Bid_Price_Level_{i}"] - df["Mid"]) / df["Mid"]
        df[f"Log_Ask_Volume_Level_{i}"] = np.log(1+df[f"Ask_Volume_Level_{i}"])
        df[f"Log_Bid_Volume_Level_{i}"] = np.log(1+df[f"Bid_Volume_Level_{i}"])
    return df

def create_image_updown_vol(t,lookback,df):
    
    height = 50
    width = 3 * lookback # lookback = 1s
    grid = np.zeros((height,width))
    width = width + 2
    origin = df.iloc[t]["Price"]
    max_vols = np.zeros(lookback)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        #print(row.name)
        w_offset = width-(3*w)-1
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        for i in range(1,11):
            ask_vol_i = row[f"Log_Ask_Volume_Level_{i}"]
            bid_vol_i = row[f"Log_Bid_Volume_Level_{i}"]
            fix = (h_offset+mid+(i-1))
            if fix >= height:
                fix = height - 1
            grid[(h_offset+mid-(i)),w_offset+1] = ask_vol_i
            grid[fix,w_offset-1] = bid_vol_i
            largest = max(ask_vol_i,bid_vol_i)
            current = max_vols.max()
            max_vols[w-1] = max(largest,current)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        w_offset = width-(3*w)-1
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        grid[(h_offset+mid-10):(h_offset+mid+10),w_offset] = max_vols.max()
    return grid






def create_image_side_vol(t,lookback,df):
    
    height = 50
    width = 3 * lookback 
    grid = np.zeros((height,width))
    width = width + 2
    origin = df.iloc[t]["Price"]
    max_vols = np.zeros(lookback)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        #print(row.name)
        w_offset = width-(3*w)-1
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        for i in range(1,11):
            ask_vol_i = row[f"Log_Ask_Volume_Level_{i}"]
            bid_vol_i = row[f"Log_Bid_Volume_Level_{i}"]
            grid[(h_offset+int(np.floor(mid/2))-(i)),w_offset+1] = ask_vol_i
            grid[(h_offset+int(np.floor(mid/2))-(i-1)),w_offset-1] = bid_vol_i
            largest = max(ask_vol_i,bid_vol_i)
            current = max_vols.max()
            max_vols[w-1] = max(largest,current)

    return grid



def create_image_updown_price(t,lookback,df):
    
    height = 20
    width = lookback 
    grid = np.zeros((height,width))
    width = width + 2
    origin = df.iloc[t]["Price"]
    max_vols = np.zeros(lookback)

    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        w_offset = w-1
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        grid[mid,w_offset] = row["Price"]
    return grid





def create_image_updown_vol_mid(t,lookback,df):
    
    height = 50
    width = 3 * lookback # lookback = 1s
    grid = np.zeros((height,width))
    width = width + 2
    origin = df.iloc[t]["Price"]
    max_vols = np.zeros(lookback)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        #print(row.name)
        w_offset = width-(3*w)-1
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        fix = (h_offset+mid)
        if fix>= height:
            fix = height - 1
        for i in range(1,11):
            ask_vol_i = row[f"Log_Ask_Volume_Level_{i}"]
            bid_vol_i = row[f"Log_Bid_Volume_Level_{i}"]
            fix_down = h_offset+mid-i
            if fix_down >= height:
                fix_down = height-i
            grid[(fix_down),w_offset] = ask_vol_i
            if fix+i >=height:
                fix = height-1
                grid[fix,w_offset] = bid_vol_i
            else:
                grid[fix+i,w_offset] = bid_vol_i
            current = max_vols.max()
            largest = max(ask_vol_i,bid_vol_i)
            max_vols[w-1] = max(largest,current)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        w_offset = width-(3*w)-1
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        grid[h_offset+mid,w_offset] = max_vols.max()
    return grid



def create_image_updown_vol_mid_triple_l10(t,lookback,df):
    
    height = 50
    width = lookback # lookback = 1s
    grid = np.zeros((height,width,3))
    width = width + 2
    origin = df.iloc[t]["Price"]
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        #print(row.name)
        w_offset = width-w-2
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        for i in range(1,11):
            fix = (h_offset+mid)
            if fix>= height:
                fix = height - 1 - i
            ask_vol_i = row[f"Log_Ask_Volume_Level_{i}"]
            bid_vol_i = row[f"Log_Bid_Volume_Level_{i}"]
            fix_down = h_offset+mid-i
            if fix_down >= height:
                fix_down = height-i
            grid[(fix_down),w_offset,0] = ask_vol_i
            if fix+i >=height:
                fix = height-1
                grid[fix,w_offset,2] = bid_vol_i
            else:
                grid[fix+i,w_offset,2] = bid_vol_i

    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        w_offset = width-w-2
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        mid_fix = h_offset+mid
        if mid_fix>= height:
            mid_fix = height -1
        grid[mid_fix,w_offset,1] = 1
    return grid


def create_image_updown_vol_mid_triple_l5(t,lookback,df):
    
    height = 35
    width = lookback # lookback = 1s
    grid = np.zeros((height,width,3))
    width = width + 2
    origin = df.iloc[t]["Price"]
    max_vols = np.zeros(lookback)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        #print(row.name)
        w_offset = width-w-2
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        for i in range(1,6):
            fix = (h_offset+mid)
            ask_vol_i = row[f"Log_Ask_Volume_Level_{i}"]
            bid_vol_i = row[f"Log_Bid_Volume_Level_{i}"]
            fix_down = h_offset+mid-i
            if fix_down >= height:
                fix_down = height-i
            grid[(fix_down),w_offset,0] = ask_vol_i
            if fix+i >=height:
                fix = height-1
                grid[fix,w_offset,2] = bid_vol_i
            else:
                grid[fix+i,w_offset,2] = bid_vol_i
            largest = max(ask_vol_i,bid_vol_i)
            current = max_vols.max()
            max_vols[w-1] = max(largest,current)
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        w_offset = width-w-2
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        mid_fix = h_offset+mid
        if mid_fix>= height:
            mid_fix = height -1
        grid[mid_fix,w_offset,1] = 1
    return grid



def create_image_updown_vol_mid_triple_l3(t,lookback,df):
    
    height = 25
    width = lookback # lookback = 1s
    grid = np.zeros((height,width,3))
    width = width + 2
    origin = df.iloc[t]["Price"]
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        #print(row.name)
        w_offset = width-w-2
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        for i in range(1,4):
            fix = (h_offset+mid)
            if fix>= height:
                fix = height - 1
            ask_vol_i = row[f"Log_Ask_Volume_Level_{i}"]
            bid_vol_i = row[f"Log_Bid_Volume_Level_{i}"]
            fix_down = h_offset+mid-i
            if fix_down >= height:
                fix_down = height-i
            grid[(fix_down),w_offset,0] = ask_vol_i
            if fix+i >=height:
                fix = height-1
                grid[fix,w_offset,2] = bid_vol_i
            else:
                grid[fix+i,w_offset,2] = bid_vol_i
    for w in range(1,lookback+1):
        row = df.iloc[t-w+1]
        w_offset = width-w-2
        direction = np.sum(df["Price_Direction"][t-w:t-w+1])
        mid = int(np.floor(height/2))+int(direction.sum())
        h_offset = int(((10000*(origin - row["Price"])/origin)+1).round(1))
        mid_fix = h_offset+mid
        if mid_fix>= height:
            mid_fix = height -1
        grid[mid_fix,w_offset,1] = 1
    return grid

