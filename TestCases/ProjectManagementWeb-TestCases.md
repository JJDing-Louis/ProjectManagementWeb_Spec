# ProjectManagementWeb 完整測試案例

## 1. 文件資訊

- **產出日期**：2026-09-07；**最後更新**：2026-09-13
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
| CON-007 | Project 表單限制 | Frontend 與 Backend／DB 不一致 | Name trim 後 1–200 字；Description 選填且最多 4000 字 | Frontend 欄位限制已對齊；Backend 邊界驗證尚待對齊 |
| CON-008 | Task Description 必填 | Frontend 必填，Backend／DB 允許空值 | Description 選填；有值時 trim 後最多 8000 字 | Frontend 必填與長度限制已對齊；Backend 8000 字邊界驗證尚待對齊 |
| CON-009 | 使用者設定範圍 | 舊草圖將個資、系統角色與專案角色放在同頁 | Settings 只管理語言與批次確認偏好；系統角色／啟用狀態在 User Detail；Project Roles 在 Project Detail | 已更新 User Story、C4 與 UI 草圖契約 |
| CON-010 | Schema 主鍵與資料模型 | 舊 Schema 為字串主鍵與明文式 Password | 以 EF migrations／model snapshot 為正式來源，使用 Identity GUID、`PasswordHash`、獨立關聯與 rowversion | `Schema.md` 已依現行模型改寫 |
| CON-011 | C4 Email 範圍 | C4 只繪出驗證信 | 到期提醒需包含 Scanner、Sender、唯一寄送紀錄、retry 與告警，未完成前一律標為 Planned | User Story、提醒 Flowchart、Backlog、彙整版與五張獨立 C4 圖已對齊；營運參數、Backend、Schema 與自動化測試尚待完成 |
| CON-012 | Project 清單搜尋方式 | 舊草圖為多欄位查詢與 Owner 篩選 | 單一 search 查 Code／Name／Description，另有 status；無 Owner filter | 已更新 User Story 與 UI 草圖契約 |
| CON-013 | Task 詳情操作型態 | 舊草圖在詳情頁直接 Confirm／Cancel | Task Detail 為詳情與留言；修改導向 `/admin/projects/{projectId}/task-items/{taskId}/edit` | 已更新 User Story、Flowchart、C4 與 UI 草圖契約 |

### 2.2 已確認的缺口處理方針

| ID | 已確認規則 | 待完成工作 | 驗收重點 | 狀態 |
|---|---|---|---|---|
| GAP-001 | 顯示名稱必填，trim 後為 1–100 字。 | Frontend 加上相同必填、trim 與 `maxlength=100` 規則；Backend 維持相同邊界與欄位錯誤。 | 0/1/100/101 字與純空白；UI/API 接受及拒絕界線一致。 | 已決議，待實作對齊 |
| GAP-002 | Email 驗證 Token 自簽發起有效 3 分鐘；重寄冷卻 60 秒，且每帳號及每 IP 於滾動 60 分鐘內最多 5 次。帳號／冷卻受限仍回 200 一般訊息，IP 濫用回 `429 rate_limited`；不存在帳號仍計入 IP。重寄成功後舊 Token 立即失效；成功使用過的 Token 再用必須失敗。 | Backend 建立可辨識最新版 Token、簽發時間、已使用狀態與帳號綁定的版本／nonce 或等效機制，並加入帳號及 IP 重寄限制。 | 驗證 3 分鐘邊界、60 秒冷卻、滾動 60 分鐘第 5／6 次、兩類 response、重寄前後 Token、重放與跨帳號攻擊；受限請求不得使現有 Token 失效。 | 已決議，待實作 |
| GAP-003 | 登入失敗不鎖定帳號；同一帳號或 IP 在滾動 15 分鐘內第 5 次失敗起回 `429 rate_limited`，本期不做 CAPTCHA，並保留安全稽核。只信任 allowlist reverse proxy 提供的 forwarded IP；多執行個體共用限流計數。 | 保留現行不累計帳號鎖定的密碼檢查；新增帳號與 IP rate limit、可信 proxy 設定、共享計數、一般化錯誤與安全稽核。 | 第 1–4 次失敗為 401；第 5 次及限制視窗內後續請求為 429；偽造 forwarded header 無效；跨 instance 仍共用門檻；視窗結束後正確密碼可登入。 | 部分已對齊；rate limit 與稽核待實作 |
| GAP-004 | Project 的 `Pending／Active／Completed／Archived` 目前允許任意互轉。 | User Story、API contract、Domain 與測試統一採無狀態轉換限制。 | 覆蓋 4×4 組合，包含更新為相同狀態。 | Backend 已對齊；待同步文件與補測試 |
| GAP-005 | Task 的 `Pending／InProgress／Blocked／Completed` 目前允許任意互轉。 | Flowchart 移除「可能因狀態轉換無效而拒絕」的暗示；Backend 與測試維持 4×4。 | 單筆、被指派者更新及批次更新皆覆蓋 4×4，包含相同狀態。 | Backend 已對齊；待同步文件與補測試 |
| GAP-006 | Project Owner 必須是已啟用、Email 已驗證，且系統角色恰為 `Administrator` 的帳號；`Admin`、`User`、`Viewer` 均不得擔任。修改 Owner 時還必須已是該 Project 成員。 | Backend 建立與修改 Project 都檢查 `IsEnabled=true`、`EmailConfirmed=true`、system role=`Administrator`；Frontend Owner 候選清單套用相同條件。 | 不存在、停用、未驗證、非 Administrator，以及修改時非成員皆拒絕，且不建立 Project／不移交 Owner。 | 已決議，待實作 |
| GAP-007 | UI checkbox 可選超過 10 筆，但單次批次狀態更新最多只能送出 10 筆。 | UI 選取超過 10 筆時保留選取，但停用送出並提示上限；Backend 對 11 筆以上回 `400 validation_error`，不得只取前 10 筆。 | 測 0/1/10/11 筆；11 筆時整批不更新，10 筆仍維持單一交易。 | 已決議，待實作 |
| GAP-008 | 同時符合「無權限」與「資源不存在」時優先回 `403`，避免洩漏資源存在性。 | 所有 Project-scoped Service/API 統一先檢查功能與資料範圍授權，再在已授權範圍內判斷 `404`。 | 無權＋存在、無權＋不存在皆為 403；有權＋不存在才是 404。 | 已決議，待全面盤點 |
| GAP-009 | `Projects.DeletedAt` 保留作為軟刪除；只有 `Administrator` 與 `Admin` 可刪除。刪除必須帶最新 rowVersion，衝突回 409 `concurrency_conflict`；記錄 `DeletedByAccountId` 與 AuditLog，FK 採 NoAction。本期不提供還原或永久刪除，子資料從一般查詢隱藏但不實體刪除。 | 補 Project delete User Story、API、UI、`DeletedByAccountId` nullable FK、rowVersion、權限與關聯查詢契約；現行 `DeletedAt` 與 query filter 保留。 | 允許角色、403 優先序、404、409、刪除者、時間、稽核、無還原／永久刪除入口，以及子資料保存。 | 已決議，待實作 |
| GAP-010 | `Accounts.NormalizedEmail` 改為 DB `NOT NULL`，並建立不帶 filter 的 UNIQUE index；重複時 API 回 `409 duplicate_email` 且包含 `errors.email`。Migration 發現 NULL／重複髒資料時 fail-fast，由人工修正後重跑，不自動合併或刪除帳號。 | 增加 migration 前置檢查，再調整 nullability 與 UNIQUE index；捕捉並行 UNIQUE 違規並映射固定 Problem Details。 | 大小寫正規化、並行註冊、NULL、髒資料 fail-fast、人工修正後重跑與固定 409 契約。 | 已決議，待 migration 與測試 |
| GAP-011 | `RefreshTokens.ReplacedByTokenId` 補上 nullable self-referencing Foreign Key，並設定 `.OnDelete(DeleteBehavior.NoAction)`。 | 補 EF mapping 與 migration；正常生命週期只撤銷 Token，不實體刪除；歷史清理由獨立 retention 流程處理。 | 不存在的 replacement ID 被 DB 拒絕；合法 rotation chain 可保存；被參照 Token 不得因 cascade 消失。 | 已決議，待 migration 與測試 |
| GAP-012 | Task 到期提醒依 Project 必填的 IANA `TimeZoneId`，每天 Project 當地時間 08:00 執行；同一 Project 當地日期只執行一次，當日服務恢復即補跑。初次失敗後最多重試 3 次，間隔 5、15、60 分鐘；最終告警寫 DB 與結構化 log，本期不做管理 UI。 | Project 補 `TimeZoneId`；既有資料由部署必填的 migration 預設 IANA timezone 回填，新 Project 必須明確指定；實作 Scanner、Sender、claim、retry、告警與測試。 | 多時區 08:00、DST 日期冪等、當日補跑、3 次重試、DB／log 告警、去重、多 worker、Task 完成與帳號失效。 | 已決議，待實作 |
| GAP-013 | Backend 核心 Service/API 授權、交易與並行路徑必須補自動化測試。 | 優先補角色矩陣、批次 rollback、rowversion、Owner、成員角色、token rotation、軟刪除及 audit/history。 | 使用實際 SQL Server 驗證 relational constraint、transaction 與 concurrency；不得以 EF InMemory 取代。 | 已決議，待實作 |
| GAP-014 | Frontend 必須補 Task 清單、批次、留言、角色與主要錯誤流程的 Component／E2E 測試。 | 補 URL query／返回狀態、checkbox、10 筆上限、偏好、留言、角色複選及 403/409/422 UX。 | Vitest 驗證元件行為；Playwright 驗證前後端整合，不只檢查元素存在。 | 已決議，待實作 |
| GAP-015 | Frontend `AGENTS.md` 必須更新為目前已完成 Vue 3 初始化且已串接 Backend 的現況。 | 移除「尚未建立前端專案」敘述，保留現行 Vue 3、TypeScript、Vite、Pinia、Router、Vitest 與 Playwright 規範。 | 文件敘述與 `package.json`、目錄、route、service 及測試工具一致。 | 已完成 |

