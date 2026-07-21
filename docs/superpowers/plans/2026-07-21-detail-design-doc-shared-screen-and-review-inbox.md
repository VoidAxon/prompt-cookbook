# detail-design-doc 共有画面判定是正・要確認一元収集 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** detail-design-doc スキルの共有/専属判定を「開放点の数」から「集合包含テスト」に是正し、共有への外出し・理解不完全・処理不能を第11章「要人間確認の一元収集」に集約する。

**Architecture:** プロンプト文面（`SKILL.md` / `template.md`）のみを編集する。実行コード・スクリプトは変更しない。各タスクは「正確な文字列置換（Edit の old→new）→ grep/再読で着地検証 → コミット」の1サイクル。テスト＝文面が入り矛盾が残っていないことの grep 検証。

**Tech Stack:** Markdown プロンプトファイル。検証は Grep/Read のみ（ビルド・実行なし）。

## Global Constraints

- 編集対象は `tools/detail-design-doc/SKILL.md` と `tools/detail-design-doc/template.md` の2ファイルのみ。`example.md` / `example.html` / `scripts/build_html.py` は変更しない。
- 既存の章立て・見出し・表の列順（型）を勝手に変えない。追加は指定箇所のみ。
- 日本語文面は本計画の new_string をそのまま使う（アクセント・約物含め逐字）。
- コミットメッセージ末尾に必ず:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- ブランチは master。ユーザーが push を指示するまで push しない。

---

### Task 1: SKILL.md Step 1 — 判定軸を集合包含テストに是正

**Files:**
- Modify: `tools/detail-design-doc/SKILL.md`（Step 1、l.45-46 と l.54-59 付近）

**Interfaces:**
- Produces: `本機能画面集合` の定義と「集合包含テスト」の語。Task 2/3/5 がこの語（判定根拠・状態=未作成→§11未処理）を参照する。

- [ ] **Step 1: 判定の導入文を「数える」→「洗い出す＋帰属で判定」に置換**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
**子画面を「専属」と「共有」に判別する（設計書の範囲確定。重要）。** 対象画面が開く子画面を列挙し、各子画面クラスの**全開放点（どこから開かれるか）**を数える。
```
new_string:
```
**子画面を「専属」と「共有」に判別する（設計書の範囲確定。重要）。** 対象画面が開く子画面を列挙し、各子画面クラスの**全開放点（どこから開かれるか）**を洗い出す。**判定は開放点の「数」ではなく「帰属」で行う（下記の集合包含テスト）。** 開放点の洗い出しを漏れなく行うのは見落とし防止のためであり、開放点が多いこと自体は判定材料ではない。
```

- [ ] **Step 2: 分類ブロック（専属/共有の bullet）を集合包含テストに差し替え**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
判定に使った経路と根拠は第11章に残す。以上で得た**全開放点**を次で分類する:

- **専属画面**（全開放点が対象画面/機能の画面群の内側だけ。単独では業務的意味を持たない子ダイアログ）→ **本設計書に取り込み、章を設けて詳細化する**（Step 7）。§2.2 では表(A)に本書内の章参照付きで載せる。**「別設計書」に外出ししない**（存在しない設計書への参照＝断リンクを作らない）。
- **共有画面**（対象画面/機能の外からも開かれる汎用画面。患者検索・職員検索・定型文テンプレート等）→ 従来どおり**別設計書**。§2.2 では表(B)に存在と入出力の要点のみ。
- 判別が曖昧なものは保守的に**共有として扱い、無理に取り込まない**（第11章に判別根拠を残す）。
- 専属画面がさらに専属の孫画面を開く場合も同様に取り込む（同一出力フォルダ・index に親子階層を反映）。ただし取り込みは「対象機能に閉じる」範囲まで。深追いで無関係画面まで巻き込まない。
```
new_string:
```
判定に使った経路と根拠は第11章に残す。以上で得た**全開放点**を、次の**集合包含テスト**で分類する。

**まず `本機能画面集合` を定義する** = 本設計書の対象画面 ＋ 本設計書に取り込む専属画面（その専属の孫画面も再帰的に含む）。「感覚的に関連」ではなく、起点＋取り込む専属子孫という**閉じた列挙可能な集合**であることが濫用防止の要。この集合に対し:

- **専属画面**（全開放点が `本機能画面集合` の内側に収まる ⊆。入口が N 個あってもすべて機能内なら専属。単独では業務的意味を持たない子ダイアログ）→ **本設計書に取り込み、章を設けて詳細化する**（Step 7）。§2.2 では表(A)に本書内の章参照付きで載せる。**「別設計書」に外出ししない**（存在しない設計書への参照＝断リンクを作らない）。
- **共有画面**（`本機能画面集合` の**外側**からの開放点が**1つでもあれば**共有。外部画面が業務的に関連するか否かは問わない。患者検索・職員検索・定型文テンプレート等）→ 従来どおり**別設計書**。§2.2 では表(B)に存在・入出力の要点に加え**判定根拠（機能外のどの開放点で共有としたか）・別設計書の状態**を記す（状態=未作成 は第11章 `未処理` へ回落）。
- **判据の本質は「機能外からの開放点が存在するか（二値）」であり「何回呼ばれるか」ではない。** 複数入口を持つだけの専属子ダイアログ（一覧のツールバー／右クリック／ダブルクリックから開く編集ダイアログ等）を、入口数を理由に共有と誤判定しない。
- 判別が曖昧なもの（ある開放点が集合外かどうか確信が持てない場合。入口が多いことは「曖昧」ではない）は保守的に**共有として扱い、無理に取り込まない**（判定根拠を第11章に残す）。
- 専属画面がさらに専属の孫画面を開く場合も同様に取り込む（同一出力フォルダ・index に親子階層を反映）。ただし取り込みは「対象機能に閉じる」範囲まで。深追いで無関係画面まで巻き込まない。
```

