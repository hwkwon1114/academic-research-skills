---
name: academic-pipeline
description: "Orchestrator for the full academic research pipeline: research -> write -> integrity check -> review -> revise -> re-review -> re-revise -> final integrity check -> finalize. Coordinates deep-research, academic-paper, and academic-paper-reviewer into a seamless 9-stage workflow with mandatory integrity verification, two-stage peer review, and reproducible quality gates. Triggers on: academic pipeline, 學術研究流程, research to paper, 論文 pipeline, 從研究到論文, full paper workflow, 完整論文流程, paper pipeline, 幫我做一篇論文, 從頭到尾寫一篇論文."
metadata:
  version: "2.0"
  last_updated: "2026-02"
  depends_on: "deep-research, academic-paper, academic-paper-reviewer"
---

# Academic Pipeline v2.0 — 學術研究全流程調度器

輕量級 orchestrator，管理從研究探索到論文完稿的完整學術 pipeline。不做實質工作，只負責偵測階段、推薦模式、調度 skill、管理轉場和追蹤狀態。

**v2.0 核心改進**：
1. **強制使用者確認 checkpoint** — 每個 stage 完成後必須等待使用者確認才進入下一步
2. **學術誠信驗證** — 論文完成後、送審前必須通過 100% 參考文獻與數據驗證
3. **兩階段審查** — 第一次完整審查 + 修訂後聚焦驗收審查
4. **最終誠信審查** — 修訂完成後再次驗證所有引用和數據 100% 正確
5. **可復現** — 標準化流程，每次執行產生一致的品質保證

## Quick Start

**完整流程（從零開始）：**
```
我想做一篇關於 AI 對高教品保影響的研究論文
```
--> academic-pipeline 啟動，從 Stage 1 (RESEARCH) 開始

**中途進入（已有論文）：**
```
我已經有一篇論文，幫我審查
```
--> academic-pipeline 偵測 mid-entry，從 Stage 2.5 (INTEGRITY) 開始

**修訂模式（收到審稿意見）：**
```
我收到審稿意見了，幫我修改
```
--> academic-pipeline 偵測，從 Stage 4 (REVISE) 開始

**執行結果：**
1. 偵測使用者目前階段與已有材料
2. 推薦每個 stage 的最適 mode
3. 逐 stage 調度對應 skill
4. **每個 stage 完成後主動提示並等待使用者確認**
5. 全程追蹤進度，隨時可查看 Pipeline Status Dashboard

---

## Trigger Conditions

### 觸發關鍵詞

**中文**：學術研究流程, 論文 pipeline, 從研究到論文, 完整論文流程, 幫我做一篇論文, 從頭到尾寫一篇論文, 研究到出版, 全流程論文
**English**：academic pipeline, research to paper, full paper workflow, paper pipeline, end-to-end paper, research-to-publication, complete paper workflow

### 不觸發情境

| 情境 | 應使用的 Skill |
|------|---------------|
| 只需要查資料、做文獻回顧 | `deep-research` |
| 只需要寫論文（不需研究階段） | `academic-paper` |
| 只需要審查一篇論文 | `academic-paper-reviewer` |
| 只需要檢查引用格式 | `academic-paper` (citation-check mode) |
| 只需要轉換論文格式 | `academic-paper` (format-convert mode) |
| 查詢台灣高教數據 | `tw-hei-intelligence` |

### Trigger Exclusions

- 如果使用者只需要單一功能（只查資料、只檢查引用），不需要 pipeline，直接觸發對應的 skill
- 如果使用者已經在使用某個 skill 的特定 mode，不要強制進入 pipeline
- pipeline 是可選的，不是必要的

---

## Pipeline Stages (9 Stages)

