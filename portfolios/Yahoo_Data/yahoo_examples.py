from yahoo_downloader import download_data

yahoo_tkrlst = ['VAS.AX','VLC.AX','VSO.AX','VHY.AX','BOND.AX','ILB.AX','RSM.AX','RGB.AX','VGS.AX','BNDX','VTS.AX','IUSB','FTAL.L','SLXX.L','IJP.AX','IEU.AX','IEAG.L','AAXJ','ALD','MCHI','DSUM','VGE.AX','EMB'] 

start_date = '2010-4-10'
end_date = '2015-11-24'

## Example 1
rtndf = download_data(yahoo_tkrlst, start_date, end_date)  # daily return dataframe 
prcdf = download_data(yahoo_tkrlst, start_date, end_date, rtn_flag=False) # daily price dataframe

