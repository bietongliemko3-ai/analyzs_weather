import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# CẤU HÌNH GIAO DIỆN & FONT TIẾNG VIỆT
st.set_page_config(page_title="Hệ thống BI - Khí tượng & Phân tích Du lịch", layout="wide")

plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    div[data-testid="stMetricValue"] { font-size: 26px !important; font-weight: bold; color: #1E3A8A; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 600; color: #4B5563; }
    .stTabs [data-baseweb="tab"] { font-size: 15px; font-weight: bold; padding: 10px 15px; }
    </style>
""", unsafe_allow_html=True)

# TẢI DỮ LIỆU SẠCH HOÀN TOÀN ĐÃ QUA XỬ LÝ TỪ NOTEBOOK
@st.cache_data
def load_data():
    df = pd.read_csv("weather_cleaned.csv") 
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# BỘ LỌC ĐỐI TƯỢNG (SIDEBAR)
st.sidebar.header("BỘ LỌC ĐIỀU HÀNH")
all_provinces = sorted(df['province'].unique())

selected_year = st.sidebar.slider(
    "Chọn Năm Khảo Sát Từng Phần:", int(df['Year'].min()), int(df['Year'].max()), int(df['Year'].max())
)

st.sidebar.markdown("---")
st.sidebar.subheader("Phần 1: Khí hậu chung và mùa vụ")
provinces_trend = st.sidebar.multiselect("1. Chọn tỉnh xem Xu hướng năm:", options=all_provinces, default=['Ha Noi', 'Ho Chi Minh City'])
provinces_monthly = st.sidebar.multiselect("2. Chọn tỉnh xem Chu kỳ tháng (Tối đa 3):", options=all_provinces, default=['Ha Noi', 'Hue', 'Ho Chi Minh City'], max_selections=3)
provinces_boxplot = st.sidebar.multiselect("3. Chọn tỉnh xem Biên độ nhiệt ngày đêm:", options=all_provinces, default=list(all_provinces[:5]))

st.sidebar.markdown("---")
st.sidebar.subheader("Phần 2: Nguyên nhân mùa mưa và mùa khô")
selected_cause_province = st.sidebar.selectbox("Chọn 1 tỉnh để phân tích nhân quả:", options=all_provinces, index=all_provinces.index('Ho Chi Minh City') if 'Ho Chi Minh City' in all_provinces else 0)

st.sidebar.markdown("---")
st.sidebar.subheader("Phần 3: Phân tích Du lịch")
single_tour_province = st.sidebar.selectbox("Chọn 1 ĐỊA PHƯƠNG để lập lịch du lịch chi tiết:", options=all_provinces, index=all_provinces.index('Ho Chi Minh City') if 'Ho Chi Minh City' in all_provinces else 0)

st.title("HỆ THỐNG BI PHÂN TÍCH KHÍ HẬU VÀ HOẠCH ĐỊNH DU LỊCH VIỆT NAM")
st.markdown("---")
tab_climate, tab_seasonal_cause, tab_tourism = st.tabs(["1. Thống Kê Khí Hậu Chung", "2. Nguyên Nhân Mùa Mưa/Khô", "3. Hoạch Định Du Lịch Chuyên Sâu"])

# 1. THỐNG KÊ KHÍ HẬU CHUNG
with tab_climate:
    st.subheader("Báo Cáo Khí Hậu Phân Phối và Xu Hướng")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Xu hướng nhiệt độ cực đại qua các năm")
        if provinces_trend:
            df_yearly = df[df['province'].isin(provinces_trend)].groupby(['Year', 'province'])['max'].mean().reset_index()
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            sns.lineplot(data=df_yearly, x='Year', y='max', hue='province', marker='o', linewidth=2.5, ax=ax1)
            for province in df_yearly['province'].unique():
                df_p = df_yearly[df_yearly['province'] == province]
                for x, y in zip(df_p['Year'], df_p['max']):
                    ax1.text(x, y + 0.1, f"{y:.1f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
            ax1.set_title("Nhiệt Độ Cao Nhất Trung Bình Qua Các Năm", fontsize=11, fontweight='bold')
            ax1.set_xlabel("Năm")
            ax1.set_ylabel("Nhiệt độ (°C)")
            # THÊM LƯỚI
            ax1.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig1)
        else:
            st.info("Vui lòng chọn ít nhất 1 tỉnh ở mục số 1 bên Sidebar.")

        st.write("#### Chu kỳ phân bổ lượng mưa theo tháng")
        if provinces_monthly:
            df_raw_filtered = df[df['province'].isin(provinces_monthly)]
            months_grid = range(1, 13)
            all_combos = pd.MultiIndex.from_product([months_grid, provinces_monthly], names=['Month', 'province']).to_frame().reset_index(drop=True)
            df_calc = df_raw_filtered.groupby(['Month', 'province'])['rain'].mean().reset_index()
            df_monthly = pd.merge(all_combos, df_calc, on=['Month', 'province'], how='left').fillna(0)
            df_monthly['Month_Str'] = "Tháng " + df_monthly['Month'].astype(str)
            full_months_list = ["Tháng " + str(i) for i in range(1, 13)]
            df_monthly['Month_Str'] = pd.Categorical(df_monthly['Month_Str'], categories=full_months_list, ordered=True)
            df_monthly = df_monthly.sort_values('Month_Str')
            
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            bars2 = sns.barplot(data=df_monthly, x='Month_Str', y='rain', hue='province', palette='Set2', ax=ax2)
            for container in ax2.containers:
                ax2.bar_label(container, fmt='%.1f', padding=3, fontsize=8)
            ax2.set_title("Lượng Mưa Trung Bình Từng Tháng (Toàn giai đoạn)", fontsize=11, fontweight='bold')
            ax2.set_xticklabels(full_months_list, rotation=15, ha='right')
            # THÊM LƯỚI (Chỉ lưới ngang cho biểu đồ cột để nhìn gọn)
            ax2.grid(axis='y', linestyle='--', alpha=0.6)
            st.pyplot(fig2)
        else:
            st.info("Vui lòng chọn từ 1 - 3 tỉnh ở mục số 2 bên Sidebar.")

    with col2:
        st.write("#### Biến động biên độ nhiệt ngày đêm theo địa phương")
        if provinces_boxplot:
            df_box = df[(df['province'].isin(provinces_boxplot)) & (df['Year'] == selected_year)]
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            sns.boxplot(data=df_box, x='province', y='Temp_Range', palette='Set2', width=0.4, ax=ax3)
            lines = ax3.get_lines()
            categories = ax3.get_xticks()
            for cat in categories:
                if len(lines) >= (cat * 6 + 5):
                    y_median = lines[cat * 6 + 4].get_ydata()[0]
                    if not np.isnan(y_median):
                        ax3.text(cat, y_median + 0.1, f"{y_median:.1f}", ha='center', va='bottom', color='black', fontsize=9, fontweight='bold')
            # THÊM LƯỚI
            ax3.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig3)
        else:
            st.info("Vui lòng chọn các tỉnh ở mục số 3 bên Sidebar.")

        st.write(f"#### Xếp hạng địa phương có nhiệt độ trung bình năm cao nhất cả nước ({selected_year})")
        df_all_temp = df[df['Year'] == selected_year].groupby('province')['avg_temp'].mean().sort_values(ascending=False).reset_index()
        
        fig4, ax4 = plt.subplots(figsize=(11, 5))
        sns.barplot(data=df_all_temp.head(15), x='province', y='avg_temp', palette='Reds_r', ax=ax4)
        for container in ax4.containers:
            ax4.bar_label(container, fmt='%.1f', padding=3, fontsize=8, fontweight='bold')
        plt.xticks(rotation=45, ha='right', fontsize=9)
        ax4.set_ylim(int(df_all_temp['avg_temp'].min() - 2), int(df_all_temp['avg_temp'].max() + 2))
        # THÊM LƯỚI (Chỉ lưới ngang cho biểu đồ cột)
        ax4.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig4)

# 2. NGUYÊN NHÂN MÙA MƯA VÀ MÙA KHÔ
with tab_seasonal_cause:
    st.subheader(f"Nghiên Cứu Quy Luật Mùa Vụ Khí Hậu Việt Nam Quy Mô Toàn Quốc (Năm {selected_year})")
    st.write("#### 1. Ma trận liên kết chỉ số khí tượng vĩ mô (Toàn quốc)")
    df_all_vietnam = df[df['Year'] == selected_year][['max', 'min', 'rain', 'humidi', 'cloud', 'pressure', 'wind', 'Temp_Range']].copy()
    df_all_vietnam = df_all_vietnam.rename(columns={
        'max': 'Nhiệt độ Max', 'min': 'Nhiệt độ Min', 'rain': 'Lượng mưa',
        'humidi': 'Độ ẩm', 'cloud': 'Lượng mây', 'pressure': 'Áp suất',
        'wind': 'Tốc độ gió', 'Temp_Range': 'Biên độ nhiệt'
    })
    fig5, ax5 = plt.subplots(figsize=(12, 6))
    sns.heatmap(df_all_vietnam.corr(), annot=True, cmap='coolwarm', fmt=".2f", center=0, linewidths=.5, ax=ax5)
    st.pyplot(fig5)
    
    st.markdown("---")
    st.write(f"#### 2. Mô hình phân tích nhân quả biến trình khí hậu toàn năm tại địa phương: **{selected_cause_province}**")
    
    full_months_bridge = pd.DataFrame({'Month': range(1, 13)})
    df_cause_raw = df[(df['province'] == selected_cause_province) & (df['Year'] == 2024)].groupby('Month')[['rain', 'cloud', 'wind', 'pressure', 'Temp_Range']].mean().reset_index()
    df_seasonal_matrix = pd.merge(full_months_bridge, df_cause_raw, on='Month', how='left').fillna(0)
    
    fig_matrix, (ax_rain, ax_wind_cloud, ax_press_range) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    ax_rain.bar(df_seasonal_matrix['Month'], df_seasonal_matrix['rain'], width=0.4, color='#3B82F6')
    ax_rain.set_ylabel("Lượng mưa (mm)", color='#1D4ED8', fontweight='bold')
    ax_rain.bar_label(ax_rain.containers[0], fmt='%.1f', padding=2, fontsize=8)
    ax_rain.set_title("TẦNG 1: BIÊN TRÌNH LƯỢNG MƯA THỰC TẾ", fontsize=10, fontweight='bold', loc='left', color='#1D4ED8')
    ax_rain.grid(axis='y', linestyle='--', alpha=0.5)
    
    ax_wind_cloud.plot(df_seasonal_matrix['Month'], df_seasonal_matrix['cloud'], color='#10B981', marker='o', linewidth=2)
    ax_wind_cloud.set_ylabel("Lượng mây (%)", color='#047857', fontweight='bold')
    for x, y in zip(df_seasonal_matrix['Month'], df_seasonal_matrix['cloud']):
        if y > 0: ax_wind_cloud.text(x, y + 2, f"{y:.0f}%", color='#047857', fontsize=8, ha='center')
        
    ax_wind_twin = ax_wind_cloud.twinx()
    ax_wind_twin.plot(df_seasonal_matrix['Month'], df_seasonal_matrix['wind'], color='#EF4444', marker='x', linestyle='--', linewidth=2)
    ax_wind_twin.set_ylabel("Tốc độ gió (m/s)", color='#B91C1C', fontweight='bold')
    for x, y in zip(df_seasonal_matrix['Month'], df_seasonal_matrix['wind']):
        if y > 0: ax_wind_twin.text(x, y - 0.2, f"{y:.1f}", color='#B91C1C', fontsize=8, ha='center', va='top')
    ax_wind_cloud.set_title("TẦNG 2: CÁC ĐỘNG LỰC THÚC ĐẨY MÙA MƯA (MÂY & GIÓ)", fontsize=10, fontweight='bold', loc='left', color='#047857')
    
    lines_2, labels_2 = ax_wind_cloud.get_legend_handles_labels()
    lines_2_twin, labels_2_twin = ax_wind_twin.get_legend_handles_labels()
    ax_wind_twin.legend(lines_2 + lines_2_twin, labels_2 + labels_2_twin, loc='upper left', fontsize=8)
    # THÊM LƯỚI (Lưới ngang cho tầng 2)
    ax_wind_cloud.grid(axis='y', linestyle='--', alpha=0.5)
    
    ax_press_range.plot(df_seasonal_matrix['Month'], df_seasonal_matrix['pressure'], color='#F97316', marker='s', linewidth=2)
    ax_press_range.set_ylabel("Áp suất (hPa)", color='#C2410C', fontweight='bold')
    p_min, p_max = df_seasonal_matrix['pressure'].min(), df_seasonal_matrix['pressure'].max()
    if p_min > 0: ax_press_range.set_ylim(p_min - 2, p_max + 2)
    for x, y in zip(df_seasonal_matrix['Month'], df_seasonal_matrix['pressure']):
        if y > 0: ax_press_range.text(x, y + 0.3, f"{y:.0f}", color='#C2410C', fontsize=8, ha='center')
        
    ax_range_twin = ax_press_range.twinx()
    ax_range_twin.plot(df_seasonal_matrix['Month'], df_seasonal_matrix['Temp_Range'], color='#8B5CF6', marker='d', linestyle='-.', linewidth=2)
    ax_range_twin.set_ylabel("Biên độ nhiệt (°C)", color='#6D28D9', fontweight='bold')
    for x, y in zip(df_seasonal_matrix['Month'], df_seasonal_matrix['Temp_Range']):
        if y > 0: ax_range_twin.text(x, y - 0.2, f"{y:.1f}°C", color='#6D28D9', fontsize=8, ha='center', va='top')
    ax_press_range.set_title("TẦNG 3: NGHỊCH LÝ KHÍ HẬU MÙA KHÔ (ÁP SUẤT & BIÊN ĐỘ NHIỆT)", fontsize=10, fontweight='bold', loc='left', color='#C2410C')
    
    lines_3, labels_3 = ax_press_range.get_legend_handles_labels()
    lines_3_twin, labels_3_twin = ax_range_twin.get_legend_handles_labels()
    ax_range_twin.legend(lines_3 + lines_3_twin, labels_3 + lines_3_twin, loc='upper right', fontsize=8)
    # THÊM LƯỚI (Lưới ngang cho tầng 3)
    ax_press_range.grid(axis='y', linestyle='--', alpha=0.5)

    ax_press_range.set_xticks(range(1, 13))
    ax_press_range.set_xticklabels([f"Tháng {int(m)}" for m in range(1, 13)], rotation=0, fontweight='bold')
    ax_press_range.set_xlabel(f"Tiến trình chu kỳ thời gian 12 tháng tại địa phương chọn riêng: {selected_cause_province} (Dữ liệu chuẩn hóa 2024)", fontsize=11, fontweight='bold', labelpad=10)
    st.pyplot(fig_matrix)

# 3. HOẠCH ĐỊNH DU LỊCH CHUYÊN SÂU 
with tab_tourism:
    st.subheader(f"Hệ Thống Lập Lịch Tour và Dự Báo An Toàn Du Lịch tại Địa Phương: **{single_tour_province}**")
    col_tour_l, col_tour_r = st.columns(2)
    
    with col_tour_l:
        st.write("#### Lịch phân bổ Ngày Vàng khí hậu du lịch lý tưởng TB (2014 - 2024)")
        
        df_tour_period = df[(df['province'] == single_tour_province) & (df['Year'] >= 2014) & (df['Year'] <= 2024)]
        df_monthly_sum = df_tour_period.groupby(['Year', 'Month'])['is_comfort_day'].sum().reset_index()
        df_calendar_avg = df_monthly_sum.groupby('Month')['is_comfort_day'].mean().reset_index()
        df_calendar_avg = df_calendar_avg.set_index('Month').reindex(range(1, 13), fill_value=0).reset_index()
        
        baseline_comfort = df_calendar_avg['is_comfort_day'].mean()
        
        fig8, ax8 = plt.subplots(figsize=(10, 5))
        bars8 = sns.barplot(data=df_calendar_avg, x='Month', y='is_comfort_day', palette='YlOrRd', ax=ax8)
        
        for container in ax8.containers:
            ax8.bar_label(container, fmt='%.1f', padding=3, fontsize=9, fontweight='bold', color='brown')
        
        ax8.axhline(baseline_comfort, color='green', linestyle='--', alpha=0.7, 
                    label=f'Mức trung bình năm ({baseline_comfort:.1f} ngày)')
        ax8.set_xlabel("Tháng trong năm")
        ax8.set_ylabel("Số ngày đẹp đạt chuẩn trung bình (ngày)")
        ax8.legend()
        # THÊM LƯỚI (Chỉ lưới ngang)
        ax8.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig8)

        st.write(f"#### Số ngày cảnh báo rủi ro thời tiết cực đoan (Hủy tour) TB (2014 - 2024)")
        df_risk_monthly_sum = df_tour_period.groupby(['Year', 'Month'])['is_risk_day'].sum().reset_index()
        df_risk_calendar_avg = df_risk_monthly_sum.groupby('Month')['is_risk_day'].mean().reset_index()
        df_risk_calendar_avg = df_risk_calendar_avg.set_index('Month').reindex(range(1, 13), fill_value=0).reset_index()
        
        fig9, ax9 = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_risk_calendar_avg, x='Month', y='is_risk_day', marker='X', color='#B91C1C', linewidth=2.5, ax=ax9)
        
        for x, y in zip(df_risk_calendar_avg['Month'], df_risk_calendar_avg['is_risk_day']):
            ax9.text(x, y + 0.3, f"{y:.1f}d", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#B91C1C')
            
        ax9.set_xticks(range(1, 13))
        ax9.set_xticklabels([f"Tháng {int(m)}" for m in range(1, 13)], rotation=0)
        ax9.set_ylim(0, df_risk_calendar_avg['is_risk_day'].max() + 2)
        ax9.set_xlabel("Tháng trong năm")
        ax9.set_ylabel("Số ngày rủi ro thiên tai trung bình (ngày)")
        # THÊM LƯỚI
        ax9.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig9)
        
    with col_tour_r:
        st.write(f"#### Biến động tổng số Ngày Vàng Du lịch giai đoạn lịch sử (2014 - 2024)")
        df_history = df[(df['province'] == single_tour_province) & (df['Year'] >= 2014) & (df['Year'] <= 2024)]
        df_yearly_comfort = df_history.groupby('Year')['is_comfort_day'].sum().reset_index()
        df_yearly_comfort = pd.merge(pd.DataFrame({'Year': range(2014, 2025)}), df_yearly_comfort, on='Year', how='left').fillna(0)
        
        fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=df_yearly_comfort, x='Year', y='is_comfort_day', marker='o', color='#F59E0B', linewidth=2.5, ax=ax_hist)
        for x, y in zip(df_yearly_comfort['Year'], df_yearly_comfort['is_comfort_day']):
            ax_hist.text(x, y + 5, f"{int(y)} ngày", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#D97706')
        ax_hist.set_xticks(range(2014, 2025))
        ax_hist.set_ylim(0, df_yearly_comfort['is_comfort_day'].max() + 35)
        # THÊM LƯỚI
        ax_hist.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig_hist)

        st.markdown("---")
        st.write(f"#### Bản đồ xếp hạng tài nguyên Ngày Vàng khí hậu du lịch toàn quốc ({selected_year})")
        df_all_comfort = df[df['Year'] == selected_year].groupby('province')['is_comfort_day'].sum().sort_values(ascending=False).reset_index()
        fig10, ax10 = plt.subplots(figsize=(10, 6))
        bars10 = sns.barplot(data=df_all_comfort, y='province', x='is_comfort_day', palette='Spectral', ax=ax10)
        for container in ax10.containers:
            ax10.bar_label(container, fmt='%d ngày', padding=5, fontsize=8, fontweight='bold')
        # THÊM LƯỚI (Biểu đồ này trục x là số ngày nên thêm lưới dọc sẽ hợp lý hơn)
        ax10.grid(axis='x', linestyle='--', alpha=0.6)
        st.pyplot(fig10)
