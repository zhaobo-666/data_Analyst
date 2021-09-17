import pandas as pd
import xlrd
import os
from openpyxl import load_workbook


class MergeCell(object):
    def __init__(self, file_obj):
        self.datas = pd.read_excel(file_obj, sheet_name=None)
        self.new_file = str(file_obj).split('.')[0]
        self.sheet_col = self.datas.keys()
        self.file_obj = file_obj

    def get_merge(self, xls_obj, sheet_name):
        try:
            te = xlrd.open_workbook(xls_obj, formatting_info=True)
        except Exception as e:
            print(e)
            te = xlrd.open_workbook(xls_obj)
        sh = te.sheet_by_index(sheet_name)
        merge = sh.merged_cells
        print(merge)
        return merge

    def replensh_xlsx(self, xls_obj, sheet_l):
        merge_list = self.get_merge(xls_obj, sheet_l)
        df = pd.read_excel(xls_obj, sheet_name=sheet_l)
        for i in merge_list:
            df.iloc[i[0] - 1:i[1] - 1, i[2]:i[3]] = df.iloc[i[0] - 1:i[1] - 1, i[2]:i[3]].ffill()
            df.iloc[i[0] - 1:i[1] - 1, i[2]:i[3]] = df.iloc[i[0] - 1:i[1] - 1, i[2]:i[3]].ffill(axis='columns')
        print(df)
        return df

    def run_merge(self):
        writer = pd.ExcelWriter(self.new_file + '_new.xlsx')
        for i in self.sheet_col:
            sheet_len = 0
            print(i)
            ddf = self.replensh_xlsx(self.file_obj, sheet_len)
            ddf.to_excel(excel_writer=writer, sheet_name=i, index=False, header=True)
            sheet_len += 1
        os.remove(self.file_obj)
        writer.save()
        writer.close()


meg = MergeCell(r'D:\desk\v-music\test4.xlsx')
meg.run_merge()
