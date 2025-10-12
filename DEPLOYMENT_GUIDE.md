# 🚀 Streamlit Cloud 배포 가이드

## ✅ 준비 완료 체크리스트

- [x] `requirements.txt` 생성 완료
- [x] `.gitignore` 생성 완료
- [x] `README.md` 생성 완료
- [x] `.streamlit/secrets.toml.example` 생성 완료
- [x] CSV 파일 크기 확인 (27.39MB - GitHub 업로드 가능!)

---

## 📋 Step 1: GitHub 계정 및 저장소 생성

### 1-1. GitHub 계정 만들기 (없는 경우)
1. https://github.com 접속
2. **Sign up** 클릭
3. 이메일, 비밀번호 입력
4. 계정 생성 완료!

### 1-2. 새 저장소 생성
1. GitHub 로그인 후 오른쪽 상단 **+** 클릭
2. **New repository** 선택
3. 설정:
   ```
   Repository name: zalcoach
   Description: 상업 시설 데이터 분석 & 날씨 마케팅 챗봇
   Visibility: Public (무료 배포를 위해 필수!)
   ✅ Add a README file (체크 안 함)
   ```
4. **Create repository** 클릭

---

## 📤 Step 2: 코드 GitHub에 업로드

### 방법 A: GitHub Desktop 사용 (추천 - 초보자용) ⭐

#### 2-A-1. GitHub Desktop 설치
1. https://desktop.github.com 접속
2. **Download for Windows** 클릭
3. 설치 후 GitHub 계정으로 로그인

#### 2-A-2. 저장소 연결
1. GitHub Desktop 실행
2. **File → Add Local Repository** 클릭
3. **Choose...** 클릭 후 `C:\Users\admin\Desktop\zalcoach` 선택
4. **Add repository** 클릭

#### 2-A-3. 첫 커밋 및 업로드
1. 왼쪽에 변경된 파일 목록 표시됨
2. 아래 **Summary** 입력: `Initial commit`
3. **Commit to main** 클릭
4. 상단 **Publish repository** 클릭
5. ✅ **Keep this code private** 체크 해제 (Public으로!)
6. **Publish repository** 클릭
7. 완료! 🎉

### 방법 B: Git 명령어 사용 (개발자용)

PowerShell에서 실행:

```powershell
# 현재 디렉토리 확인
cd C:\Users\admin\Desktop\zalcoach

# Git 초기화
git init

# 파일 추가
git add .

# 커밋
git commit -m "Initial commit"

# GitHub 저장소 연결 (your-username을 실제 GitHub 아이디로 변경!)
git remote add origin https://github.com/your-username/zalcoach.git

# 업로드
git branch -M main
git push -u origin main
```

---

## 🌐 Step 3: Streamlit Cloud에 배포

### 3-1. Streamlit Cloud 가입
1. https://share.streamlit.io 접속
2. **Sign in with GitHub** 클릭
3. GitHub 계정으로 로그인
4. **Authorize streamlit** 클릭

### 3-2. 앱 배포하기
1. **New app** 버튼 클릭 (오른쪽 상단)
2. 설정 입력:
   ```
   Repository: your-username/zalcoach
   Branch: main
   Main file path: gemini_rag.py
   ```
3. **Advanced settings** 클릭
4. **Python version**: 3.11 선택
5. **Secrets** 섹션에 다음 입력:
   ```toml
   GOOGLE_API_KEY = "여기에_실제_구글_API_키"
   OPENWEATHER_API_KEY = "여기에_실제_날씨_API_키"
   ```
6. **Deploy!** 버튼 클릭

### 3-3. 배포 대기
- ⏳ 처음 배포는 5-10분 소요
- 📦 패키지 설치 중... (진행 상황 표시)
- ✅ 배포 완료 후 URL 제공!

---

## 🎯 Step 4: 배포 완료 및 테스트

### 4-1. 앱 URL 확인
배포 성공 시 다음과 같은 URL 제공:
```
https://your-app-name.streamlit.app
```

### 4-2. 앱 테스트
1. URL 접속
2. 사이드바 → "빠른 테스트 모드" 체크
3. "데이터 로드" 클릭 (4-6분 소요)
4. 질문 입력하여 테스트!

### 4-3. 문제 발생 시
- **Logs** 탭에서 에러 확인
- 주로 발생하는 문제:
  - ❌ API 키 오타 → Secrets 다시 확인
  - ❌ 패키지 버전 충돌 → requirements.txt 수정
  - ❌ 메모리 부족 → 샘플링 모드 기본값으로 설정

---

## 🔧 Step 5: 추가 설정 (선택사항)

### 5-1. 커스텀 도메인 (유료)
- Settings → General → Custom subdomain

### 5-2. 앱 업데이트 방법
1. GitHub Desktop에서 코드 수정
2. Commit → Push
3. Streamlit Cloud 자동 재배포!

### 5-3. 앱 재시작
- Streamlit Cloud → 우측 상단 ⋮ → Reboot app

---

## 💡 유용한 팁

### 성능 최적화
```python
# gemini_rag.py 341번째 줄
use_sample = st.checkbox(
    "빠른 테스트 모드 (10% 샘플링)", 
    value=True,  # 배포 환경에서는 True 권장!
    help="첫 실행 시 권장 (4-6분)"
)
```

### 로딩 메시지 개선
첫 화면에 안내 추가:
```python
st.info("⏳ 첫 로딩 시 4-6분 소요됩니다. 잠시만 기다려주세요!")
```

### API 호출 제한 안내
```python
st.caption("💡 무료 버전 제한: 하루 1,500회 질문 가능")
```

---

## 🆘 문제 해결

### Q1: 배포가 계속 실패해요
**A:** Logs 탭에서 에러 확인 후:
- `ModuleNotFoundError` → requirements.txt에 패키지 추가
- `UnicodeDecodeError` → 이미 해결됨 (자동 인코딩 처리)
- `API key error` → Secrets 설정 확인

### Q2: 앱이 너무 느려요
**A:** 
- 샘플링 모드 기본값으로 설정
- Streamlit Cloud 무료 버전 제한 (1GB RAM)
- 필요시 유료 플랜 고려

### Q3: GitHub에 API 키가 올라갔어요!
**A:**
1. 즉시 API 키 재발급
2. `.gitignore` 확인
3. Git history 삭제 (필요 시)

---

## 📞 지원

문제 발생 시:
1. Streamlit Community Forum: https://discuss.streamlit.io
2. GitHub Issues
3. Streamlit Docs: https://docs.streamlit.io

---

## 🎉 배포 완료!

축하합니다! 이제 전 세계 어디서나 앱에 접속할 수 있습니다!

공유하세요:
- 친구, 동료에게 URL 공유
- 포트폴리오에 추가
- LinkedIn, GitHub 프로필에 링크

**Happy Deploying! 🚀**