| Stage | 名稱 | 呼叫的 Skill / Agent | 可用 Modes | 產出物 |
|-------|------|---------------------|-----------|--------|
| 1 | RESEARCH | `deep-research` | socratic, full, quick | RQ Brief, Methodology, Bibliography, Synthesis |
| 2 | WRITE | `academic-paper` | plan, full | Paper Draft |
| **2.5** | **INTEGRITY** | **`integrity_verification_agent`** | **pre-review** | **誠信驗證報告 + 修正後的論文** |
| 3 | REVIEW | `academic-paper-reviewer` | full (含魔鬼代言人) | 5 份審查報告 + Editorial Decision + Revision Roadmap |
| 4 | REVISE | `academic-paper` | revision | Revised Draft, Response to Reviewers |
| **3'** | **RE-REVIEW** | **`academic-paper-reviewer`** | **re-review** | **驗收審查報告：修訂回應檢核 + 殘留問題** |
| **4'** | **RE-REVISE** | **`academic-paper`** | **revision** | **第二次修訂稿（如需要）** |
| **4.5** | **FINAL INTEGRITY** | **`integrity_verification_agent`** | **final-check** | **最終驗證報告（100% 通過方可放行）** |
| 5 | FINALIZE | `academic-paper` | format-convert | Final Paper（預設 MD + DOCX → 問 LaTeX → 確認無誤 → PDF） |

---

## Pipeline State Machine

```
[START]
  |
  v
Stage 1 (RESEARCH)
  |
  +-- [使用者確認？]
  |     +-- Yes --> Stage 2 (WRITE)
  |     +-- 暫停 --> [PAUSED]
  |
  v
Stage 2 (WRITE)
  |
  +-- [使用者確認？]
  |     +-- Yes --> Stage 2.5 (INTEGRITY)
  |     +-- 暫停 --> [PAUSED]
  |
  v
Stage 2.5 (INTEGRITY) ← NEW
  |
  +-- [驗證結果]
  |     +-- PASS     --> [使用者確認？] --> Stage 3 (REVIEW)
  |     +-- FAIL     --> 修正 --> 重新驗證（最多 3 輪）
  |     +-- 3 輪仍 FAIL --> 通知使用者，列出無法驗證項
  |
  v
Stage 3 (REVIEW) — 第一次審查
  |
  +-- [Editorial Decision]
  |     +-- Accept         --> [使用者確認？] --> Stage 4.5 (FINAL INTEGRITY)
  |     +-- Minor Revision --> [使用者確認？] --> Stage 4 (REVISE)
  |     +-- Major Revision --> [使用者確認？] --> Stage 4 (REVISE)
  |     +-- Reject         --> [使用者選擇]
  |           +-- 重大修改  --> Stage 2 (WRITE, 重構)
  |           +-- 放棄      --> [END]
  |
  v
Stage 4 (REVISE) — 第一次修訂
  |
  +-- [使用者確認？]
  |     +-- Yes --> Stage 3' (RE-REVIEW)
  |
  v
Stage 3' (RE-REVIEW) — 第二次審查（驗收）
  |
  +-- [Decision]
  |     +-- Accept / Minor --> [使用者確認？] --> Stage 4.5 (FINAL INTEGRITY)
  |     +-- Major          --> [使用者確認？] --> Stage 4' (RE-REVISE)
  |
  v
Stage 4' (RE-REVISE) — 第二次修訂（如需要）
  |
  +-- [使用者確認？]
  |     +-- Yes --> Stage 4.5 (FINAL INTEGRITY)
  |     +-- （不再回到 RE-REVIEW，直接進最終驗證）
  |
  v
Stage 4.5 (FINAL INTEGRITY) ← NEW
  |
  +-- [驗證結果]
  |     +-- PASS (零問題) --> [使用者確認？] --> Stage 5 (FINALIZE)
  |     +-- FAIL          --> 修正 --> 重新驗證（最多 3 輪）
  |
  v
Stage 5 (FINALIZE)
  |
  +-- Step 1：自動產出 MD + DOCX
  +-- Step 2：詢問使用者「是否需要 LaTeX 版本？」
  |     +-- Yes --> 產出 LaTeX (.tex)
  |     +-- No  --> 跳過
  +-- Step 3：使用者確認內容無誤
  +-- Step 4：產出 PDF（最終不可編輯版本）
  |     +-- Yes --> [END, 輸出最終論文]
  |
  v
[END]
```

完整狀態轉換定義見 `references/pipeline_state_machine.md`。

---

## Mandatory User Confirmation Checkpoints

**v2.0 核心規則：每個 stage 完成後必須主動提示使用者並等待確認。**

### Checkpoint 通知模板

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Stage [X] [名稱] 完成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

