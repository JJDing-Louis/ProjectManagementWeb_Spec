# GitFlow 開發與發版規範（Spec）

本文件適用於 `ProjectManagementWeb_Spec`。本 repository 保存 User Story、Flowchart、Schema 設計、Static Data、C4、UI Mock 與測試案例，不含可部署的應用程式。Backend 與 Frontend 是獨立 Git repository，各自建立分支、PR 與 tag。

## Branch Strategy

| 分支        | 用途                         | 建立來源                            | 合併目標                   |
| ----------- | ---------------------------- | ----------------------------------- | -------------------------- |
| `main`      | 已核准、供正式版本參照的規格 | Release／Hotfix PR                  | 不在此直接編輯             |
| `develop`   | 下一版規格整合               | Feature／Bugfix／Release／Hotfix PR | Release 的建立來源         |
| `feature/*` | 新需求、規格擴充或一般重整   | `develop`                           | `develop`                  |
| `bugfix/*`  | 一般規格錯誤修正             | `develop`                           | `develop`                  |
| `release/*` | 待核准的規格版本             | `develop`                           | `main`，再回合併 `develop` |
| `hotfix/*`  | 已發版規格的緊急錯誤修正     | `main`                              | `main`，再回合併 `develop` |

`main`、`develop` 只接受 PR，不直接 push 或 force push。`feature`／`bugfix` 合併至 `develop`，`release`／`hotfix` 合併至 `main`，都必須使用 PR；`release`／`hotfix` 回合併 `develop` 也使用 PR。PR 合併後才更新目標分支，不改寫既有 history，也不以刪除舊分支作為導入條件。

導入狀態（2026-09-27）：Spec 既有遠端只有 `main`；導入時先從 `main` 建立 `develop`，經 repository 維護者確認後發布並設定保護規則。在遠端 `develop` 尚未建立前，不能對它開 PR。每次工作都重新確認實際 branch 與 remote 狀態。

## Branch Naming

| 類型             | 格式                                | 範例                        |
| ---------------- | ----------------------------------- | --------------------------- |
| 新需求／一般重整 | `feature/<ticket-id>-<description>` | `feature/123-project-roles` |
| 一般規格錯誤     | `bugfix/<ticket-id>-<description>`  | `bugfix/456-task-status`    |
| Release          | `release/<version>`                 | `release/1.2.0`             |
| 緊急規格修正     | `hotfix/<version>-<description>`    | `hotfix/1.2.1-role-rule`    |

`ticket-id` 使用議題編號；沒有議題系統時，使用可追溯的工作代碼（例如日期 `20260927`），並在 PR 連結需求。`description` 使用小寫英文字母、數字與連字號。一般文件重整歸 `feature/*`；已發版規格若含造成正式版錯誤的關鍵敘述，才使用 `hotfix/*`。

## Commit Convention

採用 Conventional Commits：`<type>(<scope>): <description>`。`type` 限 `feat`、`fix`、`refactor`、`docs`、`test`、`chore`、`build`、`ci`、`perf`、`style`、`revert`；`scope` 使用 `story`、`flow`、`schema`、`c4`、`ui`、`tests`、`git` 等穩定範圍。描述與 commit body 使用繁體中文。

```text
docs(story): 補充專案成員驗收條件
fix(schema): 修正成員角色關係說明
docs(git): 補充發版與回復流程
```

若規格對 API／資料契約形成不相容變更，commit body 註明 `BREAKING CHANGE: <繁體中文說明>`，並在 PR 列出 Backend／Frontend 的遷移影響。舊提交維持原狀；規範從新提交開始適用。Squash Merge 的最終 commit 也必須符合此格式。

## Pull Request

使用 [PR 範本](../.github/PULL_REQUEST_TEMPLATE.md) 填寫 Summary、Changes、Test、Risk、Rollback。Unit、Integration、Manual Test 分別填寫實際結果或「不適用／未執行」與原因；文件檢查應包含連結、圖片、圖表來源、術語、User Story 與實作契約的一致性。涉及 Backend／Frontend 的變更，各庫分別送 PR 並互相連結。

- `feature/*`／`bugfix/*` → `develop`：預設 Squash Merge，產生一個 Conventional Commit。
- `release/*`／`hotfix/*` → `main`：使用 Merge Commit 保留完整提交與分支脈絡；回合併 `develop` 也保留完整提交。若 GitHub 無法選擇 Merge Commit，先調整 repository 設定。
- 審查者確認需求來源、版本範圍、實作差異、連結及回復方式後再合併。

## Release Flow

