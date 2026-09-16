# 開發規格

本索引依 2026-09-17 的目前實作整理。規格判讀順序以 `UserStory.md`、相關 Flowchart、C4、Schema 與 StaticData 為主；實際 API／資料庫契約仍需和 Backend source、EF Core migrations 及自動化測試一起核對。

## UserStory
- UserStory.md

## UIMock(UI草圖)
- README.md (草圖與現行契約差異；PNG 與文字衝突時以本文、User Story 與 Flowchart 為準)
- SignIn.png (登入畫面)
- SignUp.png (註冊畫面)
- UserList.png (使用者清單)
- UserSetting.png (使用者設定)
- ProjectList.png (專案清單)
- ProjectDetail.png (專案設定)           
- TaskItemList.png (任務清單)   
- TaskItemDetail.png (任務設定) 

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
- ImplementationBacklog.md（目前已完成項目與對應程式／migration／測試）

## Test Cases And Logs(測試案例與日誌)
- TestCases/ProjectManagementWeb-TestCases.md（118 個案例、實測覆蓋矩陣與時間戳）
- TestCases/TestLogs/2026-09-16-第一次TDD測試日誌.md（第一次完整 TDD 回歸摘要）
