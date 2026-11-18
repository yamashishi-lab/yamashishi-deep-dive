import streamlit as st
import streamlit.components.v1 as components
import json

# --- サンプルデータと予測データの構築 ---
# 直近の推移データに「明日の予測データ（点線）」を接続した配列
times_list = ['11/14 10:00', '11/14 11:30', '11/14 13:00', '11/14 14:30', '11/15 (予測)', '明日引け目標']
historical_prices = [18200.0, 18350.0, 18280.0, 18420.0, None, None]  # 実績
predicted_prices = [None, None, None, 18420.0, 18580.0, 18850.0]  # 予測・利確ライン周辺

# 利確・損切りの固定価格ライン（例：現在地18,420円を基準）
base_price = 18420.0
target_profit = round(base_price * 1.028, 1)  # 利確目標 +2.8%
stop_loss = round(base_price * 0.985, 1)      # 損切りライン -1.5%

echarts_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        body {
            margin: 0;
            background-color: #020408;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        #chart-container {
            width: 100%;
            height: 420px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(244, 63, 94, 0.4);
            box-shadow: 0 12px 36px rgba(0,0,0,0.8);
        }
    </style>
</head>
<body>
    <div id="chart-container"></div>
    <script>
        var chartDom = document.getElementById('chart-container');
        var myChart = echarts.init(chartDom, 'dark');
        
        var option = {
            backgroundColor: '#04070e',
            title: {
                text: 'YAMASHISHI LAB 量子予測＆トレード防衛ライン',
                left: 'center',
                textStyle: { color: '#f8fafc', fontSize: 13, fontWeight: 'bold' }
            },
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(9, 13, 22, 0.95)',
                borderColor: '#f43f5e',
                textStyle: { color: '#f8fafc', fontSize: 12 }
            },
            legend: {
                data: ['実績チャート', 'AI予測トレンド', '利確目標 (+2.8%)', '損切りライン (-1.5%)'],
                top: 25,
                textStyle: { color: '#94a3b8', fontSize: 11 }
            },
            grid: {
                top: 60,
                bottom: 40,
                left: 65,
                right: 30
            },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: __TIMES_DATA__,
                axisLine: { lineStyle: { color: '#334155' } },
                axisLabel: { color: '#94a3b8', fontSize: 10 }
            },
            yAxis: {
                type: 'value',
                scale: true,
                splitLine: { lineStyle: { color: 'rgba(30, 41, 59, 0.4)', type: 'dotted' } },
                axisLine: { lineStyle: { color: '#334155' } },
                axisLabel: { color: '#94a3b8', fontSize: 10 }
            },
            series: [
                {
                    name: '実績チャート',
                    type: 'line',
                    smooth: 0.2,
                    lineStyle: { color: '#38bdf8', width: 2.5 },
                    data: __HIST_DATA__
                },
                {
                    name: 'AI予測トレンド',
                    type: 'line',
                    smooth: 0.2,
                    lineStyle: { color: '#f43f5e', width: 2.5, type: 'dashed' },
                    data: __PRED_DATA__
                }
            ],
            // 初心者にも分かりやすい「利確」と「損切り」の水平ライン（MarkLine）
            markLine: { data: [] }
        };

        // 視覚的な利確・損切りラインをグラフに追加
        option.series[0].markLine = {
            silent: true,
            symbol: ['none', 'none'],
            data: [
                {
                    yAxis: __TARGET_PROFIT__,
                    name: '利確目標',
                    label: { formatter: '利確目標: '+ __TARGET_PROFIT__ +'円 (+2.8%)', position: 'end', color: '#10b981', fontWeight: 'bold' },
                    lineStyle: { color: '#10b981', type: 'solid', width: 2 }
                },
                {
                    yAxis: __STOP_LOSS__,
                    name: '損切りライン',
                    label: { formatter: '損切り: '+ __STOP_LOSS__ +'円 (-1.5%)', position: 'end', color: '#ef4444', fontWeight: 'bold' },
                    lineStyle: { color: '#ef4444', type: 'dashed', width: 2 }
                }
            ]
        };

        myChart.setOption(option);
        window.addEventListener('resize', function () { myChart.resize(); });
    </script>
</body>
</html>
"""

# Python変数をJavaScriptに安全に埋め込む
final_html = (
    echarts_template
    .replace('__TIMES_DATA__', json.dumps(times_list))
    .replace('__HIST_DATA__', json.dumps(historical_prices))
    .replace('__PRED_DATA__', json.dumps(predicted_prices))
    .replace('__TARGET_PROFIT__', str(target_profit))
    .replace('__STOP_LOSS__', str(stop_loss))
)

components.html(final_html, height=450)
