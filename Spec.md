# 開發規格

本索引依 2026-09-24 的目前實作整理。規格判讀順序以 `UserStory.md`、相關 Flowchart、C4、Schema 與 StaticData 為主；實際 API／資料庫契約仍需和 Backend source、EF Core migrations 及自動化測試一起核對。

目前程式碼盤點結果為 40 個 `/api/v1` Controller actions 與 26 張 EF Application tables；Frontend routes 包含帳號、專案、Task、使用者、個人設定、403 與 404 畫面。數量只用來協助偵測文件漂移，實際契約仍以 route attributes、request／response contracts 與 migrations 為準。

## UserStory
- UserStory.md

## UIMock(UI草圖)
- README.md (2026-09-24 實際擷取環境、路由與畫面索引)
- SignIn.png (登入畫面)
- SignUp.png (註冊畫面)
- VerifyEmail.png、VerifyEmailFailure.png (驗證信成功提示與寄送失敗提示)
- ResendVerification.png (重新寄送驗證信)
- UserList.png (使用者清單)
- UserDetail.png (使用者詳情與帳號管理)
- UserSetting.png (本人名稱、電話與操作偏好)
- ProjectList.png (專案清單)
- ProjectForm.png (專案表單)
- ProjectDetail.png (專案詳情與成員管理)
- TaskItemList.png (Task 清單)
- TaskItemForm.png (Task 表單)
- TaskItemDetail.png (Task 詳情與留言)
- Forbidden.png、NotFound.png (403／404 狀態頁)

## C4 Diagram(C4圖)
- ProjectManagementWeb_Level1_Context.mmd                      
- ProjectManagementWeb_Level2_Container.mmd                    
- ProjectManagementWeb_Level3A_Frontend_Component.mmd  
- ProjectManagementWeb_Level3B_Backend_Component.mmd        
- ProjectManagementWeb_Level3C_Frontend_Controller_Mapping.mmd
- ProjectManagementWeb_C4_Level1_Level3.md

## Flowchart(流程圖)
- E-mail 任務到期提醒.md                        
- 從詳細頁修改 Task(前台使用者).md              
- 管理系統角色與帳號狀態.md
- 管理個人資料與偏好.md
- Task Item 留言.md                             
- 批次修改 Task 狀態(前台使用者).md             
- 註冊、Email 驗證與登入.md
- 刪除 Task Item(後台使用者).md                 
- 新增與修改 Task Item(後台使用者).md
- 建立與修改專案.md                             
- 管理專案成員.md

## Schema(資料庫設計)
- Schema.md

## StaticData(靜態資料)
- StaticData.md

## Implementation Status(實作狀態)
- ImplementationBacklog.md（目前已完成項目、剩餘技術注意事項與對應程式／migration／測試）

## Test Cases And Logs(測試案例與日誌)
- TestCases/ProjectManagementWeb-TestCases.md（118 個案例、實測覆蓋矩陣與時間戳）
- TestCases/TestLogs/2026-09-16-第一次TDD測試日誌.md（第一次完整 TDD 回歸摘要）
- TestCases/TestLogs/2026-09-24-規格同步與UI擷取日誌.md（本輪程式碼盤點、文件驗證與實際畫面擷取）
