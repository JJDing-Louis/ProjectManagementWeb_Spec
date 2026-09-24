# 刪除 Task Item（後台使用者）

> 實作同步：2026-09-24。對應 `DELETE /api/v1/projects/{projectId}/task-items/{taskId}?rowVersion=...`，由 `TaskItemsController` 與 `TaskService` 執行。

```mermaid
flowchart TB
    deleteStart([Task Item List]) --> chooseDeletion[選擇要刪除的 Task]
    chooseDeletion --> showDeleteWarning[顯示 Task 標題與不可復原提示]
    showDeleteWarning --> confirmDelete{確認刪除？}
    confirmDelete -->|否| deleteStart
    confirmDelete -->|是| authorizeDelete{後端授權通過？}
    authorizeDelete -->|否| forbiddenDelete[顯示權限不足]
    authorizeDelete -->|是| softDelete[軟刪除 Task]
    softDelete --> deleteSucceeded{刪除成功？}
    deleteSucceeded -->|否| keepTask[保留原畫面並顯示錯誤]
    deleteSucceeded -->|是| preserveRelated[(保留留言與稽核紀錄)]
    preserveRelated --> deleteFinished([返回清單並顯示成功訊息])
```

MVP 採軟刪除，因此一般清單不再顯示該 Task，但留言與稽核紀錄仍須保留，不能使用未經評估的 Cascade Delete 一併清除。
