import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# 页面配置
st.set_page_config(
    page_title="学生数据分析系统",
    page_icon="👨‍🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
    border: 1px solid #e5e7eb;
}

.info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f3f4f6;
}

.info-label {
    color: #6b7280;
    font-weight: 500;
}

.info-value {
    font-weight: 600;
    color: #1f2937;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.status-help {
    background-color: #fee2e2;
    color: #dc2626;
}

.status-no-help {
    background-color: #dcfce7;
    color: #16a34a;
}

.status-scholarship {
    background-color: #fef3c7;
    color: #d97706;
}

.status-none {
    background-color: #f3f4f6;
    color: #6b7280;
}

.metric-card {
    text-align: center;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 8px;
    margin: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'students_data' not in st.session_state:
    st.session_state.students_data = None
if 'selected_student_index' not in st.session_state:
    st.session_state.selected_student_index = 0

# 主标题
st.markdown("""
<div class="main-header">
    <h1>👨‍🎓 学生数据分析系统</h1>
</div>
""", unsafe_allow_html=True)

# 文件上传区域
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📊 数据上传")
uploaded_file = st.file_uploader(
    "选择Excel文件上传学生数据",
    type=['xlsx', 'xls'],
    help="支持Excel格式文件，包含学生基本信息和成绩数据"
)

if uploaded_file is not None:
    try:
        # 读取Excel文件
        df = pd.read_excel(uploaded_file)
        st.session_state.students_data = df
        st.success(f"✅ 成功加载 {len(df)} 名学生的数据")
    except Exception as e:
        st.error(f"❌ 文件读取失败: {str(e)}")
        st.session_state.students_data = None

st.markdown('</div>', unsafe_allow_html=True)

# 如果没有数据，显示欢迎界面
if st.session_state.students_data is None:
    st.markdown("""
    <div class="card" style="text-align: center; padding: 3rem;">
        <h3>🎯 欢迎使用学生数据分析系统</h3>
        <p style="color: #6b7280; margin: 1rem 0;">请上传Excel文件开始分析学生数据</p>
    """, unsafe_allow_html=True)
else:
    df = st.session_state.students_data
    
    # 学生选择器
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 学生选择器")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # 搜索功能
        search_term = st.text_input("🔍 搜索学生", placeholder="输入姓名、学号或班级进行搜索...")
        
        # 过滤学生数据
        if search_term:
            mask = (
                df['姓名'].astype(str).str.contains(search_term, case=False, na=False) |
                df['学号'].astype(str).str.contains(search_term, case=False, na=False) |
                df['班级_基本信息'].astype(str).str.contains(search_term, case=False, na=False)
            )
            filtered_df = df[mask]
        else:
            filtered_df = df
    
    with col2:
        st.metric("总学生数", len(df))
    
    with col3:
        st.metric("筛选结果", len(filtered_df))
    
    if len(filtered_df) > 0:
        # 学生选择下拉框
        student_options = []
        for idx, row in filtered_df.iterrows():
            student_options.append(f"{row['姓名']} - {row['学号']} - {row['班级_基本信息']}")
        
        selected_student = st.selectbox(
            "选择学生",
            options=range(len(student_options)),
            format_func=lambda x: student_options[x],
            key="student_selector"
        )
        
        # 导航按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("⬅️ 上一个", disabled=selected_student == 0):
                selected_student = max(0, selected_student - 1)
        with col3:
            if st.button("下一个 ➡️", disabled=selected_student >= len(student_options) - 1):
                selected_student = min(len(student_options) - 1, selected_student + 1)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 获取选中的学生数据
        student_data = filtered_df.iloc[selected_student]
        
        # 个人信息卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 👤 个人信息")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-row">
                <span class="info-label">姓名：</span>
                <span class="info-value">{student_data.get('姓名', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">学号：</span>
                <span class="info-value">{student_data.get('学号', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">班级：</span>
                <span class="info-value">{student_data.get('班级_基本信息', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">专业：</span>
                <span class="info-value">{student_data.get('分流专业', student_data.get('原专业', 'N/A'))}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="info-row">
                <span class="info-label">辅导员：</span>
                <span class="info-value">{student_data.get('辅导员', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">政治面貌：</span>
                <span class="info-value">{student_data.get('政治面貌', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">民族：</span>
                <span class="info-value">{student_data.get('民族', 'N/A')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">性别：</span>
                <span class="info-value">{student_data.get('性别', 'N/A')}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 帮助需求卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🆘 帮助需求")
        
        help_needed = (
            student_data.get('有无需要学院协助解决的困难') and 
            student_data.get('有无需要学院协助解决的困难') != '无'
        )
        
        if help_needed:
            st.markdown(f"""
            <div style="background: #fee2e2; padding: 1rem; border-radius: 8px; border: 1px solid #fecaca;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <div style="width: 12px; height: 12px; background: #dc2626; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="font-weight: 600; color: #dc2626;">需要帮助</span>
                </div>
                <p style="color: #dc2626; margin: 0; font-size: 0.9rem;">
                    困难详情: {student_data.get('有何困难', '未详述')}
                </p>
                <p style="color: #6b7280; margin-top: 0.5rem; font-size: 0.8rem;">
                    心理状态: {student_data.get('最新心理等级', '未评估')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #dcfce7; padding: 1rem; border-radius: 8px; border: 1px solid #bbf7d0;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 12px; height: 12px; background: #16a34a; border-radius: 50%; margin-right: 0.5rem;"></div>
                    <span style="font-weight: 600; color: #16a34a;">无需帮助</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 咨询问题卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💜 咨询问题")
        
        consultation_items = [
            "第一学年困难等级",
            "第二学年困难等级", 
            "困难保障人群"
        ]
        
        for item in consultation_items:
            value = student_data.get(item, '无')
            status_class = "status-help" if value and value != '无' else "status-none"
            st.markdown(f"""
            <div style="background: #f8fafc; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #6b7280;">{item}：</span>
                    <span class="status-badge {status_class}">{value if value else '无'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 奖学金信息卡片
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🏆 奖学金信息")
        
        scholarship_items = [
            ("人民奖学金", student_data.get('人民奖学金')),
            ("助学金", student_data.get('助学金', student_data.get('助学金.1'))),
            ("获得奖项", student_data.get('奖项'))
        ]
        
        for label, value in scholarship_items:
            status_class = "status-scholarship" if value and value != '无' else "status-none"
            st.markdown(f"""
            <div style="background: #fffbeb; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #6b7280;">{label}：</span>
                    <span class="status-badge {status_class}">{value if value else '无'}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 综合素质雷达图
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 综合素质雷达图")
        
        # 准备雷达图数据
        def normalize_value(value, min_val, max_val):
            if pd.isna(value) or value is None:
                return 0
            return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))
        
        radar_data = [
            ("德育", normalize_value(student_data.get('德育'), 12, 15), student_data.get('德育', 0)),
            ("智育", normalize_value(student_data.get('智育'), 50, 100), student_data.get('智育', 0)),
            ("体测", normalize_value(student_data.get('体测成绩'), 60, 120), student_data.get('体测成绩', 0)),
            ("附加分", normalize_value(student_data.get('附加分', student_data.get('23-24附加分')), -1, 6), student_data.get('附加分', student_data.get('23-24附加分', 0))),
            ("总分", normalize_value(student_data.get('测评总分'), 50, 110), student_data.get('测评总分', 0))
        ]
        
        categories = [item[0] for item in radar_data]
        values = [item[1] for item in radar_data]
        actual_values = [item[2] for item in radar_data]
        
        # 创建雷达图
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='综合评分',
            line_color='#3b82f6',
            fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    gridcolor='#e5e7eb'
                ),
                angularaxis=dict(
                    gridcolor='#e5e7eb'
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示具体数值
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        
        for i, (name, _, actual) in enumerate(radar_data):
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">{name}</div>
                    <div style="color: #3b82f6; font-weight: bold; font-size: 1.2rem;">{actual}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 学期成绩趋势图
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 学期成绩趋势")
        
        # 准备绩点数据
        gpa_data = []
        for semester in ['第一学期绩点', '第二学期绩点', '第三学期绩点']:
            value = student_data.get(semester)
            if pd.notna(value) and value is not None:
                gpa_data.append({
                    'semester': semester.replace('绩点', ''),
                    'gpa': float(value)
                })
        
        if gpa_data:
            semesters = [item['semester'] for item in gpa_data]
            gpas = [item['gpa'] for item in gpa_data]
            
            # 创建折线图
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=semesters,
                y=gpas,
                mode='lines+markers',
                name='绩点',
                line=dict(color='#8b5cf6', width=3),
                marker=dict(size=8, color='#8b5cf6')
            ))
            
            fig.update_layout(
                xaxis_title="学期",
                yaxis_title="绩点",
                yaxis=dict(range=[0, 4]),
                height=300,
                margin=dict(t=30, b=30, l=30, r=30),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示平均绩点
            avg_gpa = sum(gpas) / len(gpas)
            st.markdown(f"""
            <div style="text-align: center; color: #6b7280; margin-top: 1rem;">
                平均绩点: <span style="font-weight: bold; color: #8b5cf6;">{avg_gpa:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📊 暂无绩点数据")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.warning("🔍 未找到匹配的学生，请调整搜索条件")