// テスト用フィクスチャ（実装側の"事実"）。spec-impl-reconcile の RED-GREEN 回帰用。
// 領域例＝C#/WinForms（本スキルは領域非依存だが、実在ゲート/子画面/サーバーコントロールを
// 実際に exercise するため具体例を置く）。設計書 spec/OrderEntry.md の主張とわざと食い違わせてある。
using System;

namespace Demo.Order
{
    // 実体：業務ロジックは Service/Repository ではなく旧サーバーコントロール直呼び。
    // 設計書は OrderService.ExecuteOrder() / IOrderRepository を中核と書く＝ハルシネーション。
    public class OrderEntryForm
    {
        private int _orderId;
        private object _lines;

        private void btnSave_Click(object sender, EventArgs e)
        {
            // 確認子画面：設計書のどこにも記載が無い＝A1（子画面欠落）候補。
            using (var dlg = new OrderConfirmDialog(_orderId))
            {
                if (dlg.ShowDialog() != DialogResult.OK) return;
            }

            // 保存：旧サーバーコントロール直呼び（OrderService/IOrderRepository は存在しない）。
            var result = Execute(typeof(CommonQuery_Order), "SaveOrder", _orderId, _lines);

            // 横断副作用：外部在庫システムへ送信。設計書の「外部連携」に記載が無い＝A2（横断ロジック欠落）候補。
            // 効果が本画面の外（在庫システム）へ波及するので A3 ではなく A2。
            InventoryNotifier.Send(_orderId, _lines);

            // 既知バグ：レシート印刷の例外を空catchで握り潰し（失敗が無通知）。
            // 設計書のバグ候補#1に既記載＝レビューで再報しないこと（スコープ／既知除外）。
            try { PrintReceipt(_orderId); }
            catch { }
        }

        // --- 以下はフィクスチャを成立させるためのダミー宣言（挙動は空） ---
        private object Execute(Type serverControl, string proc, params object[] args) => null;
        private void PrintReceipt(int orderId) { }
    }

    // 確認子画面（設計書に無い）。閲覧だけでなく明細の削除もできる＝子画面固有機能。
    public class OrderConfirmDialog : IDisposable
    {
        public OrderConfirmDialog(int orderId) { }
        public DialogResult ShowDialog() => DialogResult.OK;
        public void RemoveLine(int index) { }   // 親仕様に無い保守機能
        public void Dispose() { }
    }

    // ダミー：旧サーバーコントロール・外部通知・列挙。
    public class CommonQuery_Order { }
    public static class InventoryNotifier { public static void Send(int id, object lines) { } }
    public enum DialogResult { OK, Cancel }
}
