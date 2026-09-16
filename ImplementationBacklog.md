# 實作待辦

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
- 對應自動化：`ReminderServiceTests` 8 個合併案例，2026-09-16 完整 Integration Passed 98／Failed 0／Skipped 0；隔離 Compose 啟動與 Playwright Passed 22／Failed 0／Skipped 0。
