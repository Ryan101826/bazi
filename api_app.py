from flask import Flask, request, jsonify
import sxtwl
from datetime import datetime

app = Flask(__name__)

# 值符字典、省略部分重复的代码
zifu_dict = {
    "子": "值符", "丑": "太阳", "寅": "伤符", "卯": "太阴",
    "辰": "官符", "巳": "死符", "午": "破碎", "未": "福德",
    "申": "白虎", "酉": "龙德", "戌": "吊客", "亥": "病符"
}

yao_dict = {
    "一爻": ["甲子", "乙未", "丙辰", "丁巳", "戊寅", "己卯", "庚子", "辛丑", "壬子", "癸未"],
    "二爻": ["甲寅", "乙巳", "丙午", "丁卯", "戊辰", "己丑", "庚寅", "辛亥", "壬寅", "癸巳"],
    "三爻": ["甲辰", "乙卯", "丙申", "丁丑", "戊午", "己亥", "庚辰", "辛酉", "壬辰", "癸卯"],
    "四爻": ["甲午", "乙丑", "丙戌", "丁亥", "戊申", "己酉", "庚午", "辛未", "壬午", "癸丑"],
    "五爻": ["甲申", "乙亥", "丙子", "丁酉", "戊戌", "己未", "庚申", "辛巳", "壬申", "癸亥"],
    "六爻": ["甲戌", "乙酉", "丙寅", "丁未", "戊子", "己巳", "庚戌", "辛卯", "壬戌", "癸酉"]
}

xun_dict = {
    "甲子": ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉"],
    "甲戌": ["甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未"],
    "甲申": ["甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳"],
    "甲午": ["甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯"],
    "甲辰": ["甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑"],
    "甲寅": ["甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥"]
}

tg = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
dz = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def query_bazi(calendar_type, year, month, day, hour):
    if calendar_type == "阳历":
        solar_date = sxtwl.fromSolar(int(year), int(month), int(day))
    else:
        solar_date = sxtwl.fromLunar(int(year), int(month), int(day))

    y = solar_date.getYearGZ()
    m = solar_date.getMonthGZ()
    d = solar_date.getDayGZ()
    h = solar_date.getHourGZ(int(hour))

    bazi_result = [tg[y.tg], dz[y.dz], tg[m.tg], dz[m.dz], tg[d.tg], dz[d.dz], tg[h.tg], dz[h.dz]]
    gan_zhi = [bazi_result[i] + bazi_result[i+1] for i in range(0, 8, 2)]

    def get_yao_position(gz):
        for yao, lst in yao_dict.items():
            if gz in lst:
                return yao
        return "未知"

    def get_xun(gz):
        for xun, lst in xun_dict.items():
            if gz in lst:
                return xun
        return "未知"

    def get_zifu(dz_branch, xun):
        if xun == "未知":
            return "未知"
        start_index = dz.index(xun_dict[xun][0][1])
        zifu_index = (dz.index(dz_branch) - start_index + len(dz)) % len(dz)
        return zifu_dict.get(dz[zifu_index], "未知")

    xun_birth = get_xun(gan_zhi[0])
    yao_list = [get_yao_position(gz) for gz in gan_zhi]
    zifu_list = [get_zifu(bazi_result[i+1], xun_birth) for i in range(0, 8, 2)]

    now = datetime.now()
    curr = sxtwl.fromSolar(now.year, now.month, now.day)
    curr_gz = tg[curr.getYearGZ().tg] + dz[curr.getYearGZ().dz]
    curr_xun = get_xun(curr_gz)
    zifu_now = [get_zifu(bazi_result[i+1], curr_xun) for i in range(0, 8, 2)]

    return {
        "bazi": bazi_result,
        "gan_zhi": gan_zhi,
        "yao": yao_list,
        "xun_birth": xun_birth,
        "zifu_birth": zifu_list,
        "zifu_now": zifu_now
    }

@app.route("/api/bazi", methods=["POST"])
def bazi_api():
    data = request.get_json()
    try:
        calendar_type = data["calendar"]
        year = data["year"]
        month = data["month"]
        day = data["day"]
        hour = data["hour"]
    except KeyError:
        return jsonify({"error": "缺少参数"}), 400

    result = query_bazi(calendar_type, year, month, day, hour)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