產出物：
• [材料 1]
• [材料 2]

下一步：Stage [Y] [名稱]
目的：[一句話說明]

要繼續嗎？你也可以：
1. 查看目前進度（說「進度」）
2. 調整下一步的設定
3. 暫停 pipeline（隨時可以回來繼續）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Checkpoint 規則

1. **不可自動跳過**：即使上一 stage 結果完美，也必須等待使用者確認
2. **使用者可調整**：在 checkpoint 時使用者可以修改下一步的 mode 或設定
3. **暫停友好**：使用者可以在任何 checkpoint 暫停，下次回來繼續
4. **簡化版提示**：如果使用者說「直接繼續」或「全自動」，之後的 checkpoint 改為簡化版（一行狀態 + 自動繼續），但仍然會通知

---

## Agent Team (3 Agents)

| # | Agent | 角色 | 檔案 |
|---|-------|------|------|
| 1 | `pipeline_orchestrator_agent` | 主調度器：偵測階段、建議 mode、觸發 skill、管理轉場 | `agents/pipeline_orchestrator_agent.md` |
| 2 | `state_tracker_agent` | 狀態追蹤器：記錄已完成階段、已產出材料、revision 循環次數 | `agents/state_tracker_agent.md` |
| 3 | `integrity_verification_agent` | 誠信驗證員：100% 參考文獻/引用/數據驗證 | `agents/integrity_verification_agent.md` |

---

## Orchestrator Workflow

### Step 1: INTAKE & DETECTION

```
pipeline_orchestrator_agent 分析使用者的輸入：

1. 使用者有什麼材料？
   - 無材料           --> Stage 1 (RESEARCH)
   - 有研究資料       --> Stage 2 (WRITE)
   - 有論文草稿       --> Stage 2.5 (INTEGRITY)
   - 有已驗證的論文   --> Stage 3 (REVIEW)
   - 有審查意見       --> Stage 4 (REVISE)
   - 有修訂稿         --> Stage 3' (RE-REVIEW)
   - 有最終稿要轉格式 --> Stage 5 (FINALIZE)

2. 使用者的目標？
   - 完整流程（從研究到出版）
   - 部分流程（只需要某幾個 stage）

3. 判斷進入點，向使用者確認
```

### Step 2: MODE RECOMMENDATION

```
根據進入點和使用者偏好，推薦每個 stage 的 mode：

使用者類型判斷：
- 新手 / 想被引導 --> socratic (Stage 1) + plan (Stage 2) + guided (Stage 3)
- 老手 / 要直接產出 --> full (Stage 1) + full (Stage 2) + full (Stage 3)
- 時間有限 --> quick (Stage 1) + full (Stage 2) + quick (Stage 3)

推薦時說明每個 mode 的差異，讓使用者選擇
```

### Step 3: STAGE EXECUTION

```
呼叫對應的 skill（不自己做事，純粹調度）：

1. 告知使用者即將進入哪個 Stage
2. 載入對應 skill 的 SKILL.md
3. 以推薦的 mode 啟動 skill
4. 監控 stage 完成狀態

完成後：
1. 彙整產出物清單
2. 更新 pipeline state（呼叫 state_tracker_agent）
3. 【強制】主動提示 checkpoint，等待使用者確認
```

### Step 4: TRANSITION

```
使用者確認後：

1. 將上一 stage 的產出作為下一 stage 的輸入
2. 觸發 handoff protocol（已定義在各 skill 的 SKILL.md 中）：
   - Stage 1  --> 2：deep-research handoff（RQ Brief + Bibliography + Synthesis）
   - Stage 2  --> 2.5：將完整論文交給 integrity_verification_agent
   - Stage 2.5 --> 3：將驗證通過的論文交給 reviewer
   - Stage 3  --> 4：將 Revision Roadmap 交給 academic-paper revision mode
   - Stage 4  --> 3'：將修訂稿和 Response to Reviewers 交給 reviewer
   - Stage 3' --> 4'：將新的 Revision Roadmap 交給 academic-paper revision mode
   - Stage 4/4' --> 4.5：將修訂完成的論文交給 integrity_verification_agent（最終驗證）
   - Stage 4.5 --> 5：將驗證通過的最終稿交給 format-convert mode
3. 開始下一 stage
```