### 2.3 已確認的 OPEN 決議

| ID | 最終決議 |
|---|---|
| OPEN-001 | Email 驗證 Token 有效期精確為 3 分鐘；重寄冷卻 60 秒，每帳號及每 IP 於滾動 60 分鐘內最多 5 次。 |
| OPEN-002 | 登入採帳號與 IP rate limit；滾動 15 分鐘內第 5 次失敗起回 `429 rate_limited`，不鎖帳號，本期不做 CAPTCHA，需保留安全稽核。 |
| OPEN-003 | 只有已啟用、Email 已驗證且系統角色恰為 `Administrator` 的帳號可擔任 Project Owner；`Admin` 不在允許範圍。 |
| OPEN-004 | 本期提供 Project 軟刪除；`Administrator` 與 `Admin` 可刪除，記錄 `DeletedByAccountId` 與 AuditLog，不提供還原；子資料隱藏但不實體刪除。 |
| OPEN-005 | 每個 Project 使用必填 IANA `TimeZoneId`；依當地時間每日 08:00 執行提醒；失敗後最多重試 3 次，間隔 5、15、60 分鐘。 |
| OPEN-006 | `NormalizedEmail` 改為 `NOT NULL` 並建立無 filter UNIQUE index；重複回 `409 duplicate_email` 與 `errors.email`。 |
| OPEN-007 | 已成功使用的 Email 驗證 Token 再次使用回 `400 invalid_email_token`；跨帳號失敗不得消耗原 Token。 |
| OPEN-008 | `RefreshTokens.ReplacedByTokenId` self-FK 採 `.OnDelete(DeleteBehavior.NoAction)`。 |

### 2.4 已確認的補充決議

| ID | 最終決議 |
|---|---|
| OPEN-009 | `DeletedByAccountId` nullable FK 採 NoAction；本期不提供 Project 永久刪除，資料持續保留。 |
| OPEN-010 | 以 Project 當地日期作為提醒冪等鍵；DST 不得造成同一日期重複或遺漏。08:00 停機時於同一當地日恢復後補跑；最終 Failed 告警寫入 DB 與結構化 log，本期不提供管理 UI。 |
| OPEN-011 | 只信任 allowlist reverse proxy 的 forwarded IP；未經信任來源的 header 不採用。多執行個體必須使用共享 rate-limit store。 |
| OPEN-012 | Migration 由部署設定提供必填預設 IANA timezone 回填既有 Project；新 Project 不採系統預設值，必須明確指定 TimeZoneId。 |
| OPEN-013 | Email 重寄上限採滾動 60 分鐘；帳號／60 秒冷卻限制回 200 一般訊息，IP 濫用回 `429 rate_limited`；不存在帳號仍計入 IP。 |
| OPEN-014 | Project 軟刪除必須帶最新 rowVersion；stale rowVersion 回 409 `concurrency_conflict`。 |
| OPEN-015 | NormalizedEmail migration 發現 NULL／重複資料時 fail-fast，由人工修正後重跑；不得自動合併或刪除帳號。 |

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
- **類型與優先級**：Edge／P1；**測試層級**：Unit、API、UI；**狀態**：Planned（GAP-001）
- **對應需求**：AUTH；`RegistrationRules`
- **前置條件**：無。
- **測試步驟**：分別送出帳號 256/257 字、顯示名稱 trim 後 0/1/100/101 字與純空白、密碼 9/10 字，以及合法帳號字元 `-._@+`；同步檢查 UI 的 required、trim 與 `maxlength=100`。
- **預期結果**：顯示名稱 1/100 字可送出，0/101 字與純空白在 UI 阻擋且 API 回 400 欄位錯誤；其他欄位上限內通過、超界拒絕；UI 與 API 邊界一致並保留失敗輸入。
- **資料後置狀態**：失敗組不新增帳號；成功組依個案清理。
- **現有自動化覆蓋**：部分：`RegistrationValidatorTests` 僅測一般有效／無效值；Frontend 顯示名稱目前未設定 `maxlength=100`。

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
- **測試步驟**：1. 以不存在帳號、錯密碼、停用帳號登入。2. 對有效帳號連續送出錯誤密碼。3. 隨後以正確密碼登入。
- **預期結果**：失敗皆回 401 `invalid_credentials` 與相同一般訊息；不洩漏帳號存在或停用狀態；錯誤登入不鎖定帳號、不停用帳號，之後正確密碼仍可登入。
- **資料後置狀態**：失敗時不新增 refresh token，且不因失敗次數改變帳號啟用／鎖定狀態；最後成功登入才新增 token。
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
- **類型與優先級**：Error／P0；**測試層級**：Unit、API、UI；**狀態**：Planned（GAP-002）
- **對應需求**：AUTH；Email 驗證 Flowchart
- **前置條件**：固定 TimeProvider；準備亂碼、變造 Token 與簽發時間已知的有效 Token。
- **測試步驟**：分別在簽發後 2:59.999、3:00.000，以及超過 3 分鐘時呼叫 confirm；另送亂碼與變造 Token。
- **預期結果**：3 分鐘以前有效；自簽發滿 3 分鐘起，以及亂碼／變造 Token 均回 400 `invalid_email_token`，顯示不洩漏細節的失效訊息並提供重寄路徑。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無；目前尚未落實精確 3 分鐘契約。

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
- **前置條件**：準備已登入且持有有效 refresh cookie 的 client，以及沒有 cookie、帶未知 cookie 的 client。
- **測試步驟**：1. 有效 client 呼叫 logout，檢查 Set-Cookie／DB，再 refresh 與開受保護頁。2. 另外以缺少及未知 refresh cookie 呼叫 logout。
- **預期結果**：三種請求皆為 204 且清除 `PMW-REFRESH` cookie；有效 token 被撤銷且後續 refresh 失敗；缺少或未知 token 採冪等成功、不建立或異動其他 token；UI 回登入頁。
- **資料後置狀態**：有效 client 的 session 結束；缺少或未知 token 不影響其他 session；業務資料不變。
- **現有自動化覆蓋**：無。

