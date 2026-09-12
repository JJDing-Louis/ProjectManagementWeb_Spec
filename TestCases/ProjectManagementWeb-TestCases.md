# ProjectManagementWeb 完整測試案例

## 1. 文件資訊

- **產出日期**：2026-09-07
- **需求來源**：`UserStory.md`、`Flowchart/`、`Schema.md`、`StaticData.md`、`UIMock/`、Backend API／EF Core migrations／現有測試、Frontend routes／views／services／現有測試
- **測試範圍**：帳號與驗證、授權與 Session、使用者管理、偏好、專案與成員、Task 清單與異動、留言、到期提醒、SQL 完整性、UI／E2E
- **狀態定義**：`Ready` 表示已有可測介面；`Planned` 表示需求已定義但功能尚未實作，或因契約缺口尚不能執行。
- **自動化覆蓋說明**：僅依目前 repository 中實際存在的測試檔判定；「部分」不代表本次已執行通過。

## 2. 規格衝突決議與缺口

### 2.1 已決議的衝突

| ID | 主題 | 原衝突 | 決議 | 規格修正狀態 |
|---|---|---|---|---|
| CON-001 | 未驗證帳號登入 | 舊 Flowchart 要求已驗證，現行程式允許登入 | 允許登入，但有效角色與 Functions 固定為 `Viewer` | 已更新 User Story 與登入 Flowchart |
| CON-002 | Email 驗證後角色 | 舊 Flowchart 自動授予 `User` | 驗證後維持 `Viewer`，只能由 Admin 改角色 | 已更新驗證 Flowchart |
| CON-003 | 註冊欄位 | 舊草圖缺少顯示名稱與確認密碼 | 帳號、顯示名稱、Email、密碼、確認密碼均必填；顯示名稱 1–100 字 | 已更新 User Story、Flowchart 與 `UIMock/README.md` |
| CON-004 | Project Role 基數 | 舊 Schema／草圖／流程看似單一角色 | 成員可有多個 Project Roles；修改時完整取代且至少一個 | 已更新 User Story、Flowchart、Schema 與 UI 草圖契約 |
| CON-005 | Task 清單批次刪除 | 舊草圖暗示 checkbox 支援批次刪除 | checkbox 只供批次改狀態；刪除為後台每列單筆軟刪除 | 已更新 `UIMock/README.md` |
| CON-006 | 批次目標狀態初始值 | User Story 要求先選狀態，UI 預設 `InProgress` | 保留 `InProgress` 預設值；只在未選 Task 時停用確認 | 已更新 User Story、Flowchart 與 UI 草圖契約 |
| CON-007 | Project 表單限制 | Frontend 與 Backend／DB 不一致 | Name trim 後 1–200 字；Description 選填且最多 4000 字 | 已更新 User Story、Flowchart 與 UI 草圖契約；Frontend 尚待對齊 |
| CON-008 | Task Description 必填 | Frontend 必填，Backend／DB 允許空值 | Description 選填；有值時 trim 後最多 8000 字 | 已更新 User Story、Flowchart 與 UI 草圖契約；Frontend 尚待對齊 |
| CON-009 | 使用者設定範圍 | 舊草圖將個資、系統角色與專案角色放在同頁 | Settings 只管理語言與批次確認偏好；系統角色／啟用狀態在 User Detail；Project Roles 在 Project Detail | 已更新 User Story、C4 與 UI 草圖契約 |
| CON-010 | Schema 主鍵與資料模型 | 舊 Schema 為字串主鍵與明文式 Password | 以 EF migrations／model snapshot 為正式來源，使用 Identity GUID、`PasswordHash`、獨立關聯與 rowversion | `Schema.md` 已依現行模型改寫 |
| CON-011 | C4 Email 範圍 | C4 只繪出驗證信 | 加入到期提醒 Scanner、Sender、紀錄、retry 與告警，全部明確標為 Planned | C4 已更新，不代表功能已實作 |
| CON-012 | Project 清單搜尋方式 | 舊草圖為多欄位查詢與 Owner 篩選 | 單一 search 查 Code／Name／Description，另有 status；無 Owner filter | 已更新 User Story 與 UI 草圖契約 |
| CON-013 | Task 詳情操作型態 | 舊草圖在詳情頁直接 Confirm／Cancel | Task Detail 為詳情與留言；修改導向 `/admin/projects/{projectId}/task-items/{taskId}/edit` | 已更新 User Story、Flowchart、C4 與 UI 草圖契約 |

### 2.2 規格與實作缺口

| ID | 缺口 | 影響 |
|---|---|---|
| GAP-001 | 顯示名稱已定為必填且 trim 後 1–100 字，但 Frontend input 尚未設定 `maxlength=100`。 | API 會拒絕超長輸入，但 UI 無法在送出前提供立即回饋。 |
| GAP-002 | Email 驗證 token 的明確有效期間、重寄後舊 token 是否失效、重寄冷卻／頻率未定義。 | 過期與重送安全案例只能部分執行。 |
| GAP-003 | 登入失敗鎖定、rate limit、CAPTCHA 與稽核要求未定義。 | 暴力嘗試防護無可驗收門檻。 |
| GAP-004 | Project status 的合法狀態轉換未定義；目前 API 接受 enum 內任意目標。 | 只能測現行 enum，不能斷言業務狀態機。 |
| GAP-005 | Task Flowchart 寫需驗證狀態轉換，但正式 Backend contract 表示四種狀態可任意互轉。 | 本文件測目前契約的 4×4 轉換；若要限制需先定義矩陣。 |
| GAP-006 | 建立 Project 的 Owner 是否必須 Email 已驗證、能否為有效 Viewer 未定義；現況只要求啟用帳號。 | 不對驗證狀態自行加限制。 |
| GAP-007 | 批次 Task 最大筆數、request body 上限與大型批次效能門檻未定義。 | 資源耗盡與效能測試沒有 pass/fail 數字。 |
| GAP-008 | 無權限且資源不存在時應優先回 403 或 404 未明定；目前部分 service 先做資源範圍授權。 | 防枚舉與錯誤語意需統一。 |
| GAP-009 | Project 沒有刪除 User Story／API，但 Domain 有 `DeletedAt`。 | 不建立 Project 刪除功能案例。 |
| GAP-010 | `Accounts.NormalizedEmail` 在 runtime 要求唯一，但 migration 不是 UNIQUE。 | 繞過應用服務可能建立重複 Email；列 SQL Planned 案例。 |
| GAP-011 | `RefreshTokens.ReplacedByTokenId` 沒有 FK。 | Token chain 完整性依賴應用服務，資料庫不能獨立保證。 |
| GAP-012 | 到期提醒沒有資料表、migration、排程、worker、API／管理介面與告警查詢。 | 全模組 Planned。 |
| GAP-013 | 現有 Backend 自動化主要是模型、註冊驗證、OpenAPI 與編號 constraint；核心 service/API 授權與交易幾乎未覆蓋。 | 高風險核心流程需優先自動化。 |
| GAP-014 | 現有 Frontend E2E 只涵蓋登入、語言、RWD 導覽、refresh、建立 Project/Task；列表、批次、留言、角色與錯誤流程未涵蓋。 | 多數 P0/P1 案例仍為手動。 |
| GAP-015 | Frontend `AGENTS.md` 仍寫「尚未建立前端專案」，與 repository 現況不符。 | 文件狀態可能誤導測試與開發。 |

## 3. 需求代碼

| 代碼 | 需求 |
|---|---|
| AUTH | 註冊、Email 驗證、登入、refresh、logout |
| US-1 | 查看有權存取的 Task 清單、搜尋、篩選、排序與分頁 |
| US-2 | 單筆／批次 Task 狀態切換與全有或全無交易 |
| US-3 | Task 狀態持久化；checkbox 不持久化 |
| US-4 | Task 詳情、返回條件與留言 |
| US-5 | Task 到期 Email 提醒 |
| US-6 | 後台新增 Task |
| US-7 | 後台修改 Task與 optimistic concurrency |
| US-8 | 後台軟刪除 Task |
| FLOW-PRJ | 建立／修改 Project |
| FLOW-MEMBER | 管理 Project Member 與 Project Role |
| FLOW-USER | 管理系統角色與帳號狀態 |
| PREF | 個人批次確認偏好 |
| API | `/api/v1`、Problem Details、OpenAPI、CSRF/JWT 契約 |
| DB | 正式 EF Core migrations／model snapshot |

## 4. 測試案例