- [ ] **Step 3: 着地検証（grep）**

Run: `grep -n "集合包含テスト\|本機能画面集合\|機能外からの開放点が存在するか" tools/detail-design-doc/SKILL.md`
Expected: 3 語がヒットする（少なくとも各1行）。

- [ ] **Step 4: 矛盾がないことの確認（grep）**

Run: `grep -n "全開放点を次で分類する" tools/detail-design-doc/SKILL.md`
Expected: ヒットなし（旧文が消えている）。

- [ ] **Step 5: Commit**

```bash
git add tools/detail-design-doc/SKILL.md
git commit -m "$(cat <<'EOF'
feat(detail-design-doc): 共有/専属判定を集合包含テストに是正

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: template.md §2.2 表(B) — 判定根拠・別設計書の状態 列を追加

**Files:**
- Modify: `tools/detail-design-doc/template.md`（§2.2 コメント l.60-62、表(B) ヘッダ l.71-72）

**Interfaces:**
- Consumes: Task 1 の `本機能画面集合`・状態=未作成→§11 の語。
- Produces: 表(B) の列「判定根拠」「別設計書の状態（既存/未作成/対象外）」。Task 3（Step 8/10 チェック）が参照。

- [ ] **Step 1: (B) のガイドコメントを更新**

Edit `tools/detail-design-doc/template.md`:

old_string:
```
     (B) 共有画面 = 複数の無関係な画面から開かれる汎用画面（患者検索・職員検索・定型文テンプレート等）。
         別設計書とし、ここでは存在と入出力の要点のみ記す。
     専属/共有の判別が曖昧なものは保守的に (B) 共有として扱い、無理に取り込まない。 -->
```
new_string:
```
     (B) 共有画面 = 本機能画面集合（対象画面＋取り込む専属子孫の閉集合）の外側からの開放点が
         1つでもある画面（患者検索・職員検索・定型文テンプレート等）。別設計書とし、ここでは
         存在・入出力の要点に加え「判定根拠（機能外のどの開放点で共有としたか）」と
         「別設計書の状態」を記す。状態は 既存/未作成/対象外 の3値。状態=未作成 のものは
         第11章 `未処理` に一元集約する（本表の状態列＝構造化された事実記録、第11章＝人間向け行動総账）。
     専属/共有の判別が曖昧（ある開放点が集合外か確信が持てない）なものは保守的に (B) 共有として扱う。 -->
