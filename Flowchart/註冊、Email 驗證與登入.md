# 註冊、Email 驗證與登入

## 註冊與 Email 驗證

```mermaid
flowchart TB
    registrationStart([進入註冊頁]) --> enterRegistration[輸入帳號、顯示名稱、Email、密碼與確認密碼]
    enterRegistration --> registrationValid{格式正確且帳號、Email 未重複？}
    registrationValid -->|否| showRegistrationError[顯示欄位錯誤]
    showRegistrationError --> enterRegistration
    registrationValid -->|是| createPendingAccount[建立待驗證帳號]
    createPendingAccount --> sendVerification[寄送驗證信]
    sendVerification --> emailSent{寄送成功？}
    emailSent -->|否| showResend[顯示失敗並提供重新寄送]
    showResend --> sendVerification
    emailSent -->|是| openVerification[使用者開啟驗證連結]
    openVerification --> tokenValid{Token 有效且未過期？}
    tokenValid -->|否| showExpired[顯示連結失效並提供重新寄送]
    showExpired --> sendVerification
    tokenValid -->|是| activateAccount[標記 Email 已驗證，角色維持 Viewer]
    activateAccount --> registrationFinished([進入登入頁])
```

## 登入

```mermaid
flowchart TB
    loginStart([進入登入頁]) --> enterCredentials[輸入帳號與密碼]
    enterCredentials --> loginAllowed{帳密正確且未停用？}
    loginAllowed -->|否| showLoginError[顯示一般性登入失敗訊息]
    showLoginError --> loginStart
    loginAllowed -->|是| taskList([進入 Task Item 清單])
```

登入失敗訊息不應透露帳號是否存在。已停用的帳號不能登入；Email 尚未驗證的帳號可以登入，但 Access Token 與當前帳號資料的有效系統角色固定為 `Viewer`，不得進行寫入操作。Email 驗證完成後仍維持 `Viewer`，不會自動晉升為 `User`；必須由 Admin 另行調整系統角色。驗證連結需設定有效期限，過期後由使用者重新寄送。
