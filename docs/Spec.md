# SPEC - AURUMQUANT AI TRADING PLATFORM

**Phiên bản:** 2.0  
**Ngày cập nhật:** 2026-06-17  
**Nguồn thiết kế chính:** giao diện `quant-command/`  
**Nguồn nghiệp vụ:** tài liệu trong `docs/` về XAU/USD, backtest, chiến lược và kiểm chứng mô hình  
**Thị trường ưu tiên:** XAU/USD  
**Mở rộng sau MVP:** Forex, Crypto, Indices, Commodities, Stocks  

---

# 1. Tầm Nhìn Sản Phẩm

AurumQuant AI là nền tảng nghiên cứu, kiểm chứng và vận hành giao dịch định lượng. Sản phẩm không chỉ là bot vào lệnh, mà là một command center cho toàn bộ vòng đời trading:

1. Thu thập và kiểm định dữ liệu thị trường.
2. Xây dựng chiến lược và mô hình AI.
3. Backtest sát điều kiện thực tế.
4. Kiểm chứng bằng Out-of-Sample, Walk-Forward, Monte Carlo và stress test.
5. Paper Trading trước khi Live.
6. Giao dịch Live qua MetaTrader 5 với Risk Engine độc lập.
7. Giám sát agent, lệnh, rủi ro, cảnh báo, audit log và tích hợp vận hành.

Nền tảng không được định vị là công cụ bảo đảm lợi nhuận. Mục tiêu là tìm kiếm edge có cơ sở thống kê, kiểm chứng được sau chi phí giao dịch, và chỉ triển khai khi Risk Engine cho phép.

---

# 2. Nguyên Tắc Bắt Buộc

## 2.1. Validation First

Không chiến lược hoặc mô hình nào được chạy Live chỉ vì Net Profit cao. Deployment Gate phải xét tối thiểu:

* Out-of-Sample performance.
* Walk-Forward consistency.
* Cost sensitivity.
* Max Drawdown.
* Profit Factor.
* Expectancy sau spread, slippage, commission, swap.
* Số lượng giao dịch đủ lớn.
* Paper/Forward test.
* Data leakage check.
* Overfitting check.

## 2.2. Risk Engine Độc Lập

AI Agent, Strategy Engine và Copilot chỉ đề xuất hành động. Risk Engine có quyền:

* Từ chối lệnh.
* Giảm volume.
* Chặn entry mới.
* Pause agent.
* Kích hoạt Emergency Stop.
* Đưa hệ thống về monitoring-only mode.

Không module nào được ghi trực tiếp vào Execution Gateway nếu chưa có RiskDecision hợp lệ.

## 2.3. Backtest-Live Parity

Logic tạo tín hiệu trong Backtest, Paper và Live phải dùng cùng một Strategy Interface. Khác biệt giữa môi trường chỉ nằm ở data source, execution adapter và trạng thái thật/giả lập.

## 2.4. Không Dùng Dữ Liệu Tương Lai

Bắt buộc kiểm tra:

* Không random split hoặc shuffle time series.
* Scaler chỉ fit trên Train Set.
* Indicator không dùng future bar.
* Không dùng high/low của candle chưa đóng như dữ liệu đã biết.
* Label horizon không rò rỉ qua boundary Train/Validation/Test.
* Không decomposition/DWT trên toàn chuỗi trước khi split.

## 2.5. XAU/USD Là Trọng Tâm MVP

Theo tài liệu nghiên cứu, XAU/USD có spread biến động, slippage cao, dễ fake breakout và rất nhạy với CPI, NFP, FOMC. MVP phải ưu tiên:

* Spread filter.
* News blackout.
* Session filter London/New York.
* ATR-based SL/TP.
* Hard risk per trade.
* No-trade decision khi tín hiệu không đủ chắc.

---

# 3. Phạm Vi MVP

## 3.1. Chức Năng Có Trong MVP

MVP phải hiện thực toàn bộ bề mặt chức năng đang có trong UI `quant-command`:

* App Shell, Top Bar, Sidebar, Bottom Terminal, AI Copilot.
* Command Center.
* Live Trading Workspace.
* Portfolio.
* Orders & Positions.
* AI Models.
* Strategy Lab.
* Backtesting.
* Risk Management Center.
* Market Data.
* Alerts.
* Activity Logs / Audit Trail.
* Integrations.
* Settings / Roles & Permissions.

## 3.2. Chiến Lược Ưu Tiên

Ba hướng đáng làm trước:

1. **Mean Reversion M5 cho XAU/USD**  
   Dễ bắt đầu nhất, phù hợp scalping vàng khi có spread/news/session filter.

