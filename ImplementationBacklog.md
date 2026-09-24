# 實作狀態與待辦

本文件於 2026-09-24 依目前 Backend `develop@9721918`、Frontend `develop@8078669` 與 Spec `main@f598377` 重新核對。下列項目均已進入現行程式；本輪沒有仍標示為 Planned 的產品功能。歷史測試數字保留實際執行時間，不以本次文件同步冒充全量重測。

## 完成項目摘要

| ID | 功能 | 狀態 | 主要實作／驗證 |
|---|---|---|---|
| BE-001 | Task 到期提醒背景工作 | 已完成 | Hangfire Scanner／Sender、SQL 冪等／claim／retry、`ReminderServiceTests` |
| BE-002 | 本人名稱與電話維護 | 已完成 | `GET/PUT /users/me/profile`、`OwnProfileValidator`、`UserService`、AuditLog |
| FE-001 | 個人設定畫面 | 已完成 | `SettingsView` 分離個人資料與操作偏好，更新後同步導覽名稱 |
| FE-002 | 使用者清單內聯管理 | 已完成 | 每列系統角色下拉選單與啟用狀態開關，使用原子 administration endpoint |
| FE-003 | 專案成員可搜尋下拉選單 | 已完成 | `SearchableSelectDropdown`、member-candidate API、帳號／姓名篩選 |
| SEC-001 | Bootstrap Admin 保護 | 已完成 | 清單與候選人排除，三個帳號管理 API 與直接加入專案皆有後端保護 |

## 待辦狀態

- 目前沒有經產品規格確認但尚未實作的 backlog。
- 若後續要把 `Accounts.PhoneNumber` 的 30 字上限提升為資料庫 constraint，需要新增 migration 並先清查既有資料；目前限制位於 Application 與 Frontend。
- 本文件只記錄已確認的產品工作。新需求必須先同步 User Story、Flowchart、Schema／StaticData、C4 與 Test Cases，再加入新的 backlog ID。

## BE-001 Task 到期提醒背景工作

- 狀態：已完成（2026-09-16）
- 需求來源：`UserStory.md` 的「5. 接收 Task 到期提醒」
- 流程來源：`Flowchart/E-mail 任務到期提醒.md`

### 已定案規則

- 每個 Project 必須有合法的 IANA `TimeZoneId`；依 Project 當地時間每日 08:00 執行提醒判斷。
- 同一 Project／當地提醒日期只執行一次；08:00 漏跑時在同一當地日恢復後補跑，跨日不補前一日，DST 不得造成重複或遺漏。
- 未完成 Task 的提醒期間為到期前第 3 天至逾期後第 3 天，每天提醒一次，超過逾期第 3 天後停止提醒。
- 收件人帳號必須仍啟用且已完成 E-mail 驗證。
- 同一個 Task、收件人及提醒日期不得重複寄送。
- 不另外限制寄件網域或訂定業務層的寄送速率；以 E-mail 服務回傳成功，且系統成功記錄寄送時間與服務回應編號，作為成功寄出的判定。
- 初次寄送失敗後最多重試 3 次；初次寄送不計入重試次數，重試間隔依序為 5、15、60 分鐘。達到上限後停止重試，同時寫入資料庫與結構化 log 告警；本期不提供告警管理 UI。

### 後端實作範圍

- 建立每日掃描未完成 Task 的排程工作。
- 依 Project 的 IANA `TimeZoneId` 計算當地日期及到期前第 3 天至逾期後第 3 天的提醒範圍。
- 建立 Project／當地提醒日期的執行冪等控制，支援同日補跑與 DST 邊界。
- 建立可防止重複寄送的提醒紀錄與唯一限制。
- 將掃描工作與單封 E-mail 寄送工作分離。
- 寄送前重新讀取 Task、收件人與提醒狀態。
- 記錄寄送狀態、寄送時間、服務回應編號、錯誤與重試次數。
- 補齊成功、略過、重複排程、寄送失敗、重試成功及達到重試上限的測試。

### 完成條件

- 後端程式、資料庫 migration 與測試均已完成並通過驗證。
- 排程重複執行或多個 worker 同時處理時，不會對同一提醒日期重複寄送。
- 對應實作：`ProjectManagementWeb.Infrastructure/Services/ReminderService.cs`、`ProjectManagementWeb.Infrastructure/Jobs/ReminderJobs.cs`、`ProjectManagementWeb.Api/Program.cs`。
- 對應 migration：`20260916075443_AddTaskReminders`；Hangfire SQL schema 由 migrator 初始化，runtime 帳號維持無 DDL 權限。
- 對應自動化：`ReminderServiceTests` 8 個合併案例，2026-09-16 完整 Integration Passed 98／Failed 0／Skipped 0；隔離 Compose 啟動與 Playwright Passed 22／Failed 0／Skipped 0。這是提醒功能完成時的歷史證據；目前全量基線請查看 `TestCases/ProjectManagementWeb-TestCases.md` §8.1。

## BE-002／FE-001 本人名稱與電話維護

- 狀態：已完成（2026-09-21）
- 後端：`UsersController`、`IUserService`、`OwnProfileResponse`、`UpdateOwnProfileRequest`、`OwnProfileValidator` 與 `UserService`。
- 前端：`SettingsView`、Profile HTTP adapter／DTO mapper、Auth store 顯示名稱同步。
- 契約：名稱 trim 後 1–100 字；電話可清除，非空值 trim 後最多 30 字且符合電話格式；只更新本人，不包含帳號、Email、角色或啟用狀態。
- 驗證：2026-09-21 Backend Integration Passed 101、Frontend Vitest Passed 79、隔離 Playwright desktop／mobile Passed 26；Failed 0、Skipped 0。

## FE-002／FE-003／SEC-001 使用者與成員管理 UX

- 狀態：已完成（2026-09-19～2026-09-21）
- `/users` 不顯示 Bootstrap Admin；具管理 Functions 者可由清單直接變更角色或狀態，仍由 `PUT /users/{id}/administration` 以單一交易處理。
- `/users/{id}` 顯示名稱、電話、Email、驗證與角色；個資唯讀，管理表單只處理角色與啟用狀態。
- Project Detail 使用 `SearchableSelectDropdown` 呈現 member candidates，支援帳號或姓名篩選；角色仍使用多選元件。
- 2026-09-24 本輪以獨立 SQL volume、臨時帳密及 desktop Playwright 實際建立 Project／Task 並擷取 16 張 UI Mock；文件擷取案例 Passed 1／Failed 0，結束後容器與 volume 已清除。這只證明本輪畫面擷取流程，不取代 §8.1 的正式全量回歸。