#### TC-F-AUTH-014 Session restore 與同時 401 single-flight
- **類型與優先級**：Functional／P0；**測試層級**：UI、E2E；**狀態**：Ready
- **對應需求**：US-3；Frontend contract
- **前置條件**：refresh cookie 有效，記憶體 access token 已清除。
- **測試步驟**：重新整理；同時觸發多個需授權 request；觀察 network。
- **預期結果**：只送一次 refresh；取得新 access token 後各原 request 最多重送一次；不形成 loop。
- **資料後置狀態**：保持登入並完成 token rotation。
- **現有自動化覆蓋**：完整（部分層級）：`mockServices.spec.ts` 三案例、`app.spec.ts` refresh E2E。

#### TC-ERR-AUTH-015 重寄後舊 Email 驗證 Token 立即失效
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL；**狀態**：Planned（GAP-002）
- **對應需求**：AUTH；Email 驗證 Flowchart；GAP-002
- **前置條件**：同一未驗證啟用帳號已取得 Token A；Backend 已實作可辨識最新版 Token 的版本／nonce 或等效機制。
- **測試步驟**：1. 重寄並取得 Token B。2. 以 Token A 驗證。3. 以 Token B 驗證。
- **預期結果**：Token A 在重寄完成後立即回 400 `invalid_email_token`；Token B 可成功驗證；回應不揭露失效原因細節。
- **資料後置狀態**：帳號只由最新版 Token 驗證成功；Token A 無法再改變資料。
- **現有自動化覆蓋**：無；目前 Identity Email Token 未綁定「最新一次重寄」版本，因此功能尚未實作。

#### TC-ERR-AUTH-016 已使用 Email 驗證 Token 的重放語意
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL；**狀態**：Planned（GAP-002、OPEN-007）
- **對應需求**：AUTH；GAP-002；OPEN-007
- **前置條件**：未驗證啟用帳號持有目前最新版 Token。
- **測試步驟**：1. 使用 Token 完成驗證。2. 以相同 Token 再次呼叫驗證端點。
- **預期結果**：第一次成功；第二次回 400 `invalid_email_token`，不得視為冪等成功，且不洩漏 Token 已使用的細節。
- **資料後置狀態**：帳號只產生一次有效驗證狀態轉換，重放不產生額外狀態或稽核異動。
- **現有自動化覆蓋**：無；一次性使用狀態尚未實作。

#### TC-ERR-AUTH-017 Email 驗證 Token 不可跨帳號使用
- **類型與優先級**：Security／P0；**測試層級**：Service、API；**狀態**：Planned（GAP-002、OPEN-007）
- **對應需求**：AUTH；Email 驗證 Token 的帳號綁定安全契約；OPEN-007
- **前置條件**：未驗證帳號 A、B；Token A 為 A 的最新版 Token。
- **測試步驟**：1. 以帳號 B 的 accountId 搭配 Token A 呼叫驗證端點。2. 再由帳號 A 使用 Token A。
- **預期結果**：跨帳號請求回 400 `invalid_email_token` 且不揭露 Token 所屬帳號；攻擊請求不消耗 Token A，帳號 A 隨後仍可在 3 分鐘內成功驗證。
- **資料後置狀態**：帳號 B 維持未驗證；帳號 A 只因自己的合法請求完成驗證。
- **現有自動化覆蓋**：無；跨帳號失敗不消耗 Token 的狀態追蹤尚未實作。

#### TC-ERR-AUTH-018 重寄驗證信冷卻與每小時上限
- **類型與優先級**：Security／P0；**測試層級**：Service、API；**狀態**：Planned（GAP-002、OPEN-001、OPEN-013）
- **對應需求**：AUTH；GAP-002；OPEN-001；OPEN-013
- **前置條件**：固定 TimeProvider；未驗證啟用帳號；可辨識相同／不同 IP。
- **測試步驟**：1. 首次重寄。2. 在 59.999 秒及 60 秒重寄。3. 分別以相同帳號／不同 IP、不同帳號／相同 IP 累計滾動 60 分鐘內第 5 與第 6 次。4. 以不存在帳號累計 IP 次數。5. 視窗結束後再重寄。
- **預期結果**：帳號或冷卻受限時仍回 200 一般訊息；滿 60 秒可進入頻率判斷；每帳號第 6 次回一般 200 但不寄信，每 IP 第 6 次回 429 `rate_limited`；不存在帳號仍累計 IP 且不洩漏存在性；滾動視窗結束後可重寄。
- **資料後置狀態**：只有允許的請求建立新 Token／EmailMessages；被限制請求不建立 Token、不使現有 Token 失效。
- **現有自動化覆蓋**：無；冷卻與雙維度限制尚未實作。

#### TC-SEC-AUTH-019 登入失敗 rate limit、不鎖帳號與安全稽核
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL；**狀態**：Planned（GAP-003、OPEN-002、OPEN-011）
- **對應需求**：AUTH；GAP-003；OPEN-002；OPEN-011
- **前置條件**：固定 TimeProvider；有效啟用帳號；設定 allowlist reverse proxy，並準備兩個共用 rate-limit store 的應用執行個體。
- **測試步驟**：以同帳號／不同 IP 及不同帳號／同 IP 分別在滾動 15 分鐘內送出 5 次錯誤密碼；跨兩個執行個體累計；再送第 6 次與正確密碼；另偽造非可信來源的 forwarded IP；時間推進超過視窗後登入並檢查稽核。
- **預期結果**：兩個維度及跨 instance 都能啟動同一限制；只採信 allowlist proxy 的 forwarded IP；第 1–4 次失敗回 401，第 5 次及限制視窗內後續請求回 429 `rate_limited`；不顯示 CAPTCHA、不鎖定帳號；視窗結束後可登入；稽核不記錄密碼／Token。
- **資料後置狀態**：帳號狀態不變；只有最後成功登入建立 refresh token；保留不含敏感資料的安全稽核與 rate-limit 計數。
- **現有自動化覆蓋**：無；rate limit 與登入安全稽核尚未實作。

