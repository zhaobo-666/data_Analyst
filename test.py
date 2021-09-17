import re
a = "12!@#$^'。？》'\""

# 过滤特殊字符
def filter_str(desstr):
    # 过滤除中英文及数字以外的其他字符
    sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", desstr)
    return sub_str

print(filter_str(a))