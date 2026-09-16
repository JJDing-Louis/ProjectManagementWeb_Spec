# 註冊、Email 驗證與登入

## 註冊與 Email 驗證

```mermaid
flowchart TB
    registrationStart([進入註冊頁]) --> enterRegistration[輸入帳號、顯示名稱、Email、密碼與確認密碼]
    enterRegistration --> registrationValid{格式正確且帳號、Email 未重複？}
    registrationValid -->|否| showRegistrationError[顯示欄位錯誤]
    showRegistrationError --> enterRegistration
    registrationValid -->|是| createPendingAccount[建立待驗證帳號]
    createPendingAccount --> issueVerification[建立 3 分鐘、帳號綁定、一次性 Token]
    issueVerification --> sendVerification[寄送驗證信]
    sendVerification --> emailSent{寄送成功？}
    emailSent -->|否| logFailure[保留 Failed 紀錄與不含敏感資料的 Warning Log]
    logFailure --> showResend[顯示一般訊息並保留重新寄送；舊 Token 不失效]
    showResend --> resendAllowed{冷卻、帳號與 IP 限制允許？}
    resendAllowed -->|否| showGeneric[帳號／冷卻回一般 200；IP 濫用回 429]
    showGeneric --> showResend
    resendAllowed -->|是| issueVerification
    emailSent -->|是| openVerification[使用者開啟驗證連結]
    openVerification --> tokenValid{Token 為最新版、帳號相符、未使用且未滿 3 分鐘？}
    tokenValid -->|否| showExpired[顯示連結失效並提供重新寄送]
    showExpired --> showResend
    tokenValid -->|是| activateAccount[標記 Email 已驗證，角色維持 Viewer]
    activateAccount --> registrationFinished([進入登入頁])
```

## 登入

```mermaid
flowchart TB
    loginStart([進入登入頁]) --> enterCredentials[輸入帳號與密碼]
    enterCredentials --> rateLimited{帳號或來源 IP<br/>15 分鐘內已達 5 次失敗？}
    rateLimited -->|是| recordLimited[記錄 RateLimited 稽核與安全 Warning Log]
    recordLimited --> showRateLimit[回 429 rate_limited]
    showRateLimit --> loginStart
    rateLimited -->|否| loginAllowed{帳密正確且未停用？}
    loginAllowed -->|否| recordFailure[以帳號與 IP 雜湊記錄 InvalidCredentials]
    recordFailure --> fifthFailure{本次為第 5 次失敗？}
    fifthFailure -->|否| showLoginError[回 401 並顯示一般性登入失敗訊息]
    fifthFailure -->|是| showRateLimit
    showLoginError --> loginStart
    loginAllowed -->|是| taskList([進入 Task Item 清單])
```

登入失敗訊息不應透露帳號是否存在，且不得鎖定帳號。同一帳號或來源 IP 在滾動 15 分鐘內第 5 次失敗起回 429；共用 SQL 計數讓多執行個體採用同一門檻。只有 allowlist 內的 Proxy 才可提供 forwarded IP，否則一律使用直接連線位址；安全 Log 不記錄帳號、IP、密碼或 Token。已停用的帳號不能登入；Email 尚未驗證的帳號可以登入，但 Access Token 與當前帳號資料的有效系統角色固定為 `Viewer`，不得進行寫入操作。Email 驗證完成後仍維持 `Viewer`，不會自動晉升為 `User`；必須由 Admin 另行調整系統角色。驗證 Token 自簽發起有效 3 分鐘且只能使用一次；成功重寄才會使舊 Token 失效，SMTP 失敗只留安全 Log，不得廢止使用者原本仍有效的 Token。