#### TC-F-AUTH-020 已驗證帳號正常登入與目前帳號資料
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、UI、E2E；**狀態**：Ready
- **對應需求**：AUTH；登入 Flowchart；API login、`/auth/me` 與 Cookie 契約
- **前置條件**：已啟用且 Email 已驗證的 User、Administrator、Admin 帳號各一；密碼正確。
- **測試步驟**：1. 取得 CSRF token 與配對 cookie。2. 各帳號登入。3. 檢查 response、`PMW-REFRESH` Set-Cookie 與 RefreshTokens。4. 以 access token 呼叫 `/auth/me`。
- **預期結果**：CSRF endpoint 回 200 token 與配對 cookie；登入 200；JSON 只含 access token 與到期時間，不含 refresh token；refresh token 只以 HttpOnly、Path=`/api/v1/auth` cookie 傳遞且 DB 僅保存 hash；`/auth/me` 的帳號、Email、名稱、驗證／啟用狀態、唯一系統角色與 functions 均與目前帳號一致；UI 進入原 redirect 或 Task 清單。
- **資料後置狀態**：每次登入新增一筆有效 refresh token；帳號與業務資料不變。
- **現有自動化覆蓋**：部分：`mockServices.spec.ts` 驗證 CSRF／Bearer 流程，`app.spec.ts` 驗證登入後載入 Project；未驗證三種角色、Cookie／DB 與 `/auth/me` 完整欄位。

#### TC-ERR-AUTH-021 缺少、未知、過期、已撤銷或停用帳號的 Refresh Token
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：AUTH；API refresh contract
- **前置條件**：固定 TimeProvider；準備未知 token、已過期 token、已撤銷 token，以及 token 有效但帳號已停用的四組資料；另準備無 cookie client。
- **測試步驟**：各組帶有效 CSRF 配對呼叫 refresh，檢查 Problem Details、Set-Cookie、token family 與前端登入狀態。
- **預期結果**：缺少 cookie 回 401 `missing_refresh_token`；未知 token 回 401 `invalid_refresh_token`；過期或已撤銷 token 回 401 `refresh_token_reuse` 並撤銷同 family 尚有效 token；停用帳號回 401 `account_disabled` 並撤銷該 token；均不回傳 access／refresh token，UI 清除登入狀態且不得形成重試迴圈。
- **資料後置狀態**：應撤銷的 token／family 已撤銷；沒有新增 token 或業務資料異動。
- **現有自動化覆蓋**：部分：`mockServices.spec.ts` 只測前端 refresh 401 清除 access token；Backend 各失敗分支尚無自動化。

#### TC-ERR-AUTH-022 重寄驗證信時 SMTP 失敗
- **類型與優先級**：Error／P1；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：AUTH；註冊與 Email 驗證 Flowchart 的重寄失敗路徑
- **前置條件**：未驗證且啟用帳號；重寄限制未觸發；Email gateway 回傳失敗。
- **測試步驟**：以帳號及 Email 分別重寄，檢查 response、EmailMessages 與驗證頁；恢復 gateway 後再次重寄。
- **預期結果**：為避免揭露帳號狀態，失敗時仍回 200 一般訊息；EmailMessages 記錄 Failed 與可診斷但不含敏感 token 的錯誤；UI 保留重寄入口且不宣稱已成功寄出；gateway 恢復後可依冷卻／上限規則重試。
- **資料後置狀態**：失敗寄送有 Failed 紀錄且帳號仍未驗證；恢復後成功重寄的最新版 Token 與舊 Token 狀態另依 TC-ERR-AUTH-015 驗證。
- **現有自動化覆蓋**：無；現有前端測試只覆蓋註冊首次寄信失敗提示。

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

#### TC-F-USER-009 本人與管理者讀取使用者詳情
- **類型與優先級**：Functional／P1；**測試層級**：API、UI；**狀態**：Ready
- **對應需求**：User Story「畫面與查詢契約」；FLOW-USER；`GET /users/{id}`
- **前置條件**：一般帳號本人、具 `accounts.read` 的 Admin，以及存在與不存在的 userId。
- **測試步驟**：1. 本人讀取自己的詳情。2. Admin 讀取他人詳情。3. 兩者在已授權條件下讀取不存在 ID。4. 核對 `/users/{id}` 顯示內容與可操作控制。
- **預期結果**：存在資料回 200，包含帳號、顯示名稱、Email、驗證狀態、啟用狀態、唯一系統角色及 bootstrap 標記；已授權但不存在回 404 `not_found`；一般本人只讀，Admin 僅依 functions 顯示角色／啟用狀態控制，不提供個資編輯。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-USER-010 帳號管理授權與不存在的帳號／角色
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：User Story「使用註冊」4；FLOW-USER；使用者管理 API 契約
- **前置條件**：User、Viewer、Administrator、Admin 各一；準備存在及不存在的 userId、有效及不存在的 roleId。
- **測試步驟**：1. 非 Admin 三種角色直接呼叫 `/role`、`/status`、`/administration`，目標分別為存在與不存在帳號。2. Admin 對不存在帳號變更狀態。3. Admin 對存在帳號指定不存在角色。4. 檢查 UI、AccountRoles、狀態、TokenVersion、RefreshTokens 與 AuditLogs。
- **預期結果**：只有具備對應 manage functions 的 Admin 可進入異動流程；非 Admin 對存在或不存在目標皆回 403 且 UI 不顯示操作；Admin 對不存在帳號或角色回 404 `not_found`；所有失敗均不變更角色／狀態、不遞增 TokenVersion、不撤銷 session，也不寫成功 audit。
- **資料後置狀態**：所有帳號、角色關聯、token 與稽核維持原狀。
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
- **類型與優先級**：Functional／P0；**測試層級**：API、SQL、E2E；**狀態**：Planned（GAP-006、OPEN-005）
- **對應需求**：FLOW-PRJ；API Project contract
- **前置條件**：具 projects.create；Owner 帳號啟用、Email 已驗證且系統角色為 Administrator；提供有效 IANA TimeZoneId。
- **測試步驟**：建立 Project，檢查 response、Projects、ProjectMembers、ProjectMemberRoles、AuditLogs 與 TimeZoneId。
- **預期結果**：201；狀態 Pending、versionNumber=1；產生 `PRJ-YYYYMMDD######`；Owner 自動成為 member 且具 ProjectManager；保存 IANA TimeZoneId 並建立稽核。
- **資料後置狀態**：Project 與 Owner 關聯完整。
- **現有自動化覆蓋**：部分：`app.spec.ts` 測 Admin 建立與 code 格式；編號另有 SQL tests；Backend 目前只檢查 Owner 啟用狀態，尚未檢查 Email 驗證與 Administrator role，Project 也沒有 TimeZoneId。

#### TC-ERR-PRJ-004 無權建立與不具資格的 Owner
- **類型與優先級**：Security／P0；**測試層級**：API、SQL；**狀態**：Planned（GAP-006）
- **對應需求**：FLOW-PRJ
- **前置條件**：準備 Viewer／User／Admin／Administrator，以及不存在、停用、未驗證或非 Administrator 的 Owner 候選帳號。
- **測試步驟**：1. 無建立權限角色嘗試建立。2. 有權角色分別以不存在、停用、未驗證、Admin、User、Viewer 作 Owner 建立。3. 修改時分別指定非成員或任一不合格成員為 Owner。
- **預期結果**：無權 403；任一無效 Owner 回 422 `invalid_owner`；建立失敗不消耗已 rollback 的業務編號、不產生孤兒資料；修改失敗不移交 Owner。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`SqlServerConstraintTests` 測編號 rollback，不測 Project service。

