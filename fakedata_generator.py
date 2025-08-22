import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import io
import zipfile

st.title('가상 데이터 자동 생성기')

st.markdown('''
- 여러 파일의 컬럼명, 값 타입, 범위 등을 입력하세요.
- 각 파일마다 300행의 랜덤 데이터를 생성해 ZIP 파일로 다운로드할 수 있습니다.
''')

def get_value(val_type, min_val, max_val):
    if val_type == '숫자':
        return np.random.randint(int(min_val), int(max_val) + 1)
    elif val_type == '실수':
        return np.random.uniform(float(min_val), float(max_val))
    elif val_type == '문자':
        return ''.join(np.random.choice(list('가나다라마바사아자차카타파하'), size=5))
    elif val_type == '날짜':
        start = datetime.strptime(min_val, '%Y-%m-%d')
        end = datetime.strptime(max_val, '%Y-%m-%d')
        delta = (end - start).days
        rand_days = np.random.randint(0, delta + 1)
        return (start + timedelta(days=rand_days)).strftime('%Y-%m-%d')
    else:
        return ''

# 폴더 경로 입력란 제거 (Streamlit Cloud에서는 불필요)
# folder = st.text_input('저장할 폴더 경로', value='output')

file_count = st.number_input('생성할 파일 개수', min_value=1, max_value=10, value=1, step=1)

file_inputs = []
for i in range(file_count):
    st.subheader(f'파일 {i+1} 설정')
    file_name = st.text_input(f'파일명 (확장자 제외) #{i+1}', key=f'file_name_{i}')
    col_count = st.number_input(f'컬럼 개수 #{i+1}', min_value=1, max_value=20, value=3, step=1, key=f'col_count_{i}')
    columns = []
    for j in range(col_count):
        col1, col2, col3, col4 = st.columns([2,2,2,2])
        with col1:
            col_name = st.text_input(f'컬럼명 #{j+1}', key=f'col_name_{i}_{j}')
        with col2:
            val_type = st.selectbox(f'값 타입 #{j+1}', ['숫자', '실수', '문자', '날짜'], key=f'val_type_{i}_{j}')
        with col3:
            min_val = st.text_input(f'최소/시작값 #{j+1}', key=f'min_val_{i}_{j}')
        with col4:
            max_val = st.text_input(f'최대/끝값 #{j+1}', key=f'max_val_{i}_{j}')
        columns.append({'name': col_name, 'type': val_type, 'min': min_val, 'max': max_val})
    file_inputs.append({'file_name': file_name, 'columns': columns})

if st.button('가상 데이터 생성 및 다운로드'):
    # 입력값 검증
    all_valid = True
    error_messages = []
    
    for i, file_input in enumerate(file_inputs):
        if not file_input['file_name'].strip():
            error_messages.append(f"파일 {i+1}의 파일명을 입력하세요.")
            all_valid = False
        
        for j, col in enumerate(file_input['columns']):
            if not col['name'].strip():
                error_messages.append(f"파일 {i+1}의 컬럼 {j+1} 이름을 입력하세요.")
                all_valid = False
            if not col['min'].strip() or not col['max'].strip():
                error_messages.append(f"파일 {i+1}의 컬럼 {j+1} 최소/최대값을 입력하세요.")
                all_valid = False
    
    if not all_valid:
        for msg in error_messages:
            st.error(msg)
    else:
        try:
            # 여러 파일을 ZIP으로 묶어서 다운로드 제공
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_input in file_inputs:
                    data = {}
                    for col in file_input['columns']:
                        data[col['name']] = [get_value(col['type'], col['min'], col['max']) for _ in range(300)]
                    df = pd.DataFrame(data)
                    
                    # Excel 파일을 메모리에 생성
                    excel_buffer = io.BytesIO()
                    df.to_excel(excel_buffer, index=False)
                    excel_buffer.seek(0)
                    
                    # ZIP에 추가
                    zip_file.writestr(f"{file_input['file_name']}.xlsx", excel_buffer.getvalue())
            
            zip_buffer.seek(0)
            
            st.success(f'총 {len(file_inputs)}개의 파일이 생성되었습니다!')
            
            # 다운로드 버튼 제공
            st.download_button(
                label=" ZIP 파일 다운로드",
                data=zip_buffer,
                file_name="generated_data.zip",
                mime="application/zip"
            )
            
        except Exception as e:
            st.error(f'파일 생성 중 오류가 발생했습니다: {e}')
