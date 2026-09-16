# UI 草圖契約說明

`UIMock/` 內的 PNG 為早期畫面草圖，保留用來說明版面概念。草圖中的欄位、按鈕或互動若與本文不同，以本文、`UserStory.md` 與 Flowchart 的文字契約為準。

## 已依現行實作校正的差異

### SignUp.png

- 正式註冊欄位為帳號、顯示名稱、Email、密碼與確認密碼，全部為必填。
- 註冊後為 `Viewer`；Email 未驗證時仍可登入，但只能取得 `Viewer` 能力。
- Email 驗證完成後不會自動晉升角色。

### ProjectDetail.png

- 每位專案成員可同時擁有一個或多個 Project Role，畫面使用複選元件。
- 新增或修改成員時必須保留至少一個有效 Project Role；修改時完整取代原角色集合。

### ProjectList.png

- 清單提供單一搜尋欄，同時模糊查詢 Project Code、Name 與 Description，另提供 Status 篩選。
- 不提供各欄位獨立啟用的搜尋欄，也不提供 Owner 篩選。

### TaskItemList.png

- checkbox 只用於選取目前頁面中可修改狀態的 Task，不支援批次刪除。
- 每列的「刪除」是具有後台權限使用者的單筆軟刪除，與 checkbox 選取無關。
- 草圖中的 `Delete` 批次操作不屬於現行需求。`ClearAll` 若顯示，只能表示清除目前頁面的 checkbox 選取，不得刪除資料。
- 批次目標狀態進入頁面時預設為 `InProgress`；尚未選取 Task 時確認按鈕為 Disabled。

### Project 表單

- Project 名稱為必填，trim 後長度為 1–200 個字元。
- Description 為選填，trim 後最多 4000 個字元。
- Owner 為必填；候選清單只顯示已啟用、Email 已驗證且系統角色恰為 `Administrator` 的帳號。修改時，新 Owner 還必須已是該 Project 成員。
- IANA `TimeZoneId` 為必填；新 Project 必須由使用者明確指定合法值，不得以系統預設代填。

### Task Item 表單與 TaskItemDetail.png

- Task Description 為選填，若有值則 trim 後最多 8000 個字元。
- Task Detail 顯示詳細資料與留言。具備修改權限者按下「編輯」後進入 `/admin/projects/{projectId}/task-items/{taskId}/edit`，不在詳情頁以 Confirm／Cancel 直接修改 Task 欄位。

### UserSetting.png

- `/settings` 只管理語言與「略過批次狀態確認視窗」偏好。
- 帳號、顯示名稱、Email 及驗證狀態在 `/users/{id}` 顯示，現行版本不提供這些欄位的編輯。
- 系統角色與帳號啟用狀態由 Admin 在 `/users/{id}` 管理；Project Role 在各 Project Detail 的成員管理區調整。
