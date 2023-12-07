from dotenv import load_dotenv
import os

'''
Здесь хранятся переменные id, используемые в методах.
'''

load_dotenv()

# Для Реестров
per_page_store = os.environ.get('PER_PAGE')

# Для taxes_rout.py
taxes_percent = os.environ.get('TAXES_PERCENT')   # Налоговая ставка Организации
tax_exp_category_id = os.environ.get('TAX_EXP_CATEGORY_ID')
agent_exp_category_id = os.environ.get('AGENT_EXP_CATEGORY_ID')
loan_repay_exp_category_id = os.environ.get('LOAN_REPAY_EXP_CATEGORY_ID')

# Для section_card_debtor
section_card_id_main = os.environ.get('SECTION_CARD_ID_MAIN')
section_card_id_cd = os.environ.get('SECTION_CARD_ID_CD')
section_card_id_tribun = os.environ.get('SECTION_CARD_ID_TRIBUN')
section_card_id_realty = os.environ.get('SECTION_CARD_ID_REALTY')
section_card_id_pass = os.environ.get('SECTION_CARD_ID_PASS')

# Для type_ed
type_ed_id_ilb = os.environ.get('TYPE_ED_ID_ILB')
type_ed_id_ile = os.environ.get('TYPE_ED_ID_ILE')
type_ed_id_sp = os.environ.get('TYPE_ED_ID_SP')
type_ed_id_nn = os.environ.get('TYPE_ED_ID_NN')
type_ed_id_sogl = os.environ.get('TYPE_ED_ID_SOGL')

# Для status_cd
status_cd_none = os.environ.get('STATUS_CD_NONE')
status_cd_isp = os.environ.get('STATUS_CD_ISP')
status_cd_rab = os.environ.get('STATUS_CD_RAB')
status_cd_otm = os.environ.get('STATUS_CD_OTM')
status_cd_sogl = os.environ.get('STATUS_CD_SOGL')
status_cd_pgsh = os.environ.get('STATUS_CD_PGSH')
status_cd_pgsh_cess = os.environ.get('STATUS_CD_PGSH_CESS')
status_cd_pgsh_pp = os.environ.get('STATUS_CD_PGSH_PP')
status_cd_bnkr = os.environ.get('STATUS_CD_BNKR')

# Для status_ed
status_ed_none = os.environ.get('STATUS_ED_NONE')
status_ed_mov_8 = os.environ.get('STATUS_ED_MOV_8')
status_ed_mov_9 = os.environ.get('STATUS_ED_MOV_9')
status_ed_mov_ifns = os.environ.get('STATUS_ED_MOV_ROSP')
status_ed_mov_sud = os.environ.get('STATUS_ED_SUD_OPIS')
