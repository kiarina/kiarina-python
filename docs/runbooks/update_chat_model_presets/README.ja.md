# Update Chat Model Presets

[English](README.md) | 日本語

`kiarina-agi-text` の chat model preset を最新化する手順です。

## Scope

主な変更対象は次のファイルです。

- `packages/kiarina-agi-text/src/kiarina/agi/chat_model/_settings.py`
- `packages/kiarina-agi-text/src/kiarina/agi/chat_model/_types/chat_model_specifier.py`

provider 実装単体の default model は、明示的に依頼された場合だけ変更します。公開 API や設定 schema は、preset 更新だけを理由に変更しません。

## Procedure

### 1. Research official information

各 provider の一次資料で、次の情報を確認します。

- API で使用する model ID
- availability と preview、deprecated、shutdown の状態
- context window と max output tokens
- input、cached input、cache write、output の標準料金
- image、audio、video、PDF の対応状況
- tool calling、built-in tools、endpoint の制約
- 後継 model と migration path

確認日と参照 URL を作業メモに残します。検索結果や比較記事だけを根拠にせず、provider の model、pricing、deprecation、migration document で照合します。

主な参照先:

- [OpenAI Models](https://developers.openai.com/api/docs/models)
- [Anthropic Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Gemini Latest Models](https://ai.google.dev/gemini-api/docs/latest-model)
- [Gemini Deprecations](https://ai.google.dev/gemini-api/docs/deprecations)

### 2. Select the preset set

新しい model を追加するだけでなく、既存 preset の役割も見直します。

古い model は、次の条件をすべて満たす新しい model がある場合に削除できます。

- provider が後継または migration target として案内している
- 標準料金が同額以下
- 主要な性能が同等以上
- context、output、modalities、tool 機能を失わない
- 同等以上の availability がある

低価格、低遅延、特殊な modality など、独自の役割が残る model は旧世代でも維持します。preview、招待制、用途限定の model は、固有機能を最新の汎用 model で代替できる場合は残しません。

alias は、通常利用する安定した preset にだけ割り当てます。削除する preset を参照する alias が残らないようにします。

### 3. Update settings

`ChatModelSettings.presets` に model ごとの値を登録します。

| Field | Rule |
| --- | --- |
| `model_name` | API に渡す公式 model ID |
| `context_window` | provider が示す context 上限 |
| `max_output_tokens` | provider が示す output 上限 |
| `token_count_limit` | output と運用上の余裕を確保した input 上限 |
| cost fields | 標準料金を microdollars / 1K tokens で登録 |
| `input_enabled` | provider が受け付ける modality だけを有効化 |
| `endpoint_type` | model が必要とする endpoint を指定 |
| `visible` | preview、特殊用途、fallback 制約がある場合は `False` を検討 |

`$/MTok` から microdollars / 1K tokens への変換は、値を1,000倍します。たとえば `$3/MTok` は `3_000` です。

長い context に追加料金がある場合だけ、その料金を表す設定を有効化します。標準料金で全 context を利用できる model では有効化しません。

OpenAI の GPT-5.6 preset では、272K input tokens を超えた場合にリクエスト全体の input 料金へ2倍、output 料金へ1.5倍を適用します。cache write は uncached input 料金の1.25倍として計算します。閾値の判定には cache read と cache write を含む input tokens を使用します。

削除した preset が型の例や文書に残っていないか検索します。

```bash
rg 'old-model-name' packages/kiarina-agi-text docs
```

### 4. Do not add settings tests

`ChatModelSettings` の preset 値だけを固定する test は追加しません。model 更新のたびに設定と同じ値を test に重複して記述することになるためです。

新しい preset の API 互換性は追加時の API test で確認します。料金計算など provider のロジックを変更する場合は、settings の値ではなくproviderの振る舞いをunit testで検証します。

### 5. Run addition-only API tests

新しい preset を追加した場合だけ、その preset ごとに costly な chat model helper test を実行します。料金だけの変更や通常の regression test では実行しません。

```bash
KIARINA_AGI_TEXT_TEST_CHAT_MODEL=<preset-name> \
mise run test kiarina-agi-text --no-pytest-args --costly --path tests/chat_model/_helpers/
```

`--no-pytest-args` は package の `.pytest-args` 全体を無視します。これにより `--reruns` も適用されず、新しい model の互換性エラーを無駄に再試行することを防げます。

追加した preset が複数ある場合は、すべてについて個別に実行します。API 負荷と rate limit を避けるため、原則として逐次実行します。

この test は、invoke、stream、tool calling、parallel tool calling、対応する file input と疑似 file output の一連の経路を確認します。

認証情報がない場合は、model 設定の不具合と区別して先に認証を解決します。認証前の失敗を model compatibility の判定には使用しません。secret は repository や test output に記録しません。

costly marker は [Pytest Markers](../../playbooks/pytest_markers/README.ja.md)、認証を含む外部 API test の扱いは [External Service Tests](../../playbooks/external_service_tests/README.ja.md) を参照してください。

### 6. Run package and repository checks

costly test の後に、通常の package test と repository check を実行します。

```bash
mise run test kiarina-agi-text
make
git diff --check
```

costly test は追加時だけ実行しますが、通常の package test と `make` は model の追加、削除、料金変更のいずれでも実行します。

### 7. Review the final diff

完了前に次を確認します。

- 調査した値と設定値が一致している
- 安価な独自ポジションの model を誤って削除していない
- deprecated または置き換え済みの preset が残っていない
- alias が存在する preset に解決される
- provider 実装の default model を意図せず変更していない
- 公開 API と設定 schema に不要な変更がない
- 追加したすべての preset で addition-only API test が成功している
- package test と `make` が成功している

## 2026-07 Update

この手順を初めて適用した更新では、次の整理を行いました。

- OpenAI: GPT-5.6 Sol、Terra、Lunaを追加し、GPT-5.5とGPT-5.4を削除
- Anthropic: Claude Sonnet 5、Opus 5、Fable 5とVertex presetを追加し、4.6系を削除
- Google: Gemini 3.6 Flashと3.5 Flash-Liteを追加し、3.1系と3 Flash previewを削除
- GPT-5.4 Mini、GPT-5.4 Nano、Claude Haiku 4.5は、低価格の独自ポジションがあるため維持
- GPT-5.6の272K超に対する段階料金とcache write料金をcost記録へ反映
- Fable 5とVertex Claude presetは`visible=False`に設定
- `llm`、`vlm`、`openai`、`anthropic`、`google`、`omni`のaliasを新しいpresetへ更新
