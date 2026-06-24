# Test Settings

English | [日本語](README.ja.md)

Procedure for preparing and using the `test-settings:upload` and `test-settings:download` mise tasks.

These tasks encrypt ignored `.env` and `test_settings.yaml` files with age and store only the encrypted files in a private Google Cloud Storage bucket.

## Prerequisites

Install the following commands:

- `age` and `age-keygen`
- Google Cloud CLI (`gcloud`)
- `mise`

The Google Cloud project must have billing enabled, and the operator creating the bucket must have permission to create buckets and manage its IAM policy.

Authenticate and select the project:

```sh
gcloud auth login
gcloud config set project PROJECT_ID
gcloud auth list
gcloud config get project
```

Application Default Credentials are not required. The tasks use the credentials managed by the gcloud CLI.

## 1. Create an age key

Create a private configuration directory and generate an age identity:

```sh
mkdir -p "$HOME/.config/kiarina/test-settings"
chmod 700 "$HOME/.config/kiarina/test-settings"

age-keygen \
  -o "$HOME/.config/kiarina/test-settings/identity.txt"

chmod 600 "$HOME/.config/kiarina/test-settings/identity.txt"
```

Derive and save the recipient:

```sh
age-keygen \
  -y "$HOME/.config/kiarina/test-settings/identity.txt" \
  > "$HOME/.config/kiarina/test-settings/recipient.txt"

chmod 600 "$HOME/.config/kiarina/test-settings/recipient.txt"
cat "$HOME/.config/kiarina/test-settings/recipient.txt"
```

The recipient begins with `age1` and is not secret. The identity contains `AGE-SECRET-KEY-` and must be treated as a secret.

Store a recovery copy of the identity in a password manager or another secure location. Do not store it in this repository, the test settings bucket, shell history, chat, or issue trackers.

## 2. Create a Cloud Storage bucket

Bucket names are globally unique. Choose a unique name and the location appropriate for the development team:

```sh
export PROJECT_ID="your-google-cloud-project"
export BUCKET_NAME="your-unique-private-test-settings-bucket"
export LOCATION="asia-northeast1"
export GCS_PREFIX="kiarina-python"
```

Create the bucket with uniform bucket-level access, public access prevention, and seven-day soft delete:

```sh
gcloud storage buckets create "gs://$BUCKET_NAME" \
  --project="$PROJECT_ID" \
  --location="$LOCATION" \
  --default-storage-class=STANDARD \
  --uniform-bucket-level-access \
  --public-access-prevention \
  --soft-delete-duration=7d
```

The bucket location cannot be changed after creation. Soft delete provides recovery from accidental overwrites or deletions, but incurs storage charges for retained objects.

Verify the bucket configuration:

```sh
gcloud storage buckets describe "gs://$BUCKET_NAME"
```

## 3. Grant access

The person who creates the bucket may already have access through project-level roles. Grant each developer or group the object role needed by their workflow.

For a user who uploads and downloads:

```sh
export PRINCIPAL="user:developer@example.com"

gcloud storage buckets add-iam-policy-binding "gs://$BUCKET_NAME" \
  --member="$PRINCIPAL" \
  --role="roles/storage.objectUser"
```

For a Google Group, use a principal such as `group:developers@example.com`.

- `roles/storage.objectUser` permits listing, downloading, uploading, replacing, and deleting objects.
- `roles/storage.objectViewer` is sufficient for an environment that only downloads.
- Replacing an existing Cloud Storage object requires both `storage.objects.create` and `storage.objects.delete`; `roles/storage.objectCreator` alone is therefore insufficient for repeated uploads.

The task itself never requests deletion except when Cloud Storage replaces an existing object during upload. Soft delete provides a recovery window for accidental deletion or replacement. Only bucket administrators should receive permission to change the bucket configuration or IAM policy.

Verify the policy:

```sh
gcloud storage buckets get-iam-policy "gs://$BUCKET_NAME"
```

## 4. Configure environment variables

The tasks use the following variables:

| Variable | Used by | Secret |
| --- | --- | --- |
| `KIARINA_TEST_SETTINGS_GCS_URI` | upload and download | No |
| `KIARINA_TEST_SETTINGS_AGE_RECIPIENT` | upload | No |
| `KIARINA_TEST_SETTINGS_AGE_IDENTITY` | download | Yes |

Configure them in the shell:

```sh
export KIARINA_TEST_SETTINGS_GCS_URI="gs://$BUCKET_NAME/$GCS_PREFIX"
export KIARINA_TEST_SETTINGS_AGE_RECIPIENT="$(
  cat "$HOME/.config/kiarina/test-settings/recipient.txt"
)"
export KIARINA_TEST_SETTINGS_AGE_IDENTITY="$(
  cat "$HOME/.config/kiarina/test-settings/identity.txt"
)"
```