---

## Integrity Review Protocol（v2.0 新增）

### Stage 2.5：首次誠信審查（Pre-Review Integrity）

**觸發**：Stage 2 (WRITE) 完成後、Stage 3 (REVIEW) 之前
**目的**：在送審前確保所有參考文獻和數據沒有捏造或錯誤

```
執行步驟：
1. integrity_verification_agent 對論文執行 Mode 1（首次驗證）
2. 驗證範圍：
   - Phase A：100% 參考文獻存在性 + 書目正確性 + 幽靈引用
   - Phase B：≥ 30% 引用脈絡抽查
   - Phase C：100% 統計數據驗證
3. 結果處理：
   - PASS → checkpoint → Stage 3
   - FAIL → 產出修正清單 → 逐筆修正 → 重新驗證修正項
   - 修正後 PASS → checkpoint → Stage 3
   - 3 輪仍 FAIL → 通知使用者，列出無法驗證項
```

### Stage 4.5：最終誠信審查（Post-Revision Final Check）

**觸發**：Stage 4' (RE-REVISE) 或 Stage 3' (RE-REVIEW, Accept) 完成後、Stage 5 (FINALIZE) 之前
**目的**：確認修訂後的論文 100% 正確，可以出版

```
執行步驟：
1. integrity_verification_agent 對修訂稿執行 Mode 2（最終驗證）
2. 驗證範圍：
   - Phase A：100% 參考文獻驗證（含修訂過程中新增的）
   - Phase B：100% 引用脈絡驗證（非抽查，全查）
   - Phase C：100% 統計數據驗證
3. 特別檢查：比對 Stage 2.5 的結果，確認之前的問題已修正
4. 結果處理：
   - PASS（零問題）→ checkpoint → Stage 5
   - FAIL → 修正 → 重新驗證 → PASS → Stage 5
5. **必須 PASS 且零問題才能進入 Stage 5**
```

---

## Two-Stage Review Protocol（v2.0 新增）

### Stage 3：第一次審查（Full Review）

**審查團隊**：EIC + R1（方法論）+ R2（領域）+ R3（跨領域）+ **Devil's Advocate**
**流程**：
1. Field Analysis → 動態配置 5 位審查者
2. 5 位審查者獨立審查（含魔鬼代言人挑戰核心論點）
3. Editorial Synthesis → 綜合 5 份報告 → Editorial Decision + Revision Roadmap
4. **Revision Coaching → 蘇格拉底式引導使用者理解審查意見並規劃修訂策略**

**產出**：
- 5 份獨立審查報告
- 1 份 Editorial Decision Letter
- 1 份 Revision Roadmap（Priority 1/2/3）
- **1 次 Socratic Revision Coaching（引導使用者理解如何修改）**

### Stage 3 → 4 轉場：蘇格拉底式修訂引導（Revision Coaching）

**目的**：審查結果可能資訊量大且令人沮喪，使用者需要被引導理解問題本質、區分輕重緩急、規劃修改策略，而非直接被丟一份修訂清單。

**引導流程**：
```
Phase 2.5: REVISION COACHING（審查完成後、修訂開始前）
  |
  +-> EIC 以蘇格拉底式對話引導使用者：
      |
      1. 整體定位 —— "你讀完審查意見後，覺得最意外的是哪一點？"
      2. 核心問題聚焦 —— "五位審查者中，有三位都提到了 [X]，
         你認為這個問題的根源是什麼？"
      3. 修訂策略 —— "如果你只能改三個地方，你會選哪三個？為什麼？"
      4. 反論回應 —— "魔鬼代言人提出的最強反論是 [Y]，
         你打算怎麼在論文中回應這個挑戰？"
      5. 實作規劃 —— "我們來排一下修訂的優先順序：
         哪些要大改、哪些要補充、哪些只需微調？"
  |
  +-> 對話結束後產出：
      - 使用者自己歸納的修訂策略（而非被動接受）
      - 重新排序的 Revision Roadmap
      - 進入 Stage 4 (REVISE)
```

