# UI Mock 與現行畫面

`UIMock/` 內 PNG 已於 2026-09-24 由現行 Vue 3、ASP.NET Core 與 SQL Server 隔離環境實際擷取，不再是早期線框草圖。擷取使用 1440×900 Desktop Chrome、繁體中文、臨時 Bootstrap Admin／Owner 與全新 SQL volume；完成後測試容器與 volume 已清除。

畫面是特定測試資料的視覺快照。欄位規則、授權、交易與錯誤契約仍以 `UserStory.md`、Flowchart、API source 與 Test Cases 為準。

## 路由與畫面索引

| PNG | 對應路由／狀態 | 現行畫面重點 |
|---|---|---|
| `SignIn.png` | `/sign-in` | 帳號、密碼、註冊與重新寄送入口 |
| `SignUp.png` | `/sign-up` | 帳號、顯示名稱、Email、密碼、確認密碼 |
| `VerifyEmail.png` | `/verify-email?accountId=...&emailSent=true` | 註冊成功後提示使用者開啟驗證信 |
| `VerifyEmailFailure.png` | `/verify-email?accountId=...&emailSent=false` | 帳號已建立但寄信失敗，提供重新寄送入口 |
| `ResendVerification.png` | `/resend-verification` | 以帳號或 Email 重新提出驗證信請求 |
| `ProjectList.png` | `/projects` | 單一搜尋、狀態篩選、分頁與新增入口 |
| `ProjectForm.png` | `/admin/projects/new` | 名稱、Owner、Pending 初始狀態、IANA 時區與說明 |
| `ProjectDetail.png` | `/projects/{projectId}` | Project 編號、說明、成員可搜尋下拉、多重角色與 Overview |
| `TaskItemList.png` | `/projects/{projectId}/task-items` | 搜尋、篩選、排序、checkbox 與批次狀態工具列 |
| `TaskItemForm.png` | `/admin/projects/{projectId}/task-items/new` | 標題、指派對象、開始／交付時間與選填說明 |
| `TaskItemDetail.png` | `/projects/{projectId}/task-items/{taskId}` | Task 詳情、狀態、編輯導向與留言串 |
| `UserList.png` | `/users` | 搜尋、角色篩選、每列角色下拉選單、帳號狀態開關與詳情入口 |
| `UserDetail.png` | `/users/{userId}` | 帳號、名稱、電話、Email、驗證狀態與角色／狀態管理表單 |
| `UserSetting.png` | `/settings` | 本人名稱／電話與獨立的語言／批次確認偏好 |
| `Forbidden.png` | `/forbidden` | 403 權限不足狀態 |
| `NotFound.png` | 未匹配 route | 404 Page not found 狀態 |

## 操作契約補充

- Project Detail 先載入 member candidates，`SearchableSelectDropdown` 在候選選項中依帳號或姓名篩選；Project Role 仍使用多選元件，至少保留一個角色。
- 使用者清單不顯示 Bootstrap Admin。角色下拉選單或啟用狀態開關一變更，就呼叫原子 administration endpoint；User Detail 保留完整表單入口。
- `/settings` 的名稱與電話只更新本人。帳號、Email、系統角色與啟用狀態不能由此畫面修改；操作偏好使用另一個儲存按鈕。
- Task checkbox 只用於批次更新狀態，不支援批次刪除；單筆刪除為軟刪除，且只對具有權限者顯示。
- Project／Task 編號只由後端產生，畫面不提供 Code 輸入欄位；API 與 route 仍使用 GUID。

## 現行畫面限制

- Task API 只回傳 `createdByAccountId` 與 `assignedAccountId`。前端以 Project Detail 的成員集合轉換顯示名稱；若帳號不在該集合中，就直接顯示 Account GUID。`TaskItemList.png` 與 `TaskItemDetail.png` 的建立者欄位即為此行為。
- 繁體中文模式仍有前端元件直接寫入的英文文字，包括註冊頁副標、驗證頁返回登入連結、Task 搜尋 placeholder、Auth Layout 頁尾與 404 的 `Page not found`。PNG 保留現行實際畫面，沒有在 Spec 圖片中人工翻譯。
