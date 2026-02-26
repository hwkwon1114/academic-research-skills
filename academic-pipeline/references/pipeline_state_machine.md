# Pipeline State Machine v2.0 — 完整定義

本文件定義 academic-pipeline v2.0 的所有合法狀態、轉換條件、轉換動作和異常處理。

---

## 狀態定義

### Stage 狀態

| 狀態 | 說明 |
|------|------|
| `pending` | 尚未開始，等待前置 stage 完成 |
| `in_progress` | 正在執行中 |
| `completed` | 已完成，產出物已記錄 |
| `skipped` | 使用者選擇跳過（僅限非強制 stage） |
| `blocked` | 前置條件不滿足（如誠信審查 FAIL） |

### Pipeline 全域狀態

| 狀態 | 說明 |
|------|------|
| `initializing` | 正在偵測進入點和材料 |
| `running` | Pipeline 執行中（至少一個 stage 為 in_progress） |
| `awaiting_confirmation` | Stage 完成，等待使用者確認 checkpoint |
| `paused` | 使用者暫停，可隨時恢復 |
| `completed` | 所有必要 stage 完成，最終論文已產出 |
| `aborted` | 使用者放棄（如 Reject 後選擇放棄） |

---

## 狀態轉換圖（ASCII）

```
                        +-------------+
                        | INITIALIZING|
                        +------+------+
                               |
                    [偵測進入點 & 材料]
                               |
         +----------+----------+----------+----------+
         |          |          |          |          |
         v          v          v          v          v
    +--------+ +--------+ +--------+ +--------+ +--------+
    |Stage 1 | |Stage 2 | |Stg 2.5 | |Stage 3 | |Stage 4 |
    |RESEARCH| | WRITE  | |INTEGRIT| | REVIEW | | REVISE |
    +---+----+ +---+----+ +---+----+ +---+----+ +---+----+
        |          |          |          |          |
   [checkpoint]   [checkpoint]   |     [checkpoint]  |
        |          |          |          |          |
        v          v          v          v          v
   +--------+ +--------+ +---+----+    |          |
   |Stage 2 | |Stg 2.5 | |PASS?   |    |          |
   | WRITE  | |INTEGRIT| +---+----+    |          |
   +---+----+ +---+----+     |         |          |
                         +----+----+    |          |
                         |         |    |          |
                        Yes       No    |          |
                         |     [修正]   |          |
                         |     [重驗]   |          |
                    [checkpoint]   |    |          |
                         |         |    |          |
                         v         |    |          |
                    +--------+     |    |          |
                    |Stage 3 | <---+    |          |
                    | REVIEW |          |          |
                    +---+----+          |          |
                        |               |          |
                   [DECISION]           |          |
                        |               |          |
              +---------+---------+     |          |
              |         |         |     |          |
            Accept    Minor     Major   |          |
              |       Revision  Revision|          |
              |         |         |     |          |
              |    [checkpoint]  [checkpoint]      |
              |         |         |     |          |
              |         v         v     |          |
              |    +--------+ +--------+|          |
              |    |Stage 4 | |Stage 4 ||          |
              |    | REVISE | | REVISE ||          |
              |    +---+----+ +---+----+|          |
              |        |          |     |          |
              |   [checkpoint]   [checkpoint]      |
              |        |          |     |          |
              |        v          v     |          |
              |    +--------+ +--------+           |
              |    |Stg 3'  | |Stg 3'  |           |
              |    |RE-REV. | |RE-REV. |           |
              |    +---+----+ +---+----+           |
              |        |          |                 |
              |   [DECISION]  [DECISION]            |
              |        |          |                 |
              |     Accept      Major               |
              |     /Minor        |                 |
              |        |     [checkpoint]           |
              |        |          |                 |
              |        |          v                 |
              |        |     +--------+             |
              |        |     |Stg 4'  |             |
              |        |     |RE-REVIS|             |
              |        |     +---+----+             |
              |        |          |                 |
              |   [checkpoint]  [checkpoint]        |
              |        |          |                 |
              v        v          v                 |
         +----+--------+----------+-----+           |
         |     Stage 4.5                |           |
         |   FINAL INTEGRITY            |           |
         +----------+------------------+           |
                    |                               |
               [PASS? 零問題]                        |
                    |                               |
              +-----+-----+                         |
              |           |                         |
             Yes         No                         |
              |        [修正]                        |
              |        [重驗]                        |
         [checkpoint]     |                         |
              |           |                         |
              v           |                         |
         +--------+       |                         |
         |Stage 5 | <-----+                         |
         |FINALIZE|                                 |
         +---+----+                                 |
             |                                      |
             v                                      |
         +-------+                                  |
         |  END  |                                  |
         +-------+                                  |
```

