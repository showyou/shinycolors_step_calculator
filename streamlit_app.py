import streamlit as st

st.write("""
# Shinycolors STEP Calculator
""")


# 入力UI
col1, col2 = st.columns(2)
with col1:
    current_vi = st.number_input('現在のVi', min_value=10, max_value=10000)
with col2:
    current_vi_limit = st.number_input('現在のVi上限', min_value=500, max_value=10000)

col3, col4 = st.columns(2)
with col3:
    vi_up = st.number_input('Vi UP', min_value=0, max_value=100000)
with col4:
    sp_up = st.number_input('SP UP', min_value=0, max_value=100000)

col5, col6 = st.columns(2)
with col5:
    current_vi_cnt = st.number_input('現在のVi回数', min_value=0, max_value=200)
with col6:
    current_vi_limit_cnt = st.number_input('現在のVi上限回数', min_value=0, max_value=200)


vi_params = [10, 5, 5, 10, 10, 10, 0, 0, 0, 0]
sp_params = [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0]


def _debug(stri):
    #st.write(stri)
    pass


# 戻り値, 集計値
def calc_param_sum(num, params, current):
    value = 0
    m_max = num//30
    for m in range(m_max):
        x = m * 30
        value += (num-x) * params[m] - max(0, current-x) * params[m]

    value += (num- (m_max*30) ) * params[m_max] - \
              max(0, current-(m_max*30)) * params[m_max]
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
        if max_limit_vi <= vi_up and max_limit_sp <= sp_up:
            break
        else:
            max_limit_cnt -= 1

    #st.write(f"max limit counts, vi,sp are: {max_limit_cnt}, {max_limit_vi}, {max_limit_sp}")    

    vi_cnt = max_limit_cnt
    vi_limit_cnt = max_limit_cnt
    sp_status = sp_up
    loop = 0
    while vi_cnt > current_vi_cnt and loop < 10000:
        loop += 1
        limit_vi, diff_limit_vi, limit_sp, diff_limit_sp, vi, diff_vi, sp, diff_sp = \
        calc_limit_and_now(
            vi_cnt, vi_limit_cnt, 
            vi_params, sp_params, current_vi_cnt, current_vi_limit_cnt)
        now_vi = current_vi + (vi_cnt - current_vi_cnt)* 10
        now_vi_limit = current_vi_limit + (vi_limit_cnt - current_vi_limit_cnt)*10
        _debug(f"now: {vi_cnt},{vi_limit_cnt}/ {vi}, {sp}, / {limit_vi}, {limit_sp} / {now_vi}, {now_vi_limit}")
        
        # もし条件満たしてたら
        vi_status = vi_up - (vi + limit_vi)
        sp_status = sp_up - (sp + limit_sp)
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
                        sum(sp_params[:rank]) < sp_status + sum(sp_params[:rank])*s and vi_limit_cnt>0:
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
            if -(vi_status) < diff_limit_vi and -(sp_status) < diff_limit_sp and \
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

download_data = f"""現在の属性値,現在の属性値上限,属性Upポイント,SP Upポイント,現在の属性回数,現在のSP回数,最適属性回数,最適上限回数,属性値,上限値,sp残り
{current_vi},{current_vi_limit},{vi_up},{sp_up},{current_vi_cnt},{current_vi_limit_cnt},{vi_cnt},{vi_limit_cnt},{vi},{vi_limit},{sp}
"""
st.download_button(
    label="Download results",
    data=download_data,
    file_name="step_results.csv",
    mime="text/csv"
        )

st.write("----")
st.write("""
このツールは非公式ツールです。

仕様変更によりパラメータが変わった際など、動作保証はできません。自己責任でお使いください。

質問などございましたら、https://imastodon.net/@showyou あたりまでどうぞ。
""")
st.write("-----")
st.write("""
現在の仕様

現在のパラメータ等が小さい時に、誤った結果を返すことがある
""")