> 每個案例應獨立準備資料。除特別註明外，API 錯誤需同時驗證 HTTP status、RFC 7807 `code` 與資料未被意外改動。

### 4.1 註冊、Email 驗證與登入

#### TC-F-AUTH-001 註冊有效帳號
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、E2E；**狀態**：Ready
- **對應需求**：AUTH；User Story「使用註冊」1–3；API `POST /auth/register`
- **前置條件**：帳號與 Email 均不存在；SMTP 可成功寄信。
- **測試步驟**：1. 取得 CSRF token。2. 送出符合密碼規則且確認密碼一致的註冊資料。3. 查詢 Accounts、AccountRoles、UserPreferences、EmailMessages。
- **預期結果**：201；回傳 accountId 與 `verificationEmailSent=true`；角色為 Viewer、未驗證、啟用；密碼不以原文儲存；建立預設偏好與成功郵件紀錄。
- **資料後置狀態**：新增一帳號、一 Viewer 關聯、一偏好與一寄信紀錄。
- **現有自動化覆蓋**：部分：`ApiSurfaceTests` 只測欄位錯誤；`SignUpView.spec.ts` 只 mock 成功導頁。

#### TC-E-AUTH-002 註冊欄位邊界
- **類型與優先級**：Edge／P1；**測試層級**：Unit、API、UI；**狀態**：Ready
- **對應需求**：AUTH；`RegistrationRules`
- **前置條件**：無。
- **測試步驟**：分別送出帳號 256/257 字、名稱 100/101 字、密碼 9/10 字，以及合法帳號字元 `-._@+`。
- **預期結果**：上限內通過格式驗證；超界回 400 且 errors 對應正確欄位；UI 保留輸入。
- **資料後置狀態**：失敗組不新增帳號；成功組依個案清理。
- **現有自動化覆蓋**：部分：`RegistrationValidatorTests` 僅測一般有效／無效值。

#### TC-ERR-AUTH-003 註冊空白與弱密碼
- **類型與優先級**：Error／P0；**測試層級**：Unit、API、UI；**狀態**：Ready
- **對應需求**：AUTH；API validation contract
- **前置條件**：無。
- **測試步驟**：送出空白帳號／名稱、錯誤 Email、缺大寫／小寫／數字／特殊字元的密碼及不一致確認密碼。
- **預期結果**：400 `validation_error`；所有欄位錯誤一次回傳；前端正確把 `name` 映射為 `displayName`。
- **資料後置狀態**：無帳號、角色、偏好或 Email 紀錄。
- **現有自動化覆蓋**：完整（靜態對應）：`RegistrationValidatorTests`、`ApiSurfaceTests`、`registrationErrors.spec.ts`。

#### TC-ERR-AUTH-004 重複帳號或 Email
- **類型與優先級**：Error／P0；**測試層級**：API、SQL；**狀態**：Ready
- **對應需求**：AUTH；註冊 Flowchart
- **前置條件**：已有指定帳號及 Email。
- **測試步驟**：1. 以相同帳號、不同 Email 註冊。2. 以不同帳號、相同 Email 註冊。3. 模擬兩個並行註冊。
- **預期結果**：應用層拒絕並提供一般欄位錯誤；同 normalized username 不可重複。Email DB 級競態見 TC-SQL-007。
- **資料後置狀態**：僅保留原帳號，不產生孤兒角色／偏好。
- **現有自動化覆蓋**：無。

#### TC-ERR-AUTH-005 註冊缺少或錯誤 CSRF
- **類型與優先級**：Security／P0；**測試層級**：API；**狀態**：Ready
- **對應需求**：API CSRF contract
- **前置條件**：無有效 antiforgery token/cookie 配對。
- **測試步驟**：分別省略 header、只送 header、送錯 token 呼叫 register/login/refresh/logout/confirm/resend。
- **預期結果**：400；任何帳號、token 或資料均不異動。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`ApiSurfaceTests.註冊缺少CsrfToken時應拒絕請求`。

#### TC-ST-AUTH-006 SMTP 失敗但帳號保留
- **類型與優先級**：State／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：AUTH；Frontend contract
- **前置條件**：SMTP gateway 回傳失敗。
- **測試步驟**：完成有效註冊並檢查 response、DB 與驗證頁。
- **預期結果**：201、`verificationEmailSent=false`；帳號仍存在且為 Viewer；EmailMessages 為 Failed 且保留錯誤；UI 顯示重寄入口，不宣稱已寄出。
- **資料後置狀態**：帳號可供登入；新增失敗郵件紀錄。
- **現有自動化覆蓋**：部分：`signUpView.spec.ts`、`verifyEmailView.spec.ts` 只測前端狀態。

#### TC-F-AUTH-007 未驗證帳號以 Viewer 能力登入
- **類型與優先級**：Functional／P0；**測試層級**：API、E2E；**狀態**：Ready
- **對應需求**：AUTH；User Story「使用註冊」2–3；CON-001
- **前置條件**：帳號啟用、密碼正確、Email 未驗證，DB 角色可為 Viewer 或其他角色。
- **測試步驟**：登入後呼叫 `/auth/me`，再嘗試讀取及寫入業務 API。
- **預期結果**：登入成功；有效 role=Viewer，只含 Viewer functions；可讀所屬資料，所有寫入被 403 拒絕。
- **資料後置狀態**：新增 refresh token；業務資料不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-AUTH-008 錯誤帳密與停用帳號使用相同失敗語意
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：AUTH；登入 Flowchart 的防帳號枚舉要求
- **前置條件**：準備不存在帳號、有效帳號與停用帳號。
- **測試步驟**：以不存在帳號、錯密碼、停用帳號登入。
- **預期結果**：皆回 401 `invalid_credentials` 與相同一般訊息；不洩漏帳號存在或停用狀態。
- **資料後置狀態**：不新增 refresh token。
- **現有自動化覆蓋**：無。

#### TC-ST-AUTH-009 Email 驗證成功但角色不自動提升
- **類型與優先級**：State／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：AUTH；User Story「使用註冊」3；CON-002
- **前置條件**：未驗證 Viewer 與有效 token。
- **測試步驟**：呼叫 confirm，重新登入並讀取 `/auth/me` 與 AccountRoles。
- **預期結果**：confirm 200 true、EmailConfirmed=true；系統角色仍是 Viewer，沒有自動新增 User 角色。
- **資料後置狀態**：僅驗證狀態改變。
- **現有自動化覆蓋**：無；`VerifyEmailView` 僅顯示此語意。

#### TC-ERR-AUTH-010 無效／變造／過期 Email token
- **類型與優先級**：Error／P0；**測試層級**：API、UI；**狀態**：Ready（明確過期時間仍有 GAP-002）
- **對應需求**：AUTH；Email 驗證 Flowchart
- **前置條件**：準備亂碼、其他帳號 token 與已過期 token。
- **測試步驟**：逐一呼叫 confirm。
- **預期結果**：400 `invalid_email_token`，顯示不洩漏細節的失效訊息，帳號維持未驗證並提供重寄路徑。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-AUTH-011 重寄驗證信不洩漏帳號存在性
- **類型與優先級**：Security／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：AUTH；API resend contract
- **前置條件**：準備未驗證啟用、已驗證、停用與不存在帳號。
- **測試步驟**：對四類輸入呼叫 resend。
- **預期結果**：對外均回 200 true 與相同 UI 訊息；只有未驗證且啟用帳號實際新增寄信紀錄。
- **資料後置狀態**：符合條件者新增 EmailMessages，其餘不變。
- **現有自動化覆蓋**：無。

#### TC-F-AUTH-012 Refresh rotation 與舊 token family reuse
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL；**狀態**：Ready
- **對應需求**：API Refresh Token contract
- **前置條件**：已登入並取得有效 refresh cookie。
- **測試步驟**：1. refresh 一次。2. 驗證舊 token 被取代。3. 重用舊 token。4. 再用新 token。
- **預期結果**：第一次成功並輪替；重用舊 token 回 401 `refresh_token_reuse` 且撤銷整個 family；新 token 也不可再用。
- **資料後置狀態**：family 所有 token 均撤銷。
- **現有自動化覆蓋**：部分：`DomainEntityTests` 只測 entity revoke；`mockServices.spec.ts` 測前端 single-flight。

#### TC-ST-AUTH-013 Logout 撤銷 token 並清 Cookie
- **類型與優先級**：State／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：AUTH；API logout contract
- **前置條件**：已登入。
- **測試步驟**：呼叫 logout，檢查 Set-Cookie／DB，再 refresh 與開受保護頁。
- **預期結果**：204；目前 refresh token 撤銷且 cookie 清除；refresh 失敗；UI 回登入頁。
- **資料後置狀態**：session 結束，業務資料不變。
- **現有自動化覆蓋**：無。