#### TC-E-PRJ-005 Project 欄位邊界
- **類型與優先級**：Edge／P1；**測試層級**：API、SQL、UI；**狀態**：Planned（CON-007）
- **對應需求**：FLOW-PRJ；DB
- **前置條件**：Frontend 完成對齊正式輸入契約。
- **測試步驟**：測名稱 trim 後 0/1/2/120/121/200/201 字及 description 空值/4000/4001 字。
- **預期結果**：名稱 1–200 字通過，0 或 201 字拒絕；description 空值或最多 4000 字通過，4001 字拒絕；前後端界線一致且回欄位錯誤而非 DB 500。
- **資料後置狀態**：拒絕值不建立／更新。
- **現有自動化覆蓋**：部分：Frontend 已有元件測試鎖定名稱 1–200 字與 Description 選填／4000 字上限；Backend 邊界驗證與 API／SQL 測試尚未完成。

#### TC-ST-PRJ-006 修改 Project 並增加版本
- **類型與優先級**：State／P0；**測試層級**：API、SQL、UI；**狀態**：Planned（GAP-006）
- **對應需求**：FLOW-PRJ；optimistic concurrency
- **前置條件**：可管理 Project，持有最新 rowVersion；新 Owner 是已啟用、Email 已驗證、system role=Administrator 的既有 Project 成員。
- **測試步驟**：更新名稱、說明、Owner、status、TimeZoneId；重新讀取。
- **預期結果**：200；基本資料更新；VersionNumber 加 1；回傳新 rowVersion；稽核含前後資料；成員／Task 異動不增加 VersionNumber。
- **資料後置狀態**：保存新資料與版本。
- **現有自動化覆蓋**：部分：`DomainEntityTests`、`DatabaseModelTests` 只測 VersionNumber；Backend 目前未確認新 Owner 的啟用、Email 驗證與 Administrator role，也沒有 TimeZoneId。

#### TC-ERR-PRJ-007 Project rowVersion 衝突
- **類型與優先級**：Concurrency／P0；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-PRJ
- **前置條件**：兩個 client 取得相同 rowVersion。
- **測試步驟**：A 成功更新；B 以舊 rowVersion 更新。
- **預期結果**：B 回 409 `concurrency_conflict`；UI 保留輸入並要求重新載入；A 資料不被覆蓋。
- **資料後置狀態**：只保留 A 更新。
- **現有自動化覆蓋**：無。

#### TC-ST-PRJ-008 四種 Project status 任意互轉
- **類型與優先級**：State／P1；**測試層級**：Unit、API；**狀態**：Ready（GAP-004）
- **對應需求**：FLOW-PRJ；GAP-004
- **前置條件**：可管理 Project，且每次操作持有最新 rowVersion。
- **測試步驟**：以資料驅動覆蓋 Pending／Active／Completed／Archived 的 16 組 source→target。
- **預期結果**：16 組均可成功，包含更新為相同狀態；每次成功更新依契約增加版本並留下稽核，不回傳狀態轉換錯誤。
- **資料後置狀態**：每次操作後為指定目標狀態，並保存最新 rowVersion／VersionNumber。
- **現有自動化覆蓋**：部分：`DomainEntityTests` 只驗證 Pending→Active，未覆蓋 16 組。

#### TC-ST-PRJ-009 軟刪除 Project 並記錄刪除者
- **類型與優先級**：Security／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Planned（GAP-009、OPEN-004、OPEN-014）
- **對應需求**：FLOW-PRJ；DB；GAP-009；OPEN-014
- **前置條件**：Administrator 或 Admin；Project 含 Member、Task、Comment、history；持有最新 rowVersion。
- **測試步驟**：由兩種允許角色分別刪除 Project；查一般 API、IgnoreQueryFilters 資料、DeletedAt、DeletedByAccountId 與 AuditLogs。
- **預期結果**：回 204；Project 從一般 list/detail 隱藏；所屬 Member、Task、Comment 從一般 Project scope 隱藏但資料列未實體刪除；DeletedAt 與登入操作者 DeletedByAccountId 正確；稽核含 Project 與操作者。
- **資料後置狀態**：Project 軟刪除且關聯歷史完整保留；本期沒有還原入口。
- **現有自動化覆蓋**：無；目前只有 Projects.DeletedAt/query filter，尚無刪除 API、DeletedByAccountId 或 UI。

#### TC-ERR-PRJ-010 Project 軟刪除授權、重複刪除與不存在資源
- **類型與優先級**：Security／P0；**測試層級**：Service、API、UI；**狀態**：Planned（GAP-008、GAP-009、OPEN-014）
- **對應需求**：FLOW-PRJ；GAP-008；GAP-009；OPEN-014
- **前置條件**：Viewer、User、Administrator、Admin；準備存在、已軟刪除及不存在 Project。
- **測試步驟**：四種角色分別刪除三種 Project；以 stale rowVersion 刪除；另直接嘗試呼叫未提供的 restore／永久刪除 endpoint 或操作 UI。
- **預期結果**：只有 Administrator、Admin 可刪除存在 Project；其他角色對存在／不存在 Project 均優先回 403；已授權角色對不存在或已刪除 Project 回 404；stale rowVersion 回 409 `concurrency_conflict`；不提供 restore 或永久刪除 API／UI。
- **資料後置狀態**：失敗操作不改 DeletedAt、DeletedByAccountId、子資料或 AuditLogs；成功刪除只產生一次稽核。
- **現有自動化覆蓋**：無；功能尚未實作。

#### TC-E-PRJ-011 Project IANA TimeZoneId 驗證與既有資料遷移
- **類型與優先級**：Data integrity／P0；**測試層級**：API、SQL、UI；**狀態**：Planned（OPEN-005、OPEN-012）
- **對應需求**：FLOW-PRJ；US-5；DB；OPEN-012
- **前置條件**：已決議合法 IANA timezone 清單；部署設定提供 migration 預設 IANA timezone；migration 前已有 Project 資料。
- **測試步驟**：建立／修改時分別送 `Asia/Taipei`、其他合法 IANA ID、空白、Windows timezone ID 與未知 ID；執行 migration 前置檢查及既有資料回填。
- **預期結果**：合法 IANA ID 可保存並原樣 round-trip；新 Project 的空白、Windows ID、未知 ID 回 400 欄位錯誤且不得套用系統預設；migration 使用部署設定回填既有 Project，設定缺少或無效時 fail-fast。
- **資料後置狀態**：新資料皆明確指定合法 TimeZoneId；既有資料使用部署設定的合法 IANA timezone 回填。
- **現有自動化覆蓋**：無；Project 尚無 TimeZoneId 欄位。

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

#### TC-F-MEMBER-008 讀取專案成員與多重角色
- **類型與優先級**：Functional／P1；**測試層級**：API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER；CON-004；`GET /projects/{id}/members`
- **前置條件**：Project 包含 Owner、單一角色成員、多重角色成員；另有不屬於該 Project 的帳號。
- **測試步驟**：以 Project 成員及全域管理者讀取 members；核對 Account、Name 與角色集合；再以非成員直接呼叫。
- **預期結果**：有權者取得該 Project 全部未移除成員，每位成員的多重角色不遺漏、不重複且與 DB 關聯一致；不回傳 Email 等候選／成員 API 未約定欄位；無權者回 403，UI 不顯示其他 Project 成員資料。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：部分：`projectDetailView.spec.ts` 只以 mock 成員資料驗證部分畫面結構，未覆蓋 API／DB 對應。

