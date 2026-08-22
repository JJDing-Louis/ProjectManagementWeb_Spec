# 靜態資料表

## Role
| RoleID | Name          | Desc    |
| ------ | ------------- | ------- |
| 0      | Admin         | 最高管理者   |
| 1      | User          | 一般前台使用者 |
| 2      | Administrator | 後台管理員   |
| 3      | Viewer        | 觀察者     |

## ProjectRole
| ProjectRoleID     | Name              | Desc   |
| ----------------- | ----------------- | ------ |
| ProjectManager    | ProjectManager    | 專案經理   |
| FrontendDeveloper | FrontendDeveloper | 前端開發人員 |
| BackendDeveloper  | BackendDeveloper  | 後端開發人員 |
| SystemAnalyst     | SystemAnalyst     | 系統分析師  |
| Member            | Member            | 組員     |
## TaskItemStatus
| WorkItemStatusID | Name       | Desc |
| ---------------- | ---------- | ---- |
| Pending          | Pending    | 尚未開始 |
| InProgress       | InProgress | 處理中  |
| Blocked          | Blocked    | 受阻   |
| Completed        | Completed  | 已完成  |

## TParameter

| ActionID    | Name        | Value          | Desc     |
| ----------- | ----------- | -------------- | -------- |
| SystemEmail | SystemEmail | test@gmail.com | 系統E-mail |



## Action
|ActionID|Name|Desc|
|---|---|---|
|INSERT|INSERT|新增|
|UPDATE|UPDATE|更新|
|DELETE|DELETE|刪除|
