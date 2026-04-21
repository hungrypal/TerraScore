# Earth Engine Verification Steps (Student Access)

## Objective

Confirm free student access so TerraScore can export Earth Engine data to CSV.

## Steps

1. Open Earth Engine sign-up page: https://earthengine.google.com/
2. Sign in with your student Google account.
3. Complete the verification fields and submit.
4. Wait for approval confirmation email/dashboard status.
5. Open Colab notebook `colab/gee_dataset_to_csv.ipynb` and run initialization cell.
6. If initialization succeeds, run export cell to create CSV.

## Verification Checklist

- No permission error from `ee.Initialize()`.
- Export task starts successfully.
- CSV becomes available in Google Drive for transfer to `data/exports/`.

## Current Blocker

This verification must be completed by the account owner and cannot be bypassed from repository code alone.