#### TC-F-AUTH-014 Session restore 與同時 401 single-flight
- **類型與優先級**：Functional／P0；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：US-3；Frontend contract
- **前置條件**：refresh cookie 有效，記憶體 access token 已清除。
- **測試步驟**：重新整理；同時觸發多個需授權 request；觀察 network。
- **預期結果**：只送一次 refresh；取得新 access token 後各原 request 最多重送一次；不形成 loop。
- **資料後置狀態**：保持登入並完成 token rotation。
- **現有自動化覆蓋**：完整（部分層級）：`mockServices.spec.ts` 三案例、`app.spec.ts` refresh E2E。

### 4.2 授權、角色、使用者與偏好

#### TC-F-USER-001 使用者清單搜尋、角色篩選與分頁
- **類型與優先級**：Functional／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：FLOW-USER；API Users
- **前置條件**：Admin；多角色、多頁使用者資料。
- **測試步驟**：依帳號、姓名、Email 模糊搜尋；依四種角色篩選；切換頁次。
- **預期結果**：只回符合資料，按帳號排序；page<1 校正 1，pageSize 限制 1–100；空結果顯示空狀態。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-USER-002 未具 accounts.read 禁止讀取他人資料
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：FLOW-USER；API authorization
- **前置條件**：一般 User 與 Viewer。
- **測試步驟**：呼叫 users list、他人 detail 與本人 detail，並直接輸入 `/users` route。
- **預期結果**：list／他人 detail 為 403；本人 detail 可讀；UI 不顯示入口，直接 route 導 forbidden。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`router.spec.ts` 僅測未登入 redirect。

#### TC-ST-USER-003 Admin 原子更新角色與啟用狀態
- **類型與優先級**：State／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-USER；`PUT /users/{id}/administration`
- **前置條件**：Admin、已驗證目標帳號、目標有有效 refresh tokens。
- **測試步驟**：同一 request 變更 role 與 isEnabled；檢查 AccountRoles、TokenVersion、RefreshTokens、AuditLogs。
- **預期結果**：單一交易全成或全敗；角色以取代方式更新；TokenVersion 只加 1；全部 refresh token 撤銷；稽核含操作者及前後值。
- **資料後置狀態**：目標帳號只有一個系統角色且 session 失效。
- **現有自動化覆蓋**：無。

#### TC-ERR-USER-004 未驗證帳號不得提升角色
- **類型與優先級**：Security／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：AUTH 4；FLOW-USER
- **前置條件**：Admin；未驗證 Viewer。
- **測試步驟**：分別要求改為 User、Administrator、Admin；另測保持 Viewer。
- **預期結果**：前三者 422 `email_not_confirmed`；角色、狀態、token version 均不變；Viewer request 可依指定狀態規則處理。
- **資料後置狀態**：不產生非法角色。
- **現有自動化覆蓋**：無。

#### TC-ERR-USER-005 保護最後一位有效 Admin
- **類型與優先級**：Concurrency／P0；**測試層級**：Service、API、SQL；**狀態**：Ready
- **對應需求**：FLOW-USER
- **前置條件**：系統只有一位有效且非 bootstrap 的 Admin。
- **測試步驟**：嘗試降級、停用；再以兩個並行 request 分別移除兩位 Admin。
- **預期結果**：最後一位異動回 409 `last_admin`；Serializable transaction 防止並行同時通過；至少保留一位有效 Admin。
- **資料後置狀態**：系統仍有有效 Admin。
- **現有自動化覆蓋**：無。

#### TC-ERR-USER-006 Bootstrap Admin 不可修改或加入專案
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：Backend current contract
- **前置條件**：已設定 BootstrapAdmin account。
- **測試步驟**：在清單與直接 API 嘗試改角色／狀態；搜尋 member candidates 並直接加入專案。
- **預期結果**：UI 不提供編輯；API 409 `bootstrap_admin_immutable`；候選清單排除；直接加入 422 `bootstrap_admin_not_project_member`。
- **資料後置狀態**：bootstrap Admin 維持啟用 Admin，非專案成員。
- **現有自動化覆蓋**：部分：`BootstrapAdminPolicyTests`、`bootstrapAdminProtection.spec.ts`。

#### TC-F-USER-007 分離的角色與狀態 API 保持相同不變條件
- **類型與優先級**：Contract／P1；**測試層級**：API、SQL；**狀態**：Ready
- **對應需求**：FLOW-USER；`PUT /role`、`PATCH /status`
- **前置條件**：Admin；一般已驗證帳號與有效 refresh token。
- **測試步驟**：分別只換角色、只改啟用狀態；重複測未驗證提升、最後一位 Admin、bootstrap Admin。
- **預期結果**：成功時只改指定面向並各自撤銷 tokens、遞增 TokenVersion、寫 audit；三項保護規則與整合 administration API 一致。
- **資料後置狀態**：每次成功後仍只有一個系統角色；失敗時完全不變。
- **現有自動化覆蓋**：無。

#### TC-E-USER-008 現行版本不提供個資編輯
- **類型與優先級**：Negative contract／P2；**測試層級**：UI、API；**狀態**：Ready
- **對應需求**：User Story「畫面與查詢契約」；CON-009
- **前置條件**：一般登入使用者與 Admin。
- **測試步驟**：1. 開啟 `/settings`。2. 開啟 `/users/{id}`。3. 檢查可用 API 與畫面操作。
- **預期結果**：Settings 只提供語言與批次確認偏好；User Detail 只讀顯示帳號、名稱、Email 與驗證狀態，Admin 只可修改系統角色與啟用狀態；不存在 Account、Name、Email 編輯 request。
- **資料後置狀態**：個資不變；只有使用者明確儲存時才異動偏好、系統角色或啟用狀態。
- **現有自動化覆蓋**：無。

#### TC-F-PREF-001 讀寫個人批次確認偏好
- **類型與優先級**：Functional／P1；**測試層級**：API、SQL、UI、E2E；**狀態**：Ready
- **對應需求**：US-2；PREF
- **前置條件**：兩個已登入帳號。
- **測試步驟**：A 設為 true、B 設為 false；重新登入；A 執行批次更新；再由設定頁將 A 改回 false。
- **預期結果**：偏好按帳號隔離並持久化；true 略過確認，false 顯示確認；重開後仍一致。
- **資料後置狀態**：各帳號各一筆偏好。
- **現有自動化覆蓋**：無。

#### TC-ERR-PREF-002 Viewer 只能讀偏好不能寫
- **類型與優先級**：Security／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：Viewer 只讀規則；seed functions
- **前置條件**：Viewer。
- **測試步驟**：GET 與 PUT `/users/me/preferences`。
- **預期結果**：GET 200；PUT 403；UI 若顯示可儲存控制即屬實作缺陷。
- **資料後置狀態**：偏好不變。
- **現有自動化覆蓋**：無。

### 4.3 Project 與成員

#### TC-F-PRJ-001 僅列出可存取的 Project
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：總體資料範圍；FLOW-PRJ
- **前置條件**：一般成員屬於 Project A、不屬於 B；Admin／Administrator。
- **測試步驟**：各角色呼叫 project list、A detail、B detail。
- **預期結果**：一般成員只見 A；B detail 403；全域管理者可見全部未刪除 Project。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-PRJ-002 Project 搜尋、狀態篩選與分頁
- **類型與優先級**：Functional／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：現行 Project API；CON-012
- **前置條件**：多筆不同 code/name/description/status 的專案。
- **測試步驟**：使用單一 search 分別命中三欄，搭配 status 與分頁。
- **預期結果**：依 CreatedAt 降冪；totalCount 正確；無結果顯示空狀態；不宣稱支援 Owner filter。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-PRJ-003 建立 Project 與自動 Owner membership
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、E2E；**狀態**：Ready
- **對應需求**：FLOW-PRJ；API Project contract
- **前置條件**：具 projects.create；有效啟用 Owner。
- **測試步驟**：建立 Project，檢查 response、Projects、ProjectMembers、ProjectMemberRoles、AuditLogs。
- **預期結果**：201；狀態 Pending、versionNumber=1；產生 `PRJ-YYYYMMDD######`；Owner 自動成為 member 且具 ProjectManager；建立稽核。
- **資料後置狀態**：Project 與 Owner 關聯完整。
- **現有自動化覆蓋**：部分：`app.spec.ts` 測 Admin 建立與 code 格式；編號另有 SQL tests。

