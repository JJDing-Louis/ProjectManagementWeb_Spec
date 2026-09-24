# 靜態資料與固定代碼

本文於 2026-09-24 依 `ApplicationDbContext.SeedStaticData`、Domain constants 與 enums 核對。資料庫 seed 的 GUID 由 `SeedIds.Create` 依固定字串產生；呼叫端必須使用 API 回傳的 ID，不得假設為 `0`、`1` 等流水號。

## System Role

| Name | 說明 | 主要 Functions |
|---|---|---|
| `Admin` | 最高管理者 | `SystemFunctions.All` 全部 18 項 |
| `Administrator` | 後台管理員 | 專案／成員／Task 全域管理、留言、本人偏好與帳號讀取；不含帳號角色及狀態異動 |
| `User` | 一般前台使用者 | 讀取專案／Task、更新被指派 Task、留言與本人偏好 |
| `Viewer` | 瀏覽者 | 讀取專案、Task、留言與本人偏好；本人 Profile 另由登入身分授權，不屬於 Function seed |

每個 Account 最多一個 System Role，由 `AccountRoles.UserId` UNIQUE index 保證。未完成 Email 驗證者登入後，有效 Role 與 Functions 固定降為 `Viewer`。

## Function

| 類別 | Code |
|---|---|
| Account | `accounts.read`、`accounts.manage-role`、`accounts.manage-status` |
| Project | `projects.read`、`projects.create`、`projects.manage-all`、`project-members.manage-all` |
| Task | `tasks.read`、`tasks.create`、`tasks.update-any`、`tasks.update-assigned`、`tasks.delete` |
| Comment | `comments.read`、`comments.create`、`comments.update-own`、`comments.delete-own` |
| Preference | `preferences.read-own`、`preferences.update-own` |

`Admin` 取得全部 Function。`Administrator` 不取得 `accounts.manage-role`、`accounts.manage-status` 與 `tasks.update-assigned`；`User` 不取得帳號與全域管理 Functions；`Viewer` 只有 read Functions 與 `preferences.read-own`。

## Project Role

| Code／Name | 說明 |
|---|---|
| `ProjectManager` | 專案經理；可管理自己專案的成員與專案資料 |
| `FrontendDeveloper` | 前端開發人員 |
| `BackendDeveloper` | 後端開發人員 |
| `SystemAnalyst` | 系統分析師 |
| `Member` | 一般組員；新增成員畫面預設選項 |

一名 Project Member 可同時擁有多個 Project Role；Role 集合至少一個，更新採完整取代。

## Project Status

| Value | 說明 |
|---|---|
| `Pending` | 尚未開始 |
| `Active` | 進行中 |
| `Completed` | 已完成 |
| `Archived` | 已封存 |

四種合法狀態目前允許任意互轉，也允許更新為相同狀態。

## Task Status

| Value | 說明 |
|---|---|
| `Pending` | 尚未開始 |
| `InProgress` | 處理中 |
| `Blocked` | 受阻 |
| `Completed` | 已完成 |

四種合法狀態目前允許任意互轉，也允許更新為相同狀態；Task 清單的批次目標狀態預設為 `InProgress`。

## 系統狀態代碼

下列為 Domain enum／固定代碼，不是獨立靜態資料表：

| 類別 | Values |
|---|---|
| `BusinessCodeType` | `Project`、`Task` |
| `EmailDeliveryStatus` | `Pending`、`Sent`、`Failed` |
| `TaskReminderStatus` | `Pending`、`Processing`、`Retry`、`Sent`、`Failed`、`Cancelled` |
| `EmailVerificationResendOutcome` | `Allowed`、`NotEligible`、`CooldownLimited`、`AccountLimited`、`IpLimited` |
| `LoginFailureOutcome` | `InvalidCredentials`、`RateLimited` |

## 不屬於靜態資料的設定

- SMTP 寄件人、帳密與 Host 來自 `Smtp` configuration／secret，不存在 `TParameter` seed；文件不得放測試信箱或密碼。
- Bootstrap Admin 的 Account、Email、Password 來自 `BootstrapAdmin` configuration。資料庫啟動程序會建立或修復該帳號為啟用的 `Admin`，但不將其寫成固定 seed Account。
- AuditLog 的 Action（例如 `CreateProject`、`UpdateOwnProfile`）是各 use case 寫入的事件名稱，不是 `Action` 靜態表。
