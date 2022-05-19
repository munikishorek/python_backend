from numpy.lib.mixins import _inplace_binary_method
import pandas as pd
import numpy as np
from sklearn.externals import joblib
def awake_state_prediction(ai_list):
    td = pd.to_numeric(ai_list, errors='coerce')
    test_data = pd.DataFrame(td).T
    test_data = test_data.apply(pd.to_numeric, errors="ignore")
    test_data = test_data.fillna(test_data.mean())
    X_test = test_data

    IF = joblib.load('IF1_64bit.sav')

    test_pred = IF.predict(X_test)

    return test_pred
def awake_state_prediction_2(ai_list):
    td = pd.to_numeric(ai_list, errors='coerce')
    test_data = pd.DataFrame(td).T
    test_data = test_data.apply(pd.to_numeric, errors="ignore")
    test_data = test_data.fillna(test_data.mean())
    test_data = test_data.astype(np.int64)
    X_test = test_data

    RF = joblib.load('RF_AWAKE.sav')
    [[sleeping_cs,awake_cs]] = RF.predict_proba(X_test)

    test_pred = RF.predict(X_test)
    act_pred = 1
    if test_pred == 1:
        act_pred = -1
    else:
        act_pred = 1

    return act_pred, awake_cs

def nic_state_prediction(NIC_list):
    test_data = pd.DataFrame(NIC_list).T
    test_data = test_data.apply(pd.to_numeric, errors="ignore")
    test_data = test_data.fillna(test_data.mean())
    X_test = test_data
    GB = joblib.load('RF_NIC.sav')
    test_pred = GB.predict(X_test)
    [[sleeping_cs,nic_cs]] = GB.predict_proba(X_test).tolist()

    return test_pred, nic_cs


def add_baby_monitor_data_to_cloud(ai_data):
    sleep_prediction_ai_list = [
                ai_data['fa1'],
                ai_data['fa2'],
                ai_data['fb1'],
                ai_data['fb2'],
                ai_data['max_amp'],
                ai_data['Br_freq_rpm'],
                ai_data['sd_peak1_bin'],
                ai_data['sd_whole']
            ]
    if ai_data.get('nic_features',None) and ai_data['nic_features'] != [] and ai_data.get('entropy',None) and ai_data['entropy']!=None:
        bin_num = ai_data['peak1_bin']+7
        bin_range = 1
        if bin_num<10:
            bin_range = 1
        elif bin_num>=10 and bin_num<20:
            bin_range = 2
        elif bin_num>=20 and bin_num<30:
            bin_range = 3
        else:
            bin_range = 4
        a,b,c,d,e,f,g,h = ai_data['nic_features']
        fa1,fa2,fb1,fb2,sd_whole,max_amp,Br_freq_rpm,sd_peak1_bin = ai_data['fa1'],ai_data['fa2'],ai_data['fb1'],ai_data['fb2'],ai_data['sd_whole'],ai_data['max_amp'],ai_data['Br_freq_rpm'],ai_data['sd_peak1_bin']
        awake_prediction_ai_list = [ai_data['entropy'],ai_data['periodic'],bin_range,a,b,c,d,e,f,g,h,fa1,fa2,fb1,fb2,sd_whole,max_amp,Br_freq_rpm,sd_peak1_bin]
    
        try:
            awake_prediction,awake_cf = awake_state_prediction_2(awake_prediction_ai_list)
            print(awake_prediction)
        except Exception as e:
            print(e)
            print('87')
            awake_prediction, awake_cf = None, None

        awake_prediction = [awake_prediction]
    else:
        try:
            awake_prediction = awake_state_prediction(sleep_prediction_ai_list)
            print(awake_prediction)
        except Exception as e:
            print(e)
            print('95')
            awake_prediction = None
        awake_cf = None

    # # Calculate NIC Prediction
    if ai_data.get('nic_features',None) and ai_data['nic_features'] != []:
        fa1,fa2,fb1,fb2,sd_whole,max_amp,Br_freq_rpm,sd_peak1_bin = ai_data['fa1'],ai_data['fa2'],ai_data['fb1'],ai_data['fb2'],ai_data['sd_whole'],ai_data['max_amp'],ai_data['Br_freq_rpm'],ai_data['sd_peak1_bin']
        a,b,c,d,e,f,g,h = ai_data['nic_features']
        nic_prediction_ai_list = [a,b,c,d,e,f,g,h,fa1,fa2,fb1,fb2,sd_whole,max_amp,Br_freq_rpm,sd_peak1_bin]

        #Internal test case
        # if device.mac_address in CF_TEST_DEVICES:
        try:
            nic_prediction,nic_cf = nic_state_prediction(nic_prediction_ai_list)
            nic_prediction = list(nic_prediction)
        except Exception as e:
            print(e)
            print('110')
            nic_prediction, nic_cf = None, None

    else:
        nic_prediction = None
        nic_cf = None

    return {'data':{'awake_prediction':awake_prediction, 'nic_prediction':nic_prediction,"nic_cf":nic_cf}}