#### TC-ERR-PRJ-004 無權建立與無效 Owner
- **類型與優先級**：Security／P0；**測試層級**：API、SQL；**狀態**：Ready
- **對應需求**：FLOW-PRJ
- **前置條件**：Viewer／User；不存在或停用 Owner。
- **測試步驟**：無權角色建立；有權角色以各種無效 Owner 建立。
- **預期結果**：無權 403；無效 Owner 422 `invalid_owner`；不消耗已 rollback 的業務編號，不產生孤兒資料。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`SqlServerConstraintTests` 測編號 rollback，不測 Project service。

#### TC-E-PRJ-005 Project 欄位邊界
- **類型與優先級**：Edge／P1；**測試層級**：API、SQL、UI；**狀態**：Planned（CON-007）
- **對應需求**：FLOW-PRJ；DB
- **前置條件**：Frontend 完成對齊正式輸入契約。
- **測試步驟**：測名稱 trim 後 0/1/2/120/121/200/201 字及 description 空值/4000/4001 字。
- **預期結果**：名稱 1–200 字通過，0 或 201 字拒絕；description 空值或最多 4000 字通過，4001 字拒絕；前後端界線一致且回欄位錯誤而非 DB 500。
- **資料後置狀態**：拒絕值不建立／更新。
- **現有自動化覆蓋**：無；Frontend 現況仍為名稱 2–120 字且 Description 必填。

#### TC-ST-PRJ-006 修改 Project 並增加版本
- **類型與優先級**：State／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-PRJ；optimistic concurrency
- **前置條件**：可管理 Project，持有最新 rowVersion。
- **測試步驟**：更新名稱、說明、Owner、status；重新讀取。
- **預期結果**：200；基本資料更新；VersionNumber 加 1；回傳新 rowVersion；稽核含前後資料；成員／Task 異動不增加 VersionNumber。
- **資料後置狀態**：保存新資料與版本。
- **現有自動化覆蓋**：部分：`DomainEntityTests`、`DatabaseModelTests` 只測 VersionNumber。

#### TC-ERR-PRJ-007 Project rowVersion 衝突
- **類型與優先級**：Concurrency／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-PRJ
- **前置條件**：兩個 client 取得相同 rowVersion。
- **測試步驟**：A 成功更新；B 以舊 rowVersion 更新。
- **預期結果**：B 回 409 `concurrency_conflict`；UI 保留輸入並要求重新載入；A 資料不被覆蓋。
- **資料後置狀態**：只保留 A 更新。
- **現有自動化覆蓋**：無。

#### TC-F-MEMBER-001 成員候選人搜尋與最小揭露
- **類型與優先級**：Security／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER；API member-candidates
- **前置條件**：ProjectManager；已有、停用、bootstrap 與一般帳號。
- **測試步驟**：依 account/name 搜尋並分頁。
- **預期結果**：排除既有成員、停用帳號與 bootstrap Admin；只回 id/account/name；未授權者 403。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：`ApiSurfaceTests` 只確認 endpoint 出現在 OpenAPI。

#### TC-F-MEMBER-002 加入一名多角色成員
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER；CON-004
- **前置條件**：可管理 Project；啟用且尚非成員帳號；兩個有效 Project Role IDs。
- **測試步驟**：用複選 UI 加入；重讀成員與 DB。
- **預期結果**：一筆 ProjectMembers、兩筆 ProjectMemberRoles；UI 顯示兩角色；寫入稽核。
- **資料後置狀態**：成員具指定角色集合。
- **現有自動化覆蓋**：部分：`multiSelectDropdown.spec.ts`、`projectDetailView.spec.ts` 只測 UI 複選。

#### TC-ERR-MEMBER-003 重複成員與重複角色
- **類型與優先級**：Error／P0；**測試層級**：API、SQL；**狀態**：Ready
- **對應需求**：FLOW-MEMBER；DB
- **前置條件**：帳號已是成員。
- **測試步驟**：再次加入；request 內重複 roleId；繞過 API 插入相同 membership／role mapping。
- **預期結果**：重複加入 409 `duplicate_member`；request 內角色去重；DB 複合 PK 拒絕重複資料。
- **資料後置狀態**：只保留一 membership 與每角色一 mapping。
- **現有自動化覆蓋**：部分：`DatabaseModelTests` 只檢查複合 PK metadata。

#### TC-ERR-MEMBER-004 空或無效 Project Role 集合
- **類型與優先級**：Error／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER
- **前置條件**：可管理 Project。
- **測試步驟**：新增／更新時送空陣列、未知 roleId、混合有效與無效 IDs；在 UI 嘗試取消最後一個角色。
- **預期結果**：API 422 `invalid_project_roles`；UI 不允許取消最後一個角色；原集合不變。
- **資料後置狀態**：不產生無角色成員。
- **現有自動化覆蓋**：部分：`multiSelectDropdown.spec.ts` 測 UI 最後一個角色。

#### TC-ST-MEMBER-005 更新角色採完整取代
- **類型與優先級**：State／P1；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER；Frontend contract
- **前置條件**：成員現有 A、B 角色。
- **測試步驟**：PUT 只送 B、C；重讀。
- **預期結果**：A 被移除、B 保留、C 新增；不是增量追加；稽核含前後角色集合。
- **資料後置狀態**：角色恰為 B、C。
- **現有自動化覆蓋**：部分：`projectDetailView.spec.ts` 驗證 request 參數，不驗 DB。

#### TC-ERR-MEMBER-006 Owner 移除與角色保護
- **類型與優先級**：State／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER
- **前置條件**：Project Owner 是成員。
- **測試步驟**：嘗試直接移除 Owner；先移交 Owner；檢查新 Owner ProjectManager；再移除舊 Owner。
- **預期結果**：直接移除回 409 `owner_transfer_required`；移交在交易內補新 Owner 的 ProjectManager；之後舊 Owner 若無未完成 Task 可移除。
- **資料後置狀態**：任何時點 Owner 都是成員且具 ProjectManager。
- **現有自動化覆蓋**：無。

#### TC-ERR-MEMBER-007 有未完成 Task 的成員不可移除
- **類型與優先級**：State／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER
- **前置條件**：非 Owner 成員有 Pending／InProgress／Blocked Task。
- **測試步驟**：逐狀態嘗試移除；將全部 Task 完成或重新指派後再移除。
- **預期結果**：未完成時 409 `task_reassignment_required`；全部處理後 204；刪 membership 與 role mappings並保留稽核。
- **資料後置狀態**：Task 不會指向已移除的未完成責任人。
- **現有自動化覆蓋**：無。

### 4.4 Task 清單、詳情與異動

#### TC-F-TASK-001 Task 清單欄位與預設排序
- **類型與優先級**：Functional／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-1
- **前置條件**：所屬 Project 有多筆不同 CreatedAt 的 Task。
- **測試步驟**：進入 `/projects/{id}/task-items`。
- **預期結果**：顯示 checkbox、code、title、deadline、status、creator、assignee；依 createdAt 新到舊；僅含該 Project 未軟刪除資料。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-002 搜尋、篩選、mineOnly 與分頁
- **類型與優先級**：Functional／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-1
- **前置條件**：多狀態、多指派者、多頁 Task。
- **測試步驟**：依 code/title/description 搜尋；搭配 status、assignee、onlyMine；切換 page。
- **預期結果**：交集結果正確；totalCount 正確；無資料顯示空狀態；page/pageSize 邊界依 contract 正規化。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ST-TASK-003 Query string 與返回清單狀態
- **類型與優先級**：State／P1；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：US-1、US-4
- **前置條件**：Task 清單可存取。
- **測試步驟**：設定搜尋／狀態／指派者／mineOnly／排序／頁次；開詳情；按返回；重新整理。
- **預期結果**：條件存在 URL query；返回及 reload 保留條件並載入相同範圍。
- **資料後置狀態**：後端不變；瀏覽器 URL 保留條件。
- **現有自動化覆蓋**：無。