1. 確認 `develop` 包含本版已核准的規格與必要的正式版同步變更，從 `develop` 建立 `release/x.y.z`。
2. Release 分支只接受 Bug Fix、Version Update、Release Note、Config 調整；新增需求留在下一版 `develop`。逐項核對 User Story、Flowchart、Schema、Static Data、C4、UI Mock、Test Cases 及相關程式 PR。
3. `release/x.y.z` → `main` 透過 PR 審查並使用 Merge Commit；確認合併後 `main` 的發版 commit。
4. 在該 commit 建立 annotated tag `vX.Y.Z`，確認 tag 指向該 commit；可發布 GitHub Release 作為正式規格快照。Spec 無 Production 部署步驟。
5. `release/x.y.z` → `develop` 以 PR 回合併 Release 修正，衝突處理後重新檢查文件一致性。

```text
develop → release/x.y.z → 規格 QA → main PR → vX.Y.Z tag
        → 正式規格快照 → develop 回合併 PR
```

## Hotfix Flow

1. 從 `main` 建立 `hotfix/x.y.z-description`，只修正已發版規格的緊急錯誤。
2. 核對受影響的需求、資料契約、圖與測試案例，確認 Backend／Frontend 是否需同步修正。
3. 以 Hotfix PR 合併 `main`，保留完整提交；在合併 commit 建立對應 `vX.Y.Z` tag 並更新正式規格快照。
4. 以 Hotfix PR 回合併 `develop`，確保下一版不再含錯誤敘述。

```text
main → hotfix/x.y.z-description → 規格檢查 → main PR → vX.Y.Z tag
     → 正式規格快照 → develop 回合併 PR
```

## Versioning

採用 Semantic Versioning `MAJOR.MINOR.PATCH`：不相容的需求／資料契約變更加 MAJOR；向後相容的新需求加 MINOR；向後相容的規格錯誤修正加 PATCH。Spec 版本是文件快照版本，與 Backend／Frontend 部署版本各自計算；跨庫同時發版時，在 Release Note 列出對應的 repository、tag 與相容組合。

現有提交尚無正式 `v*` tag；第一次版本由 Release PR 核對已公開規格與相容性後決定，不憑歷史檔名自行宣稱既有正式版本。

## Tagging

正式 tag 格式為 `v<version>`，例如 `v1.2.0`。只在 Release／Hotfix 合併到 `main` 後建立，必須指向 `main` 上該次發版的 commit；同一 repository 的版本不得重用。tag 公開後不得移動或覆寫。發版紀錄保存 Spec tag、commit SHA 與相容的 Backend／Frontend 版本；修正使用新的版本號。

## CI/CD Mapping

程式碼託管於 GitHub，因此目標 CI 平台為 GitHub Actions。目前 repository **沒有 GitHub Actions workflow，也沒有已設定的分支保護或自動發布**；下表是待實作的觸發契約，不代表目前已在執行。Spec 不部署 DEV／STAGING／PRODUCTION 應用程式，環境名稱只代表規格審核階段。

| 觸發條件                   | 目標檢查／發布                                                                |
| -------------------------- | ----------------------------------------------------------------------------- |
| `feature/*`／`bugfix/*` PR | Markdown 連結／圖片引用、Mermaid 語法、檔案與差異檢查；人工比對相關需求與實作 |
| `develop` PR／合併         | 上述檢查，形成下一版規格整合基線（DEV）                                       |
| `release/*` PR／更新       | 全套規格一致性審查及相關 Backend／Frontend 契約確認（STAGING 審核）           |
| `main` PR／合併            | 規格檢查與必要審核，保留正式快照候選（Production 規格）                       |
| `v*` tag                   | 驗證 tag 指向 `main` release commit，發布 GitHub Release；不觸發應用程式部署  |

GitHub repository 管理者需另行啟用 `main`／`develop` 的 PR 必要條件、審查與必要狀態檢查，限制直接 push 與 force push；先建立實際 workflow 再把檢查設為 Required。文件本身不會替代 GitHub 的保護設定。

## AI Agent 作業程序

1. 修改前檢查 repository、`git status --short --branch`、`main`／`develop` 位置與對應規格；辨識工作樹既存變更。
2. 判斷 `feature`（包含一般規格重整）、`bugfix` 或 `hotfix`，從規定基底建立符合命名的工作分支；遠端 `develop` 尚未存在時，先由維護者完成分支建立與保護設定。
3. 修改後執行相關文件檢查、`git diff --check`，檢查 `git diff`、敏感資訊、圖片來源與連結；未執行的驗證明確標示。
4. 產生繁體中文 Conventional Commit，提供含測試結果、實作影響與回復方式的 PR 說明。所有合併與正式發布交由核准流程處理。

AI Agent 未經使用者明確要求，不執行 force push、history rewrite、刪除遠端分支、合併 `main` 或 Production 發版。
