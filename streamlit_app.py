import streamlit as st

st.write("""
# Shinycolors STEP Calculator
""")


# 入力UI
current_vi_str = st.text_input('現在のVi', 0)
current_vi_limit_str = st.text_input('現在のVi上限', 500)

vi_up = st.text_input('Vi UP', 0) #D1
sp_up = st.text_input('SP UP', 0) #F2

current_vi_cnt_str = st.text_input('現在のVi回数', 0) #B2
current_vi_limit_cnt_str = st.text_input('現在のVi上限回数', 0) #D2

# 各種パラメータをintに変換
current_vi = int(current_vi_str)
current_vi_limit = int(current_vi_limit_str)
current_vi_cnt = int(current_vi_cnt_str)
current_vi_limit_cnt = int(current_vi_limit_cnt_str)

vi_params = [10, 5, 5, 10, 10, 10, 0, 0]
sp_params = [0, 0, 1, 1, 1, 1, 0, 0, 0]


def _debug(stri):
    #st.write(stri)
    pass


# 戻り値, 集計値
def calc_param_sum(num, params, current):
    value = 0
    m_max =num//30
    for m in range(m_max):
        x = m * 30
        value += (num-x) * params[m] - max(0, current-x)*params[m]
    value += (num- (m_max*30) ) * params[m_max] - \
              max(0, current-(m_max*30))*params[m_max]
    diff = sum(params[:(num-1)//30])
    return value, diff


# 戻り値 消費vi上限, 消費vi上限sp, 消費vi, 消費sp
def calc_limit_and_now(
    vi_cnt, vi_limit_cnt,
    vi_params, sp_params, current_vi_cnt, current_vi_limit_cnt
):
    limit_vi, diff_limit_vi = calc_param_sum(vi_limit_cnt, vi_params, current_vi_limit_cnt)
    limit_sp, diff_limit_sp = calc_param_sum(vi_limit_cnt, sp_params, current_vi_limit_cnt)
    vi, diff_vi = calc_param_sum(vi_cnt, vi_params, current_vi_cnt)
    sp, diff_sp = calc_param_sum(vi_cnt, sp_params, current_vi_cnt)
    return limit_vi, diff_limit_vi, limit_sp, diff_limit_sp, vi, diff_vi, sp, diff_sp


def main():
    #200から1ずつ減らして、limitに極振りした際の回数を数える
    max_limit_cnt = 200
    while max_limit_cnt > current_vi_limit_cnt:
        max_limit_vi, _ = calc_param_sum(max_limit_cnt, vi_params, current_vi_limit_cnt)
        max_limit_sp, _ = calc_param_sum(max_limit_cnt, sp_params, current_vi_limit_cnt)
        
        # 最大vi値が手持ちのvi値より小さければOK、そうでないなら1減らして再計算
        if max_limit_vi <= int(vi_up) and max_limit_sp <= int(sp_up):
            break
        else:
            max_limit_cnt -= 1

    #st.write(f"max limit counts, vi,sp are: {max_limit_cnt}, {max_limit_vi}, {max_limit_sp}")
    
    vi_cnt = max_limit_cnt
    vi_limit_cnt = max_limit_cnt
    sp_status = -1
    loop = 0
    while vi_cnt > current_vi_cnt and loop < 10000:
        loop += 1
        limit_vi, diff_limit_vi, limit_sp, diff_limit_sp, vi, diff_vi, sp, diff_sp = calc_limit_and_now(
            vi_cnt, vi_limit_cnt, 
            vi_params, sp_params, current_vi_cnt, current_vi_limit_cnt)
        now_vi = current_vi + (vi_cnt - current_vi_cnt)* 10
        now_vi_limit = current_vi_limit + (vi_limit_cnt - current_vi_limit_cnt)*10
        _debug(f"now: {vi_cnt},{vi_limit_cnt}/ {vi}, {sp}, / {limit_vi}, {limit_sp} / {now_vi}, {now_vi_limit}")
        
        # もし条件満たしてたら
        vi_status = int(vi_up) - (vi + limit_vi)
        sp_status = int(sp_up) - (sp + limit_sp)
        _debug(f"diffs {now_vi - now_vi_limit}// {vi_status}, {sp_status} ///  {vi_up}, {vi+limit_vi}" )

        if now_vi <= now_vi_limit and  vi_status >= 0 and sp_status >= 0:
            # viを上げられそうなら上げる
            if now_vi_limit - now_vi >= 10:
                rank = (vi_cnt)//30 # 30毎に区切った位置
                if(sum(vi_params[:rank]) < vi_status and \
                sum(sp_params[:rank]) < sp_status):
                    vi_cnt += 1
                    _debug(">> vi inc")
                else:
                    # 一定limit減らしても増やせる場合
                    s = (now_vi_limit - now_vi)//10
                    if sum(vi_params[:rank]) < vi_status + sum(vi_params[:rank])*s and \
                        sum(sp_params[:rank]) < sp_status + sum(sp_params[:rank])*s:
                        vi_limit_cnt -= 1
                        _debug(">>> limit dec2")
                    else:
                        break
            else:
                break
        else:
            # そうでないときは次のルールで下げる
            # limitだけ下げればいいなら、limitだけ下げる
            # そうでないなら、両方下げる
            if -(vi_status) < diff_limit_vi and \
             -(sp_status) < diff_limit_sp and \
             now_vi_limit - now_vi > 10:
                vi_limit_cnt -= 1
                _debug(">> limit dec")
            else:
                vi_cnt -= 1
                vi_limit_cnt -= 1
                _debug(">> both dec")

    return vi_cnt, vi_limit_cnt, sp_status


vi_cnt, vi_limit_cnt, sp = main()
vi = current_vi + (vi_cnt - current_vi_cnt)* 10
vi_limit = current_vi_limit + (vi_limit_cnt - current_vi_limit_cnt)*10

st.write(f"最適値は vi回数:{vi_cnt}, vi上限回数:{vi_limit_cnt} : vi:{vi}, vi上限:{vi_limit}")
st.write(f"SPの残りは {sp} です")

st.write("----")
st.write("""
このツールは非公式ツールです。

仕様変更によりパラメータが変わった際など、動作保証はできません。自己責任でお使いください。

質問などございましたら、mstdn.jp/showyou あたりまでどうぞ。
""")