#### TC-E-TASK-004 清單排序允許值與非法值
- **類型與優先級**：Edge／P2；**測試層級**：API；**狀態**：Ready
- **對應需求**：US-1；API contract
- **前置條件**：可區分 deadline/status/code/createdAt 排序的資料。
- **測試步驟**：對四個 sortBy 測 asc/desc；再送未知 sortBy、未知 direction。
- **預期結果**：合法值排序正確；依目前實作未知 sortBy fallback createdAt、非 asc fallback desc，且不形成 SQL injection。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-TASK-005 跨 Project 與無 membership 存取
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-1、US-4
- **前置條件**：Task 屬於 A；一般使用者只屬於 A 或只屬於 B。
- **測試步驟**：以 A taskId 搭配 B route projectId；非成員直接讀 list/detail/comments。
- **預期結果**：跨 route 的 Task 不得回傳；非成員 403；具 A 權限但錯 route 應 404。不存在與無權優先序見 GAP-008。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-006 checkbox 權限、全選與暫存性
- **類型與優先級**：Functional／P0；**測試層級**：UI；**狀態**：Ready
- **對應需求**：US-2、US-3
- **前置條件**：目前頁混合本人可編輯與不可編輯 Task；另以 Viewer 登入。
- **測試步驟**：勾單列、表頭全選、切頁、完成批次、reload。
- **預期結果**：無權列 disabled；Viewer 全 disabled；全選只選本頁可編輯列；批次成功與 reload 後清空；checkbox 不送 DB。
- **資料後置狀態**：只可能變更批次目標 Task status，不保存選取狀態。
- **現有自動化覆蓋**：無。

#### TC-E-TASK-007 未選 Task 時禁止確認
- **類型與優先級**：Edge／P1；**測試層級**：UI；**狀態**：Ready
- **對應需求**：US-2
- **前置條件**：Task 清單含至少一筆可修改 Task。
- **測試步驟**：1. 進入頁面且不選 Task。2. 確認目標狀態預設為 `InProgress`。3. 選取一筆 Task。4. 清除選取。
- **預期結果**：未選 Task 時確認鈕 disabled 且不得送 API；選取 Task 後可用預設 `InProgress` 送出；清除選取後再次 disabled。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-008 新增 Task 成功
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、UI、E2E；**狀態**：Ready
- **對應需求**：US-6
- **前置條件**：Admin／Administrator；有效 Project member 作 assignee。
- **測試步驟**：由 `/admin/projects/{id}/task-items/new` 送出合法資料；檢查 DB 與導頁。
- **預期結果**：201；產生 `TASK-YYYYMMDD######`；狀態固定 Pending；建立 history/audit；UI 顯示成功並進詳情。
- **資料後置狀態**：新增 Task、history、audit。
- **現有自動化覆蓋**：部分：`app.spec.ts` 測 Admin 建立與 code；無 DB history 驗證。

#### TC-ERR-TASK-009 新增 Task 驗證
- **類型與優先級**：Error／P0；**測試層級**：API、UI、SQL；**狀態**：Ready
- **對應需求**：US-6
- **前置條件**：可建立 Task。
- **測試步驟**：測空標題、301 字標題、不存在／其他 Project assignee、startAt>deadline；另 API 送空 description。
- **預期結果**：非法資料回 400/422 對應 code；依正式契約，空 description 可接受，有值時 trim 後最多 8000 字；失敗不產生 Task/history/audit 或消耗編號。
- **資料後置狀態**：失敗個案不變。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-010 後台完整修改 Task
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：US-7
- **前置條件**：具 tasks.update-any；最新 rowVersion。
- **測試步驟**：修改 title/description/start/deadline/assignee/status。
- **預期結果**：200 與新 rowVersion；所有欄位更新；寫 history/audit；前端顯示最新資料。
- **資料後置狀態**：保存新資料及追蹤紀錄。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-011 被指派者只修改 status 與 deadline
- **類型與優先級**：Security／P0；**測試層級**：API、UI、SQL；**狀態**：Ready
- **對應需求**：US-2、US-4
- **前置條件**：User 是 Task assignee。
- **測試步驟**：使用 PATCH 改 status/deadline；再嘗試完整 PUT 或竄改 title/assignee/startAt。
- **預期結果**：PATCH 只更新兩欄；完整 PUT 403；其他欄保持；history/audit action=UpdateAssigned。
- **資料後置狀態**：只變更允許欄位。
- **現有自動化覆蓋**：無。

#### TC-ERR-TASK-012 非指派者與 Viewer 不可修改
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-2、US-4；Viewer 規則
- **前置條件**：同 Project 非 assignee User；Viewer。
- **測試步驟**：直接呼叫單筆 PATCH、batch PATCH、PUT、POST、DELETE。
- **預期結果**：全部寫入 403；UI 不顯示或 disabled 對應控制；資料無異動。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ST-TASK-013 四種 Task status 任意互轉
- **類型與優先級**：State／P1；**測試層級**：Unit、API；**狀態**：Ready（依現行 contract；見 GAP-005）
- **對應需求**：US-2；Backend contract
- **前置條件**：有權修改 Task。
- **測試步驟**：以資料驅動覆蓋 Pending/InProgress/Blocked/Completed 的 16 組 source→target。
- **預期結果**：目前契約下皆可成功，包括同狀態更新；若產品建立限制矩陣，此案例需改版。
- **資料後置狀態**：每次為指定目標狀態並產生追蹤紀錄。
- **現有自動化覆蓋**：部分：`DomainEntityTests` 僅從 Pending 測四個 target。

#### TC-ERR-TASK-014 單筆修改 rowVersion 衝突
- **類型與優先級**：Concurrency／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：US-7
- **前置條件**：兩個 client 持有同版 Task。
- **測試步驟**：A 更新；B 以舊 rowVersion 完整更新、指派者更新或刪除。
- **預期結果**：B 409 `concurrency_conflict`；UI 保留輸入並提示 reload；A 結果不被覆蓋。
- **資料後置狀態**：只有 A 異動。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-015 批次狀態更新成功
- **類型與優先級**：Functional／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：US-2；批次 Flowchart
- **前置條件**：選取多筆皆有權且 rowVersion 最新。
- **測試步驟**：確認視窗檢查筆數／目標；送 batch-status；查詢 Task、history、audit；重載 UI。
- **預期結果**：200 `updatedCount=X`；同一 transaction 全部改為目標狀態；每筆有 history/audit；清除選取並顯示成功筆數。
- **資料後置狀態**：所有選取 Task 一致更新。
- **現有自動化覆蓋**：無。

#### TC-ERR-TASK-016 批次資料任一筆失敗全部 rollback
- **類型與優先級**：Transaction／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：US-2；批次 Flowchart
- **前置條件**：混入無權、跨 Project、不存在或 stale rowVersion 任一筆。
- **測試步驟**：對每類錯誤各送一批；失敗後查全部 Task/history/audit。
- **預期結果**：對應 403/404/409；沒有任何 Task 更新，也不留下該批 history/audit；UI 保留原畫面與選取並顯示原因。
- **資料後置狀態**：整批不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-TASK-017 空批次與重複 Task ID
- **類型與優先級**：Error／P1；**測試層級**：API；**狀態**：Ready
- **對應需求**：US-2；API contract
- **前置條件**：已登入。
- **測試步驟**：送空 tasks；同一 taskId 兩次（相同或不同 rowVersion）。
- **預期結果**：400 `validation_error` 或 `duplicate_task`；不更新任何資料。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ST-TASK-018 批次確認取消與偏好略過
- **類型與優先級**：State／P1；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：US-2；PREF
- **前置條件**：已選多筆；偏好分別 false/true。
- **測試步驟**：false 時取消再確認；true 時直接送出。
- **預期結果**：取消不呼叫 API且不改資料；確認才送；true 不開視窗但仍只更新選取資料。
- **資料後置狀態**：取消時不變；成功時依批次結果更新。
- **現有自動化覆蓋**：無。

#### TC-F-TASK-019 軟刪除 Task 並保留關聯
- **類型與優先級**：Data integrity／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：US-8；刪除 Flowchart
- **前置條件**：具 tasks.delete；Task 有留言與歷史；最新 rowVersion。
- **測試步驟**：開刪除確認，確認後 DELETE；查一般 API 與 IgnoreQueryFilters 的 DB 資料。
- **預期結果**：204；一般清單／詳情不顯示；Task DeletedAt 有值；留言、既有／新增刪除 history 與 audit 保留；沒有 cascade delete。
- **資料後置狀態**：Task 軟刪除，關聯紀錄可稽核。
- **現有自動化覆蓋**：無。

