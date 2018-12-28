# -=-=-=-=-=-=-=-=-=-=-=
# coding=UTF-8
# __author__='Guo Jun'
# Version 1..0.0
# -=-=-=-=-=-=-=-=-=-=-=

from ConnectDB import connDB, connClose, get_all_data
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np


def calc_gm(g, m, start_date, end_date):
    conn, cur = connDB()

    price_sql = 'select a.*, b.m_close from (select date, close as g_close from stk_price_forward where symbol =\'000651.SZ\' ) a inner join (select date,  close as m_close from stk_price_forward where symbol =\'000333.SZ\' ) b on a.date =b.date where a.date > \'' + start_date + '\' and a.date <= \'' + end_date + '\'order by a.date asc'
    try:
        cur.execute(price_sql)
        db_data = cur.fetchall()
    except Exception as e:
        print(e)

    df_price = pd.DataFrame(list(db_data), columns=['date','g_close','m_close'])
    hold_signal = []
    hold_return = [0]
    hold_cl_ret = [1]
    g_cl_ret = [1]
    m_cl_ret = [1]
    gm_cl_ret= [1]
    max_dd = [0]

    ## 持仓换仓信号，g为格力电器，m为美的集团
    for i in range(len(df_price)):
        if float(df_price['g_close'].iloc[i]) > (1-m) * float(df_price['m_close'].iloc[i]):
            hold_signal.append(m)
        elif float(df_price['g_close'].iloc[i]) < (1-g) * float(df_price['m_close'].iloc[i]):
            hold_signal.append(g)
        else:
            hold_signal.append(0)

    ## 补充持仓信号，确保换仓后持仓信号的一致性
    for j in range(1, len(hold_signal)):
        if hold_signal[j] == 0:
            hold_signal[j] = hold_signal[j - 1]

    ## 计算策略组合的每日收益
    for k in range(1, len(hold_signal)):
        if hold_signal[k - 1] == g:
            hold_return.append((float(df_price['g_close'].iloc[k]) - float(df_price['g_close'].iloc[k - 1])) / float(
                df_price['g_close'].iloc[k - 1]) * 100)
        elif hold_signal[k - 1] == m:
            hold_return.append((float(df_price['m_close'].iloc[k]) - float(df_price['m_close'].iloc[k - 1])) / float(
                df_price['m_close'].iloc[k - 1]) * 100)
        else:
            hold_return.append(0)

    ## 计算其他情况的累计收益
    for h in range(1, len(hold_return)):
        hold_cl_ret.append(hold_cl_ret[h - 1] * (1 + hold_return[h] / 100))
        g_cl_ret.append(round(df_price['g_close'].iloc[h] / df_price['g_close'].iloc[0],6))
        m_cl_ret.append(round(df_price['m_close'].iloc[h] / df_price['m_close'].iloc[0],6))
        gm_cl_ret.append(0.5*float(df_price['g_close'].iloc[h] / df_price['g_close'].iloc[0]) + 0.5*float(df_price['m_close'].iloc[h] / df_price['m_close'].iloc[0]))

    ## 计算每日最大回撤
    for x in range(1,len(hold_cl_ret)):
        temp = (hold_cl_ret[x] - max(hold_cl_ret[0:x])) / max(hold_cl_ret[0:x])
        if temp <= 0:
            max_dd.append(temp)
        else:
            max_dd.append(0)

    max_draw_down = str(round(min(max_dd) * 100, 2)) + '%' # 获得最大回测

    df_price['hold_signal'] = pd.DataFrame(hold_signal) # 持有信号，g为格力电器，m为美的集团
    df_price['hold_return'] = pd.DataFrame(hold_return) # 持有的日收益
    df_price['hold_cl_ret'] = pd.DataFrame(hold_cl_ret) # 持仓的累计收益
    df_price['g_cl_ret'] = pd.DataFrame(g_cl_ret) # 单持有格力电器的累计收益
    df_price['m_cl_ret'] = pd.DataFrame(m_cl_ret) # 单持有美的集团的累计收益
    df_price['gm_cl_ret'] = pd.DataFrame(gm_cl_ret) # 持有格力电器和美的集团各50%仓位的组合累计收益
    df_price['max_dd'] = pd.DataFrame(max_dd) # 每日的最大回测数据

    # for s in range(0,len(df_price)):
    #     print(df_price.iloc[s])

    # 计算总收益率和年化收益率
    total_return = str(round((hold_cl_ret[-1] - 1) * 100, 2)) + '%'
    annualized_return = str(
        round((hold_cl_ret[-1] ** (365.25 / (datetime.today() - datetime.strptime(start_date, '%Y-%m-%d')).days) - 1) * 100,
              2)) + '%'


    connClose(conn, cur)
    print(str(g) + ' & ' + str(m) + ': ' + total_return + ', ' + annualized_return + ', ' + max_draw_down)

    # 做图
    x = np.array(df_price['date'])
    y1 = np.array(df_price['hold_cl_ret'])
    y2 = np.array(df_price['g_cl_ret'])
    y3 = np.array(df_price['m_cl_ret'])
    y4 = np.array(df_price['gm_cl_ret'])
    y5 = np.array(df_price['max_dd'])
    plt.figure(figsize=(9, 6))

    ## 收益子图
    plt.subplot(211)
    plt.plot(x, y1, 'r', label='Cigrg_006')
    plt.plot(x, y2, 'm', label='000651', linewidth=0.7)
    plt.plot(x, y3, 'g', label='000333', linewidth=0.7)
    plt.plot(x, y4, 'y', label='0.5*[000651,000333]', linewidth=0.7)
    plt.grid(True)
    plt.axis('tight')
    plt.ylabel('Return')
    pic_txt = 'Cumulative Return for Cigrg_006: ' + start_date + ' ~ ' + end_date
    plt.legend(loc='upper left', frameon=False)
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=11.5, weight='bold')
    plt.title(pic_txt, loc ='left', fontproperties=font_set )

    ## 最大回撤子图
    plt.subplot(212)
    plt.plot(x, y5, 'b')
    # plt.xticks(rotation=30)
    plt.grid(True)
    plt.axis('tight')
    plt.xlabel('Date')
    plt.ylabel('MaxDrawDown')
    plt.ylim(min(max_dd),0)

    PNG_FILENAME = 'CIGRG_002_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.png'
    # plt.savefig(PNG_FILENAME)
    # plt.show()
    return (total_return, annualized_return, max_draw_down, df_price)


def main():
    items = 'max(date)'
    table = 'idx_price'
    condition = ' where symbol =\'000001.SH\' group by symbol'
    idx_data = get_all_data(items, table, condition)
    currentDate = idx_data[0][0].strftime('%Y-%m-%d')

    pf_test = []

    # 设定换仓阈值
    g = 0.145
    m = 0.045

    # for m in range(5, 100, 5):
    #     for g in range(m, 200, 5):
    start_date = '2018-04-20'
    end_date = currentDate
    # end_date = '2016-01-31'
    #         total_return, annualized_return, max_draw_down = calc_gm(g/1000, m/1000, start_date, end_date)
    #         pf_test.append([start_date, end_date, g/1000, m/1000, total_return, annualized_return, max_draw_down])
    total_return, annualized_return, max_draw_down, df = calc_gm(g, m, start_date, end_date)
    pf_test.append([start_date, end_date, total_return, annualized_return, max_draw_down])
    print(df.iloc[-1])
    return(df.iloc[-1])

if __name__ == "__main__":
    pf = main()