```

- [ ] **Step 2: 表(B) のヘッダに2列追加**

Edit `tools/detail-design-doc/template.md`:

old_string:
```
| 遷移先 / 連動先 | 契機 | 受け渡す情報 | 参照（別設計書ID等） |
|---|---|---|---|
```
new_string:
```
| 遷移先 / 連動先 | 契機 | 受け渡す情報 | 判定根拠（機能外のどの開放点で共有としたか） | 参照（別設計書ID等） | 別設計書の状態（既存/未作成/対象外） |
|---|---|---|---|---|---|
```

- [ ] **Step 3: 着地検証（grep）**

Run: `grep -n "別設計書の状態（既存/未作成/対象外）\|判定根拠（機能外のどの開放点で共有としたか）" tools/detail-design-doc/template.md`
Expected: 2 語ともヒット（表ヘッダとコメントで複数行）。

- [ ] **Step 4: 旧ヘッダが消えたことの確認**

Run: `grep -n "受け渡す情報 | 参照（別設計書ID等） |$" tools/detail-design-doc/template.md`
Expected: ヒットなし。

- [ ] **Step 5: Commit**

```bash
git add tools/detail-design-doc/template.md
git commit -m "$(cat <<'EOF'
feat(detail-design-doc): §2.2表(B)に判定根拠・別設計書の状態列を追加

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: SKILL.md Step 7/8/10 — 未作成共有画面の一元収集フック

**Files:**
- Modify: `tools/detail-design-doc/SKILL.md`（Step 7 末尾 l.112、Step 8 末尾 l.127、Step 10 出力 l.163）

**Interfaces:**
- Consumes: Task 2 の表(B) 状態列、Task 5 の第11章 `未処理` 分類。
- Produces: Step 8 の網羅チェック項目、Step 10 の共有未作成チェック。

- [ ] **Step 1: Step 7 に index の要確認集約案内を追記**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
分割の有無に関わらず、`00_index.md`（単一なら巻末）に**付録A 解析対象ファイル一覧**を必ず含める（取り込んだ専属画面の解析ファイルも含める）。file:line が必要なら付録Bに最小限。
```
new_string:
```
分割の有無に関わらず、`00_index.md`（単一なら巻末）に**付録A 解析対象ファイル一覧**を必ず含める（取り込んだ専属画面の解析ファイルも含める）。file:line が必要なら付録Bに最小限。**要確認事項（未確認・理解不完全・未処理・低信頼）は第11章に一元集約する**ため、分割出力では `00_index.md` の目次に「要確認事項は §11（`05_医療安全.md`）に一元集約」と1行案内し、収集点の所在を明示する。
```

- [ ] **Step 2: Step 8 網羅チェックに2項目を追加**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
- 未確認のまま埋めた箇所がないか（あれば第11章へ移す）
```
new_string:
```
- §2.2 表(B) の各行に「判定根拠」「別設計書の状態」があり、状態=`未作成` の共有画面がすべて第11章 `未処理` 分類に現れているか（共有への外出しが根拠・状態つきで追跡可能か）
- 要確認事項（未確認・理解不完全・未処理・低信頼）が第11章に一元集約されているか。各所の放棄点（追い切れない・打切り・判定保留）から第11章に1行ずつ回落しているか
- 未確認のまま埋めた箇所がないか（あれば第11章へ移す）
```

