# My Work Item：C4 Level 1～Level 3

> 圖表狀態：設計草稿。實作完成後，仍須依實際程式碼、部署方式與外部服務重新核對。

## Level 1：System Context Diagram

這一層只描述使用者、My Work Item 系統，以及系統直接依賴的外部 Email 服務，不呈現 Vue、ASP.NET Core 或 SQL Server 等技術細節。

```mermaid
C4Context
    title Project Management Web - System Context Diagram（設計草稿）

    Person(visitor, "訪客", "註冊帳號並完成 Email 驗證")
    Person(member, "專案成員", "查看所屬專案，處理 Task Item 與留言")
    Person(administrator, "後台管理員", "管理專案、成員與 Task Item")
    Person(admin, "Admin", "管理使用者、系統角色及全部專案資料")

    System(myWorkItem, "My Work Item", "公司內部的專案、成員、Task Item 與留言管理系統")
    System_Ext(emailService, "Google Gmail SMTP", "寄送帳號驗證信")

    Rel(visitor, myWorkItem, "註冊、驗證 Email 與登入", "HTTPS")
    Rel(member, myWorkItem, "查看專案並處理工作", "HTTPS")
    Rel(administrator, myWorkItem, "管理專案與工作", "HTTPS")
    Rel(admin, myWorkItem, "管理系統與權限", "HTTPS")
    Rel(myWorkItem, emailService, "寄送帳號驗證信", "SMTP")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Level 2：Container Diagram

C4 的 Container 是可執行應用程式或資料儲存的責任邊界，不等同 Docker Container。My Work Item 在 MVP 階段由前端 SPA、後端 API 與關聯式資料庫組成；Email 服務位於系統邊界之外。

```mermaid
C4Container
    title Project Management Web - Container Diagram（設計草稿）

    Person(systemUser, "系統使用者", "訪客、專案成員、後台管理員與 Admin")
    System_Ext(emailService, "Google Gmail SMTP", "寄送帳號驗證信")

    Container_Boundary(myWorkItemBoundary, "My Work Item") {
        Container(webApp, "前端網站", "Vue 3 SPA", "提供註冊、登入、使用者、專案、Task Item、留言與偏好設定畫面")
        Container(api, "後端 API", "ASP.NET Core Web API", "執行身分驗證、授權、輸入驗證、業務規則、交易與稽核")
        ContainerDb(database, "應用程式資料庫", "SQL Server", "保存使用者、角色、登入 Session、專案、成員、Task Item、留言、偏好與稽核資料")
    }

    Rel(systemUser, webApp, "操作系統", "HTTPS")
    Rel(webApp, api, "呼叫 RESTful API", "JSON/HTTPS")
    Rel(api, database, "查詢與寫入資料", "SQL/TLS")
    Rel(api, emailService, "寄送帳號驗證信", "SMTP/TLS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Level 3A：Frontend SPA Component Diagram

這張圖只展開 Vue 3 SPA。畫面 Component 依 Day6 的八張草圖分組；Email 驗證、Task 新增表單與批次狀態確認雖然尚未有草圖，但已由 Day3 的 User Story 明確定義，因此一併納入規劃。

```mermaid
C4Component
    title Project Management Web - Frontend SPA Component Diagram（設計草稿）

    Container(api, "後端 API", "ASP.NET Core Web API", "驗證權限並執行業務流程")

    Container_Boundary(webBoundary, "前端網站（Vue 3 SPA）") {
        Component(router, "Router 與 Route Guards", "Vue Router", "依登入狀態與角色載入頁面；僅負責導覽，不取代後端授權")
        Component(authViews, "帳號與驗證畫面", "Vue Views", "SignIn、SignUp、EmailVerification 與 ResendVerification")
        Component(userViews, "使用者管理畫面", "Vue Views", "UserList 與 UserSetting")
        Component(projectViews, "專案管理畫面", "Vue Views", "ProjectList 與 ProjectDetail")
        Component(taskViews, "Task 與留言畫面", "Vue Views", "TaskItemList、TaskItemDetail、TaskItemForm 與 BatchStatusDialog")
        Component(clientState, "狀態與 API Client", "Pinia / HTTP Client", "保存登入狀態與查詢條件，統一處理 Token、HTTP 錯誤及 API 呼叫")
    }

    Rel(router, clientState, "讀取登入狀態")
    Rel(authViews, clientState, "帳號 API")
    Rel(userViews, clientState, "使用者 API")
    Rel(projectViews, clientState, "專案 API")
    Rel(taskViews, clientState, "Task API")
    Rel(clientState, api, "呼叫 RESTful API", "JSON/HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Level 3B：Backend API Controller Component Diagram

這張圖只展開 ASP.NET Core Web API。Controller 依前端畫面所需的使用案例分組，並把業務流程留在 Application Service，避免 Controller 直接存取資料庫或堆疊規則。

```mermaid
C4Component
    title Project Management Web - Backend API Component Diagram（設計草稿）

    Container_Boundary(apiBoundary, "後端 API（ASP.NET Core Web API）") {

        Boundary(controllerLayer, "Controller Layer", "Presentation") {
            Component(authController, "Account Controller", "ASP.NET Core Controller", "處理註冊、登入、登出、Token 更新、Email 驗證與重新寄送")
            Component(userControllers, "User Controllers", "ASP.NET Core Controller", "UsersController、UserPreferencesController")
            Component(projectControllers, "Project Controllers", "ASP.NET Core Controller", "ProjectsController、ProjectMembersController")
            Component(taskControllers, "Task Controllers", "ASP.NET Core Controller", "TaskItemsController、CommentsController")
        }

        Boundary(applicationLayer, "Application / Service Layer", "Application") {
            Component(identityService, "Identity 與 User Service", "C#", "執行帳號、Session、Token、角色、Email 驗證與偏好規則")
            Component(projectService, "Project Service", "C#", "執行專案、Owner、成員、角色與版本衝突規則")
            Component(taskService, "Task 與 Comment Service", "C#", "執行狀態轉換、指派、批次交易、軟刪除與留言規則")
        }

        Boundary(infrastructureLayer, "Infrastructure Layer", "Infrastructure") {
            Component(persistence, "資料存取與交易", "Repositories / Unit of Work", "封裝查詢、分頁、Optimistic Concurrency、交易與稽核寫入")
            Component(emailGateway, "Email Gateway", "SMTP Adapter", "隔離驗證信內容與 Gmail SMTP 呼叫")
        }
    }

    ContainerDb(database, "應用程式資料庫", "SQL Server", "保存系統與稽核資料")

    System_Ext(emailService, "Google Gmail SMTP", "寄送帳號驗證信")

    Rel(authController, identityService, "執行帳號使用案例")
    Rel(userControllers, identityService, "執行使用者使用案例")
    Rel(projectControllers, projectService, "執行專案使用案例")
    Rel(taskControllers, taskService, "執行 Task 使用案例")

    Rel(identityService, persistence, "查詢與保存")
    Rel(projectService, persistence, "查詢與交易")
    Rel(taskService, persistence, "查詢與交易")

    Rel(identityService, emailGateway, "要求寄送驗證信")

    Rel(persistence, database, "執行參數化查詢與交易", "SQL/TLS")
    Rel(emailGateway, emailService, "寄送信件", "SMTP/TLS")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## Level 3C：Frontend Component 與 Controller 對應圖

標準 C4 Component Diagram 一次只展開一個 Container。下圖是為了讓開發者快速核對畫面與 Controller 責任而補充的跨 Container 對應圖，不取代 Level 3A 或 Level 3B。

```mermaid
C4Component
    title Project Management Web - Frontend Component to Controller Mapping（設計草稿）

    Container_Boundary(webBoundary, "前端網站（Vue 3 SPA）") {
        Component(authViews, "帳號與驗證畫面", "Vue Views", "SignIn、SignUp、EmailVerification、ResendVerification")
        Component(userViews, "使用者管理畫面", "Vue Views", "UserList、UserSetting")
        Component(projectViews, "專案管理畫面", "Vue Views", "ProjectList、ProjectDetail")
        Component(taskViews, "Task 與留言畫面", "Vue Views", "TaskItemList、TaskItemDetail、TaskItemForm、BatchStatusDialog")
    }

    Container_Boundary(apiBoundary, "後端 API（ASP.NET Core Web API）") {
        Component(authController, "AuthController", "Controller", "帳號、Session、Token 與 Email 驗證")
        Component(userControllers, "UsersController / UserPreferencesController", "Controllers", "使用者、系統角色與個人偏好")
        Component(projectControllers, "ProjectsController / ProjectMembersController", "Controllers", "專案、Owner、成員與專案角色")
        Component(taskControllers, "TaskItemsController / CommentsController", "Controllers", "Task、批次狀態、軟刪除與留言")
    }

    Rel(authViews, authController, "註冊、登入、驗證與登出 API", "JSON/HTTPS")
    Rel(userViews, userControllers, "使用者查詢、角色與偏好 API", "JSON/HTTPS")
    Rel(projectViews, projectControllers, "專案與成員管理 API", "JSON/HTTPS")
    Rel(taskViews, taskControllers, "Task、批次狀態與留言 API", "JSON/HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="2")
```

## 設計邊界

- Level 1 不呈現框架、資料庫或內部元件。
- Level 2 不把頁面、Controller、Service、Repository 或資料表誤當成 Container。
- Level 3A 與 Level 3B 各自只展開一個 Container；Level 3C 是為了核對畫面與 Controller 而提供的跨 Container 補充圖。
- 畫面與 Controller 的對應代表功能責任，不表示 Vue View 會略過 API Client 或直接呼叫 C# 類別。
- Controller 名稱是依目前 User Story 與 UI 草圖提出的設計命名；後端實作完成後，須再依實際 Route 與類別名稱回頭校正。
- Component 表示責任單元，不保證每個元件只會對應一個 Class 或一個檔案。
- 前端的按鈕顯示與 Disabled 狀態只改善操作體驗，所有授權與狀態轉換仍由後端重新驗證。
- Task 批次更新由應用服務建立單一交易邊界，任一項失敗即整批不更新。
- Project 與 Task 更新透過版本欄位處理 Optimistic Concurrency，衝突時回傳 HTTP 409。
- Email 僅用於 Day3 明確要求的帳號驗證；本圖未自行加入 Task 到期提醒或背景排程。
