# ClockWithWeatherForecast

## 画面仕様

![display](/spec/display.png)

## 基本仕様

|機能|要件|更新間隔|
|:--|:--|:--|
|時刻表示機能|年月日曜日時分秒を表示する|秒の表示更新0.2秒、それ以外は変化時|
|室温・湿度・気圧表示機能|BME280で取得する|1分※|
|天気予報|yahoo天気rssを取得する|3時間※|

※BME280の取得と天気予報はアプリ起動時からの更新間隔

### その他の要件

* ntpdでntp同期を行うこと
* フォントで天気マークが無い場合はアイコンを使用する
* フォントはSource han codeとする
* ダークグレーバック＋パステルグリーン文字色、オフホワイトバック＋黒文字色切り替え
* 6時/18時で画面表示切替（黒バック⇔白バック）
* 時刻は24時間表示のみ
* 分、秒は2桁0埋めとし、その他のすべての（時刻以外も）表示は0埋めしない
* 天気予報表示は現在時刻に近い物から左に並べる。現在時刻が10時なら9,12,15,18,21,0,3とする

## 追加検討

* 数分後の雨予報の音声通知
* 日の出、日の入りでの画面表示切替（黒バック⇔白バック）
* フォント・色テーマ変更機能
* 過去12時間表示していた天気予報と温湿度気圧の表示
* 過去7日間表示していた天気予報のロギング
* 過去7日の温湿度気圧のロギング
* 焼き付き防止のため固定表示の文字について何か対策が必要かもしれない