- [ ] **Step 3: Step 10 出力に共有未作成チェックを追記**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
出力: `<出力先>/_selfcheck.md`。spec-impl-reconcile と同じ分類コード（A1/A2/A3/B/C/D/E）・深刻度・対処区分で、**1行1件の表**にする。医療安全に触れる差異は行頭 `【医療安全】`。末尾に「本自己校验は複用＋3類の定点深読に限定。網羅的な突合は spec-impl-reconcile を使うこと」と限界を明記する。差異が見つかれば md 本体を修正し、必要なら HTML を再生成する（Step 9）。
```
new_string:
```
出力: `<出力先>/_selfcheck.md`。spec-impl-reconcile と同じ分類コード（A1/A2/A3/B/C/D/E）・深刻度・対処区分で、**1行1件の表**にする。医療安全に触れる差異は行頭 `【医療安全】`。末尾に「本自己校验は複用＋3類の定点深読に限定。網羅的な突合は spec-impl-reconcile を使うこと」と限界を明記する。差異が見つかれば md 本体を修正し、必要なら HTML を再生成する（Step 9）。加えて、**共有と判定したのに別設計書が未作成のもの**を1類として洗い出し、§2.2 表(B) の状態=`未作成` と第11章 `未処理` 分類に整合して現れているかを確認する（食い違えば md を修正する）。
```

- [ ] **Step 4: 着地検証（grep）**

Run: `grep -nF "要確認事項は §11" tools/detail-design-doc/SKILL.md; grep -nF "の共有画面がすべて第11章" tools/detail-design-doc/SKILL.md; grep -nF "共有と判定したのに別設計書が未作成" tools/detail-design-doc/SKILL.md`
Expected: 3 語すべて各1件ヒット（`-F` で固定文字列検索。バッククォートを避ける）。

- [ ] **Step 5: Commit**

```bash
git add tools/detail-design-doc/SKILL.md
git commit -m "$(cat <<'EOF'
feat(detail-design-doc): 未作成共有画面を第11章に一元集約するチェックを追加

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: SKILL.md よくある失敗表 — 2行追加

**Files:**
- Modify: `tools/detail-design-doc/SKILL.md`（よくある失敗表、`new` の Grep 行の直後）

**Interfaces:**
- Consumes: Task 1 の集合包含テスト、Task 2 の表(B) 列、Task 5 の §11 未処理。

- [ ] **Step 1: 失敗表に2行挿入**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
| `new` の Grep だけで開放点を数え、Factory/DI/反射経由の子画面・呼出元を取りこぼす | 開放点は new＋Factory＋DI＋**文字列型名の Grep**で数える。`new` 0件を「呼出なし・専属」と即断しない（Step 1・§2.1） |
```
new_string:
```
| `new` の Grep だけで開放点を数え、Factory/DI/反射経由の子画面・呼出元を取りこぼす | 開放点は new＋Factory＋DI＋**文字列型名の Grep**で数える。`new` 0件を「呼出なし・専属」と即断しない（Step 1・§2.1） |
| 全開放点が機能内なのに入口数が多いだけで共有と誤判定 | 判定は開放点の「帰属」で（集合包含テスト）。全開放点 ⊆ 本機能画面集合 なら入口 N 個でも専属。数で判定しない（Step 1） |
| 共有と判定した画面を根拠も状態も残さず別設計書へ外出しし、reviewer が未対応を検証できない | §2.2 表(B) に判定根拠・別設計書の状態（既存/未作成/対象外）を記し、状態=未作成 は第11章 `未処理` へ回落（Step 1・Step 8・§2.2） |
```

- [ ] **Step 2: 着地検証（grep）**

Run: `grep -n "入口数が多いだけで共有と誤判定\|根拠も状態も残さず別設計書へ外出し" tools/detail-design-doc/SKILL.md`
Expected: 2 行ともヒット。

- [ ] **Step 3: Commit**

```bash
git add tools/detail-design-doc/SKILL.md
git commit -m "$(cat <<'EOF'
feat(detail-design-doc): よくある失敗表に共有誤判定・外出し可視化の2行を追加

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: 第11章を「要人間確認の一元収集」に昇格（template.md §11 + SKILL.md 原則1）

**Files:**
- Modify: `tools/detail-design-doc/template.md`（§11 見出し・コメント・表 l.345-351）
- Modify: `tools/detail-design-doc/SKILL.md`（中核原則1 l.9 末尾）

**Interfaces:**
- Consumes: Task 1〜4 が参照する `未処理`/`理解不完全`/`低信頼`/`未確認` の4分類語。
- Produces: 第11章の4分類・triage 列・回落ルール。

- [ ] **Step 1: template.md §11 の見出し・コメント・表ヘッダを差し替え**

Edit `tools/detail-design-doc/template.md`:

old_string:
```
## 11. 未確認事項・申し送り
<!-- 確度=未確認（安全に判断できず本文に書けなかったもの）をすべてここに集約する。
     本文に残す〔推定〕（裏付けは無いが合理的に導ける記述）とは区別する:
     〔推定〕は本文に置き、未確認はここへ隔離する。 -->

| No | 内容 | 未確認の理由（どこまで追ったか） |
|---|---|---|
```
new_string:
```
## 11. 未確認事項・申し送り（要人間確認の一元収集）
<!-- この章は「AI が確定できなかった／処理しきれなかった／確信を持てなかった」事項を一元集約する
     唯一の収集点。人間はこの章を読めば、本設計書で人手の確認・判断が要る箇所を漏れなく把握できる。
     収集する4分類:
       未確認    = 安全に判断できなかった事実（テーブル/カラム/設定/文言の実在等）。従来どおり。
       理解不完全 = 追跡が途中（複雑ロジック/動的SQLを解ききれない、子画面の開放点を追い切れない等）。
       未処理    = スコープ外にしたが対応が要る依存（共有と判定し別設計書が未作成＝§2.2表(B)状態=未作成、
                   外部依存等）。§2.2 表(B) の該当行と交叉参照し、正文を重複させない。
       低信頼    = 〔推定〕を多用した／自動生成図（Mermaid 等）など置信度が低い区域。
     ★〔推定〕（裏付けは無いが合理的に導ける記述）は本文に置く。ここへ入れるのは真の gap のみ。
       「推断したもの全部」を倒し込まない（ダンプ化の防止）。確度分層 確定/推定/未確認 を維持する。
     ★影響列は必ず埋める（triage 用）。後工程の DDD 生成をブロックするか、医療安全に触れるかを明示。
       医療安全に触れる行は行頭に【医療安全】。
     ★本章が捉えるのは known gaps（自分が搞不定と分かっているもの）のみ。「搞定したつもりで誤り」
       （unknown unknowns）は捉えられない → spec-impl-reconcile の全量突合・人手の網羅確認で担保する。 -->

| No | 分類 | 内容 | 影響（後工程DDD生成/医療安全をブロックするか） | どこまで追ったか | 人間への依頼（何を確認/判断してほしいか） |
|---|---|---|---|---|---|
```

- [ ] **Step 2: SKILL.md 中核原則1 の末尾に一元収集ルールを追記**

Edit `tools/detail-design-doc/SKILL.md`:

old_string:
```
（幻覚の禁止）— 見つからなければ〔推定〕か第11章に落とす。
```
new_string:
```
（幻覚の禁止）— 見つからなければ〔推定〕か第11章に落とす。**第11章は「要人間確認の一元収集点」**であり、未確認だけでなく理解不完全（追い切れない）・未処理（共有と判定し別設計書が未作成 等）・低信頼も分類つきで回落する。各所の放棄点（打切り・追跡途中・判定保留）は必ず第11章に1行残す。ただし〔推定〕は本文に置き、真の gap のみ回落する（ダンプ化の防止）。
```

- [ ] **Step 3: 着地検証（grep）**

Run: `grep -n "要人間確認の一元収集\|理解不完全\|低信頼\|人間への依頼" tools/detail-design-doc/template.md`
Expected: 各語ヒット（表ヘッダ・コメント）。

Run: `grep -n "要人間確認の一元収集点" tools/detail-design-doc/SKILL.md`
Expected: 1 件ヒット。

- [ ] **Step 4: 旧表ヘッダが消えたことの確認**

Run: `grep -n "未確認の理由（どこまで追ったか）" tools/detail-design-doc/template.md`
Expected: ヒットなし。

- [ ] **Step 5: Commit**

```bash
git add tools/detail-design-doc/template.md tools/detail-design-doc/SKILL.md
git commit -m "$(cat <<'EOF'
feat(detail-design-doc): 第11章を要人間確認の一元収集（4分類・triage列）に昇格

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 完了条件（全タスク後の最終確認）

- [ ] `SKILL.md`: 集合包含テスト（本機能画面集合）・帰属判定・失敗表2行・Step 7/8/10 フック・原則1の一元収集ルールが入っている。
- [ ] `template.md`: §2.2 表(B) が6列（判定根拠・状態を含む）、第11章が「要人間確認の一元収集」で6列。
- [ ] `git status` が clean、`example.*` / `build_html.py` は無変更。
- [ ] 旧文（`全開放点を次で分類する` / 旧表(B)ヘッダ / `未確認の理由（どこまで追ったか）`）が残っていない。
