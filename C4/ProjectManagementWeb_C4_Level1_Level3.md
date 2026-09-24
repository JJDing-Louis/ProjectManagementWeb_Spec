# Project Management Web：C4 Level 1～Level 3

> 圖表狀態：已於 2026-09-24 依目前 Vue 3 SPA、ASP.NET Core Controllers／Services、Hangfire、SQL Server、SMTP 與 Docker Compose 實作同步；本輪納入本人 Profile、使用者清單內聯管理及可搜尋成員下拉選單。

## Level 1：System Context Diagram

這一層只描述使用者、Project Management Web 系統，以及系統直接依賴的外部 Email 服務，不呈現 Vue、ASP.NET Core 或 SQL Server 等技術細節。

```mermaid
C4Context
    title Project Management Web - System Context Diagram（現行實作）

    Person(visitor, "訪客", "註冊帳號並完成 Email 驗證")
    Person(member, "專案成員", "維護個人名稱與電話，查看所屬專案，處理 Task Item 與留言")
    Person(administrator, "後台管理員", "管理專案、成員與 Task Item")
    Person(admin, "Admin", "管理使用者、系統角色及全部專案資料")

    System(projectManagementWeb, "Project Management Web", "公司內部的專案、成員、Task Item、留言與到期提醒管理系統")
    System_Ext(emailService, "Google Gmail SMTP", "寄送帳號驗證信與 Task 到期提醒")

    Rel(visitor, projectManagementWeb, "註冊、驗證 Email 與登入", "HTTPS")
    Rel(member, projectManagementWeb, "維護個人資料、查看專案並處理工作", "HTTPS")
    Rel(administrator, projectManagementWeb, "管理專案與工作", "HTTPS")
    Rel(admin, projectManagementWeb, "管理系統與權限", "HTTPS")
    Rel(projectManagementWeb, emailService, "寄送帳號驗證信與 Task 到期提醒", "SMTP")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Level 2：Container Diagram

C4 的 Container 是可執行應用程式或資料儲存的責任邊界，不等同 Docker Container。Project Management Web 在 MVP 階段由前端 SPA、後端 API 與關聯式資料庫組成；Email 服務位於系統邊界之外。

```mermaid
C4Container
    title Project Management Web - Container Diagram（現行實作）

    Person(systemUser, "系統使用者", "訪客、專案成員、後台管理員與 Admin")
    System_Ext(emailService, "Google Gmail SMTP", "寄送帳號驗證信與 Task 到期提醒")

    Container_Boundary(projectManagementWebBoundary, "Project Management Web") {
        Container(webApp, "前端網站", "Vue 3 SPA", "提供註冊、登入、個人資料、使用者管理、專案、Task Item、留言與偏好設定畫面")
        Container(api, "後端 API", "ASP.NET Core Web API + Hangfire", "執行身分驗證、授權、業務規則、交易與稽核，以及 Task 到期掃描與寄送 Worker")
        ContainerDb(database, "應用程式資料庫", "SQL Server", "保存使用者、角色、Session、專案、Task、留言、偏好、提醒狀態、Hangfire 工作與稽核")
    }

    Rel(systemUser, webApp, "操作系統", "HTTPS")
    Rel(webApp, api, "呼叫 RESTful API", "JSON/HTTPS")
    Rel(api, database, "查詢與寫入資料", "SQL/TLS")
    Rel(api, emailService, "寄送帳號驗證信與 Task 到期提醒", "SMTP/TLS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Level 3A：Frontend SPA Component Diagram

這張圖只展開目前 Vue 3 SPA。Component 依實際 Router、Views、Pinia stores、typed service contracts 與 HTTP adapters 分組；Email 驗證、Task 表單與批次狀態確認皆已實作並納入測試。

```mermaid
C4Component
    title Project Management Web - Frontend SPA Component Diagram（現行實作）

    Container(api, "後端 API", "ASP.NET Core Web API", "驗證權限並執行業務流程")

    Container_Boundary(webBoundary, "前端網站（Vue 3 SPA）") {
        Component(router, "Router 與 Route Guards", "Vue Router", "依登入狀態與角色載入頁面；僅負責導覽，不取代後端授權")
        Component(authViews, "帳號與驗證畫面", "Vue Views", "SignInView、SignUpView、VerifyEmailView 與 ResendVerificationView")
        Component(userViews, "使用者、個人資料與偏好畫面", "Vue Views", "UserList 內聯管理角色與狀態、UserDetail 唯讀個資與管理表單、Settings 本人名稱電話與偏好")
        Component(projectViews, "專案管理畫面", "Vue Views", "ProjectList、ProjectDetail、ProjectForm 與可搜尋成員下拉選單")
        Component(taskViews, "Task 與留言畫面", "Vue Views", "TaskList、TaskDetail 與 TaskForm；批次確認現由 TaskList 處理")
        Component(clientState, "狀態與 API Client", "Pinia / HTTP Client", "保存記憶體 Access Token 與目前使用者，統一處理 CSRF、single-flight refresh、DTO mapping、HTTP 錯誤及 API 呼叫")
    }

    Rel(router, clientState, "讀取登入狀態")
    Rel(authViews, clientState, "帳號 API")
    Rel(userViews, clientState, "使用者、本人 Profile 與偏好 API")
    Rel(projectViews, clientState, "專案 API")
    Rel(taskViews, clientState, "Task API")
    Rel(clientState, api, "呼叫 RESTful API", "JSON/HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Level 3B：Backend API Controller Component Diagram

這張圖只展開 ASP.NET Core Web API。Controller 依前端畫面所需的使用案例分組，並把業務流程留在 Application Service，避免 Controller 直接存取資料庫或堆疊規則。

```mermaid
C4Component
    title Project Management Web - Backend API Component Diagram（現行實作）

    Container_Boundary(apiBoundary, "後端 API（ASP.NET Core Web API）") {

        Boundary(controllerLayer, "Controller Layer", "Presentation") {
            Component(authController, "Auth / Security Controllers", "ASP.NET Core Controller", "AuthController、SecurityController")
            Component(userControllers, "User / Role Controllers", "ASP.NET Core Controller", "UsersController、RolesController；偏好由 UsersController 提供")
            Component(projectControllers, "Project Controller", "ASP.NET Core Controller", "ProjectsController；同時提供 Project Members API")
            Component(taskControllers, "Task Controllers", "ASP.NET Core Controller", "TaskItemsController、CommentsController")
        }

        Boundary(applicationLayer, "Application / Service Layer", "Application") {
            Component(identityService, "Identity 與 User Service", "C#", "執行帳號、Session、本人名稱電話、角色與狀態原子異動、Bootstrap Admin 保護、登入雙維度限流、3 分鐘一次性 Email Token、重寄限流與偏好規則")
            Component(projectService, "Project Service", "C#", "執行專案、Owner、成員、角色與版本衝突規則")
            Component(taskService, "Task 與 Comment Service", "C#", "執行任意狀態更新、指派、批次交易、軟刪除與留言規則")
            Component(reminderScanner, "Task Reminder Scanner", "Hangfire Recurring Job", "依 Project 當地日期於 08:00 後掃描七日視窗，建立不重複的提醒工作")
            Component(reminderSender, "Task Reminder Sender", "Hangfire Recurring Job", "原子 claim、寄送前重查、單封寄送、重試、寄送結果與安全告警記錄")
        }

        Boundary(infrastructureLayer, "Infrastructure Layer", "Infrastructure") {
            Component(persistence, "資料存取與交易", "Repositories / Unit of Work", "封裝查詢、Token 最新版與一次性狀態、登入／重寄 SQL 共享限流、交易及稽核寫入")
            Component(emailGateway, "Email Gateway", "SMTP Adapter", "隔離驗證信與 Task 到期提醒的 Gmail SMTP 呼叫，回傳 provider response ID")
        }
    }

    ContainerDb(database, "應用程式資料庫", "SQL Server", "保存系統與稽核資料")

    System_Ext(emailService, "Google Gmail SMTP", "寄送帳號驗證信與 Task 到期提醒")

    Rel(authController, identityService, "執行帳號使用案例")
    Rel(userControllers, identityService, "執行使用者使用案例")
    Rel(projectControllers, projectService, "執行專案使用案例")
    Rel(taskControllers, taskService, "執行 Task 使用案例")

    Rel(identityService, persistence, "查詢與保存")
    Rel(projectService, persistence, "查詢與交易")
    Rel(taskService, persistence, "查詢與交易")
    Rel(reminderScanner, persistence, "掃描 Task 並建立 Project 日期與 Task 收件人唯一提醒紀錄")
    Rel(reminderScanner, reminderSender, "由 SQL reminder 狀態交付單封寄送工作")
    Rel(reminderSender, persistence, "原子 claim、更新寄送、取消、重試與 Failed 告警狀態")

    Rel(identityService, emailGateway, "要求寄送驗證信")
    Rel(reminderSender, emailGateway, "以 reminder ID idempotency key 寄送 Task 到期提醒")

    Rel(persistence, database, "執行參數化查詢與交易", "SQL/TLS")
    Rel(emailGateway, emailService, "寄送信件", "SMTP/TLS")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## Level 3C：Frontend Component 與 Controller 對應圖

標準 C4 Component Diagram 一次只展開一個 Container。下圖是為了讓開發者快速核對畫面與 Controller 責任而補充的跨 Container 對應圖，不取代 Level 3A 或 Level 3B。

```mermaid
C4Component
    title Project Management Web - Frontend Component to Controller Mapping（現行實作）

    Container_Boundary(webBoundary, "前端網站（Vue 3 SPA）") {
        Component(authViews, "帳號與驗證畫面", "Vue Views", "SignInView、SignUpView、VerifyEmailView、ResendVerificationView")
        Component(userViews, "使用者、個人資料與偏好畫面", "Vue Views", "UserList、UserDetail、Settings")
        Component(projectViews, "專案管理畫面", "Vue Views", "ProjectList、ProjectDetail、ProjectForm、SearchableSelectDropdown")
        Component(taskViews, "Task 與留言畫面", "Vue Views", "TaskList、TaskDetail、TaskForm")
    }

    Container_Boundary(apiBoundary, "後端 API（ASP.NET Core Web API）") {
        Component(authController, "AuthController / SecurityController", "Controllers", "帳號、Session、Token、Email 驗證與 CSRF token")
        Component(userControllers, "UsersController / RolesController", "Controllers", "使用者清單與詳情、本人 Profile、系統角色、帳號狀態與個人偏好")
        Component(projectControllers, "ProjectsController", "Controller", "專案、Owner、成員與專案角色")
        Component(taskControllers, "TaskItemsController / CommentsController", "Controllers", "Task、批次狀態、軟刪除與留言")
    }

    Rel(authViews, authController, "註冊、登入、驗證與登出 API", "JSON/HTTPS")
    Rel(userViews, userControllers, "使用者查詢、本人 Profile、角色、狀態與偏好 API", "JSON/HTTPS")
    Rel(projectViews, projectControllers, "專案與成員管理 API", "JSON/HTTPS")
    Rel(taskViews, taskControllers, "Task、批次狀態與留言 API", "JSON/HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="2")
```

## 設計邊界

- Level 1 不呈現框架、資料庫或內部元件。
- Level 2 不把頁面、Controller、Service、Repository 或資料表誤當成 Container。
- Level 3A 與 Level 3B 各自只展開一個 Container；Level 3C 是為了核對畫面與 Controller 而提供的跨 Container 補充圖。
- 畫面與 Controller 的對應代表功能責任，不表示 Vue View 會略過 API Client 或直接呼叫 C# 類別。
- Controller 名稱與責任已依目前實際 Route 與類別校正；新增 Controller 或拆分 route 時必須同步此圖。
- Component 表示責任單元，不保證每個元件只會對應一個 Class 或一個檔案。
- 前端的按鈕顯示與 Disabled 狀態只改善操作體驗，所有授權、rowVersion 與目標狀態 enum 值仍由後端重新驗證；Project／Task 的四種合法狀態可任意互轉並包含相同狀態更新。
- Task 批次更新由應用服務建立單一交易邊界，任一項失敗即整批不更新。
- Project 與 Task 更新透過版本欄位處理 Optimistic Concurrency，衝突時回傳 HTTP 409。
- Email 驗證與 Task 到期提醒均為現行 runtime 功能。提醒由 Hangfire Scanner／Sender、SQL 唯一紀錄與原子 claim、5／15／60 分鐘 retry，以及 DB／安全結構化 Log 告警組成；Hangfire schema 由 migrator 初始化。
