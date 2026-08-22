## E-mail 任務到期提醒

這個功能分成「找出需要提醒的 Task」與「寄送單封提醒信」兩段。兩段分開後，即使 Email 服務暫時失敗，也不必重新掃描全部 Task。

### 掃描到期任務

```mermaid
flowchart TB
    reminderStart([Hangfire 觸發掃描排程]) --> calculateWindow[依系統時區計算提醒範圍]
    calculateWindow --> queryTasks[(查詢未完成且即將到期的 Task)]
    queryTasks --> hasReminderTasks{有符合條件的 Task？}
    hasReminderTasks -->|否| reminderSummary([記錄執行摘要並結束])
    hasReminderTasks -->|是| selectReminderTask[逐筆取得 Task 與指派對象]
    selectReminderTask --> recipientValid{帳號啟用且 Email 已驗證？}
    recipientValid -->|否| recordSkipped[記錄略過原因]
    recipientValid -->|是| createReminder{原子建立唯一提醒紀錄？}
    createReminder -->|否| recordDuplicate[略過已建立的提醒]
    createReminder -->|是| markPending[(標記為 Pending)]
    recordSkipped --> nextReminder[處理下一筆]
    recordDuplicate --> nextReminder
    markPending --> nextReminder
    nextReminder --> hasNextReminder{還有下一筆？}
    hasNextReminder -->|是| selectReminderTask
    hasNextReminder -->|否| reminderSummary
```

### 寄送單封提醒信

```mermaid
flowchart TB
    sendJobStart([Hangfire 取得 Pending 或 Retry 紀錄]) --> claimSend{原子取得寄送權？}
    claimSend -->|否| sendJobFinished([略過並結束])
    claimSend -->|是| recheckTask{Task 仍未完成且在提醒範圍？}
    recheckTask -->|否| cancelReminder[(標記為 Cancelled)]
    recheckTask -->|是| composeReminder[產生含期限與 Task 連結的信件]
    composeReminder --> sendReminder[呼叫 Email 服務]
    sendReminder --> reminderSent{寄送成功？}
    reminderSent -->|是| markReminderSent[(記錄 SentAt 與服務回應編號)]
    reminderSent -->|否| updateAttempt[(記錄錯誤與重試次數)]
    updateAttempt --> retryLimit{已達重試上限？}
    retryLimit -->|否| scheduleRetry[(標記為 Retry 並設定下次時間)]
    retryLimit -->|是| markReminderFailed[標記失敗並留下告警紀錄]
    cancelReminder --> sendJobEnd([結束寄送工作])
    markReminderSent --> sendJobEnd
    scheduleRetry --> sendJobEnd
    markReminderFailed --> sendJobEnd
```

「即將到期」要有明確且可設定的範圍，例如以系統時區判斷 `現在時間 <= 交付期限 <= 提醒截止時間`。查詢條件至少包含 Task 尚未完成、指派對象帳號仍啟用，以及 Email 已完成驗證。

為了避免排程重複執行或多台主機同時處理，寄送紀錄應以 Task、收件人與提醒規則建立唯一限制，並以原子操作取得寄送權。寄送前還要重新讀取 Task，避免使用者剛完成任務，系統卻仍寄出舊提醒。

Email 是外部服務；若服務已收信，但程式在寫回成功紀錄前中斷，重試仍可能造成極少數重複信件。若供應商支援 Idempotency Key，應使用寄送紀錄編號作為 Key；否則要透過寄送回應編號、有限次重試及告警紀錄降低風險。