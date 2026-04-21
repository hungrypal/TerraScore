# Dataset Blocker: Google Earth Engine Verification

## Problem

Google Earth Engine dataset access is currently blocked pending verification of free student access.

## Why This Blocks CSV Conversion

CSV conversion depends on authenticated dataset retrieval. Without verification, export functions cannot run successfully.

## Required Verification Steps

1. Sign in to Google Earth Engine with student account.
2. Complete student/free-tier verification workflow.
3. Confirm account status is active and can access target dataset.
4. Execute verification test script in Colab.

## Acceptance Criteria

- Dataset can be queried without permission errors.
- At least one sample region export to CSV completes.
- CSV is available under `data/exports/`.

## Temporary Status

- State: `blocked`
- Owner: data team
- Next checkpoint: next scrum