#### TC-ERR-MEMBER-009 不存在、停用或競態失效的成員候選人
- **類型與優先級**：Error／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Ready
- **對應需求**：FLOW-MEMBER「搜尋有效且未停用的使用者」；成員 API 契約
- **前置條件**：可管理 Project；準備不存在、已停用及原先在候選清單但送出前被停用的帳號。
- **測試步驟**：1. 直接以不存在或已停用 accountId 加入成員。2. 先取得有效候選人，再於提交前停用該帳號並送出。3. 檢查錯誤、畫面候選清單、ProjectMembers、ProjectMemberRoles 與 AuditLogs。
- **預期結果**：候選清單不顯示停用帳號；三種加入請求均回 422 `invalid_account`，UI 顯示帳號已不可使用並要求重新選擇；不得建立 membership、角色 mapping 或成功 audit。
- **資料後置狀態**：Project 成員與角色集合不變。
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
- **預期結果**：跨 route 的 Task 不得回傳；對 Project scope 無權時，不論 Task 是否存在皆回 403；已通過 scope 授權但 Task 不存在或不屬該 route 時才回 404。
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
- **類型與優先級**：Error／P0；**測試層級**：API、UI、SQL；**狀態**：Planned（CON-008）
- **對應需求**：US-6
- **前置條件**：可建立 Task。
- **測試步驟**：測空標題、301 字標題、不存在／其他 Project assignee、startAt>deadline；另送 description 空值、純空白、8000 與 8001 字。
- **預期結果**：非法資料回 400/422 對應 code；依正式契約，空 description 可接受，有值時 trim 後最多 8000 字；失敗不產生 Task/history/audit 或消耗編號。
- **資料後置狀態**：失敗個案不變。
- **現有自動化覆蓋**：部分：Frontend 已有元件測試鎖定 Description 選填與 8000 字上限；Backend 尚未在寫入 DB 前把 8001 字映射為欄位驗證錯誤。

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
- **類型與優先級**：Functional／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Planned（GAP-007）
- **對應需求**：US-2；批次 Flowchart
- **前置條件**：選取 1 或 10 筆，皆有權且 rowVersion 最新。
- **測試步驟**：分別以 1、10 筆確認視窗檢查筆數／目標；送 batch-status；查詢 Task、history、audit；重載 UI。
- **預期結果**：200 `updatedCount=X`；同一 transaction 全部改為目標狀態；每筆有 history/audit；清除選取並顯示成功筆數。
- **資料後置狀態**：所有選取 Task 一致更新。
- **現有自動化覆蓋**：無；目前 UI 與 Backend 都沒有單批 10 筆上限。

#### TC-ERR-TASK-016 批次資料任一筆失敗全部 rollback
- **類型與優先級**：Transaction／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Planned（GAP-008）
- **對應需求**：US-2；批次 Flowchart
- **前置條件**：混入無權、跨 Project、不存在或 stale rowVersion 任一筆。
- **測試步驟**：對每類錯誤各送一批；失敗後查全部 Task/history/audit。
- **預期結果**：含無權項目時，即使同批另含不存在項目也優先回 403；全部已授權但含不存在項目才回 404；版本衝突回 409；沒有任何 Task 更新，也不留下該批 history/audit；UI 保留原畫面與選取並顯示原因。
- **資料後置狀態**：整批不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-TASK-017 空批次、重複 Task ID 與超過 10 筆
- **類型與優先級**：Error／P0；**測試層級**：API、UI；**狀態**：Planned（GAP-007）
- **對應需求**：US-2；API contract
- **前置條件**：已登入。
- **測試步驟**：1. 送空 tasks。2. 同一 taskId 兩次（相同或不同 rowVersion）。3. UI 勾選 11 筆。4. 繞過 UI 直接送 11 筆 API request。
- **預期結果**：空集合回 400 `validation_error`；重複 ID 回 400 `duplicate_task`；UI 保留 11 筆選取但停用送出並提示上限；API 對 11 筆回 400 `validation_error`，不得截斷成前 10 筆。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無；目前 UI 允許直接送出 11 筆，Backend 亦未拒絕。

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

#### TC-F-TASK-021 Task 詳情完整欄位、唯讀呈現與編輯導向
- **類型與優先級**：Functional／P0；**測試層級**：API、UI、E2E；**狀態**：Ready
- **對應需求**：US-4；Task Detail 畫面與「從詳細頁修改 Task」Flowchart；CON-013
- **前置條件**：可讀 Task 的 Viewer、被指派 User 與後台管理者；Task 具有完整描述及時間資料，清單 URL 已帶搜尋／篩選／排序／分頁 query。
- **測試步驟**：各角色由清單開啟 `/projects/{projectId}/task-items/{taskId}`；核對所有欄位、留言區、編輯控制與返回；有修改權角色點擊編輯後取消。
- **預期結果**：顯示 Task 編號、標題、描述、開始時間、交付期限、建立者、指派對象、狀態、建立與最後更新時間；詳情頁不提供 Task 欄位內聯儲存；Viewer 沒有編輯／留言控制，被指派者與後台管理者依權限顯示編輯入口並導向 `/admin/projects/{projectId}/task-items/{taskId}/edit` 且預填目前資料；取消或返回後保留原清單 query。
- **資料後置狀態**：檢視、取消與返回皆不異動 Task；瀏覽器保留原清單條件。
- **現有自動化覆蓋**：無；現有 E2E 未直接覆蓋 Task 詳情完整欄位與角色化操作。

#### TC-ERR-TASK-022 修改 Task 的欄位、指派者與日期驗證
- **類型與優先級**：Error／P0；**測試層級**：Service、API、SQL、UI；**狀態**：Planned（CON-008）
- **對應需求**：US-7；US-4 被指派者可修改期限；新增與修改 Task Flowchart；CON-008
- **前置條件**：後台管理者與 Task 被指派者皆持有最新 rowVersion；另準備不存在、其他 Project 與已移除的成員。
- **測試步驟**：1. 完整 PUT 分別送空白／301 字標題、description 空值／純空白／8000／8001 字、三種無效 assignee，以及 startAt 晚於 deadline。2. 被指派者 PATCH deadline 為等於及早於既有 startAt。3. 每次失敗後查 Task、history、audit。
- **預期結果**：合法邊界可保存；空白／超長欄位回 400 `validation_error`，無效 assignee 回 422 `invalid_assignee`，不合法日期回 422 `invalid_deadline`；被指派者 deadline 等於 startAt 可成功，早於 startAt 被拒絕；失敗時 UI 保留輸入，Task、history、audit 均不變。
- **資料後置狀態**：只有合法邊界案例更新 Task 並產生對應追蹤；失敗案例完全不變。
- **現有自動化覆蓋**：部分：Frontend 已有元件測試鎖定 Description 選填與 8000 字上限；Backend 共用標題／指派者／日期驗證，但尚未在寫入 DB 前驗證 Description 8000 字上限。

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
- **預期結果**：不得洩漏或異動留言；對 route 的 Project scope 無權時一律先回 403，不因留言／Task 不存在改回 404；已授權 scope 內資源不存在才回 404。
- **資料後置狀態**：不變。
- **現有自動化覆蓋**：無。