2. **ML Liquidity Sweep / Setup Classifier**  
   Không dự báo giá tuyệt đối, mà phân loại setup: Buy, Sell, No Trade, Low Quality.

3. **HMM Regime Filter + Strategy Switching**  
   Nhận diện Trend, Sideway, High Volatility, News Shock, Uncertain để chọn chiến lược hoặc đứng ngoài.

RL Agent như PPO/SAC/TD3 được giữ trong roadmap nâng cao, nhưng UI đã phải hỗ trợ trạng thái model, reward builder, validation score, live drift và deployment gate.

---

# 4. Kiến Trúc Tổng Thể

```text
Web UI quant-command
      |
API Gateway
      |
Auth / RBAC / Session Context
      |
Application Services
      |
+----------------------+----------------------+----------------------+
| Market Data Service  | Research Service     | Trading Service      |
| Feed Integrity       | Strategy Registry    | Signal Engine        |
| Dataset Versioning   | Model Registry       | Risk Engine          |
| News Calendar        | Backtest Engine      | Execution Gateway    |
+----------------------+----------------------+----------------------+
      |
Storage / Queue / Audit / Alerting
      |
MT5 Gateway / Discord / TradingView / DeepSeek Copilot
```

## 4.1. Môi Trường Vận Hành

UI có selector môi trường:

* `Backtest`
* `Paper`
* `Live`

Khi chọn `Live`, Top Bar phải hiển thị cảnh báo `REAL MONEY`. Các hành động có tác động tiền thật phải yêu cầu xác nhận rõ ràng, được audit và tùy quyền có thể yêu cầu 2FA hoặc approval.

## 4.2. Account Context

Người dùng có thể đổi account trên Top Bar. Account có các loại:

* Demo.
* Prop.
* Live.
* Research.

Thông tin hiển thị:

* Broker.
* Server.
* Masked account number.
* Balance.
* Equity.
* Free margin.
* Margin level.
* Floating PnL.
* Daily PnL.
* Latency.
* Market status.

Password, token và private credential không bao giờ hiển thị lại trong UI hoặc log.

---

# 5. App Shell Và Điều Hướng

## 5.1. Sidebar

Sidebar là điều hướng chính gồm:

* Command Center.
* Live Trading.
* Portfolio.
* Orders & Positions.
* AI Models.
* Strategy Lab.
* Backtesting.
* Risk Management.
* Market Data.
* Alerts.
* Activity Logs.
* Integrations.
* Settings.

Sidebar có trạng thái thu gọn/mở rộng và status mini cho:

* MT5.
* Discord.
* AI Engine.

Các status này phải lấy từ backend health check thay vì hard-code.

## 5.2. Top Bar

Top Bar phải cung cấp:

* Environment selector.
* Live money warning.
* Account selector.
* Broker/server/account mask.
* Balance/equity/free margin/margin level.
* Floating PnL và Daily PnL.
* Latency.
* Market open/closed.
* Clock realtime.
* Emergency Stop button.

Top Bar là vùng luôn hiển thị, vì nó chứa context rủi ro trước mọi hành động.

## 5.3. Bottom Terminal

Bottom Terminal hiển thị nhanh:

* Positions.
* Pending orders.
* History.
* AI Decisions.
* Risk Logs.
* System Logs.

Terminal có thể đóng/mở. Dữ liệu phải stream hoặc polling realtime. Mỗi dòng log cần correlation ID để nối signal, risk decision và order execution.

---

# 6. AI Copilot

## 6.1. Mục Đích

Copilot là trợ lý vận hành giúp người dùng:

* Hỏi lý do agent chưa vào lệnh.
* Phân tích thị trường hiện tại.
* Giải thích last trade.
* Tạo daily report.
* Yêu cầu pause agent, reduce risk, move SL to break-even.
* Thực hiện quick backtest.
* Xử lý lệnh đến từ Discord cần approval.

## 6.2. Provider

Copilot dùng **DeepSeek API** thông qua backend proxy.

Yêu cầu cấu hình:

```text
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

Không ghi API key thật vào source code, Spec, frontend bundle, log hoặc audit. Frontend chỉ gọi endpoint nội bộ như:

```text
POST /api/copilot/chat
POST /api/copilot/commands/simulate
POST /api/copilot/commands/confirm
POST /api/copilot/commands/reject
```

Nếu chưa có key hoặc provider lỗi, hệ thống được phép fallback sang mock/local response nhưng phải hiển thị trạng thái degraded.

## 6.3. Context Copilot

Mỗi request gửi Copilot phải có context được kiểm soát:

* Environment.
* Account ID đã mask.
* Symbol.
* Timeframe.
* Active strategy/model.
* Session.
* Open positions summary.
* Risk state.
* Recent alerts.
* Permission scope của user.

Không gửi credential, password, raw API key, full account number hoặc dữ liệu nhạy cảm không cần thiết.

## 6.4. Command Confirmation

Nếu Copilot hoặc Discord tạo hành động có tác động giao dịch, UI phải hiển thị Confirmation Card:

* Action.
* Account.
* Environment.
* Positions affected.
* Total volume.
* Current PnL.
* Estimated slippage.
* Buttons: Simulate, Modify, Reject, Confirm.

Trong `Live`, nút confirm phải ghi rõ `Confirm LIVE` và có thể yêu cầu permission cao hơn. Tất cả kết quả `simulated`, `executed`, `rejected` phải audit.

---

# 7. Command Center

## 7.1. Mục Đích

Command Center là dashboard tổng quan realtime về tài khoản, AI agents, positions và risk.

## 7.2. Metrics Bắt Buộc

Nhóm account/performance:

* Balance.
* Equity.
* Floating PnL.
* Day PnL.
* Week PnL.
* Month PnL.
* Drawdown và Max Drawdown.
* Win Rate.
* Profit Factor.
* Sharpe.
* Sortino.
* Exposure.
* Margin Usage.
* Realized PnL.

Metric phải có timestamp dữ liệu cuối cùng. Nếu stale, UI phải cảnh báo.

## 7.3. AI Agents

Agent card phải hiển thị:

* Name.
* Symbol.
* Timeframe.
* Model.
* Status: Running, Paused, Waiting, Error.
* Current action: Buy, Sell, Hold.
* Confidence.
* Regime.
* Reward.
* Trades today.
* Daily PnL.
* Drawdown.
* Latency.
* Last update.

Hành động:

* Pause agent.
* Resume agent.
* Open more actions menu.

Pause/Resume phải qua quyền RBAC và audit.

## 7.4. Live Positions

Sử dụng cùng bảng Positions toàn hệ thống. Command Center chỉ hiển thị subset đang mở và summary:

* Open count.
* Total lots.
* Open risk.

## 7.5. Risk Monitor

Risk Monitor hiển thị score `/100`, risk level và từng risk metric. Nếu High Risk hoặc Critical, Command Center phải ưu tiên cảnh báo rõ.

---

# 8. Live Trading Workspace

## 8.1. Mục Đích

Live Trading Workspace là màn hình thao tác trực tiếp với symbol/session/model hiện tại, ví dụ:

```text
XAUUSD · M5 · PPO-v12 · London Session · Strategy active
```

## 8.2. Chart

Chart phải hỗ trợ:

* Symbol/timeframe.
* OHLC candles.
* Volume hoặc tick volume.
* AI markers: entry-buy, entry-sell, exit.
* Marker label gồm action, volume, model, confidence, PnL nếu exit.
* Spread/regime/news overlay trong các phiên bản sau.

## 8.3. Manual Order Panel

Manual Order Panel phải có:

* Symbol selector.
* Buy/Sell quote buttons.
* Order type: Market, Limit, Stop.
* Volume.
* Entry.
* Stop Loss.
* Take Profit.
* Risk percent.
* Risk amount.
* R:R.
* Estimated spread.
* Estimated commission.
* Estimated margin.
* Max loss.
* Max profit.

Quick tools:

* Auto lot.
* SL by ATR.
* TP by R:R.
* Break-even.
* Trailing.
* AI manage.

Primary action là `Review`, không gửi lệnh trực tiếp. Sau Review, lệnh phải qua:

```text
Order Draft -> Simulation -> RiskDecision -> User Confirmation -> Execution
```

## 8.4. Positions

Live Trading phải hiển thị positions đang mở cho symbol/account hiện tại, có khả năng filter theo strategy, agent hoặc manual.

---

# 9. Portfolio

## 9.1. Mục Đích

Portfolio hiển thị phân tích hiệu suất theo tài khoản, symbol, strategy, model và session.

## 9.2. Biểu Đồ Bắt Buộc

* Equity Curve.
* Drawdown.
* PnL by Symbol.
* Daily PnL Heatmap.

## 9.3. Metrics Mở Rộng

Backend phải hỗ trợ tính:

* Daily/weekly/monthly return.
* CAGR.
* Volatility.
* Sharpe.
* Sortino.
* Calmar.
* Profit Factor.
* Expectancy.
* Max Drawdown.
* Drawdown duration.
* PnL by strategy.
* PnL by model.
* PnL by regime.
* PnL by session: Asia, London, New York.

---

# 10. Orders & Positions

## 10.1. Tabs

Màn hình phải có các tab:

* Open.
* Pending.
* Closed.
* Rejected.
* AI Suggestions.
* Manual.
* Strategy.

## 10.2. Filters

Filters tối thiểu:

* Account.
* Symbol.
* Strategy.
* Model.
* Side.
* Date range.
* AI / Manual.
* Environment.

## 10.3. Position Columns

Bảng positions phải có:

* Symbol.
* Ticket.
* Side.
* Volume.
* Entry.
* Current price.
* SL.
* TP.
* PnL.
* Swap.
* Commission.
* Duration.
* Strategy.
* Agent.
* Confidence.
* Risk%.
* Action menu.

## 10.4. Rejected Orders

Rejected tab phải hiển thị rõ lý do, ví dụ:

```text
ORDER_BLOCKED margin_level (114% < 150%)
```

Không được chỉ hiển thị lỗi chung chung.

---

# 11. AI Models

## 11.1. Mục Đích

AI Models là registry của model dùng bởi agents và strategies.

## 11.2. Model Card

Mỗi model hiển thị:

* Name.
* Algorithm.
* Version.
* Trained date.
* Status: Live, Paper Trading, Approved, Training, Validating, Paused, Deprecated, Failed, Draft.
* Backtest Sharpe.
* Live Sharpe.
* Validation Score.
* Backtest MaxDD.
* Live DD.
* Drift.
* Last retrain.
* Training steps.

## 11.3. Model Gate

Model chỉ được Approved/Live nếu:

* Không có data leakage.
* OOS metrics đạt ngưỡng.
* Trading metrics đạt ngưỡng, không chỉ ML accuracy.
* Drift dưới ngưỡng.
* Có backtest sau chi phí.
* Có Paper Trading hoặc forward validation nếu dùng Live.

Nếu accuracy tốt nhưng expectancy âm, model phải được đánh dấu:

```text
PREDICTIVELY_VALID
TRADING_INVALID
```

---

# 12. Strategy Lab

## 12.1. Wizard

Strategy Lab là wizard gồm:

1. Market.
2. Data.
3. Features.
4. Model.
5. Actions.
6. Reward.
7. Risk.
8. Execution.
9. Backtest.
10. Paper.
11. Deploy.

Mỗi bước phải lưu draft và có trạng thái hoàn thành.

## 12.2. Reward Function Builder

UI hiện có Reward Builder cho RL. Backend phải lưu được reward components:

* Net profit.
* Risk-adjusted profit.
* Drawdown penalty.
* Transaction cost penalty.
* Slippage penalty.
* Holding-time penalty.
* Overtrading penalty.
* Exposure penalty.
* Volatility penalty.
* Stop-loss penalty.
* Reward for correct hold.
* Reward for avoiding bad trades.
* Stable equity growth.

Reward formula phải version hóa. Thay đổi weight tạo Strategy/Model config version mới.

## 12.3. Strategy Templates

MVP cần ít nhất:

### XAU/USD M5 Mean Reversion

Entry Buy:

* Candle đã đóng.
* Giá chạm/phá Bollinger Band dưới.
* RSI oversold.
* Z-score âm vượt ngưỡng.
* Wick dưới đủ lớn hoặc liquidity sweep.
* Không ở High-Volatility Trend chống hướng.
* Spread dưới ngưỡng.
* Không trong news blackout.
* Risk Engine còn room.

Entry Sell:

* Candle đã đóng.
* Giá chạm/phá Bollinger Band trên.
* RSI overbought.
* Z-score dương vượt ngưỡng.
* Wick trên đủ lớn hoặc liquidity sweep.
* Không ở High-Volatility Trend chống hướng.
* Spread dưới ngưỡng.
* Không trong news blackout.

Exit:

* Giá hồi về middle band.
* TP.
* SL.
* Time stop.
* Regime đổi.
* Risk Engine yêu cầu giảm/đóng.

### ML Liquidity Sweep Classifier

Input features:

* OHLC.
* ATR.
* RSI.
* MACD.
* Bollinger Band width.
* EMA distance.
* Body ratio.
* Wick ratio.
* Previous high/low distance.
* Session.
* Spread.
* Tick volume.
* Regime.

Labels:

* Buy setup.
* Sell setup.
* No trade.
* Low-quality setup.

Model phải được đánh giá bằng Precision/Recall/F1/PR-AUC và Trading Expectancy sau chi phí.

### HMM Regime Filter

States có thể được gắn nhãn:

* Trend Up.
* Trend Down.
* Sideway.
* High Volatility.
* Low Volatility.
* News Shock.
* Uncertain.

Nếu xác suất state thấp hoặc thay đổi liên tục, regime là `UNCERTAIN` và mặc định No Trade.

---

# 13. Backtesting

## 13.1. Configuration

Màn hình Backtesting phải hỗ trợ:

* Strategy.
* Model.
* Symbol.
* Timeframe.
* Date range.
* Capital.
* Spread.
* Commission.
* Swap.
* Slippage.
* Latency.
* Leverage.
* Train percentage.
* Validation percentage.
* Test percentage.
* Walk-forward config.
* Monte Carlo count.
* Seed.

## 13.2. Run Backtest

Nút `Run Backtest` tạo job:

```text
Queued -> Loading Data -> Validating Data -> Calculating Features -> Training/Loading Model -> Simulating -> Calculating Metrics -> Completed/Failed
```

Job có thể chạy async và trả progress realtime.

## 13.3. Equity Chart

Equity chart phải phân biệt:

* In-sample.
* Validation.
* Out-of-sample.

Không được gộp các giai đoạn làm người dùng hiểu nhầm.

## 13.4. Metrics Bắt Buộc

Backtest results phải có:

* Net Profit.
* CAGR.
* Sharpe.
* Sortino.
* Calmar.
* Max DD.
* Profit Factor.
* Expectancy.
* Win Rate.
* Average Win.
* Average Loss.
* Trades.
* Turnover.
* Recovery.

Mở rộng:

* Spread cost.
* Commission cost.
* Slippage cost.
* Swap cost.
* Profit before cost.
* Profit after cost.
* Monthly heatmap.
* Trade distribution.
* Return distribution.
* Regime performance.
* Session performance.
* Monte Carlo ruin probability.
* Parameter stability.

## 13.5. Backtest Tiêu Chuẩn

Backtest cho XAU/USD phải có:

1. Dữ liệu OHLC, spread, volume/tick volume.
2. Time split, không random split.
3. Feature tính không dùng tương lai.
4. Cost model gồm spread, slippage, commission, swap.
5. Walk-forward validation.
6. Stress test với spread x2, slippage x2, tin mạnh, trend một chiều, sideway dài, loss streak.
7. Báo cáo lỗi data leakage và overfitting.

---

# 14. Risk Management Center

## 14.1. Mục Đích

Risk Management Center quản lý hard rules, circuit breakers và monitoring.

## 14.2. Risk Rules

UI hiện có các rule sau, backend phải hỗ trợ tối thiểu:

* Max risk per trade.
* Max daily loss.
* Max weekly loss.
* Max drawdown.
* Max account exposure.
* Max symbol exposure.
* Max correlated exposure.
* Max positions.
* Max trades/day.
* Max lot size.
* Min margin level.
* Max spread.
* Max slippage.
* No trading near news.
* Allowed sessions.
* Cooldown after loss streak.
* Stop on latency anomaly.
* Stop on MT5 disconnect.
* Stop on feed mismatch.
* Stop on model drift.

Mỗi rule có:

* Enabled.
* Threshold.
* Warning.
* Critical.
* Action.
* Priority.

Một số system-level rules phải là `NON_OVERRIDABLE`.

## 14.3. Risk Monitor

Risk Monitor dùng chung toàn hệ thống:

* Daily Loss.
* Current Drawdown.
* Max Drawdown.
* Risk Per Trade.
* Total Open Risk.
* Margin Usage.
* Consecutive Losses.
* Spread Anomaly.

Risk score phải có giải thích, không chỉ là số.

---

# 15. Market Data

## 15.1. Market Watch

Market Data hiển thị:

* Symbol.
* Bid.
* Ask.
* Spread.
* Volatility.
* Tick rate.
* Latency.
* Feeds.

Các feeds gồm tối thiểu:

* MT5 Broker Feed.
* TradingView Feed.
* External Provider.

## 15.2. Feed Integrity

Hệ thống phải so sánh feed và phát hiện mismatch, ví dụ XAUUSD External feed lệch MT5 4.2pt. Khi mismatch vượt ngưỡng:

* Cảnh báo Market Data.
* Block hoặc downgrade Live Trading cho symbol.
* Ghi RiskEvent.

## 15.3. Economic Calendar

Calendar phải hỗ trợ các event quan trọng:

* CPI.
* NFP.
* FOMC.
* ECB.
* Retail Sales.

News blackout phải kết nối trực tiếp với Risk Engine.

---

# 16. Alerts

## 16.1. Sources

Alerts gom các nguồn:

* Trading.
* Risk.
* Model.
* Market.
* MT5.
* Discord.
* System.
* Security.

## 16.2. Alert Table

Columns:

* Severity: Critical, High, Medium, Low, Info.
* Source.
* Account.
* Agent.
* Symbol.
* Time.
* Message.
* Status: Open, Ack, Resolved.
* Actions.

Actions:

* Ack.
* Resolve.
* Mute.
* Ask AI.

Critical alert không được bị mute vĩnh viễn nếu liên quan tiền thật hoặc execution.

---

# 17. Activity Logs / Audit Trail

## 17.1. Mục Đích

Audit Trail là bản ghi bất biến của signal, approval, execution và rule change.

## 17.2. Columns

* Timestamp.
* User / Service.
* Source.
* Account.
* Action.
* Previous -> Next.
* Result: OK, REJECTED, PENDING.
* Correlation ID.
* Latency.

## 17.3. Hành Động Bắt Buộc Audit

* Bật/tắt Live Auto Trade.
* Pause/resume agent.
* Emergency Stop.
* Close all positions.
* Cancel pending orders.
* Manual order confirm.
* AI command confirm/reject.
* Discord command approval.
* Risk rule change.
* Model deploy/deprecate.
* Strategy deploy.
* Integration reconnect.
* Permission change.

Audit log không được ghi password, API key hoặc secret.

---

# 18. Integrations

## 18.1. MetaTrader 5

Thông tin hiển thị:

* Status.
* Broker.
* Server.
* Account mask.
* Heartbeat.
* Ping.
* Execution enabled/disabled.

Actions:

* Reconnect.
* Test.

MT5 Gateway phải hỗ trợ:

* Account sync.
* Quote sync.
* Order send.
* Order status.
* Position sync.
* Reconciliation sau reconnect/restart.
* Magic number/ownership.

## 18.2. Discord

Thông tin hiển thị:

* Bot status.
* Server.
* Channel.
* Synced users.
* Allowed commands.
* Approval required.
* Notifications.

Discord command có tác động trading phải qua confirmation trong Web UI hoặc approval policy tương đương.

## 18.3. TradingView

Thông tin hiển thị:

* Provider.
* Symbol map.
* Timeframe map.
* Webhooks.
* Alert sync.

TradingView webhook không được trực tiếp vào lệnh Live. Nó chỉ tạo signal/suggestion để Risk Engine xử lý.

## 18.4. DeepSeek

DeepSeek là provider Copilot:

* Health check.
* Model name.
* Token/error usage.
* Rate limit state.
* Fallback state.

API key chỉ nằm ở backend secret/env.

---

# 19. Settings / Roles & Permissions

## 19.1. Roles

UI hiện có roles:

* Owner.
* Admin.
* Quant Researcher.
* Trader.
* Risk Manager.
* Viewer.
* Discord Operator.

## 19.2. Permissions

Permissions:

* View dashboards.
* Execute trades.
* Approve AI actions.
* Pause agents.
* Modify risk rules.
* Deploy models.
* Manage integrations.
* Emergency stop.
* View audit log.

## 19.3. RBAC Rules

* Viewer không được trade.
* Trader không được sửa risk rules.
* Quant Researcher được deploy model theo policy nhưng không được execute Live nếu thiếu quyền.
* Risk Manager được modify risk rules và emergency stop.
* Discord Operator chỉ được gửi command trong phạm vi allowed commands và vẫn cần approval nếu policy yêu cầu.
* Emergency Stop là quyền riêng, không tự động gắn cho mọi trader.

---

# 20. Emergency Stop

## 20.1. UI Flow

Emergency Stop nằm ở Top Bar và mở dialog xác nhận. Dialog phải có:

* Pause all agents.
* Block new orders.
* Cancel pending orders.
* Close all positions.
* Disconnect execution bridge.
* Monitoring-only mode.
* Reason required.
* Scope.
* Estimated PnL impact.
* Admin permission status.
* Discord notify channels.
* Hold to confirm.

## 20.2. Backend Flow

```text
EmergencyStopRequested
-> PermissionCheck
-> AuditLog(PENDING)
-> PauseAgents
-> BlockNewOrders
-> CancelPendingOrders
-> ClosePositions according to policy
-> DisableExecutionBridge optional
-> Notify Discord/Alerts
-> AuditLog(OK/FAILED/PARTIAL)
```

Nếu broker không phản hồi, trạng thái phải là `STOP_FAILED` hoặc `PARTIAL_STOP`, không được báo stopped hoàn toàn.

---

# 21. Data Model Chính

## 21.1. Account

```text
Account
- id
- label
- type: Demo | Prop | Live | Research
- broker
- server
- masked_account
- balance
- equity
- free_margin
- margin_level
- floating_pnl
- daily_pnl
- latency_ms
- environment
- status
```

## 21.2. Agent

```text
Agent
- id
- name
- symbol
- timeframe
- strategy_version_id
- model_version_id
- status: Running | Paused | Waiting | Error
- action: Buy | Sell | Hold
- confidence
- regime
- reward
- trades_today
- daily_pnl
- drawdown
- latency_ms
- updated_at
```

## 21.3. Position

```text
Position
- id
- ticket
- account_id
- symbol
- side: Buy | Sell
- volume
- entry_price
- current_price
- stop_loss
- take_profit
- pnl
- swap
- commission
- duration_min
- strategy
- agent
- confidence
- risk_pct
- status: AI | Manual | Managed
```

## 21.4. ModelVersion

```text
ModelVersion
- id
- name
- algorithm
- version
- status
- trained_at
- training_steps
- validation_score
- backtest_sharpe
- live_sharpe
- backtest_max_dd
- live_dd
- drift
- last_retrain_at
- artifact_uri
- config_json
```

## 21.5. BacktestRun

```text
BacktestRun
- id
- strategy_version_id
- model_version_id
- dataset_version_id
- symbol
- timeframe
- date_range
- capital
- spread_model
- commission_model
- slippage_model
- swap_model
- latency_ms
- train_pct
- validation_pct
- test_pct
- walk_forward_config
- monte_carlo_count
- seed
- status
- metrics_json
- created_by
- created_at
```

## 21.6. RiskRule

```text
RiskRule
- id
- name
- enabled
- threshold
- warning_threshold
- critical_threshold
- action
- priority
- non_overridable
- updated_by
- updated_at
```

## 21.7. Signal

```text
Signal
- id
- agent_id
- strategy_version_id
- model_version_id
- account_id
- symbol
- timeframe
- action: BUY | SELL | CLOSE | HOLD
- confidence
- regime
- requested_volume
- suggested_sl
- suggested_tp
- reason_json
- status: CREATED | APPROVED | REJECTED | EXPIRED | EXECUTED
- created_at
```

## 21.8. RiskDecision

```text
RiskDecision
- id
- signal_id
- decision: APPROVE | MODIFY | REJECT
- original_volume
- approved_volume
- checks_json
- rejection_code
- created_at
```

## 21.9. Order

```text
Order
- id
- signal_id
- account_id
- broker_order_id
- broker_position_id
- symbol
- side
- order_type
- requested_volume
- filled_volume
- requested_price
- average_fill_price
- stop_loss
- take_profit
- status
- broker_response_json
- created_at
- updated_at
```

## 21.10. Alert

```text
Alert
- id
- severity
- source
- account_id
- agent_id
- symbol
- message
- status: Open | Ack | Resolved
- created_at
- acknowledged_by
- resolved_by
```

## 21.11. AuditLog

```text
AuditLog
- id
- timestamp
- actor
- source
- account_id
- action
- previous_state
- next_state
- result
- correlation_id
- latency_ms
- metadata_json
```

---

# 22. API Groups

## 22.1. Core Context

```text
GET /api/context
GET /api/accounts
POST /api/context/environment
POST /api/context/account
```

## 22.2. Dashboard

```text
GET /api/dashboard/metrics
GET /api/agents
POST /api/agents/{id}/pause
POST /api/agents/{id}/resume
GET /api/risk/monitor
```

## 22.3. Trading

```text
GET /api/positions
GET /api/orders
POST /api/orders/draft
POST /api/orders/simulate
POST /api/orders/confirm
POST /api/orders/reject
POST /api/emergency-stop
```

## 22.4. Research

```text
GET /api/models
GET /api/strategies
POST /api/strategies
POST /api/backtests
GET /api/backtests/{id}
GET /api/backtests/{id}/progress
```

## 22.5. Market Data

```text
GET /api/market/watch
GET /api/market/feed-integrity
GET /api/market/calendar
GET /api/market/candles
```

## 22.6. Operations

```text
GET /api/alerts
POST /api/alerts/{id}/ack
POST /api/alerts/{id}/resolve
GET /api/audit-logs
GET /api/integrations
POST /api/integrations/{id}/reconnect
POST /api/integrations/{id}/test
GET /api/settings/roles
PUT /api/settings/roles
```

## 22.7. Copilot

```text
POST /api/copilot/chat
POST /api/copilot/commands/simulate
POST /api/copilot/commands/confirm
POST /api/copilot/commands/reject
GET /api/copilot/health
```

---

# 23. Ngoại Lệ Và Quy Tắc Xử Lý

## 23.1. Spread Anomaly

Khi spread vượt ngưỡng:

* Không mở lệnh mới.
* Lệnh đang mở vẫn được quản lý.
* Hiển thị alert Market/Risk.
* Ghi RiskEvent.
* Chỉ mở lại khi spread ổn định qua số tick cấu hình.

## 23.2. Slippage Cao

Nếu slippage vượt max:

* Ghi requested price và filled price.
* Pause hoặc risk-limit agent.
* Không tự động gửi lệnh bù.
* Alert operator.

## 23.3. Model Drift

Nếu drift vượt ngưỡng:

* Alert Model.
* Pause agent nếu critical.
* Chặn deploy mới.
* Yêu cầu retrain/validation.

## 23.4. Margin Block

Nếu margin level dưới ngưỡng:

* Risk Engine reject order.
* Rejected tab hiển thị mã lỗi rõ ràng.
* Copilot giải thích được lý do.

## 23.5. MT5 Disconnect

Trong Live:

* Block new orders.
* Mark feed stale.
* Reconnect theo backoff.
* Không retry order chưa rõ trạng thái vô hạn.
* Sau reconnect phải sync orders/positions và reconciliation.

## 23.6. Market Closed

* Không gửi market order.
* Hiển thị thời gian mở cửa dự kiến nếu có.
* Auto session có thể Running nhưng Execution Status là Market Closed.

## 23.7. News Blackout

Trước/sau CPI, NFP, FOMC:

* Chặn entry mới theo window.
* Cho phép quản lý/đóng vị thế theo policy.
* Chỉ mở lại sau cooldown và spread ổn định.

## 23.8. Không Có Chiến Lược Đạt Chuẩn

Dashboard phải hiển thị:

```text
Chưa có chiến lược đủ điều kiện triển khai. Hãy hoàn thành Out-of-Sample, Walk-Forward, Cost Stress Test và Paper Trading.
```

Không được tự chọn chiến lược ít tệ nhất để Live.

---

# 24. Tiêu Chí Nghiệm Thu

## 24.1. UI Coverage

Mọi route hiện có trong `quant-command` phải có dữ liệu thật hoặc mock-backed API rõ ràng:

* `/`
* `/live`
* `/portfolio`
* `/orders`
* `/models`
* `/strategy`
* `/backtest`
* `/risk`
* `/market`
* `/alerts`
* `/logs`
* `/integrations`
* `/settings`

## 24.2. Data & Market

* Import hoặc stream được OHLC.
* Có spread.
* Có latency.
* Có feed integrity.
* Có news calendar.
* Có dataset version.

## 24.3. Research & Backtest

* Có ít nhất Mean Reversion M5.
* Có ML setup classifier skeleton.
* Có HMM regime skeleton.
* Có backtest với spread, commission, slippage, swap.
* Có Train/Validation/Test.
* Có Walk-Forward.
* Có Monte Carlo hoặc stress test.
* Có leakage/overfit warnings.

## 24.4. Live/Paper Trading

* Có Paper mode.
* Có Live mode warning.
* Manual order phải qua Review.
* AI/Discord command phải qua confirmation.
* RiskDecision trước Execution.
* Có MT5 integration health.
* Có reconciliation sau reconnect.

## 24.5. Risk & Safety

* Có Risk Rules.
* Có Risk Monitor.
* Có Emergency Stop hold-to-confirm.
* Có Daily Loss Stop.
* Có Drawdown Stop.
* Có Spread Filter.
* Có News Filter.
* Có Model Drift Stop.
* Có audit cho mọi hành động nhạy cảm.

## 24.6. Copilot

* Copilot gọi DeepSeek qua backend proxy.
* Không lộ API key ở frontend.
* Có fallback degraded.
* Có command confirmation.
* Có permission check.
* Có audit cho confirm/reject.

## 24.7. Security

* RBAC đúng theo Settings.
* Không log secret.
* Live action yêu cầu quyền phù hợp.
* Emergency Stop có quyền riêng.
* Credential được mã hóa.

---

# 25. Kết Luận

AurumQuant AI phải được xây như một hệ thống vận hành trading có kỷ luật, không phải một demo backtest đẹp. Giao diện `quant-command` đã định hình rõ sản phẩm: một command center realtime, có Copilot, có risk-first execution, có audit trail và có các workspace nghiên cứu.

Định hướng triển khai là:

1. UI-first để backend phục vụ đúng màn hình và đúng workflow.
2. XAU/USD-first để kiểm soát spread, slippage, news và regime.
3. Validation-first để mọi chiến lược phải sống sót qua OOS, WFO, cost và stress test.
4. Risk-first để không agent, model, Copilot hoặc integration nào được bỏ qua Risk Engine.

Chiến lược tốt không phải là chiến lược luôn vào lệnh. Chiến lược tốt là chiến lược biết khi nào không nên giao dịch.