#### TC-ST-TASK-020 刪除確認取消與失敗保留畫面
- **類型與優先級**：State／P1；**測試層級**：UI；**狀態**：Ready
- **對應需求**：US-8
- **前置條件**：後台清單有 Task。
- **測試步驟**：點刪除並核對標題／說明；先取消；再模擬 403/409/5xx。
- **預期結果**：確認文含 Task 標題與軟刪除影響；取消不送 request；失敗保留畫面並顯示錯誤；成功才回清單與提示。
- **資料後置狀態**：取消／失敗不變。
- **現有自動化覆蓋**：無。

### 4.5 Task 留言

#### TC-F-CMT-001 讀取留言串
- **類型與優先級**：Functional／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-4；留言 Flowchart
- **前置條件**：可讀 Task；多筆留言含已軟刪除資料。
- **測試步驟**：讀取 comments。
- **預期結果**：只回未刪除留言，依 CreatedAt 升冪；顯示作者、內容、時間；Viewer 可讀。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-F-CMT-002 新增 1–2000 字留言
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：US-4；留言 Flowchart
- **前置條件**：有 comments.create 且可讀 Task。
- **測試步驟**：分別送 1 字、2000 字與含前後空白／換行內容。
- **預期結果**：200；內容 trim 後保存、換行保留；作者取目前 token 而非 request；寫 audit；UI 重新載入留言串。
- **資料後置狀態**：新增留言與 audit。
- **現有自動化覆蓋**：無。

#### TC-ERR-CMT-003 空白與 2001 字留言
- **類型與優先級**：Edge／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-4；留言 Flowchart
- **前置條件**：可留言。
- **測試步驟**：送空字串、全空白、2001 字；編輯也重複測試。
- **預期結果**：400 `validation_error`；UI 保留內容並顯示錯誤；DB 不變。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ST-CMT-004 作者修改留言
- **類型與優先級**：State／P1；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：US-4；留言 Flowchart
- **前置條件**：作者持有最新 rowVersion。
- **測試步驟**：編輯自己的留言並重載。
- **預期結果**：200、新 rowVersion、UpdatedAt 更新；內容與 audit 前後值正確。
- **資料後置狀態**：保存新內容與稽核。
- **現有自動化覆蓋**：無。

#### TC-ERR-CMT-005 非作者或 Viewer 不可修改／刪除
- **類型與優先級**：Security／P0；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：US-4；Viewer 規則
- **前置條件**：同 Project 非作者、Viewer。
- **測試步驟**：直接 PUT/DELETE 他人留言；觀察 UI 控制。
- **預期結果**：403；非作者不顯示編輯／刪除；Viewer 不顯示新增；內容不變。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-CMT-006 留言 rowVersion 衝突
- **類型與優先級**：Concurrency／P1；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：留言 Flowchart；API contract
- **前置條件**：兩 client 取得同一留言版本。
- **測試步驟**：A 修改；B 用舊版修改與刪除。
- **預期結果**：B 409 `concurrency_conflict`；保留 B 未送出內容並提示重新載入；A 資料不被覆蓋。
- **資料後置狀態**：只保留 A 異動。
- **現有自動化覆蓋**：無。

#### TC-ST-CMT-007 軟刪除自己的留言
- **類型與優先級**：State／P1；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：留言 Flowchart
- **前置條件**：作者、最新 rowVersion。
- **測試步驟**：取消一次刪除；再確認；讀留言與 DB。
- **預期結果**：取消不送 request；確認 204；一般留言串不再顯示；DB DeletedAt 與 audit 保留。
- **資料後置狀態**：留言軟刪除。
- **現有自動化覆蓋**：無。

#### TC-ERR-CMT-008 跨 Task／Project comment ID
- **類型與優先級**：Security／P0；**測試層級**：API；**狀態**：Ready
- **對應需求**：US-4；API resource scope
- **前置條件**：留言屬 A Project/A Task。
- **測試步驟**：用 B Project 或 B Task route 讀／改／刪該留言。
- **預期結果**：不得洩漏或異動留言；依已授權 route scope 回 403 或 404，具體優先序見 GAP-008。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

### 4.6 Task 到期提醒（全部 Planned）

#### TC-ST-REM-001 七日提醒視窗
- **類型與優先級**：State／P0；**測試層級**：Unit、Service、SQL；**狀態**：Planned
- **對應需求**：US-5；Email 到期提醒 Flowchart
- **前置條件**：固定系統時區與 now；未完成 Task。
- **測試步驟**：資料驅動測 deadline 相對今天 -4 至 +4 天（到期前以正向天數表示）。
- **預期結果**：只在到期前 3/2/1 天、當天、逾期 1/2/3 天建立每日提醒；其餘不建立。
- **資料後置狀態**：每個有效日期一筆 Pending reminder。
- **現有自動化覆蓋**：無；功能尚未實作。

#### TC-ERR-REM-002 Completed Task 不提醒
- **類型與優先級**：Error／P0；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5
- **前置條件**：期限在視窗內，status=Completed。
- **測試步驟**：執行掃描；另在 Pending 建立後、寄送前把 Task 完成。
- **預期結果**：掃描不建立；寄送前重查時標記 Cancelled，不呼叫 Email provider。
- **資料後置狀態**：無 reminder 或既有 reminder=Cancelled。
- **現有自動化覆蓋**：無。

#### TC-ERR-REM-003 收件人停用或未驗證
- **類型與優先級**：Security／P0；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5
- **前置條件**：期限在視窗內；收件人分別停用／未驗證。
- **測試步驟**：掃描；若掃描後才變更狀態，再執行寄送 worker。
- **預期結果**：掃描記錄略過或寄送前 Cancelled；不寄信。
- **資料後置狀態**：可追蹤略過／取消原因。
- **現有自動化覆蓋**：無。

#### TC-ERR-REM-004 排程重複與多 worker 去重
- **類型與優先級**：Concurrency／P0；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5；提醒 Flowchart
- **前置條件**：同 Task、recipient、reminderDate；兩 scheduler／worker。
- **測試步驟**：並行掃描及並行 claim/send。
- **預期結果**：唯一限制只建立一筆；只有一個 worker 取得寄送權；最多一次 provider 呼叫。
- **資料後置狀態**：單一 reminder，狀態一致。
- **現有自動化覆蓋**：無。

#### TC-F-REM-005 寄送成功判定
- **類型與優先級**：Functional／P0；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5
- **前置條件**：Pending reminder；provider 回成功與 response ID。
- **測試步驟**：worker claim、重查、組信、寄送、寫回。
- **預期結果**：信件含期限與 Task link；只有 provider 成功且 SentAt/response ID 寫入成功才標 Sent。
- **資料後置狀態**：Sent、SentAt、response ID 完整。
- **現有自動化覆蓋**：無。

#### TC-ST-REM-006 初次失敗後最多重試三次
- **類型與優先級**：State／P0；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5
- **前置條件**：provider 持續失敗。
- **測試步驟**：執行初次寄送與三次 retry，再觸發一次。
- **預期結果**：總嘗試最多 4 次；前三次失敗安排有限重試；第 4 次後 Failed、告警；不再排程。
- **資料後置狀態**：Failed、retryCount=3、保留錯誤與告警。
- **現有自動化覆蓋**：無。

#### TC-ST-REM-007 重試後成功
- **類型與優先級**：State／P1；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5
- **前置條件**：初次失敗，第二次 provider 成功。
- **測試步驟**：初次寄送、排 retry、執行 retry。
- **預期結果**：最終 Sent；retryCount 正確；不再重試；錯誤歷程可追蹤。
- **資料後置狀態**：Sent 與 provider response ID。
- **現有自動化覆蓋**：無。

#### TC-ERR-REM-008 Provider 接受但成功紀錄寫回失敗
- **類型與優先級**：Failure／P1；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：提醒 Flowchart 的 at-least-once 風險
- **前置條件**：provider 已接受；DB 寫回失敗。
- **測試步驟**：模擬成功 response 後 DB 例外，再重試。
- **預期結果**：記錄失敗／可重試；若 provider 支援 idempotency key，以 reminder ID 防重；否則明確記錄極少數重複風險。
- **資料後置狀態**：不得錯誤標 Sent；具可診斷狀態。
- **現有自動化覆蓋**：無。

#### TC-ST-REM-009 每日掃描摘要與取消
- **類型與優先級**：Operational／P2；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：ImplementationBacklog BE-001
- **前置條件**：混合成功建立、重複、略過、無符合資料。
- **測試步驟**：執行掃描，檢查摘要與 cancellation。
- **預期結果**：摘要數量與原因正確；CancellationToken 中止後不繼續建立／寄送，已提交資料保持一致。
- **資料後置狀態**：只有中止前已完成的原子操作存在。
- **現有自動化覆蓋**：無。

