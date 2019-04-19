import re


def getSchoolName(s):
    re_str = '([\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+)|(\d+|q+)'
    s = re.sub(re_str, '', s)
    # s = re.sub('', '', s)
    # s = s.replace('qq', '')
    return s
    # s = s.strip()
    # s = re.split("[ \n]", s)
    # s = s[0]
    # result = ''
    # for i in s:
    #     if is_chinese(i):
    #         result = result + i
    #     else:
    #         break
    # return result


def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