#### TC-ERR-CMT-009 留言儲存失敗時保留未送出內容
- **類型與優先級**：Failure／P1；**測試層級**：Service、API、UI；**狀態**：Ready
- **對應需求**：US-4；留言 Flowchart 的 `commentSucceeded` 失敗路徑
- **前置條件**：具留言權限；可使新增或修改在 DB 儲存時失敗，並可模擬 5xx／網路 timeout。
- **測試步驟**：1. 輸入含換行的留言並觸發新增儲存失敗。2. 編輯既有留言並觸發失敗。3. 檢查 UI draft、留言串、DB 與 audit。4. 恢復服務後由使用者重送一次。
- **預期結果**：失敗時顯示可重試的一般錯誤，輸入內容保持原樣且不得顯示假成功；DB 不留下半套留言或成功 audit；恢復後只在使用者明確重送時建立／修改一次並重新載入留言串。
- **資料後置狀態**：失敗階段資料不變；重送成功後恰有一次留言異動及對應 audit。
- **現有自動化覆蓋**：無。

### 4.6 Task 到期提醒（全部 Planned）

#### TC-ST-REM-001 七日提醒視窗
- **類型與優先級**：State／P0；**測試層級**：Unit、Service、SQL；**狀態**：Planned
- **對應需求**：US-5；Email 到期提醒 Flowchart
- **前置條件**：Project 具有合法 IANA TimeZoneId；固定 UTC now 與 Project 當地日期；未完成 Task。
- **測試步驟**：在 Project 當地時間每日 08:00 執行掃描，資料驅動測 deadline 當地日期相對今天 -4 至 +4 天（到期前以正向天數表示）。
- **預期結果**：只在到期前 3/2/1 天、當天、逾期 1/2/3 天建立每日提醒；UTC 日期不同不得影響 Project 當地日期判斷；其餘不建立。
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
- **測試步驟**：固定 TimeProvider；執行初次寄送，分別在失敗後 4:59／5:00、14:59／15:00、59:59／60:00 驗證三次 retry，再觸發一次。
- **預期結果**：總嘗試最多 4 次；三次 retry 分別只在 5、15、60 分鐘到期後執行；第 4 次總嘗試失敗後標為 Failed，同時寫入 DB 與結構化 log 告警，不再排程。
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

#### TC-ST-REM-010 多 Project 時區皆於當地 08:00 執行
- **類型與優先級**：State／P0；**測試層級**：Unit、Service；**狀態**：Planned（OPEN-005）
- **對應需求**：US-5；GAP-012；OPEN-005
- **前置條件**：至少三個不同 UTC offset 的 IANA TimeZoneId Project，Task 皆在提醒視窗內；固定 TimeProvider。
- **測試步驟**：沿 UTC 時間軸推進並逐分鐘執行 scheduler 判斷；記錄各 Project scanner 的當地執行時間。
- **預期結果**：正常運行時每個 Project 於當地日 08:00 取得一次掃描資格；若 08:00 未執行，當地日內恢復後仍可取得一次補跑資格；不得以伺服器本機時區統一判斷，同一 UTC 時刻可執行零至多個 Project。
- **資料後置狀態**：每 Project／當地提醒日期最多建立一批符合資格的 reminder。
- **現有自動化覆蓋**：無；Project timezone 與 scheduler 尚未實作。

#### TC-ERR-REM-011 DST、08:00 漏跑與告警查詢
- **類型與優先級**：Operational／P1；**測試層級**：Service、SQL；**狀態**：Planned（OPEN-010）
- **對應需求**：US-5；OPEN-010
- **前置條件**：使用有 DST 的 IANA timezone；可模擬 scheduler 在 08:00 停機及最終寄送失敗。
- **測試步驟**：測 DST 切換日、08:00 前後停機／恢復、同一當地時間重複，以及達到 retry 上限後的營運查詢。
- **預期結果**：以 Project 當地日期作為冪等鍵，DST 重複／跳時不得重複或遺漏；08:00 漏跑後在同一當地日恢復即補跑，跨日不補前一日；最終 Failed 同時寫 DB 與結構化 log，本期不提供管理 UI。
- **資料後置狀態**：每 Project／當地日期最多一批 reminder；補跑與最終失敗均可由 DB／log 追蹤。
- **現有自動化覆蓋**：無；需求已決議，功能與自動化尚未實作。

#### TC-ST-REM-012 寄送前 Task 改期、改派或軟刪除
- **類型與優先級**：State／P0；**測試層級**：Service、SQL；**狀態**：Planned
- **對應需求**：US-5；Email 到期提醒 Flowchart 的寄送前重查
- **前置條件**：已為未完成 Task 與原收件人建立 Pending reminder，但尚未呼叫 Email provider。
- **測試步驟**：分別在 reminder 建立後、worker 執行寄送前重查之前，將 Task 期限移出當日提醒視窗、改派給另一成員或軟刪除，再執行寄送；下一次掃描檢查新期限／新收件人的資格。
- **預期結果**：舊 reminder 在寄送前重查後標記 Cancelled 且不寄給原收件人；改派不沿用舊收件人紀錄，新收件人僅在符合其提醒日期時建立獨立唯一紀錄；軟刪除 Task 不再建立提醒；狀態與取消原因可追蹤。
- **資料後置狀態**：舊 reminder=Cancelled；不產生錯誤收件或重複寄送；後續只保留依最新 Task 狀態合法建立的 reminder。
- **現有自動化覆蓋**：無；功能尚未實作。

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
- **類型與優先級**：Data integrity／P1；**測試層級**：SQL；**狀態**：Planned（OPEN-009；其餘既有 FK 可先執行）
- **對應需求**：DB；OPEN-009
- **前置條件**：完整關聯資料。
- **測試步驟**：嘗試刪除被 Project/Task/history/comment/audit 參照的 Account、Project、Task；另刪除 membership，並嘗試刪除被 Projects.DeletedByAccountId 參照的 Account。
- **預期結果**：既有 Restrict/NoAction 防止遺失歷史；刪 membership 僅 cascade 其 ProjectMemberRoles；Identity 支援資料依 migration 規則處理；被 DeletedByAccountId 參照的 Account 因 NoAction 不得刪除。
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
- **類型與優先級**：Security／P0；**測試層級**：Service、SQL；**狀態**：Planned（GAP-009；其餘既有異動可先執行）
- **對應需求**：各異動 Flowchart、DB
- **前置條件**：登入 actor 與目標 account 不同。
- **測試步驟**：建立／修改／刪除 Project、Member、Task、Comment、User；檢查記錄。
- **預期結果**：ActorAccountId 來自 JWT current user；action/entity/time/必要前後快照正確；Task history actor 亦正確。
- **資料後置狀態**：每個成功異動有可追溯紀錄；失敗異動無成功稽核。
- **現有自動化覆蓋**：無。

#### TC-SQL-007 重複 Email DB constraint
- **類型與優先級**：Data integrity／P0；**測試層級**：SQL、API；**狀態**：Planned（GAP-010、OPEN-006、OPEN-015）
- **對應需求**：AUTH、DB；OPEN-015
- **前置條件**：已將 NormalizedEmail 改為 NOT NULL 並新增無 filter UNIQUE index；準備含重複 normalized Email 與 NULL 的 migration 前資料集。
- **測試步驟**：1. 以 NULL／重複髒資料執行 migration。2. 人工修正後重跑。3. 繞過 UserManager 並行插入相同 NormalizedEmail。4. 以大小寫不同但正規化後相同的 Email 註冊。5. 測試 NULL。
- **預期結果**：髒資料使 migration fail-fast，不自動合併、刪除或任意改寫帳號；人工修正後 migration 成功；NULL 被 NOT NULL 拒絕；重複被 UNIQUE 拒絕；API 競態固定回 409 `duplicate_email` 且含 `errors.email`，不得回 500。
- **資料後置狀態**：所有 Account 均有唯一且非 NULL 的 NormalizedEmail。
- **現有自動化覆蓋**：無。