### 4.7 SQL、API 共通與平台

#### TC-SQL-001 單一系統角色 constraint
- **類型與優先級**：Data integrity／P0；**測試層級**：SQL；**狀態**：Ready
- **對應需求**：AUTH、FLOW-USER、DB
- **前置條件**：實際 SQL Server migration 已套用。
- **測試步驟**：同 UserId 插入第二個不同 RoleId。
- **預期結果**：UNIQUE constraint 拒絕；帳號最多一個角色。
- **資料後置狀態**：僅一筆 AccountRoles。
- **現有自動化覆蓋**：完整：`DatabaseModelTests` metadata + `SqlServerConstraintTests` 實際 SQL（需環境變數）。

#### TC-SQL-002 業務編號格式、日切、隔離、並行與 rollback
- **類型與優先級**：Concurrency／P0；**測試層級**：Unit、SQL；**狀態**：Ready
- **對應需求**：API、DB
- **前置條件**：實際 SQL Server；固定 UTC 時間。
- **測試步驟**：測 Project/Task 各自序號、跨 UTC 日、10 個並行 request、transaction rollback、999999 上限。
- **預期結果**：格式與序號正確、不重複、不跨類型互相影響；rollback 不耗號；上限回 null／API 409 `daily_code_limit_exceeded`。
- **資料後置狀態**：counter 僅反映已提交建立。
- **現有自動化覆蓋**：完整：`DomainEntityTests`、`SqlServerConstraintTests` 五類案例。

#### TC-SQL-003 軟刪除 query filters
- **類型與優先級**：Data integrity／P0；**測試層級**：SQL、API；**狀態**：Ready
- **對應需求**：US-8、DB
- **前置條件**：Projects、TaskItems、TaskItemComments 各有 DeletedAt/null 資料。
- **測試步驟**：一般 EF/API 查詢與 IgnoreQueryFilters 查詢。
- **預期結果**：一般查詢排除軟刪除；稽核查詢仍能取得；歷史與關聯未 cascade 消失。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-SQL-004 FK 與刪除行為
- **類型與優先級**：Data integrity／P1；**測試層級**：SQL；**狀態**：Ready
- **對應需求**：DB
- **前置條件**：完整關聯資料。
- **測試步驟**：嘗試刪除被 Project/Task/history/comment/audit 參照的 Account、Project、Task；另刪除 membership。
- **預期結果**：Restrict/NoAction 防止遺失歷史；刪 membership 僅 cascade 其 ProjectMemberRoles；Identity 支援資料依 migration 規則處理。
- **資料後置狀態**：失敗刪除不破壞參照完整性。
- **現有自動化覆蓋**：無。

#### TC-SQL-005 rowversion 自動更新與 Base64 round-trip
- **類型與優先級**：Concurrency／P0；**測試層級**：SQL、API；**狀態**：Ready
- **對應需求**：US-7、API、DB
- **前置條件**：Project、Task、Comment 各一筆。
- **測試步驟**：讀 Base64 rowVersion、成功更新、比較新舊值、原樣回傳新值再更新。
- **預期結果**：每次 DB 更新 rowversion 改變；API Base64 可 round-trip；空白／非法 Base64 視為 409 conflict，不造成 500。
- **資料後置狀態**：僅合法版本更新。
- **現有自動化覆蓋**：`ApiSurfaceTests` 只確認 schema 有 rowVersion。

#### TC-SQL-006 Audit 與 History 不相信 request 操作者
- **類型與優先級**：Security／P0；**測試層級**：Service、SQL；**狀態**：Ready
- **對應需求**：各異動 Flowchart、DB
- **前置條件**：登入 actor 與目標 account 不同。
- **測試步驟**：建立／修改／刪除 Project、Member、Task、Comment、User；檢查記錄。
- **預期結果**：ActorAccountId 來自 JWT current user；action/entity/time/必要前後快照正確；Task history actor 亦正確。
- **資料後置狀態**：每個成功異動有可追溯紀錄；失敗異動無成功稽核。
- **現有自動化覆蓋**：無。

#### TC-SQL-007 重複 Email DB constraint
- **類型與優先級**：Data integrity／P0；**測試層級**：SQL；**狀態**：Planned（GAP-010）
- **對應需求**：AUTH、DB
- **前置條件**：新增 NormalizedEmail UNIQUE migration 後。
- **測試步驟**：繞過 UserManager 並行插入相同 NormalizedEmail。
- **預期結果**：DB 拒絕第二筆且應用映射為可理解衝突，而不是 500。
- **資料後置狀態**：NormalizedEmail 唯一。
- **現有自動化覆蓋**：無。

#### TC-F-API-001 OpenAPI、enum、路由與 Problem Details
- **類型與優先級**：Contract／P0；**測試層級**：API；**狀態**：Ready
- **對應需求**：API
- **前置條件**：Testing／Development 開啟 OpenAPI。
- **測試步驟**：讀 `/openapi/v1.json` 與 `/swagger/v1/swagger.json`；對 400/401/403/404/409/422/500 代表案例取 response。
- **預期結果**：核心 routes 與 DTO/enum/rowVersion 一致；錯誤為 RFC 7807 且含 code/traceId，不含 stack、SQL、token。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`ApiSurfaceTests` 測 OpenAPI 核心 endpoint 與 DTO 欄位。

#### TC-F-API-002 固定角色、Project Role 與 Function mapping
- **類型與優先級**：Contract／P0；**測試層級**：API、SQL；**狀態**：Ready
- **對應需求**：StaticData、AUTH、API
- **前置條件**：migration seed 完成；四種角色帳號。
- **測試步驟**：GET `/roles`、GET `/projects/roles`、GET `/auth/me`；比對 seed 與每角色 functions。
- **預期結果**：系統角色恰為 Admin/Administrator/User/Viewer；Project Role 恰為五個固定 code；Admin 有全部 functions、Viewer 僅讀 Project/Task/Comment 與自己偏好，其他角色符合 seed。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-SEC-API-003 JWT 期限、claims 與 token-version 即時失效
- **類型與優先級**：Security／P0；**測試層級**：API、SQL；**狀態**：Ready
- **對應需求**：API authentication contract
- **前置條件**：可簽發有效 token；可控制時間與更新帳號 TokenVersion。
- **測試步驟**：解析 token 的 sub/jti/role/permission/token-version、驗簽與 15 分鐘期限；測過期、錯 issuer/audience/signature；異動角色／停用後重用舊 token。
- **預期結果**：合法 token 可用；所有無效 token 401；角色／狀態異動後舊 token 因版本不符立刻失效；未驗證帳號 token 只含 Viewer 能力。
- **資料後置狀態**：測試異動依個案保留，無未授權業務寫入。
- **現有自動化覆蓋**：部分：`HttpCurrentUserTests` 只測 claims 映射。

#### TC-F-API-004 Health、CORS 與 OpenAPI 環境邊界
- **類型與優先級**：Platform／P2；**測試層級**：API；**狀態**：Ready
- **對應需求**：API 平台端點、Backend configuration
- **前置條件**：Development、Testing、Production-like 三環境；允許與不允許 origin。
- **測試步驟**：GET `/health`；以不同 origin preflight；檢查各環境 `/openapi`、`/swagger`。
- **預期結果**：health 200 代表應用存活；只允許設定 origin 且 credentials policy 正確；OpenAPI 只在 Development/Testing 或明確開啟時暴露。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：`ApiSurfaceTests` 僅在 Testing 讀 OpenAPI；health/CORS 未覆蓋。

### 4.8 UI、導覽、錯誤與可用性

#### TC-F-UI-001 Route guard 與登入 redirect
- **類型與優先級**：Security UX／P0；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：AUTH、API
- **前置條件**：未登入；另有不同 functions 的帳號。
- **測試步驟**：直接開受保護 route；登入；直接開 users／create routes。
- **預期結果**：未登入導 sign-in 並保存完整 redirect；登入後回原 route；缺 requiredFunction 導 forbidden；Backend 仍獨立驗權。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`router.spec.ts` 測未登入 redirect。

#### TC-F-UI-002 Loading、empty、success 與 error 狀態
- **類型與優先級**：Functional UX／P1；**測試層級**：UI；**狀態**：Ready
- **對應需求**：US-1、US-2、各 Flowchart
- **前置條件**：可控制 pending、空 response、成功與失敗 response。
- **測試步驟**：對 Project/User/Task list 與 detail/form 逐一模擬四種狀態。
- **預期結果**：狀態互斥且訊息清楚；錯誤不顯示空狀態；提交中避免重送；成功顯示 toast／正確導頁。
- **資料後置狀態**：依成功與否一致。
- **現有自動化覆蓋**：極少；`components.spec.ts` 只測 StatusBadge。

