# 현재 접속 세션수 표시 — Firebase presence 설정

`index.html` 좌측 메뉴 하단 「현재 접속 N명」 배지의 설정 절차.
GitHub Pages는 정적 호스팅이므로 접속 집계는 Firebase Realtime Database로 처리.

## 1. Firebase 프로젝트 생성

| 단계 | 내용 |
|---|---|
| 1 | https://console.firebase.google.com 접속 → 프로젝트 추가 |
| 2 | Google 애널리틱스 — 사용 안 함 선택 ※ 불필요 |
| 3 | 빌드 > Realtime Database > 데이터베이스 만들기 |
| 4 | 위치 — `asia-southeast1` ※ 국내 최근접 리전 |
| 5 | 보안 규칙 — 잠금 모드로 시작 ※ 규칙은 3항에서 교체 |

## 2. 웹 앱 등록 · config 입력

프로젝트 설정 > 내 앱 > 웹(`</>`) 추가 → 발급된 `firebaseConfig` 값을
`index.html` 하단 `FIREBASE_CONFIG` 블록에 입력.

```js
const FIREBASE_CONFIG = {
  apiKey: "AIza...",
  authDomain: "프로젝트ID.firebaseapp.com",
  databaseURL: "https://프로젝트ID-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "프로젝트ID",
  appId: "1:000...:web:..."
};
```

`databaseURL` 미입력 시 배지 미표시. ※ 설정 전에도 문서는 정상 동작

## 3. 데이터베이스 보안 규칙

Realtime Database > 규칙 탭에 아래 내용 교체 후 게시.

```json
{
  "rules": {
    "presence": {
      "$room": {
        ".read": true,
        ".write": true,
        "$sid": { ".validate": "newData.isNumber()" }
      }
    }
  }
}
```

`presence` 경로만 개방, 그 외 경로 접근 차단. 값은 타임스탬프(숫자)만 허용.

## 4. 배포

`push.cmd` 실행 → `main` 브랜치 반영 → GitHub Pages 자동 갱신.
루트와 `/docs` 두 경로의 `index.html`을 동일하게 유지.

## 동작 방식

| 항목 | 내용 |
|---|---|
| 접속 등록 | 페이지 로드 시 `presence/manual-202608` 하위에 세션 노드 생성 |
| 이탈 처리 | `onDisconnect` — 탭 종료·네트워크 단절 시 서버가 노드 자동 삭제 |
| 하트비트 | 30초 주기 타임스탬프 갱신 |
| 집계 기준 | 최근 90초 내 갱신된 세션만 카운트 |
| 잔여 정리 | 10분 초과 미갱신 노드는 접속 클라이언트가 삭제 |

## 집계 한계

- 세션 단위 집계 — 동일 사용자가 탭 2개를 열면 2로 계산
- 문서를 열어둔 상태는 실제 열람 여부와 무관하게 접속으로 계산
- 새로고침 시 노드 재생성 — 순간적으로 중복 계산 가능
- 사내망에서 `*.firebasedatabase.app` · `www.gstatic.com` 차단 시 배지 미표시
  ※ 이 경우에도 문서 본문 기능에는 영향 없음

## 보안 유의

- 저장소가 public이므로 `apiKey`는 소스에 노출됨. ※ Firebase 웹 API 키는 비밀값이 아님
- 노출 위험은 규칙으로 통제 — 3항 규칙 적용 시 `presence` 경로 외 접근 불가
- 무단 쓰기로 인한 카운트 조작 가능성 존재. ※ 사내 참고용 지표로만 활용