---

## 合法的狀態轉換

### 正常流程轉換

| 從 | 到 | 前置條件 | 動作 |
|----|-----|---------|------|
| INIT | Stage 1 | 使用者確認要從 Stage 1 開始 | 偵測 mode 偏好，啟動 deep-research |
| INIT | Stage 2 | 使用者有研究材料，確認跳過 Stage 1 | 偵測材料，啟動 academic-paper |
| INIT | Stage 2.5 | 使用者有完整論文 | 啟動 integrity_verification_agent |
| INIT | Stage 3 | 使用者有已驗證的論文 + 誠信報告 | 確認論文語言/領域，啟動 reviewer |
| INIT | Stage 4 | 使用者有審查意見 | 確認論文 + 審查意見，啟動 revision |
| INIT | Stage 5 | 使用者有最終稿要轉格式 | 確認格式需求，啟動 format-convert |
| Stage 1 | **checkpoint** | Stage 1 completed | 等待使用者確認 |
| checkpoint | Stage 2 | 使用者確認 | handoff RQ Brief + Bibliography + Synthesis |
| Stage 2 | **checkpoint** | Stage 2 completed，Paper Draft 產出 | 等待使用者確認 |
| checkpoint | Stage 2.5 | 使用者確認 | 傳遞 Paper Draft 給 integrity agent |
| Stage 2.5 | **checkpoint** | PASS | 等待使用者確認 |
| Stage 2.5 | Stage 2.5 (retry) | FAIL | 修正問題，重新驗證（最多 3 輪） |
| checkpoint | Stage 3 | 使用者確認 | 傳遞驗證通過的論文給 reviewer |
| Stage 3 | **checkpoint** | Decision produced | 等待使用者確認 |
| checkpoint | Stage 4 | Decision = Minor/Major，使用者確認 | 傳遞 Revision Roadmap |
| checkpoint | Stage 4.5 | Decision = Accept，使用者確認 | 跳過修訂，直接最終驗證 |
| Stage 4 | **checkpoint** | Stage 4 completed | 等待使用者確認 |
| checkpoint | Stage 3' | 使用者確認 | 傳遞 Revised Draft + Response to Reviewers |
| Stage 3' | **checkpoint** | Decision produced | 等待使用者確認 |
| checkpoint | Stage 4.5 | Decision = Accept/Minor，使用者確認 | 傳遞 final draft 到最終驗證 |
| checkpoint | Stage 4' | Decision = Major，使用者確認 | 傳遞新的 Revision Roadmap |
| Stage 4' | **checkpoint** | Stage 4' completed | 等待使用者確認 |
| checkpoint | Stage 4.5 | 使用者確認 | 傳遞修訂稿到最終驗證 |
| Stage 4.5 | **checkpoint** | PASS（零問題） | 等待使用者確認 |
| Stage 4.5 | Stage 4.5 (retry) | FAIL | 修正問題，重新驗證（最多 3 輪） |
| checkpoint | Stage 5 | 使用者確認 | 傳遞 final accepted draft |

### 特殊流程轉換

| 從 | 到 | 前置條件 | 動作 |
|----|-----|---------|------|
| Stage 3 (Reject) | Stage 2 | 使用者選擇重構 | 清除 Stage 2-3 狀態，保留 Stage 1 材料，重啟 Stage 2 |
| Stage 3 (Reject) | ABORT | 使用者選擇放棄 | 儲存所有已產出材料，標記 pipeline aborted |
| Stage 3' (Major) | Stage 4' | 使用者確認 | 最後一次修訂機會 |
| Stage 4' | Stage 4.5 | 修訂完成 | 直接進最終驗證（不再回到審查） |
| Any stage | PAUSED | 使用者說「暫停」「先這樣」 | 儲存 pipeline state |
| PAUSED | 上次 stage | 使用者回來繼續 | 恢復 pipeline state，顯示 Dashboard |

### 禁止的轉換（不合法）