For persistent zsh configuration, add equivalent exports to `~/.zshrc`, referencing the key files instead of embedding the private key directly. Then reload the shell:

```sh
source "$HOME/.zshrc"
```

Do not put these variables in the repository `.env`. That file is itself included in the encrypted test settings.

An upload-only environment needs the GCS URI and recipient, but does not need the identity.

## 5. Perform the initial upload

Create or update the required `.env` and `test_settings.yaml` files in the repository.

Preview the files and destination object names:

```sh
mise run test-settings:upload --dry-run
```

Review the complete list carefully, then encrypt and upload:

```sh
mise run test-settings:upload
```

Verify that only `.age` files exist below the prefix:

```sh
gcloud storage ls --recursive "$KIARINA_TEST_SETTINGS_GCS_URI"
```

The upload task:

- finds regular files named `.env` or `test_settings.yaml`;
- rejects files that are not ignored by Git;
- encrypts each file before uploading it;
- preserves its repository-relative path and adds `.age`;
- does not automatically delete remote objects.

## 6. Set up another development environment

On the new environment:

1. Clone the repository and run the normal development setup.
2. Install and authenticate the Google Cloud CLI.
3. Restore the age identity from the secure recovery location.
4. Set its permissions to `0600`.
5. Configure the GCS URI and age identity environment variables.

Confirm access:

```sh
gcloud storage ls --recursive "$KIARINA_TEST_SETTINGS_GCS_URI"
```

Preview the download:

```sh
mise run test-settings:download --dry-run
```

Download and decrypt:

```sh
mise run test-settings:download
```

The command refuses to replace existing files. After reviewing the dry run, use `--force` when replacement is intended:

```sh
mise run test-settings:download --force
```

Downloaded plaintext files are placed atomically and assigned permission `0600`.

## 7. Update shared test settings

After changing a local `.env` or `test_settings.yaml`:

```sh
mise run test-settings:upload --dry-run
mise run test-settings:upload
```

Other environments can then retrieve the update:

```sh
mise run test-settings:download --dry-run
mise run test-settings:download --force
```

Coordinate updates with other developers. The tasks do not merge plaintext settings or detect concurrent edits.

## 8. Remove a retired file

The upload task intentionally does not delete remote objects. After confirming that a test settings file is no longer needed, a bucket administrator can remove its encrypted object explicitly:

```sh
gcloud storage rm \
  "$KIARINA_TEST_SETTINGS_GCS_URI/packages/example/test_settings.yaml.age"
```

Use the exact object URI shown by `gcloud storage ls --recursive` and rely on soft delete for recovery if necessary.

## 9. Rotate the age key

To rotate the key:

1. Back up the current identity.
2. Generate a new identity and recipient.
3. Set `KIARINA_TEST_SETTINGS_AGE_RECIPIENT` to the new recipient.
4. Upload every settings file again.
5. Restore the new identity on another environment and verify download and decryption.
6. Distribute the new identity through the approved secret channel.
7. Retire the old identity only after every remote object has been re-encrypted and verified.

An interrupted upload can leave objects encrypted for different recipients. Do not retire the previous identity until the complete upload and cross-environment download have succeeded.

## Troubleshooting

### Missing environment variable

The task reports the exact missing variable. Check the current shell:

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

Do not print or paste the identity value into logs or support requests.

### Permission denied from Cloud Storage

Check the active account, project, object listing, and bucket IAM policy:

```sh
gcloud auth list
gcloud config get project
gcloud storage ls --recursive "$KIARINA_TEST_SETTINGS_GCS_URI"
```

A bucket administrator can also inspect the IAM policy:

```sh
gcloud storage buckets get-iam-policy "gs://$BUCKET_NAME"
```

### Existing local files

`test-settings:download` preserves existing files by default. Use the dry run to review conflicts and pass `--force` only when replacement is intended.

### Decryption failure

Confirm that the configured identity corresponds to the recipient used for the latest upload:

```sh
age-keygen -y "$HOME/.config/kiarina/test-settings/identity.txt"
cat "$HOME/.config/kiarina/test-settings/recipient.txt"
```

The outputs must match.

## References

- [age](https://age-encryption.org/)
- [Create a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets)
- [Cloud Storage IAM roles](https://cloud.google.com/storage/docs/access-control/iam-roles)
- [Cloud Storage IAM permissions](https://cloud.google.com/storage/docs/access-control/iam-permissions)
- [Public access prevention](https://cloud.google.com/storage/docs/public-access-prevention)
- [Soft delete](https://cloud.google.com/storage/docs/soft-delete)
