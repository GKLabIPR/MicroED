我々の施設で MicroED 測定をした場合、画像から自分で処理してみたいといった希望がなければ、原則として ins/hkl ファイルのペアで納品します。
位相をつけて大半の原子を置いた状態にしますが、disorder のモデリングや原子名の調整など、精密化の仕上げはお任せしています。
精密化に自信がなく、投稿可能なレベルまでやってほしいという場合は、別途相談ください。

MicroED の解析技術は日進月歩であるため、投稿前に最新の方法で再解析すると、データの質が改善することがあります。
そのため、論文執筆に取り掛かる段階で連絡ください。
MicroED 測定と解析の method・統計値の表・格子定数の散布図・結晶の形の写真なども、こちらで執筆・記入します。

# Software

Olex2 はかならず[最新版(1.5 系列の中でも Alpha 版)をダウンロード](https://www.olexsys.org/olex2/docs/getting-started/installing-olex2/)して使ってください。
古いバージョンでは電子散乱因子が使えませんし、`EXTI` の処理にバグがあります。
精密化には SHELXL ではなくて Olex.refine を推奨します。

# Modeling

## Hydrogens

水素は Q peak として見える場合と見えない場合があります。
見えた場合でも、結合の分極により、水素原子核の位置と peak の位置は一致しません。
そのため、基本的には riding model にしてください。

Hydroxy hydrogen など、位置が一意に決まらず、Q peak や Fo-Fc difference map 上も見えない場合は、水素結合など化学的考察から最も蓋然性が高い場所に置いてください。

## Elements

MicroED は元素の区別が苦手です。例えば、ピリジンやイミダゾールの窒素の位置は、マップだけでは確定しないことがあります。
上に書いたように水素は見えないことがあるし、結合距離も信頼できないことがあります。
配位や水素結合など、化学的な環境と併せて総合的に判断してください。

## Maps

低分子の結晶学の人は Olex2 上の Q peak しか見ない人が多いですが、disorder した原子のピークや、twin や anistropy による ghost molecule や streak といった病理を見落としますので、かならず正負の Fo-Fc 差マップをメッシュで表示して確認してください。
Olex2 では Work - Draw - Toolbox Work - MAP: Diff - Show Map となります。



PXRD パターンを取得している場合は、精密化した構造から PXRD
パターンを計算して、
観測ピークを説明できるか確認してください。
MicroED では微小結晶しか測定できませんので、体積比では大半を占める
成分が大きい結晶しか与えない場合など、PXRD パターン(= bulk の主成分)と
MicroED で解いた構造が一致しない場合があります。
また、電顕の高真空中で溶媒や包摂したガスなどが脱離し、別の結晶多形に変化することも
ありえます。

## 温度

測定温度は約 79 K なので、精密化の際に ins ファイルに `TEMP -194.15` と記入してください。
(CIF ファイルは単位が K だが、ins ファイルは単位が摂氏温度であることに注意)

# Refinement

## Scattering factors

Olex2 最新版を使えば電子散乱因子を(近似的にではありますが)利用できます。
`SFAC` のところに Peng など何種類かあります。ものによって R の下がり方が違うことがあるので、それぞれ試してみるとよいです。

## R factor

多重散乱の影響等がありますので、X 線ほどは R が下がりません。
R1 15 - 20 % くらいが普通です。多重散乱が強いデータでは R1 25 % くらいになることもあります。

## Extinction correction

`EXTI` (extinction correction)は必ず入れてください。
理論的には正しくないのですが、多重散乱による影響を「統計的に」モデル化して抑制できます。
ただし、EXTI と ADP と global scale には相関があるため、local minima に陥ったり、重原子に強い difference peak
が残ることがあります。
この症状が出た場合、`EXTI` をオフにして全原子を isotropic にしたあと 100 cycles ほど回して過去の履歴を「忘れさせ」(この時点では重原子周りが赤く = negative になるはず)、その後、重原子を anisotropic ADP に変える → EXTI を入れる → ligand も
anisotropic に変えるなどとすると、difference peak が弱くなるようでした。
途中の各ステップは 10 cycle 程度までとし、local minima に陥るのを防ぐ工夫が必要です。
それでも解決しない場合もあり、その場合は諦めて、ありのまま出すしかありません。

## NPD (non-positive semidefinite)

ADP tensor に NPD (non-positive semidefinite) が出る場合は、適宜 `ISOR` や `SIMU` などの restraints をかけてください。

NPD だらけになる場合は、B factor をかけて、高角の強度を弱くする(実空間で blur する)必要があります。
これらは、多重散乱の影響を無視して kinematical refinement を行うこと、多数の結晶からのデータをマージすること、電荷を無視することなどから生じる MicroED に特徴的な問題です。

### 詳しい説明

分解能依存的な回折強度の減衰には、結晶ごとのばらつきがあります。
そのため、何かを基準にして、他の結晶にはプラスやマイナスの B をかけて揃えます。
具体的には、分解能依存的なスケール因子 exp B/d^2 をかけます。
B は結晶ごとに決めます。

この時、何に揃えるかは任意です。
したがって、B の絶対値には意味がなく、原子間の相対的な違いにだけ意味があると考えてください。

偶然選ばれた reference 次第では、「真の」(physical な)回折強度減衰よりも高分解能側が持ち上がった状態になりえます。
これは実空間でいえば、map が sharpening された状態、つまり負の温度因子を持つ状態になります。
しかし、物理的な温度因子は負にならないので、精密化プログラムの中で負(とか 0.1 未満とか)にならないように constrain されています。
そのため、スケール結果が sharp すぎる状態になっている場合は ADP 精密化が 0 で頭打ちになって進まなくなったり、ADP tensor が positive semi-definite でなくなってしまうので、構造因子に適当な B をかけて高分解能側を弱くしてやる必要があります。
実空間では、密度を「ぼかした」状態に相当するので blur といいます。

## ESD (estimated standard deviation)

格子定数や結合長などについて、MicroED では ESD (estimated standard deviation) の計算における仮定が満たされていませんので、
ESD は非常な過小評価になっています。
いくら ESD が 0.0003 Å とかであったとしても、実際は 0.3 % 程度の誤差がありえます。
そのため、小数点以下三桁目の精度はないと考えてください。
論文では 1.234 Å のように書かず、1.23 Å までにしてください。

# Submission

これらのため、CheckCIF の Alert が出ると思いますが、きちんと説明する書き方(「言い訳」)がありますので、deposition
前にかならず相談ください。

よくある Alert と対応は以下の通りです。

## Cell measurement

> PLAT183_ALERT_1_A Missing _cell_measurement_reflns_used Value \
> PLAT184_ALERT_1_A Missing _cell_measurement_theta_min Value \
> PLAT185_ALERT_1_A Missing _cell_measurement_theta_max Value

同梱する cif ファイルから転載してください。

## Diffractometer

> PLAT660_ALERT_1_A No Valid _diffrn_radiation_type Value Reported

以下のように記載してください。

```
_diffrn_measurement_method         'continuous rotation electron
diffraction (MicroED)'
_diffrn_measurement_device_type    'Talos Arctica electron microscope'
_diffrn_detector                   'Ceta camera'
_diffrn_detector_type              CMOS
_diffrn_source                     'Talos Arctica Field Emission Gun'
_diffrn_radiation_probe            electron
_diffrn_radiation_type             electron
_diffrn_ambient_temperature 79
_cell_measurement_temperature 79
```

Ceta camera の部分は Falcon 3 の場合は 'Falcon 3 direct electron detector (integration mode)' としてください。

## R1, wR2

> PLAT082_ALERT_2_A High R1 Value \
> PLAT084_ALERT_3_A High wR2 Value (i.e. > 0.25)

Validation Response Form で以下のように書いてください。

> We refined the atomic model only kinematically, ignoring effects of multiple scattering (dynamical diffraction).
> This led to high R1 and wR2 values.

## Rint

> RINTA01_ALERT_3_A The value of Rint is greater than 0.25 \
> PLAT020_ALERT_3_A The Value of Rint is Greater Than 0.12

Rint は複数の結晶をマージすることが稀だった時代に考えられた指標であり、多重度が高い場合には役に立ちません。
次のようにコメントしてください。

> R(int) increases with the multiplicity of the dataset.
> This is pointed out in Diederichs & Karplus, Nat. Struct. Biol., 1997 for the case of a related metric R(merge).
> We merged X crystals.
> The traditional threshold of 0.12 (or 0.25) is for low multiplicity datasets and not adequate for this data.

マージした結晶の数 (X) は、報告 PDF を見て書いてください。

## Chirality

Chirality がある物質の場合、`_chemical_absolute_configuration` は実験的に決めたわけではなく、合成ルートから類推したものですから、`syn` にしてください。
