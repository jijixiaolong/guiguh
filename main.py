import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import BytesIO

# 设置页面配置
st.set_page_config(
    page_title="学生数据分析系统",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .help-needed {
        background-color: #fee2e2;
        color: #dc2626;
        border-left: 5px solid #dc2626;
    }
    .help-not-needed {
        background-color: #dcfce7;
        color: #16a34a;
        border-left: 5px solid #16a34a;
    }
    .award-card {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4a 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_data(uploaded_file):
    """加载上传的Excel文件"""
    try:
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"文件读取错误: {str(e)}")
        return None

def normalize_value(value, min_val, max_val):
    """标准化数值到0-100范围"""
    if pd.isna(value):
        return 0
    return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))

def create_radar_chart(student_data, df=None):
    """创建雷达图"""
    # 数据预处理
    categories = ['德育', '智育', '体测', '附加分', '总分']
    
    # 获取实际值
    actual_values = [
        student_data.get('德育', 0),
        student_data.get('智育', 0),
        student_data.get('体测成绩', 0),
        student_data.get('附加分', student_data.get('23-24附加分', 0)),
        student_data.get('测评总分', 0)
    ]
    
    # 标准化值
    normalized_values = [
        normalize_value(actual_values[0], 12, 15),
        normalize_value(actual_values[1], 50, 100),
        normalize_value(actual_values[2], 60, 120),
        normalize_value(actual_values[3], -1, 6),
        normalize_value(actual_values[4], 50, 110)
    ]
    
    fig = go.Figure()
    
    # 添加班级平均数据（如果提供了df参数）
    if df is not None:
        # 计算班级平均值 - 先将列转换为数值类型
        class_avg = [
            pd.to_numeric(df['德育'], errors='coerce').mean() if '德育' in df else 0,
            pd.to_numeric(df['智育'], errors='coerce').mean() if '智育' in df else 0,
            pd.to_numeric(df['体测成绩'], errors='coerce').mean() if '体测成绩' in df else 0,
            pd.to_numeric(df['附加分'], errors='coerce').mean() if '附加分' in df else 
                (pd.to_numeric(df['23-24附加分'], errors='coerce').mean() if '23-24附加分' in df else 0),
            pd.to_numeric(df['测评总分'], errors='coerce').mean() if '测评总分' in df else 0
        ]
        
        # 标准化班级平均值
        normalized_class_avg = [
            normalize_value(class_avg[0], 12, 15),
            normalize_value(class_avg[1], 50, 100),
            normalize_value(class_avg[2], 60, 120),
            normalize_value(class_avg[3], -1, 6),
            normalize_value(class_avg[4], 50, 110)
        ]
        
        # 添加班级平均值曲线
        fig.add_trace(go.Scatterpolar(
            r=normalized_class_avg + [normalized_class_avg[0]],  # 闭合图形
            theta=categories + [categories[0]],
            fill='toself',
            name='班级平均',
            line_color='rgba(255, 99, 132, 0.8)',
            fillcolor='rgba(255, 99, 132, 0.2)',
            customdata=class_avg + [class_avg[0]],
            hovertemplate='<b>%{theta}</b><br>班级平均: %{customdata:.2f}<br>标准化值: %{r:.1f}%<extra></extra>'
        ))
    
    # 添加学生个人数据
    fig.add_trace(go.Scatterpolar(
        r=normalized_values + [normalized_values[0]],  # 闭合图形
        theta=categories + [categories[0]],
        fill='toself',
        name='个人得分',
        line_color='rgb(67, 130, 246)',
        fillcolor='rgba(67, 130, 246, 0.3)',
        customdata=actual_values + [actual_values[0]],
        hovertemplate='<b>%{theta}</b><br>实际值: %{customdata}<br>标准化值: %{r:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20
            )),
        showlegend=True,
        title="综合素质雷达图",
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_gpa_chart(student_data, df=None):
    """创建绩点趋势图"""
    semesters = []
    gpas = []
    
    # 显示调试信息
    st.write("调试信息：尝试获取绩点数据")
    
    # 收集绩点数据
    for sem_num in ['第一学期', '第二学期', '第三学期']:
        gpa_key = f'{sem_num}绩点'
        if gpa_key in student_data and pd.notna(student_data[gpa_key]):
            st.write(f"找到{sem_num}绩点数据: {student_data[gpa_key]}")
            semesters.append(sem_num)
            try:
                gpa_value = float(student_data[gpa_key]) if not isinstance(student_data[gpa_key], (int, float)) else student_data[gpa_key]
                gpas.append(gpa_value)
            except (ValueError, TypeError) as e:
                st.write(f"绩点数据转换错误: {sem_num}={student_data[gpa_key]}, 错误: {str(e)}")
    
    # 如果没有数据，使用默认数据以展示功能
    if not semesters or len(semesters) < 2:
        st.warning("没有足够的绩点数据，使用示例数据展示功能")
        semesters = ['第一学期', '第二学期', '第三学期']
        gpas = [3.2, 3.5, 3.1]  # 示例数据
    
    fig = go.Figure()
    
    # 添加个人绩点线
    fig.add_trace(go.Scatter(
        x=semesters,
        y=gpas,
        mode='lines+markers',
        name='个人绩点',
        line=dict(color='rgb(139, 92, 246)', width=3),
        marker=dict(size=10, color='rgb(139, 92, 246)')
    ))
    
    # 如果有班级数据，添加班级平均绩点
    if df is not None:
        try:
            class_avg_gpas = []
            for sem_num in semesters:
                gpa_key = f'{sem_num}绩点'
                if gpa_key in df.columns:
                    avg = pd.to_numeric(df[gpa_key], errors='coerce').mean()
                    class_avg_gpas.append(avg)
                    st.write(f"班级平均{sem_num}绩点: {avg}")
                else:
                    # 如果没有这个学期的数据，使用默认值
                    class_avg_gpas.append(3.0)  # 使用默认值
                    st.write(f"未找到班级{sem_num}绩点数据，使用默认值")
            
            # 添加班级平均线
            fig.add_trace(go.Scatter(
                x=semesters,
                y=class_avg_gpas,
                mode='lines+markers',
                name='班级平均',
                line=dict(color='rgba(255, 99, 132, 0.8)', width=2, dash='dot'),
                marker=dict(size=8, color='rgba(255, 99, 132, 0.8)')
            ))
        except Exception as e:
            st.write(f"添加班级平均绩点时出错: {str(e)}")
    
    # 添加趋势预测线（如果有至少两个学期的数据）
    if len(gpas) >= 2:
        try:
            # 使用简单线性回归进行趋势预测
            x_numeric = np.arange(len(gpas))
            coeffs = np.polyfit(x_numeric, gpas, 1)
            trend_line = np.polyval(coeffs, x_numeric)
            
            # 预测下一学期
            next_semester = f'第{len(gpas)+1}学期(预测)'
            next_gpa = np.polyval(coeffs, len(gpas))
            
            # 确保预测值在合理范围内 (0-4)
            next_gpa = max(0, min(4, next_gpa))
            
            # 添加趋势线和预测点
            all_semesters = semesters + [next_semester]
            all_trend = list(trend_line) + [next_gpa]
            
            fig.add_trace(go.Scatter(
                x=all_semesters,
                y=all_trend,
                mode='lines',
                name='趋势预测',
                line=dict(color='rgba(75, 192, 192, 0.6)', width=2, dash='dash'),
            ))
            
            # 添加预测点
            fig.add_trace(go.Scatter(
                x=[next_semester],
                y=[next_gpa],
                mode='markers',
                marker=dict(size=12, color='rgba(75, 192, 192, 0.8)', symbol='star'),
                name='预测绩点',
                hovertemplate='%{x}<br>预测绩点: %{y:.2f}<extra></extra>'
            ))
        except Exception as e:
            st.write(f"添加趋势预测时出错: {str(e)}")
    
    fig.update_layout(
        title="学期绩点趋势",
        xaxis_title="学期",
        yaxis_title="绩点",
        yaxis=dict(range=[0, 4]),
        height=400,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # 添加参考线
    fig.add_shape(
        type="line",
        x0=semesters[0],
        y0=3.0,
        x1=semesters[-1] if len(semesters) > 1 else semesters[0],
        y1=3.0,
        line=dict(color="green", width=1, dash="dot"),
    )
    fig.add_annotation(
        x=semesters[0],
        y=3.0,
        text="良好",
        showarrow=False,
        yshift=10,
        font=dict(size=10, color="green")
    )
    
    return fig

def display_student_info(student_data):
    """显示学生基本信息"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 基本信息")
        info_data = {
            "姓名": student_data.get('姓名', '未知'),
            "学号": student_data.get('学号', '未知'),
            "班级": student_data.get('班级_基本信息', '未知'),
            "性别": student_data.get('性别', '未知')
        }
        for key, value in info_data.items():
            st.write(f"**{key}:** {value}")
    
    with col2:
        st.markdown("### 🎓 学籍信息")
        academic_data = {
            "专业": student_data.get('分流专业', student_data.get('原专业', '未知')),
            "辅导员": student_data.get('辅导员', '未知'),
            "政治面貌": student_data.get('政治面貌', '未知'),
            "民族": student_data.get('民族', '未知')
        }
        for key, value in academic_data.items():
            st.write(f"**{key}:** {value}")

def display_help_status(student_data):
    """显示帮助需求状态"""
    help_needed = (student_data.get('有无需要学院协助解决的困难') not in [None, '无', np.nan])
    
    if help_needed:
        st.markdown("""
        <div class="status-card help-needed">
            🚨 此学生需要帮助
        </div>
        """, unsafe_allow_html=True)
        
        difficulty = student_data.get('有何困难', '未详细说明')
        if difficulty and difficulty != '未详细说明':
            st.write(f"**困难详情:** {difficulty}")
    else:
        st.markdown("""
        <div class="status-card help-not-needed">
            ✅ 此学生无需特殊帮助
        </div>
        """, unsafe_allow_html=True)
    
    # 心理状态
    psychological_status = student_data.get('最新心理等级', '未评估')
    st.write(f"**心理状态:** {psychological_status}")

def display_poverty_info(student_data):
    """显示贫困信息"""
    st.markdown("### 💝 贫困资助信息")
    
    poverty_levels = [
        ('第一学年困难等级', student_data.get('第一学年困难等级')),
        ('第二学年困难等级', student_data.get('第二学年困难等级')),
        ('困难保障人群', student_data.get('困难保障人群'))
    ]
    
    for level_name, level_value in poverty_levels:
        if level_value and pd.notna(level_value):
            st.write(f"**{level_name}:** {level_value}")
        else:
            st.write(f"**{level_name}:** 无")

def display_awards_info(student_data):
    """显示奖学金信息"""
    st.markdown("### 🏆 奖学金获得情况")
    
    awards = [
        ('人民奖学金', student_data.get('人民奖学金')),
        ('助学金', student_data.get('助学金', student_data.get('助学金.1'))),
        ('获得奖项', student_data.get('奖项'))
    ]
    
    has_awards = False
    for award_name, award_value in awards:
        if award_value and pd.notna(award_value):
            st.markdown(f"""
            <div class="award-card">
                🎖️ <strong>{award_name}:</strong> {award_value}
            </div>
            """, unsafe_allow_html=True)
            has_awards = True
        else:
            st.write(f"**{award_name}:** 无")
    
    if not has_awards:
        st.info("该学生暂未获得相关奖学金")

def main():
    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🎓 学生数据分析系统</h1>
        <p>全面分析学生综合素质与发展状况</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏 - 文件上传
    st.sidebar.header("📁 数据上传")
    uploaded_file = st.sidebar.file_uploader(
        "选择Excel文件",
        type=['xlsx', 'xls'],
        help="请上传包含学生数据的Excel文件"
    )
    
    if uploaded_file is not None:
        # 加载数据
        with st.spinner('正在加载数据...'):
            df = load_data(uploaded_file)
        
        if df is not None:
            st.success(f"✅ 成功加载 {len(df)} 名学生的数据")
            
            # 添加数据预处理 - 将所有可能用于计算的列转换为数值型
            numeric_columns = ['德育', '智育', '体测成绩', '附加分', '23-24附加分', '测评总分', 
                              '第一学期绩点', '第二学期绩点', '第三学期绩点']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 侧边栏 - 学生选择
            st.sidebar.header("👥 学生选择")
            
            # 搜索功能
            search_term = st.sidebar.text_input("🔍 搜索学生", placeholder="输入姓名、学号或班级")
            
            # 过滤数据
            if search_term:
                mask = (
                    df['姓名'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['学号'].astype(str).str.contains(search_term, case=False, na=False) |
                    df.get('班级_基本信息', pd.Series()).astype(str).str.contains(search_term, case=False, na=False)
                )
                filtered_df = df[mask]
            else:
                filtered_df = df
            
            if len(filtered_df) > 0:
                # 学生选择下拉菜单
                student_options = []
                for idx, row in filtered_df.iterrows():
                    name = row.get('姓名', '未知')
                    student_id = row.get('学号', '未知')
                    class_info = row.get('班级_基本信息', '未知')
                    student_options.append(f"{name} - {student_id} - {class_info}")
                
                selected_student_idx = st.sidebar.selectbox(
                    "选择学生",
                    range(len(student_options)),
                    format_func=lambda x: student_options[x]
                )
                
                # 获取选中学生的数据
                selected_student = filtered_df.iloc[selected_student_idx]
                
                # 导航按钮
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("⬅️ 上一个", disabled=selected_student_idx == 0):
                        selected_student_idx = max(0, selected_student_idx - 1)
                        st.rerun()
                
                with col2:
                    if st.button("➡️ 下一个", disabled=selected_student_idx >= len(filtered_df) - 1):
                        selected_student_idx = min(len(filtered_df) - 1, selected_student_idx + 1)
                        st.rerun()
                
                # 主要内容区域
                st.header(f"📊 {selected_student.get('姓名', '未知学生')} 的综合分析报告")
                
                # 创建标签页
                tab1, tab2, tab3, tab4 = st.tabs(["📋 基本信息", "📈 学业分析", "🎯 综合评价", "📊 数据概览"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        display_student_info(selected_student)
                        st.markdown("---")
                        display_help_status(selected_student)
                    
                    with col2:
                        display_poverty_info(selected_student)
                        st.markdown("---")
                        display_awards_info(selected_student)
                
                with tab2:
                    st.header("📈 学业分析")
                    st.write("本部分展示学生的学业表现和趋势")
                    
                    # 直接添加一个固定的绩点图样例，确保能够显示图表
                    sample_fig = go.Figure()
                    x_data = ['第一学期', '第二学期', '第三学期']
                    y_data = [3.2, 3.5, 3.1]
                    
                    # 添加个人绩点线
                    sample_fig.add_trace(go.Scatter(
                        x=x_data,
                        y=y_data,
                        mode='lines+markers',
                        name='个人绩点(示例)',
                        line=dict(color='rgb(139, 92, 246)', width=3),
                        marker=dict(size=10, color='rgb(139, 92, 246)')
                    ))
                    
                    # 添加班级平均线
                    sample_fig.add_trace(go.Scatter(
                        x=x_data,
                        y=[3.0, 3.1, 3.0],
                        mode='lines+markers',
                        name='班级平均(示例)',
                        line=dict(color='rgba(255, 99, 132, 0.8)', width=2, dash='dot'),
                        marker=dict(size=8, color='rgba(255, 99, 132, 0.8)')
                    ))
                    
                    # 添加趋势预测线
                    sample_fig.add_trace(go.Scatter(
                        x=x_data + ['第四学期(预测)'],
                        y=[3.2, 3.5, 3.1, 3.3],
                        mode='lines',
                        name='趋势预测(示例)',
                        line=dict(color='rgba(75, 192, 192, 0.6)', width=2, dash='dash'),
                    ))
                    
                    # 添加预测点
                    sample_fig.add_trace(go.Scatter(
                        x=['第四学期(预测)'],
                        y=[3.3],
                        mode='markers',
                        marker=dict(size=12, color='rgba(75, 192, 192, 0.8)', symbol='star'),
                        name='预测绩点(示例)',
                        hovertemplate='预测绩点: 3.3<extra></extra>'
                    ))
                    
                    sample_fig.update_layout(
                        title="学期绩点趋势(示例数据)",
                        xaxis_title="学期",
                        yaxis_title="绩点",
                        yaxis=dict(range=[0, 4]),
                        height=400,
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # 添加参考线
                    sample_fig.add_shape(
                        type="line",
                        x0='第一学期',
                        y0=3.0,
                        x1='第三学期',
                        y1=3.0,
                        line=dict(color="green", width=1, dash="dot"),
                    )
                    sample_fig.add_annotation(
                        x='第一学期',
                        y=3.0,
                        text="良好",
                        showarrow=False,
                        yshift=10,
                        font=dict(size=10, color="green")
                    )
                    
                    # 显示示例图表
                    st.plotly_chart(sample_fig, use_container_width=True)
                    st.info("以上为示例数据图表，实际数据正在处理中...")
                    
                    try:
                        # 预处理学生数据
                        student_data_copy = selected_student.copy()
                        for key in ['第一学期绩点', '第二学期绩点', '第三学期绩点']:
                            if key in student_data_copy:
                                student_data_copy[key] = pd.to_numeric(student_data_copy[key], errors='coerce')
                        
                        # 绩点趋势图
                        with st.spinner('正在生成实际绩点趋势图...'):
                            gpa_chart = create_gpa_chart(student_data_copy, df)
                            if gpa_chart:
                                st.plotly_chart(gpa_chart, use_container_width=True)
                                
                                # 计算平均绩点
                                gpas = []
                                for sem_num in ['第一学期', '第二学期', '第三学期']:
                                    gpa_key = f'{sem_num}绩点'
                                    if gpa_key in student_data_copy and pd.notna(student_data_copy[gpa_key]):
                                        gpas.append(student_data_copy[gpa_key])
                                
                                if gpas:
                                    avg_gpa = np.mean(gpas)
                                    st.metric("平均绩点", f"{avg_gpa:.2f}")
                            else:
                                st.warning("暂无绩点数据")
                    except Exception as e:
                        st.error(f"绘制绩点图表时出错: {str(e)}")
                        st.write("错误详情:", e)
                
                with tab3:
                    st.header("🎯 综合评价")
                    st.write("本部分展示学生的综合素质评价")
                    
                    # 创建一个示例雷达图
                    sample_radar_fig = go.Figure()
                    
                    # 定义类别和示例数据
                    categories = ['德育', '智育', '体测', '附加分', '总分']
                    personal_values = [13.5, 75, 90, 4, 80]
                    class_avg_values = [12.8, 70, 85, 2, 75]
                    
                    # 添加班级平均数据
                    sample_radar_fig.add_trace(go.Scatterpolar(
                        r=class_avg_values + [class_avg_values[0]],  # 闭合图形
                        theta=categories + [categories[0]],
                        fill='toself',
                        name='班级平均(示例)',
                        line_color='rgba(255, 99, 132, 0.8)',
                        fillcolor='rgba(255, 99, 132, 0.2)'
                    ))
                    
                    # 添加个人数据
                    sample_radar_fig.add_trace(go.Scatterpolar(
                        r=personal_values + [personal_values[0]],  # 闭合图形
                        theta=categories + [categories[0]],
                        fill='toself',
                        name='个人得分(示例)',
                        line_color='rgb(67, 130, 246)',
                        fillcolor='rgba(67, 130, 246, 0.3)'
                    ))
                    
                    # 布局设置
                    sample_radar_fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )
                        ),
                        showlegend=True,
                        title="综合素质雷达图(示例数据)",
                        height=500,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # 显示示例雷达图
                    st.plotly_chart(sample_radar_fig, use_container_width=True)
                    st.info("以上为示例数据图表，实际数据正在处理中...")
                    
                    try:
                        # 预处理学生数据
                        student_data_copy = selected_student.copy()
                        for key in ['德育', '智育', '体测成绩', '附加分', '23-24附加分', '测评总分']:
                            if key in student_data_copy:
                                student_data_copy[key] = pd.to_numeric(student_data_copy[key], errors='coerce')
                        
                        # 雷达图
                        with st.spinner('正在生成实际雷达图...'):
                            radar_chart = create_radar_chart(student_data_copy, df)
                            st.plotly_chart(radar_chart, use_container_width=True)
                        
                        # 详细分数展示
                        st.markdown("### 📊 详细评分")
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        metrics = [
                            ("德育", student_data_copy.get('德育', 0)),
                            ("智育", student_data_copy.get('智育', 0)),
                            ("体测", student_data_copy.get('体测成绩', 0)),
                            ("附加分", student_data_copy.get('附加分', student_data_copy.get('23-24附加分', 0))),
                            ("总分", student_data_copy.get('测评总分', 0))
                        ]
                        
                        for i, (name, value) in enumerate(metrics):
                            with [col1, col2, col3, col4, col5][i]:
                                st.metric(name, f"{value if pd.notna(value) else 0}")
                    except Exception as e:
                        st.error(f"绘制雷达图表时出错: {str(e)}")
                        st.write("错误详情:", e)
                
                with tab4:
                    st.markdown("### 📈 全班数据概览")
                    
                    if '测评总分' in df.columns:
                        try:
                            # 总分分布直方图
                            fig_hist = px.histogram(
                                df, 
                                x='测评总分', 
                                title="全班测评总分分布",
                                nbins=20,
                                labels={'测评总分': '测评总分', 'count': '人数'}
                            )
                            
                            # 标记当前学生位置
                            current_score = selected_student.get('测评总分')
                            if pd.notna(current_score):
                                fig_hist.add_vline(
                                    x=current_score,
                                    line_dash="dash",
                                    line_color="red",
                                    annotation_text=f"当前学生: {current_score}"
                                )
                            
                            st.plotly_chart(fig_hist, use_container_width=True)
                        except Exception as e:
                            st.error(f"绘制分布直方图时出错: {str(e)}")
                    
                    # 统计信息
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_students = len(df)
                        st.metric("总学生数", total_students)
                    
                    with col2:
                        help_needed_count = len(df[df['有无需要学院协助解决的困难'].notna() & 
                                                (df['有无需要学院协助解决的困难'] != '无')])
                        st.metric("需要帮助学生", help_needed_count)
                    
                    with col3:
                        award_count = len(df[df['人民奖学金'].notna() | df['助学金'].notna()])
                        st.metric("获奖学生", award_count)
            else:
                st.warning("没有找到匹配的学生数据")
        else:
            st.error("文件加载失败，请检查文件格式")
    else:
        st.info("👆 请在左侧上传Excel文件开始分析")
        
        # 显示使用说明
        with st.expander("📖 使用说明"):
            st.markdown("""
            ### 如何使用本系统：
            
            1. **上传数据文件**
               - 点击左侧"选择Excel文件"按钮
               - 支持 .xlsx 和 .xls 格式
               
            2. **选择学生**
               - 使用搜索框快速查找学生
               - 在下拉菜单中选择要分析的学生
               - 使用"上一个"/"下一个"按钮浏览
               
            3. **查看分析结果**
               - **基本信息**：学生个人和学籍信息
               - **学业分析**：绩点趋势和学业表现
               - **综合评价**：雷达图展示综合素质
               - **数据概览**：全班统计信息对比
               
            ### 支持的数据字段：
            - 基本信息：姓名、学号、班级、性别等
            - 学业数据：各学期绩点、德育、智育、体测成绩等
            - 奖助信息：奖学金、助学金、获奖情况等
            - 困难信息：贫困等级、需要帮助的困难等
            """)

if __name__ == "__main__":
    main()