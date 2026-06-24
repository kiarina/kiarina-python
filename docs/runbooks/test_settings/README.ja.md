# Test Settings

[English](README.md) | 日本語

`test-settings:upload` と `test-settings:download` mise task を準備して使用するための手順です。

これらの task は、gitignore されている `.env` と `test_settings.yaml` を age で暗号化し、暗号化済みファイルだけを private な Google Cloud Storage bucket に保存します。

## Prerequisites

次の command をインストールします。

- `age` と `age-keygen`
- Google Cloud CLI (`gcloud`)
- `mise`

Google Cloud project では billing が有効である必要があります。また、bucket を作成する操作者には bucket の作成と IAM policy の管理権限が必要です。

認証を行い、project を選択します。

```sh
gcloud auth login
gcloud config set project PROJECT_ID
gcloud auth list
gcloud config get project
```

Application Default Credentials は必要ありません。task は gcloud CLI が管理する認証情報を使用します。

## 1. Create an age key

private な設定 directory を作成し、age identity を生成します。

```sh
mkdir -p "$HOME/.config/kiarina/test-settings"
chmod 700 "$HOME/.config/kiarina/test-settings"

age-keygen \
  -o "$HOME/.config/kiarina/test-settings/identity.txt"

chmod 600 "$HOME/.config/kiarina/test-settings/identity.txt"
```

recipient を導出して保存します。

```sh
age-keygen \
  -y "$HOME/.config/kiarina/test-settings/identity.txt" \
  > "$HOME/.config/kiarina/test-settings/recipient.txt"

chmod 600 "$HOME/.config/kiarina/test-settings/recipient.txt"
cat "$HOME/.config/kiarina/test-settings/recipient.txt"
```

recipient は `age1` から始まり、secret ではありません。
identity には `AGE-SECRET-KEY-` が含まれており、secret として扱う必要があります。

identity の recovery copy を password manager などの安全な場所に保存してください。
この repository、test settings bucket、shell history、chat、issue tracker には保存しないでください。

## 2. Create a Cloud Storage bucket

Bucket name はグローバルに一意です。
開発チームに適した一意な名前と location を選択します。

```sh
export PROJECT_ID="your-google-cloud-project"
export BUCKET_NAME="your-unique-private-test-settings-bucket"
export LOCATION="asia-northeast1"
export GCS_PREFIX="kiarina-python"
```

uniform bucket-level access、public access prevention、7日間の soft delete を設定して bucket を作成します。

```sh
gcloud storage buckets create "gs://$BUCKET_NAME" \
  --project="$PROJECT_ID" \
  --location="$LOCATION" \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access \
  --public-access-prevention \
  --soft-delete-duration=7d
```

Bucket の location は作成後に変更できません。soft delete は誤った上書きや削除からの復旧に利用できますが、保持中の object に storage cost が発生します。

Bucket の設定を確認します。

```sh
gcloud storage buckets describe "gs://$BUCKET_NAME"
```

## 3. Grant access

Bucket を作成したユーザーは、project-level role によってすでにアクセスできる場合があります。各 developer または group には、その workflow に必要な object role を付与します。

upload と download を行うユーザーへ付与する場合:

```sh
export PRINCIPAL="user:developer@example.com"

gcloud storage buckets add-iam-policy-binding "gs://$BUCKET_NAME" \
  --member="$PRINCIPAL" \
  --role="roles/storage.objectUser"
```

Google Group の場合は、`group:developers@example.com` のような principal を使用します。

- `roles/storage.objectUser` は object の list、download、upload、置換、削除を許可します。
- download だけを行う環境には `roles/storage.objectViewer` で十分です。
- 既存の Cloud Storage object の置換には `storage.objects.create` と `storage.objects.delete` の両方が必要なため、繰り返し upload する用途では `roles/storage.objectCreator` だけでは不足します。

Task 自体は、upload 時に Cloud Storage が既存 object を置換する場合を除き、削除を要求しません。soft delete により、誤った削除や置換から復旧できる期間を確保します。Bucket 設定や IAM policy の変更権限は bucket administrator だけに付与してください。

Policy を確認します。

```sh
gcloud storage buckets get-iam-policy "gs://$BUCKET_NAME"
```

## 4. Configure environment variables

Task は次の環境変数を使用します。

| Variable | Used by | Secret |
| --- | --- | --- |
| `KIARINA_TEST_SETTINGS_GCS_URI` | upload と download | No |
| `KIARINA_TEST_SETTINGS_AGE_RECIPIENT` | upload | No |
| `KIARINA_TEST_SETTINGS_AGE_IDENTITY` | download | Yes |

Shell で設定します。

```sh
export KIARINA_TEST_SETTINGS_GCS_URI="gs://$BUCKET_NAME/$GCS_PREFIX"
export KIARINA_TEST_SETTINGS_AGE_RECIPIENT="$(
  cat "$HOME/.config/kiarina/test-settings/recipient.txt"
)"
export KIARINA_TEST_SETTINGS_AGE_IDENTITY="$(
  cat "$HOME/.config/kiarina/test-settings/identity.txt"
)"
```

zsh で永続化する場合は、private key を直接埋め込まず、key file を参照する同等の export を `~/.zshrc` に追加します。その後 shell を再読み込みします。