| 從 | 到 | 原因 |
|----|-----|------|
| Stage 1 | Stage 3 | 不可跳過 Stage 2 和 2.5（除非 mid-entry + 有論文）|
| Stage 2 | Stage 3 | **不可跳過 Stage 2.5（誠信審查是強制的）** |
| Stage 4 | Stage 5 | 不可跳過 RE-REVIEW（修訂後必須再審） |
| Stage 3' | Stage 5 | **不可跳過 Stage 4.5（最終誠信審查是強制的）** |
| Stage 4' | Stage 3' | 不可再回到 RE-REVIEW（最多 1 輪 RE-REVISE） |
| Stage 5 | Stage 3 | 不可回退（FINALIZE 後不可再審查） |
| completed | in_progress | 已完成的 stage 不可重新開始 |

---

## 材料依賴矩陣

| 材料 | 產出於 | 消費於 | 必要/建議 |
|------|--------|--------|----------|
| RQ Brief | Stage 1 | Stage 2 (Phase 0) | 建議 |
| Methodology Blueprint | Stage 1 | Stage 2 (Phase 0) | 建議 |
| Bibliography | Stage 1 | Stage 2 (Phase 1) | 建議 |
| Synthesis Report | Stage 1 | Stage 2 (Phase 3) | 建議 |
| Paper Draft | Stage 2 | Stage 2.5 (input) | **必要** |
| **Integrity Report (Pre)** | **Stage 2.5** | **Stage 3 (前置)** | **必要** |
| **Verified Paper Draft** | **Stage 2.5** | **Stage 3 (Phase 0)** | **必要** |
| Review Reports (x5) | Stage 3 | Stage 4 (input) | 必要 |
| Editorial Decision | Stage 3 | Stage 4 (input) | 必要 |
| Revision Roadmap | Stage 3 | Stage 4 (input) | 必要 |
| Revised Draft | Stage 4 | Stage 3' (Phase 0) | 必要 |
| Response to Reviewers | Stage 4 | Stage 3' (input) | 建議 |
| **Re-Review Report** | **Stage 3'** | **Stage 4' (input)** | **必要（if Major）** |
| **Re-Revised Draft** | **Stage 4'** | **Stage 4.5 (input)** | **必要（if executed）** |
| **Integrity Report (Final)** | **Stage 4.5** | **Stage 5 (前置)** | **必要** |
| Final Paper | Stage 5 | END (delivery) | 必要 |

---

## 異常狀態處理

### 超時

如果某個 stage 長時間無進展（例如 Socratic mode 超過 15 輪未收斂）：
1. state_tracker 標記該 stage 為 `stalled`
2. orchestrator 提供選項：
   - 切換 mode（socratic --> full）
   - 縮小範圍
   - 跳過此 stage（非強制 stage）

### 材料遺失

如果轉場時發現需要的材料不存在：
1. state_tracker 報告材料缺口
2. orchestrator 建議回到產出該材料的 stage
3. 使用者可以選擇：補做 / 跳過（自負風險，但不可跳過誠信審查）

### 誠信審查 FAIL 循環

如果 Stage 2.5 或 4.5 的修正超過 3 輪仍未通過：
1. 列出所有無法驗證的項目
2. 使用者決定：
   - 手動處理無法驗證的項目
   - 移除無法驗證的引用
   - 繼續進入下一 stage（附「部分未驗證」警告）

### Session 中斷

如果使用者離開後回來：
1. orchestrator 顯示 Progress Dashboard
2. 確認是否從斷點繼續
3. 檢查是否需要刷新任何已過時的材料

---

## Revision Loop 規則（v2.0）

### 簡化的修訂循環

```
v2.0 的修訂循環比 v1.0 更簡單明確：

Stage 3 (首次 REVIEW)
  → Decision: Accept → Stage 4.5
  → Decision: Minor/Major → Stage 4
      → Stage 4 (REVISE)
          → Stage 3' (RE-REVIEW, 驗收)
              → Decision: Accept/Minor → Stage 4.5
              → Decision: Major → Stage 4' (最後一次修訂)
                  → Stage 4.5（直接進最終驗證，不再回審）

最多 1 輪 RE-REVISE，不會無限循環。
未解決問題 → Acknowledged Limitations。
```

### 與 v1.0 的差異

| v1.0 | v2.0 |
|------|------|
| 最多 2 輪 review-revise 循環 | 固定 2 次審查（Stage 3 + Stage 3'）+ 最多 1 次 RE-REVISE |
| 無誠信審查 | 強制 Pre-review + Final integrity check |
| 4 位審查者 | 5 位審查者（+Devil's Advocate） |
| 可跳過任何 stage | Stage 2.5 和 4.5 不可跳過 |
| 無 checkpoint 強制 | 每個 stage 必須 checkpoint |