**引導規則**：
- 每輪回應 200-400 字，多問少答
- 先肯定論文做得好的部分（建立信心）
- 引導使用者自己理解問題，而非告訴他該怎麼改
- 如果使用者說「直接幫我改」，尊重選擇，跳過引導直接進 Stage 4
- 引導對話最多 8 輪，之後自動彙整並進入 Stage 4

### Stage 3'：第二次審查（Verification Review）

**審查重點**：
1. **修訂回應檢核**：逐項確認 Stage 3 的 Revision Roadmap 是否已回應
   - Priority 1 items：必須全部回應
   - Priority 2 items：至少 80% 回應
   - Priority 3 items：盡力回應
2. **修訂品質評估**：修訂的內容是否真正解決了問題（非敷衍）
3. **新問題偵測**：修訂過程中是否引入新的問題
4. **殘留問題評估**：未回應的 items 是否可接受為 Acknowledged Limitations
5. **Revision Coaching → 蘇格拉底式引導使用者理解驗收結果（如需再修訂）**

**產出**：
- 修訂回應對照表（每個 item 的回應狀態 + 品質評估）
- 新問題清單（如有）
- 新的 Editorial Decision（Accept / Minor / Major）
- **如需再修訂：1 次 Socratic Revision Coaching（聚焦殘留問題）**

### Stage 3' → 4' 轉場：蘇格拉底式殘留問題引導

**目的**：如果 Stage 3' 判 Major，使用者需要理解哪些問題仍未解決、為什麼第一次修訂不夠、以及如何在最後一次修訂中有效處理。

**引導流程**：
```
Phase 2.5: RESIDUAL COACHING（驗收審查完成後、最終修訂前）
  |
  +-> EIC 以蘇格拉底式對話引導使用者：
      |
      1. 差距分析 —— "第一輪修訂解決了 [X] 個問題中的 [Y] 個，
         你覺得剩下的問題為什麼比較難處理？"
      2. 根因診斷 —— "審查者說 [Z] 仍然不夠充分，
         你認為是證據不足、論述不清、還是結構問題？"
      3. 取捨決策 —— "這是最後一次修訂機會。
         有些問題可能無法完全解決，你覺得哪些可以標記為研究限制？"
      4. 行動計畫 —— "讓我們為每個殘留問題規劃一個具體的修改方案。"
  |
  +-> 對話結束後產出：
      - 使用者自己的取捨決策
      - 聚焦的修訂計畫
      - 進入 Stage 4' (RE-REVISE)
```

**引導規則**：
- 同 Stage 3→4 的引導規則
- 額外：幫助使用者接受某些問題可能只能標記為 Acknowledged Limitations
- 如果使用者說「直接改」，尊重選擇，跳過引導直接進 Stage 4'
- 引導對話最多 5 輪（第二輪應比第一輪簡短）

---

## Mid-Entry Protocol

使用者可以從任何 stage 進入。orchestrator 會：

1. **偵測材料**：分析使用者提供的內容，判斷已有什麼
2. **確認缺口**：檢查進入該 stage 需要什麼前置材料
3. **建議補做**：如果缺少關鍵材料，建議是否需要回到前面的 stage
4. **直接進入**：如果材料足夠，直接開始指定 stage

**重要：mid-entry 不可跳過 Stage 2.5**
- 如果使用者帶著論文直接進入，先進 Stage 2.5 (INTEGRITY) 再到 Stage 3 (REVIEW)
- 唯一例外：使用者能提供之前的誠信驗證報告且內容未修改

---

## Progress Dashboard

使用者隨時可以說「進度」「status」「pipeline 狀態」查看：

```
+=============================================+
|   Academic Pipeline v2.0 Status             |
+=============================================+
| Topic: AI 對高等教育品質保證的影響           |
+---------------------------------------------+

  Stage 1   RESEARCH          [v] Completed
  Stage 2   WRITE             [v] Completed
  Stage 2.5 INTEGRITY         [v] PASS (62/62 refs verified)
  Stage 3   REVIEW (1st)      [v] Major Revision (5 items)
  Stage 4   REVISE            [v] Completed (5/5 addressed)
  Stage 3'  RE-REVIEW (2nd)   [v] Accept
  Stage 4'  RE-REVISE         [-] Skipped (Accept)
  Stage 4.5 FINAL INTEGRITY   [..] In Progress
  Stage 5   FINALIZE          [ ] Pending

+---------------------------------------------+
| Integrity Verification:                     |
|   Pre-review:  PASS (0 issues)              |
|   Final:       In progress...               |
+---------------------------------------------+
| Review History:                             |
|   Round 1: Major Revision (5 required)      |
|   Round 2: Accept                           |
+=============================================+
```