#### TC-SQL-008 Refresh Token replacement self-FK
- **類型與優先級**：Data integrity／P0；**測試層級**：SQL、Service；**狀態**：Planned（GAP-011、OPEN-008）
- **對應需求**：AUTH、DB；GAP-011
- **前置條件**：已建立 `RefreshTokens.ReplacedByTokenId` nullable self-FK，DeleteBehavior=NoAction。
- **測試步驟**：1. 建立合法 A→B rotation chain。2. 嘗試寫入不存在的 replacement ID。3. 嘗試實體刪除仍被 A 參照的 B。4. 撤銷 token family 並檢查 chain。
- **預期結果**：合法 chain 可保存；不存在 ID 被 FK 拒絕；刪除被參照 Token 時由 DB 拒絕，不 cascade 刪除舊 Token；撤銷 family 不破壞參照完整性。
- **資料後置狀態**：只保留有效參照的 rotation chain；失敗操作完整 rollback。
- **現有自動化覆蓋**：無；目前欄位只有應用層邏輯參照，尚無 DB FK。

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

#### TC-SEC-API-005 Project scope 的 403 優先於資源 404
- **類型與優先級**：Security／P0；**測試層級**：Service、API；**狀態**：Planned（GAP-008）
- **對應需求**：API authorization；GAP-008
- **前置條件**：準備對 Project A 無權及有權的帳號；Project／Task／Comment／Member 各準備存在與不存在 ID。
- **測試步驟**：對所有 Project-scoped list/detail/create/update/delete endpoint 執行四格矩陣：無權＋存在、無權＋不存在、有權＋存在、有權＋不存在。
- **預期結果**：無權＋存在與無權＋不存在皆先回 403 `forbidden`；有權＋存在依操作成功；有權＋不存在才回 404 `not_found`；兩種無權回應不洩漏資源存在性差異。
- **資料後置狀態**：失敗請求不異動 Project、Task、Comment、Member、history 或 audit。
- **現有自動化覆蓋**：無；目前各 Service 的授權／查詢順序不完全一致，批次 Task 仍可能先因不存在回 404。

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
| AUTH | AUTH 系列 001–022 | ✓ | ✓ | ✓ | 部分；3 分鐘 Token、重寄／重放與登入 rate limit 皆為 Planned |
| US-1 | TASK 系列 001–005 | ✓ | ✓ | ✓ | Ready |
| US-2 | TASK 系列 006–018、TC-F-PREF-001 | ✓ | ✓ | ✓ | 部分；批次上限與 403 優先序 Planned |
| US-3 | TC-F-AUTH-014、TC-F-TASK-006 | ✓ | ✓ | ✓ | Ready |
| US-4 | TC-ST-TASK-003、TC-ERR-TASK-005、TC-F-TASK-021、CMT 系列 001–009 | ✓ | ✓ | ✓ | Ready |
| US-5 | REM 系列 001–012、TC-E-PRJ-011 | ✓ | ✓ | ✓ | Planned；時區、DST、補跑、重試及告警契約已決議 |
| US-6 | TC-F-TASK-008、TC-ERR-TASK-009 | ✓ | ✓ | ✓ | 部分；Description 契約對齊 Planned |
| US-7 | TASK 系列 010–014、TC-ERR-TASK-022 | ✓ | ✓ | ✓ | 部分；Description 契約對齊 Planned |
| US-8 | TC-F-TASK-019、TC-ST-TASK-020、TC-SQL-003 | ✓ | ✓ | ✓ | Ready |
| FLOW-PRJ | PRJ 系列 001–011 | ✓ | ✓ | ✓ | 部分；欄位邊界、Administrator Owner、TimeZoneId 與 Project 軟刪除 Planned |
| FLOW-MEMBER | MEMBER 系列 001–009 | ✓ | ✓ | ✓ | Ready |
| FLOW-USER | USER 系列 001–010 | ✓ | ✓ | ✓ | Ready；現行版本不含個資編輯 |
| PREF | PREF 系列 001–002 | ✓ | ✓ | ✓ | Ready |
| API／DB | SQL 系列 001–008、API 系列 001–005 | ✓ | ✓ | ✓ | 部分；403 優先序、Email UNIQUE 與 Refresh Token self-FK Planned |
| UI／UIMock | UI 系列 001–008 | ✓ | ✓ | ✓ | Ready；舊 PNG 差異依 `UIMock/README.md` |

## 6. 自動化覆蓋摘要與建議順序

### 6.1 目前可確認的自動化

- Backend Unit：註冊 validator、Bootstrap Admin policy、目前使用者 claims、Domain status／版本／token entity、EF model metadata、SMTP option。
- Backend Integration：CSRF、註冊 validation Problem Details、OpenAPI surface；實際 SQL Server 的單一角色與業務編號完整性（未設定 `PMW_TEST_SQL_CONNECTION` 時會略過）。
- Frontend Unit／Component：HTTP client 的 CSRF／Bearer／single-flight refresh／Problem Details、註冊導頁與欄位 mapping、Bootstrap Admin UI 保護、Project Role 複選、少量 Project detail 與 StatusBadge。
- Frontend E2E：登入、語言、mobile drawer、refresh restore、Admin 建立 Project 與 Task；需實際 Backend、SQL Server 與 `PMW_E2E_PASSWORD`。

### 6.2 建議自動化優先順序

1. P0 Auth API／Service：正常登入、`/auth/me`、refresh 各失敗分支、logout 冪等、Email resend 失敗與 Token 安全規則。
2. P0 API／Service 授權矩陣：Viewer、User assignee／non-assignee、ProjectManager、Administrator、Admin。
3. 批次 Task 的全有或全無 transaction、rowVersion 衝突與 audit/history rollback。
4. 角色／帳號狀態原子更新、最後一位 Admin 並行競態、token revocation。
5. Project member 查詢／加入／角色取代／Owner 移交／未完成 Task 阻擋。
6. Task／Comment 詳情、驗證、失敗回復、軟刪除、關聯保存與 query filters。
7. 前端清單 query、返回狀態、checkbox 權限、確認偏好及 403/409/422 UX。
8. BE-001 實作後，補齊 TC-ST-REM-001～012 與 TC-E-PRJ-011 的 clock-controlled、IANA timezone 與 SQL concurrency 測試。

## 7. 執行注意事項

- SQL 與 transaction 案例必須使用隔離的 SQL Server，不得用 EF InMemory 取代 relational constraint／rowversion／transaction 行為。
- Email 測試使用可控制的 gateway fake；只有 SMTP smoke test 才連外，且不得記錄完整驗證 token、密碼或 App Password。
- E2E 每次建立唯一資料並清理；不得依測試順序或既有正式資料。
- 涉及時間的案例固定 `TimeProvider`、UTC 與 Project IANA timezone；到期提醒以 Project 當地日期作冪等鍵，並依 OPEN-010 的 DST／當日補跑規則驗證。
- `Planned` 案例不是通過或失敗；它代表必須先完成需求決議或功能實作。