```sh
source "$HOME/.zshrc"
```

これらの環境変数を repository の `.env` に設定しないでください。その `.env` 自体が暗号化対象に含まれます。

upload 専用環境には GCS URI と recipient が必要ですが、identity は必要ありません。

## 5. Perform the initial upload

Repository 内に必要な `.env` と `test_settings.yaml` を作成または更新します。

対象ファイルと保存先 object name を preview します。

```sh
mise run test-settings:upload --dry-run
```

完全な一覧を注意して確認してから、暗号化して upload します。

```sh
mise run test-settings:upload
```

Prefix 以下に `.age` file だけが存在することを確認します。

```sh
gcloud storage ls --recursive "$KIARINA_TEST_SETTINGS_GCS_URI"
```

upload task は次のように動作します。

- `.env` または `test_settings.yaml` という名前の通常 file を検索する
- Git に ignore されていない file を拒否する
- 各 file を upload 前に暗号化する
- repository からの relative path を維持して `.age` を追加する
- remote object を自動削除しない

## 6. Set up another development environment

新しい環境では次を行います。

1. Repository を clone して通常の開発 setup を実行する
2. Google Cloud CLI をインストールして認証する
3. 安全な recovery location から age identity を復元する
4. permission を `0600` に設定する
5. GCS URI と age identity の環境変数を設定する

Access を確認します。

```sh
gcloud storage ls --recursive "$KIARINA_TEST_SETTINGS_GCS_URI"
```

Download を preview します。

```sh
mise run test-settings:download --dry-run
```

Download して復号します。

```sh
mise run test-settings:download
```

Command は既存 file の置換を拒否します。dry run を確認した後、意図して置換する場合は `--force` を使用します。

```sh
mise run test-settings:download --force
```

Download した plaintext file はアトミックに配置され、permission は `0600` に設定されます。

## 7. Update shared test settings

Local の `.env` または `test_settings.yaml` を変更した後に実行します。

```sh
mise run test-settings:upload --dry-run
mise run test-settings:upload
```

他の環境では次のように更新を取得できます。

```sh
mise run test-settings:download --dry-run
mise run test-settings:download --force
```

他の developer と更新タイミングを調整してください。Task は plaintext settings の merge や concurrent edit の検出を行いません。

## 8. Remove a retired file

upload task は意図的に remote object を削除しません。test settings file が不要になったことを確認した後、bucket administrator が暗号化済み object を明示的に削除できます。

```sh
gcloud storage rm \
  "$KIARINA_TEST_SETTINGS_GCS_URI/packages/example/test_settings.yaml.age"
```

`gcloud storage ls --recursive` が表示した正確な object URI を使用し、必要な場合は soft delete から復旧します。

## 9. Rotate the age key

Key を rotation する場合:

1. 現在の identity を backup する
2. 新しい identity と recipient を生成する
3. `KIARINA_TEST_SETTINGS_AGE_RECIPIENT` に新しい recipient を設定する
4. すべての settings file を再度 upload する
5. 別の環境に新しい identity を復元し、download と復号を確認する
6. 承認された secret channel を通じて新しい identity を配布する
7. すべての remote object の再暗号化と検証が完了してから古い identity を廃止する

Upload が途中で失敗すると、異なる recipient で暗号化された object が混在する可能性があります。完全な upload と別環境での download が成功するまで、以前の identity を廃止しないでください。

## Troubleshooting

### Missing environment variable

Task は不足している環境変数を正確に表示します。現在の shell を確認します。

```sh
for name in \
  KIARINA_TEST_SETTINGS_GCS_URI \
  KIARINA_TEST_SETTINGS_AGE_RECIPIENT \
  KIARINA_TEST_SETTINGS_AGE_IDENTITY
do
  if printenv "$name" >/dev/null; then
    echo "$name is set"
  else
    echo "$name is not set"
  fi
done
```

Identity の値を log や support request に表示または貼り付けないでください。

### Permission denied from Cloud Storage

Active account、project、object list、bucket IAM policy を確認します。

```sh
gcloud auth list
gcloud config get project
gcloud storage ls --recursive "$KIARINA_TEST_SETTINGS_GCS_URI"
```

Bucket administrator は IAM policy も確認できます。

```sh
gcloud storage buckets get-iam-policy "gs://$BUCKET_NAME"
```

### Existing local files

`test-settings:download` はデフォルトで既存 file を保持します。dry run で conflict を確認し、意図して置換する場合だけ `--force` を指定します。

### Decryption failure

設定した identity が最新の upload で使用した recipient に対応することを確認します。

```sh
age-keygen -y "$HOME/.config/kiarina/test-settings/identity.txt"
cat "$HOME/.config/kiarina/test-settings/recipient.txt"
```

出力が一致する必要があります。

## References

- [age](https://age-encryption.org/)
- [Create a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets)
- [Cloud Storage IAM roles](https://cloud.google.com/storage/docs/access-control/iam-roles)
- [Cloud Storage IAM permissions](https://cloud.google.com/storage/docs/access-control/iam-permissions)
- [Public access prevention](https://cloud.google.com/storage/docs/public-access-prevention)
- [Soft delete](https://cloud.google.com/storage/docs/soft-delete)