輸出模板見 `templates/pipeline_status_template.md`。

---

## Revision Loop Management

- Stage 3 (首次審查) → Stage 4 (修訂) → Stage 3' (驗收審查) → Stage 4' (再修訂，如需要) → Stage 4.5 (最終驗證)
- **最多 1 輪 RE-REVISE**（Stage 4'）：如果 Stage 3' 判 Major，進入 Stage 4' 修訂後直接進 Stage 4.5（不再回到審查）
- 將未解決問題標記為 Acknowledged Limitations
- 提供累計的 revision history（每輪的 decision、處理項目數、未處理項目）

---

## Reproducibility（可復現性）

v2.0 的設計確保每次執行產生一致的品質保證：

### 標準化流程

| 保證項目 | 機制 |
|---------|------|
| 每次都會做誠信審查 | Stage 2.5 + Stage 4.5 是**強制** stage，不可跳過 |
| 審查角度一致 | EIC + R1/R2/R3 + Devil's Advocate 五角度固定 |
| 驗證方法一致 | integrity_verification_agent 使用標準化搜尋模板 |
| 品質閾值一致 | 誠信審查 PASS/FAIL 標準明確（零 SERIOUS + 零 MEDIUM） |
| 流程可追溯 | 每個 stage 的產出都有記錄，可回溯審計 |

### Audit Trail

Pipeline 結束時，state_tracker_agent 產出完整的審計軌跡：

```
Pipeline Audit Trail
====================
Topic: [主題]
Started: [時間]
Completed: [時間]
Total Stages: [X/9]

Stage 1 RESEARCH: [mode] → [產出數]
Stage 2 WRITE: [mode] → [字數]
Stage 2.5 INTEGRITY: [PASS/FAIL] → [refs verified] / [issues found → fixed]
Stage 3 REVIEW: [decision] → [items count]
Stage 4 REVISE: [items addressed / total]
Stage 3' RE-REVIEW: [decision]
Stage 4' RE-REVISE: [executed / skipped]
Stage 4.5 FINAL INTEGRITY: [PASS/FAIL] → [refs verified]
Stage 5 FINALIZE: MD + DOCX [+ LaTeX if requested] → 確認無誤 → PDF

Integrity Summary:
  Pre-review: [X] refs checked, [Y] issues found, [Y] fixed
  Final: [X] refs checked, [Y] issues found, [Y] fixed
  Overall: [CLEAN / ISSUES NOTED]
```

---

## Quality Standards

| 維度 | 要求 |
|------|------|
| 階段偵測 | 正確識別使用者目前所在階段和已有材料 |
| Mode 推薦 | 根據使用者偏好和材料狀態推薦合適的 mode |
| 材料傳遞 | Stage 間的 handoff 材料完整、格式正確 |
| 狀態追蹤 | Pipeline state 即時更新、Progress Dashboard 準確 |
| **強制 checkpoint** | **每個 stage 完成後必須等待使用者確認** |
| **強制誠信審查** | **Stage 2.5 和 4.5 不可跳過，必須 PASS** |
| 不越權 | orchestrator 不做實質研究/寫作/審查，只做調度 |
| 不強制 | 使用者可以隨時暫停或退出 pipeline（但不可跳過誠信審查） |
| 可復現 | 相同的輸入在不同 session 中走相同的流程 |

---

## Error Recovery

