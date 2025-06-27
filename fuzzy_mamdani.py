import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from firebase_connector import FirebaseConnector
from bot_telegram import TelegramBot

class FuzzyMamdani:
    def __init__(self, firebase_cred_path, firebase_database_url, bot_token, chat_id): 
        self.firebase_connector = FirebaseConnector(firebase_cred_path, firebase_database_url)
        self.telegram_bot = TelegramBot(bot_token, chat_id)

        self.suhu_air = ctrl.Antecedent(np.arange(0, 40, 0.1), 'suhu_air')
        self.ph_air = ctrl.Antecedent(np.arange(0, 15, 0.1), 'ph_air')
        self.cahaya = ctrl.Antecedent(np.arange(0, 100, 1), 'cahaya')
        self.co2 = ctrl.Antecedent(np.arange(300, 2000, 1), 'co2')
        self.kondisi = ctrl.Consequent(np.arange(0, 101, 1), 'kondisi')

        self.define_membership_functions()

        self.define_rules()

        self.kondisi_ctrl = ctrl.ControlSystem(self.rules)
        self.kondisi_simulator = ctrl.ControlSystemSimulation(self.kondisi_ctrl)

    def define_membership_functions(self):
        self.suhu_air['dingin'] = fuzz.trapmf(self.suhu_air.universe, [0, 0, 16, 18])
        self.suhu_air['ideal'] = fuzz.trapmf(self.suhu_air.universe, [16, 18, 23, 25 ])
        self.suhu_air['panas'] = fuzz.trapmf(self.suhu_air.universe, [23, 25, 40, 40])

        self.ph_air['asam'] = fuzz.trapmf(self.ph_air.universe, [0, 0, 5.0, 5.5])
        self.ph_air['ideal'] = fuzz.trapmf(self.ph_air.universe, [5.0, 5.5 ,6.5, 7.0])
        self.ph_air['basa'] = fuzz.trapmf(self.ph_air.universe, [6.5, 7.0, 14, 14])

        self.cahaya['redup'] = fuzz.trapmf(self.cahaya.universe, [0, 0, 50, 60])
        self.cahaya['ideal'] = fuzz.trapmf(self.cahaya.universe, [50, 60 ,80, 90])
        self.cahaya['terang'] = fuzz.trapmf(self.cahaya.universe, [80, 90, 100, 100])

        self.co2['rendah'] = fuzz.trapmf(self.co2.universe, [300, 300, 700, 800])
        self.co2['ideal'] = fuzz.trapmf(self.co2.universe, [700, 800,1200, 1300])
        self.co2['tinggi'] = fuzz.trapmf(self.co2.universe, [1200, 1300, 2000, 2000])

        self.kondisi['buruk'] = fuzz.trapmf(self.kondisi.universe, [0, 0, 40, 55])
        self.kondisi['cukup'] = fuzz.trapmf(self.kondisi.universe, [40, 55, 60, 75])
        self.kondisi['baik'] = fuzz.trapmf(self.kondisi.universe, [60, 75, 100,100])
        self.kondisi.defuzzify_method = 'mom'
    def define_rules(self):
        self.rules = [
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['dingin'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['baik']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['ideal'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['asam'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['cukup']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['ideal'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['redup'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['ideal'] & self.co2['tinggi'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['rendah'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['ideal'], self.kondisi['buruk']),
                        ctrl.Rule(self.suhu_air['panas'] & self.ph_air['basa'] & self.cahaya['terang'] & self.co2['tinggi'], self.kondisi['buruk']),
        ]
    def calculate_fuzzy(self):
        data = self.firebase_connector.get_data('sensor')  
        if data:
            suhu_air_value = data.get('suhu_air', 0)
            ph_air_value = data.get('ph_air', 0)
            cahaya_value = data.get('cahaya', 0)
            co2_value = data.get('co2', 0)
            
            self.kondisi_simulator.input['suhu_air'] = suhu_air_value
            self.kondisi_simulator.input['ph_air'] = ph_air_value
            self.kondisi_simulator.input['cahaya'] = cahaya_value
            self.kondisi_simulator.input['co2'] = co2_value
            
            self.kondisi_simulator.compute()
    
            kondisi_output = self.kondisi_simulator.output['kondisi']
            return kondisi_output
        else:
            return None
    def get_linguistic_label(self, variable, value):
        memberships = {}
        for term_name, term_mf in variable.terms.items():
            membership_value = fuzz.interp_membership(variable.universe, term_mf.mf, value)
            memberships[term_name] = membership_value
        
        if not memberships or max(memberships.values()) == 0:
            return "Tidak Terdefinisi" 
        
        return max(memberships, key=memberships.get)
    def get_linguistic_condition(self, kondisi_value):
        derajat_buruk = fuzz.interp_membership(self.kondisi.universe, self.kondisi['buruk'].mf, kondisi_value)
        derajat_cukup = fuzz.interp_membership(self.kondisi.universe, self.kondisi['cukup'].mf, kondisi_value)
        derajat_baik = fuzz.interp_membership(self.kondisi.universe, self.kondisi['baik'].mf, kondisi_value)
    
        if derajat_baik > derajat_cukup and derajat_baik > derajat_buruk:
            return "Baik"
        elif derajat_cukup > derajat_buruk:
            return "Cukup"
        else:
            return "Buruk"


if __name__ == "__main__":
    BOT_TOKEN = "8186150981:AAETswpM_IWkURVryb-RMXWsqNd7RB0dm6I"
    CHAT_ID = 1099636525
    FIREBASE_CRED_PATH = 'greenhouse.json'  
    FIREBASE_DATABASE_URL = 'https://kondisigreenhouse-default-rtdb.asia-southeast1.firebasedatabase.app/'  

    fuzzy_mamdani = FuzzyMamdani(FIREBASE_CRED_PATH, FIREBASE_DATABASE_URL, BOT_TOKEN, CHAT_ID)
    fuzzy_mamdani.calculate_fuzzy()