#### TC-ERR-UI-003 400/401/403/404/409/422/5xx 與 timeout mapping
- **類型與優先級**：Error／P0；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：Frontend contract
- **前置條件**：可攔截或建立各狀態回應。
- **測試步驟**：逐狀態觸發 request；另測非 JSON error、網路中斷、15 秒 timeout、caller cancellation。
- **預期結果**：語意不混淆；401 只 refresh 一次；409 保留輸入；422 對應業務／欄位；5xx/timeout 可重試且不曝露內部資訊。
- **資料後置狀態**：失敗操作不出現假成功。
- **現有自動化覆蓋**：部分：`mockServices.spec.ts` 測 Problem Details、401 與網路 client 的部分路徑。

#### TC-F-UI-004 桌面與手機版導覽
- **類型與優先級**：Responsive／P1；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：UI 規格、Frontend AGENTS
- **前置條件**：1440×900 與 Pixel 7 viewport。
- **測試步驟**：檢查 Sidebar、project tree、mobile drawer、backdrop、表格橫向捲動與各表單/detail layout。
- **預期結果**：桌面 Sidebar 固定；<=900px 用 drawer；<=620px 表單單欄；主要控制可操作且內容不被遮擋。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`app.spec.ts` 測 mobile drawer 與 desktop 基本頁。

#### TC-F-UI-005 鍵盤、焦點、label 與語意
- **類型與優先級**：Accessibility／P1；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：Frontend AGENTS 可用性要求
- **前置條件**：桌面瀏覽器、只使用鍵盤。
- **測試步驟**：Tab 全流程；操作表單、checkbox、dialog、multi-select、mobile navigation；觸發錯誤與 toast。
- **預期結果**：可見 focus；label/aria-name 正確；錯誤具 alert、toast 具 status；顏色不是唯一狀態提示；Esc 可關閉 multi-select。
- **資料後置狀態**：依操作一致。
- **現有自動化覆蓋**：部分：`multiSelectDropdown.spec.ts` 檢查 ARIA 結構，未做完整鍵盤流程。

#### TC-F-UI-006 語言切換與持久化
- **類型與優先級**：State／P2；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：現行 UI 規格
- **前置條件**：可使用 localStorage。
- **測試步驟**：zh-TW 切 en、reload、登出登入；清除 localStorage。
- **預期結果**：語言保存於唯一允許的 localStorage key；reload 保留；清除後回 zh-TW；access token/refresh token 不出現在 storage。
- **資料後置狀態**：僅 locale preference 留在 localStorage。
- **現有自動化覆蓋**：部分：`app.spec.ts` 測切換與 reload。

#### TC-SEC-UI-007 使用者內容防 XSS
- **類型與優先級**：Security／P0；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：Frontend AGENTS 不信任輸入
- **前置條件**：Project/Task/Comment/name 包含 `<script>`、事件屬性與特殊字元。
- **測試步驟**：建立資料並在 list/detail/comment 顯示。
- **預期結果**：以文字顯示、不執行腳本、不注入 DOM attribute；API／log 不曝露機密。
- **資料後置狀態**：原始文字可安全保存與顯示。
- **現有自動化覆蓋**：無。

#### TC-F-UI-008 UI Mock 核心資訊對照
- **類型與優先級**：Visual contract／P2；**測試層級**：UI；**狀態**：Ready
- **對應需求**：八張 `UIMock/*.png` 與 `UIMock/README.md`
- **前置條件**：各角色與代表資料。
- **測試步驟**：逐頁核對 SignIn、SignUp、UserList、UserSetting、ProjectList、ProjectDetail、TaskItemList、TaskItemDetail 的核心資訊與返回操作。
- **預期結果**：User Story 所需資訊可見；PNG 舊控制與文字契約不同時，以 `UIMock/README.md`、User Story 與 Flowchart 為 pass/fail 依據。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：現有 component/E2E 測試只覆蓋少數頁面結構。

## 5. 覆蓋矩陣

| 需求 | 主要案例 | Happy path | Edge／Error | State／Concurrency | 狀態 |
|---|---|---:|---:|---:|---|
| AUTH | AUTH 系列 001–014 | ✓ | ✓ | ✓ | Ready；token 時效仍有 GAP-002 |
| US-1 | TASK 系列 001–005 | ✓ | ✓ | ✓ | Ready |
| US-2 | TASK 系列 006–018、TC-F-PREF-001 | ✓ | ✓ | ✓ | Ready |
| US-3 | TC-F-AUTH-014、TC-F-TASK-006 | ✓ | ✓ | ✓ | Ready |
| US-4 | TC-ST-TASK-003、TC-ERR-TASK-005、CMT 系列 001–008 | ✓ | ✓ | ✓ | Ready |
| US-5 | REM 系列 001–009 | ✓ | ✓ | ✓ | Planned |
| US-6 | TC-F-TASK-008、TC-ERR-TASK-009 | ✓ | ✓ | ✓ | Ready |
| US-7 | TASK 系列 010–014 | ✓ | ✓ | ✓ | Ready |
| US-8 | TC-F-TASK-019、TC-ST-TASK-020、TC-SQL-003 | ✓ | ✓ | ✓ | Ready |
| FLOW-PRJ | PRJ 系列 001–007 | ✓ | ✓ | ✓ | 部分；欄位邊界 Planned |
| FLOW-MEMBER | MEMBER 系列 001–007 | ✓ | ✓ | ✓ | Ready |
| FLOW-USER | USER 系列 001–008 | ✓ | ✓ | ✓ | Ready；現行版本不含個資編輯 |
| PREF | PREF 系列 001–002 | ✓ | ✓ | ✓ | Ready |
| API／DB | SQL 系列 001–007、API 系列 001–004 | ✓ | ✓ | ✓ | 部分；Email UNIQUE Planned |
| UI／UIMock | UI 系列 001–008 | ✓ | ✓ | ✓ | Ready；舊 PNG 差異依 `UIMock/README.md` |

## 6. 自動化覆蓋摘要與建議順序

### 6.1 目前可確認的自動化

- Backend Unit：註冊 validator、Bootstrap Admin policy、目前使用者 claims、Domain status／版本／token entity、EF model metadata、SMTP option。
- Backend Integration：CSRF、註冊 validation Problem Details、OpenAPI surface；實際 SQL Server 的單一角色與業務編號完整性（未設定 `PMW_TEST_SQL_CONNECTION` 時會略過）。
- Frontend Unit／Component：HTTP client 的 CSRF／Bearer／single-flight refresh／Problem Details、註冊導頁與欄位 mapping、Bootstrap Admin UI 保護、Project Role 複選、少量 Project detail 與 StatusBadge。
- Frontend E2E：登入、語言、mobile drawer、refresh restore、Admin 建立 Project 與 Task；需實際 Backend、SQL Server 與 `PMW_E2E_PASSWORD`。

### 6.2 建議自動化優先順序

1. P0 API／Service 授權矩陣：Viewer、User assignee／non-assignee、ProjectManager、Administrator、Admin。
2. 批次 Task 的全有或全無 transaction、rowVersion 衝突與 audit/history rollback。
3. 角色／帳號狀態原子更新、最後一位 Admin 並行競態、token revocation。
4. Project member 加入／角色取代／Owner 移交／未完成 Task 阻擋。
5. Task／Comment 軟刪除、關聯保存與 query filters。
6. 前端清單 query、返回狀態、checkbox 權限、確認偏好及 403/409/422 UX。
7. BE-001 實作後，補齊 TC-ST-REM-001～009 的 clock-controlled 與 SQL concurrency 測試。

## 7. 執行注意事項

- SQL 與 transaction 案例必須使用隔離的 SQL Server，不得用 EF InMemory 取代 relational constraint／rowversion／transaction 行為。
- Email 測試使用可控制的 gateway fake；只有 SMTP smoke test 才連外，且不得記錄完整驗證 token、密碼或 App Password。
- E2E 每次建立唯一資料並清理；不得依測試順序或既有正式資料。
- 涉及時間的案例固定 `TimeProvider`、UTC 與產品設定時區；到期提醒實作前先定義 DST 與「日期」邊界。
- `Planned` 案例不是通過或失敗；它代表必須先完成需求決議或功能實作。