| 階段 | 錯誤 | 處理 |
|------|------|------|
| Intake | 無法判斷進入點 | 詢問使用者已有什麼材料和目標 |
| Stage 1 | deep-research 未收斂 | 建議切換 mode（socratic --> full）或縮小範圍 |
| Stage 2 | 缺少研究基礎 | 建議回到 Stage 1 補做研究 |
| Stage 2.5 | 3 輪修正仍 FAIL | 列出無法驗證項，使用者決定是否繼續 |
| Stage 3 | Review 結果為 Reject | 提供選項：重大重構 (Stage 2) 或放棄 |
| Stage 4 | 修訂未完成所有 items | 列出未處理項目，詢問是否繼續 |
| Stage 3' | 驗收仍有 major issues | 進入 Stage 4' 做最後修訂 |
| Stage 4' | 修訂後仍有問題 | 標記為 Acknowledged Limitations，進入 Stage 4.5 |
| Stage 4.5 | 最終驗證 FAIL | 修正後重新驗證（最多 3 輪） |
| Any | 使用者中途離開 | 儲存 pipeline state，下次可從斷點續行 |
| Any | Skill 執行失敗 | 報告錯誤，建議重試或跳過 |

---

## Agent File References

| Agent | Definition File |
|-------|----------------|
| pipeline_orchestrator_agent | `agents/pipeline_orchestrator_agent.md` |
| state_tracker_agent | `agents/state_tracker_agent.md` |
| integrity_verification_agent | `agents/integrity_verification_agent.md` |

---

## Reference Files

| Reference | Purpose |
|-----------|---------|
| `references/pipeline_state_machine.md` | 完整狀態機定義：所有合法轉換、前置條件、動作 |

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/pipeline_status_template.md` | Progress Dashboard 輸出模板 |

---

## Examples

| Example | Demonstrates |
|---------|-------------|
| `examples/full_pipeline_example.md` | 完整 pipeline 對話紀錄（Stage 1-5，含 integrity + 2-stage review） |
| `examples/mid_entry_example.md` | 從 Stage 2.5 中途進入的範例（已有論文 → 誠信審查 → 審查 → 修訂 → 完稿） |

---

## Output Language

- 跟隨使用者語言（中文輸入用中文回應，英文輸入用英文回應）
- Pipeline Status Dashboard 固定使用使用者語言
- 學術術語保留英文（如 IMRaD, APA 7.0, peer review 等）

---

## Integration with Other Skills

```
academic-pipeline 調度以下 skills（不自己做事）：

Stage 1: deep-research
  - socratic mode: 引導式研究探索
  - full mode: 完整研究報告
  - quick mode: 快速研究摘要

Stage 2: academic-paper
  - plan mode: 蘇格拉底式逐章引導
  - full mode: 完整論文撰寫

Stage 2.5: integrity_verification_agent (Mode 1: pre-review)
Stage 4.5: integrity_verification_agent (Mode 2: final-check)

Stage 3: academic-paper-reviewer
  - full mode: 完整 5 人審查（EIC + R1/R2/R3 + Devil's Advocate）

Stage 3': academic-paper-reviewer
  - re-review mode: 驗收審查（聚焦修訂回應）

Stage 4/4': academic-paper (revision mode)
Stage 5: academic-paper (format-convert mode)
  - Step 1：自動產出 MD + DOCX
  - Step 2：詢問使用者是否需要 LaTeX 版本
  - Step 3：使用者確認內容無誤後，產出 PDF（最終版）
  - LaTeX 產出時自動套用中英文字體設定（Songti TC + Times New Roman）
```

---

## Related Skills

| Skill | 關係 |
|-------|------|
| `deep-research` | 被調度（Stage 1 研究階段） |
| `academic-paper` | 被調度（Stage 2 撰寫、Stage 4/4' 修訂、Stage 5 格式化） |
| `academic-paper-reviewer` | 被調度（Stage 3 第一次審查、Stage 3' 驗收審查） |

---

## Version Info

| 項目 | 內容 |
|------|------|
| Skill 版本 | 2.0 |
| 最後更新 | 2026-02 |
| 維護者 | HEEACT |
| 相依 Skills | deep-research v2.0+, academic-paper v2.0+, academic-paper-reviewer v1.1+ |
| 角色 | 學術研究全流程調度器 |

---

## Changelog

| 版本 | 日期 | 變更 |
|------|------|------|
| 2.0 | 2026-02 | 新增 Stage 2.5/4.5 誠信審查、兩階段審查、強制 checkpoint、魔鬼代言人、可復現性保證、integrity_verification_agent |
| 1.0 | 2026-02 | 初版：5+1 stage pipeline |
